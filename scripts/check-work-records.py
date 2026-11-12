"""Check newly introduced record violations; long Task/Issue bodies only warn."""

import sys
sys.dont_write_bytecode = True

import argparse
import difflib
from pathlib import PurePosixPath
import re
import subprocess

from harness_inventory import Candidate

SCOPES = ['AGENTS.md', 'README.md', 'STRUCTURE.md', 'docs', 'harness', 'work']
DATE = r'(?:19|20)\d{2}(?:[-/.]\d{1,2}[-/.]\d{1,2}|년\s*\d{1,2}월\s*\d{1,2}일)'
FIELD = re.compile(r'(?i)(?<!\w)(?:작성일|수정일|검증일|기록일|확인일|작성\s*날짜|수정\s*날짜|검증\s*날짜|기록\s*날짜|verifiedAt|recordedAt|checkedAt|verification_date|record_date)\s*["`*_]*\s*[:：=|]\s*["`*_]*' + DATE)
DATED_NAME = re.compile(r'(?:^|[-_. ])' + DATE + r'(?:$|[-_. ])')
PAYLOAD = re.compile(r'^<!--\s*(?:tdd-plan|tdd-evidence|harness-inventory)\s*-->$')


def inspect_record(name, text, old):
    lines = text.splitlines()
    record = name.startswith('work/records/') and '/artifacts/' not in name and re.fullmatch(r'(?:issue|task-\d+)\.md', PurePosixPath(name).name)
    errors, warnings = [], []
    if record and len(lines) > 100:
        warnings.append(f'{name}: {len(lines)} lines > 100; retain necessary current decisions, move needed execution detail to artifacts.')
    if old is None and name.startswith('work/records/') and DATED_NAME.search(PurePosixPath(name).stem):
        errors.append(f'{name}: record filename contains a date; use the work identifier.')
    changed = set()
    for kind, _, _, start, end in difflib.SequenceMatcher(None, (old or '').splitlines(), lines, autojunk=False).get_opcodes():
        if kind in ('insert', 'replace'):
            changed.update(range(start, end))
    fence = None
    for index, line in enumerate(lines):
        # Native payloads in artifacts remain intact; authored prose still checks.
        if '/artifacts/' in name:
            marker = re.match(r'^\s*(`{3,}|~{3,})', line)
            if marker:
                token = marker[1]
                if fence is None:
                    fence = token
                elif token[0] == fence[0] and len(token) >= len(fence):
                    fence = None
                continue
            if fence:
                continue
        if index not in changed:
            continue
        if FIELD.search(line):
            errors.append(f'{name}:{index + 1}: record date field; use commit, run ID or source digest.')
        if record and PAYLOAD.fullmatch(line.strip()):
            errors.append(f'{name}:{index + 1}: execution payload belongs in artifacts; keep its conclusion and link here.')
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', default='index')
    parser.add_argument('--base', help='Comparison commit; defaults to HEAD for index, first parent for a commit.')
    args = parser.parse_args()
    try:
        if args.candidate == 'work':
            raise ValueError('Use an exact index or committed candidate')
        view = Candidate(args.candidate)
        base = args.base
        if base is None:
            if args.candidate == 'index':
                base = view.git('rev-parse', '--verify', 'HEAD', allowed=(0, 128)).decode().strip() or None
            else:
                parents = view.git('rev-list', '--parents', '-n', '1', view.commit).decode().split()
                base = parents[1] if len(parents) > 1 else None
        previous = Candidate(base, cwd=view.root) if base else None
        diff = ['diff', '--cached'] if args.candidate == 'index' else ['diff', previous.commit, view.commit] if previous else ['diff-tree', '--root', '--no-commit-id', '-r', view.commit]
        if args.candidate == 'index' and previous:
            diff.append(previous.commit)
        names = view.git(*diff, '--name-only', '-z', '--diff-filter=AM', '--no-renames', '--', *SCOPES).decode().split('\0')
        names = [n for n in names if n and PurePosixPath(n).suffix in ('.md', '.json', '.yaml', '.yml', '.toml') and not ('/artifacts/' in n and not n.endswith('.md'))]
        view.load(names)
        if previous:
            previous.load(names)
        errors = []
        for name in names:
            old = previous.read(name) if previous else None
            failures, warnings = inspect_record(name, view.read(name).decode('utf-8-sig'), old.decode('utf-8-sig') if old is not None else None)
            errors.extend(failures)
            for warning in warnings:
                print('WARNING: ' + warning, file=sys.stderr)
        for error in errors:
            print('Record violation: ' + error, file=sys.stderr)
        return 2 if errors else 0
    except (ValueError, OSError, UnicodeError, subprocess.SubprocessError) as error:
        print('Record candidate unverified: ' + str(error).splitlines()[0], file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
