"""Execute a declared test cycle; this is the only evidence-writing tool."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid

import tdd_core as core


def export(root, task, state):
    path = core.safe_path(root, task)
    receipts = [r for r in state["cycles"].values() if r.get("finished")]
    payload = "<!-- tdd-evidence -->\n```json\n" + json.dumps({"schema": 1, "receipts": receipts}, ensure_ascii=False, indent=2) + "\n```"
    text = path.read_text(encoding="utf-8")
    pattern = r"<!-- tdd-evidence -->\s*```json\s*\n.*?\n```"
    text = re.sub(pattern, lambda _: payload, text, flags=re.S) if re.search(pattern, text, re.S) else text.rstrip() + "\n\n" + payload + "\n"
    path.write_text(text, encoding="utf-8")


def run(root, task, data, state, args):
    cycle = next((c for c in data["cycles"] if c["id"] == args.cycle), None)
    if cycle is None:
        raise ValueError("Cycle is not declared in the Task")
    kind = cycle.get("kind", "behavior")
    spec = core.digest(core.canonical(cycle))
    previous = state["cycles"].get(args.cycle, {})
    if previous.get("finished"):
        raise ValueError("Cycle is already closed; declare a new cycle")
    provided = args.command[1:] if args.command[:1] == ["--"] else args.command
    if provided and provided != cycle["command"]:
        raise ValueError("Execution command must match the declared argument array")
    if args.phase in ("red", "green") and kind != "behavior":
        raise ValueError("Exceptions use before/verify, never fabricated Red/Green")
    if args.phase == "verify" and kind == "behavior":
        raise ValueError("Behavior cycles require a real Red before Green")
    if args.phase == "before" and kind != "refactor":
        raise ValueError("Only refactoring uses a before baseline")
    before = core.snapshot(root, cycle)
    anchor = previous.get("red") if kind == "behavior" else previous.get("before")
    if args.phase == "green" or (args.phase == "verify" and kind == "refactor"):
        if not anchor or previous.get("spec") != spec or previous.get("worktree") != core.worktree_id(root):
            raise ValueError("Missing current worktree Red/before baseline")
        if any(before[name] != sha for name, sha in anchor["manifest"].items() if name not in cycle["targets"]):
            raise ValueError("Tests/settings changed since Red/before; execute a new cycle")
    if kind == "bootstrap" and not cycle.get("bootstrapEvidence"):
        raise ValueError("Bootstrap verification needs the recorded real initial test evidence")
    run_id = uuid.uuid4().hex
    directory = core.state_file(root, task).parent / "runs" / run_id
    directory.mkdir(parents=True)
    report = directory / ("junit" if cycle["adapter"] == "junit" else "report.json")
    values = {"root": str(root), "report": str(report), "run_id": run_id}
    command = []
    for part in cycle["command"]:
        for key, value in values.items():
            part = part.replace("{" + key + "}", value)
        command.append(part)
    # Argument arrays are executed directly; Windows npm/Gradle batch files use cmd's list2cmdline.
    if os.name == "nt" and command[0].lower().endswith((".cmd", ".bat")):
        if any(re.search(r'[&|<>^%\r\n]', part) for part in command):
            raise ValueError("Unsafe batch argument; use a direct executable")
        command = [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/v:off", "/c", "call", os.path.normpath(command[0]), *command[1:]]
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1"}
    started = time.time()
    process = subprocess.run(command, cwd=root, env=env, timeout=args.timeout, check=False)
    after = core.snapshot(root, cycle)
    if before != after:
        raise ValueError("Inputs changed while tests were running; no evidence recorded")
    if cycle["adapter"] == "command":
        result = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0, "names": [], "failedNames": []}
    else:
        result = core.parse_report(cycle["adapter"], report, run_id)
        if result["tests"] <= result["skipped"]:
            raise ValueError("No executed tests; result is indeterminate")
    expected = cycle.get("expectedFailures", [])
    if args.phase == "red":
        if (process.returncode == 0 or result["errors"] or not result["failures"] or not expected
                or set(result["failedNames"]) != set(expected)):
            raise ValueError("Red requires only the declared executed assertion failures, no environment errors")
    elif process.returncode != 0 or result["failures"] or result["errors"]:
        raise ValueError("Verification failed; no successful evidence recorded")
    entry = {"runId": run_id, "started": started, "finishedAt": time.time(),
             "command": cycle["command"], "exitCode": process.returncode,
             "result": result, "manifest": after, "ok": args.phase != "red"}
    receipt = {**previous, "id": cycle["id"], "kind": kind, "spec": spec,
               "worktree": core.worktree_id(root), "baseline": core.git(root, "rev-parse", "HEAD"),
               "task": task, "finished": False}
    if args.phase == "red":
        receipt["red"] = entry
    elif args.phase == "before":
        receipt["before"] = entry
    else:
        receipt.update(final=entry, finished=True)
    state["cycles"][cycle["id"]] = receipt
    core.write_json(core.state_file(root, task), state)
    print(f"TDD {args.phase}: {result['tests']} tests, {result['failures']} assertion failures, {result['errors']} errors; cycle {cycle['id']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True)
    parser.add_argument("--cycle")
    parser.add_argument("--phase", choices=("red", "green", "before", "verify"))
    parser.add_argument("--activate", action="store_true")
    parser.add_argument("--export", action="store_true", help="Preserve finished receipts in the existing Task record")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    lock = None
    try:
        root = core.repository()
        task = core.normalize(args.task)
        data = core.plan(root, task)
        path = core.state_file(root, task)
        path.parent.mkdir(parents=True, exist_ok=True)
        lock = path.with_suffix(".lock")
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        state = core.read_state(root, task)
        if args.activate:
            for cycle in data["cycles"]:
                if cycle.get("kind") in ("environment", "correction", "bootstrap"):
                    state["cycles"].setdefault(cycle["id"], {"id": cycle["id"], "kind": cycle["kind"], "spec": core.digest(core.canonical(cycle)), "worktree": core.worktree_id(root), "finished": False})
            core.write_json(path, state)
            core.write_json(core.safe_path(root, ".tmp/tdd-active.json"), {"task": task})
        if args.phase:
            if not args.cycle:
                raise ValueError("--phase needs --cycle")
            run(root, task, data, state, args)
        if args.export:
            export(root, task, state)
        if not (args.activate or args.phase or args.export):
            raise ValueError("Choose --activate, --phase, or --export")
        return 0
    except (ValueError, OSError, subprocess.SubprocessError, KeyError, json.JSONDecodeError) as error:
        print(f"TDD unverified: {str(error).splitlines()[0]}\nNext: fix the input and execute the declared cycle.", file=sys.stderr)
        return 2
    finally:
        if lock is not None and 'fd' in locals():
            lock.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
