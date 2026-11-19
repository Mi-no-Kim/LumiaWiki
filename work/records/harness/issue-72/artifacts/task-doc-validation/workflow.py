"""Mechanical document operations with evidence-based, separate acceptance checks."""

from pathlib import Path
import hashlib
import json
import re
import sys

sys.dont_write_bytecode = True
ARTIFACTS = Path(__file__).resolve().parent.parent


class Refused(Exception):
    def __init__(self, issues):
        self.issues = issues
        super().__init__('; '.join(issues))


def text(path):
    return Path(path).read_text(encoding='utf-8')


def field(document, key):
    match = re.search(r'^- ' + re.escape(key) + r': (.*)$', document, re.M)
    return match[1].strip() if match else None


def replace_field(original, key, value, *, section=None):
    prefix = ''
    if section is None and key in ['내용', '확인', '잔여'] and '<a id="result"></a>' in original:
        section = 'result'
    if section:
        marker = '<a id="' + section + '"></a>'
        if marker not in original:
            raise Refused(['missing section: ' + section])
        offset = original.index(marker)
        prefix, original = original[:offset], original[offset:]
    updated, count = re.subn(r'^- ' + re.escape(key) + r': .*$',
                             lambda _: '- ' + key + ': ' + value,
                             original, count=1, flags=re.M)
    if count != 1:
        raise Refused(['missing field: ' + key])
    return prefix + updated


def set_field(path, key, value, *, section=None):
    updated = replace_field(text(path), key, value, section=section)
    Path(path).write_text(updated, encoding='utf-8', newline='\n')


def block(document):
    match = re.search(r'```json\n(.*?)\n```', document, re.S)
    if not match:
        raise Refused(['missing condition definitions'])
    return json.loads(match[1])


def rules(document, prefix):
    return re.findall(r'<!-- ' + prefix + r'-rule:[\s\S]*?-->', document)


def inline_json(value):
    encoded = json.dumps(value, ensure_ascii=False)
    width = max([len(run) for run in re.findall(r'`+', encoded)] or [0]) + 1
    ticks = '`' * width
    return ticks + encoded + ticks


def parse_json_field(value):
    value = value or ''
    marker = re.match(r'^`+', value)
    if marker and value.endswith(marker[0]):
        value = value[len(marker[0]):-len(marker[0])]
    return json.loads(value)


def json_objects(value, depth=0):
    if depth > 8:
        return
    decoder = json.JSONDecoder()
    for match in re.finditer(r'\{', value):
        try:
            result, _ = decoder.raw_decode(value[match.start():])
            if isinstance(result, dict):
                yield result
                for child in result.values():
                    if isinstance(child, str) and '{' in child:
                        yield from json_objects(child, depth + 1)
        except ValueError:
            continue


class Workspace:
    def __init__(self, folder):
        self.folder = Path(folder).resolve()
        self.folder.relative_to(ARTIFACTS)
        self.input = json.loads(text(self.folder / 'input.json'))

    def path(self, name):
        result = (self.folder / name).resolve()
        result.relative_to(self.folder)
        return result

    def write(self, name, value):
        target = self.path(name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(value, encoding='utf-8', newline='\n')

    def snapshot(self):
        return {p.relative_to(self.folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(self.folder.rglob('*')) if p.is_file()}

    def active(self, document='parent.md'):
        value = field(text(self.path(document)), '적용 전달본') or ''
        match = re.search(r'\]\(([^)#]+)\)', value)
        if not match:
            raise Refused([document + ': missing assignment reference'])
        return self.path(match[1])

    def policy(self):
        return block(text(self.active()))

    def _known_events(self):
        events = self.input.get('initial_events', []) + self.input.get('events', [])
        vault = self.folder.parent.parent / 'sealed' / 'events.json'
        if vault.is_file():
            events = self.input.get('initial_events', []) + json.loads(text(vault)).get(self.folder.name, [])
        return events

    def revision_issues(self):
        try:
            parent = text(self.path('parent.md'))
            task = text(self.path('task.md'))
            if self.active() != self.active('task.md'):
                return ['parent/task assignment reference mismatch']
            parent_revision, task_revision = field(parent, '전달본 식별'), field(task, '전달본 식별')
            if not parent_revision or not task_revision:
                return ['missing parent/task revision identifier']
            if not re.fullmatch(r'r[0-9]{3,}', parent_revision) or not re.fullmatch(r'r[0-9]{3,}', task_revision):
                return ['invalid parent/task revision identifier']
            if parent_revision != task_revision:
                return ['parent/task revision mismatch']
            return []
        except (OSError, ValueError, Refused) as error:
            return ['assignment unavailable: ' + str(error)]

    def conditions(self, conditions):
        observations, issues = [], []
        for item in conditions:
            kind, name = item['kind'], item['id']
            ok, detail = False, ''
            try:
                path = self.path(item.get('path', 'start.md'))
                value = text(path) if path.is_file() else None
                if kind == 'contains':
                    ok = value is not None and item['value'] in value
                elif kind == 'absent_text':
                    ok = value is not None and item['value'] not in value
                elif kind == 'equals':
                    ok = value == item['value']
                elif kind == 'exists':
                    ok = path.is_file()
                elif kind == 'missing':
                    ok = not path.exists()
                elif kind == 'links':
                    failures = []
                    if value is None:
                        failures.append('source absent')
                    else:
                        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', value):
                            filename, _, anchor = target.partition('#')
                            dest = (path.parent / filename).resolve()
                            dest.relative_to(self.folder)
                            if not dest.is_file() or (anchor and f'<a id="{anchor}"></a>' not in text(dest)):
                                failures.append(target)
                    ok, detail = not failures, ', '.join(failures)
                elif kind == 'choice':
                    # A seed choice is input, not a claim in a generated summary.
                    events = self.input.get('initial_events', [])
                    observed = text(self.path('execution.md')) if self.path('execution.md').is_file() else ''
                    ok = any(event.get('kind') == 'choice' and event.get('value') == item['value'] for event in events)
                    delivered = list(json_objects(observed))
                    known = self._known_events()
                    ok = ok or any(event.get('kind') == 'choice' and event.get('value') == item['value']
                                   and event in known for event in delivered)
                elif kind == 'task_complete':
                    ok = self.path('task.md').is_file() and field(text(self.path('task.md')), '상태') == '완료'
                    if ok:
                        task_result = self.check_task()
                        ok = not task_result['issues']
                        detail = '; '.join(task_result['issues'])
                else:
                    detail = 'unsupported condition: ' + kind
            except (OSError, ValueError) as error:
                detail = str(error)
            observations.append({'id': name, 'satisfied': ok, 'observation': detail})
            if not ok:
                issues.append('condition failed: ' + name + (': ' + detail if detail else ''))
        return {'issues': issues, 'observations': observations}

    def creation_inputs(self):
        values = {name: self.input.get(name) for name in ['goal', 'result', 'creation', 'acceptance']}
        def known(value):
            return bool(value) and (not isinstance(value, str) or (bool(value.strip()) and not value.strip().startswith(('미정', '미확인', '없음'))))
        for name in ['goal', 'result', 'acceptance']:
            if not known(values[name]):
                values[name] = None
        try:
            source = text(self.active())
            for name, heading in [('goal', '목적'), ('result', '기대 결과')]:
                match = re.search(r'^## ' + heading + r'\s*\n(.*?)(?=^## |\Z)', source, re.S | re.M)
                candidate = match[1].strip() if match else None
                if not known(values[name]) and known(candidate):
                    values[name] = candidate
            if not values['acceptance']:
                values['acceptance'] = block(source).get('criteria', [])
                if not values['acceptance']:
                    parent_conditions = block(text(self.path('parent.md'))).get('criteria', [])
                    values['acceptance'] = [item for item in parent_conditions if item.get('kind') != 'task_complete']
            creation = values['creation']
            if not isinstance(creation, dict) or not all(creation.get(key) for key in ['parent', 'task', 'path_checked', 'collision_checked']):
                proof = field(text(self.path('parent.md')), '생성 식별 확인') or ''
                values['creation'] = {'proof': proof} if proof.startswith('확인 —') else None
        except (OSError, ValueError, Refused):
            pass
        for name in ['goal', 'result']:
            if not known(values[name]):
                values[name] = None
        return values

    def creation_issues(self):
        return ['missing creation input: ' + name for name, value in self.creation_inputs().items() if not value]

    def create_task(self):
        issues = self.creation_issues()
        if issues:
            raise Refused(issues)
        if self.path('task.md').exists():
            raise Refused(['task already exists'])
        source = text(ARTIFACTS / 'task-body-template-draft.md')
        document = re.search(r'```markdown\n(.*?)\n```', source, re.S)[1] + '\n'
        actual = {
            '<부모 Issue 번호>-<로컬 순번>': 'T — 가상 시험',
            '<작업 제목>': self.creation_inputs()['goal'],
            '<조사·논의·결정·실행·검수·커밋 중 필요한 여러 개를 쉼표로 구분>': self.input.get('tags', '조사, 논의, 결정, 실행, 검수'),
            '(task-common-procedure-draft.md)': '(../../../task-common-procedure-draft.md)',
            '<저장소·번호·URL>': '미발급 — 가상 역할이며 정식 번호 아님',
            '<본문의 실제 작업·근거 구역 링크>': '[계획과 합의](#sequence)',
            '<현재 허용된 대상과 행동>': '이 배정의 전체 계획과 준비를 확인한다.',
            '<제한되는 행동·미충족 조건·해소 조건·근거>': '전달사항의 선택·준비·실행 조건을 따른다.',
            '<실제 부모 기록 링크>': '[부모 P](parent.md#children)',
            '<확정 전달사항 파일 또는 합의한 개정본 링크>': '[전달사항](' + self.active().name + ')',
            '<r001 또는 실제 개정 식별>': field(text(self.path('parent.md')), '전달본 식별'),
            '<원본 경로·전달본 식별·확정 근거가 있는 Issue의 배정 결정 링크>': '[부모 배정](parent.md#assignment)',
            '<실제 대상·입력과 필요한 선행 결과·등록·브랜치 등의 확보 상태와 제한>': '분리된 시험 폴더와 제공된 입력만 사용한다. 실제 발급·제품 수정은 없다.',
            '<결정·이유·근거·위임 범위·사용자 확인 조건. 공통 조건·커밋 묶음은 필요한 때 한 번만 정의>': '입력의 모의 계획 합의와 배정을 적용한다. 모의 응답은 실제 사용자 승인으로 쓰지 않는다.',
            '<질문·판단 기준·결정 주체·필요한 시점>': self.input.get('pending', '안내 방식은 모의 사용자 역할이 선택한다.'),
            '<전달본 완료 조건별 확인 계획>': '현재 전달사항의 조건별로 실제 파일·선택 근거·보존을 대조한다.',
            '<artifacts/task-실제순번-execution.md. 생성 후 실제 링크로 전환>': 'execution.md — 시험용 예정 경로',
            '<작업식별자>': 'pending',
            '<대상과 행동이 드러나는 할 일 이름>': '미정 — 생성 후 전체 계획에서 구체화',
            '<실제 결과가 발생한 뒤 전체 결과·반영 범위와 현재 결론>': '미발생.',
            '<완료 조건별 판정·근거·한계. 상세는 실제 수행 기록의 해당 구역 연결>': '미실시.',
            '<미반영·미해결·재개 조건과 다음 행동. 없음을 확인했으면 없음>': '배정 결과·확인·종료가 남아 있다.',
        }
        for old, new in actual.items():
            document = document.replace(old, new)
        document = re.sub(r'<(?!/?a\b|!)([^<>]+)>', '미정', document)
        if rules(document, 'task') != rules(source, 'task'):
            raise Refused(['template rules changed'])
        parent = replace_field(text(self.path('parent.md')), '보유 Task', '[Task T](task.md#summary)')
        self.write('task.md', document)
        self.write('parent.md', parent)
        return {'state': '예정', 'execution_exists': self.path('execution.md').exists()}

    def set_plan(self, jobs):
        document = text(self.path('task.md'))
        old = {m[1]: '[x] 수행·확인 완료' in m[2] for m in re.finditer(r'<a id="work-([a-z-]+)"></a>([\s\S]*?)(?=<a id=|\Z)', document)}
        marker = document.index('<!-- task-rule:execution')
        begin = document.index('-->', marker) + 3
        end = document.index('<a id="result">', begin)
        execution = text(self.path('execution.md')) if self.path('execution.md').is_file() else ''
        sections = []
        for key, title, tags in jobs:
            ref = (f'[수행 기록](execution.md#work-{key})' if f'id="work-{key}"' in execution else f'execution.md#work-{key} — 미착수 예정 경로')
            sections.append(f'<a id="work-{key}"></a>\n#### {title}\n\n- 태그: {tags}\n'
                            f'- [{"x" if old.get(key) else " "}] 수행·확인 완료\n'
                            f'- 할 일: {title}. 현재 배정·선행 조건 안에서 수행한다.\n'
                            '- 확인: 이 행동의 실제 관찰·근거와 조건을 대조한다.\n'
                            f'- 수행 기록: {ref}.\n')
        self.write('task.md', document[:begin] + '\n\n' + '\n'.join(sections) + '\n' + document[end:])

    def summary(self, state, location, next_action, blocked='없음'):
        document = text(self.path('task.md'))
        for name, value in [('상태', state), ('현재 진행 위치', location), ('다음 행동', next_action), ('막힌 조건', blocked)]:
            document = replace_field(document, name, value)
        self.write('task.md', document)

    def _record_documents(self, key, action, observation, remaining='없음', *, done=False, verdict=None, document=None):
        document = text(self.path('task.md')) if document is None else document
        match = re.search(r'<a id="work-' + re.escape(key) + r'"></a>\n#### (.+)', document)
        if not match:
            raise Refused(['unplanned work: ' + key])
        if done and (not observation.strip() or verdict != '충족' or not remaining.startswith('없음')):
            raise Refused(['completed work needs a satisfied verdict, observation and no remaining work'])
        if verdict not in [None, '충족', '불충족', '미확인', '미실시']:
            raise Refused(['invalid work verdict'])
        observation = inline_json({'판정': verdict or '미확인', '관찰': observation})
        if not self.path('execution.md').exists():
            source = text(ARTIFACTS / 'task-execution-template-draft.md')
            header = re.search(r'```markdown\n(.*?)\n```', source, re.S)[1].split('<a id="work-', 1)[0]
            header = header.replace('<부모 Issue 번호>-<실제 순번>', 'T — 가상 시험')
            header = header.replace('<실제 Task 본문 링크>', '[Task T](task.md#sequence)')
            header = header.replace('(task-common-procedure-draft.md#recording-proposal)', '(../../../task-common-procedure-draft.md#recording-proposal)')
            execution = header
            document = replace_field(document, '수행 기록', '[실제 수행 기록](execution.md)')
        else:
            execution = text(self.path('execution.md'))
        pattern = r'<a id="work-' + re.escape(key) + r'"></a>[\s\S]*?(?=\n<a id="work-|\Z)'
        previous = re.search(pattern, execution)
        if previous:
            for event in json_objects(previous[0]):
                encoded = json.dumps(event, ensure_ascii=False)
                if event in self._known_events() and encoded not in action:
                    action += ' 보존한 모의 사건: ' + inline_json(event)
        section = (f'<a id="work-{key}"></a>\n## {match[1]}\n\n- 할 일: [본문](task.md#work-{key})\n\n'
                   f'- 조치·판단: {action}\n- 확인: {observation}\n- 잔여: {remaining}\n')
        if previous:
            execution = re.sub(pattern, lambda _: section, execution, count=1)
        else:
            execution += '\n' + section
        pattern = r'(<a id="work-' + re.escape(key) + r'"></a>[\s\S]*?- )\[[ x]\]( 수행·확인 완료)'
        document = re.sub(pattern, lambda m: m[1] + ('[x]' if done else '[ ]') + m[2], document, count=1)
        document = document.replace(f'execution.md#work-{key} — 미착수 예정 경로', f'[수행 기록](execution.md#work-{key})')
        return {'execution.md': execution, 'task.md': document}

    def record(self, key, action, observation, remaining='없음', *, done=False, verdict=None):
        updates = self._record_documents(key, action, observation, remaining, done=done, verdict=verdict)
        for name, value in updates.items():
            self.write(name, value)

    def check_task(self):
        issues = self.revision_issues()
        document = text(self.path('task.md'))
        pending = field(document, '남은 결정') or ''
        if not pending.startswith('없음'):
            issues.append('unresolved required decision')
        if '- [ ] 수행·확인 완료' in document:
            issues.append('unfinished planned work')
        result = self.conditions(self.policy().get('criteria', []))
        issues.extend(result['issues'])
        if not self.policy().get('criteria'):
            issues.append('no acceptance criteria')
        execution = text(self.path('execution.md')) if self.path('execution.md').is_file() else ''
        if not execution:
            issues.append('missing execution evidence')
        for key in re.findall(r'<a id="work-([a-z-]+)">', document):
            section = re.search(r'<a id="work-' + re.escape(key) + r'"></a>[\s\S]*?(?=\n<a id="work-|\Z)', execution)
            if not section:
                issues.append('missing work evidence: ' + key)
                continue
            try:
                observation = parse_json_field(field(section[0], '확인') or '{}')
            except ValueError:
                observation = {}
            if observation.get('판정') != '충족' or not observation.get('관찰'):
                issues.append('unverified work evidence: ' + key)
            if not (field(section[0], '잔여') or '').startswith('없음'):
                issues.append('unresolved work remainder: ' + key)
        if field(document, '막힌 조건') != '없음':
            issues.append('unresolved blocking condition')
        return {'issues': issues, 'observations': result['observations']}

    def complete_task(self):
        result = self.check_task()
        if result['issues']:
            raise Refused(result['issues'])
        document = text(self.path('task.md'))
        changes = [('내용', '현재 배정의 결과·필수 확인·기록과 종료 조건을 충족했다.'),
                   ('확인', json.dumps(result, ensure_ascii=False)), ('잔여', 'Task 자기 범위의 잔여 없음. 부모 수용은 별도다.'),
                   ('상태', '완료'), ('현재 진행 위치', '[결과](#result)'), ('다음 행동', '부모가 실제 결과와 전체 수용 조건을 별도로 검사한다.')]
        for key, value in changes:
            document = replace_field(document, key, value)
        self.write('task.md', document)
        return result

    def check_parent(self):
        definition = block(text(self.path('parent.md')))
        result = self.conditions(definition.get('criteria', []))
        if not definition.get('criteria'):
            result['issues'].append('no parent acceptance criteria')
        result['issues'].extend(self.revision_issues())
        return result

    def accept_parent(self):
        result = self.check_parent()
        if result['issues']:
            raise Refused(result['issues'])
        parent = replace_field(text(self.path('parent.md')), '수용 판정', json.dumps(result, ensure_ascii=False))
        parent = replace_field(parent, '상태', '완료')
        self.write('parent.md', parent)
        return result

    def apply_files(self, desired):
        issues = self.revision_issues()
        policy = self.policy()
        permitted = policy.get('allowed_writes', [])
        for name in desired:
            if name not in permitted:
                issues.append('write not allowed: ' + name)
            self.path(name)
        for name in policy.get('required_sources', []):
            if not self.path(name).is_file():
                issues.append('missing required source: ' + name)
        decision = [item for item in policy.get('criteria', []) if item['kind'] == 'choice']
        issues.extend(self.conditions(decision)['issues'])
        for name in desired:
            expected = self.input.get('expected_before', {}).get(name)
            if expected is not None and text(self.path(name)) != expected:
                issues.append('concurrent edit conflict: ' + name)
        if issues:
            raise Refused(issues)
        for name, value in desired.items():
            self.write(name, value)
        return {'written': list(desired)}

    def use_event(self, event_id, work):
        events = self.input.get('events', [])
        vault = self.folder.parent.parent / 'sealed' / 'events.json'
        if vault.is_file():
            events = json.loads(text(vault)).get(self.folder.name, events)
        event = next((event for event in events if event['id'] == event_id), None)
        if event is None:
            raise Refused(['event not provided: ' + event_id])
        updates = {}
        task = text(self.path('task.md'))
        if event['kind'] == 'supply':
            for name, value in event['files'].items():
                target = self.path(name)
                if target.exists() and text(target) != value:
                    raise Refused(['source provision would overwrite a changed file: ' + name])
                updates[name] = value
        if event['kind'] == 'revise':
            target = self.path(event['assignment_name'])
            if target.exists() and text(target) != event['assignment_text']:
                raise Refused(['revision would overwrite an existing source'])
            updates[event['assignment_name']] = event['assignment_text']
            parent = replace_field(text(self.path('parent.md')), '적용 전달본', '[개정 전달사항](' + event['assignment_name'] + ')')
            parent = replace_field(parent, '전달본 식별', event['revision'])
            if 'parent_policy' in event:
                parent, count = re.subn(r'```json\n.*?\n```', lambda _: '```json\n' + json.dumps(event['parent_policy'], ensure_ascii=False, indent=2) + '\n```', parent, count=1, flags=re.S)
                if count != 1:
                    raise Refused(['parent conditions missing during revision'])
            updates['parent.md'] = parent
        if event['kind'] == 'choice':
            task = replace_field(task, '현재 합의', '모의 선택 사건: ' + json.dumps(event, ensure_ascii=False))
            task = replace_field(task, '남은 결정', '없음 — 지정한 모의 선택을 확인했다.')
        updates.update(self._record_documents(work, '모의 사건을 입력으로 확인했다. 실제 사용자 승인이 아니다.', json.dumps(event, ensure_ascii=False), document=task))
        for name in updates:
            self.path(name)
        for name, value in updates.items():
            self.write(name, value)
        return event

    def adopt_revision(self):
        current = self.active()
        if not current.is_file():
            raise Refused(['parent revision unavailable'])
        task = replace_field(text(self.path('task.md')), '적용 전달본', '[확정 전달사항](' + current.name + ')')
        task = replace_field(task, '전달본 식별', field(text(self.path('parent.md')), '전달본 식별'))
        task = replace_field(task, '현재 합의', '부모의 확정 개정본을 확인했다. 이전 전달본·기존 수행 근거는 보존하며 현재 계획·영향받는 확인을 보완한다.')
        self.write('task.md', task)

    def move_file(self, source, destination):
        issues = self.revision_issues()
        if [source, destination] not in self.policy().get('allowed_moves', []):
            issues.append('move not allowed')
        origin, target = self.path(source), self.path(destination)
        if not origin.is_file() or target.exists():
            issues.append('move source absent or destination already exists')
        expected = self.input.get('expected_before', {}).get(source)
        if expected is not None and origin.is_file() and text(origin) != expected:
            issues.append('concurrent edit conflict: ' + source)
        if issues:
            raise Refused(issues)
        target.parent.mkdir(parents=True, exist_ok=True)
        origin.rename(target)
        return {'moved': [source, destination]}

