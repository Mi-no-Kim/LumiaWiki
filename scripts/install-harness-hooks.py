"""Preserve, connect and restore one selected project Git hook atomically."""

import sys
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess


BRANCH_HOOKS = ('reference-transaction', 'pre-push')
BRANCH_CHECKER_MARKER = b'__LUMIA_BRANCH_NAME_CHECKER__'
BRANCH_ARCHIVE_MARKER = b'__LUMIA_BRANCH_ARCHIVE_PIN__'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(root, *args):
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, timeout=5)
    if result.returncode:
        raise ValueError('Git hook location could not be inspected')
    return result.stdout.decode('utf-8').strip()


def location(root):
    configured = subprocess.run(['git', '-C', str(root), 'config', '--path', '--get', 'core.hooksPath'],
                                capture_output=True, timeout=5)
    if configured.returncode not in (0, 1):
        raise ValueError('Git hooksPath could not be inspected')
    value = configured.stdout.decode('utf-8').strip()
    directory = Path(value or git(root, 'rev-parse', '--git-path', 'hooks'))
    if not directory.is_absolute():
        directory = root / directory
    if not directory.resolve().is_relative_to(root):
        raise ValueError('External Git hook location requires manual connection; nothing changed')
    cursor = root
    for part in directory.relative_to(root).parts:
        cursor = cursor / part
        if cursor.is_symlink() or cursor.is_junction():
            raise ValueError('Reparse-point Git hook location requires manual review')
    return directory


def source_checkout(root, requested):
    if requested is None:
        return root
    source = requested.resolve(strict=True)
    top = Path(git(source, 'rev-parse', '--show-toplevel')).resolve()
    if source != top:
        raise ValueError('The source must be the top level of a Git worktree')
    target_common = Path(git(root, 'rev-parse', '--path-format=absolute', '--git-common-dir')).resolve()
    source_common = Path(git(top, 'rev-parse', '--path-format=absolute', '--git-common-dir')).resolve()
    if source_common != target_common:
        raise ValueError('The source worktree must share the target Git repository')
    return top


def wrapper_bytes(root, source_root, event):
    source = source_root / 'scripts/hooks' / event
    if source.is_symlink() or source.is_junction() or not source.is_file():
        raise ValueError('Versioned hook definition is absent or a link')
    wrapper = source.read_bytes().replace(b'\r\n', b'\n')
    if event in BRANCH_HOOKS:
        # These hooks are shared by linked worktrees, even on older checkouts.
        checker = source_root / 'scripts/check-branch-names.py'
        if checker.is_symlink() or checker.is_junction() or not checker.is_file():
            raise ValueError('Branch name checker is absent or a link')
        if wrapper.count(BRANCH_CHECKER_MARKER) != 1 or wrapper.count(BRANCH_ARCHIVE_MARKER) != 1:
            raise ValueError('Branch hook placeholders must each occur once')
        archive = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(checker), 'archive-pin'],
                                 cwd=root, capture_output=True, timeout=15)
        if archive.returncode:
            raise ValueError(archive.stderr.decode('utf-8').strip() or 'Could not inspect the local archive')
        pin = shlex.quote(archive.stdout.decode('utf-8').strip()).encode('utf-8')
        payload = shlex.quote(checker.read_text(encoding='utf-8')).encode('utf-8')
        wrapper = wrapper.replace(BRANCH_ARCHIVE_MARKER, pin).replace(BRANCH_CHECKER_MARKER, payload)
    return wrapper


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hook', choices=('pre-commit', 'commit-msg', *BRANCH_HOOKS), default='pre-commit')
    parser.add_argument('--source-worktree', type=Path, help='Read branch hook sources from a linked worktree')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--status', action='store_true')
    mode.add_argument('--remove', action='store_true')
    args = parser.parse_args()
    if args.source_worktree is not None and args.hook not in BRANCH_HOOKS:
        parser.error('--source-worktree is supported only for branch hooks')
    try:
        root = Path(git(Path.cwd(), 'rev-parse', '--show-toplevel')).resolve()
        directory = location(root)
        hook = directory / args.hook
        backup = directory / (args.hook + '.harness-original')
        metadata = directory / ('.harness-inventory-' + args.hook + '.json')
        for path in (hook, backup, metadata):
            if path.is_symlink() or path.is_junction():
                raise ValueError('Reparse-point hook/backup/metadata requires manual review')
        data = json.loads(metadata.read_text(encoding='utf-8')) if metadata.exists() else None
        if metadata.exists():
            if not isinstance(data, dict) or data.get('schema') != 1 or not hook.is_file() or sha(hook.read_bytes()) != data['wrapper']:
                raise ValueError('Installed wrapper changed; preserve it and remove outer wrappers first')
            if data['original'] is not None and (not backup.is_file() or sha(backup.read_bytes()) != data['original']):
                raise ValueError('Original hook backup changed; nothing removed')
            if data['original'] is None and backup.exists():
                raise ValueError('Unexpected backup exists; preserve it for review')
        if args.status:
            print(json.dumps({'event': args.hook, 'installed': data is not None, 'hookDirectory': str(directory),
                              'previousHook': bool(data and data['original']), 'configurationChanged': False}))
            return 0
        if data is not None:
            if not args.remove:
                return 0
            if data['original'] is None:
                hook.unlink()
            else:
                os.replace(backup, hook)
            metadata.unlink()
            return 0
        if args.remove:
            return 0
        if backup.exists():
            raise ValueError('Unowned original-hook backup exists; nothing overwritten')
        wrapper = wrapper_bytes(root, source_checkout(root, args.source_worktree), args.hook)
        if hook.is_file() and hook.read_bytes().replace(b'\r\n', b'\n') == wrapper:
            raise ValueError('Unowned inventory wrapper exists; do not nest it')
        original = sha(hook.read_bytes()) if hook.exists() else None
        directory.mkdir(parents=True, exist_ok=True)
        if original is not None:
            shutil.copy2(hook, backup)
        try:
            metadata.write_text(json.dumps({'schema': 1, 'original': original, 'wrapper': sha(wrapper)}) + '\n', encoding='utf-8')
            hook.write_bytes(wrapper)
            hook.chmod(0o755)
        except OSError:
            if backup.exists():
                os.replace(backup, hook)
            elif original is None:
                hook.unlink(missing_ok=True)
            metadata.unlink(missing_ok=True)
            raise
        return 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print('Inventory hook unverified: ' + str(error).splitlines()[0] + '\nNext: preserve the existing hook and resolve this installation condition.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
