import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[2]
CHECK = PROJECT / "scripts/check-java-submission.py"
POLICY = "docs/details/development/java-policy.json"
HTTP = "docs/details/development/java-http-api.json"
APPROVALS = "docs/details/development/java-ci-approvals.json"
SETTINGS = ".github/workflows/java-contract.yml"
INITIAL = "work/records/harness/issue-106/artifacts/task-003-initial-http-approval.json"
ISSUE = "work/records/harness/issue-106/issue.md"
ID = "http-106-003-initial"
ANCHOR = "initial-http-approval"


class JavaSubmissionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="lumia-java-submission-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "repo"
        self.root.mkdir()
        self.context = Path(temporary.name) / "approvals.json"
        self.git("init", "-q")
        self.git("config", "user.name", "Contract fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.write(POLICY, (PROJECT / POLICY).read_text(encoding="utf-8"))
        self.write(ISSUE, f'<a id="{ANCHOR}"></a>\n')

    def git(self, *args):
        result = subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True, timeout=20)
        return result.stdout.decode("utf-8").strip()

    def write(self, path, data):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8", newline="\n")

    def commit(self):
        self.git("add", "--", "docs", "work")
        for folder in (".github", "scripts", "db"):
            if (self.root / folder).is_dir():
                self.git("add", "--", folder)
        self.git("commit", "-qm", "Fixture")
        return self.git("rev-parse", "HEAD")

    def approved(self, approved_id=ID, **scope):
        return {
            "version": 1,
            "id": approved_id,
            "kind": "http",
            "source": {"path": ISSUE, "anchor": ANCHOR},
            "approver": {"id": "fixture-project-owner", "authority": "Fixture approval authority"},
            "reason": "Independently approved fixture HTTP scope",
            "limits": "Only the stated method and path changes",
            "scope": {"http": [], **scope},
        }

    def base_with_inventory(self, entries=()):
        self.write(INITIAL, self.approved(initialHttp=[
            {"method": row["method"], "path": row["path"]} for row in entries
        ]))
        self.write(HTTP, {"version": 1, "initialApproval": ID, "entries": list(entries)})
        return self.commit()

    def check(self, base, head, *flags, status):
        result = subprocess.run([sys.executable, "-B", "-X", "utf8", str(CHECK), "--base", base, "--candidate", head,
                                 *flags], cwd=self.root, text=True, encoding="utf-8", capture_output=True, timeout=45)
        self.assertIn(result.returncode, [0, 1, 2], result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(status, data["status"], result.stdout + result.stderr)
        return data

    def test_approved_empty_initial_inventory_uses_base_without_backend(self):
        self.write(INITIAL, self.approved(initialHttp=[]))
        base = self.commit()
        self.write(HTTP, {"version": 1, "initialApproval": ID, "entries": []})
        head = self.commit()
        report = self.check(base, head, status="pass")
        self.assertFalse(report["checks"]["backend"])
        self.assertTrue(report["checks"]["http"])

    def test_candidate_cannot_approve_itself(self):
        base = self.commit()
        self.write(INITIAL, self.approved(initialHttp=[]))
        self.write(HTTP, {"version": 1, "initialApproval": ID, "entries": []})
        head = self.commit()
        accepted_changes = [{"path": INITIAL, "before": None, "after": self.digest(INITIAL)}]
        self.context.write_text(json.dumps({
            "baseRevision": base, "candidateId": head, "inputChanges": accepted_changes,
            "approvalsComplete": True,
        }), encoding="utf-8")
        report = self.check(base, head, "--approval-context", str(self.context), status="violation")
        self.assertIn("Initial public HTTP inventory", report["reason"])

    def test_only_each_policy_inventory_exception_and_settings_input_enables_checks(self):
        base = self.base_with_inventory()
        for name in ("policy", "inventory", "exception", "settings"):
            with self.subTest(name=name):
                self.git("switch", "--detach", base)
                old_bytes = (self.root / HTTP).read_text(encoding="utf-8")
                if name == "policy":
                    path = POLICY
                    payload = json.loads((self.root / POLICY).read_text(encoding="utf-8"))
                    payload["http"]["developmentProfiles"].append("preview")
                elif name == "inventory":
                    path = HTTP
                    payload = json.loads(old_bytes)
                    payload["entries"] = [{"method": "GET", "path": "/new", "approval": "unapproved"}]
                elif name == "exception":
                    path = APPROVALS
                    payload = {"version": 1, "exceptions": []}
                else:
                    path, payload = SETTINGS, "name: Settings only\n"
                self.write(path, payload)
                head = self.commit()
                checks = self.check(base, head, "--select-only", status="selected")["checks"]
                self.assertEqual([path], checks["paths"])
                self.assertTrue(all(checks[name] for name in ("approval", "module", "http")))
                report = self.check(base, head, status="unconfirmed")
                self.assertNotEqual("", report["reason"])

    def test_input_change_requires_an_exact_digest_from_actual_base(self):
        self.write(INITIAL, self.approved(initialHttp=[]))
        self.write(HTTP, {"version": 1, "initialApproval": ID, "entries": []})
        actual_workflow = "name: Scoped verification\n"
        self.write(APPROVALS, {
            "version": 1, "source": {"path": ISSUE, "anchor": ANCHOR}, "approvalsComplete": True,
            "inputChanges": [{"path": SETTINGS, "before": None,
                              "after": hashlib.sha256(actual_workflow.encode()).hexdigest()}],
        })
        base = self.commit()
        self.write(SETTINGS, actual_workflow)
        head = self.commit()
        self.check(base, head, status="pass")
        self.write(SETTINGS, "name: Unapproved settings\n")
        bad = self.commit()
        report = self.check(base, bad, status="violation")
        self.assertIn(SETTINGS, report["reason"])

    def test_checker_dependencies_and_runtime_migrations_are_material_inputs(self):
        base = self.base_with_inventory()
        for path in (
            "scripts/check-java.py", "scripts/java_guard.py", "scripts/harness_inventory.py",
            "scripts/tdd_core.py", "scripts/java-contract/src/main/java/lumia/contract/ModuleCheck.java",
            "db/migration/V1__probe.sql",
        ):
            with self.subTest(path=path):
                self.git("switch", "--detach", base)
                self.write(path, "changed\n")
                head = self.commit()
                checks = self.check(base, head, "--select-only", status="selected")["checks"]
                self.assertEqual([path], checks["paths"])
                self.assertTrue(checks["http"])
                if path.startswith("scripts/"):
                    self.assertTrue(checks["approval"] and checks["module"])
                    self.check(base, head, status="unconfirmed")

    def test_bootstrap_requires_complete_first_installation_and_is_not_reusable(self):
        self.write(INITIAL, self.approved(initialHttp=[]))
        self.write(HTTP, {"version": 1, "initialApproval": ID, "entries": []})
        build = "scripts/java-contract/build.gradle"
        sources = {SETTINGS: "name: First installation\n", build: "plugins {}\n"}
        self.write(APPROVALS, {
            "version": 1, "bootstrap": True, "source": {"path": ISSUE, "anchor": ANCHOR},
            "inputChanges": [{"path": path, "before": None, "after": hashlib.sha256(value.encode()).hexdigest()}
                             for path, value in sources.items()],
        })
        base = self.commit()
        self.write(build, sources[build])
        self.check(base, self.commit(), status="unconfirmed")
        self.write(SETTINGS, sources[SETTINGS])
        first_installation = self.commit()
        self.check(base, first_installation, status="pass")
        for path in sources:
            (self.root / path).unlink()
        removed = self.commit()
        for path, value in sources.items():
            self.write(path, value)
        reintroduced = self.commit()
        self.check(removed, reintroduced, status="unconfirmed")
        (self.root / ".git/shallow").write_text(removed + "\n", encoding="utf-8", newline="\n")
        result = self.check(removed, reintroduced, status="unconfirmed")
        self.assertIn("Full base history", result["reason"])

    def test_exact_http_method_replacement_requires_both_changes(self):
        base = self.base_with_inventory([{"method": "GET", "path": "/example", "approval": ID}])
        new_id = "change-approved"
        self.write(HTTP, {"version": 1, "initialApproval": ID, "entries": [
            {"method": "POST", "path": "/example", "approval": new_id},
        ]})
        head = self.commit()
        changes = [{"op": op, "method": method, "path": "/example"}
                   for op, method in (("add", "POST"), ("remove", "GET"))]
        approval = self.approved(new_id, http=changes)
        approval["source"]["ref"] = base
        context = {
            "baseRevision": base, "candidateId": head, "approvalsComplete": True,
            "approvals": {new_id: {"status": "verified", "record": approval}},
            "changeApprovals": [{**change, "approval": new_id} for change in changes],
        }
        self.context.write_text(json.dumps(context), encoding="utf-8")
        self.check(base, head, "--approval-context", str(self.context), status="pass")
        context["changeApprovals"].pop()
        self.context.write_text(json.dumps(context), encoding="utf-8")
        report = self.check(base, head, "--approval-context", str(self.context), status="violation")
        self.assertIn("remove approval", report["reason"])

    def digest(self, path):
        return hashlib.sha256((self.root / path).read_bytes()).hexdigest()


if __name__ == "__main__":
    unittest.main()
