"""Apply the documented scenarios to isolated Markdown files; no product actions."""

from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT.parent
SPEC = ARTIFACTS / 'task-document-management-test-cases.md'
TASK_SOURCE = ARTIFACTS / 'task-body-template-draft.md'
EXECUTION_SOURCE = ARTIFACTS / 'task-execution-template-draft.md'
SOURCE = SPEC.read_text(encoding='utf-8')
BLOCKS = re.findall(r'```markdown\n(.*?)\n```', SOURCE, re.S)
START, GUIDE = [block + '\n' for block in BLOCKS]
A = '# 시작 안내\n\n작업 상태와 상세 기록의 작성 방법을 확인하세요.\n\n[기록 방법 보기](guide.md#recording)\n'
NOTE = '이 안내는 내부 작업자를 위한 것입니다.'
USER_MODE = '고정된 시험 입력으로 일괄 모의 수행 (추천)'
RESULTS = []


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def write(path, text):
    path = path.resolve()
    path.relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def read(path):
    return path.read_text(encoding='utf-8')


def rule_blocks(text, kind):
    return re.findall(r'<!-- ' + kind + r'-rule:[\s\S]*?-->', text)


def link_ok(folder, filename='start.md'):
    for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', read(folder / filename)):
        file, _, anchor = target.partition('#')
        dest = (folder / filename).parent / file
        if not dest.is_file() or (anchor and f'<a id="{anchor}"></a>' not in read(dest)):
            return False
    return True


class Trial:
    """Mechanical file editing only; each scenario below supplies its decisions."""

    def __init__(self, number, goal, scope, tags='조사, 논의, 결정, 실행, 검수', guide=True):
        self.number = number
        self.folder = ROOT / f'tc-{number:02}'
        self.folder.mkdir(exist_ok=False)
        self.jobs = []
        self.records = []
        self.goal = goal
        self.tags = tags
        self.parent_state = '진행 중'
        write(self.folder / 'start.md', START)
        if guide:
            write(self.folder / 'guide.md', GUIDE)
        mission = ('두 문서의 링크 점검 방법을 비교하고 가상 사용자 선택·이유·후속 조건을 정리한다.' if number == 3 else
                   '상세 문서를 이동하고 들어오고 나가는 현재 링크·표식·본문 보존을 확인한다.' if number == 11 else
                   '시작 안내의 잘못된 링크와 상세 설명 중복을 정리하고 선택·확인 근거를 남긴다.')
        acceptance = ('수동 대조와 로컬 검사 방식을 재현 가능성·준비 부담·이번 두 문서의 확인 범위로 비교한다. '
                      '가상 선택·이유·후속 조건을 기록한다. 검사기 실행·문서 수정 성공은 조건이 아니다.' if number == 3 else
                      '이전 파일이 새 위치로 이동하고 start.md·index.md·이동 문서의 세 현재 링크가 최종 위치에서 유효하다. '
                      '기존 표식·본문·범위 밖 내용을 보존한다. 상세 설명 중복 해소는 맡기지 않는다.' if number == 11 else
                      '실제 링크 대상 파일·표식, 두 상세 문장의 중복 제거, 선택 입력과 반영 일치, 원문·범위 밖 내용 보존을 대조한다. '
                      '중단·취소·부분 진행에서는 이 전체 목표의 미충족·잔여를 유지한다.')
        self.assignment = (
            '# 시험용 Task T 전달사항\n\n- 태그: ' + tags + '\n\n'
            '<a id="purpose"></a>\n## 목적\n\n' + mission + '\n\n'
            '<a id="result"></a>\n## 기대 결과\n\n' + mission + '\n\n'
            '<a id="scope"></a>\n## 이미 정해진 조건\n\n' + scope + '\n'
            '조건의 근거는 [시험용 부모](parent.md#assignment)다. 모든 사용자 역할 사건은 모의 입력이다.\n\n'
            '<a id="decisions"></a>\n## Task에서 결정할 사항\n\n'
            '사례에서 맡긴 선택만 결정한다. 필요한 응답은 승인된 모의 입력으로 제공하며 실제 사용자 승인으로 쓰지 않는다.\n\n'
            '<a id="acceptance"></a>\n## 완료 조건과 확인 방법\n\n'
            + acceptance + '\n'
        )
        write(self.folder / 'assignment.md', self.assignment)
        self.assignment_sha = digest(self.assignment)
        self.parent('진행 중', '미판정 — 자식 결과와 실제 대상의 별도 대조 전이다.')
        source = read(TASK_SOURCE)
        body = re.search(r'```markdown\n(.*?)\n```', source, re.S).group(1) + '\n'
        fields = {
            '<부모 Issue 번호>-<로컬 순번>': 'T — 가상 시험',
            '<작업 제목>': f'TC-{number:02} — {goal}',
            '<조사·논의·결정·실행·검수·커밋 중 필요한 여러 개를 쉼표로 구분>': tags,
            '(task-common-procedure-draft.md)': '(../../task-common-procedure-draft.md)',
            '<저장소·번호·URL>': '미생성 — 가상 역할 P/T, 정식 번호 아님',
            '<본문의 실제 작업·근거 구역 링크>': '[계획과 합의](#sequence)',
            '<현재 허용된 대상과 행동>': '이 사례의 전체 계획을 구체화한다.',
            '<제한되는 행동·미충족 조건·해소 조건·근거>': '전달사항의 선행 조건·선택을 확인한다.',
            '<실제 부모 기록 링크>': '[시험용 부모 P](parent.md#children)',
            '<확정 전달사항 파일 또는 합의한 개정본 링크>': '[전달사항](assignment.md)',
            '<r001 또는 실제 개정 식별>': 'r001 — 시험 초판',
            '<원본 경로·전달본 식별·확정 근거가 있는 Issue의 배정 결정 링크>': '[부모 기준 기록](parent.md#assignment)',
            '<실제 대상·입력과 필요한 선행 결과·등록·브랜치 등의 확보 상태와 제한>': '분리된 시험 폴더. 실제 번호·외부 등록은 없다. 입력 확보 상태는 각 할 일에서 확인한다.',
            '<결정·이유·근거·위임 범위·사용자 확인 조건. 공통 조건·커밋 묶음은 필요한 때 한 번만 정의>': '배정은 부모 기준 기록을 따른다. 사용자 역할 사건은 모의 입력이며 실제 제품 권한을 만들지 않는다.',
            '<질문·판단 기준·결정 주체·필요한 시점>': '사례의 미결 사항을 계획에서 확인한다.',
            '<전달본 완료 조건별 확인 계획>': '해당 사례의 결과·관찰 기준과 실제 파일·응답 입력을 대조한다.',
            '<artifacts/task-실제순번-execution.md. 생성 후 실제 링크로 전환>': 'execution.md — 시험용 예정 경로',
            '<작업식별자>': 'pending',
            '<대상과 행동이 드러나는 할 일 이름>': '미정 — 생성 후 계획에서 구체화',
            '<해당 행동에 필요한 태그 여러 개. 아직 판별하지 못했으면 미확인>': '미확인',
            '<수행할 대상·행동·남길 결과. 필요한 선행 조건·담당 역할·사용자 확인 시점은 공통 조건 또는 여기에서 명시>': '미정 — 생성 시 결과·합의를 채우지 않았다.',
            '<이 행동의 완료를 판단할 대상·방법·기준과 필요한 근거>': '계획에서 구체화한다.',
            '<미착수는 artifacts/task-실제순번-execution.md#work-작업식별자 예정 경로, 착수 후 실제 구역 링크>': '미생성 — 예정 경로만 둔다.',
            '<실제 결과가 발생한 뒤 전체 결과·반영 범위와 현재 결론>': '미발생.',
            '<완료 조건별 판정·근거·한계. 상세는 실제 수행 기록의 해당 구역 연결>': '미실시.',
            '<미반영·미해결·재개 조건과 다음 행동. 없음을 확인했으면 없음>': '해당 배정의 미수행 결과.',
        }
        for old, new in fields.items():
            assert old in body, old
            body = body.replace(old, new)
        assert rule_blocks(body, 'task') == rule_blocks(source, 'task')
        write(self.folder / 'task.md', body)
        assert '- 상태: 예정' in body and not (self.folder / 'execution.md').exists()

    def parent(self, state, judgment):
        self.parent_state = state
        assignment_block = ('<a id="assignment"></a>\n## 배정 기준 기록\n\n'
                            '- 원본: [전달사항](assignment.md)\n- 전달본: r001 — 시험 안의 초판\n'
                            '- 근거: 사례 입력과 사용자가 선택한 일괄 모의 수행 방식.\n\n')
        if (self.folder / 'parent.md').exists():
            existing = read(self.folder / 'parent.md')
            assignment_block = existing[existing.index('<a id="assignment">'):existing.index('<a id="children">')]
        write(self.folder / 'parent.md',
              f'# TC-{self.number:02} 시험용 부모 P\n\n'
              '가상 부모·자식이며 정식 Issue/Task 번호나 실제 사용자 승인 기록이 아니다.\n\n'
              f'- 상태: {state}\n- 역할·설정: [일괄 시험](../run.md#setup)\n'
              f'- 적용 사례: [TC-{self.number:02}](../../task-document-management-test-cases.md#case-{self.number:02})\n\n'
              + assignment_block +
              '<a id="children"></a>\n## 보유 자식\n\n[시험용 Task T](task.md#summary)\n\n'
              '<a id="acceptance"></a>\n## 전체 수용과 잔여\n\n' + judgment + '\n')

    def field(self, name, value):
        path = self.folder / 'task.md'
        body, count = re.subn(r'^- ' + re.escape(name) + r': .*$', '- ' + name + ': ' + value,
                             read(path), count=1, flags=re.M)
        assert count == 1, name
        write(path, body)

    def summary(self, state, current, next_action, blocked='없음'):
        for key, value in [('상태', state), ('현재 진행 위치', current), ('다음 행동', next_action), ('막힌 조건', blocked)]:
            self.field(key, value)

    def plan(self, jobs):
        old = {job['id']: job for job in self.jobs}
        self.jobs = [dict(id=key, title=title, tags=tags, done=old.get(key, {}).get('done', False))
                     for key, title, tags in jobs]
        self.sync_plan()
        if not old:
            self.field('현재 합의', '모의 계획 합의 입력: 이 사례의 아래 전체 계획과 준비를 확인했다. 실제 사용자는 일괄 모의 수행 방식을 선택했으며 개별 가상 선택·취소·배정 개정은 실제 승인으로 쓰지 않는다.')

    def sync_plan(self):
        path = self.folder / 'task.md'
        body = read(path)
        marker = '<!-- task-rule:execution'
        start = body.index('-->', body.index(marker)) + 3
        end = body.index('<a id="result"></a>', start)
        sections = []
        for job in self.jobs:
            key = job['id']
            reference = (f'[수행 기록](execution.md#work-{key})' if key in self.records
                         else f'execution.md#work-{key} — 미착수 예정 경로')
            sections.append(f'<a id="work-{key}"></a>\n#### {job["title"]}\n\n'
                            f'- 태그: {job["tags"]}\n- [{"x" if job["done"] else " "}] 수행·확인 완료\n'
                            f'- 할 일: {job["title"]}. 배정·선행 조건과 현재 합의 범위에서 수행한다.\n'
                            '- 확인: 이 행동의 실제 결과·입력·제한을 사례의 관찰 기준과 대조한다.\n'
                            f'- 수행 기록: {reference}.\n')
        write(path, body[:start] + '\n\n' + '\n'.join(sections) + '\n' + body[end:])

    def record(self, key, action, observation, remaining='없음', done=True):
        job = next(job for job in self.jobs if job['id'] == key)
        if '- 상태: 예정\n' in read(self.folder / 'task.md'):
            self.summary('진행 중', f'[현재 할 일](#work-{key})', job['title'] + '을 진행한다.')
        path = self.folder / 'execution.md'
        if not path.exists():
            source = read(EXECUTION_SOURCE)
            body = re.search(r'```markdown\n(.*?)\n```', source, re.S).group(1)
            header = body.split('<a id="work-', 1)[0]
            header = header.replace('<부모 Issue 번호>-<실제 순번>', 'T — 가상 시험')
            header = header.replace('<실제 Task 본문 링크>', '[시험용 Task T](task.md#sequence)')
            header = header.replace('(task-common-procedure-draft.md#recording-proposal)',
                                    '(../../task-common-procedure-draft.md#recording-proposal)')
            write(path, header)
            self.field('수행 기록', '[실제 수행 기록](execution.md)')
        section = (f'<a id="work-{key}"></a>\n## {job["title"]}\n\n'
                   f'- 할 일: [{job["title"]}](task.md#work-{key})\n\n'
                   f'- 조치·판단: {action}\n- 확인: {observation}\n- 잔여: {remaining}\n')
        current = read(path)
        if key in self.records:
            pattern = r'<a id="work-' + re.escape(key) + r'"></a>[\s\S]*?(?=\n<a id="work-|\Z)'
            current, count = re.subn(pattern, lambda match: section, current, count=1)
            assert count == 1
        else:
            current += '\n' + section
            self.records.append(key)
        write(path, current)
        job['done'] = done
        self.sync_plan()

    def result(self, content, checked, remaining):
        self.field('내용', content)
        self.field('확인', checked)
        self.field('잔여', remaining)

    def inspect(self):
        self.summary('진행 중', '[원문 대조](#work-inspect)', '배정 안의 원문을 대조한다.')
        assert read(self.folder / 'start.md') == START
        assert read(self.folder / 'guide.md') == GUIDE
        assert not link_ok(self.folder)
        self.record('inspect', '두 시험 원문을 실제로 대조하고 A/B 후보를 비교했다. 파일은 수정하지 않았다.',
                    '기록 링크의 record와 실제 recording이 다르고 상세 두 문장이 중복된다. 후보는 아직 미선정이다.')

    def choose_a(self, reason='가상 사용자 역할의 A안 선택'):
        self.field('현재 합의', '모의 입력: ' + reason + '. 적용 대상은 이 시험의 start.md다. 실제 사용자 선택·제품 권한이 아니다.')
        self.field('남은 결정', '없음 — 시험 입력에서 A안을 지정했다.')
        self.record('choose', '모의 A안 선택 사건을 확인하고 현재 합의·남은 결정·다음 행동을 갱신했다.',
                    '시험용 선택이 지정된 주체·범위에 맞다. 실제 사용자 응답으로 기록하지 않았다.')

    def apply_a(self, expected_guide=GUIDE, value=A):
        self.summary('진행 중', '[반영·확인](#work-apply)', '선택한 시험 문안을 허용 범위에 반영한다.')
        write(self.folder / 'start.md', value)
        assert link_ok(self.folder)
        assert read(self.folder / 'guide.md') == expected_guide
        for sentence in ['Task 본문은 현재 상태와 계획을 관리합니다.', '자세한 수행 내용은 별도 수행 기록에 남깁니다.']:
            assert sentence not in read(self.folder / 'start.md')
        self.record('apply', '모의 선택과 현재 배정·선행 결과를 확인하고 허용된 문안을 반영했다.',
                    '실제 링크·표식, 상세 중복 해소, 입력의 A안 선택, 원문·범위 밖 보존을 대조해 충족했다.')

    def complete(self, result):
        assert all(job['done'] for job in self.jobs if job['id'] != 'close')
        self.record('close', '배정 결과와 수행·판정·연결·보존을 대조했다.',
                    '자기 결과와 종료 조건을 충족했다. 부모 수용은 별도로 대조한다.')
        self.result(result, '현재 배정과 해당 사례의 결과 조건 충족. 상세는 [수행 기록](execution.md).',
                    'Task 자기 범위의 잔여 없음. 부모의 전체 수용은 별도다.')
        self.summary('완료', '[결과](#result)', '부모가 실제 결과와 전체 수용 조건을 별도로 대조한다.')
        assert '- 상태: 진행 중' in read(self.folder / 'parent.md')
        assert result in read(self.folder / 'task.md')
        self.parent('완료', '자식 완료 뒤에도 부모가 진행 중·미판정임을 먼저 확인했다. '
                    '[Task 결과](task.md#result)와 실제 대상·모의 입력을 별도로 대조해 이 시험용 부모의 결과를 수용했다. '
                    '실제 사용자 전체 승인이나 실제 Issue 완료가 아니다. 잔여 없음.')

    def finish(self, observation, expected_state):
        assert re.search(r'^- 상태: (.+)$', read(self.folder / 'task.md'), re.M)[1] == expected_state
        assert rule_blocks(read(self.folder / 'task.md'), 'task') == rule_blocks(read(TASK_SOURCE), 'task')
        if (self.folder / 'execution.md').exists():
            text = read(self.folder / 'execution.md')
            assert rule_blocks(text, 'execution') == rule_blocks(read(EXECUTION_SOURCE), 'execution')
            assert text.index('<!-- execution-rule:') < text.index('<a id="work-')
            assert len(re.findall(r'<!-- execution-rule:', text)) == 1
            for key in self.records:
                assert f'execution.md#work-{key}' in read(self.folder / 'task.md')
                assert f'task.md#work-{key}' in text
        assert digest(read(self.folder / 'assignment.md')) == self.assignment_sha
        RESULTS.append((self.number, '충족', expected_state, observation, f'tc-{self.number:02}/task.md#result'))


STANDARD = [('inspect', '원문 대조와 후보 작성', '조사, 검수'),
            ('choose', '안내 방식 논의·선택', '논의, 결정'),
            ('apply', '선택 반영·확인', '실행, 검수'),
            ('close', '결과 검수·종료', '검수')]
SCOPE = '두 원문을 읽고 start.md만 수정한다. guide.md를 보존한다. 안내 방식은 모의 사용자 선택 뒤 반영한다.'


def run_cases():
    # TC-01 uses the actual interactive run; do not rewrite its files.
    first = ARTIFACTS / 'task-doc-tc01-a'
    assert '- 상태: 완료' in read(first / 'task.md')
    assert read(first / 'start.md') == A and read(first / 'guide.md') == GUIDE
    RESULTS.append((1, '충족', '완료', '기존 실제 A안 응답·종료 결과 재대조', '../task-doc-tc01-a/task.md#result'))

    # TC-02: return missing information, without generating a Task.
    folder = ROOT / 'tc-02'
    folder.mkdir(exist_ok=False)
    variants = [('담당 결과 부족', '결과·범위·결정 주체·수용 기준을 확정해 주세요.'),
                ('수용 기준 부족', '완료 조건과 확인 대상·방법을 보완해 주세요.'),
                ('식별 정보 부족', '부모 목록·파일·사용 이력으로 식별·저장 위치·충돌 확인을 보완해 주세요.')]
    rows = '\n'.join(f'| {kind} | {answer} | 미생성 |' for kind, answer in variants)
    write(folder / 'case.md', '# TC-02 생성 보류\n\n입력은 세 독립 변형이며 빠진 답이 다른 원천에도 없다는 조건이다.\n\n'
          '<a id="result"></a>\n## 반환과 판정\n\n| 입력 | 실제 반환한 보완 요청 | Task |\n|---|---|---|\n' + rows +
          '\n\n담당 결과 부족을 Task 내부 문안의 미정으로 대신하지 않았다. 임의 번호·경로·수용 기준을 채우지 않았다.\n')
    assert not (folder / 'task.md').exists() and not (folder / 'execution.md').exists()
    assert len(variants) == 3
    RESULTS.append((2, '충족', '미생성', '독립 부족 입력 3개에서 보완 요청·미생성 확인', 'tc-02/case.md#result'))

    t = Trial(3, '링크 점검 방법의 비교·선정과 후속 조건 정리',
              '원문 검토·비교·논의만 허용한다. 두 방법을 재현 가능성·준비 부담·두 문서의 확인 범위로 비교한다. 검사기 작성·실행·문서 수정은 맡기지 않는다.',
              tags='조사, 논의, 결정, 검수')
    t.plan([('compare', '방법 비교', '조사, 검수'), ('choose', '방법 선정', '논의, 결정'), ('close', '결과 검수·종료', '검수')])
    t.field('남은 결정', '수동 대조와 로컬 검사 중 가상 사용자 역할이 비교 뒤 선택한다.')
    t.record('compare', '실제 두 원문을 읽고 수동 대조와 로컬 검사 방식을 같은 기준으로 비교했다.',
             '수동은 대상 두 파일·표식의 절차를 지정하면 재현할 수 있고 추가 실행 환경이 필요 없다. '
             '로컬 검사는 정의·환경 준비와 오탐 범위 확인이 필요하며 구현·실행하지 않았으므로 실제 검출 능력은 미확인이다. '
             '이번 두 문서의 경로·표식 비교에는 수동 대조를 적용할 수 있다.')
    t.field('현재 합의', '모의 입력: 수동 대조를 선택한다. 이유는 두 문서에서 추가 환경 없이 경로·표식을 확인하기 위해서다. 실제 사용자 선택이 아니다.')
    t.field('남은 결정', '없음 — 모의 방법 선택 완료.')
    t.record('choose', '모의 사용자 역할이 수동 대조를 선택했다.', '선택·이유·후속 입력 조건을 기록했다. 실행 허용으로 확대하지 않았다.')
    assert read(t.folder / 'start.md') == START and read(t.folder / 'guide.md') == GUIDE
    t.complete('방법 비교·모의 선택·이유·후속 조건을 정리했다. 실제 문서 수정·검사기 실행은 하지 않았다.')
    t.finish('방법 미정 상태의 생성 허용과 비교·선정 범위 준수', '완료')

    t = Trial(4, '후속 자료 미확보 상태의 생성·독립 활동·재개',
              '현재 허용은 생성·계획과 제공된 원문의 읽기 전용 대조다. guide.md는 가상 사용자 역할이 제공하며 대상 확정·검증 전 필요하다. 자료 확보가 수정 허용은 아니다.', guide=False)
    assert not (t.folder / 'guide.md').exists()
    t.plan([('inspect', '확보한 원문 대조', '조사, 검수'), ('source', '후속 자료 확인', '조사, 검수')])
    t.summary('진행 중', '[확보 원문](#work-inspect)', '이미 허용된 읽기 전용 대조를 진행한다.', 'guide.md 원문 미확보. 연결 성공·수정·검증을 추론하지 않는다.')
    assert read(t.folder / 'start.md') == START and not (t.folder / 'guide.md').exists()
    t.record('inspect', '확보된 start.md만 읽었다.', '현재 링크 문자열은 관찰했지만 미제공 파일·표식의 정답은 확정하지 않았다.')
    t.summary('중단', '[후속 자료](#work-source)', '가상 사용자 역할의 원문 제공을 기다린다.', 'guide.md 원문 필요. 다른 독립 활동은 마쳤다.')
    assert '- 상태: 중단' in read(t.folder / 'task.md')
    write(t.folder / 'guide.md', GUIDE)  # Authorized simulated provision, only now.
    t.summary('진행 중', '[후속 자료](#work-source)', '제공받은 실제 시험 파일을 읽기 전용으로 확인한다.')
    assert '<a id="recording"></a>' in read(t.folder / 'guide.md')
    t.record('source', '모의 원문 제공 사건 뒤 실제 파일을 읽어 준비를 재확인하고 재개했다.',
             '제공 후에만 recording 표식을 확인했다. 자료 확보는 새 수정 권한이 아니므로 start.md를 변경하지 않았다.')
    t.summary('중단', '[결과](#result)', '문안 선택·편집 허용을 확보한 뒤 의존 작업을 진행할 수 있다.', '현재 배정의 허용은 읽기 전용이며 편집·전체 결과 검증의 조건은 아직 미충족이다.')
    t.result('원문 미확보·독립 조사·자료 제공 후 재개를 확인했다.', '해당 관찰 범위 충족. 수정·전체 수용을 확인한 것은 아니다.', '문안 선택·편집 허용과 결과 반영이 필요하다.')
    assert read(t.folder / 'start.md') == START
    t.finish('자료 미확보의 생성 허용·독립 활동·재개와 권한 비확대', '중단')

    t = Trial(5, '사용자 역할의 무응답 상태 관리', SCOPE)
    t.plan(STANDARD)
    t.inspect()
    t.record('choose', 'A/B 질문과 권고를 제시한 모의 상태다. 응답 사건은 제공하지 않았다.',
             '미정 선택을 합의·결정 완료로 바꾸지 않았다.', '모의 사용자 역할의 실제 선택 입력 필요.', done=False)
    t.field('남은 결정', 'A/B 선택. 다른 독립 활동은 남아 있지 않다.')
    t.summary('중단', '[논의·선택](#work-choose)', '응답 입력을 기다린다.', '다음 합의 행동이 선택 응답에 막혔다. 무응답·AI 권고는 승인이 아니다.')
    t.result('후보까지 준비했고 문서를 수정하지 않았다.', '기대된 무응답 경계 관찰 충족.', '선택·반영·전체 수용은 남아 있다.')
    assert read(t.folder / 'start.md') == START
    assert not next(j for j in t.jobs if j['id'] == 'choose')['done']
    t.finish('무응답에서 선택·반영·완료를 만들지 않음', '중단')

    t = Trial(6, '추가 비교 요청에 따른 계획과 합의 갱신', SCOPE)
    t.plan(STANDARD)
    t.inspect()
    t.record('choose', '모의 입력: 아직 고르지 않고 처음 읽는 사람·반복 사용자의 관점에서 더 비교해 달라.',
             '추가 비교 요청을 선정·실행 허용으로 처리하지 않았다.', '추가 비교 후 A/B 선택 필요.', done=False)
    t.field('현재 합의', '모의 추가 비교 요청에 따라 두 독자 관점을 비교한다. 안내 방식은 아직 미정이며 배정·권한은 그대로다.')
    t.plan([STANDARD[0], ('readers', '독자 관점 추가 비교', '조사, 검수'), *STANDARD[1:]])
    assert read(t.folder / 'start.md') == START and digest(read(t.folder / 'assignment.md')) == t.assignment_sha
    t.record('readers', '같은 후보를 두 독자 관점으로 추가 비교했다.',
             '처음 읽는 사람은 A의 용도 설명을 얻고 반복 사용자는 B의 짧은 진입을 쓸 수 있다. 두 안 모두 같은 상세 원문으로 이동한다.')
    t.choose_a('추가 비교 뒤 가상 사용자 역할이 A안을 선택')
    t.apply_a()
    t.complete('추가 비교 요청·현재 계획 갱신·모의 선택·반영을 확인했다. 전달사항은 바꾸지 않았다.')
    t.finish('추가 요청을 배정 개정·선정으로 오인하지 않고 계획 갱신', '완료')

    t = Trial(7, '부모 배정 개정과 원본·기존 결과 보존', SCOPE)
    t.plan(STANDARD)
    t.inspect()
    old_inspection = read(t.folder / 'execution.md')
    t.summary('중단', '[배정 참조](#assignment)', '부모가 두 문서 수정 배정을 개정한다.', 'r001은 guide.md 변경을 허용하지 않는다.')
    assert read(t.folder / 'guide.md') == GUIDE
    revised = t.assignment.replace('start.md만 수정한다. guide.md를 보존한다.',
                                    'start.md와 guide.md의 첫 상세 문장을 함께 수정한다. 나머지 원문·범위 밖 내용은 보존한다.')
    revised += '\n개정 근거: 모의 사용자 역할이 두 문서 수정·새 완료 조건·범위를 확정했다. '
    revised += 'guide.md의 첫 문장은 “Task 본문에는 현재 상태·계획·유효한 결정을 정리합니다.”로 바꾸고 두 문서 결과를 대조한다.\n'
    write(t.folder / 'assignment-r002.md', revised)
    parent = read(t.folder / 'parent.md').replace('- 원본: [전달사항](assignment.md)',
               '- 원본: [새 전달사항](assignment-r002.md)\n- 이전 원본: [r001](assignment.md) — 바이트 보존')
    parent = parent.replace('- 전달본: r001 — 시험 안의 초판', '- 전달본: r002 — 두 문서 수정으로 모의 배정 개정')
    write(t.folder / 'parent.md', parent)
    t.field('적용 전달본', '[개정 전달사항](assignment-r002.md)')
    t.field('전달본 식별', 'r002 — 시험 개정본')
    t.field('현재 합의', '모의 부모 변경 합의: r002로 두 문서를 수정한다. 기존 원문 대조는 r001에서 수행한 결과로 보존하며 새 범위만 보완·재확인한다.')
    t.choose_a('r002 범위에서 가상 사용자 역할이 A안을 선택')
    t.field('현재 합의', '모의 부모 변경 합의 r002와 모의 A안 선택을 적용한다. r002는 start.md와 guide.md의 첫 상세 문장을 함께 수정하는 배정이다. 이전 원문 대조는 r001에 근거한 결과다.')
    new_guide = GUIDE.replace('Task 본문은 현재 상태와 계획을 관리합니다.', 'Task 본문에는 현재 상태·계획·유효한 결정을 정리합니다.')
    write(t.folder / 'guide.md', new_guide)
    t.apply_a(expected_guide=new_guide)
    t.record('apply', 'r002와 모의 A안 선택 뒤 두 문서를 새 범위에 맞게 반영했다.',
             'r001 원본은 같고 기존 원문 대조 구역의 내용도 유지된다. 새 범위의 첫 문장·링크·중복·선택을 재확인했다.')
    assert old_inspection.split('<a id="work-inspect">')[1].strip() in read(t.folder / 'execution.md')
    t.complete('r001을 보존하고 r002의 두 문서 결과와 참조를 확인했다.')
    assert '- 전달본: r002' in read(t.folder / 'parent.md')
    t.finish('배정 개정 전 실행 제한·r001 보존·r002 참조와 영향 확인', '완료')

    t = Trial(8, '할 일 재구성과 수행 근거 보존', SCOPE)
    t.plan(STANDARD)
    t.inspect()
    evidence = read(t.folder / 'execution.md')
    t.plan([STANDARD[0], STANDARD[1], ('apply-review', '반영과 전체 확인을 묶어 수행', '실행, 검수')])
    t.field('현재 합의', '배정 안에서 미착수 반영·검수 할 일을 묶었다. 기존 inspect 식별자·태그·근거는 유지한다. 사용자 선택 조건은 그대로다.')
    t.summary('진행 중', '[현재 계획](#execution-plan)', '기존 사용자 역할 선택 조건을 유지하며 다음 논의를 준비한다.')
    t.result('미착수 계획만 재구성했다.', '기존 기록·태그·식별자와 필수 선택 조건을 보존했다.', '사용자 역할 선택과 반영·전체 수용은 아직 남아 있다.')
    assert read(t.folder / 'execution.md') == evidence
    assert t.records == ['inspect'] and 'work-apply-review' not in read(t.folder / 'execution.md')
    t.finish('계획 병합·재배열에도 기존 실제 기록과 선택 의무 유지', '진행 중')

    t = Trial(9, '잘못된 반영 결과의 검출·보완·재확인', SCOPE, tags='실행, 검수')
    t.plan([('apply', '반영 결과 보완·재확인', '실행, 검수'), ('close', '검수·종료', '검수')])
    t.field('현재 합의', '시작 입력: 가상 A안 선택과 반영이 있었으나 실제 확인은 끝나지 않은 모의 상태다.')
    write(t.folder / 'start.md', A.replace('#recording)', '#records)'))
    assert not link_ok(t.folder)
    t.record('apply', '초기 오입력 #records를 실제 파일과 대조해 불일치를 발견했다.',
             '실제 표식은 recording이다. 확인 실패로 완료 체크·전체 수용을 제한했다.', '링크 보완·재확인 필요.', done=False)
    assert not t.jobs[0]['done']
    write(t.folder / 'start.md', A)
    assert link_ok(t.folder) and read(t.folder / 'guide.md') == GUIDE
    t.record('apply', '초기 #records 불일치의 원인은 잘못된 표식 반영이었다. 같은 할 일에서 #recording으로 보완했다.',
             '실패 당시 기준을 보존했다. 실제 링크·A안·중복 제거·원문 보존을 재확인해 충족했다.')
    assert t.records == ['apply']
    t.complete('확인 실패와 원인을 보존하고 같은 구역에서 보완·재확인했다.')
    t.finish('실패를 완료로 덮지 않고 같은 할 일에서 수정·재검증', '완료')

    t = Trial(10, '일부 저장·가상 사용자 변경을 포함한 복구', SCOPE, tags='조사, 실행, 검수')
    t.plan([('apply', '실제 상태 복구와 남은 반영', '조사, 실행, 검수'), ('close', '검수·종료', '검수')])
    partial = START.replace('#record)', '#recording)').replace('# 시작 안내\n', '# 시작 안내\n\n' + NOTE + '\n', 1)
    write(t.folder / 'start.md', partial)
    t.summary('중단', '[복구](#work-apply)', '옛 다음 행동: 링크를 고친다.', '모의 중단 이후 실제 저장·확인 상태를 재대조해야 한다.')
    t.field('현재 합의', '모의 시작 상태: A안 선택, 링크 저장, 별도 사용자 문장 추가가 있다. 저장 뒤 확인은 없었다.')
    t.record('apply', '초기 상태는 일부 저장·추가 문장이 있는 모의 입력이며 사전 확인 근거는 없다.',
             '아직 복구 확인을 수행하지 않았다.', '실제 파일·사용자 변경·미수행 대조.', done=False)
    actual = read(t.folder / 'start.md')
    assert NOTE in actual and '(guide.md#recording)' in actual
    t.summary('진행 중', '[복구](#work-apply)', '저장된 부분은 보존하고 남은 문안만 반영한다.')
    restored = actual.replace('Task 본문은 현재 상태와 계획을 관리합니다.\n자세한 수행 내용은 별도 수행 기록에 남깁니다.',
                              '작업 상태와 상세 기록의 작성 방법을 확인하세요.')
    write(t.folder / 'start.md', restored)
    assert NOTE in read(t.folder / 'start.md') and link_ok(t.folder)
    assert read(t.folder / 'guide.md') == GUIDE
    t.record('apply', '실제 저장된 링크·미수행 문안·추가 문장을 대조했다. 옛 입력으로 덮어쓰지 않고 상세 중복만 A안으로 바꿨다.',
             '추가 문장·기존 제목·상세 원문을 보존했다. 이번 재개 후 사후 확인한 사실이며 과거에 검증한 것으로 기록하지 않았다.')
    t.complete('부분 저장과 가상 사용자 변경을 보존한 채 남은 작업을 복구·확인했다.')
    t.finish('저장·미수행·미확인을 구별하고 추가 문장·기존 상태 보존', '완료')

    t = Trial(11, '문서 이동과 들어오고 나가는 참조 보정',
              'guide.md를 guides/recording.md로 이동하고 start.md·index.md·이동 문서의 링크를 보정한다. 본문·표식·추가 문장은 보존한다.', tags='조사, 실행, 검수')
    t.plan([('move', '문서 이동·참조 보정·확인', '조사, 실행, 검수'), ('close', '검수·종료', '검수')])
    write(t.folder / 'start.md', START.replace('#record)', '#recording)'))
    write(t.folder / 'index.md', '# 문서 목록\n\n[기록 안내](guide.md#recording)\n')
    write(t.folder / 'guide.md', GUIDE + '\n[시작 안내로 돌아가기](start.md)\n')
    source_path = (t.folder / 'guide.md').resolve()
    destination = (t.folder / 'guides/recording.md').resolve()
    source_path.relative_to(t.folder.resolve())
    destination.relative_to(t.folder.resolve())
    destination.parent.mkdir()
    source_path.rename(destination)
    for name in ['start.md', 'index.md']:
        write(t.folder / name, read(t.folder / name).replace('(guide.md#recording)', '(guides/recording.md#recording)'))
    write(destination, read(destination).replace('(start.md)', '(../start.md)'))
    assert not source_path.exists() and destination.is_file()
    assert all(link_ok(t.folder, name) for name in ['start.md', 'index.md', 'guides/recording.md'])
    assert read(destination).startswith(GUIDE)
    t.record('move', '허용된 시험 폴더 안의 절대 원본·목적 경로를 확인한 뒤 한 파일을 이동하고 세 문서의 상대 링크를 보정했다.',
             '기존 위치는 없어지고 새 파일·recording 표식·세 방향의 현재 링크가 유효하다. 본문 설명·표식은 보존했다.')
    t.complete('문서 이동·들어오는 두 링크·이동한 문서의 돌아가기 링크를 실제 최종 위치에서 확인했다.')
    t.finish('실제 파일 이동과 양방향 상대 링크·표식·본문 보존', '완료')

    t = Trial(12, '취소와 부모의 필수 결과 잔여 처리', SCOPE)
    t.plan([STANDARD[0], ('cancel', '취소 요청과 부분 결과 보존', '논의, 결정, 검수')])
    t.inspect()
    t.record('cancel', '모의 입력: 이 Task를 취소하고 대체 작업·최종 안내 방식은 아직 정하지 않는다.',
             '비교 근거와 원문을 보존하고 취소를 목표 달성으로 처리하지 않았다.')
    t.summary('취소', '[결과](#result)', '부모가 필수 결과의 대체·범위 변경을 판단한다.')
    t.result('모의 취소 요청에 따라 부분 결과를 보존하고 취소했다.', '취소 처리를 확인했으며 문제 해소·전체 결과 완료가 아니다.', '링크·중복 문제 해소는 부모의 필수 결과로 남는다. 대체 작업은 미정이다.')
    t.parent('진행 중', '자식은 취소됐다. 링크·중복 문제 해소가 필수 결과로 남아 전체 수용은 불충족이다. 대체 결과·범위 변경 판단이 필요하며 새 Task·번호·선택을 만들지 않았다.')
    assert read(t.folder / 'start.md') == START and read(t.folder / 'guide.md') == GUIDE
    t.finish('취소를 완료·부모 자동 수용으로 바꾸지 않고 근거·잔여 보존', '취소')


def supplement():
    """Resolve review findings, then observe missing/provided data in two child contexts."""
    baseline = {
        'purpose': '시작 안내의 링크·중복 정리',
        'result_scope': 'start.md의 실제 수정과 확인 근거',
        'acceptance': '링크·상세 중복·선택 일치·원문 보존을 실제 파일과 대조',
        'creation_information': '가상 P/T, 분리된 시험 위치, 충돌 없음의 시험 입력',
        'internal_question': 'A/B 안내 방식은 생성 후 가상 사용자 역할이 선택',
    }
    variants = [
        ('담당 결과 부족', 'result_scope', '담당 결과·범위·결정 주체·수용 기준을 확정해 주세요.'),
        ('수용 기준 부족', 'acceptance', '완료 조건과 확인 대상·방법을 보완해 주세요.'),
        ('생성 정보 부족', 'creation_information', '부모 목록·파일·사용 이력으로 식별·위치·충돌 확인을 보완해 주세요.'),
    ]
    parts = ['# TC-02 생성 보류\n\n각 입력은 기준 배정에서 한 묶음만 누락했다. 누락된 답은 다른 원천에도 없다. '
             '아래 입력을 각각 다시 읽어 부족한 묶음을 확인하고 보완 요청을 반환했다.\n']
    for title, key, answer in variants:
        incoming = dict(baseline)
        incoming[key] = None
        missing = [name for name, value in incoming.items() if value is None]
        assert missing == [key]
        assert all(incoming[name] == baseline[name] for name in incoming if name != key)
        parts.append(f'## {title}\n\n```json\n' + json.dumps(incoming, ensure_ascii=False, indent=2) +
                     '\n```\n\n반환: ' + answer + '\n\n판정: 생성 제한. 내부 문안 미정으로 배정 부족을 대신하지 않았다.\n')
    parts.append('<a id="result"></a>\n## 반환과 판정\n\n독립 입력 3개 모두 필요한 보완 요청을 반환했다. '
                 '임의의 결과·수용 기준·번호·경로를 채우지 않았으며 Task·수행 기록은 미생성이다.\n')
    write(ROOT / 'tc-02/case.md', '\n'.join(parts))
    assert not (ROOT / 'tc-02/task.md').exists() and not (ROOT / 'tc-02/execution.md').exists()

    pending = {
        9: '없음 — A안 선택이 초기 모의 입력에 제공됐다. 실제 사용자 선택으로 기록하지 않는다.',
        10: '없음 — A안 선택은 초기 모의 입력이다. 추가 문장 보존과 사후 확인이 필요했던 상태를 복구했다.',
        11: '없음 — 이동 경로·세 문서의 참조 보정은 부모 배정에서 확정됐으며 별도 문안 선택은 없다.',
    }
    for number, value in pending.items():
        path = ROOT / f'tc-{number:02}/task.md'
        body, count = re.subn(r'^- 남은 결정: .*$', '- 남은 결정: ' + value, read(path), count=1, flags=re.M)
        assert count == 1
        write(path, body)
    path = ROOT / 'tc-07/task.md'
    body = read(path).replace('모의 부모 변경 합의 r002와 모의 A안 선택을 적용한다. 이전 원문 대조는 r001에 근거한 결과다.',
                              '모의 부모 변경 합의 r002와 모의 A안 선택을 적용한다. r002는 start.md와 guide.md의 첫 상세 문장을 함께 수정하는 배정이다. 이전 원문 대조는 r001에 근거한 결과다.')
    write(path, body)
    for number, value in {
        4: 'guide.md 확보는 해소했다. 문안 선택·편집 허용은 여전히 필요하며 그 전에는 수정하지 않는다.',
        8: 'A/B 안내 방식은 가상 사용자 역할이 선택해야 한다. 계획 재구성이 이 의무를 없애지 않는다.',
        12: '최종 안내 방식·대체 작업은 미정이다. 취소가 이 선택이나 부모의 필수 결과를 확정하지 않는다.',
    }.items():
        path = ROOT / f'tc-{number:02}/task.md'
        body = re.sub(r'^- 남은 결정: .*$', '- 남은 결정: ' + value, read(path), count=1, flags=re.M)
        write(path, body)

    following = ('후속 점검에 필요한 입력은 점검할 두 문서의 실제 원문·파일 위치다. '
                 '수동 대조의 대상은 링크의 파일·표식이며 파일 변경·검사기 구현·실행은 이번 선정 배정의 허용이 아니다. '
                 '실행이 필요하면 해당 실행의 범위·허용과 입력을 먼저 확인한다.')
    path = ROOT / 'tc-03/task.md'
    body = re.sub(r'^- 현재 합의: (.*)$', lambda m: '- 현재 합의: ' + m[1] + ' ' + following,
                  read(path), count=1, flags=re.M)
    write(path, body)
    path = ROOT / 'tc-03/execution.md'
    body = read(path).replace('선택·이유·후속 입력 조건을 기록했다. 실행 허용으로 확대하지 않았다.',
                             '선택·이유·후속 입력 조건을 기록했다. ' + following)
    write(path, body)

    # Only the actor code and folder path are sent to each fresh interpreter.
    # No SPEC text, GUIDE bytes or expected anchor value is present in this code.
    probe = ROOT / 'source-probe'
    probe.mkdir(exist_ok=False)
    write(probe / 'start.md', START)
    actor = '''from pathlib import Path
import json,re,sys
folder=Path(sys.argv[1]).resolve()
entry=folder/'start.md'
detail=folder/'guide.md'
target=re.search(r'\\[[^\\]]+\\]\\(([^)]+)\\)',entry.read_text(encoding='utf-8')).group(1)
available=detail.is_file()
anchors=re.findall(r'<a id="([^"]+)"',detail.read_text(encoding='utf-8')) if available else None
print(json.dumps({'detail_available':available,'entry_target':target,'detail_anchors':anchors}))
'''

    def observe():
        result = subprocess.run([sys.executable, '-B', '-X', 'utf8', '-c', actor, str(probe)],
                                cwd=probe, capture_output=True, text=True, encoding='utf-8', check=True)
        return json.loads(result.stdout)

    absent = observe()
    assert absent['detail_available'] is False and absent['detail_anchors'] is None
    write(probe / 'guide.md', GUIDE)
    provided = observe()
    assert provided['detail_available'] is True and provided['detail_anchors'] == ['recording']
    path = ROOT / 'tc-04/execution.md'
    body = read(path).replace('제공 후에만 recording 표식을 확인했다.',
                             '제공 후에만 recording 표식을 확인했다. 보완 확인에서는 사례 원문·정답 표식 없이 '
                             '관찰 코드와 입력 폴더 경로만 전달한 새 Python 프로세스를 두 번 실행했다. '
                             '제공 전에는 상세 원문 부재·표식 미확인(null), 제공 후에는 실제 표식 목록을 반환했다. '
                             '이는 입력 가용성의 실행 확인이며 AI의 맹검·기억 차단 검증은 아니다.')
    write(path, body)
    return {'before_provision': absent, 'after_provision': provided}


def report(failure=None):
    rows = '\n'.join(f'| [TC-{n:02}]({path}) | {verdict} | {state} | {note} |'
                     for n, verdict, state, note, path in RESULTS)
    text = '''# Task 생성·문서 관리 일괄 모의 수행

<a id="setup"></a>
## 실행 설정과 경계

- 실행 식별: task-doc-suite-a
- 실제 담당 기록: [Issue #72](../../issue.md#task-generation-test)
- 사례 원천: [12개 사례](../task-document-management-test-cases.md#case-list)
- 실제 사용자 지시: “다 검증하고 검증되면 수행해”. 이후 응답으로 “고정된 시험 입력으로 일괄 모의 수행 (추천)”을 선택했다.
- TC-01의 실제 A안 응답·완료 결과는 보존하고 현재 파일을 재대조한다. 나머지 11개는 각 폴더에서 독립된 입력으로 수행한다.
- P/T는 시험 역할이며 실제 Issue/Task 번호가 아니다. 부모·Task·전달사항·수행 기록과 입력 파일의 대응은 각 폴더에 있다. TC-02는 생성 제한을 확인하므로 Task·수행 기록을 만들지 않는다.
- 현재 대화의 같은 AI가 작성안을 적용하며 이 실행 파일은 기계적 파일 작성·대조를 보조한다. 자율 판단 엔진이나 제품의 새로운 운영 도구가 아니며 맹검·별도 모델·새 문맥 검증도 아니다.
- [실행 정의](exercise.py)의 입력·파일 변경·판정 조건을 재현 근거로 보존한다. 기존 폴더를 덮어쓰지 않으며 같은 폴더에서 재실행하지 않는다. 삭제·외부 등록·커밋은 수행하지 않는다.
- 사례의 통과는 기대된 관찰·제한 동작이 확인됐다는 뜻이다. 미생성·중단·진행 중·취소를 시험 통과에 맞추려고 완료로 바꾸지 않는다.
- 최종 검수에서 TC-02의 실제 입력 세 묶음, 방법 선정의 후속 조건과 현재 남은 결정 표현을 구체화했다. TC-04는 원문·정답을 포함하지 않은 관찰 코드를 새 Python 프로세스에서 제공 전후에 실행해 입력 가용성을 추가 확인했다. 이는 AI의 맹검·기억 차단을 확인한 것이 아니다.

## 고정한 모의 사건

| 사례 | 주입할 시험 입력 |
|---|---|
| TC-03 | 가상 사용자 역할이 수동 대조를 선택. 두 파일에서 추가 환경 없이 확인하려는 이유와 후속 실행 조건 기록 |
| TC-04 | 초기에 guide.md를 두지 않고 독립 활동·중단 관찰 후 원문 제공. 새 편집 허용은 주입하지 않음 |
| TC-05 | 응답 없음. 선택·반영을 하지 않아야 함 |
| TC-06 | 처음·반복 사용자의 관점에서 추가 비교 요청. 보완 뒤 가상 A안 선택 |
| TC-07 | 가상 부모에서 두 문서 수정·새 기준으로 r002 개정. 이후 가상 A안 선택 |
| TC-09 | 가상 A안 선택 뒤 오입력 #records가 있는 수정본 제공 |
| TC-10 | 가상 A안 선택·링크만 저장·별도 문장 추가·확인 미실시 상태 제공 |
| TC-12 | 가상 취소 요청. 대체 작업·최종 안내 방식은 미정 |

모의 사건은 실제 사용자 선택·실제 사용자 파일 변경·제품 권한으로 쓰지 않는다. TC-01에서 실제 응답을 받았던 사실과 구별한다.

<a id="results"></a>
## 현재 판정

| 사례·근거 | 시험 판정 | 시험용 Task 상태 | 실제 관찰 요약 |
|---|---|---|---|
'''
    text += rows + '\n\n'
    text += ('실행 실패: ' + failure + '\n' if failure else
             '모든 사례의 기대 동작을 확인했다. TC-01은 기존 상호작용 결과 재대조이며 나머지 11개를 새로 수행했다. '
             'TC-02의 세 부족 변형을 모두 포함한다. 중단·취소 사례의 과제 목표까지 달성한 것이 아니다.\n')
    write(ROOT / 'run.md', text)


if __name__ == '__main__':
    assert len(BLOCKS) == 2
    assert len(re.findall(r'^## TC-\d{2}\.', SOURCE, re.M)) == 12
    assert not list(ROOT.glob('tc-*')), 'Existing case folders must be preserved'
    report('실행 시작 — 아직 전체 판정 전이다.')
    try:
        run_cases()
        assert len(RESULTS) == 12
        supplement()
        report()
    except Exception as error:
        report(type(error).__name__ + ': ' + str(error))
        raise
    print(json.dumps({'cases': len(RESULTS), 'results': RESULTS, 'mode': USER_MODE}, ensure_ascii=False))
