"""Frozen legacy enrollment and automatic protection of real new record paths."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from harness_inventory import Candidate
from rule_comments import PROFILES, POLICY, comments, inspect, record_names

LEGACY = 'work/records/harness/issue-1/issue.md'
ISSUE = 'work/records/issues/issue-2/issue.md'
TASK = 'work/records/issues/issue-2/task-001.md'
EXECUTION = 'work/records/issues/issue-2/artifacts/task-001-execution.md'


def values(profile):
    prefix, rules, _ = PROFILES[profile]
    return {r: f'<!-- {prefix}:{r}\nKeep {r}.\n-->' for r in rules}


def body(profile, state='예정'):
    summary = '' if profile == 'execution' else f'## 현재 요약\n\n- 상태: {state}\n\n'
    return '# Fictional record\n\n' + summary + '\n\n'.join(values(profile).values()) + '\n'


class CurrentRecordTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='current-record-rules-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.env = {**os.environ, 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
                    'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONUTF8': '1'}
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fictional record test')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'core.autocrlf', 'false')
        self.policy = {'schema': 1, 'legacyRecords': [LEGACY], 'profiles': {}, 'targets': [], 'revisions': []}
        for profile, (_, _, source) in PROFILES.items():
            self.write(source, '# Source\n\n```markdown\n' + body(profile) + '```\n')
            self.policy['profiles'][profile] = {'source': source, 'comments': values(profile)}
            self.policy['targets'].append({'path': source, 'profile': profile, 'mode': 'template'})
        self.write(LEGACY, '# Existing record without new comments\n')
        self.save()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8', newline='')

    def save(self):
        self.write(POLICY, json.dumps(self.policy, ensure_ascii=False))

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], env=self.env, check=True, capture_output=True)

    def errors(self, candidate='work', previous=None):
        view = Candidate(candidate, cwd=self.root, seconds=15)
        old = Candidate(previous, cwd=self.root, seconds=15) if previous else None
        return inspect(view, old)

    def commit(self):
        self.git('add', '--', 'harness', 'work')
        self.git('-c', 'core.hooksPath=' + str(self.root / 'no-hooks'), 'commit', '-qm', 'Fixture adoption')

    def test_existing_untracked_record_is_exempt_without_edit(self):
        before = (self.root / LEGACY).read_bytes()
        self.assertIn(LEGACY, record_names(Candidate('work', cwd=self.root)))
        self.assertEqual([], self.errors())
        self.assertEqual(before, (self.root / LEGACY).read_bytes())

    def test_new_issue_task_and_execution_are_automatically_enrolled(self):
        for name, profile in [(ISSUE, 'issue'), (TASK, 'task'), (EXECUTION, 'execution')]:
            self.write(name, body(profile))
        self.assertEqual([], self.errors())
        for name, profile in [(ISSUE, 'issue'), (TASK, 'task'), (EXECUTION, 'execution')]:
            self.write(name, '# Entire comment set removed\n')
            self.assertTrue(any(name in error for error in self.errors()))
            self.write(name, body(profile))

    def test_phase_and_harness_issue_locations_are_also_automatic(self):
        for parent in ['phase-001/issue-3', 'harness/issue-4']:
            name = 'work/records/' + parent + '/issue.md'
            self.write(name, '# Missing protected rules\n')
            self.assertTrue(any(name in error for error in self.errors()))
            self.write(name, body('issue'))
        self.assertEqual([], self.errors())

    def test_completed_new_record_stays_protected(self):
        self.write(ISSUE, body('issue', '완료'))
        self.assertEqual([], self.errors())
        self.write(ISSUE, body('issue', '완료').replace(values('issue')['start'], ''))
        self.assertTrue(self.errors())

    def test_current_five_states_and_legacy_values_are_separate(self):
        for state in ['예정', '진행 중', '중단', '완료', '취소']:
            self.write(TASK, body('task', state))
            self.assertEqual([], self.errors(), state)
        for state in ['검증 중', '대기', '보류', '미정']:
            self.write(TASK, body('task', state))
            self.assertTrue(any('current state' in e for e in self.errors()), state)
        self.write(TASK, body('task'))
        self.write(LEGACY, '## 현재 요약\n- 상태: 검증 중\n')
        self.assertEqual([], self.errors())

    def test_quoted_or_duplicate_state_is_not_a_valid_current_summary(self):
        raw = body('task').replace('- 상태: 예정', '```text\n- 상태: 예정\n```')
        self.write(TASK, raw)
        self.assertTrue(self.errors())
        self.write(TASK, body('task').replace('- 상태: 예정', '- 상태: 예정\n- 상태: 완료'))
        self.assertTrue(self.errors())
        self.write(TASK, body('task').replace('- 상태: 예정', '- 상태:\n예정'))
        self.assertTrue(self.errors())

    def test_state_examples_in_html_attributes_and_raw_text_are_not_summaries(self):
        from rule_comments import check_state
        summary = '## 현재 요약\n- 상태: 예정\n'
        for wrapper in ['<div title="\n{}">', '<xmp>\n{}</xmp>', '<textarea>\n{}</textarea>', '<![CDATA[\n{}]]>', '```markdown\n{}\n```', '`\n{}`']:
            self.assertTrue(check_state(wrapper.format(summary).encode('utf-8')), wrapper)

    def test_declared_previous_issue_policy_cannot_disappear(self):
        self.policy['legacyIssuePolicy'] = 'harness/issue-rule-comments.json'
        self.save()
        with self.assertRaises(ValueError):
            self.errors()

    def test_current_cli_runs_without_optional_legacy_policy_or_records(self):
        # The formal configuration must work in a fresh checkout without the
        # old local policy or its untracked historical attachments.
        (self.root / LEGACY).unlink()
        for candidate in ['work', 'index']:
            if candidate == 'index':
                self.git('add', '--', 'harness')
            result = subprocess.run([sys.executable, '-B', '-X', 'utf8',
                                     str(SCRIPTS / 'check-rule-comments.py'),
                                     '--candidate', candidate], cwd=self.root,
                                    env=self.env, capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(0, result.returncode, result.stderr)

    def test_cli_keeps_previously_present_issue_policy_protection(self):
        old = 'harness/issue-rule-comments.json'
        self.write(old, '{}')
        self.commit()
        (self.root / old).unlink()
        result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(SCRIPTS / 'check-rule-comments.py'), '--candidate', 'work'], cwd=self.root, env=self.env, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(2, result.returncode)
        self.assertIn('Previously protected Issue policy', result.stderr)

    def test_comment_changes_duplicates_nested_and_quotes(self):
        for profile in PROFILES:
            for rule, value in values(profile).items():
                for replacement in ['', value.replace('Keep', 'Alter'), value * 2, '<!-- outer\n' + value + '\n-->']:
                    with self.subTest(profile=profile, rule=rule):
                        source = PROFILES[profile][2]
                        self.write(source, '# Source\n```markdown\n' + body(profile).replace(value, replacement) + '```\n')
                        self.assertTrue(self.errors())
                        self.write(source, '# Source\n```markdown\n' + body(profile) + '```\n')
            quoted = '```markdown\n' + body(profile) + '```\n'
            self.assertEqual(({}, []), comments(quoted.encode(), profile))

    def test_code_and_raw_html_do_not_supply_live_rules(self):
        for wrapper in ['```markdown\n{}\n```', '<textarea>{}</textarea>', '<div title="{}"></div>']:
            self.assertEqual(({}, []), comments(wrapper.format(body('task')).encode(), 'task'))

    def test_index_uses_staged_policy_and_bytes_not_worktree(self):
        self.write(TASK, body('task'))
        self.git('add', '--', 'harness', 'work')
        self.write(TASK, '# Broken worktree\n')
        self.assertEqual([], self.errors('index'))
        self.assertTrue(self.errors('work'))
        self.git('add', '--', TASK)
        self.write(TASK, body('task'))
        self.assertTrue(self.errors('index'))
        self.assertEqual([], self.errors('work'))

    def test_frozen_legacy_list_cannot_capture_new_records(self):
        self.commit()
        self.write(ISSUE, '# Not a valid current issue\n')
        self.policy['legacyRecords'].append(ISSUE)
        self.save()
        self.assertTrue(any('frozen legacy list changed' in e for e in self.errors(previous='HEAD')))

    def test_profile_reset_or_source_target_removal_is_rejected(self):
        self.commit()
        self.policy['profiles']['task']['comments']['start'] = values('task')['start'].replace('Keep', 'Change')
        self.save()
        self.assertTrue(any('baseline changed' in e for e in self.errors(previous='HEAD')))
        self.policy['targets'] = self.policy['targets'][1:]
        self.save()
        with self.assertRaises(ValueError):
            self.errors(previous='HEAD')

    def test_deleted_new_record_is_not_silently_unenrolled(self):
        self.write(ISSUE, body('issue'))
        self.commit()
        (self.root / ISSUE).unlink()
        self.assertTrue(any('protected file is missing' in e for e in self.errors(previous='HEAD')))

    def test_reference_mode_is_confined_to_explicit_examples(self):
        name = 'harness/examples/task-reference.md'
        self.write(name, body('task', '<미확정 참조>'))
        self.policy['targets'].append({'path': name, 'profile': 'task', 'mode': 'reference'})
        self.save()
        self.assertEqual([], self.errors())
        self.policy['targets'][-1]['path'] = TASK
        self.save()
        with self.assertRaises(ValueError):
            self.errors()

    def test_unknown_artifacts_and_phase_bodies_are_not_records(self):
        for name in ['work/records/phase-001/phase.md', 'work/records/issues/issue-2/artifacts/task-doc-suite/cases/sample/task.md', 'work/records/issues/issue-2/artifacts/task-input.md']:
            self.write(name, '# Historical input\n')
        self.assertEqual([], self.errors())

    def test_unsafe_legacy_paths_and_directory_wildcards_are_invalid(self):
        for value in ['work/records/harness/**', '../outside.md', 'harness-design/issue.md', 'work/records/harness/issue-1/../issue.md']:
            self.policy['legacyRecords'] = [value]
            self.save()
            with self.assertRaises(ValueError):
                self.errors()

    def test_scoped_user_revision_is_exact_and_needs_real_anchor(self):
        self.write(TASK, body('task'))
        approval = 'work/records/issues/issue-2/artifacts/revision.md'
        self.write(approval, '<a id="decision"></a>\nActual fixture instruction\n')
        before = values('task')['start']
        replacement = before.replace('Keep', 'Revise')
        self.write(TASK, body('task').replace(before, replacement))
        self.policy['revisions'] = [{'path':TASK,'profile':'task','rule':'start','before':before,'replacement':replacement,'approval':approval+'#decision'}]
        self.save()
        self.assertEqual([], self.errors())
        self.policy['revisions'][0]['approval'] = approval + '#missing'
        self.save()
        with self.assertRaises(ValueError):
            self.errors()

    def test_cli_and_hook_feedback_use_the_shared_policy(self):
        self.write(TASK, '# No protected comments\n')
        script = SCRIPTS / 'check-rule-comments.py'
        result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(script), '--candidate', 'work'], cwd=self.root, env=self.env, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(2, result.returncode, result.stderr)
        event = json.dumps({'hook_event_name':'PostToolUse','tool_name':'apply_patch'})
        result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(script), '--hook'], cwd=self.root, env=self.env, input=event, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(0, result.returncode)
        self.assertEqual('block', json.loads(result.stdout)['decision'])
        self.assertIn('task-rule:', json.loads(result.stdout)['reason'])


if __name__ == '__main__':
    unittest.main()
