"""Current record profiles, frozen legacy paths and read-only comment checks."""

import json
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
PARENT = r'work/records/(?:phase-[0-9]+/issue-[0-9]+|issues/issue-[0-9]+|harness/issue-[0-9]+)'
RECORDS = {
    'issue': re.compile(PARENT + r'/issue\.md\Z'),
    'task': re.compile(PARENT + r'/task-[0-9]+\.md\Z'),
    'execution': re.compile(PARENT + r'/artifacts/task-[0-9]+-execution\.md\Z'),
}


def record_profile(name):
    return next((kind for kind, pattern in RECORDS.items() if pattern.fullmatch(name)), None)


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
    prefix, rules, _ = PROFILES[profile]
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
    if errors or set(values) != set(PROFILES[profile][1]):
        raise ValueError('Incomplete ' + profile + ' baseline: ' + '; '.join(errors))
    return values


def read_policy(view):
    raw = view.read(POLICY)
    if raw is None:
        raise ValueError('Current record policy is absent from candidate')
    data = json.loads(raw.decode('utf-8-sig'))
    if not isinstance(data, dict) or data.get('schema') != 1 or set(data.get('profiles', {})) != set(PROFILES):
        raise ValueError('Unsupported current record policy')
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
    for profile, (_, rules, source) in PROFILES.items():
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
        if name.casefold() in seen or target.get('profile') not in PROFILES or target.get('mode') not in ('template', 'body', 'reference'):
            raise ValueError('Invalid or duplicate explicit target')
        if not name.startswith(('harness/templates/', 'harness/examples/')) or not name.endswith('.md'):
            raise ValueError('Only current templates/examples may be explicit targets')
        if target['mode'] == 'reference' and not name.startswith('harness/examples/'):
            raise ValueError('Reference-only state placeholders are confined to examples')
        seen.add(name.casefold())
    for profile, (_, _, source) in PROFILES.items():
        if {'path': source, 'profile': profile, 'mode': 'template'} not in targets:
            raise ValueError('Mandatory source template target is missing: ' + profile)
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
        approval = change.get('approval', '')
        source, sep, anchor = approval.partition('#')
        source = path_name(source)
        if not source.startswith('work/records/') or not sep or not anchor:
            raise ValueError('Revision requires an actual approval record section')
        evidence = view.read(source)
        if evidence is None or ('anchor', anchor) not in set(live_markup(evidence)):
            raise ValueError('Approval record reference is unverified')
        keys.add(key)
    return data


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


def check_state(raw):
    text = visible_text(raw)
    summaries = re.findall(r'^## 현재 요약\s*\n(.*?)(?=^#{1,2} |\Z)', text, re.M | re.S)
    if len(summaries) != 1:
        return ['one current summary section is required']
    states = re.findall(r'^- 상태:[ \t]*([^\r\n]*?)[ \t]*$', summaries[0], re.M)
    return [] if len(states) == 1 and states[0] in STATES else ['current state must be one of: ' + ', '.join(STATES)]


def inspect(view, previous=None):
    data = read_policy(view)
    errors = []
    targets = {t['path']: t for t in data['targets']}
    legacy = set(data['legacyRecords'])
    current_names = set(record_names(view))
    previous_names = set()
    if previous is not None and previous.read(POLICY) is not None:
        old = read_policy(previous)
        if old.get('legacyIssuePolicy') != data.get('legacyIssuePolicy'):
            errors.append(POLICY + ': declared legacy Issue protection changed')
        if old['legacyRecords'] != data['legacyRecords']:
            errors.append(POLICY + ': frozen legacy list changed; it is not refreshed for new records')
        if old['profiles'] != data['profiles']:
            errors.append(POLICY + ': captured profile baseline changed; use scoped explicit revisions')
        for target in old['targets']:
            if targets.get(target['path']) != target:
                errors.append(target['path'] + ': explicit target removed or reclassified')
        previous_names = set(record_names(previous))
    for name in (current_names | previous_names) - legacy:
        targets[name] = {'path': name, 'profile': record_profile(name), 'mode': 'body'}
    view.load(targets)
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
                errors.append(name + ': ' + PROFILES[profile][0] + ':' + rule + ': missing or changed identifier/content/boundary')
        if mode == 'body' and profile in ('issue', 'task'):
            errors.extend(name + ': ' + failure for failure in check_state(raw))
    return errors
