"""Read-only consistency and acceptance audit, without scenario expected outcomes."""

import argparse
from collections import Counter
from pathlib import Path
import json
import re
import sys

sys.dont_write_bytecode = True
from workflow import ARTIFACTS, Workspace, field, rules, text


def visible(document):
    output, fence = [], None
    for line in document.splitlines():
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
        elif fence is None:
            output.append(line)
    return re.sub(r'(`+)(.*?)(?<!`)\1(?!`)', '', '\n'.join(output))


def audit(folder):
    ws = Workspace(folder)
    before = ws.snapshot()
    issues, link_count = [], 0
    if not ws.path('task.md').exists():
        missing = ws.creation_issues()
        if not missing:
            issues.append('task not created despite complete creation input')
        if ws.path('execution.md').exists():
            issues.append('execution without a Task')
        result = {'case': ws.folder.name, 'state': '미생성', 'issues': issues, 'creation_missing': missing}
    else:
        document = text(ws.path('task.md'))
        state = field(document, '상태')
        if state not in ['예정', '진행 중', '중단', '완료', '취소']:
            issues.append('invalid Task state')
        if rules(document, 'task') != rules(text(ARTIFACTS / 'task-body-template-draft.md'), 'task'):
            issues.append('Task rules changed')
        if re.findall(r'^## (.+)$', document, re.M) != ['현재 요약', '전달사항 참조', '계획과 합의', '결과']:
            issues.append('Task sections changed')
        if state == '완료':
            issues.extend(ws.check_task()['issues'])
        drift = ws.revision_issues()
        if drift and state != '중단':
            issues.extend(drift)
        if state == '중단' and field(document, '막힌 조건') in [None, '', '없음']:
            issues.append('stopped without a blocking condition')
        if ws.path('execution.md').exists():
            execution = text(ws.path('execution.md'))
            if rules(execution, 'execution') != rules(text(ARTIFACTS / 'task-execution-template-draft.md'), 'execution'):
                issues.append('execution rules changed or repeated')
            if execution.index('<!-- execution-rule:') > execution.index('<a id="work-'):
                issues.append('execution header rule inside work sections')
            for work in re.findall(r'<a id="work-([a-z-]+)">', execution):
                if f'execution.md#work-{work}' not in document or f'task.md#work-{work}' not in execution:
                    issues.append('broken work return link: ' + work)
        result = {'case': ws.folder.name, 'state': state, 'issues': issues,
                  'parent_state': field(text(ws.path('parent.md')), '상태')}
    if field(text(ws.path('parent.md')), '상태') == '완료':
        issues.extend(ws.check_parent()['issues'])
    for source in ws.folder.glob('*.md'):
        if source.name not in ['parent.md', 'task.md', 'execution.md', 'return.md'] and not source.name.startswith('assignment'):
            continue
        document = visible(text(source))
        ids = re.findall(r'<a\s+id="([^"]+)"', document)
        if any(count > 1 for count in Counter(ids).values()):
            issues.append('duplicate anchor: ' + source.name)
        for target in re.findall(r'(?<!!)\[[^\]\n]+\]\((<[^>]+>|[^)\s]+)\)', document):
            target = target.strip('<>')
            if re.match(r'[a-z][a-z0-9+.-]*:', target):
                continue
            filename, _, anchor = target.partition('#')
            destination = (source.parent / filename).resolve() if filename else source
            destination.relative_to(ARTIFACTS.parent)
            if not destination.is_file() or (anchor and f'<a id="{anchor}"></a>' not in visible(text(destination))):
                issues.append('broken management link: ' + source.name + ': ' + target)
            link_count += 1
    if ws.snapshot() != before:
        issues.append('audit changed the case files')
    result['management_links'] = link_count
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--case', help='One neutral case label; no scenario oracle is read')
    args = parser.parse_args()
    run = args.run.resolve()
    run.relative_to(ARTIFACTS)
    folders = [run / 'cases' / args.case] if args.case else sorted((run / 'cases').glob('*'))
    if not folders or any(not folder.is_dir() for folder in folders):
        raise ValueError('no cases to audit')
    results = [audit(folder) for folder in folders if folder.is_dir()]
    if not results:
        raise ValueError('no cases were audited')
    report = {'cases': len(results), 'issues': sum(len(item['issues']) for item in results), 'results': results}
    print(json.dumps(report, ensure_ascii=False))
    return 1 if report['issues'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
