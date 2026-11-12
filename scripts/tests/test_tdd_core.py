import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tdd_core as core


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def test_parent_escape_is_rejected(self):
        with self.assertRaises(ValueError):
            core.safe_path(self.root, "../outside")

    def test_windows_absolute_path_is_rejected(self):
        with self.assertRaises(ValueError):
            core.safe_path(self.root, "C:/outside")

    def test_preservation_path_is_rejected_before_reading(self):
        for name in ("harness-design/probe.md", ".harness-state/probe.json"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                core.safe_path(self.root, name)

    def test_secret_path_is_rejected(self):
        with self.assertRaises(ValueError):
            core.safe_path(self.root, ".env")

    def test_git_patterns_and_private_aliases_are_rejected(self):
        for name in ("*", "frontend/src/[ab].ts", ".GIT/config", ".env.local", ".env."):
            with self.subTest(name=name), self.assertRaises(ValueError):
                core.safe_path(self.root, name)

    def test_junctions_and_resolved_preservation_aliases_are_rejected(self):
        junction = self.root / "scripts/junction"
        with patch.object(Path, "is_junction", autospec=True, side_effect=lambda p: p == junction):
            with self.assertRaises(ValueError):
                core.safe_path(self.root, "scripts/junction/probe.py")
        probe = self.root / "scripts/probe.py"
        with patch.object(Path, "resolve", autospec=True, side_effect=lambda p: self.root / "harness-design/probe.py" if p == probe else p):
            with self.assertRaises(ValueError):
                core.safe_path(self.root, "scripts/probe.py")

    def test_runtime_and_tests_have_different_classes(self):
        self.assertEqual("behavior", core.classify("frontend/src/probe.ts"))
        self.assertEqual("test", core.classify("frontend/src/probe.test.ts"))
        self.assertEqual("behavior", core.classify("scripts/tdd_core.py"))
        self.assertEqual("test", core.classify("scripts/tests/test_tdd_core.py"))

    def test_behavior_sql_and_settings_are_not_document_exceptions(self):
        self.assertEqual("behavior", core.classify("db/migration/V2__sample.sql"))
        self.assertEqual("setting", core.classify("backend/build.gradle"))
        self.assertEqual("document", core.classify("work/records/phase-001/issue-42/task-002.md"))
        self.assertEqual("unknown", core.classify("unclassified.bin"))

    def test_patch_add_move_and_delete_paths_are_complete(self):
        patch = "*** Begin Patch\n*** Add File: frontend/src/a.ts\n+x\n*** Update File: frontend/src/b.ts\n*** Move to: frontend/src/c.ts\n@@\n-x\n+y\n*** Delete File: frontend/src/d.ts\n*** End Patch"
        self.assertEqual(["frontend/src/a.ts", "frontend/src/b.ts", "frontend/src/c.ts", "frontend/src/d.ts"], core.patch_paths(patch))

    def test_malformed_patch_is_indeterminate(self):
        with self.assertRaises(ValueError):
            core.patch_paths("not a patch")

    def test_junit_assertion_failure_is_different_from_error(self):
        p = self.root / "junit.xml"
        p.write_text('<testsuites><testsuite><testcase classname="Probe" name="missing"><failure type="AssertionError">expected</failure></testcase><testcase classname="Probe" name="setup"><error type="DockerError"/></testcase><testcase classname="Probe" name="skip"><skipped/></testcase></testsuite></testsuites>', encoding="utf-8")
        result = core.parse_report("junit", p)
        self.assertEqual((3, 1, 1, 1), tuple(result[k] for k in ("tests", "failures", "errors", "skipped")))

    def test_unittest_report_requires_current_run_and_counts(self):
        p = self.root / "python.json"
        p.write_text(json.dumps({"runId": "current", "tests": 1, "failures": 1, "errors": 0, "skipped": 0, "names": ["Probe.test_missing"], "failedNames": ["Probe.test_missing"]}), encoding="utf-8")
        self.assertEqual(1, core.parse_report("unittest", p, "current")["failures"])
        with self.assertRaises(ValueError):
            core.parse_report("unittest", p, "old")

    def test_vitest_runtime_errors_are_not_red(self):
        p = self.root / "vitest.json"
        p.write_text(json.dumps({"numTotalTests": 1, "numFailedTests": 1, "numPassedTests": 0, "numPendingTests": 0, "numRuntimeErrorTestSuites": 1, "testResults": [{"assertionResults": [{"fullName": "probe", "status": "failed", "failureMessages": ["AssertionError: expected"]}]}]}), encoding="utf-8")
        self.assertEqual(1, core.parse_report("vitest", p)["errors"])


if __name__ == "__main__":
    unittest.main()
