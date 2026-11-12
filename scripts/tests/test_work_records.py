"""Changed record candidates: narrow errors, non-blocking length warnings."""

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
SCRIPT = SCRIPTS / 'check-work-records.py'
RECORD = 'work/records/harness/issue-1/issue.md'


def checker():
    spec = importlib.util.spec_from_file_location('record_check', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RuleTests(unittest.TestCase):
    def test_needed_decisions_blockers_and_domain_dates_are_allowed(self):
        text = '# Issue\n- 결정: 현재 허용 범위 변경. 근거: 사용자 승인.\n- 막힘: CI 실패로 병합 보류.\n- 출시일: 2030-01-02\n- API 원본: {"createdAt": "2030-01-02T00:00:00Z"}\n'
        self.assertEqual(([], []), checker().inspect_record(RECORD, text, None))

    def test_explicit_new_record_dates_are_rejected_in_text_and_metadata(self):
        for text in ['- 작성일: 2030-01-02\n', '- **작성일**: `2030-01-02`\n', '| 검증일 | 2030/01/02 |\n', '{"recordedAt": "2030-01-02T00:00:00Z"}\n']:
            with self.subTest(text=text):
                self.assertTrue(checker().inspect_record(RECORD, text, None)[0])

    def test_unchanged_old_date_is_not_a_new_violation(self):
        old = '# Issue\n- 작성일: 2030-01-02\n- 결과: 대기\n'
        new = old.replace('결과: 대기', '결과: 통과, 근거 연결')
        self.assertEqual(([], []), checker().inspect_record(RECORD, new, old))

    def test_new_dated_record_filename_is_rejected_but_old_name_is_not(self):
        name = 'work/records/harness/issue-1/artifacts/result-2030-01-02.md'
        self.assertTrue(checker().inspect_record(name, '# Result\n', None)[0])
        self.assertFalse(checker().inspect_record(name, '# Result\nOK\n', '# Result\n')[0])

    def test_execution_blocks_belong_in_artifacts(self):
        for marker in ['tdd-plan', 'tdd-evidence', 'harness-inventory']:
            text = '<!-- ' + marker + ' -->\n```json\n{}\n```\n'
            self.assertTrue(checker().inspect_record(RECORD, text, None)[0])
            self.assertEqual(([], []), checker().inspect_record('work/records/harness/issue-1/artifacts/evidence.md', text, None))
            self.assertEqual(([], []), checker().inspect_record('work/records/harness/issue-1/artifacts/task-001.md', text, None))

    def test_native_artifact_payload_is_preserved_but_prose_date_is_rejected(self):
        name = 'work/records/harness/issue-1/artifacts/evidence.md'
        text = '```json\n{"recordedAt": "2030-01-02T00:00:00Z"}\n```\n'
        self.assertEqual(([], []), checker().inspect_record(name, text, None))
        self.assertTrue(checker().inspect_record(name, text + '- 기록일: 2030-01-02\n', None)[0])

    def test_100_lines_allowed_101_warned_including_blank_lines(self):
        self.assertEqual(([], []), checker().inspect_record(RECORD, '# Issue\n' + '\n' * 99, None))
        errors, warnings = checker().inspect_record(RECORD, '# Issue\n' + '\n' * 100, None)
        self.assertFalse(errors)
        self.assertEqual(1, len(warnings))
        self.assertIn('101', warnings[0])
        self.assertTrue(checker().inspect_record('work/records/phase-001/issue-1/task-001.md', 'x\n' * 101, None)[1])
        self.assertFalse(checker().inspect_record('work/records/harness/issue-1/artifacts/long.md', 'x\n' * 101, None)[1])
        self.assertFalse(checker().inspect_record('work/records/harness/issue-1/artifacts/issue.md', 'x\n' * 101, None)[1])


class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='record-check-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Record fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.root, capture_output=True, text=True, check=True)

    def write(self, text):
        path = self.root / RECORD
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')

    def run_check(self, *args):
        return subprocess.run([sys.executable, '-B', '-X', 'utf8', str(SCRIPT), *args], cwd=self.root, capture_output=True, text=True, encoding='utf-8')

    def test_initial_index_reads_staged_content_and_warning_succeeds(self):
        self.write('current\n' * 101)
        self.git('add', '--', RECORD)
        self.write('- 작성일: 2030-01-02\n')
        result = self.run_check()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('WARNING', result.stderr)
        self.git('add', '--', RECORD)
        self.write('current\n')
        self.assertEqual(2, self.run_check().returncode)

    def test_committed_candidate_uses_parent_diff_not_worktree(self):
        self.write('# Issue\n- 작성일: 2030-01-02\n')
        self.git('add', '--', RECORD)
        self.git('commit', '-qm', 'old fixture')
        self.write('# Issue\n- 작성일: 2030-01-02\n- 결과: current\n')
        self.git('add', '--', RECORD)
        self.git('commit', '-qm', 'current fixture')
        self.write('- 검증일: 2031-02-03\n')
        result = self.run_check('--candidate', 'HEAD')
        self.assertEqual(0, result.returncode, result.stderr)
        self.git('add', '--', RECORD)
        self.git('commit', '-qm', 'new invalid fixture')
        self.assertEqual(2, self.run_check('--candidate', 'HEAD').returncode)

    def test_unmodified_long_record_does_not_warn(self):
        self.write('current\n' * 101)
        self.git('add', '--', RECORD)
        self.git('commit', '-qm', 'old long fixture')
        result = self.run_check()
        self.assertEqual((0, ''), (result.returncode, result.stderr))

    def test_sparse_ci_prepares_missing_parent_documents_only(self):
        self.git('config', 'uploadpack.allowFilter', 'true')
        for value in ('prior', 'current'):
            (self.root / 'AGENTS.md').write_text('# ' + value + '\n', encoding='utf-8')
            (self.root / 'unrelated.txt').write_text(value + '\n', encoding='utf-8')
            self.git('add', '--', 'AGENTS.md', 'unrelated.txt')
            self.git('commit', '-qm', value + ' fixture')
        clone = self.root / 'clone'
        self.git('clone', '--filter=blob:none', '--no-checkout', '--depth=2', self.root.as_uri(), str(clone))
        self.git('-C', str(clone), 'sparse-checkout', 'set', '--no-cone', '/AGENTS.md')
        self.git('-C', str(clone), 'checkout', '-q', 'HEAD')
        def check():
            return subprocess.run([sys.executable, '-B', '-X', 'utf8', str(SCRIPT), '--candidate', 'HEAD'],
                                  cwd=clone, capture_output=True, text=True, encoding='utf-8')
        failed = check()
        self.assertEqual(2, failed.returncode)
        self.assertIn('Invalid or oversized source object: AGENTS.md', failed.stderr)
        code = (SCRIPTS / 'quality/record-base.py').read_text(encoding='utf-8')
        prepared = subprocess.run([sys.executable, '-B', '-X', 'utf8', '-c', code], cwd=clone,
                                  capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(0, prepared.returncode, prepared.stderr)
        self.assertEqual(0, check().returncode)
        unrelated = self.git('-C', str(clone), 'rev-parse', 'HEAD^:unrelated.txt').stdout.strip()
        objects = subprocess.run(['git', 'cat-file', '--batch-check'], cwd=clone,
                                 input=unrelated + '\n', capture_output=True, text=True,
                                 env={**os.environ, 'GIT_NO_LAZY_FETCH': '1'}, check=True)
        self.assertIn(' missing', objects.stdout)


if __name__ == '__main__':
    unittest.main()
