"""Conservative closing-reference guard; inspect messages, never change Issues."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys


KEYWORD = r'(?<![\w])(?:close[sd]?|fix(?:es|ed)?|resolve[sd]?)(?![\w])'
REFERENCE = r'(?:https?://[^\s/]+/[^\s/]+/[^\s/]+/issues/[0-9]+|(?:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)?\#[0-9]+)'
# Include simple Markdown/punctuation wrappers as a preventive policy, not a
# claim to reproduce every GitHub parser rule. Quoted examples are not exempt.
CLOSING = re.compile(KEYWORD + r'[\s:：,;.!?()\[\]{}*_`~\"\x27\-]*' +
                     r'(?:issues?\s+)?' + REFERENCE, re.IGNORECASE)


def violations(text, label):
    return [f'{label}:{text.count(chr(10), 0, match.start()) + 1}: {match.group(0)!r}'
            for match in CLOSING.finditer(text)]


def git(repo, *args):
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True)
    if result.returncode:
        raise ValueError('Git message range is unavailable; fetch the exact base/head history')
    return result.stdout.decode('utf-8')


def commit(repo, revision):
    return git(repo, 'rev-parse', '--verify', '--end-of-options', revision + '^{commit}').strip()


def range_violations(repo, base, head):
    if base == '':
        raise ValueError('Base revision must not be empty')
    head = commit(repo, head)
    base = commit(repo, base) if base and set(base) != {'0'} else None
    revision = base + '..' + head if base else head
    rows = git(repo, 'log', '--format=%H%x00%B%x00', '--no-show-signature', revision, '--').split('\0')
    messages = [(rows[i].strip(), rows[i + 1]) for i in range(0, len(rows) - 1, 2)]
    if git(repo, 'rev-parse', '--is-shallow-repository').strip() == 'true':
        location = Path(git(repo, 'rev-parse', '--git-path', 'shallow').strip())
        location = location if location.is_absolute() else Path(repo) / location
        boundary = set(location.read_text(encoding='ascii').splitlines())
        if boundary.intersection(oid for oid, _ in messages):
            raise ValueError('Commit range crosses a shallow boundary; fetch complete history')
    return [item for oid, message in messages for item in violations(message, 'commit ' + oid)]


def read_message(path):
    return path.read_text(encoding='utf-8-sig')


def event_violations(repo, payload, name):
    if name == 'pull_request':
        pr = payload['pull_request']
        if not isinstance(pr['title'], str) or not isinstance(pr['body'], (str, type(None))):
            raise ValueError('PR title/body must be text')
        return (violations(pr['title'], 'PR title') + violations(pr['body'] or '', 'PR body') +
                range_violations(repo, pr['base']['sha'], pr['head']['sha']))
    if name == 'push':
        return range_violations(repo, payload['before'], payload['after'])
    if name == 'workflow_dispatch':
        head = commit(repo, 'HEAD')
        return violations(git(repo, 'show', '-s', '--format=%B', head), 'commit ' + head)
    raise ValueError('Unsupported event; use pull_request, push or workflow_dispatch')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--message-file', type=Path, help='Final commit/squash/merge message')
    mode.add_argument('--base', help='Exclude commits already reachable from this base')
    mode.add_argument('--event-file', type=Path, help='Read CI JSON without shell interpolation')
    parser.add_argument('--head', default='HEAD')
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--pr-file', type=Path, help='PR title and body, with --base')
    parser.add_argument('--event-name', default=os.environ.get('GITHUB_EVENT_NAME'))
    args = parser.parse_args(argv)
    if args.pr_file and not args.base:
        parser.error('--pr-file requires --base')
    try:
        if args.message_file:
            failures = violations(read_message(args.message_file), 'message')
        elif args.event_file:
            failures = event_violations(args.repo, json.loads(read_message(args.event_file)), args.event_name)
        else:
            failures = range_violations(args.repo, args.base, args.head)
            if args.pr_file:
                failures += violations(read_message(args.pr_file), 'PR title/body')
        for failure in failures:
            print('Closing reference rejected: ' + failure, file=sys.stderr)
        if failures:
            print('Use a descriptive summary and a separate Refs #number line; do not hide the keyword with punctuation.', file=sys.stderr)
        return 1 if failures else 0
    except (ValueError, OSError, UnicodeError, KeyError, TypeError, AttributeError, subprocess.SubprocessError) as error:
        print('Closing references unverified: ' + str(error).splitlines()[0], file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
