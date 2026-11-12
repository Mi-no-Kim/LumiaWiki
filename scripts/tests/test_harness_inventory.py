"""Observable candidate and Git hook checks in disposable repositories."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[2]
DOCUMENT = 'harness/스킬 현황.md'
HOOK_DOCUMENT = 'harness/hook 현황.md'
DOCUMENTS = (DOCUMENT, HOOK_DOCUMENT)
SKILL = '.agents/skills/fixture/SKILL.md'
HELPER = '.agents/skills/fixture/scripts/helper.py'
TOOLS = ['scripts/check-harness-inventory.py', 'scripts/harness_inventory.py',
         'scripts/install-harness-hooks.py', 'scripts/install-hooks.py',
         'scripts/tdd-check.py', 'scripts/tdd_core.py']


def digest(root, files):
    hashes = {}
    for name in sorted(files):
        data = (root / name).read_bytes().replace(b'\r\n', b'\n')
        hashes[name] = hashlib.sha256(data).hexdigest()
    return hashlib.sha256(json.dumps(hashes, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def table(entries):
    rows = ['| 항목·원천 | 적용 조건 | 동작 | 확인 상태 |',
            '|---|---|---|---|']
    for item in sorted(entries, key=lambda entry: entry['id']):
        state = {'unverified': '미확인', 'stale': '재확인 필요', 'verified': '확인'}[item['verification']['status']]
        rows.append(f"| [{item['title']}](<../{item['definition']}>) | {item['when']} | {item['purpose']} | {state} |")
    return '\n'.join(rows)


class RepositoryCase(unittest.TestCase):
    def setUp(self):
        parent = PROJECT / '.tmp/issue-55/fixtures'
        parent.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='inventory-', dir=parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-q')
        self.git('config', 'user.name', 'Inventory fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.write('.gitignore', '.tmp/\n__pycache__/\n')
        for name in TOOLS:
            self.write(name, (PROJECT / name).read_text(encoding='utf-8'))
        self.write(SKILL, '---\nname: fixture\ndescription: Fixture only\n---\n# Fixture\n')
        self.write(HELPER, 'VALUE = 1\n')
        self.entries = [self.entry('skill:fixture', 'skill', SKILL, [SKILL, HELPER])]
        self.refresh()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8', newline='')

    def git(self, *args, check=True, cwd=None, input=None):
        return subprocess.run(['git', *args], cwd=cwd or self.root, input=input,
                              capture_output=True, text=True, encoding='utf-8', check=check)

    def run_tool(self, script='check-harness-inventory.py', *args, cwd=None):
        return subprocess.run([sys.executable, '-B', str(self.root / 'scripts' / script), *args],
                              cwd=cwd or self.root, capture_output=True, text=True,
                              encoding='utf-8', env={**os.environ, 'PYTHONUTF8': '1'})

    def check(self, candidate='work'):
        return self.run_tool('check-harness-inventory.py', '--candidate', candidate)

    def entry(self, identity, kind, definition, files):
        return {'id': identity, 'kind': kind, 'title': identity.split(':')[-1],
                'purpose': 'Fixture behavior', 'when': 'fixture 요청',
                'definition': definition, 'files': sorted(files),
                'sourceDigest': digest(self.root, files),
                'verification': {'status': 'unverified', 'sourceDigest': None,
                                 'environment': None, 'scope': None, 'evidence': None}}

    def refresh(self, update_hashes=True):
        if update_hashes:
            for item in self.entries:
                item['sourceDigest'] = digest(self.root, item['files'])
        for document in DOCUMENTS:
            entries = [item for item in self.entries if (item['kind'] == 'skill') == (document == DOCUMENT)]
            self.write_inventory(document, entries)

    def write_inventory(self, document, entries):
        self.write(document, '# Inventory fixture\n\n<!-- inventory-table -->\n' +
                   table(entries) + '\n<!-- /inventory-table -->\n\n' +
                   '<!-- harness-inventory -->\n```json\n' +
                   json.dumps({'schema': 1, 'entries': entries}, ensure_ascii=False, indent=2) +
                   '\n```\n')

    def add_hook(self):
        name = 'scripts/hooks/pre-commit'
        self.write(name, (PROJECT / name).read_text(encoding='utf-8'))
        self.entries.append(self.entry('git:pre-commit', 'git', name, [name, *TOOLS]))
        self.refresh()

    def stage(self):
        self.git('add', '--', '.')

    def assert_allowed(self, candidate='work'):
        result = self.check(candidate)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual('', result.stdout)

    def assert_denied(self, candidate='work'):
        result = self.check(candidate)
        self.assertNotEqual(0, result.returncode, 'An inconsistent candidate must be denied')
        self.assertNotIn('Traceback', result.stderr)


class CandidateTests(RepositoryCase):
    def test_both_catalogs_are_required_even_when_no_hook_exists(self):
        self.assert_allowed()
        for document in DOCUMENTS:
            with self.subTest(document=document):
                (self.root / document).unlink()
                result = self.check()
                self.assertNotEqual(0, result.returncode)
                self.assertIn('Inventory document is absent', result.stderr)
                self.refresh()

    def test_hook_entry_cannot_be_registered_in_skill_catalog(self):
        self.add_hook()
        self.write_inventory(DOCUMENT, self.entries)
        self.write_inventory(HOOK_DOCUMENT, [])
        result = self.check()
        self.assertNotEqual(0, result.returncode)
        self.assertIn('wrong catalog', result.stderr)

    def test_staging_other_catalog_cannot_cover_a_stale_skill(self):
        self.add_hook()
        self.stage()
        self.write(HELPER, 'VALUE = 9\n')
        self.git('add', '--', HELPER)
        self.refresh()
        self.git('add', '--', HOOK_DOCUMENT)
        result = self.check('index')
        self.assertNotEqual(0, result.returncode)
        self.assertIn('source digest differs: skill:fixture', result.stderr)
        self.git('add', '--', DOCUMENT)
        self.assert_allowed('index')

    def test_fifty_skills_stay_usable_and_last_source_change_is_identified(self):
        for number in range(49):
            name = f'.agents/skills/scale-{number:02d}/SKILL.md'
            self.write(name, f'# Scale fixture {number}\n')
            self.entries.append(self.entry(f'skill:scale-{number:02d}', 'skill', name, [name]))
        self.refresh()
        self.stage()
        self.assert_allowed('index')
        changed = '.agents/skills/scale-48/SKILL.md'
        self.write(changed, '# Changed last source\n')
        self.git('add', '--', changed)
        denied = self.check('index')
        self.assertNotEqual(0, denied.returncode)
        self.assertIn('Inventory source digest differs: skill:scale-48', denied.stderr)

    def test_consistent_work_and_index_are_read_only(self):
        self.stage()
        index = self.root / '.git/index'
        before = index.read_bytes(), (self.root / DOCUMENT).read_bytes()
        self.assert_allowed()
        self.assert_allowed('index')
        self.assertEqual(before, (index.read_bytes(), (self.root / DOCUMENT).read_bytes()))
        self.assertFalse((self.root / 'scripts/__pycache__').exists())

    def test_modified_skill_and_cosmetic_document_edit_are_denied(self):
        self.write(SKILL, '# Changed behavior\n')
        with (self.root / DOCUMENT).open('a', encoding='utf-8') as stream:
            stream.write('\nCosmetic edit\n')
        self.assert_denied()

    def test_new_skill_without_registration_is_denied(self):
        self.write('.agents/skills/new/SKILL.md', '# New skill\n')
        self.assert_denied()

    def test_deleted_skill_without_registration_is_denied(self):
        (self.root / SKILL).unlink()
        self.assert_denied()

    def test_modified_and_new_support_files_are_detected(self):
        self.write(HELPER, 'VALUE = 2\n')
        self.assert_denied()
        self.refresh()
        self.assert_allowed()
        self.write('.agents/skills/fixture/assets/new.txt', 'new input\n')
        self.assert_denied()

    def test_unstaged_document_fix_cannot_validate_staged_source(self):
        self.stage()
        self.write(HELPER, 'VALUE = 2\n')
        self.git('add', '--', HELPER)
        self.refresh()
        self.assert_allowed()
        self.assert_denied('index')

    def test_unstaged_changes_do_not_invalidate_matching_index(self):
        self.stage()
        self.write(HELPER, 'VALUE = 3\n')
        self.assert_allowed('index')
        self.assert_denied('work')

    def test_unrelated_change_needs_no_inventory_update(self):
        self.stage()
        self.write('README.md', 'Unrelated change\n')
        self.git('add', '--', 'README.md')
        self.assert_allowed('index')

    def test_commit_candidate_uses_committed_contents(self):
        self.stage()
        self.git('commit', '-qm', 'fixture baseline')
        self.write(HELPER, 'VALUE = 5\n')
        self.assert_allowed('HEAD')

    def test_duplicate_entry_and_wrong_digest_are_denied(self):
        self.entries.append(dict(self.entries[0]))
        self.refresh()
        self.assert_denied()
        self.entries.pop()
        self.entries[0]['sourceDigest'] = '0' * 64
        self.refresh(update_hashes=False)
        self.assert_denied()

    def test_summary_table_must_match_metadata(self):
        path = self.root / DOCUMENT
        path.write_text(path.read_text(encoding='utf-8').replace('Fixture behavior', 'Old purpose', 1), encoding='utf-8')
        self.assert_denied()

    def test_verified_digest_cannot_silently_advance_with_source(self):
        evidence = 'work/records/harness/issue-1/issue.md'
        self.write(evidence, '<a id="verification"></a>\n# Observed result\n')
        self.entries[0]['verification'].update(status='verified', sourceDigest=self.entries[0]['sourceDigest'],
                                             environment='fixture', scope='behavior',
                                             evidence=evidence + '#verification')
        self.refresh()
        self.assert_allowed()
        self.write(HELPER, 'VALUE = 6\n')
        self.refresh()
        self.assert_denied()
        self.entries[0]['verification']['status'] = 'stale'
        self.refresh()
        self.assert_allowed()

    def test_verification_binds_evidence_without_recording_dates(self):
        evidence = 'work/records/harness/issue-1/issue.md'
        self.write(evidence, '<a id="verification"></a>\n# Observed result\n')
        verified = {'status': 'verified', 'sourceDigest': self.entries[0]['sourceDigest'],
                    'environment': 'fixture', 'scope': 'behavior',
                    'evidence': evidence + '#verification'}
        self.entries[0]['verification'] = dict(verified)
        self.refresh()
        self.assert_allowed()
        for status in ('unverified', 'stale', 'verified'):
            for forbidden in (None, 'not recorded'):
                with self.subTest(status=status, value=forbidden):
                    value = {'status': status} if status == 'unverified' else {**verified, 'status': status}
                    value['date'] = forbidden
                    self.entries[0]['verification'] = value
                    self.refresh()
                    result = self.check()
                    self.assertEqual(2, result.returncode)
                    self.assertIn('date fields are forbidden', result.stderr)

    def test_preserved_private_and_parent_paths_are_rejected(self):
        for bad in ('harness-design/secret.md', '.harness-state/state.json', '.env',
                    '../outside.py', 'C:/outside.py', 'scripts/../outside.py'):
            with self.subTest(path=bad):
                self.entries[0]['files'] = [SKILL, bad]
                self.refresh(update_hashes=False)
                self.assert_denied()

    def test_crlf_text_has_the_same_fingerprint(self):
        path = self.root / SKILL
        path.write_bytes(path.read_bytes().replace(b'\n', b'\r\n'))
        self.assert_allowed()

    def test_crlf_document_is_accepted(self):
        path = self.root / DOCUMENT
        path.write_bytes(path.read_bytes().replace(b'\n', b'\r\n'))
        self.assert_allowed()

    def test_codex_json_and_inline_toml_handlers_are_registered(self):
        json_name = '.codex/hooks.json'
        self.write(json_name, json.dumps({'hooks': {'PreToolUse': [{'matcher': 'apply_patch', 'hooks': [
            {'type': 'command', 'command': 'python scripts/probe.py'}]}]}}))
        self.assert_denied()
        self.write('scripts/probe.py', 'print("fixture")\n')
        self.entries.append(self.entry('codex:.codex/hooks.json:PreToolUse:0:0', 'codex', json_name,
                                       [json_name, 'scripts/probe.py']))
        self.refresh()
        self.assert_allowed()

        self.write('scripts/probe.py', 'print("changed")\n')
        self.assert_denied()
        self.refresh()
        toml_name = '.codex/config.toml'
        self.write(toml_name, '[[hooks.PostToolUse]]\nmatcher = "apply_patch"\n[[hooks.PostToolUse.hooks]]\ntype = "command"\ncommand = "echo fixture"\n')
        self.assert_denied()
        self.entries.append(self.entry('codex:.codex/config.toml:PostToolUse:0:0', 'codex', toml_name, [toml_name]))
        self.entries[1]['files'].append(toml_name)
        self.refresh()
        self.assert_allowed()

    def test_project_feature_config_is_required_even_without_its_own_handler(self):
        definition = '.codex/hooks.json'
        self.write(definition, json.dumps({'hooks': {'PreToolUse': [{'hooks': [
            {'type': 'command', 'command': 'echo fixture'}]}]}}))
        self.entries.append(self.entry('codex:.codex/hooks.json:PreToolUse:0:0', 'codex', definition, [definition]))
        self.refresh()
        self.assert_allowed()
        config = '.codex/config.toml'
        self.write(config, '[features]\nhooks = false\n')
        self.assert_denied()
        self.entries[1]['files'].append(config)
        self.refresh()
        self.assert_allowed()
        self.write(config, '[features]\nhooks = true\n')
        self.assert_denied()

    def test_malformed_codex_document_is_a_controlled_denial(self):
        for text in ('[]', '{"hooks": []}', '{"hooks": {"PreToolUse": [null]}}'):
            self.write('.codex/hooks.json', text)
            self.assert_denied()

    def test_new_git_definition_and_dependency_changes_are_detected(self):
        self.write('scripts/hooks/pre-commit', '#!/bin/sh\nexit 0\n')
        self.assert_denied()
        self.add_hook()
        self.assert_allowed()
        dependency = (self.root / 'scripts/harness_inventory.py').read_text(encoding='utf-8')
        self.write('scripts/harness_inventory.py', dependency + '\n# changed dependency\n')
        self.assert_denied()

    def test_standard_index_and_p4_hook_definitions_need_registration(self):
        for event in ('post-index-change', 'p4-changelist', 'p4-prepare-changelist',
                      'p4-post-changelist', 'p4-pre-submit'):
            with self.subTest(event=event):
                definition = 'scripts/hooks/' + event
                self.write(definition, '#!/bin/sh\nexit 0\n')
                self.assert_denied()
                self.entries.append(self.entry('git:' + event, 'git', definition, [definition]))
                self.refresh()
                self.assert_allowed()
                (self.root / definition).unlink()
                self.entries.pop()
                self.refresh()

    def test_unknown_file_in_hook_definition_directory_is_not_silently_ignored(self):
        self.write('scripts/hooks/future-event', '#!/bin/sh\nexit 0\n')
        self.assert_denied()

    @unittest.skipUnless(os.name == 'nt', 'Windows junction case')
    def test_worktree_junction_is_rejected_without_reading_its_target(self):
        outside = self.root / '.tmp/owned-target'
        outside.mkdir(parents=True)
        link = self.root / '.agents/skills/fixture/assets'
        result = subprocess.run(['cmd', '/d', '/c', 'mklink', '/J', str(link), str(outside)],
                                capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.addCleanup(os.rmdir, link)
        self.entries[0]['files'].append('.agents/skills/fixture/assets/unknown.txt')
        self.refresh(update_hashes=False)
        self.assert_denied()


class HookTests(RepositoryCase):
    def install(self, *args):
        return self.run_tool('install-harness-hooks.py', *args)

    def test_existing_hook_is_preserved_duplicate_install_is_noop_and_remove_restores(self):
        self.add_hook()
        hook = self.root / '.git/hooks/pre-commit'
        original = b'#!/bin/sh\nexit 0\n'
        hook.write_bytes(original)
        hook.chmod(0o755)
        self.assertEqual(0, self.install().returncode)
        self.assertNotEqual(original, hook.read_bytes())
        installed = hook.read_bytes()
        self.assertEqual(0, self.install().returncode)
        self.assertEqual(installed, hook.read_bytes())
        self.assertEqual(0, self.install('--remove').returncode)
        self.assertEqual(original, hook.read_bytes())

    def test_real_commit_runs_old_hook_then_rejects_or_accepts_candidate(self):
        self.add_hook()
        hook = self.root / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nmkdir -p .tmp\nprintf old >> .tmp/order\n', encoding='utf-8', newline='\n')
        hook.chmod(0o755)
        self.assertEqual(0, self.install().returncode)
        self.stage()
        self.write(HELPER, 'VALUE = 7\n')
        self.git('add', '--', HELPER)
        denied = self.git('commit', '-qm', 'must be denied', check=False)
        self.assertNotEqual(0, denied.returncode)
        self.refresh()
        self.git('add', '--', DOCUMENT)
        accepted = self.git('commit', '-qm', 'valid candidate', check=False)
        self.assertEqual(0, accepted.returncode, accepted.stderr)
        self.assertEqual('oldold', (self.root / '.tmp/order').read_text())

    def test_modified_wrapper_or_backup_is_not_removed(self):
        self.add_hook()
        self.assertEqual(0, self.install().returncode)
        hook = self.root / '.git/hooks/pre-commit'
        self.assertTrue(hook.exists())
        hook.write_bytes(hook.read_bytes() + b'\n# user edit\n')
        changed = hook.read_bytes()
        self.assertNotEqual(0, self.install('--remove').returncode)
        self.assertEqual(changed, hook.read_bytes())

    def test_corrupt_installation_metadata_is_preserved(self):
        self.add_hook()
        self.assertEqual(0, self.install().returncode)
        metadata = self.root / '.git/hooks/.harness-inventory-pre-commit.json'
        hook = self.root / '.git/hooks/pre-commit'
        original = hook.read_bytes()
        for invalid in ('[]', 'null', '{}'):
            with self.subTest(metadata=invalid):
                metadata.write_text(invalid, encoding='utf-8')
                result = self.install('--remove')
                self.assertNotEqual(0, result.returncode)
                self.assertNotIn('Traceback', result.stderr)
                self.assertEqual(invalid, metadata.read_text(encoding='utf-8'))
                self.assertEqual(original, hook.read_bytes())

    def test_existing_hook_rejection_is_preserved(self):
        self.add_hook()
        hook = self.root / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nexit 17\n', encoding='utf-8', newline='\n')
        hook.chmod(0o755)
        self.assertEqual(0, self.install().returncode)
        self.stage()
        self.assertNotEqual(0, self.git('commit', '-qm', 'old hook denies', check=False).returncode)

    def test_external_custom_hook_location_is_not_modified(self):
        outside = self.root.parent / (self.root.name + '-external')
        self.git('config', 'core.hooksPath', str(outside))
        result = self.install()
        self.assertNotEqual(0, result.returncode)
        self.assertFalse(outside.exists())

    def test_hook_skips_only_branches_without_both_inventory_files(self):
        self.add_hook()
        self.assertEqual(0, self.install().returncode)
        for document in DOCUMENTS:
            (self.root / document).unlink()
        self.stage()
        self.assertNotEqual(0, self.git('commit', '-qm', 'partial setup', check=False).returncode)
        (self.root / TOOLS[0]).unlink()
        self.stage()
        self.assertEqual(0, self.git('commit', '-qm', 'branch predating inventory', check=False).returncode)

    def test_unstaged_marker_deletion_cannot_skip_staged_inventory(self):
        self.add_hook()
        self.assertEqual(0, self.install().returncode)
        self.stage()
        self.write(HELPER, 'VALUE = 99\n')
        self.git('add', '--', HELPER)
        self.assert_denied('index')
        for document in DOCUMENTS:
            (self.root / document).unlink()
        (self.root / TOOLS[0]).unlink()
        denied = self.git('commit', '-qm', 'unstaged deletion must not bypass', check=False)
        self.assertNotEqual(0, denied.returncode)
        self.assertIn('Inventory checker is missing', denied.stderr)


if __name__ == '__main__':
    unittest.main()
