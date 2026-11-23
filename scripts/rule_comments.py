"""Current record profiles, frozen legacy paths and read-only comment checks."""

import json
from collections import Counter
from pathlib import Path
import re

from harness_inventory import path_name, safe_work_path
from issue_rule_comments import FENCE, RAW_TEXT, TAG, body_text, live_markup, tag_end

POLICY = 'harness/rule-comments.json'
STATES = ('예정', '진행 중', '중단', '완료', '취소')
LEGACY_STATES = ('예정', '진행 중', '검증 중', '대기', '보류', '완료', '취소')
PROFILES = {
    'issue': ('issue-rule', ('start', 'state', 'position', 'completion'), 'harness/templates/issue.md'),
    'task': ('task-rule', ('tags', 'recording', 'start', 'summary', 'assignment', 'plan', 'execution', 'completion'), 'harness/templates/task.md'),
    'execution': ('execution-rule', ('recording',), 'harness/templates/task-execution.md'),
}
PLAN_PROFILES = {
    'task-with-plan': ('separate-task-rule', ('recording',), 'harness/templates/task-with-plan.md'),
    'task-plan': ('task-plan-rule', ('recording',), 'harness/templates/task-plan.md'),
}
ALL_PROFILES = {**PROFILES, **PLAN_PROFILES}
STAGE_ID = r'stage-[a-z0-9]+(?:-[a-z0-9]+)*'
PARENT = r'work/records/(?:phase-[0-9]+/issue-[0-9]+|issues/issue-[0-9]+|harness/issue-[0-9]+)'
RECORDS = {
    'issue': re.compile(PARENT + r'/issue\.md\Z'),
    'task': re.compile(PARENT + r'/task-[0-9]+\.md\Z'),
    'execution': re.compile(PARENT + r'/artifacts/task-[0-9]+-execution\.md\Z'),
}


def record_profile(name):
    return next((kind for kind, pattern in RECORDS.items() if pattern.fullmatch(name)), None)


def effective_profile(name, policy):
    profile = record_profile(name)
    if profile == 'task' and policy.get('schema') == 2 and (
        name not in policy['compatibleTasks'] or name in policy.get('taskPlanMigrations', {})
    ):
        return 'task-with-plan'
    return profile


def record_names(view):
    """Discover only real record locations, including untracked working files."""
    if view.kind != 'work':
        args = ('ls-files', '-z') if view.kind == 'index' else ('ls-tree', '-r', '--name-only', '-z', view.commit)
        return sorted({path_name(n) for n in view.git(*args, '--', 'work/records').decode('utf-8').split('\0') if n and record_profile(n)})
    found = []
    base = safe_work_path(view.root, 'work/records')
    if not base.exists():
        return found
    for group in base.iterdir():
        if not (group.name in ('issues', 'harness') or re.fullmatch(r'phase-[0-9]+', group.name)):
            continue
        group_name = group.relative_to(view.root).as_posix()
        group = safe_work_path(view.root, group_name)
        if not group.is_dir():
            continue
        for parent in group.iterdir():
            if not re.fullmatch(r'issue-[0-9]+', parent.name):
                continue
            parent = safe_work_path(view.root, parent.relative_to(view.root).as_posix())
            if not parent.is_dir():
                continue
            for child in parent.iterdir():
                name = child.relative_to(view.root).as_posix()
                if record_profile(name):
                    safe_work_path(view.root, name)
                    found.append(name)
                elif child.name == 'artifacts':
                    child = safe_work_path(view.root, name)
                    if child.is_dir():
                        for artifact in child.iterdir():
                            name = artifact.relative_to(view.root).as_posix()
                            if record_profile(name):
                                safe_work_path(view.root, name)
                                found.append(name)
    if len(found) > 10000:
        raise ValueError('Too many record files')
    return sorted(found)


def comments(raw, profile, mode='body'):
    prefix, rules, _ = ALL_PROFILES[profile]
    opening = re.compile(r'<!--\s*' + re.escape(prefix) + r':([a-z-]+)\b')
    values, errors = {}, []
    for kind, block in live_markup(raw, 'body' if mode == 'reference' else mode):
        if kind != 'comment':
            continue
        for match in opening.finditer(block):
            rule = match[1]
            if rule not in rules:
                continue
            label = prefix + ':' + rule
            if match.start() or not block.endswith('-->') or '<!--' in block[match.end():]:
                errors.append(label + ': malformed or nested boundary')
            elif rule in values:
                errors.append(label + ': duplicate comment')
            else:
                values[rule] = block
    return values, errors


def baseline(raw, profile):
    values, errors = comments(raw, profile, 'template')
    if errors or set(values) != set(ALL_PROFILES[profile][1]):
        raise ValueError('Incomplete ' + profile + ' baseline: ' + '; '.join(errors))
    return values


def read_policy(view):
    raw = view.read(POLICY)
    if raw is None:
        raise ValueError('Current record policy is absent from candidate')
    data = json.loads(raw.decode('utf-8-sig'))
    if not isinstance(data, dict) or data.get('schema') not in (1, 2):
        raise ValueError('Unsupported current record policy')
    profiles = ALL_PROFILES if data['schema'] == 2 else PROFILES
    if set(data.get('profiles', {})) != set(profiles):
        raise ValueError('Incomplete record profiles')
    legacy_policy = data.get('legacyIssuePolicy')
    if legacy_policy is not None:
        if legacy_policy != 'harness/issue-rule-comments.json' or view.read(legacy_policy) is None:
            raise ValueError('Declared legacy Issue protection policy is missing')
    legacy = data.get('legacyRecords')
    if not isinstance(legacy, list) or len(legacy) > 10000:
        raise ValueError('Frozen legacy record paths are required')
    legacy = [path_name(n) for n in legacy]
    if len(set(n.casefold() for n in legacy)) != len(legacy) or any(not record_profile(n) for n in legacy):
        raise ValueError('Legacy entries must be unique exact record paths')
    for profile, (_, rules, source) in profiles.items():
        item = data['profiles'][profile]
        if item.get('source') != source or set(item.get('comments', {})) != set(rules):
            raise ValueError('Invalid baseline source/rules: ' + profile)
        for rule, value in item['comments'].items():
            if not isinstance(value, str):
                raise ValueError('Invalid baseline comment')
            actual, errors = comments(value.encode('utf-8'), profile)
            if errors or actual != {rule: value}:
                raise ValueError('Invalid baseline comment boundary')
    targets = data.get('targets')
    if not isinstance(targets, list) or len(targets) > 1000:
        raise ValueError('Explicit template/example targets are required')
    seen = set()
    for target in targets:
        name = path_name(target['path'])
        if name.casefold() in seen or target.get('profile') not in profiles or target.get('mode') not in ('template', 'body', 'reference'):
            raise ValueError('Invalid or duplicate explicit target')
        if not name.startswith(('harness/templates/', 'harness/examples/')) or not name.endswith('.md'):
            raise ValueError('Only current templates/examples may be explicit targets')
        if target['mode'] == 'reference' and not name.startswith('harness/examples/'):
            raise ValueError('Reference-only state placeholders are confined to examples')
        seen.add(name.casefold())
    for profile, (_, _, source) in profiles.items():
        if {'path': source, 'profile': profile, 'mode': 'template'} not in targets:
            raise ValueError('Mandatory source template target is missing: ' + profile)
    if data['schema'] == 2:
        compatible = data.get('compatibleTasks')
        if not isinstance(compatible, list) or len(compatible) > 10000:
            raise ValueError('Exact pre-adoption Task paths are required')
        names = [path_name(name) for name in compatible]
        if len({name.casefold() for name in names}) != len(names) or any(
            record_profile(name) != 'task' or name in legacy for name in names
        ):
            raise ValueError('Pre-adoption Task paths must be unique exact non-legacy Task paths')
        migrations = data.get('taskPlanMigrations', {})
        if not isinstance(migrations, dict) or not set(migrations) <= set(names):
            raise ValueError('Migration must identify an exact pre-adoption Task')
        for name, approval in migrations.items():
            if not isinstance(approval, str) or approval.partition('#')[0] not in (
                name, name.rsplit('/', 1)[0] + '/issue.md'
            ):
                raise ValueError('Migration approval must belong to the Task or its Issue')
            check_approval(view, approval)
    revisions = data.get('revisions', [])
    if not isinstance(revisions, list) or len(revisions) > 4000:
        raise ValueError('Invalid scoped revisions')
    keys = set()
    for change in revisions:
        name, profile, rule = path_name(change['path']), change['profile'], change['rule']
        key = (name, profile, rule)
        matching = next((t for t in targets if t['path'] == name), None)
        if profile not in PROFILES or rule not in PROFILES[profile][1] or key in keys:
            raise ValueError('Invalid scoped revision key')
        if (record_profile(name) != profile and (matching is None or matching['profile'] != profile)) or name in legacy:
            raise ValueError('Revision must identify its exact current record/profile')
        if change.get('before') != data['profiles'][profile]['comments'][rule]:
            raise ValueError('Revision before-text does not match baseline')
        replacement = change.get('replacement')
        if replacement is not None:
            if not isinstance(replacement, str):
                raise ValueError('Invalid revision replacement')
            values, errors = comments(replacement.encode('utf-8'), profile)
            if errors or values != {rule: replacement}:
                raise ValueError('Revision must replace only one comment')
        check_approval(view, change.get('approval', ''))
        keys.add(key)
    return data


def check_approval(view, approval):
    source, sep, anchor = approval.partition('#')
    source = path_name(source)
    if not source.startswith('work/records/') or not sep or not anchor:
        raise ValueError('Revision requires an actual approval record section')
    evidence = view.read(source)
    if evidence is None or ('anchor', anchor) not in set(live_markup(evidence)):
        raise ValueError('Approval record reference is unverified')


def visible_text(raw):
    """Keep text context; exclude comments, code, HTML attributes and raw text."""
    text = body_text(raw, 'body')
    output, cursor, fence = [], 0, None

    def skip(end):
        nonlocal cursor
        output.append('\n' * text[cursor:end].count('\n'))
        cursor = end

    while cursor < len(text):
        if cursor == 0 or text[cursor - 1] == '\n':
            end = text.find('\n', cursor)
            end = len(text) if end < 0 else end + 1
            match = FENCE.match(text[cursor:end])
            if match:
                token, rest = match.groups()
                if fence is None:
                    fence = token
                elif token[0] == fence[0] and len(token) >= len(fence) and not rest.strip():
                    fence = None
                skip(end)
                continue
            if fence is not None or text[cursor:end].startswith(('    ', '\t')):
                skip(end)
                continue
        if text.startswith('<!--', cursor):
            end = text.find('-->', cursor + 4)
            skip(len(text) if end < 0 else end + 3)
            continue
        if text[cursor] == '`':
            token = re.match(r'`+', text[cursor:])[0]
            close = re.search(r'(?<!`)' + re.escape(token) + r'(?!`)', text[cursor + len(token):])
            skip(cursor + len(token) + (close.end() if close else 0))
            continue
        if text.startswith('<![CDATA[', cursor):
            end = text.find(']]>', cursor + 9)
            skip(len(text) if end < 0 else end + 3)
            continue
        tag = TAG.match(text, cursor)
        if tag:
            end = tag_end(text, tag.end())
            name = tag[1].lower()
            if not text.startswith('</', cursor) and name in RAW_TEXT | {'plaintext'}:
                closing = re.search(r'</' + name + r'\s*>', text[end:], re.I) if name != 'plaintext' else None
                end = len(text) if closing is None else end + closing.end()
            skip(end)
            continue
        output.append(text[cursor])
        cursor += 1
    return ''.join(output)


def record_state(raw):
    text = visible_text(raw)
    summaries = re.findall(r'^## 현재 요약\s*\n(.*?)(?=^#{1,2} |\Z)', text, re.M | re.S)
    if len(summaries) != 1:
        return None
    states = re.findall(r'^- 상태:[ \t]*([^\r\n]*?)[ \t]*$', summaries[0], re.M)
    return states[0] if len(states) == 1 and states[0] in STATES else None


def check_state(raw):
    return [] if record_state(raw) else ['current state must be one of: ' + ', '.join(STATES)]


def check_position(raw, plan_link, stage_ids=()):
    summary = re.search(r'^## 현재 요약\s*\n(.*?)(?=^#{1,2} |\Z)', visible_text(raw), re.M | re.S)
    position = re.findall(r'^- 현재 진행 위치: (.+)$', summary[1], re.M) if summary else []
    match = re.fullmatch(r'\[[^\]]+\]\(([^\s)#]*)#([^\s)#]+)\)', position[0]) if len(position) == 1 else None
    if match:
        path, anchor = match.groups()
        if path == plan_link and anchor in stage_ids:
            return []
        if not path and ('anchor', anchor) in list(live_markup(raw)):
            return []
    return ['current position must link a Task section or its plan stage']


def task_paths(name):
    folder, task = name.rsplit('/', 1)
    stem = task.removesuffix('.md')
    return folder, task, f'artifacts/{stem}-plan.md', f'artifacts/{stem}-execution.md'


def task_assignment(raw, task):
    basename = re.escape(task.removesuffix('.md')) + r'-assignment(?:-r\d+)?\.md'
    return re.findall(r'^- 적용 전달본: \[[^\]]+\]\(artifacts/(' + basename + r')\)$', visible_text(raw), re.M)


def work_anchors(raw):
    return {value for kind, value in live_markup(raw or b'') if kind == 'anchor' and value.startswith('work-')}


def completed_evidence(raw, heading_level, label, link):
    completed = []
    for section in re.split(r'^' + '#' * heading_level + r' ', visible_text(raw or b''), flags=re.M)[1:]:
        if re.search(r'^- \[x\] ' + label + r'$', section, re.M):
            targets = re.findall(r'^- 수행 기록: \[[^\]]+\]\((<[^>\n]+>|[^\s)]+)\)\.?[ \t]*$', section, re.M)
            prefix = link + '#'
            evidence = [target.removeprefix(prefix) for value in targets
                        if (target := value.strip('<>')).startswith(prefix) and len(target) > len(prefix)]
            completed.append(evidence[0] if len(evidence) == 1 else None)
    return completed


def check_migration(view, previous, name, raw):
    before = previous.read(name)
    if before is None:
        return []
    folder, _, plan_link, execution_link = task_paths(name)
    errors = []
    if record_state(before) != record_state(raw):
        errors.append('migration must preserve the current state')
    if not work_anchors(before) <= work_anchors(raw):
        errors.append('migration must preserve existing Task work anchors')
    old_execution = previous.read(f'{folder}/{execution_link}')
    new_execution = view.read(f'{folder}/{execution_link}')
    if not work_anchors(old_execution) <= work_anchors(new_execution):
        errors.append('migration must preserve existing execution evidence anchors')
    previous_checks = completed_evidence(before, 4, '수행·확인 완료', execution_link)
    actual_checks = completed_evidence(view.read(f'{folder}/{plan_link}'), 2, '단계 완료', Path(execution_link).name)
    prior_links = Counter(item for item in previous_checks if item)
    if len(actual_checks) < len(previous_checks) or prior_links - Counter(actual_checks):
        errors.append('migration must preserve completed work and its evidence')
    return errors


def check_plan(view, name, raw, policy):
    folder, task, plan_link, execution_link = task_paths(name)
    plan = view.read(f'{folder}/{plan_link}')
    execution = view.read(f'{folder}/{execution_link}')
    visible = visible_text(raw)
    state = record_state(raw)
    errors = []
    assigned = task_assignment(raw, task)
    assignment_fields = re.findall(r'^- 적용 전달본:', visible, re.M)
    if len(assignment_fields) != 1 or len(assigned) != 1 or view.read(f'{folder}/artifacts/{assigned[0]}') is None:
        errors.append('Task must link one existing assignment')
    summary = re.search(r'^## 현재 요약\s*\n(.*?)(?=^#{1,2} |\Z)', visible, re.M | re.S)
    next_actions = re.findall(r'^- 다음 행동:[ \t]*(.*)$', summary[1], re.M) if summary else []
    if len(next_actions) != 1 or not next_actions[0].strip():
        errors.append('Task summary requires one next action')
    if re.search(r'^[ \t]*[-*+] \[[ xX]\] (?:단계 완료|수행·확인 완료)(?:\s|$)', visible, re.M):
        errors.append('stage completion checks belong only in the plan')
    links = re.findall(r'^- 상세 계획: (.+)$', visible, re.M)
    if links == ['미작성']:
        if plan is not None or execution is not None or state == '완료':
            return errors + ['the Task must link its plan before execution or completion']
        return errors + check_position(raw, plan_link)
    if len(links) != 1 or not re.fullmatch(r'\[[^\]]+\]\(' + re.escape(plan_link) + r'\)', links[0]):
        return errors + ['one canonical Task plan link is required']
    if plan is None:
        return errors + ['linked Task plan is missing']

    actual, comment_errors = comments(plan, 'task-plan')
    errors.extend(comment_errors)
    if actual != policy['profiles']['task-plan']['comments']:
        errors.append('plan recording comment is missing or changed')
    plan_text = visible_text(plan)
    backlink = re.findall(r'^- Task: (.+)$', plan_text, re.M)
    if len(backlink) != 1 or not re.fullmatch(r'\[[^\]]+\]\(\.\./' + re.escape(task) + r'#summary\)', backlink[0]) or (
        list(live_markup(raw)).count(('anchor', 'summary')) != 1
    ):
        errors.append('plan must link the owning Task summary')
    plan_assignment = re.findall(r'^- 적용 전달본: \[[^\]]+\]\(([^\s/)]+)\)$', plan_text, re.M)
    if len(assigned) != 1 or assigned != plan_assignment:
        errors.append('Task and plan must link the same existing assignment')
    agreement = re.findall(r'^- 계획 합의: (제안|합의)(?: — .+)?$', plan_text, re.M)
    if len(agreement) != 1 or ((execution is not None or state == '완료') and agreement != ['합의']):
        errors.append('execution requires an agreed plan')

    heading = re.compile(r'^## (\d+)\. (' + STAGE_ID + r') — \S.*$', re.M)
    headings = list(heading.finditer(plan_text))
    ids = [match[2] for match in headings]
    plan_source = body_text(plan, 'body')
    anchors = []
    for kind, value, (_, end) in live_markup(plan, with_spans=True):
        if kind == 'anchor' and re.fullmatch(STAGE_ID, value):
            following = heading.match(plan_source[end:].lstrip('\n'))
            anchors.append(value if following and following[2] == value else None)
    if not ids or len(ids) != len(set(ids)) or anchors != ids or [m[1] for m in headings] != [
        str(i) for i in range(1, len(headings) + 1)
    ]:
        errors.append('plan requires unique stage anchors and a sequential stage order')

    errors.extend(check_position(raw, plan_link, ids))
    evidence_source = body_text(execution or b'', 'body')
    evidence = [(value, start, end) for kind, value, (start, end) in live_markup(execution or b'', with_spans=True)
                if kind == 'anchor' and value.startswith('work-')]
    evidence_backlinks = {}
    for index, (anchor, _, start) in enumerate(evidence):
        end = evidence[index + 1][1] if index + 1 < len(evidence) else len(evidence_source)
        section = visible_text(evidence_source[start:end].encode('utf-8'))
        backlinks = re.findall(r'^- 할 일: \[[^\]]+\]\(([^\s)]+)\)$', section, re.M)
        evidence_backlinks.setdefault(anchor, []).extend(backlinks or [None])
    for index, match in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(plan_text)
        section = plan_text[match.end():end]
        if any(len(re.findall(r'^- ' + field + r': \S.*$', section, re.M)) != 1 for field in (
            '태그', '선행 입력', '완료 기준', '확인', '확인·결정 지점', '수행 기록'
        )):
            errors.append(match[2] + ': required plan fields are missing or duplicated')
        work = re.search(r'^### 세부 작업\s*\n(.*)', section, re.M | re.S)
        order = re.findall(r'^([1-9]\d*)\. \S', work[1], re.M) if work else []
        if not order or order != [str(i) for i in range(1, len(order) + 1)]:
            errors.append(match[2] + ': ordered subtasks are required')
        checks = re.findall(r'^- \[([ x])\] 단계 완료$', section, re.M)
        if len(checks) != 1 or (state == '완료' and checks != ['x']):
            errors.append(match[2] + ': stage completion is missing or inconsistent')
        if checks == ['x']:
            link = re.search(r'^- 수행 기록: \[[^\]]+\]\(' + re.escape(Path(execution_link).name) + r'#([^\s)]+)\)$', section, re.M)
            expected_backlink = Path(plan_link).name + '#' + match[2]
            if agreement != ['합의'] or not link or evidence_backlinks.get(link[1]) != [expected_backlink]:
                errors.append(match[2] + ': a completed stage requires confirmed execution evidence')
    return errors


def inspect(view, previous=None):
    data = read_policy(view)
    errors = []
    targets = {t['path']: t for t in data['targets']}
    legacy = set(data['legacyRecords'])
    compatible = set(data.get('compatibleTasks', ()))
    migrations = data.get('taskPlanMigrations', {})
    current_names = set(record_names(view))
    previous_names = set()
    old = {}
    if previous is not None and previous.read(POLICY) is not None:
        old = read_policy(previous)
        if old.get('legacyIssuePolicy') != data.get('legacyIssuePolicy'):
            errors.append(POLICY + ': declared legacy Issue protection changed')
        if old['legacyRecords'] != data['legacyRecords']:
            errors.append(POLICY + ': frozen legacy list changed; it is not refreshed for new records')
        if any(data['profiles'].get(key) != value for key, value in old['profiles'].items()):
            errors.append(POLICY + ': captured profile baseline changed; use scoped explicit revisions')
        for target in old['targets']:
            if targets.get(target['path']) != target:
                errors.append(target['path'] + ': explicit target removed or reclassified')
        previous_names = set(record_names(previous))
        if old['schema'] == 2 and (
            data['schema'] != 2 or old['compatibleTasks'] != data.get('compatibleTasks')
            or any(migrations.get(key) != value for key, value in old.get('taskPlanMigrations', {}).items())
        ):
            errors.append(POLICY + ': Task format adoption and migration records are protected')
        if old['schema'] == 1 and data['schema'] == 2:
            prior_tasks = {name for name in previous_names - legacy if record_profile(name) == 'task'}
            if not prior_tasks <= compatible or not compatible <= current_names | previous_names:
                errors.append(POLICY + ': adoption must preserve exact existing Task paths')
    for name in (current_names | previous_names) - legacy:
        targets[name] = {'path': name, 'profile': effective_profile(name, data), 'mode': 'body'}
    view.load(targets)
    inputs = []
    for name, target in targets.items():
        if target['profile'] == 'task-with-plan' and target['mode'] == 'body':
            folder, task, plan, execution = task_paths(name)
            inputs.extend((f'{folder}/{plan}', f'{folder}/{execution}'))
            raw = view.read(name)
            if raw:
                inputs.extend(f'{folder}/artifacts/{assignment}' for assignment in task_assignment(raw, task))
    view.load(inputs)
    for name, target in targets.items():
        profile, mode = target['profile'], target['mode']
        raw = view.read(name)
        if raw is None:
            errors.append(name + ': protected file is missing')
            continue
        expected = dict(data['profiles'][profile]['comments'])
        for change in data.get('revisions', []):
            if change['path'] == name and change['profile'] == profile:
                expected[change['rule']] = change['replacement']
        actual, failures = comments(raw, profile, mode)
        errors.extend(name + ': ' + failure for failure in failures)
        for rule, value in expected.items():
            if (value is None and rule in actual) or (value is not None and actual.get(rule) != value):
                errors.append(name + ': ' + ALL_PROFILES[profile][0] + ':' + rule + ': missing or changed identifier/content/boundary')
        if mode == 'body' and profile in ('issue', 'task', 'task-with-plan'):
            errors.extend(name + ': ' + failure for failure in check_state(raw))
        if mode == 'body' and profile == 'task-with-plan':
            errors.extend(name + ': ' + failure for failure in check_plan(view, name, raw, data))
            if previous is not None and name in migrations and name not in old.get('taskPlanMigrations', {}):
                errors.extend(name + ': ' + failure for failure in check_migration(view, previous, name, raw))
    return errors
