"""Authored-size warnings and profile boundaries; fixtures use caller TMPDIR."""
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parent
POLICY = json.loads((ROOT / 'harness/rule-comments.json').read_text(encoding='utf-8'))
sys.path.insert(0, str(SCRIPTS))


def record_checker():
    spec = importlib.util.spec_from_file_location('pilot_record_checker', SCRIPTS / 'check-work-records.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def task_body():
    text = (ROOT / 'harness/templates/task.md').read_text(encoding='utf-8')
    return re.search(r'^```markdown\n(.*?)^```', text, re.M | re.S)[1]


class AuthoredLengthTests(unittest.TestCase):
    def setUp(self):
        self.module = record_checker()
        self.fixed = list(POLICY['profiles']['task']['comments'].values())
        self.comment = POLICY['profiles']['task']['comments']['tags']

    def test_fixed_live_standalone_comments_do_not_consume_warning_budget(self):
        errors, warnings = self.module.inspect_record('work/records/harness/issue-1/task-001.md', task_body(), None, self.fixed)
        self.assertEqual(([], []), (errors, warnings))
        self.assertLess(self.module.authored_line_count(task_body(), self.fixed), 100)
        self.assertGreater(len(task_body().splitlines()), 100)

    def test_written_content_above_threshold_still_warns(self):
        text = '\n'.join(self.fixed) + '\n' + 'authored decision\n' * 101
        errors, warnings = self.module.inspect_record('work/records/harness/issue-1/task-001.md', text, None, self.fixed)
        self.assertFalse(errors)
        self.assertEqual(1, len(warnings))
        self.assertIn('101 authored lines', warnings[0])

    def test_fenced_or_changed_comments_remain_counted(self):
        for text in ['```markdown\n' + self.comment + '\n```', self.comment.replace('Task 태그', 'Changed 태그', 1)]:
            with self.subTest(text=text[:30]):
                self.assertEqual(len(text.splitlines()), self.module.authored_line_count(text, self.fixed))

    def test_inline_prose_is_not_hidden_by_a_protected_comment(self):
        text = 'authored decision ' + self.comment + '\n'
        self.assertEqual(len(text.splitlines()), self.module.authored_line_count(text, self.fixed))

    def test_crlf_and_lf_counts_match(self):
        self.assertEqual(self.module.authored_line_count(task_body(), self.fixed),
                         self.module.authored_line_count(task_body().replace('\n', '\r\n'), self.fixed))

    def test_issue_cli_does_not_exclude_task_only_comments(self):
        with tempfile.TemporaryDirectory(prefix='profile-length-') as folder:
            root = Path(folder)
            subprocess.run(['git', 'init', '-q'], cwd=root, check=True, capture_output=True)
            (root / 'harness').mkdir()
            (root / 'harness/rule-comments.json').write_text(json.dumps(POLICY), encoding='utf-8')
            name = 'work/records/harness/issue-1/issue.md'
            target = root / name
            target.parent.mkdir(parents=True)
            issue_comments = list(POLICY['profiles']['issue']['comments'].values())
            text = '\n'.join(issue_comments) + '\n' + self.comment + '\n'
            text += 'authored decision\n' * (110 - self.module.authored_line_count(text, issue_comments))
            target.write_text(text, encoding='utf-8')
            subprocess.run(['git', 'add', '--', 'harness', 'work'], cwd=root, check=True, capture_output=True)
            result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(SCRIPTS / 'check-work-records.py'), '--candidate', 'index'], cwd=root, capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn('110 authored lines', result.stderr)

if __name__ == '__main__':
    unittest.main()
