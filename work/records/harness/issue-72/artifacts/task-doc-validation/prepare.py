"""Controller-only fixture preparation. Do not give this file to the executor."""

from copy import deepcopy
import argparse
from pathlib import Path
import hashlib
import json
import re
import sys

sys.dont_write_bytecode = True
from workflow import Workspace, set_field

ARTIFACTS = Path(__file__).resolve().parent.parent
RUN = ARTIFACTS / 'task-doc-suite-b'
RAW = re.findall(r'```markdown\n(.*?)\n```', (ARTIFACTS / 'task-document-management-test-cases.md').read_text(encoding='utf-8'), re.S)
START, GUIDE = [part + '\n' for part in RAW]
A = '# 시작 안내\n\n작업 상태와 상세 기록의 작성 방법을 확인하세요.\n\n[기록 방법 보기](guide.md#recording)\n'
NOTE = '이 안내는 내부 작업자를 위한 것입니다.'
NEW_GUIDE = GUIDE.replace('Task 본문은 현재 상태와 계획을 관리합니다.', 'Task 본문에는 현재 상태·계획·유효한 결정을 정리합니다.')


def condition(key, kind, path=None, value=None):
    result = {'id': key, 'kind': kind}
    if path is not None:
        result['path'] = path
    if value is not None:
        result['value'] = value
    return result


def policy(mode='edit'):
    if mode == 'compare':
        return {'allowed_writes': [], 'criteria': [condition('criteria-' + word, 'contains', 'execution.md', word)
                for word in ['수동', '로컬', '재현', '준비', '범위', '후속']] + [condition('method', 'choice', value='manual')]}
    return {'allowed_writes': ['start.md'], 'required_sources': ['guide.md'], 'criteria': [
        condition('link', 'links', 'start.md'), condition('layout', 'equals', 'start.md', A),
        condition('guide', 'equals', 'guide.md', GUIDE), condition('choice', 'choice', value='A')]}


def parent_policy(task_policy):
    if not task_policy['criteria']:
        return {'criteria': []}
    return {'criteria': [condition('child-result', 'task_complete')] + deepcopy(task_policy['criteria'])}


def assignment(goal, selected):
    question = ('수동 대조와 로컬 검사 방식을 비교한 뒤 모의 사용자 역할이 선택한다.'
                if any(item.get('value') == 'manual' for item in selected['criteria']) else
                '없음 — 이동 경로·표식·참조 보정 범위는 부모 배정에서 정했다.' if selected.get('allowed_moves') else
                'A는 짧은 설명 한 문장과 기록 방법 링크, B는 기록 방법 링크만 남기는 안이다. '
                '두 안 모두 상세 두 문장의 중복을 줄인다. 모의 사용자 역할이 비교 뒤 선택하며 AI 권고는 선택을 대신하지 않는다.')
    return ('# 시험용 전달사항\n\n- 태그: 조사, 논의, 결정, 실행, 검수\n\n'
            '## 목적\n\n' + goal + '\n\n## 기대 결과\n\n' + goal + '\n\n'
            '## 이미 정해진 조건\n\n이 문서의 허용 대상·선행 입력·완료 조건을 따른다. '
            '모의 사용자 사건은 실제 사용자 승인으로 쓰지 않는다.\n\n'
            '## Task에서 결정할 사항\n\n' + question + '\n\n'
            '## 완료 조건과 확인 방법\n\n다음 조건 정의를 실제 파일·선택 근거와 대조한다. '
            '생성 입력의 사본을 Task 현재 값으로 바꾸지 않는다.\n\n```json\n' +
            json.dumps(selected, ensure_ascii=False, indent=2) + '\n```\n')


def make(label, number, note, selected=None, mode='edit', files=None, events=None, initial=None, pending=None):
    selected = deepcopy(selected or policy(mode))
    initial_files = deepcopy(files if files is not None else {'start.md': START, 'guide.md': GUIDE})
    goal = '두 문서의 링크 점검 방법을 비교하고 선정·이유·후속 조건을 정리한다.' if mode == 'compare' else '시작 안내의 링크·중복을 정리하고 선택·확인 근거를 남긴다.'
    data = {'goal': goal, 'result': goal, 'acceptance': deepcopy(selected['criteria']),
            'creation': {'parent': 'P', 'task': 'T', 'path_checked': True, 'collision_checked': True},
            'note': note, 'expected_before': deepcopy(initial_files), 'initial_events': initial or [],
            'events': [{'id': item['id'], 'kind': item['kind']} for item in events or []],
            'pending': pending or ('방법 선택은 모의 사용자 역할이 결정한다.' if mode == 'compare' else 'A/B 안내 방식은 모의 사용자 역할이 결정한다.')}
    return {'label': label, 'number': number, 'input': data, 'policy': selected, 'files': initial_files,
            'events': events or []}


CHOICE = {'id': 'selection', 'kind': 'choice', 'value': 'A', 'reason': '짧은 안내로 링크 용도를 알린다.'}
CASES = [make('sample-a', 1, '배정의 전체 작업을 수행한다. 실제 생성 직후에는 미착수이며 수행 기록이 없다.', events=[CHOICE])]
for label, missing in [('sample-b', 'result'), ('sample-c', 'acceptance'), ('sample-d', 'creation')]:
    item = make(label, 2, '생성 입력을 확인하고 필요한 보완을 반환한다. 다른 원천에 누락된 답은 없다.')
    item['input'][missing] = None
    if missing in ['result', 'acceptance']:
        item['policy']['criteria'] = []
    if missing == 'result':
        item['input']['goal'] = '시작 안내의 문제를 줄이기 위한 과제를 준비한다.'
        item['input']['acceptance'] = None
        item['policy']['allowed_writes'] = []
        item['input']['note'] += ' 문안 제안만 맡길지 실제 수정까지 맡길지와 그 결과의 수용 기준은 아직 결정하지 않았다.'
    CASES.append(item)
CASES.append(make('sample-e', 3, '원문 검토·방법 비교·논의만 맡긴다. 파일 수정·검사기 작성·실행은 배정하지 않았다.', mode='compare',
                  events=[{'id': 'method', 'kind': 'choice', 'value': 'manual', 'reason': '두 파일에서 추가 환경 없이 경로·표식을 대조한다.'}]))
p = policy(); p['allowed_writes'] = []; p['criteria'] = [condition('source', 'exists', 'guide.md'), condition('link', 'links', 'start.md'), condition('choice', 'choice', value='A')]
CASES.append(make('sample-f', 4, '현재 허용은 생성·계획과 확보 원문의 읽기 전용 대조다. 상세 원문은 아직 미제공이다. 필요한 지점에서 supply 사건을 요청할 수 있다. 자료 제공은 편집 허용이 아니다.',
                  selected=p, files={'start.md': START}, events=[{'id': 'supply', 'kind': 'supply', 'files': {'guide.md': GUIDE}}]))
CASES.append(make('sample-g', 5, '후보를 비교하고 선택을 질문할 수 있다. 응답 사건은 제공되지 않았다. 다른 독립 활동은 후보 준비 후 남아 있지 않다.'))
CASES.append(make('sample-h', 6, '후보 비교 뒤 extra 사건으로 추가 요청을 확인한다. 배정 범위를 바꾸지 않는 추가 비교이며 그 뒤 선택 사건이 별도로 있다.',
                  events=[{'id': 'extra', 'kind': 'request', 'value': '아직 고르지 않겠다. 처음 읽는 사람과 반복 사용자의 관점에서 더 비교해 달라.'}, CHOICE]))
p2 = policy(); p2['allowed_writes'] = ['start.md', 'guide.md']; p2['criteria'][2]['value'] = NEW_GUIDE
revision = {'id': 'revision', 'kind': 'revise', 'revision': 'r002', 'assignment_name': 'assignment-r002.md',
            'assignment_text': assignment('두 문서를 함께 정리하고 상세 원문의 첫 문장을 개정한다.', p2), 'parent_policy': parent_policy(p2)}
CASES.append(make('sample-i', 7, '원문 대조 후 revision 사건에 부모 배정 변경이 제공된다. 변경 전 허용은 start.md뿐이다. 이전 원문·전달본·수행 근거를 보존하고 적용 범위와 계획을 맞춘다.', events=[revision, CHOICE]))
CASES.append(make('sample-j', 8, '기존 Task의 원문 대조는 모의 사전 상태에서 완료돼 있다. 남은 링크 수정과 안내 문안 정리의 두 미착수 할 일(각각 확인 포함)을 한 반영·확인 할 일로 병합하는 요청이다. 이번 관찰은 계획 조정까지다. 사용자 선택 조건과 기존 완료 작업 식별자·근거를 유지한다.'))
CASES.append(make('sample-k', 9, '초기 입력은 모의 A안 선택 뒤 반영된 문서이며 확인은 끝나지 않았다. 실제 결과·기준을 대조하고 부족하면 같은 할 일에서 보완·재확인한다.',
                  files={'start.md': A.replace('#recording)', '#records)'), 'guide.md': GUIDE}, initial=[CHOICE], pending='없음 — A안 선택은 초기 모의 입력이다.'))
partial = START.replace('#record)', '#recording)').replace('# 시작 안내\n', '# 시작 안내\n\n' + NOTE + '\n', 1)
p = policy(); p['criteria'][1] = condition('layout', 'contains', 'start.md', '작업 상태와 상세 기록의 작성 방법을 확인하세요.'); p['criteria'].append(condition('user-note', 'contains', 'start.md', NOTE))
for line in ['Task 본문은 현재 상태와 계획을 관리합니다.', '자세한 수행 내용은 별도 수행 기록에 남깁니다.']:
    p['criteria'].append(condition('detail-' + str(len(p['criteria'])), 'absent_text', 'start.md', line))
CASES.append(make('sample-l', 10, '초기 입력은 모의 중단 뒤 링크만 저장되고 별도 사용자 문장이 추가된 상태다. 본문 다음 행동은 이전 값이고 저장 뒤 확인 근거는 없다. 실제 저장·미수행·미확인을 구별하고 추가 문장을 보존한다.',
                  selected=p, files={'start.md': partial, 'guide.md': GUIDE}, initial=[CHOICE], pending='없음 — A안 선택은 초기 모의 입력이다.'))
move_guide = GUIDE + '\n[시작 안내로 돌아가기](start.md)\n'
p = {'allowed_writes': ['start.md', 'index.md', 'guides/recording.md'], 'allowed_moves': [['guide.md', 'guides/recording.md']], 'criteria': [
    condition('old-location', 'missing', 'guide.md'), condition('new-location', 'exists', 'guides/recording.md'),
    *[condition('link-' + str(i), 'links', name) for i, name in enumerate(['start.md', 'index.md', 'guides/recording.md'])],
    condition('body', 'equals', 'guides/recording.md', move_guide.replace('(start.md)', '(../start.md)'))]}
CASES.append(make('sample-m', 11, 'guide.md를 guides/recording.md로 이동하고 세 문서의 들어오고 나가는 현재 상대 링크를 보정한다. 본문·recording 표식은 보존하며 별도 문안 선택은 없다.', selected=p,
                  files={'start.md': START.replace('#record)', '#recording)'), 'guide.md': move_guide, 'index.md': '# 목록\n\n[기록](guide.md#recording)\n'}, pending='없음 — 이동 경로·범위는 배정에서 확정됐다.'))
CASES.append(make('sample-n', 12, '원문 대조와 후보 작성 이후 cancel 사건이 있다. 최종 안내 방식·대체 작업은 미정이며 부모의 링크·중복 문제 해소는 필수 결과로 남는다.',
                  events=[{'id': 'cancel', 'kind': 'cancel', 'value': '이 Task는 여기서 취소하자. 최종 안내 방식과 대체 작업은 아직 정하지 않았다.'}]))
p = policy(); p['criteria'][1]['value'] = A.replace('작업 상태와 상세 기록의 작성 방법을 확인하세요.', '기록 작성법을 확인하세요.')
CASES.append(make('sample-o', 13, '이미 생성된 Task가 있다. 부모와 Task의 현재 배정 참조·원본을 대조하고 허용된 작업을 판단한다. 부모의 확정 개정본은 제공돼 있다.', selected=p,
                  initial=[CHOICE], pending='없음 — A안 선택은 초기 모의 입력이다.'))
user_changed = START.replace('Task 본문은 현재 상태와 계획을 관리합니다.', '사용자 수정: 이 설명은 원문을 유지하며 별도 합의 전 줄이지 마세요.')
item = make('sample-p', 14, '이미 생성된 Task와 과거 합의 원문이 있다. 그 후 사용자가 같은 문장을 수정했다. 새로운 충돌 해소 선택은 제공하지 않았다. 원본과 사용자 변경을 대조하고 조건 안에서 수행한다.',
            files={'start.md': user_changed, 'guide.md': GUIDE}, initial=[CHOICE], pending='없음 — A안은 이전 모의 선택이며 이후 겹치는 사용자 변경을 확인해야 한다.')
item['input']['expected_before']['start.md'] = START
CASES.append(item)
CASES.append(make('sample-q', 15, '기존 Task에 완료 체크·완료 상태가 붙어 있다. 실제 대상·현재 배정·근거와 상태를 대조한다. 보완 전에 읽기 전용 검사와 complete_task 및 accept_parent를 각각 호출하고 실제 반환·전후 무변경을 확인한다. 그 반환에 따라 현재 범위의 실제 오류를 보완할 수 있지만 표시만 맞춰 수용하지 않는다.',
                  files={'start.md': A.replace('#recording)', '#records)'), 'guide.md': GUIDE}, initial=[CHOICE], pending='없음 — A안 선택은 초기 모의 입력이다.'))


def prepare(run=RUN):
    global RUN
    RUN = Path(run).resolve()
    RUN.relative_to(ARTIFACTS)
    RUN.mkdir(exist_ok=False)
    (RUN / 'cases').mkdir()
    (RUN / 'sealed').mkdir()
    events = {}
    states = {1:'완료',2:'미생성',3:'완료',4:'중단',5:'중단',6:'완료',7:'완료',8:'진행 중',9:'완료',10:'완료',11:'완료',12:'취소',13:'완료',14:'중단',15:'완료'}
    oracle = {}
    for case in CASES:
        folder = RUN / 'cases' / case['label']; folder.mkdir()
        (folder / 'input.json').write_text(json.dumps(case['input'], ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        for name, value in case['files'].items():
            target = folder / name; target.parent.mkdir(parents=True, exist_ok=True); target.write_text(value, encoding='utf-8', newline='\n')
        source = assignment(case['input']['goal'], case['policy'])
        if not case['input']['result']:
            source = source.replace('## 기대 결과\n\n' + case['input']['goal'], '## 기대 결과\n\n미정 — 문안 제안과 실제 반영 중 담당 결과·범위를 정하지 않았다.')
        (folder / 'assignment.md').write_text(source, encoding='utf-8', newline='\n')
        parent = ('# 시험용 부모 P\n\n가상 시험이며 실제 번호·승인으로 쓰지 않는다.\n\n- 상태: 진행 중\n'
                  '- 적용 전달본: [전달사항](assignment.md)\n- 전달본 식별: r001\n- 보유 Task: 미생성\n- 수용 판정: 미판정\n'
                  '- 생성 식별 확인: ' + ('확인 — 이 시험의 P/T·저장 위치·충돌 부재를 제공한다.' if case['input']['creation'] else '미확인 — 식별·저장 위치·충돌 확인 근거를 아직 제공하지 않았다.') + '\n'
                  '- 다음 행동: 실제 입력·준비와 Task 결과를 확인한다.\n- 잔여: 전체 수용은 아직 미판정이다.\n\n'
                  '<a id="assignment"></a>\n## 배정과 전체 수용 조건\n\n```json\n' + json.dumps(parent_policy(case['policy']), ensure_ascii=False, indent=2) +
                  '\n```\n\n<a id="children"></a>\n## 자식과 현재 위치\n\n자식 상태만으로 전체 수용을 판단하지 않는다.\n')
        (folder / 'parent.md').write_text(parent, encoding='utf-8', newline='\n')
        events[case['label']] = case['events']
        oracle[case['label']] = {'scenario': case['number'], 'expected_task_state': states[case['number']], 'input_sha': hashlib.sha256((folder/'input.json').read_bytes()).hexdigest()}
        if case['number'] == 8:
            ws = Workspace(folder); ws.create_task()
            ws.set_plan([('inspect','기존 원문 대조','조사, 검수'),('choose','안내 방식 선택','논의, 결정'),
                         ('link','링크 수정과 자체 확인','실행, 검수'),('intro','안내 문안 정리와 자체 확인','실행, 검수'),('close','전체 결과·종료 확인','검수')])
            ws.summary('진행 중','[계획과 합의](#sequence)','완료된 원문 대조를 보존하고 미착수 계획을 재구성한다.')
            ws.record('inspect','가상 사전 상태 입력: 원문 대조가 끝난 기존 기록이다. 이번 실행에서 과거에 수행한 사실이 아니다.',
                      '입력에서 start의 record 링크와 실제 recording 표식 불일치 및 상세 두 문장의 중복이 확인돼 있다.',done=True,verdict='충족')
        if case['number'] in [9,10,13,14,15]:
            ws = Workspace(folder); ws.create_task()
            ws.set_plan([('recover','입력된 기존 작업의 실제 상태 대조·보완','조사, 실행, 검수'),('close','전체 결과·종료 확인','검수')])
            ws.summary('중단' if case['number']==10 else '진행 중','[현재 작업](#work-recover)','입력된 기존 상태를 대조한다.')
            ws.record('recover','가상 사전 상태 입력이며 이 실행에서 과거에 수행한 사실이 아니다.','사전 확인 근거는 아직 없다.','실제 대조·보완 필요.',done=False)
            if case['number']==13:
                # Keep Task r001; only the already decided parent moves to r002.
                original = policy()
                (folder/'assignment.md').write_text(assignment(case['input']['goal'], original), encoding='utf-8', newline='\n')
                (folder/'assignment-r002.md').write_text(assignment(case['input']['goal'], case['policy']), encoding='utf-8', newline='\n')
                set_field(folder/'parent.md','적용 전달본','[확정 개정본](assignment-r002.md)')
                set_field(folder/'parent.md','전달본 식별','r002')
            if case['number']==15:
                body = (folder/'task.md').read_text(encoding='utf-8').replace('- [ ] 수행·확인 완료','- [x] 수행·확인 완료')
                (folder/'task.md').write_text(body, encoding='utf-8', newline='\n')
                set_field(folder/'task.md','상태','완료')
                set_field(folder/'task.md','막힌 조건','없음')
    (RUN/'sealed/events.json').write_text(json.dumps(events, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (RUN/'sealed/oracle.json').write_text(json.dumps(oracle, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    sources = {}
    for case in CASES:
        folder = RUN/'cases'/case['label']
        sources[case['label']] = {**case, 'initial_assignment_text': (folder/'assignment.md').read_text(encoding='utf-8'),
                                'initial_parent_policy': parent_policy(case['policy'])}
    (RUN/'sealed/source-cases.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'run':str(RUN),'input_units':len(CASES),'scenarios':len(states)},ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, default=RUN)
    args = parser.parse_args()
    prepare(args.run)
