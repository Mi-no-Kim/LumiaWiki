"""Preserve, connect and restore this repository's inventory pre-commit hook."""

import sys
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--status', action='store_true')
    mode.add_argument('--remove', action='store_true')
    args = parser.parse_args()
    try:
        root = Path(git(Path.cwd(), 'rev-parse', '--show-toplevel')).resolve()
        directory = location(root)
        hook = directory / 'pre-commit'
        backup = directory / 'pre-commit.harness-original'
        metadata = directory / '.harness-inventory-pre-commit.json'
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
            print(json.dumps({'installed': data is not None, 'hookDirectory': str(directory),
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
        source = root / 'scripts/hooks/pre-commit'
        if source.is_symlink() or source.is_junction() or not source.is_file():
            raise ValueError('Versioned pre-commit definition is absent or a link')
        wrapper = source.read_bytes().replace(b'\r\n', b'\n')
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
