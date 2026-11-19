"""Executor operations for the isolated, neutral document inputs.

Reads supplied inputs/current documents only. Events arrive through the provider API.
Does not contain or emit scenario verdicts.
"""
from pathlib import Path
import json
import re
import sys

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parent / 'task-doc-validation'))
from workflow import Workspace, Refused, field, set_field, text


def packed(value):
    return json.dumps(value, ensure_ascii=False)


def emit(ws, action, **values):
    print(packed({'unit': ws.folder.name, 'action': action, **values}))


def section(ws, key):
    path = ws.path('execution.md')
    if not path.exists():
        return {}
    match = re.search(r'<a id="work-' + key + r'"></a>([\s\S]*?)(?=\n<a id="work-|\Z)', text(path))
    if not match:
        return {}
    result = {k: field(match[1], k) or '' for k in ['조치·판단', '확인']}
    try:
        observation = json.loads(result['확인'])
        if isinstance(observation, dict) and '관찰' in observation:
            result['확인'] = observation['관찰']
    except ValueError:
        pass
    return result


def record(ws, key, action, observation, remaining='없음', done=False, verdict=None):
    # Preserve actual prior failure/seed/event facts when updating the same work.
    old = section(ws, key)
    if old.get('조치·판단'):
        action = old['조치·판단'] + ' / 현재 조치: ' + action
    if old.get('확인'):
        observation = old['확인'] + ' / 현재 확인: ' + observation
    ws.record(key, action, observation, remaining, done=done,
              verdict=verdict or ('충족' if done else '미확인'))


def refuse(ws, key, label, callback):
    before = ws.snapshot()
    try:
        callback()
    except Refused as error:
        assert ws.snapshot() == before, label + ': refusal mutated files'
        details = packed(error.issues)
        if ws.path('task.md').exists():
            record(ws, key, label + '의 보호 조건을 실제 호출로 확인했다.',
                   'Refused: ' + details + '; 거절 전후 snapshot 동일, 파일 무변경.',
                   '거절 이유가 해소된 뒤에만 의존 행동을 재개한다.', verdict='불충족')
        else:
            ws.write('return.md', '# 생성 입력 보완 반환\n\n'
                     '- 관찰: ' + label + ' 호출은 Refused: ' + details + '\n'
                     '- 보존: 거절 전후 snapshot 동일. Task·수행 기록 미생성, 부모·대상 원문 무변경.\n'
                     '- 필요한 보완: ' + details + '. 누락 답은 다른 원천에 없다는 입력을 유지하며 추론하지 않는다.\n'
                     '- 다음 행동: 제공자가 누락 생성 입력을 확정한 뒤 생성 여부를 다시 판단한다.\n')
        emit(ws, label, refused=error.issues, unchanged=True)
        return error.issues
    raise AssertionError(label + ': expected protection was not applied')


def readonly(ws, callback):
    before = ws.snapshot()
    result = callback()
    assert ws.snapshot() == before
    return result


def taskfield(ws, key, value):
    set_field(ws.path('task.md'), key, value)


def deliver(ws, event_id, work):
    old = section(ws, work)
    event = ws.use_event(event_id, work)
    # use_event intentionally updates the same section; restore its prior useful facts.
    if old:
        now = section(ws, work)
        ws.record(work, old.get('조치·판단', '') + ' / ' + now['조치·판단'],
                  old.get('확인', '') + ' / 전달받은 모의 사건: ' + packed(event),
                  '사건의 종류·적용 범위를 판단한 뒤 다음 관련 행동을 정한다.', done=False)
    emit(ws, 'provider event delivered', event_id=event['id'], kind=event['kind'])
    return event


STANDARD = [
    ('survey', '두 원문의 중복과 현재 링크·허용 조건을 대조한다', '조사, 검수'),
    ('decide', 'A/B 후보·영향을 비교하고 지정 주체의 선택을 확인한다', '조사, 논의, 결정'),
    ('apply', '선택과 허용 조건을 갖춘 안내를 반영하고 관련 영향을 확인한다', '실행, 검수'),
    ('close', '전체 결과·보존·종료와 부모의 별도 수용 조건을 확인한다', '검수'),
]


def create(ws):
    if ws.creation_issues():
        refuse(ws, None, 'create_task', ws.create_task)
        return False
    if ws.path('task.md').exists():
        emit(ws, 'existing Task retained', state=field(text(ws.path('task.md')), '상태'))
        return True
    receipt = ws.create_task()
    assert receipt == {'state': '예정', 'execution_exists': False}
    assert field(text(ws.path('task.md')), '상태') == '예정'
    assert not ws.path('execution.md').exists()
    emit(ws, 'created and observed', **receipt)
    return True


def start(ws, jobs=STANDARD):
    ws.set_plan(jobs)
    taskfield(ws, '태그', ', '.join(dict.fromkeys(t.strip() for _, _, tags in jobs for t in tags.split(','))))
    taskfield(ws, '현재 합의',
              '입력의 모의 배정과 전체 계획을 적용한다. 원문 대조→후보 비교·지정 주체 선택→허용된 반영·확인→자기 종료와 부모 별도 검사의 순서다. '
              '선택 전의 조사·후보 준비만 독립 수행한다. 계획이나 자료 제공은 편집 권한을 추가하지 않는다. 실제 사용자 승인은 아니다.')
    taskfield(ws, '남은 결정', ws.input.get('pending', '없음'))
    ws.summary('진행 중', '[계획과 합의](#sequence)', '현재 입력·대상 원문과 준비·선행 조건을 읽기 전용으로 대조한다.')


def survey(ws, key='survey', done=True):
    current = text(ws.path('start.md'))
    guide = text(ws.path('guide.md')) if ws.path('guide.md').exists() else None
    observation = {
        'assignment': ws.active().name,
        'revision': field(text(ws.path('parent.md')), '전달본 식별'),
        'start_link_targets': re.findall(r'\]\(([^)]+)\)', current),
        'guide_anchors': re.findall(r'<a id="([^"]+)"', guide or ''),
        'guide_exists': guide is not None,
        'allowed_writes': ws.policy().get('allowed_writes', []),
        'user_delta': {name: text(ws.path(name)) for name, original in ws.input.get('expected_before', {}).items()
                       if ws.path(name).exists() and text(ws.path(name)) != original},
    }
    record(ws, key, '실제 시작 안내와 상세 원문을 읽고 중복·링크 문자열·명시 표식·허용 범위·기존 변경을 대조했다.',
           packed(observation) + '; 원문의 기록 위치 설명은 guide.md에서 보존한다.',
           '자료를 확보한 뒤 실제 원문 대조를 마친다.' if guide is None else '없음', done=done and guide is not None)
    return observation


def compare(ws, key='decide'):
    taskfield(ws, '남은 결정',
              '모의 사용자 역할에 질문: A안(짧은 용도 안내+상세 링크)과 B안(현재 두 설명 문장 유지+링크 정정) 중 무엇을 선택하는가? '
              '판단 기준은 중복 최소화·첫 방문자의 용도 이해·상세 기록 접근이다. start.md 반영 전에 응답을 확인한다.')
    record(ws, key,
           'A안은 "작업 상태와 상세 기록의 작성 방법을 확인하세요."와 상세 링크만 두어 설명의 원천을 guide.md에 모은다. '
           'B안은 현재 두 설명을 유지하면서 링크를 guide.md#recording으로 고친다. '
           'A는 중복 수정 위험을 줄이지만 클릭 전 상세 설명이 적고, B는 즉시 읽기 쉽지만 두 원문이 어긋날 가능성이 있다. '
           '두 문서 규모와 명시된 중복 해소 목표상 A를 권고한다. 이는 제안이며 지정한 모의 사용자 역할의 선택 전에는 확정하지 않는다.',
           '실제 start.md는 guide.md#record를 가리키며 guide.md의 명시 표식은 recording이다. '
           '현재의 두 설명은 guide.md와 중복된다. 상세 원문·표식은 보존한다. 후보의 후속 조건은 선택 응답·현재 편집 허용·원문 보존·반영 후 링크/문안 재대조다.',
           'A/B 응답을 확인한 뒤 의존 반영을 시작한다.')


def selected(ws, key, event):
    assert event['kind'] == 'choice'
    taskfield(ws, '현재 합의',
              '입력 제공자의 모의 선택 ' + str(event.get('value')) + '을 확인했다. 이유: ' + event.get('reason', event.get('content', '전달된 사건 원문 참조')) +
              '. 현재 전달본의 편집 대상·완료 조건 안에서만 반영한다. 실제 사용자 승인이 아니다. 상세: [선택 근거](execution.md#work-' + key + ').')
    taskfield(ws, '남은 결정', '없음 — 제공된 모의 선택만 확인했다. 범위·권한은 현재 전달본을 따른다.')
    record(ws, key, '실제 전달받은 모의 선택과 후보의 적용 범위를 대조했다.',
           '지정 주체 역할의 choice 사건과 이유를 확인했다. request/supply를 선택으로 해석하지 않았다.', done=True)


def desired_start(ws):
    for item in ws.policy().get('criteria', []):
        if item.get('path') == 'start.md' and item['kind'] == 'equals':
            return item['value']
    current = text(ws.path('start.md'))
    current = current.replace('Task 본문은 현재 상태와 계획을 관리합니다.\n자세한 수행 내용은 별도 수행 기록에 남깁니다.',
                              '작업 상태와 상세 기록의 작성 방법을 확인하세요.')
    return current.replace('guide.md#record)', 'guide.md#recording)').replace('guide.md#records)', 'guide.md#recording)')


def apply(ws, key='apply', files=None):
    files = files if files is not None else {'start.md': desired_start(ws)}
    ws.summary('진행 중', '[반영·확인](#work-' + key + ')', '허용된 변경을 실제 반영하고 현재 전달본 조건과 직접 참조를 대조한다.')
    result = ws.apply_files(files)
    checks = readonly(ws, lambda: ws.conditions(ws.policy()['criteria']))
    record(ws, key, '현재 원문·허용 범위·선택 근거를 확인한 뒤 ' + ', '.join(files) + '에 필요한 문안·링크 변경을 실제 저장했다.',
           packed({'write': result, 'actual_conditions': checks}) + '; 변경하지 않은 원문과 기존 사용자 문장도 실제로 재대조했다.',
           '실제 조건의 실패를 같은 할 일에서 보완한다.' if checks['issues'] else '없음', done=not checks['issues'])
    return checks


def finish(ws, key='close'):
    actual = readonly(ws, lambda: ws.conditions(ws.policy()['criteria']))
    assert not actual['issues'], actual
    assert not ws.revision_issues()
    assert (field(text(ws.path('task.md')), '남은 결정') or '').startswith('없음')
    record(ws, key, 'Task의 실제 결과·원문 보존·관리 연결·필수 확인과 종료 범위를 현재 배정에 대조했다. 시험 폴더 외의 반영·발급·커밋은 범위에 없다.',
           packed(actual), done=True)
    ws.summary('진행 중', '[종료 확인](#work-' + key + ')', 'Task 자기 조건을 검사한 뒤 Task만 완료하고 부모 전체 조건은 별도로 확인한다.')
    task_result = readonly(ws, ws.check_task)
    assert not task_result['issues'], task_result
    parent_before = text(ws.path('parent.md'))
    ws.complete_task()
    assert text(ws.path('parent.md')) == parent_before, 'child completion changed parent'
    parent_result = readonly(ws, ws.check_parent)
    record(ws, key, 'complete_task 뒤 부모 원문이 동일함을 확인했다. check_parent로 부모의 실제 전체 조건과 전달본 대응을 독립 대조했다.',
           packed({'task_check': task_result, 'parent_unchanged_after_child': True, 'parent_check': parent_result}), done=True)
    if parent_result['issues']:
        refuse(ws, key, 'accept_parent', ws.accept_parent)
        taskfield(ws, '잔여', 'Task 자기 범위는 완료. 부모는 별도 미충족: ' + packed(parent_result['issues']))
    else:
        ws.accept_parent()
        taskfield(ws, '잔여', 'Task 자기 범위와 부모의 독립 조건 검사·수용을 마쳤다. 시험 범위의 잔여 없음.')
    taskfield(ws, '내용', '현재 전달본의 실제 결과와 확인·보존·종료를 충족했다. 상세: [실제 근거](execution.md#work-' + key + '). 가상 시험이며 운영 적용은 없다.')
    ws.summary('완료', '[결과](#result)', '이 시험 단위의 실제 결과·근거를 판정자에게 인계한다.')
    emit(ws, 'Task completion and separate parent inspection', task_state='완료', parent_state=field(text(ws.path('parent.md')), '상태'))


def stop(ws, key, reason, decision, state='중단'):
    ws.summary(state, '[현재 근거](#work-' + key + ')', decision, reason)
    taskfield(ws, '내용', '허용된 원문 대조·후보/계획 준비 결과를 보존했다. 의존 반영과 목표 달성은 미완료다. [근거](execution.md#work-' + key + ').')
    taskfield(ws, '확인', packed(readonly(ws, ws.check_task)))
    taskfield(ws, '잔여', reason + ' 다음 행동: ' + decision)
    emit(ws, 'current limitation retained', state=state, remaining=reason)


def initial(names):
    for name in names:
        ws = Workspace(BASE / 'cases' / name)
        if not create(ws):
            continue
        if ws.path('execution.md').exists():
            continue
        start(ws)
        survey(ws)
        if ws.path('guide.md').exists():
            compare(ws)


def compare_methods(ws):
    assert create(ws)
    start(ws, [
        ('compare', '두 원문을 읽고 수동 대조와 로컬 검사 방법을 비교한다', '조사'),
        ('decide', '비교 기준과 후속 조건을 제시하고 방법 선택 응답을 확인한다', '논의, 결정'),
        ('close', '선정·이유·한계·후속 조건과 범위 보존을 대조한다', '검수'),
    ])
    taskfield(ws, '현재 합의', '원문 검토·방법 비교·논의만 허용한다. 파일 수정·검사기 작성·실행은 미배정이다. 선택 응답 후 선정·이유·후속 조건의 정리만 마친다.')
    start_text, guide_text = text(ws.path('start.md')), text(ws.path('guide.md'))
    assert 'guide.md#record)' in start_text and 'id="recording"' in guide_text
    record(ws, 'compare',
           '수동 방법은 두 원문의 상대 경로와 recording 표식을 읽어 대조한다. 준비 비용이 작고 의미·중복·현재 두 문서 범위를 함께 볼 수 있지만 반복 재현과 누락 방지는 검토자에 의존한다. '
           '로컬 검사 방법은 경로·표식을 자동 추출해 대상 존재를 검사하므로 다수 문서의 반복 재현에 유리하다. 반면 검사기 준비·오탐 처리·실행 환경 유지가 필요하고 문안의 의미나 중복까지 결정하지 못한다. '
           '판단 기준은 두 문서라는 현재 범위, 준비 비용, 재현 요구, 의미 확인 가능성이다. 현 범위에서는 수동을 권고하되 지정 주체 응답 전에는 선정하지 않는다.',
           '실제 원문을 읽어 start.md의 guide.md#record와 guide.md의 recording 표식 차이를 확인했다. 두 설명 문장도 중복된다. '
           '이 비교의 후속 조건: 범위가 늘거나 반복 재현 요구가 생기면 로컬 방법의 준비·허용을 별도 논의한다. 현재 파일 수정·검사기 작성·실행은 하지 않았다.', done=True)
    taskfield(ws, '남은 결정', '모의 사용자 역할에 질문: 현재 두 원문은 준비 비용과 의미 검토를 중시해 수동 대조를 선택하는가, 반복 재현을 중시해 로컬 검사 준비를 후속 논의하는가? 선정 기록 전에 응답을 확인한다.')
    record(ws, 'decide', '수동/로컬의 비교·권고·후속 조건과 현재 허용 범위를 제시하고 지정 주체에 선택을 질문했다.',
           '방법 비교는 실행 허용이 아니다. 아직 방법 선택 응답은 미제공이다.', 'method 모의 응답을 확인한다.')
    event = deliver(ws, 'method', 'decide')
    selected(ws, 'decide', event)
    return event


def supplied_source(ws):
    assert create(ws)
    start(ws, [
        ('source', '미제공 상세 원문을 확보하고 실제 내용을 대조한다', '조사'),
        ('assess', '자료 확보와 편집 권한·선택 조건을 구별한다', '조사, 논의, 검수'),
        ('close', '허용된 준비의 결과와 미충족을 보존해 반환한다', '검수'),
    ])
    taskfield(ws, '현재 합의', '현재 허용은 생성·계획과 확보 원문의 읽기 전용 대조다. supply는 자료 제공이며 편집 허용·A/B 선택이 아니다.')
    survey(ws, 'source', done=False)
    refuse(ws, 'assess', 'apply_files before source', lambda: ws.apply_files({'start.md': desired_start(ws)}))
    event = deliver(ws, 'supply', 'source')
    assert event['kind'] == 'supply'
    survey(ws, 'source')
    taskfield(ws, '대상·준비', 'supply 모의 사건으로 guide.md를 확보해 실제 원문을 읽었다. 편집 허용은 없으며 A/B 선택도 제공되지 않았다. [확보·대조 근거](execution.md#work-source).')
    refuse(ws, 'assess', 'apply_files after source', lambda: ws.apply_files({'start.md': desired_start(ws)}))
    record(ws, 'assess', '자료의 실제 부재는 해소했지만 allowed_writes는 여전히 비어 있고 choice 사건은 없다. 확보 원문을 읽어 recording 표식과 현재 record 링크의 차이를 확인했다.',
           '자료 제공을 새 편집 허용이나 사용자 선택으로 해석하지 않았다. 준비 결과와 남은 질문을 반환한다.',
           '없음 — 이 할 일의 구별·검수는 마쳤다. 전체 미충족은 Task 요약과 종료 할 일에서 관리한다.', done=True)
    refuse(ws, 'close', 'complete_task with unavailable authority and choice', ws.complete_task)
    stop(ws, 'assess', '상세 자료는 확보했으나 편집 허용·A/B 선택이 없고 현재 링크가 불일치한다.',
         '제공자 역할에서 현재 편집 허용과 A/B 선택을 확정하면 영향받는 계획·조건을 다시 확인한다.')


def move_guide(ws):
    assert create(ws)
    start(ws, [
        ('move', 'guide의 내용·표식을 보존해 이동하고 세 문서의 왕복 링크를 보정한다', '조사, 실행, 검수'),
        ('close', '이전 경로 부재·새 원문 보존·모든 상대 링크와 종료를 확인한다', '검수'),
    ])
    taskfield(ws, '현재 합의', '현재 전달본이 guide.md→guides/recording.md 이동과 세 문서의 상대 링크 보정을 확정했다. 별도 문안 선택은 없다. 본문·recording 표식을 보존한다.')
    survey(ws, 'move')
    original = text(ws.path('guide.md'))
    record(ws, 'move', '이동의 원본·목적 절대 경로가 이 시험 폴더 안에 있고 목적 파일은 아직 없음을 확인했다.',
           packed({'source': str(ws.path('guide.md')), 'destination': str(ws.path('guides/recording.md'))}),
           '실제 이동과 세 문서 상대 링크 보정·검증이 남아 있다.')
    moved = ws.move_file('guide.md', 'guides/recording.md')
    assert not ws.path('guide.md').exists() and text(ws.path('guides/recording.md')) == original
    files = {
        'start.md': text(ws.path('start.md')).replace('(guide.md#recording)', '(guides/recording.md#recording)'),
        'index.md': text(ws.path('index.md')).replace('(guide.md#recording)', '(guides/recording.md#recording)'),
        'guides/recording.md': original.replace('(start.md)', '(../start.md)'),
    }
    checks = apply(ws, 'move', files)
    record(ws, 'move', '허용된 이동을 실제 수행했다. 본문·recording 표식은 그대로 두고 들어오는 두 링크와 나가는 한 상대 링크만 최종 위치 기준으로 보정했다.',
           packed({'move': moved, 'conditions': checks}), done=not checks['issues'])


def guard_pending(ws):
    refuse(ws, 'decide', 'apply_files before required choice', lambda: ws.apply_files({'start.md': desired_start(ws)}))


def continue_selection(ws):
    guard_pending(ws)
    event = deliver(ws, 'selection', 'decide')
    selected(ws, 'decide', event)
    apply(ws)
    return event


def recover_existing(ws):
    assert ws.path('task.md').exists() and ws.path('execution.md').exists()
    original_state = field(text(ws.path('task.md')), '상태')
    original_checks = readonly(ws, ws.check_task)
    if original_state == '완료' and original_checks['issues']:
        refuse(ws, 'recover', 'complete_task against inconsistent completed seed', ws.complete_task)
    record(ws, 'recover',
           '기존 Task·수행 기록과 work-recover/work-close 식별자는 초기화하지 않고 실제 입력·대상·부모 배정과 대조했다. '
           '기존 가상 사전 상태는 이번 실행의 과거 수행 사실이 아니다.',
           packed({'initial_task_state': original_state, 'initial_actual_check': original_checks}),
           '실제 결함·배정 불일치·사용자 변경의 영향을 판단한 뒤 허용된 부분을 보완한다.')
    record(ws, 'close', '기존 전체 결과·종료 체크와 실제 근거를 대조했다. 초기 미충족을 그대로 보존하고 목표 완료를 재판정한다.',
           packed(original_checks), '현재 실제 조건과 보존·종료 확인이 남아 있다.')
    ws.summary('진행 중', '[실제 상태 대조·보완](#work-recover)', '현재 배정·저장본·사용자 변경을 대조한 뒤 허용된 보완을 수행한다.')
    survey(ws, 'recover', done=False)
    drift = ws.revision_issues()
    if drift:
        refuse(ws, 'recover', 'apply_files before adopting supplied parent revision',
               lambda: ws.apply_files({'start.md': desired_start(ws)}))
        old_reference = field(text(ws.path('task.md')), '적용 전달본')
        old_revision = field(text(ws.path('task.md')), '전달본 식별')
        ws.adopt_revision()
        taskfield(ws, '현재 합의',
                  '부모가 이미 확정해 제공한 ' + ws.active().name + '을 채택했다. 기존 ' + str(old_revision) + ' 전달본과 수행 근거는 보존한다. '
                  '현재 문안·확인 조건의 영향을 work-recover에서 다시 확인한다. 초기 A 선택은 제공된 모의 근거이며 실제 사용자 승인이 아니다. [개정 영향](execution.md#work-recover).')
        record(ws, 'recover', '부모가 확정한 개정본을 실제 읽고 adopt_revision으로 Task 참조를 맞췄다. 새로운 배정이나 권한을 대신 정하지 않았다.',
               packed({'old_reference': old_reference, 'old_revision': old_revision,
                       'adopted_reference': field(text(ws.path('task.md')), '적용 전달본'),
                       'adopted_revision': field(text(ws.path('task.md')), '전달본 식별'),
                       'current_policy': ws.policy()}), '영향받는 실제 파일·문안과 전체 조건을 재대조한다.')
    else:
        taskfield(ws, '현재 합의',
                  '기존 모의 A 선택과 현재 전달본을 적용한다. 실제 저장·미수행·미확인과 기존 사용자 변경을 구별한다. '
                  '이 배정 안의 오류 보완과 비충돌 문장 보존만 수행한다. [복구 근거](execution.md#work-recover).')
    deltas = {name: text(ws.path(name)) for name, old in ws.input.get('expected_before', {}).items()
              if ws.path(name).exists() and text(ws.path(name)) != old}
    if deltas:
        refuse(ws, 'recover', 'apply_files against overlapping user change',
               lambda: ws.apply_files({'start.md': desired_start(ws)}))
        taskfield(ws, '남은 결정',
                  '모의 사용자 역할에 질문: 이전 A 선택 뒤 겹친 현재 사용자 문장을 그대로 유지할지, 축약할지 새로 합의해야 한다. '
                  '충돌 해소 응답은 미제공이며 이전 선택으로 덮어쓸 수 없다. 반영 전에 범위와 문안을 확인한다.')
        taskfield(ws, '현재 합의',
                  '과거 모의 A 선택은 보존한다. 이후 같은 문장에 생긴 사용자 변경은 새 충돌이므로 현재 원문을 보존한다. '
                  '새 충돌 해소 선택이 없어 의존 반영·완료를 제한한다. [충돌 근거](execution.md#work-recover).')
        refuse(ws, 'close', 'complete_task with user conflict unresolved', ws.complete_task)
        refuse(ws, 'close', 'accept_parent with user conflict unresolved', ws.accept_parent)
        stop(ws, 'recover', '기존 선택 이후 겹치는 사용자 변경이 있고 새 충돌 해소 응답은 없다.',
             '현재 사용자 문장·이전 선택 근거를 보존해 새 문안과 편집 범위를 제공자 역할에 확인한다.')
        return
    taskfield(ws, '남은 결정', '없음 — 초기 모의 선택과 현재 확정 전달본을 적용하며 충돌 없는 사용자 문장은 보존한다.')
    if original_state == '중단':
        record(ws, 'recover', '저장된 링크 보정은 유지하고 아직 남은 중복 제거만 실제 수행한다. 추가 사용자 문장은 비충돌이므로 보존한다.',
               '링크는 이미 recording으로 저장돼 있으나 저장 뒤 검증 근거가 없었고 중복 설명은 아직 남아 있었다. 이전 다음 행동을 실제 잔여에 맞췄다.',
               '중복 제거 후 사용자 문장·상세 원문·링크를 재확인한다.')
    checks = apply(ws, 'recover')
    assert not checks['issues'], checks
    finish(ws)


def planning_observation(ws):
    # Reorganize the remaining result and its checks together without executing them.
    jobs = list(STANDARD)
    jobs[2] = ('apply', '선택된 문안 반영·링크와 보존 검증을 한 단위로 수행한다', '실행, 검수')
    ws.set_plan(jobs)
    taskfield(ws, '현재 합의',
              '이번 관찰 범위는 초기 원문 대조 후 계획 조정까지다. 반영·확인은 같은 변경본과 근거로 충족되므로 미착수 apply 한 단위로 구체화한다. '
              '별도 전체 종료 close는 유지한다. 기존 survey 식별자·완료 근거와 decide 질문·미선택을 보존했다. '
              '태그·계획 조정은 실행 권한이나 A/B 선택이 아니다. [조정 근거](execution.md#work-decide).')
    record(ws, 'decide', '원문 대조 근거를 유지하며 남은 반영과 직접 검증을 apply로 묶어 계획을 구체화했다. 같은 결과·근거를 함께 다루므로 재배열로 필요한 검증이 빠지지 않는다.',
           'survey의 식별자·완료 체크·수행 링크와 decide의 A/B 질문은 유지했다. apply·close는 미완료이며 실제 대상 파일은 그대로다. 선택 응답은 제공되지 않았다.',
           '이번 관찰은 계획 조정까지이며, 선택과 반영은 후속 허용 범위에서 판단한다.')
    taskfield(ws, '내용', '원문 대조와 전체 계획 조정까지만 수행했다. 안내 수정·목표 완료는 미수행이다. [계획 조정](execution.md#work-decide).')
    taskfield(ws, '확인', '실제 대상 파일은 입력 원문과 동일하다. 기존 작업 식별자·근거·선택 조건을 보존했고 반영·확인·종료는 미완료다.')
    taskfield(ws, '잔여', 'A/B 응답, 허용된 반영·직접 검증·전체 자기 수용과 부모 별도 수용은 남아 있다.')
    ws.summary('진행 중', '[계획 조정](#work-decide)', '제공된 관찰 범위에서 계획과 미결 질문을 인계한다. 후속 허용 범위가 정해지면 선택 단계부터 이어간다.')
    emit(ws, 'planning observation retained', state='진행 중', payload_unchanged=True)


if __name__ == '__main__':
    if sys.argv[1] == 'initial':
        initial(sys.argv[2:])
