"""Select Java checks for exact Git candidate inputs and verify independent approvals."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from harness_inventory import Candidate
from java_guard import Authorization, POLICY, Violation, git_commit, parse_json, source_kind


HTTP = "docs/details/development/java-http-api.json"
INPUT_APPROVALS = "docs/details/development/java-ci-approvals.json"
INITIAL_SOURCE = "work/records/harness/issue-106/artifacts/task-003-initial-http-approval.json"
RULES = "docs/details/development/Java 작성과 관리.md"
WORKFLOW = ".github/workflows/java-contract.yml"
SETTINGS = {
    INPUT_APPROVALS, INITIAL_SOURCE, RULES, WORKFLOW,
    "scripts/check-java-submission.py", "scripts/check-java.py", "scripts/java_guard.py",
    "scripts/harness_inventory.py", "scripts/tdd_core.py",
    "backend/build.gradle", "backend/settings.gradle", "backend/gradle.properties",
    "backend/gradle/wrapper/gradle-wrapper.properties",
}
SCOPES = (
    "backend", "db/migration", "docs/details/development", "scripts/check-java-submission.py",
    "scripts/check-java.py", "scripts/java_guard.py", "scripts/harness_inventory.py",
    "scripts/tdd_core.py", "scripts/java-contract", WORKFLOW, INITIAL_SOURCE,
)


def is_setting(path):
    return path in SETTINGS or path.startswith("scripts/java-contract/") or (
        path.startswith(("backend/src/main/resources/", "backend/src/test/resources/"))
        and Path(path).suffix in {".yaml", ".yml", ".properties"}
    )


def select(base, candidate):
    changed = candidate.git("diff", "--name-only", "-z", "--no-renames", base, candidate.commit, "--", *SCOPES)
    paths = sorted(set(changed.decode("utf-8").split("\0")) - {""})
    settings = [path for path in paths if is_setting(path)]
    java = any(source_kind(path) for path in paths)
    inputs = POLICY in paths or HTTP in paths or bool(settings)
    database = any(path.startswith("db/migration/") for path in paths)
    return {
        "paths": paths,
        "settings": settings,
        "approval": java or inputs,
        "module": java or inputs,
        "http": java or inputs or database,
        "backend": bool(candidate.git("ls-tree", "--name-only", candidate.commit, "--", "backend")),
    }


def read_document(view, name, required=True):
    raw = view.read(name)
    if raw is None and not required:
        return None
    if raw is None:
        raise ValueError(f"Required Git input is missing: {name}")
    return parse_json(raw)


def endpoint(value):
    method, path = value["method"], value["path"]
    if not isinstance(method, str) or not re.fullmatch(r"[A-Z][A-Z0-9_-]*", method):
        raise ValueError("Invalid explicit HTTP method")
    if not isinstance(path, str) or not path.startswith("/") or any(ord(ch) < 32 for ch in path):
        raise ValueError("Invalid registered HTTP path")
    return method, path


def http_inventory(view, required=True):
    data = read_document(view, HTTP, required)
    if data is None:
        return None
    if data["version"] != 1 or not isinstance(data["entries"], list) or not data["initialApproval"]:
        raise ValueError("Invalid public HTTP inventory format")
    rows = {}
    for item in data["entries"]:
        pair = endpoint(item)
        if pair in rows or not isinstance(item["approval"], str) or not item["approval"]:
            raise ValueError(f"Duplicate or unapproved inventory entry: {pair}")
        rows[pair] = item["approval"]
    return data["initialApproval"], rows


def matches(authorization, approval_id, predicate, label):
    def covered(record):
        return record["id"] == approval_id and record["kind"] == "http" and predicate(record["scope"])

    authorization.approval(covered, label)


def verify_inventory(previous, candidate, authorization):
    before = http_inventory(previous, required=False)
    initial_id, after = http_inventory(candidate)
    if before is None:
        matches(authorization, initial_id, lambda scope: (
            "initialHttp" in scope and {endpoint(item) for item in scope["initialHttp"]} == set(after)
        ), "Initial public HTTP inventory")
        if any(key != initial_id for key in after.values()):
            raise Violation("Initial HTTP entries must cite the initial approval")
        return
    old_initial, old_entries = before
    if old_initial != initial_id:
        raise Violation("Initial HTTP approval identity cannot be replaced")
    matches(authorization, initial_id, lambda scope: "initialHttp" in scope, "Initial public HTTP approval")
    if any(after[item] != old_entries[item] for item in after.keys() & old_entries.keys()):
        raise Violation("An existing HTTP mapping's approval identity changed")
    records = authorization.data.get("changeApprovals", [])
    for op, changed in (("add", after.keys() - old_entries.keys()), ("remove", old_entries.keys() - after.keys())):
        for method, path in sorted(changed):
            affected = {"op": op, "method": method, "path": path}
            approved_ids = [item["approval"] for item in records if all(item.get(k) == v for k, v in affected.items())]
            if len(approved_ids) != 1 or (op == "add" and after[method, path] != approved_ids[0]):
                if authorization.data.get("approvalsComplete") is True:
                    raise Violation(f"No exact HTTP {op} approval: {method} {path}")
                raise ValueError(f"HTTP {op} approval unconfirmed: {method} {path}")
            matches(authorization, approved_ids[0], lambda scope: affected in scope["http"],
                    f"Public HTTP {op}: {method} {path}")


def fingerprint(data):
    return None if data is None else hashlib.sha256(data).hexdigest()


def verify_settings(previous, candidate, settings, authorization):
    for path in settings:
        delta = {"path": path, "before": fingerprint(previous.read(path)), "after": fingerprint(candidate.read(path))}
        if delta not in authorization.data.get("inputChanges", []):
            if authorization.data.get("approvalsComplete") is True:
                raise Violation(f"Unapproved Java checker input change: {path}")
            raise ValueError(f"Java checker input approval unconfirmed: {path}")


def context_data(previous, candidate, trusted_path):
    """Only a caller outside the checkout or a record from the actual base can supply approvals."""
    trusted = Authorization(candidate, previous.commit, candidate.commit, trusted_path)
    data = dict(trusted.data)
    approvals = dict(data.get("approvals", {}))
    initial = read_document(previous, INITIAL_SOURCE, required=False)
    if initial is not None:
        source = {**initial["source"], "ref": previous.commit}
        trusted.source(source)
        approved = {**initial, "source": source}
        approvals[approved["id"]] = {"status": "verified", "record": approved}
    accepted = read_document(previous, INPUT_APPROVALS, required=False)
    if accepted is not None:
        if accepted["version"] != 1:
            raise ValueError("Unsupported base Java approval catalog")
        reference = {**accepted["source"], "ref": previous.commit}
        trusted.source(reference)
        if not accepted.get("bootstrap") or previous.read(WORKFLOW) is None:
            data["inputChanges"] = [*data.get("inputChanges", []), *accepted.get("inputChanges", [])]
        for record in accepted.get("approvals", []):
            record = {**record, "source": {**record["source"], "ref": previous.commit}}
            trusted.source(record["source"])
            if record["id"] in approvals:
                raise ValueError("Duplicate independently approved Java record")
            status = "unconfirmed" if record["kind"] == "exception" else "verified"
            approvals[record["id"]] = {"status": status, "record": record}
        data.setdefault("changeApprovals", accepted.get("changeApprovals", []))
        approved_scope = accepted.get("taskScope")
        if approved_scope is not None and "taskScope" not in data:
            source = {**approved_scope["source"], "ref": previous.commit}
            trusted.source(source)
            data["taskScope"] = {**approved_scope, "status": "verified", "source": source}
        data.setdefault("approvalsComplete", accepted.get("approvalsComplete", False))
    return {**data, "candidateId": candidate.commit, "baseRevision": previous.commit, "approvals": approvals}


def verify(args, previous, candidate, plan):
    if not plan["approval"]:
        return {"status": "not-applicable", "reason": "No Java or approval input changes"}
    with tempfile.TemporaryDirectory(prefix="lumia-java-approval-") as directory:
        context = Path(directory) / "approval.json"
        data = context_data(previous, candidate, args.approval_context)
        context.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        authorization = Authorization(candidate, previous.commit, candidate.commit, str(context))
        verify_settings(previous, candidate, plan["settings"], authorization)
        if plan["http"]:
            verify_inventory(previous, candidate, authorization)
        checker = Path(__file__).with_name("check-java.py")
        result = subprocess.run([sys.executable, "-B", "-X", "utf8", str(checker),
                                 "--base", previous.commit, "--candidate", candidate.commit, "--approval-only",
                                 "--approval-context", str(context)], check=False, text=True, encoding="utf-8",
                                capture_output=True, timeout=40)
        if result.returncode not in (0, 1, 2) or not result.stdout:
            raise ValueError("Java placement approval result could not be read")
        payload = json.loads(result.stdout)
        if result.returncode == 1:
            raise Violation(payload["reason"])
        if result.returncode == 2:
            raise ValueError(payload["reason"])
    return {"status": "pass", "reason": "Independent approval inputs match the submission"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--approval-context")
    parser.add_argument("--select-only", action="store_true")
    args = parser.parse_args()
    plan = {}
    try:
        candidate = Candidate(args.candidate, seconds=40)
        base = git_commit(candidate, args.base)
        if candidate.commit != args.candidate or base != args.base:
            raise ValueError("Both revisions must name exact Git commits")
        if candidate.git("merge-base", base, candidate.commit).decode().strip() != base:
            raise ValueError("The approved base is not an ancestor of the effective candidate")
        previous = Candidate(base, seconds=40)
        plan = select(base, candidate)
        result = {"status": "selected", "reason": None} if args.select_only else verify(args, previous, candidate, plan)
    except Violation as error:
        result = {"status": "violation", "reason": str(error)}
    except (ValueError, KeyError, TypeError, AttributeError, OSError, subprocess.SubprocessError) as error:
        result = {"status": "unconfirmed", "reason": str(error)}
    print(json.dumps({**result, "base": args.base, "candidate": args.candidate, "checks": plan}, ensure_ascii=False))
    return {"violation": 1, "unconfirmed": 2}.get(result["status"], 0)


if __name__ == "__main__":
    raise SystemExit(main())
