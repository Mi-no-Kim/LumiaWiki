"""Check protected Issue/Task/execution comments after tools and in Git candidates."""

import sys
sys.dont_write_bytecode = True

import argparse
import json
import re
import subprocess

from harness_inventory import Candidate, path_name
from issue_rule_comments import POLICY, baseline, fingerprint, inspect


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', default='index')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--hook', action='store_true', help='Read PostToolUse input; check worktree; return hook feedback')
    mode.add_argument('--describe-baseline', help='Print an extracted baseline; never writes or approves a revision')
    mode.add_argument('--plan-fingerprint', metavar='TASK_PATH', help='Print the linked Task plan fingerprint without recording approval')
    args = parser.parse_args()
    hook = args.hook
    try:
        if hook:
            raw = sys.stdin.buffer.read(4_000_001)
            if len(raw) > 4_000_000:
                raise ValueError('Hook input is oversized')
            event = json.loads(raw)
            if not isinstance(event, dict) or event.get('hook_event_name') != 'PostToolUse':
                raise ValueError('Expected a PostToolUse event')
        view = Candidate('work' if hook else args.candidate, seconds=10)
        if args.plan_fingerprint:
            from rule_comments import effective_profile, field_values, plan_fingerprint, read_policy, task_paths
            name = path_name(args.plan_fingerprint)
            if effective_profile(name, read_policy(view)) != 'task-with-plan':
                raise ValueError('Expected a Task record that uses a separate plan')
            folder, _, plan_link, _ = task_paths(name)
            task = view.read(name)
            plan = view.read(f'{folder}/{plan_link}')
            links = field_values(task, '상세 계획') if task is not None else []
            if (len(links) != 1 or plan is None
                    or not re.fullmatch(r'\[[^\]]+\]\(' + re.escape(plan_link) + r'\)', links[0])):
                raise ValueError('Expected a linked Task plan in the selected candidate')
            print(plan_fingerprint(plan))
            return 0
        if args.describe_baseline:
            raw = view.read(args.describe_baseline)
            if raw is None:
                raise ValueError('Baseline source is absent')
            values = baseline(raw)
            print(json.dumps({'comments': values, 'digest': fingerprint(values)}, ensure_ascii=False, indent=2))
            return 0
        # An installed wrapper can outlive the branch that introduced this check.
        # Skip only an exact older Git candidate with neither policy nor adapter.
        if view.kind != 'work' and all(view.read(n) is None for n in (POLICY, 'scripts/check-issue-rule-comments.py', 'harness/rule-comments.json', 'scripts/rule_comments.py', 'scripts/check-rule-comments.py')):
            return 0
        previous = None
        ref = view.git('rev-parse', '--verify', 'HEAD', allowed=(0, 128)).decode().strip() if view.kind in ('work', 'index') else None
        if ref:
            previous = Candidate(ref, cwd=view.root, seconds=10)
        elif view.commit:
            parents = view.git('rev-list', '--parents', '-n', '1', view.commit).decode().split()
            if len(parents) > 1:
                previous = Candidate(parents[1], cwd=view.root, seconds=10)
        if previous is not None and previous.read(POLICY) is not None and view.read(POLICY) is None:
            raise ValueError('Previously protected Issue policy is missing')
        errors = inspect(view, previous) if view.read(POLICY) is not None else []
        current_policy = view.read('harness/rule-comments.json')
        if current_policy is None and view.read(POLICY) is None:
            raise ValueError('Record comment policy is missing')
        if current_policy is not None:
            from rule_comments import inspect as inspect_current
            errors.extend(inspect_current(view, previous))
        elif view.read('scripts/rule_comments.py') is not None:
            raise ValueError('Current record policy is missing; restore the complete configuration')
    except (ValueError, OSError, KeyError, TypeError, AttributeError, UnicodeError, subprocess.SubprocessError) as error:
        errors = ['Record rule comments unverified: ' + str(error).splitlines()[0][:700]]
    if errors:
        reason = '\n'.join(errors[:12])
        if len(errors) > 12:
            reason += f'\n... {len(errors) - 12} more violations'
        if hook:
            print(json.dumps({'decision': 'block', 'reason': reason,
                              'hookSpecificOutput': {'hookEventName': 'PostToolUse',
                              'additionalContext': 'Record comment/state preservation failed. Changes remain on disk. Review and repair only the reported scope; do not infer permission to revise protected rules or legacy enrollment.'}}, ensure_ascii=False))
            # Codex parses stdout JSON on successful command completion. Exit 2
            # is the alternative stderr-feedback protocol, not JSON output.
            return 0
        else:
            print(reason, file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
