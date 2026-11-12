import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
TASK = "work/records/phase-001/issue-1/task-001.md"


class FlowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="lumia-tdd-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "scripts").mkdir()
        for name in ("tdd_core.py", "tdd-run.py", "tdd-check.py", "test-python.py", "install-hooks.py"):
            shutil.copyfile(SCRIPTS / name, self.root / "scripts" / name)
        self.write(".gitignore", ".tmp/\n__pycache__/\n")
        self.write("frontend/src/probe.py", "def answer():\n    return 0\n")
        self.write("tests/test_probe.py", "import unittest\nfrom frontend.src.probe import answer\nclass ProbeTests(unittest.TestCase):\n    def test_answer(self):\n        self.assertEqual(1, answer())\n")
        self.cycle = {"id": "probe", "kind": "behavior", "expectation": "answer is one", "targets": ["frontend/src/probe.py"], "tests": ["tests/test_probe.py"], "settings": [], "adapter": "unittest", "expectedFailures": ["test_probe.ProbeTests.test_answer"], "command": [sys.executable, "{root}/scripts/test-python.py", "--report", "{report}", "--run-id", "{run_id}", "--", "discover", "-s", "tests", "-p", "test_probe.py"]}
        self.save_plan()
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "TDD fixture")
        self.git("add", ".")
        self.git("commit", "-qm", "synthetic fixture baseline")

    def write(self, name, text):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def save_plan(self):
        self.write(TASK, '# Synthetic test fixture only\n<!-- tdd-plan -->\n```json\n' + json.dumps({"schema": 1, "cycles": [self.cycle]}) + '\n```\n')

    def git(self, *args, cwd=None, check=True):
        return subprocess.run(["git", *args], cwd=cwd or self.root, capture_output=True, text=True, check=check)

    def tool(self, name, *args, input=None, cwd=None):
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1"}
        return subprocess.run([sys.executable, "-X", "utf8", str((cwd or self.root) / "scripts" / name), *args], input=input, cwd=cwd or self.root, capture_output=True, text=True, env=env)

    def run_phase(self, phase, *extra):
        return self.tool("tdd-run.py", "--task", TASK, "--cycle", "probe", "--phase", phase, *extra, "--", *self.cycle["command"])

    def edit_check(self):
        event = {"tool_name": "apply_patch", "tool_input": {"command": "*** Begin Patch\n*** Update File: frontend/src/probe.py\n@@\n-    return 0\n+    return 1\n*** End Patch"}}
        return self.tool("tdd-check.py", "--hook", "--task", TASK, input=json.dumps(event))

    def green(self, export=False):
        red = self.run_phase("red")
        self.assertEqual(0, red.returncode, red.stderr)
        self.write("frontend/src/probe.py", "def answer():\n    return 1\n")
        result = self.run_phase("green", *( ["--export"] if export else []))
        self.assertEqual(0, result.returncode, result.stderr)

    def test_hook_without_red_explicitly_denies_without_writing(self):
        before = (self.root / "frontend/src/probe.py").read_bytes()
        result = self.edit_check()
        self.assertIn('"deny"', result.stdout)
        self.assertEqual(before, (self.root / "frontend/src/probe.py").read_bytes())

    def test_hook_json_denial_is_a_successful_protocol_response(self):
        result = self.edit_check()
        self.assertIn('"deny"', result.stdout)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_real_red_opens_edits_green_closes_old_red(self):
        self.assertEqual(0, self.run_phase("red").returncode)
        self.assertEqual("", self.edit_check().stdout)
        self.green()
        self.assertIn('"deny"', self.edit_check().stdout)

    def test_candidate_uses_index_not_unstaged_content(self):
        self.green()
        self.git("add", "frontend/src/probe.py")
        self.write("frontend/src/probe.py", "def answer():\n    return 2\n")
        good = self.tool("tdd-check.py", "--candidate", "index", "--task", TASK)
        self.assertEqual(0, good.returncode, good.stderr)
        self.git("add", "frontend/src/probe.py")
        self.assertNotEqual(0, self.tool("tdd-check.py", "--candidate", "index", "--task", TASK).returncode)

    def test_changed_tests_invalidate_open_red(self):
        self.assertEqual(0, self.run_phase("red").returncode)
        with (self.root / "tests/test_probe.py").open("a", encoding="utf-8") as f:
            f.write("\n# changed test input\n")
        self.assertIn('"deny"', self.edit_check().stdout)

    def test_zero_tests_and_setup_errors_are_not_red(self):
        self.cycle["command"][-1] = "missing_tests.py"
        self.save_plan()
        self.assertNotEqual(0, self.run_phase("red").returncode)

    def test_reporter_emits_executed_assertion_failure(self):
        result = self.tool("test-python.py", "--report", ".tmp/report.json", "--run-id", "probe", "--", "discover", "-s", "tests")
        report = self.root / ".tmp/report.json"
        data = json.loads(report.read_text()) if report.exists() else {}
        self.assertEqual((1, 1, 0), (data.get("tests"), data.get("failures"), data.get("errors")))
        self.assertEqual(1, result.returncode)

    def test_durable_green_survives_runtime_state_cleanup(self):
        self.green(export=True)
        self.git("add", "frontend/src/probe.py", TASK)
        shutil.rmtree(self.root / ".tmp") if (self.root / ".tmp").exists() else None
        result = self.tool("tdd-check.py", "--candidate", "index", "--task", TASK)
        self.assertEqual(0, result.returncode, result.stderr)
        text = (self.root / TASK).read_text()
        self.assertIn("<!-- tdd-evidence -->", text)

    def test_hook_install_preserves_previous_hook_and_restores_it(self):
        hook = self.root / ".git/hooks/pre-commit"
        original = b"#!/bin/sh\nexit 0\n"
        hook.write_bytes(original)
        hook.chmod(0o755)
        self.assertEqual(0, self.tool("install-hooks.py").returncode)
        self.assertNotEqual(original, hook.read_bytes())
        installed = hook.read_bytes()
        self.assertEqual(0, self.tool("install-hooks.py").returncode)
        self.assertEqual(installed, hook.read_bytes())
        self.assertEqual(0, self.tool("install-hooks.py", "--remove").returncode)
        self.assertEqual(original, hook.read_bytes())

    def test_test_only_change_does_not_reuse_old_green(self):
        self.green()
        self.write("tests/test_probe.py", "# changed test input\n")
        self.git("add", "tests/test_probe.py")
        self.assertNotEqual(0, self.tool("tdd-check.py", "--candidate", "index", "--task", TASK).returncode)

    def test_worktree_cannot_reuse_an_open_red(self):
        self.assertEqual(0, self.run_phase("red").returncode)
        linked = self.root.with_name(self.root.name + "-linked")
        self.git("worktree", "add", "--detach", str(linked), "HEAD")
        self.addCleanup(self.git, "worktree", "remove", "--force", str(linked))
        event = {"tool_name": "apply_patch", "tool_input": {"command": "*** Begin Patch\n*** Update File: frontend/src/probe.py\n@@\n-x\n+y\n*** End Patch"}}
        result = self.tool("tdd-check.py", "--hook", "--task", TASK, input=json.dumps(event), cwd=linked)
        self.assertIn('"deny"', result.stdout)

    def test_durable_evidence_can_verify_a_different_worktree(self):
        self.green(export=True)
        self.git("add", "frontend/src/probe.py", TASK)
        self.git("commit", "-qm", "verified synthetic candidate")
        linked = self.root.with_name(self.root.name + "-linked")
        self.git("worktree", "add", "--detach", str(linked), "HEAD")
        self.addCleanup(self.git, "worktree", "remove", "--force", str(linked))
        result = self.tool("tdd-check.py", "--candidate", "HEAD", "--task", TASK, cwd=linked)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('"deny"', self.tool("tdd-check.py", "--hook", "--task", TASK,
            input=json.dumps({"tool_name": "apply_patch", "tool_input": {"command": "*** Begin Patch\n*** Update File: frontend/src/probe.py\n@@\n-x\n+y\n*** End Patch"}}), cwd=linked).stdout)

    def test_git_hook_runs_previous_hook_then_rejects_or_accepts_real_commit(self):
        hook = self.root / ".git/hooks/pre-commit"
        hook.write_text('#!/bin/sh\nmkdir -p .tmp\nprintf old >> .tmp/hook-order\n', encoding="utf-8", newline="\n")
        hook.chmod(0o755)
        self.assertEqual(0, self.tool("install-hooks.py").returncode)
        self.assertEqual(0, self.tool("tdd-run.py", "--task", TASK, "--activate").returncode)
        self.write("frontend/src/probe.py", "def answer():\n    return 2\n")
        self.git("add", "frontend/src/probe.py")
        denied = self.git("commit", "-qm", "must be denied", check=False)
        self.assertNotEqual(0, denied.returncode)
        self.write("frontend/src/probe.py", "def answer():\n    return 0\n")
        self.green()
        self.git("add", "frontend/src/probe.py")
        accepted = self.git("commit", "-qm", "verified candidate", check=False)
        self.assertEqual(0, accepted.returncode, accepted.stderr)
        self.assertEqual("oldold", (self.root / ".tmp/hook-order").read_text())

    def test_modified_hook_is_not_overwritten_or_removed(self):
        self.assertEqual(0, self.tool("install-hooks.py").returncode)
        hook = self.root / ".git/hooks/pre-commit"
        hook.write_bytes(hook.read_bytes() + b"\n# user modification\n")
        changed = hook.read_bytes()
        self.assertNotEqual(0, self.tool("install-hooks.py", "--remove").returncode)
        self.assertEqual(changed, hook.read_bytes())

    def test_codex_hook_command_resolves_from_a_subdirectory(self):
        configuration = json.loads((SCRIPTS.parent / ".codex/hooks.json").read_text())
        hook = configuration["hooks"]["PreToolUse"][0]["hooks"][0]
        command = hook["commandWindows"] if os.name == "nt" else hook["command"]
        event = {"tool_name": "apply_patch", "tool_input": {"command": "*** Begin Patch\n*** Update File: frontend/src/probe.py\n@@\n-x\n+y\n*** End Patch"}}
        result = subprocess.run(command, cwd=self.root / "frontend/src", input=json.dumps(event), shell=True, capture_output=True, text=True)
        self.assertIn('"deny"', result.stdout, result.stderr)

    def test_refactor_needs_before_and_after_success(self):
        self.cycle.update(kind="refactor", reason="synthetic equivalent expression")
        self.save_plan()
        self.assertIn('"deny"', self.edit_check().stdout)
        self.write("frontend/src/probe.py", "def answer():\n    return 1\n")
        self.assertEqual(0, self.run_phase("before").returncode)
        self.assertEqual("", self.edit_check().stdout)
        self.write("frontend/src/probe.py", "def answer():\n    return 1 + 0\n")
        self.assertEqual(0, self.run_phase("verify").returncode)
        self.assertIn('"deny"', self.edit_check().stdout)

    def test_environment_exception_needs_an_actual_verification(self):
        self.cycle.update(kind="environment", reason="synthetic JSON setup", targets=["package.json"], tests=[], adapter="command",
                          command=[sys.executable, "-c", "import json; json.load(open('package.json'))"])
        self.save_plan()
        self.write("package.json", "{}\n")
        self.git("add", "package.json", TASK)
        self.assertNotEqual(0, self.tool("tdd-check.py", "--candidate", "index", "--task", TASK).returncode)
        self.assertEqual(0, self.run_phase("verify").returncode)
        self.assertEqual(0, self.tool("tdd-check.py", "--candidate", "index", "--task", TASK).returncode)

    def test_environment_exception_cannot_hide_runtime_behavior(self):
        self.cycle.update(kind="environment", reason="incorrectly classified runtime change", adapter="command", command=[sys.executable, "-c", "pass"])
        self.save_plan()
        self.assertNotEqual(0, self.run_phase("verify").returncode)

    def test_setup_error_is_not_a_red_assertion(self):
        self.write("tests/test_probe.py", "import unittest\nclass ProbeTests(unittest.TestCase):\n    def test_answer(self):\n        raise RuntimeError('synthetic setup failure')\n")
        self.assertNotEqual(0, self.run_phase("red").returncode)

    def test_read_only_checker_does_not_create_python_bytecode(self):
        env = dict(os.environ)
        env.pop("PYTHONDONTWRITEBYTECODE", None)
        env.pop("PYTHONPYCACHEPREFIX", None)
        event = {"tool_name": "apply_patch", "tool_input": {"command": "*** Begin Patch\n*** Update File: frontend/src/probe.py\n@@\n-x\n+y\n*** End Patch"}}
        result = subprocess.run([sys.executable, str(self.root / "scripts/tdd-check.py"), "--hook", "--task", TASK], cwd=self.root, input=json.dumps(event), env=env, capture_output=True, text=True)
        self.assertIn('"deny"', result.stdout)
        self.assertFalse((self.root / "scripts/__pycache__").exists())


if __name__ == "__main__":
    unittest.main()
