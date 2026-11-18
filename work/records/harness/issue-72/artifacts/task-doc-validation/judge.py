"""Judge-only replay of fixed scenario expectations; never used by the executor."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from verify import audit
from workflow import ARTIFACTS, Workspace, block, field, text


def assess(run):
    oracle = json.loads(text(run / 'sealed/oracle.json'))
    events = json.loads(text(run / 'sealed/events.json'))
    original = json.loads(text(run / 'sealed/source-cases.json'))
    actual_names = {p.name for p in (run / 'cases').iterdir() if p.is_dir()}
    if actual_names != set(oracle):
        raise ValueError('input unit set changed')
    results = []
    for label, expected in oracle.items():
        ws = Workspace(run / 'cases' / label)
        case = original[label]
        item = audit(ws.folder)
        issues = list(item['issues'])
        number = expected['scenario']
        if item['state'] != expected['expected_task_state']:
            issues.append('scenario state differs from fixed expectation')
        if hashlib.sha256(ws.path('input.json').read_bytes()).hexdigest() != expected['input_sha']:
            issues.append('executor changed original input')
        if text(ws.path('assignment.md')) != case['initial_assignment_text']:
            issues.append('original r001 assignment changed')
        expected_parent = case['initial_parent_policy']
        if number == 7:
            revision = next(event for event in events[label] if event['kind'] == 'revise')
            expected_parent = revision['parent_policy']
            if text(ws.path(revision['assignment_name'])) != revision['assignment_text']:
                issues.append('provided revision source changed')
        if block(text(ws.path('parent.md'))) != expected_parent:
            issues.append('parent acceptance conditions drifted')
        if number == 2:
            if not ws.path('return.md').is_file() or not text(ws.path('return.md')).strip():
                issues.append('missing actual creation response')
        if number in [3,5,8,12,14]:
            for name, value in case['files'].items():
                if text(ws.path(name)) != value:
                    issues.append('out-of-scope payload changed: ' + name)
        if number == 4:
            if text(ws.path('start.md')) != case['files']['start.md']:
                issues.append('source provision was treated as write permission')
            supplied = next(event for event in events[label] if event['kind'] == 'supply')
            for name, value in supplied['files'].items():
                if not ws.path(name).exists() or text(ws.path(name)) != value:
                    issues.append('provided source missing or changed')
        if number == 11:
            expected_start = case['files']['start.md'].replace('(guide.md#recording)', '(guides/recording.md#recording)')
            expected_index = case['files']['index.md'].replace('(guide.md#recording)', '(guides/recording.md#recording)')
            if text(ws.path('start.md')) != expected_start or text(ws.path('index.md')) != expected_index:
                issues.append('move changed unrelated entrance content')
        if number == 10:
            note = next(item['value'] for item in case['policy']['criteria'] if item['id']=='user-note')
            if note not in text(ws.path('start.md')):
                issues.append('user-added sentence lost during recovery')
        results.append({'input': label, 'scenario': number, 'state': item['state'],
                        'issues': issues, 'management_links': item['management_links']})
    return {'units': len(results), 'scenarios': len({r['scenario'] for r in results}),
            'issues': sum(len(r['issues']) for r in results), 'results': results}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True, type=Path)
    args = parser.parse_args()
    run = args.run.resolve()
    run.relative_to(ARTIFACTS)
    result = assess(run)
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(1 if result['issues'] else 0)
