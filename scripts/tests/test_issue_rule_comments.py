"""Issue rule preservation in disposable worktrees, indices and hook events."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from issue_rule_comments import RULES, POLICY, baseline, comments

SCRIPT = SCRIPTS / 'check-issue-rule-comments.py'
TARGET = 'work/records/harness/issue-fixture/issue.md'
APPROVAL = 'work/records/harness/issue-fixture/approval.md'
VALUES = {r: f'<!-- issue-rule:{r}\nKeep {r}. -->' for r in RULES}
BODY = '# Fictional Issue\n\n' + '\n\n'.join(VALUES.values()) + '\n'


class ParserTests(unittest.TestCase):
    def test_template_and_line_endings(self):
        wrapped = '# Template\n```markdown\n' + BODY + '```\n'
        self.assertEqual(VALUES, baseline(wrapped.replace('\n', '\r\n').encode()))

    def test_nested_unclosed_and_duplicate_comments(self):
        for text in ['<!-- outer\n' + VALUES['start'] + '\n-->',
                     VALUES['start'].replace('-->', ''), VALUES['start'] * 2]:
            with self.subTest(text=text):
                self.assertTrue(comments(text.encode())[1])

    def test_quoted_rules_are_not_live_rules(self):
        self.assertEqual(({}, []), comments(('```markdown\n' + BODY + '```\n').encode()))

    def test_inline_examples_do_not_duplicate_or_swallow_live_rules(self):
        quoted = '`<!-- issue-rule:start -->`\n`<!--`\n' + BODY
        self.assertEqual((VALUES, []), comments(quoted.encode()))

    def test_code_inside_a_real_comment_is_preserved(self):
        value = '<!-- issue-rule:start\n```text\nquoted code\n```\n-->'
        self.assertEqual(({'start': value}, []), comments(value.encode()))

    def test_escaped_openers_are_not_real_comments(self):
        self.assertEqual(({}, []), comments(BODY.replace('<!--', r'\<!--').encode()))
        self.assertEqual((VALUES, []), comments(BODY.replace('<!--', r'\\<!--').encode()))

    def test_indented_code_is_not_a_duplicate_live_rule(self):
        sample = '\n'.join('    ' + line for line in VALUES['start'].splitlines())
        self.assertEqual((VALUES, []), comments((BODY + '\n' + sample + '\n').encode()))

    def test_markup_in_attributes_is_not_a_real_comment(self):
        self.assertEqual(({}, []), comments(('<div title="' + BODY + '"></div>').encode()))

    def test_raw_text_and_declarations_do_not_contain_live_comments(self):
        for tag in ['script', 'style', 'textarea', 'title']:
            with self.subTest(tag=tag):
                self.assertEqual(({}, []), comments((f'<{tag}>' + BODY + f'</{tag}>').encode()))
        self.assertEqual(({}, []), comments(('<![CDATA[' + BODY + ']]>').encode()))

    def test_real_comments_inside_ordinary_html_are_still_checked(self):
        self.assertEqual((VALUES, []), comments(('<div title="regular">\n' + BODY + '</div>').encode()))


class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='issue-comment-check-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.env = {**os.environ, 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
                    'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONUTF8': '1'}
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fictional hook test')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'core.autocrlf', 'false')
        self.policy = {'schema': 1, 'baseline': {'comments': VALUES},
                       'targets': [{'path': TARGET, 'mode': 'body'}], 'revisions': []}
        self.write(TARGET, BODY)
        self.save_policy()

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8', newline='')

    def save_policy(self):
        self.write(POLICY, json.dumps(self.policy))

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.root, env=self.env, capture_output=True, check=True)

    def check(self, candidate='work', hook=False, cwd=None):
        args = ['--hook'] if hook else ['--candidate', candidate]
        event = json.dumps({'hook_event_name': 'PostToolUse', 'tool_name': 'apply_patch', 'cwd': str(self.root)}) if hook else None
        return subprocess.run([sys.executable, '-B', '-X', 'utf8', str(SCRIPT), *args],
                              cwd=cwd or self.root, input=event, env=self.env,
                              capture_output=True, text=True, encoding='utf-8')

    def test_normal_edit_and_six_other_rules_remain_editable(self):
        self.write(TARGET, BODY + '- Status: draft\n<!-- issue-rule:summary\nRevised non-protected rule. -->\n')
        self.assertEqual(0, self.check().returncode)

    def test_each_protected_rule_change_removal_and_rename_are_denied(self):
        for rule in RULES:
            for replacement in ['', VALUES[rule].replace('Keep', 'Change'), VALUES[rule].replace('issue-rule:', 'other:')]:
                with self.subTest(rule=rule, replacement=replacement):
                    self.write(TARGET, BODY.replace(VALUES[rule], replacement))
                    result = self.check()
                    self.assertEqual(2, result.returncode, result.stderr)
                    self.assertIn('issue-rule:' + rule, result.stderr)

    def test_all_removed_or_enrolled_file_deleted_is_denied(self):
        self.write(TARGET, '# Fictional Issue\n')
        self.assertEqual(2, self.check().returncode)
        (self.root / TARGET).unlink()
        self.assertEqual(2, self.check().returncode)

    def test_unenrolled_legacy_issue_is_not_forced_to_adopt_the_draft(self):
        self.write('work/records/harness/legacy/issue.md', '# Existing Issue\n')
        self.assertEqual(0, self.check().returncode)

    def test_index_is_independent_of_unstaged_content(self):
        self.git('add', '--', POLICY, TARGET)
        self.write(TARGET, '# Broken working file\n')
        self.assertEqual(0, self.check('index').returncode)
        self.assertEqual(2, self.check().returncode)
        self.git('add', '--', TARGET)
        self.write(TARGET, BODY)
        self.assertEqual(2, self.check('index').returncode)
        self.assertEqual(0, self.check().returncode)

    def revision(self, rule, replacement):
        self.write(APPROVAL, '# Fictional approval evidence\n<a id="explicit-revision"></a>\nUser-approved test scope only.\n')
        self.policy['revisions'] = [{'path': TARGET, 'rule': rule, 'before': VALUES[rule],
                                    'replacement': replacement, 'approval': APPROVAL + '#explicit-revision'}]
        self.save_policy()

    def test_explicit_revision_is_exact_and_does_not_authorize_other_changes(self):
        value = VALUES['state'].replace('Keep state.', 'Explicitly revised state.')
        self.revision('state', value)
        self.write(TARGET, BODY.replace(VALUES['state'], value))
        self.assertEqual(0, self.check().returncode)
        self.write(TARGET, BODY.replace(VALUES['state'], value).replace('Keep start.', 'Unauthorized change.'))
        self.assertEqual(2, self.check().returncode)

    def test_explicit_comment_removal_is_supported_without_authorizing_file_deletion(self):
        self.revision('completion', None)
        self.write(TARGET, BODY.replace(VALUES['completion'], ''))
        self.assertEqual(0, self.check().returncode)
        (self.root / TARGET).unlink()
        self.assertEqual(2, self.check().returncode)

    def test_missing_approval_baseline_mismatch_and_out_of_scope_rule_are_denied(self):
        self.revision('state', VALUES['state'])
        for field, value in [('approval', APPROVAL + '#missing'), ('before', 'unverified'), ('rule', 'summary')]:
            change = self.policy['revisions'][0]
            old = change[field]
            change[field] = value
            self.save_policy()
            self.assertEqual(2, self.check().returncode)
            change[field] = old

    def test_approval_requires_an_active_anchor_not_matching_text_or_quoted_markup(self):
        self.revision('state', VALUES['state'])
        for text in ['grid="explicit-revision"',
                     '```html\n<a id="explicit-revision"></a>\n```\n',
                     '`<a id="explicit-revision"></a>`',
                     '<!-- <a id="explicit-revision"></a> -->',
                     '\\<a id="explicit-revision"></a>',
                     '<div title=\'<a id="explicit-revision"></a>\'></div>',
                     '<textarea><a id="explicit-revision"></a></textarea>']:
            with self.subTest(text=text):
                self.write(APPROVAL, text)
                result = self.check()
                self.assertEqual(2, result.returncode)
                self.assertIn('approval reference is unverified', result.stderr)

    def test_target_cannot_disappear_by_removing_all_comments_and_enrollment_together(self):
        self.git('add', '--', POLICY, TARGET)
        self.git('commit', '-qm', 'Fictional enrolled baseline')
        self.policy['targets'] = [{'path': 'work/records/harness/other/issue.md', 'mode': 'body'}]
        self.write(self.policy['targets'][0]['path'], BODY)
        self.save_policy()
        self.write(TARGET, '# No rules\n')
        self.assertEqual(2, self.check().returncode)

    def test_enrolled_baseline_cannot_be_redefined_to_accept_unapproved_changes(self):
        self.git('add', '--', POLICY, TARGET)
        self.git('commit', '-qm', 'Fictional immutable baseline')
        self.policy['baseline']['comments'] = dict(VALUES)
        changed = VALUES['state'].replace('Keep state.', 'Silently redefined baseline.')
        self.policy['baseline']['comments']['state'] = changed
        self.save_policy()
        self.write(TARGET, BODY.replace(VALUES['state'], changed))
        result = self.check()
        self.assertEqual(2, result.returncode)
        self.assertIn('captured baseline changed', result.stderr)

    def test_hook_reports_the_completed_edit_without_rolling_it_back(self):
        content = BODY.replace(VALUES['start'], '')
        self.write(TARGET, content)
        result = self.check(hook=True)
        self.assertEqual(0, result.returncode, 'Hook JSON feedback uses the exit-0 contract')
        feedback = json.loads(result.stdout)
        self.assertEqual('block', feedback['decision'])
        self.assertIn('issue-rule:start', feedback['reason'])
        self.assertEqual(content, (self.root / TARGET).read_text(encoding='utf-8'))

    def test_registered_command_works_from_a_subdirectory(self):
        for name in ['check-rule-comments.py', 'check-issue-rule-comments.py', 'issue_rule_comments.py', 'harness_inventory.py']:
            self.write('scripts/' + name, (SCRIPTS / name).read_text(encoding='utf-8'))
        config = json.loads((SCRIPTS.parent / '.codex/hooks.json').read_text(encoding='utf-8'))
        matches = [(group, handler) for group in config['hooks']['PostToolUse']
                   for handler in group['hooks'] if 'check-rule-comments.py' in handler.get('command', '')]
        self.assertEqual(1, len(matches), 'Exactly one common rule checker must be registered')
        group, handler = matches[0]
        self.assertEqual('*', group['matcher'])
        self.assertFalse(handler['async'])
        command = handler['commandWindows' if os.name == 'nt' else 'command']
        cwd = self.root / 'nested directory'
        cwd.mkdir()
        event = json.dumps({'hook_event_name': 'PostToolUse', 'tool_name': 'Bash', 'cwd': str(cwd)})
        for body, violation in [(BODY, False), ('# Missing rules\n', True)]:
            self.write(TARGET, body)
            result = subprocess.run(command, shell=True, cwd=cwd, input=event, env=self.env,
                                    capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(0, result.returncode, result.stderr)
            if violation:
                self.assertEqual('block', json.loads(result.stdout)['decision'])

    def test_missing_or_malformed_policy_is_unverified(self):
        self.write(POLICY, '{}')
        self.assertEqual(2, self.check().returncode)
        (self.root / POLICY).unlink()
        self.assertEqual(2, self.check().returncode)


if __name__ == '__main__':
    unittest.main()
