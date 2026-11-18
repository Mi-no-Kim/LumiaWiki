"""Read-only preservation checks for explicitly enrolled Issue rule comments."""

import hashlib
import json
import re

from harness_inventory import path_name


POLICY = 'harness/issue-rule-comments.json'
RULES = ('start', 'state', 'position', 'completion')
FENCE = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')
OPEN = re.compile(r'<!--\s*issue-rule:([a-z-]+)\b')
ANCHOR = re.compile(r'<a\s+id=([\'"])([^\s\'"<>]+)\1\s*>\s*</a\s*>', re.I)
TAG = re.compile(r'</?([a-z][a-z0-9-]*)\b', re.I)
RAW_TEXT = {'script', 'style', 'textarea', 'title', 'xmp', 'iframe', 'noembed', 'noframes'}


def tag_end(text, start):
    quote = None
    for cursor in range(start, len(text)):
        char = text[cursor]
        if quote:
            if char == quote:
                quote = None
        elif char in ('\'', '"'):
            quote = char
        elif char == '>':
            return cursor + 1
    return len(text)


def body_text(raw, mode):
    text = raw.decode('utf-8-sig').replace('\r\n', '\n')
    if mode == 'template':
        found = re.search(r'^```markdown\s*\n(.*?)^```\s*$', text, re.M | re.S)
        if not found:
            raise ValueError('Task/Issue body template needs one initial markdown block')
        text = found[1]
    return text


def live_markup(raw, mode='body', with_spans=False):
    text = body_text(raw, mode)
    cursor, fence = 0, None
    while cursor < len(text):
        if cursor == 0 or text[cursor - 1] == '\n':
            endline = text.find('\n', cursor)
            endline = len(text) if endline < 0 else endline + 1
            match = FENCE.match(text[cursor:endline])
            if match:
                token, rest = match.groups()
                if fence is None:
                    fence = token
                elif token[0] == fence[0] and len(token) >= len(fence) and not rest.strip():
                    fence = None
                cursor = endline
                continue
            if fence is not None:
                cursor = endline
                continue
            if text[cursor:endline].startswith(('    ', '\t')):
                cursor = endline
                continue
        if text[cursor] == '\\' and cursor + 1 < len(text) and text[cursor + 1] in r'!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~':
            cursor += 2
            continue
        if text[cursor] == '`':
            token = re.match(r'`+', text[cursor:])[0]
            close = re.search(r'(?<!`)' + re.escape(token) + r'(?!`)', text[cursor + len(token):])
            cursor += len(token) + (close.end() if close else 0)
            continue
        if not text.startswith('<!--', cursor):
            if text.startswith('<![CDATA[', cursor):
                close = text.find(']]>', cursor + 9)
                cursor = len(text) if close < 0 else close + 3
                continue
            tag = TAG.match(text, cursor)
            if tag:
                end = tag_end(text, tag.end())
                anchor = ANCHOR.match(text, cursor)
                if anchor:
                    yield ('anchor', anchor[2], (cursor, anchor.end())) if with_spans else ('anchor', anchor[2])
                    cursor = anchor.end()
                    continue
                name = tag[1].lower()
                if not text.startswith('</', cursor) and name in RAW_TEXT | {'plaintext'}:
                    closing = re.search(r'</' + name + r'\s*>', text[end:], re.I) if name != 'plaintext' else None
                    cursor = len(text) if closing is None else end + closing.end()
                else:
                    cursor = end
                continue
            if text.startswith(('<!', '<?'), cursor):
                cursor = tag_end(text, cursor + 2)
                continue
            cursor += 1
            continue
        end = text.find('-->', cursor + 4)
        block_end = len(text) if end < 0 else end + 3
        block = text[cursor:block_end]
        yield ('comment', block, (cursor, block_end)) if with_spans else ('comment', block)
        cursor = block_end


def comments(raw, mode='body'):
    result, errors = {}, []
    for kind, block in live_markup(raw, mode):
        if kind != 'comment':
            continue
        # A real HTML comment is parsed as one unit, preserving code quoted
        # inside it. Code examples outside comments never become live rules.
        for match in OPEN.finditer(block):
            rule = match[1]
            if rule not in RULES:
                continue
            if match.start() != 0 or not block.endswith('-->') or '<!--' in block[match.end():]:
                errors.append(f'issue-rule:{rule}: malformed or nested comment boundary')
            else:
                if rule in result:
                    errors.append(f'issue-rule:{rule}: duplicate comment')
                result[rule] = block
    return result, errors


def baseline(raw, mode='template'):
    values, errors = comments(raw, mode)
    if errors or set(values) != set(RULES):
        raise ValueError('Baseline needs exactly the four protected comments: ' + '; '.join(errors))
    return values


def fingerprint(values):
    data = json.dumps(values, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def read_policy(view):
    raw = view.read(POLICY)
    if raw is None:
        raise ValueError('Issue comment policy is absent from this candidate')
    policy = json.loads(raw.decode('utf-8-sig'))
    if not isinstance(policy, dict) or policy.get('schema') != 1:
        raise ValueError('Unsupported Issue comment policy')
    values = policy.get('baseline', {}).get('comments')
    if not isinstance(values, dict) or set(values) != set(RULES):
        raise ValueError('Baseline must contain only the four protected rules')
    for rule, value in values.items():
        if not isinstance(value, str):
            raise ValueError('Invalid baseline comment')
        parsed, errors = comments(value.encode('utf-8'))
        if errors or parsed != {rule: value}:
            raise ValueError('Invalid baseline boundary: ' + rule)
    targets = policy.get('targets')
    if not isinstance(targets, list) or not targets or len(targets) > 1000:
        raise ValueError('Explicit Issue comment targets are required')
    seen = set()
    for target in targets:
        name = path_name(target['path'])
        if name in seen or target.get('mode') not in ('body', 'template') or not name.endswith('.md'):
            raise ValueError('Duplicate or invalid Issue target')
        if not name.startswith('work/records/'):
            raise ValueError('Only explicitly enrolled work records/drafts may be checked')
        seen.add(name)
    revisions = policy.get('revisions', [])
    if not isinstance(revisions, list) or len(revisions) > 4000:
        raise ValueError('Invalid scoped revisions')
    revision_keys = set()
    for change in revisions:
        key = (path_name(change['path']), change['rule'])
        if key[0] not in seen or key[1] not in RULES or key in revision_keys:
            raise ValueError('Revision must identify one enrolled file and protected rule')
        revision_keys.add(key)
        if change.get('before') != values[key[1]]:
            raise ValueError('Revision does not match its recorded baseline')
        replacement = change.get('replacement')
        if replacement is not None:
            if not isinstance(replacement, str):
                raise ValueError('Invalid revision replacement')
            parsed, errors = comments(replacement.encode('utf-8'))
            if errors or parsed != {key[1]: replacement}:
                raise ValueError('Revision may replace only its one protected comment')
        approval = change.get('approval')
        if not isinstance(approval, str):
            raise ValueError('Revision needs a user-approval record reference')
        source, separator, anchor = approval.partition('#')
        source = path_name(source)
        if not source.startswith('work/records/') or not separator or not anchor:
            raise ValueError('Revision approval must point to a work record section')
        evidence = view.read(source)
        if evidence is None or ('anchor', anchor) not in set(live_markup(evidence)):
            raise ValueError('Revision approval reference is unverified')
    return policy


def inspect(view, previous=None):
    policy = read_policy(view)
    targets = {t['path']: t for t in policy['targets']}
    errors = []
    if previous is not None and previous.read(POLICY) is not None:
        old = read_policy(previous)
        if old['baseline']['comments'] != policy['baseline']['comments']:
            errors.append(POLICY + ': captured baseline changed; keep it and record scoped user revisions instead')
        for target in old['targets']:
            if target['path'] not in targets:
                errors.append(target['path'] + ': target removed from policy; scope change requires separate review')
    for name, target in targets.items():
        expected = dict(policy['baseline']['comments'])
        for change in policy.get('revisions', []):
            if change['path'] == name:
                expected[change['rule']] = change['replacement']
        raw = view.read(name)
        if raw is None:
            errors.append(name + ': enrolled file missing; file deletion is not a comment revision')
            continue
        actual, failures = comments(raw, target['mode'])
        errors.extend(name + ': ' + failure for failure in failures)
        for rule in RULES:
            if expected[rule] is None:
                if rule in actual:
                    errors.append(f'{name}: issue-rule:{rule}: explicitly removed rule is still present')
            elif actual.get(rule) != expected[rule]:
                reason = 'missing' if rule not in actual else 'changed identifier/content/boundary'
                errors.append(f'{name}: issue-rule:{rule}: {reason}; restore or record an explicit scoped revision')
    return errors
