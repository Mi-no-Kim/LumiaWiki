"""Behavior checks with a disposable Git index; no project records are edited."""

from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest

from check_task_status import staged_state


TASK = "work/records/phase-001/issue-15/task-001.md"


class StagedTaskStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        subprocess.run(["git", "init", "--quiet", str(self.repo)], check=True)
        self.path = self.repo / TASK
        self.path.parent.mkdir(parents=True)

    def stage(self, summary):
        self.path.write_text("# Task\n\n## 현재 요약\n" + summary +
                             "\n## 과거 기록\n- 상태: 예정\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "--", TASK], check=True,
                       capture_output=True)

    def test_reads_index_even_when_worktree_says_completed(self):
        self.stage("- 상태: 진행 중\n")
        self.path.write_text("## 현재 요약\n- 상태: 완료\n", encoding="utf-8")
        before = self.path.read_bytes()
        self.assertEqual(staged_state(self.repo, TASK), "진행 중")
        self.assertEqual(self.path.read_bytes(), before)

    def test_cli_status_is_readable_in_windows_default_encoding(self):
        self.stage("- 상태: 완료\n")
        before = (self.repo / ".git/index").read_bytes()
        for expected, code, label in (("완료", 0, "일치:"), ("검증 중", 1, "불일치:")):
            with self.subTest(expected=expected):
                result = subprocess.run(
                    [sys.executable, "-B", str(Path(__file__).with_name("check_task_status.py")),
                     "--repo", str(self.repo), "--task", TASK, "--expect-state", expected],
                    capture_output=True,
                    env={**os.environ, "PYTHONIOENCODING": "cp949", "PYTHONUTF8": "0"},
                )
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertEqual(result.stderr, b"")
                self.assertIn(label, result.stdout.decode("cp949"))
                self.assertEqual((self.repo / ".git/index").read_bytes(), before)

    def test_completed_and_intentional_pause_are_distinct(self):
        for state in ("완료", "보류", "취소"):
            self.stage(f"- 상태: {state}\n")
            self.assertEqual(staged_state(self.repo, TASK), state)

    def test_missing_staged_record_is_unconfirmed(self):
        with self.assertRaises(ValueError):
            staged_state(self.repo, TASK)

    def test_ambiguous_or_unknown_state_is_unconfirmed(self):
        for summary in ("- 상태: 완료\n- 상태: 보류\n", "- 상태: 알 수 없음\n", ""):
            self.stage(summary)
            with self.assertRaises(ValueError):
                staged_state(self.repo, TASK)

    def test_disallowed_paths_are_rejected_before_git(self):
        for path in ("harness-design/task-001.md", ".harness-state/task-001.md",
                     "work/records/../task-001.md", "C:/task-001.md",
                     TASK.replace("/", "\\")):
            with self.assertRaises(ValueError):
                staged_state(self.repo / "nonexistent", path)


if __name__ == "__main__":
    unittest.main()
