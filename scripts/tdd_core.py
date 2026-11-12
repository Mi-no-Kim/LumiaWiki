"""Local TDD evidence helpers. No model, network, or automatic test execution."""

import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import subprocess
import time
import xml.etree.ElementTree as ET

EXCLUDED = ("harness-design", ".harness-state")
PATHSPECS = [".", ":(exclude)harness-design/**", ":(exclude).harness-state/**"]
CONTEXT = [
    ".gitattributes",
    "package.json", "package-lock.json", "frontend/package.json",
    "frontend/package-lock.json", "frontend/vite.config.mjs", "frontend/vitest.config.mjs",
    "frontend/tsconfig.json", "frontend/src/test/setup.ts", "backend/build.gradle",
    "backend/settings.gradle", "backend/gradle/wrapper/gradle-wrapper.properties",
    "backend/src/main/resources/application.yaml", "backend/src/test/resources/application-test.yaml",
    "scripts/test-python.py", "scripts/tdd-run.py", "scripts/tdd-check.py",
    "scripts/tdd_core.py", ".codex/hooks.json",
]
DEADLINE = None


def budget():
    if DEADLINE is not None and time.monotonic() >= DEADLINE:
        raise ValueError("TDD inspection time limit exceeded; verification required")


def git(root, *args, binary=False):
    budget()
    timeout = max(0.05, min(5, DEADLINE - time.monotonic())) if DEADLINE else 10
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, timeout=timeout)
    if result.returncode:
        raise ValueError("Git candidate could not be inspected")
    return result.stdout if binary else result.stdout.decode("utf-8").strip()


def repository(cwd=None):
    return Path(git(cwd or Path.cwd(), "rev-parse", "--show-toplevel")).resolve()


def normalize(name):
    if not isinstance(name, str) or not name or any(ord(c) < 32 or c in "*?[]" for c in name):
        raise ValueError("Invalid target path")
    name = name.replace("\\", "/")
    if PureWindowsPath(name).drive or name.startswith("/"):
        raise ValueError("Absolute target paths are not allowed")
    parts = PurePosixPath(name).parts
    if not parts or any(p.casefold() in ("..", ".git") or ":" in p or p.endswith((" ", ".")) for p in parts):
        raise ValueError("Target escapes the permitted workspace")
    if parts[0].casefold() in EXCLUDED or (parts[-1].casefold().startswith(".env") and parts[-1].casefold() != ".env.example"):
        raise ValueError("Preserved or private target is excluded")
    return "/".join(parts)


def safe_path(root, name):
    base = Path(root).resolve()
    name = normalize(name)
    path = base / name
    cursor = base
    # Inspect ancestors outwards: never traverse a junction to inspect its child.
    for part in PurePosixPath(name).parts:
        cursor = cursor / part
        if cursor.is_symlink() or cursor.is_junction():
            raise ValueError("Symbolic link or junction targets require explicit review")
    resolved = path.resolve()
    if not resolved.is_relative_to(base):
        raise ValueError("Symlink target escapes the workspace")
    normalize(resolved.relative_to(base).as_posix())
    return path


def classify(name):
    name = normalize(name)
    if name.startswith((".tmp/", "frontend/node_modules/", "frontend/dist/", "backend/build/", "backend/.gradle/")):
        return "ignore"
    if name.startswith(("docs/", "harness/", "work/")) or name in ("AGENTS.md", "README.md", "STRUCTURE.md"):
        return "document"
    if ("/test/" in name or "/tests/" in name or re.search(r"(?:\.test\.|/test_[^/]+\.py$)", name)):
        return "test"
    if name.startswith("scripts/") and name.endswith((".py", ".mjs", ".js")):
        return "behavior"
    if name in CONTEXT or name.startswith((".codex/", ".github/", ".vscode/")) or name.endswith((".gradle", ".json", ".yaml", ".yml", ".toml", ".config.mjs")):
        return "setting"
    if name.startswith(("frontend/src/", "backend/src/main/", "db/migration/")):
        return "document" if name.endswith((".css", ".svg", ".png", ".jpg")) else "behavior"
    if name.startswith("frontend/public/"):
        return "document"
    return "unknown"


def patch_paths(patch):
    if not isinstance(patch, str) or not patch.startswith("*** Begin Patch\n") or "*** End Patch" not in patch:
        raise ValueError("Cannot determine edited paths")
    names = re.findall(r"^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)$", patch, re.M)
    if not names:
        raise ValueError("No editable paths found")
    return list(dict.fromkeys(names))


def parse_report(adapter, path, run_id=None):
    path = Path(path)
    result = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0, "names": [], "failedNames": []}
    if adapter == "junit":
        files = sorted(path.rglob("*.xml")) if path.is_dir() else [path]
        if not files or len(files) > 1000:
            raise ValueError("Missing or excessive JUnit reports")
        for report in files:
            if report.is_symlink() or (path.is_dir() and not report.resolve().is_relative_to(path.resolve())):
                raise ValueError("Test report escaped its execution directory")
            if report.stat().st_size > 20_000_000:
                raise ValueError("Test report too large")
            tree = ET.fromstring(report.read_bytes())
            for case in tree.iter("testcase"):
                name = ".".join(filter(None, (case.get("classname"), case.get("name"))))
                result["tests"] += 1
                result["names"].append(name)
                if case.find("skipped") is not None:
                    result["skipped"] += 1
                if case.find("error") is not None:
                    result["errors"] += 1
                for failure in case.findall("failure"):
                    text = " ".join((failure.get("type", ""), failure.get("message", ""), failure.text or ""))
                    if re.search(r"Assertion|ComparisonFailure|assert\.", text, re.I):
                        result["failures"] += 1
                        result["failedNames"].append(name)
                    else:
                        result["errors"] += 1
        return result
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if adapter == "unittest":
        if data.get("runId") != run_id:
            raise ValueError("Unittest report belongs to a different run")
        for key in result:
            result[key] = data.get(key, [] if key.endswith("Names") or key == "names" else 0)
    elif adapter == "vitest":
        result.update(tests=data.get("numTotalTests", 0), skipped=data.get("numPendingTests", 0), errors=data.get("numRuntimeErrorTestSuites", 0))
        for suite in data.get("testResults", []):
            for case in suite.get("assertionResults", []):
                name = case.get("fullName", "")
                result["names"].append(name)
                if case.get("status") == "failed":
                    if re.search(r"AssertionError|expected|expect\(", " ".join(case.get("failureMessages", [])), re.I):
                        result["failures"] += 1
                        result["failedNames"].append(name)
                    else:
                        result["errors"] += 1
    else:
        raise ValueError("Unsupported test report adapter")
    if any(type(result[k]) is not int or result[k] < 0 for k in ("tests", "failures", "errors", "skipped")):
        raise ValueError("Malformed test counts")
    if not isinstance(result["names"], list) or not isinstance(result["failedNames"], list):
        raise ValueError("Malformed test identifiers")
    if result["tests"] != len(result["names"]):
        raise ValueError("Report test count does not match executed identifiers")
    return result


def content(root, name, candidate="work"):
    path = safe_path(root, name)
    budget()
    if candidate == "work":
        if not path.exists():
            return None
        if not path.is_file() or path.stat().st_size > 20_000_000:
            raise ValueError("Target is not a bounded regular file")
        return path.read_bytes()
    ref = ":" if candidate == "index" else git(root, "rev-parse", "--verify", candidate + "^{commit}") + ":"
    result = subprocess.run(["git", "-C", str(root), "show", ref + normalize(name)], capture_output=True, timeout=2)
    if result.returncode:
        return None
    # A symlink stored in the index must not be read as ordinary verified code.
    mode_args = ["ls-files", "--stage", "--", name] if candidate == "index" else ["ls-tree", ref[:-1], "--", name]
    if git(root, *mode_args).startswith("120000"):
        raise ValueError("Candidate contains a symbolic link")
    return result.stdout


def digest(value):
    return hashlib.sha256(value).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def block(text, marker):
    match = re.search(r"<!-- " + re.escape(marker) + r" -->\s*```json\s*\n(.*?)\n```", text, re.S)
    return json.loads(match.group(1)) if match else None


def plan(root, task, candidate="work"):
    raw = content(root, task, candidate)
    if raw is None:
        raise ValueError("Task plan is absent from this candidate")
    data = block(raw.decode("utf-8-sig"), "tdd-plan")
    if not isinstance(data, dict) or data.get("schema") != 1 or not isinstance(data.get("cycles"), list):
        raise ValueError("Task needs one schema-1 tdd-plan JSON block")
    seen = set()
    for cycle in data["cycles"]:
        if not re.fullmatch(r"[a-zA-Z0-9_.-]+", cycle.get("id", "")) or cycle["id"] in seen:
            raise ValueError("Invalid or duplicate TDD cycle")
        seen.add(cycle["id"])
        if cycle.get("kind", "behavior") not in ("behavior", "environment", "refactor", "correction", "bootstrap"):
            raise ValueError("Unsupported TDD cycle kind")
        if not cycle.get("targets") or not isinstance(cycle.get("command"), list) or not cycle["command"]:
            raise ValueError("Cycle requires explicit targets and command arguments")
        if not all(isinstance(arg, str) for arg in cycle["command"]) or cycle.get("adapter") not in ("unittest", "vitest", "junit", "command"):
            raise ValueError("Cycle needs string arguments and a supported report adapter")
        for name in cycle["targets"] + cycle.get("tests", []) + cycle.get("settings", []):
            safe_path(root, name)
        if cycle.get("kind") == "environment" and any(classify(name) in ("behavior", "unknown") for name in cycle["targets"]):
            raise ValueError("Runtime behavior cannot be hidden in an environment exception")
        if cycle.get("kind", "behavior") != "behavior" and not cycle.get("reason"):
            raise ValueError("Exception needs a reason")
        if cycle.get("adapter") == "command" and cycle.get("kind") != "environment":
            raise ValueError("Only environment exceptions may use an exit-code-only check")
    return data


def snapshot(root, cycle, candidate="work"):
    names = sorted(set(cycle["targets"] + cycle.get("tests", []) + cycle.get("settings", []) + CONTEXT))
    for name in names:
        safe_path(root, name)
    if candidate == "work":
        values = {name: content(root, name) for name in names}
        attrs = git(root, "check-attr", "-z", "text", "eol", "filter", "--", *names, binary=True).decode().split("\x00")
        attributes = {}
        for i in range(0, len(attrs) - 1, 3):
            attributes.setdefault(attrs[i], {})[attrs[i + 1]] = attrs[i + 2]
        config = subprocess.run(["git", "-C", str(root), "config", "--get", "core.autocrlf"], capture_output=True, timeout=1)
        autocrlf = config.stdout.decode().strip().lower() in ("true", "input")
        for name, value in values.items():
            if value is None:
                continue
            attr = attributes.get(name, {})
            if attr.get("filter", "unspecified") not in ("unspecified", "unset"):
                raise ValueError("Custom Git content filters need separate candidate verification")
            text = attr.get("text", "unspecified")
            convert = text == "set" or (text != "unset" and (text == "auto" or attr.get("eol") in ("lf", "crlf") or autocrlf) and b"\x00" not in value)
            values[name] = value.replace(b"\r\n", b"\n") if convert else value
    else:
        if candidate == "index":
            listing = git(root, "ls-files", "--stage", "-z", "--", *names, binary=True)
        else:
            commit = git(root, "rev-parse", "--verify", candidate + "^{commit}")
            listing = git(root, "ls-tree", "-r", "-z", commit, "--", *names, binary=True)
        objects = {}
        for row in listing.split(b"\x00"):
            if not row:
                continue
            meta, name = row.split(b"\t", 1)
            fields = meta.decode().split()
            if fields[0] == "120000" or (candidate == "index" and fields[2] != "0"):
                raise ValueError("Symlink or unmerged candidate requires review")
            objects[name.decode()] = fields[1] if candidate == "index" else fields[2]
        values = dict.fromkeys(names)
        if objects:
            budget()
            result = subprocess.run(["git", "-C", str(root), "cat-file", "--batch"], input=("\n".join(objects.values()) + "\n").encode(), capture_output=True, timeout=2)
            if result.returncode:
                raise ValueError("Cannot read candidate blob contents")
            stream = io.BytesIO(result.stdout)
            for name in objects:
                header = stream.readline().split()
                if len(header) != 3 or header[1] != b"blob" or int(header[2]) > 20_000_000:
                    raise ValueError("Invalid or oversized candidate blob")
                values[name] = stream.read(int(header[2]))
                if stream.read(1) != b"\n":
                    raise ValueError("Incomplete candidate blob")
    return {name: digest(value) if value is not None else None for name, value in values.items()}


def worktree_id(root):
    return digest(os.path.normcase(str(Path(root).resolve())).encode())[:20]


def state_file(root, task):
    task = normalize(task)
    match = re.search(r"(?:^|/)issue-(\d+)/(task-(\d+)\.md|issue\.md)$", task)
    fixture = re.match(r"\.tmp/(issue-\d+/task-\d+)/", task)
    scope = (fixture[1] + "/fixtures/" + digest(task.encode())[:16]) if fixture else (f"issue-{match[1]}/task-{match[3]}" if match and match[3] else "tdd/" + digest(task.encode())[:16])
    return safe_path(root, f".tmp/{scope}/tdd/{worktree_id(root)}/state.json")


def read_state(root, task):
    path = state_file(root, task)
    if not path.exists():
        return {"schema": 1, "worktree": worktree_id(root), "task": normalize(task), "cycles": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("worktree") != worktree_id(root) or data.get("task") != normalize(task):
        raise ValueError("TDD state belongs to another worktree or task")
    return data


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".new")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def active_task(root):
    path = safe_path(root, ".tmp/tdd-active.json")
    if not path.exists():
        raise ValueError("No active Task; run tdd-run.py --task <record> --activate")
    return normalize(json.loads(path.read_text(encoding="utf-8"))["task"])


def receipts(root, task, candidate):
    state = read_state(root, task)
    values = list(state["cycles"].values())
    raw = content(root, task, candidate)
    formal = block(raw.decode("utf-8-sig"), "tdd-evidence") if raw else None
    if formal:
        if formal.get("schema") != 1:
            raise ValueError("Unsupported durable evidence schema")
        values += formal.get("receipts", [])
    return values


def check_edit(root, names, task=None):
    targets = []
    for name in names:
        if Path(name).is_absolute() or PureWindowsPath(name).drive:
            try:
                name = Path(name).resolve().relative_to(root).as_posix()
            except ValueError:
                raise ValueError("Patch target is outside the repository") from None
        name = normalize(name)
        safe_path(root, name)
        if classify(name) not in ("document", "test", "ignore"):
            targets.append(name)
    if not targets:
        return
    task = task or active_task(root)
    data = plan(root, task)
    state = read_state(root, task)
    for name in targets:
        permitted = False
        for cycle in data["cycles"]:
            if name not in cycle["targets"]:
                continue
            record = state["cycles"].get(cycle["id"], {})
            if record.get("spec") != digest(canonical(cycle)):
                continue
            kind = cycle.get("kind", "behavior")
            anchor = record.get("red") if kind == "behavior" else record.get("before")
            if kind in ("environment", "correction", "bootstrap"):
                # Explicit registered exceptions permit edits, never a fabricated Green.
                permitted = bool(cycle.get("reason")) and not record.get("finished")
            elif anchor and not record.get("finished") and record.get("worktree") == worktree_id(root):
                now = snapshot(root, cycle)
                permitted = all(now[p] == sha for p, sha in anchor["manifest"].items() if p not in cycle["targets"])
            if permitted:
                break
        if not permitted:
            raise ValueError(f"No current Red/exception for {name}; start a new cycle")


def changed_paths(root, candidate, base):
    args = ["diff", "--name-only", "-z", "--no-renames"]
    if candidate == "index":
        args += ["--cached", base]
    else:
        args += [base, candidate]
    output = git(root, *args, "--", *PATHSPECS, binary=True)
    return [normalize(x) for x in output.decode("utf-8").split("\x00") if x]


def check_candidate(root, candidate="index", task=None, base="HEAD"):
    names = changed_paths(root, candidate, base)
    needed = [name for name in names if classify(name) not in ("document", "ignore")]
    if not needed:
        return
    task = task or active_task(root)
    data = plan(root, task, candidate)
    available = receipts(root, task, candidate)
    manifests = {}
    for name in needed:
        valid = False
        for cycle in data["cycles"]:
            if name not in cycle["targets"] + cycle.get("tests", []) + cycle.get("settings", []):
                continue
            if cycle["id"] not in manifests:
                manifests[cycle["id"]] = snapshot(root, cycle, candidate)
            manifest = manifests[cycle["id"]]
            for receipt in available:
                final = receipt.get("final")
                if (receipt.get("id") == cycle["id"] and receipt.get("spec") == digest(canonical(cycle))
                        and receipt.get("finished") and final and final["manifest"] == manifest
                        and final.get("ok") and receipt.get("kind") == cycle.get("kind", "behavior")):
                    if receipt["kind"] == "behavior" and not receipt.get("red"):
                        continue
                    if receipt["kind"] == "refactor" and not receipt.get("before"):
                        continue
                    valid = True
                    break
        if not valid:
            raise ValueError(f"Candidate evidence missing or changed: {name}; verify this exact candidate")
