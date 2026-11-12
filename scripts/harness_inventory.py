"""Bounded, read-only views of project-managed skill and hook sources."""

import datetime
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import subprocess
import time
import tomllib

DOCUMENT = 'harness/스킬과 hook 현황.md'
SCOPES = ['.agents/skills', '.codex/hooks.json', '.codex/config.toml', 'scripts/hooks']
GIT_EVENTS = {'applypatch-msg', 'pre-applypatch', 'post-applypatch', 'pre-commit',
              'pre-merge-commit', 'prepare-commit-msg', 'commit-msg', 'post-commit',
              'pre-rebase', 'post-checkout', 'post-merge', 'pre-push', 'pre-receive',
              'update', 'proc-receive', 'post-receive', 'post-update', 'reference-transaction',
              'push-to-checkout', 'pre-auto-gc', 'post-rewrite', 'sendemail-validate', 'fsmonitor-watchman',
              'post-index-change', 'p4-changelist', 'p4-prepare-changelist',
              'p4-post-changelist', 'p4-pre-submit'}
TEXT_SUFFIXES = {'.md', '.py', '.js', '.mjs', '.ts', '.tsx', '.json', '.yaml', '.yml',
                 '.toml', '.sh', '.txt', '.svg', '.html', '.css', '.xml', '.sql'}
HEX = re.compile(r'[0-9a-f]{64}\Z')


def path_name(name):
    if not isinstance(name, str) or not name or len(name) > 1000:
        raise ValueError('Invalid source path')
    if any(ord(c) < 32 or c in '\\:*?[]' for c in name) or name.startswith('/') or PureWindowsPath(name).drive:
        raise ValueError('Source path must be a literal repository-relative path')
    parts = PurePosixPath(name).parts
    if PurePosixPath(name).as_posix() != name or any(
        p in ('.', '..') or p.endswith((' ', '.')) or
        p.casefold() in ('.git', '.harness-state', 'harness-design', '.tmp', '.aws', '.ssh') or
        (p.casefold().startswith('.env') and p != '.env.example') for p in parts
    ):
        raise ValueError('Preserved, private, temporary or escaping source path is excluded')
    return name


def safe_work_path(root, name):
    name = path_name(name)
    cursor = root
    for part in PurePosixPath(name).parts:
        cursor = cursor / part
        if cursor.is_symlink() or cursor.is_junction():
            raise ValueError('Symlink/junction source requires explicit review: ' + name)
    if not cursor.resolve().is_relative_to(root):
        raise ValueError('Source is outside the repository')
    return cursor


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def source_hash(name, content):
    if PurePosixPath(name).suffix in TEXT_SUFFIXES or PurePosixPath(name).name in GIT_EVENTS:
        content = content.replace(b'\r\n', b'\n')
    return hashlib.sha256(content).hexdigest()


class Candidate:
    def __init__(self, candidate='index', cwd=None, seconds=2.7):
        self.root = Path(cwd or Path.cwd()).resolve()
        self.deadline = time.monotonic() + seconds
        self.root = Path(self.git('rev-parse', '--show-toplevel').decode().strip()).resolve()
        self.kind = candidate
        self.commit = None
        if candidate not in ('work', 'index'):
            self.commit = self.git('rev-parse', '--verify', '--end-of-options', candidate + '^{commit}').decode().strip()
        self.cache = {}

    def git(self, *args, input=None, allowed=(0,)):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise ValueError('Inventory inspection time limit exceeded; candidate is unverified')
        result = subprocess.run(['git', '-C', str(self.root), *args], input=input,
                                capture_output=True, timeout=remaining,
                                env={**os.environ, 'GIT_NO_LAZY_FETCH': '1',
                                     'GIT_TERMINAL_PROMPT': '0', 'GIT_OPTIONAL_LOCKS': '0'})
        if result.returncode not in allowed:
            raise ValueError('Git candidate could not be inspected')
        return result.stdout

    def names(self):
        if self.kind != 'work':
            return self.load(SCOPES)
        # Inspect reparse points before asking Git to consider untracked paths.
        tracked = self.git('ls-files', '-z', '--', *SCOPES).decode('utf-8').split('\0')
        found = set()

        def visit(name):
            path = safe_work_path(self.root, name)
            if not path.exists():
                return
            if path.is_file():
                found.add(name)
            elif path.is_dir():
                for child in path.iterdir():
                    if child.name in ('__pycache__', '.git', 'node_modules', '.venv', '.tmp'):
                        continue
                    visit(name + '/' + child.name)
                    if len(found) > 5000:
                        raise ValueError('Too many managed source files')
        for scope in SCOPES:
            visit(scope)
        ignored = set()
        if found:
            payload = ('\0'.join(sorted(found)) + '\0').encode('utf-8')
            ignored = set(self.git('check-ignore', '-z', '--stdin', input=payload, allowed=(0, 1)).decode('utf-8').split('\0'))
        names = sorted((found - ignored) | {n for n in tracked if n})
        return [n for n in names if self.read(n) is not None]

    def load(self, names):
        names = list(dict.fromkeys(path_name(n) for n in names))
        if not names:
            return []
        if self.kind == 'work':
            return [n for n in names if self.read(n) is not None]
        args = ('ls-files', '--stage', '-z') if self.kind == 'index' else ('ls-tree', '-r', '-z', self.commit)
        output = self.git(*args, '--', *names)
        objects = {}
        for row in output.split(b'\0'):
            if not row:
                continue
            metadata, raw_name = row.split(b'\t', 1)
            fields = metadata.decode('ascii').split()
            name = path_name(raw_name.decode('utf-8'))
            if fields[0] not in ('100644', '100755') or (self.kind == 'index' and fields[2] != '0'):
                raise ValueError('Symlink, submodule or unmerged candidate: ' + name)
            objects[name] = fields[1] if self.kind == 'index' else fields[2]
        pending = {n: oid for n, oid in objects.items() if n not in self.cache}
        if pending:
            payload = ('\n'.join(pending.values()) + '\n').encode('ascii')
            stream = io.BytesIO(self.git('cat-file', '--batch', input=payload))
            for name in pending:
                header = stream.readline().split()
                if len(header) != 3 or header[1] != b'blob' or int(header[2]) > 20_000_000:
                    raise ValueError('Invalid or oversized source object: ' + name)
                data = stream.read(int(header[2]))
                if stream.read(1) != b'\n':
                    raise ValueError('Incomplete source object')
                self.cache[name] = data
        for name in names:
            if name not in objects:
                self.cache.setdefault(name, None)
        return sorted(objects)

    def read(self, name):
        name = path_name(name)
        if name not in self.cache:
            if self.kind != 'work':
                self.load([name])
            else:
                path = safe_work_path(self.root, name)
                if not path.exists():
                    self.cache[name] = None
                elif not path.is_file() or path.stat().st_size > 20_000_000:
                    raise ValueError('Source is not a bounded regular file: ' + name)
                else:
                    self.cache[name] = path.read_bytes()
        return self.cache.get(name)


def inventory(view, optional=False):
    raw = view.read(DOCUMENT)
    if raw is None:
        if optional:
            return {'schema': 1, 'entries': []}, ''
        raise ValueError('Inventory document is absent from this candidate')
    text = raw.decode('utf-8-sig').replace('\r\n', '\n')
    blocks = re.findall(r'<!-- harness-inventory -->\s*```json\s*\n(.*?)\n```', text, re.S)
    if len(blocks) != 1:
        raise ValueError('Inventory needs one harness-inventory JSON block')
    data = json.loads(blocks[0])
    if not isinstance(data, dict) or data.get('schema') != 1 or not isinstance(data.get('entries'), list):
        raise ValueError('Unsupported inventory schema')
    if len(data['entries']) > 500:
        raise ValueError('Too many inventory entries')
    seen = set()
    for item in data['entries']:
        if not isinstance(item, dict) or not isinstance(item.get('id'), str) or item['id'] in seen:
            raise ValueError('Invalid or duplicate inventory identity')
        seen.add(item['id'])
        path_name(item.get('definition'))
        files = item.get('files')
        if not isinstance(files, list) or not files or len(files) > 5000 or len(set(files)) != len(files):
            raise ValueError('Inventory entry needs a unique source file list')
        for name in files:
            path_name(name)
    return data, text


def discover(view, entries):
    names = view.names()
    if len({name.casefold() for name in names}) != len(names):
        raise ValueError('Managed source paths have a case collision')
    registered = {item['id']: item for item in entries}
    found = {}
    for definition in names:
        match = re.fullmatch(r'\.agents/skills/([^/]+)/SKILL\.md', definition)
        if match:
            identity = 'skill:' + match[1]
            folder = definition.rsplit('/', 1)[0] + '/'
            found[identity] = ('skill', definition, sorted(n for n in names if n.startswith(folder)))
        elif definition.startswith('scripts/hooks/') and definition.count('/') == 2:
            event = definition.rsplit('/', 1)[1]
            if event not in GIT_EVENTS:
                raise ValueError('Unrecognized file in Git hook definition directory: ' + definition)
            text = view.read(definition).decode('utf-8-sig')
            markers = re.findall(r'^# inventory-dependencies: (.+)$', text, re.M)
            if len(markers) > 1:
                raise ValueError('Duplicate Git hook dependency declaration')
            dependencies = json.loads(markers[0]) if markers else []
            if not isinstance(dependencies, list):
                raise ValueError('Git hook dependencies must be an explicit file list')
            files = sorted(set([definition, *(path_name(n) for n in dependencies)]))
            found['git:' + event] = ('git', definition, files)
    project_config = '.codex/config.toml'
    config_sources = [project_config] if view.read(project_config) is not None else []
    for definition in ('.codex/hooks.json', project_config):
        raw = view.read(definition)
        if raw is None:
            continue
        data = json.loads(raw.decode('utf-8-sig')) if definition.endswith('.json') else tomllib.loads(raw.decode('utf-8-sig'))
        if not isinstance(data, dict):
            raise ValueError('Project hook configuration must be an object: ' + definition)
        hooks = data.get('hooks', {})
        if not isinstance(hooks, dict):
            raise ValueError('Invalid project hook definition: ' + definition)
        for event, groups in hooks.items():
            if not isinstance(groups, list):
                raise ValueError('Hook event needs matcher groups: ' + definition)
            for i, group in enumerate(groups):
                if not isinstance(group, dict) or not isinstance(group.get('hooks'), list):
                    raise ValueError('Invalid hook matcher group: ' + definition)
                for j, handler in enumerate(group['hooks']):
                    if not isinstance(handler, dict) or not isinstance(handler.get('type'), str):
                        raise ValueError('Invalid hook handler: ' + definition)
                    identity = f'codex:{definition}:{event}:{i}:{j}'
                    files = sorted(set([definition, *config_sources, *registered.get(identity, {}).get('files', [])]))
                    found[identity] = ('codex', definition, files)
    return found


def digest(view, files):
    # Definition batches are cached; only fetch additional dependency blobs.
    view.load([name for name in files if name not in view.cache])
    manifest = {}
    for name in sorted(files):
        raw = view.read(name)
        if raw is None:
            raise ValueError('Declared source is absent: ' + name)
        manifest[name] = source_hash(name, raw)
    return hashlib.sha256(canonical(manifest)).hexdigest()


def render(entries):
    def cell(value):
        return value.replace('|', '\\|').replace('\r', ' ').replace('\n', ' ')
    rows = ['| 종류 | 항목·원천 | 역할·적용 조건 | 확인 상태 |', '|---|---|---|---|']
    labels = {'unverified': '미확인', 'stale': '재확인 필요', 'verified': '확인'}
    for item in sorted(entries, key=lambda entry: entry['id']):
        status = labels[item['verification']['status']]
        rows.append(f"| {item['kind']} | [{cell(item['title'])}](<../{item['definition']}>) | {cell(item['purpose'])}<br>조건: {cell(item['when'])} | {status} |")
    return '\n'.join(rows)


def validate_verification(view, item):
    value = item.get('verification')
    if not isinstance(value, dict) or value.get('status') not in ('unverified', 'stale', 'verified'):
        raise ValueError('Invalid verification status: ' + item['id'])
    if value['status'] == 'unverified':
        if any(value.get(k) is not None for k in ('sourceDigest', 'date', 'environment', 'scope', 'evidence')):
            raise ValueError('Unverified entry cannot claim a verified baseline: ' + item['id'])
        return
    if not isinstance(value.get('sourceDigest'), str) or not HEX.fullmatch(value['sourceDigest']):
        raise ValueError('Verification needs its own source digest: ' + item['id'])
    if value['status'] == 'verified' and value['sourceDigest'] != item['sourceDigest']:
        raise ValueError('Verification is stale; recheck or label it stale: ' + item['id'])
    for key in ('date', 'environment', 'scope', 'evidence'):
        if not isinstance(value.get(key), str) or not value[key].strip() or len(value[key]) > 2000:
            raise ValueError('Verification needs date/environment/scope/evidence: ' + item['id'])
    datetime.date.fromisoformat(value['date'])
    evidence, _, anchor = value['evidence'].partition('#')
    raw = view.read(path_name(evidence))
    if raw is None:
        raise ValueError('Verification evidence is absent from candidate: ' + item['id'])
    if anchor and f'id="{anchor}"' not in raw.decode('utf-8-sig'):
        raise ValueError('Verification evidence anchor is absent: ' + item['id'])


def inspect(view, describe=False, render_only=False):
    data, text = inventory(view, optional=describe)
    actual = discover(view, data['entries'])
    registered = {item['id']: item for item in data['entries']}
    if describe:
        return {'schema': 1, 'entries': [{'id': identity, 'kind': kind, 'definition': definition,
                                        'files': files, 'sourceDigest': digest(view, files)}
                                       for identity, (kind, definition, files) in sorted(actual.items())]}
    if set(actual) != set(registered):
        missing = sorted(set(actual) - set(registered))
        removed = sorted(set(registered) - set(actual))
        raise ValueError('Inventory membership differs; missing=' + ','.join(missing) + '; removed=' + ','.join(removed))
    for identity, item in registered.items():
        kind, definition, files = actual[identity]
        if item.get('kind') != kind or item['definition'] != definition or sorted(item['files']) != files:
            raise ValueError('Inventory source list differs: ' + identity)
        for key in ('title', 'purpose', 'when'):
            if not isinstance(item.get(key), str) or not item[key].strip() or len(item[key]) > 2000:
                raise ValueError('Inventory needs title/purpose/when: ' + identity)
        if item.get('sourceDigest') != digest(view, files):
            raise ValueError('Inventory source digest differs: ' + identity)
        validate_verification(view, item)
    expected = render(data['entries'])
    if render_only:
        return expected
    tables = re.findall(r'<!-- inventory-table -->\s*\n(.*?)\n<!-- /inventory-table -->', text, re.S)
    if len(tables) != 1 or tables[0].strip() != expected:
        raise ValueError('Inventory summary table differs; render it from the same metadata')
    return None

# Issue #55 negative CI fixture: inventory intentionally not updated.
