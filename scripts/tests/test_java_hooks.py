import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[2]
CHECKER = PROJECT / "scripts/check-java.py"
POLICY = "docs/details/development/java-policy.json"
BASE_PACKAGE = "io.github.minokim.lumiawiki"
PACKAGE_PATH = BASE_PACKAGE.replace(".", "/")
TEST = f"backend/src/test/java/{PACKAGE_PATH}/dev/ProbeTests.java"
PRODUCTION = f"backend/src/main/java/{PACKAGE_PATH}/dev/Probe.java"
TASK = "work/records/harness/issue-106/task-002.md"
ARTIFACT = "work/records/harness/issue-106/artifacts/task-002"


class JavaHooksTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="lumia-java-hook-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name) / "repo"
        self.root.mkdir()
        self.context = Path(directory.name) / "approved.json"
        self.write(POLICY, (PROJECT / POLICY).read_text(encoding="utf-8"))
        self.write(".gitignore", ".tmp/\n")
        self.write(TASK, "# Fixture\n<a id=\"scope\"></a>\n")
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Java hook fixture")
        self.git("config", "core.autocrlf", "false")
        self.git("add", "--", ".gitignore", POLICY, TASK)
        self.git("commit", "-qm", "Fixture baseline")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()
        self.env = os.environ.copy()
        self.env.pop("LUMIA_JAVA_APPROVAL_CONTEXT", None)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")

    def java(self, name=TEST, package=BASE_PACKAGE + ".dev", body=""):
        self.write(name, f"package {package};\nclass {Path(name).stem} {{ {body} }}\n")

    def git(self, *arguments, check=True, env=None):
        return subprocess.run(["git", *arguments], cwd=self.root, env=env,
                              text=True, encoding="utf-8", capture_output=True, check=check, timeout=30)

    def run_python(self, script, *args, event=None, env=None):
        return subprocess.run([sys.executable, "-B", "-X", "utf8", str(script), *args], cwd=self.root,
                              input=json.dumps(event) if event else None, text=True, encoding="utf-8",
                              capture_output=True, env=env or self.env, timeout=30)

    def check_candidate(self, *args, expected, tdd=False):
        flags = [] if tdd else ["--approval-only"]
        result = self.run_python(CHECKER, *flags, *args)
        self.assertEqual(expected, json.loads(result.stdout)["status"], result.stdout + result.stderr)
        self.assertEqual({"pass": 0, "not-applicable": 0, "violation": 1, "unconfirmed": 2}[expected],
                         result.returncode, result.stdout)
        return result

    def describe(self, *args, event=None):
        result = self.run_python(CHECKER, "--identify", *args, event=event)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def verify_scope(self, identity=None, approvals=None, **extra):
        identity = identity or self.describe()
        source = {"ref": self.base, "path": TASK, "anchor": "scope"}
        data = {
            "candidateId": identity["candidateId"], "baseRevision": identity["baseRevision"],
            "taskScope": {"status": "verified", "source": source,
                          "changes": [dict(change, scope="fixture") for change in identity["changes"]]},
            "approvals": approvals or {}, "approvalsComplete": True, **extra,
        }
        self.context.write_text(json.dumps(data), encoding="utf-8")
        return ("--approval-context", str(self.context))

    def event(self, path, kind):
        return {"cwd": str(self.root), "tool_name": "apply_patch", "tool_input": {
            "command": f"*** Begin Patch\n*** {kind} File: {path}\n*** End Patch",
        }}

    def test_no_backend_candidate_ignores_untracked_source(self):
        self.java()
        self.check_candidate(expected="not-applicable")

    def test_staged_java_not_worktree_controls_both_directions(self):
        self.java()
        self.git("add", "--", TEST)
        scope = self.verify_scope()
        self.java(package="different")
        self.check_candidate(*scope, expected="pass")
        self.git("add", "--", TEST)
        self.java()
        scope = self.verify_scope()
        self.check_candidate(*scope, expected="violation")

    def test_java_unicode_before_placement_tokenization(self):
        self.write(TEST, r"p\u0061ckage io.github.minokim.lumiawiki.dev;" + "\n" +
                   r'class ProbeTests { String value = "\uAC00=\\u005a"; }')
        self.git("add", "--", TEST)
        self.check_candidate(*self.verify_scope(), expected="pass")

    def test_explicit_candidate_rejects_checked_out_or_unbound_scope(self):
        self.java()
        self.git("add", "--", TEST)
        self.git("commit", "-qm", "Fixture test")
        candidate = self.git("rev-parse", "HEAD").stdout.strip()
        args = ("--candidate", candidate, "--base", self.base)
        self.java(package="different")
        scope = self.verify_scope(self.describe(*args))
        self.check_candidate(*args, *scope, expected="pass")
        self.check_candidate(*args, expected="unconfirmed")

    def test_last_production_java_deletion_still_requires_tdd(self):
        self.java(PRODUCTION)
        self.git("add", "--", PRODUCTION)
        self.git("commit", "-qm", "Production fixture")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("rm", "--", PRODUCTION)
        scope = self.verify_scope()
        result = self.check_candidate(*scope, expected="unconfirmed", tdd=True)
        self.assertIn("No active Task", result.stdout)

    def test_package_info_cannot_hide_production_changes(self):
        path = str(Path(PRODUCTION).with_name("package-info.java")).replace("\\", "/")
        header = f"package {BASE_PACKAGE}.dev;\n"
        self.write(path, header)
        self.git("add", "--", path)
        scope = self.verify_scope()
        self.check_candidate(*scope, expected="unconfirmed", tdd=True)
        self.git("commit", "-qm", "Initial package descriptor")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()
        before = self.run_python(CHECKER, "--mode", "before-edit", "--hook",
                                 event=self.event(path, "Update"))
        self.assertEqual("deny", json.loads(before.stdout)["hookSpecificOutput"]["permissionDecision"])
        self.write(path, header + "class Hidden {}\n")
        self.git("add", "--", path)
        self.check_candidate(*self.verify_scope(), expected="violation", tdd=True)

    def test_approval_with_exact_delegation_and_no_self_approval(self):
        data = json.loads((self.root / POLICY).read_text(encoding="utf-8"))
        data["java"]["modules"]["items"] = {"owner": "Items", "responsibility": "Fixtures",
                                          "publicTypes": [], "extraPackages": {"production": [], "test": []}}
        self.write(POLICY, json.dumps(data))
        self.git("add", "--", POLICY)
        self.git("commit", "-qm", "Approved module baseline")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()
        data["java"]["modules"]["items"]["extraPackages"]["test"].append("application.dto")
        self.write(POLICY, json.dumps(data))
        target = f"backend/src/test/java/{PACKAGE_PATH}/items/application/dto/ProbeTests.java"
        self.java(target, BASE_PACKAGE + ".items.application.dto")
        self.git("add", "--", POLICY, target)
        described = self.describe()
        record = {
            "id": "delegate", "kind": "delegation", "reason": "Test scope", "limits": "Package only",
            "approver": {"id": "owner", "authority": "task delegation"},
            "source": {"ref": self.base, "path": TASK, "anchor": "scope"},
            "scope": {"policy": described["policyChanges"], "packages": [{
                "source": "test", "package": BASE_PACKAGE + ".items.application.dto",
                "owner": "Items", "visibility": "internal", "operations": ["create"],
            }]},
        }
        self.check_candidate(*self.verify_scope(), expected="violation")
        self.check_candidate(*self.verify_scope(approvalsComplete=False), expected="unconfirmed")
        approval = {"delegate": {"status": "verified", "record": record}}
        self.check_candidate(*self.verify_scope(approvals=approval), expected="pass")
        self.git("commit", "-qm", "Candidate cannot supply its own approval")
        candidate = self.git("rev-parse", "HEAD").stdout.strip()
        args = ("--candidate", candidate, "--base", self.base)
        record["source"]["ref"] = candidate
        scope = self.verify_scope(self.describe(*args), approvals=approval)
        self.check_candidate(*args, *scope, expected="violation")

    def test_expired_exception_and_unreadable_reference(self):
        path = f"backend/src/test/java/{PACKAGE_PATH}/temporary/ProbeTests.java"
        self.java(path, BASE_PACKAGE + ".temporary")
        self.git("add", "--", path)
        record = {"kind": "exception", "scope": {"packages": [
            {"source": "test", "package": BASE_PACKAGE + ".temporary", "operations": ["create"]},
        ]}}
        scope = self.verify_scope(approvals={"exception": {"status": "expired", "record": record}})
        self.check_candidate(*scope, expected="violation")
        scope = self.verify_scope(approvals={"exception": {"status": "unconfirmed", "record": record}})
        self.check_candidate(*scope, expected="unconfirmed")

    def test_hook_protocol_for_missing_red_and_placement_notice(self):
        unrelated = self.run_python(CHECKER, "--mode", "before-edit", "--hook",
                                    event=self.event(".tmp/notes.md", "Add"))
        self.assertEqual("", unrelated.stdout, unrelated.stderr)
        before = self.run_python(CHECKER, "--mode", "before-edit", "--hook",
                                 event=self.event(PRODUCTION, "Update"))
        self.assertEqual(0, before.returncode, before.stderr)
        self.assertEqual("deny", json.loads(before.stdout)["hookSpecificOutput"]["permissionDecision"])
        self.java(package="different")
        after = self.run_python(CHECKER, "--mode", "after-edit", "--hook", event=self.event(TEST, "Add"))
        self.assertEqual(0, after.returncode, after.stderr)
        self.assertIn("Java violation", json.loads(after.stdout)["systemMessage"])
        self.java()
        correct = self.run_python(CHECKER, "--mode", "after-edit", "--hook", event=self.event(TEST, "Add"))
        self.assertEqual("", correct.stdout, correct.stderr)

    def test_real_tdd_runner_linked_artifacts_and_closed_cycle(self):
        self.java(PRODUCTION, body="int result() { return 0; }")
        self.write(TASK, "# Fixture\n<a id=\"scope\"></a>\n"
                   "[Plan](artifacts/task-002-tdd-plan.json)\n[Evidence](artifacts/task-002-tdd-evidence.json)\n")
        self.write("probe.py", """import pathlib, sys, unittest
from xml.etree.ElementTree import Element, SubElement, ElementTree
class Probe(unittest.TestCase):
    def test_result(self):
        if pathlib.Path('omit-required').exists():
            self.skipTest('fixture omits the original test')
        self.assertIn('return 1;', pathlib.Path(sys.argv[1]).read_text())
    def test_other(self):
        self.assertTrue(True)
result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(Probe))
suite = Element('testsuite')
case = SubElement(suite, 'testcase', classname='Probe', name='test_result')
SubElement(suite, 'testcase', classname='Probe', name='test_other')
if result.failures:
    SubElement(case, 'failure', type='AssertionError').text = result.failures[0][1]
elif result.skipped:
    SubElement(case, 'skipped')
ElementTree(suite).write(sys.argv[2])
sys.exit(not result.wasSuccessful())
""")
        cycle = {"id": "probe", "kind": "behavior", "targets": [PRODUCTION], "tests": ["probe.py"],
                 "adapter": "junit", "expectedFailures": ["Probe.test_result"],
                 "command": [sys.executable, "probe.py", PRODUCTION, "{report}"]}
        self.write(ARTIFACT + "-tdd-plan.json", json.dumps({"schema": 1, "cycles": [cycle]}))
        self.git("add", "--", TASK, PRODUCTION, "probe.py", ARTIFACT + "-tdd-plan.json")
        self.git("commit", "-qm", "TDD fixture")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()
        runner = PROJECT / "scripts/tdd-run.py"
        args = ("--task", TASK, "--cycle", "probe")
        red = self.run_python(runner, *args, "--phase", "red")
        self.assertEqual(0, red.returncode, red.stdout + red.stderr)
        event = self.event(PRODUCTION, "Update")
        before = self.run_python(CHECKER, "--mode", "before-edit", "--hook", "--task", TASK, event=event)
        self.assertEqual("", before.stdout, before.stderr)
        self.java(PRODUCTION, body="int result() { return 1; }")
        self.write("omit-required", "")
        skipped = self.run_python(runner, *args, "--phase", "green")
        self.assertNotEqual(0, skipped.returncode)
        self.assertIn("same executed tests: Probe.test_result", skipped.stderr)
        (self.root / "omit-required").unlink()
        green = self.run_python(runner, *args, "--phase", "green", "--export")
        self.assertEqual(0, green.returncode, green.stdout + green.stderr)
        after = self.run_python(CHECKER, "--mode", "before-edit", "--hook", "--task", TASK, event=event)
        self.assertIn('"deny"', after.stdout)
        self.git("add", "--", PRODUCTION, ARTIFACT + "-tdd-evidence.json")
        scope = self.verify_scope()
        self.check_candidate(*scope, "--task", TASK, expected="pass", tdd=True)
        self.assertNotIn("tdd-evidence -->", (self.root / TASK).read_text())

        receipt_path = self.root / (ARTIFACT + "-tdd-evidence.json")
        original_receipt = receipt_path.read_bytes()
        state_file, = self.root.glob(".tmp/issue-106/task-002/tdd/*/state.json")
        original_state = state_file.read_bytes()
        state_file.unlink()
        for defect in ("successful-red", "unexecuted-green", "changed-test-input"):
            with self.subTest(defect=defect):
                stored = json.loads(original_receipt)
                receipt = stored["receipts"][0]
                if defect == "successful-red":
                    receipt["red"].update(exitCode=0, ok=True, result=receipt["final"]["result"])
                elif defect == "unexecuted-green":
                    receipt["final"]["result"]["tests"] = 0
                else:
                    receipt["red"]["manifest"]["probe.py"] = "unrelated"
                receipt_path.write_text(json.dumps(stored), encoding="utf-8")
                self.git("add", "--", ARTIFACT + "-tdd-evidence.json")
                self.check_candidate(*self.verify_scope(), "--task", TASK, expected="unconfirmed", tdd=True)
        receipt_path.write_bytes(original_receipt)
        state_file.write_bytes(original_state)
        self.git("add", "--", ARTIFACT + "-tdd-evidence.json")

        refactor = {**cycle, "id": "no-behavior-change", "kind": "refactor",
                    "reason": "Keeps the established return value"}
        self.write(ARTIFACT + "-tdd-plan.json", json.dumps({"schema": 1, "cycles": [cycle, refactor]}))
        baseline = self.run_python(runner, "--task", TASK, "--cycle", refactor["id"], "--phase", "before")
        self.assertEqual(0, baseline.returncode, baseline.stdout + baseline.stderr)
        unapproved = self.run_python(CHECKER, "--mode", "before-edit", "--hook", "--task", TASK, event=event)
        self.assertIn('"deny"', unapproved.stdout)
        identity = self.describe("--mode", "before-edit", event=event)
        self.verify_scope(identity)
        approved = json.loads(self.context.read_text(encoding="utf-8"))
        approved["taskScope"]["changes"][0]["tddExceptions"] = [refactor["id"]]
        self.context.write_text(json.dumps(approved), encoding="utf-8")
        allowed = self.run_python(CHECKER, "--mode", "before-edit", "--hook", "--task", TASK,
                                  "--approval-context", str(self.context), event=event)
        self.assertEqual("", allowed.stdout, allowed.stderr)

        self.java(PRODUCTION, body="int result() { /* refactored */ return 1; }")
        self.write("omit-required", "")
        skipped = self.run_python(runner, "--task", TASK, "--cycle", refactor["id"], "--phase", "verify")
        self.assertNotEqual(0, skipped.returncode)
        self.assertIn("same executed tests: Probe.test_result", skipped.stderr)
        (self.root / "omit-required").unlink()

        for label, targets, settings in (
            ("setting-only", ["notes.txt"], [PRODUCTION]),
            ("unchanged-target", ["notes.txt", PRODUCTION], []),
        ):
            with self.subTest(label=label):
                unrelated = {**refactor, "id": label, "targets": targets, "settings": settings}
                plan_path = ARTIFACT + "-tdd-plan.json"
                self.write(plan_path, json.dumps({"schema": 1, "cycles": [unrelated]}))
                self.write("notes.txt", "before")
                run_args = ("--task", TASK, "--cycle", label)
                before = self.run_python(runner, *run_args, "--phase", "before")
                self.assertEqual(0, before.returncode, before.stderr)
                self.write("notes.txt", "after")
                after = self.run_python(runner, *run_args, "--phase", "verify", "--export")
                self.assertEqual(0, after.returncode, after.stderr)
                self.git("add", "--", PRODUCTION, plan_path, "notes.txt", ARTIFACT + "-tdd-evidence.json")
                scope = self.verify_scope()
                approved = json.loads(self.context.read_text(encoding="utf-8"))
                approved["taskScope"]["changes"][0]["tddExceptions"] = [label]
                self.context.write_text(json.dumps(approved), encoding="utf-8")
                self.check_candidate(*scope, "--task", TASK, expected="unconfirmed", tdd=True)

    def test_actual_git_pre_commit_propagates_java_decision_after_existing_hook(self):
        for path in ("check-java.py", "java_guard.py", "harness_inventory.py", "tdd_core.py"):
            self.write(f"scripts/{path}", (PROJECT / "scripts" / path).read_text(encoding="utf-8"))
        for stub in ("check-harness-inventory.py", "check-work-records.py", "check-rule-comments.py"):
            self.write(f"scripts/{stub}", "pass\n")
        self.git("add", "--", "scripts")
        self.git("commit", "-qm", "Isolated hook fixture")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()
        hooks = self.root / ".git/hooks"
        shutil.copyfile(PROJECT / "scripts/hooks/pre-commit", hooks / "pre-commit")
        (hooks / "pre-commit").chmod(0o755)
        previous = hooks / "pre-commit.harness-original"
        previous.write_bytes(b"#!/bin/sh\necho existing-hook-ran\n")
        previous.chmod(0o755)
        self.java(package="different")
        self.git("add", "--", TEST)
        self.verify_scope()
        env = {**self.env, "LUMIA_JAVA_APPROVAL_CONTEXT": str(self.context)}
        rejected = self.git("commit", "-m", "Reject placement", env=env, check=False)
        self.assertNotEqual(0, rejected.returncode)
        self.assertIn("existing-hook-ran", rejected.stderr)
        self.assertIn('"status": "violation"', rejected.stderr)
        self.java()
        self.git("add", "--", TEST)
        self.verify_scope()
        accepted = self.git("commit", "-m", "Accept placement", env=env)
        self.assertIn('"status": "pass"', accepted.stderr)


if __name__ == "__main__":
    unittest.main()
