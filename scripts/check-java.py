"""Java hook entry point and reusable index/commit approval check."""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from harness_inventory import Candidate, path_name, safe_work_path
from java_guard import (
    Authorization, Change, MAX_INPUT, POLICY, Policy, Violation, changes_between, check_place,
    check_policy, configured_context, edit_identity, git_commit, index_identity, json_changes, parse_json,
    placement, source_kind,
)
import tdd_core


EXIT = {"pass": 0, "not-applicable": 0, "violation": 1, "unconfirmed": 2}
NEXT = {
    "before-edit": "Run the declared Red or verify the scoped exception, then retry the edit.",
    "after-edit": "Fix the Java destination or confirm its package approval, then recheck it.",
    "candidate": "Check the target, restage a corrected candidate or confirm its approval and TDD evidence, then rerun.",
}


def patch_operations(view, event):
    if event.get("tool_name") != "apply_patch":
        return []
    text = event["tool_input"]["command"]
    first, *lines = text.splitlines()
    if first != "*** Begin Patch" or not lines or lines[-1] != "*** End Patch":
        raise ValueError("Cannot identify apply_patch operations")
    cwd = Path(event.get("cwd") or view.root)
    if not cwd.resolve().is_relative_to(view.root):
        raise ValueError("Edit working directory is outside the repository")

    def path(value):
        raw = Path(value)
        if ".." in raw.parts:
            raise ValueError("Edit target traverses a parent directory")
        absolute = (cwd / raw).absolute()
        if not absolute.is_relative_to(view.root):
            return absolute.as_posix()
        relative = absolute.relative_to(view.root).as_posix()
        if source_kind(relative):
            safe_work_path(view.root, path_name(relative))
        return relative

    operations = []
    for line in lines[:-1]:
        match = re.fullmatch(r"\*\*\* (Add File|Update File|Delete File|Move to): (.+)", line)
        if match:
            kind, name = match.groups()
            target = path(name)
            if kind == "Move to":
                if not operations or operations[-1].operation != "modify":
                    raise ValueError("Move destination is missing a source")
                old = operations.pop()
                operations.append(Change("move", target, old.path, behavior=True))
            else:
                operation = {"Add File": "create", "Update File": "modify", "Delete File": "delete"}[kind]
                operations.append(Change(operation, target, behavior=True))
        elif line.startswith("*** ") and line != "*** End of File":
            raise ValueError("Unrecognized apply_patch operation")
    if not operations:
        raise ValueError("No apply_patch paths were identified")
    return [item for item in operations if source_kind(item.path) or (item.from_path and source_kind(item.from_path))]


def production_targets(changes):
    return list(dict.fromkeys(path for change in changes for path in change.production_targets()))


def allows_cycle(exceptions, path, cycle):
    return path in cycle["targets"] and (
        cycle.get("kind", "behavior") == "behavior" or cycle["id"] in exceptions.get(path, [])
    )


def check_tdd(view, args, changes, base, scopes):
    targets = production_targets(changes)
    if not targets:
        return
    tdd_core.DEADLINE = view.deadline
    permit = lambda path, cycle: allows_cycle(scopes, path, cycle)
    try:
        if args.mode == "before-edit":
            tdd_core.check_edit(view.root, targets, args.task, allow_cycle=permit)
        else:
            tdd_core.check_candidate(view.root, view.commit or view.kind, args.task, base,
                                     names=targets, allow_cycle=permit, require_target_change=True)
    except (ValueError, OSError) as error:
        raise ValueError(f"{targets[0]}: {error}") from error


def identify(view, base, identity, changes):
    deltas = []
    if view.kind != "work" and any(change.path == POLICY or change.from_path == POLICY for change in changes):
        old = Candidate(base, cwd=view.root, seconds=8)
        deltas = list(json_changes(Policy(old.read(POLICY)).data, Policy(view.read(POLICY)).data))
    return {"candidateId": identity, "baseRevision": base,
            "changes": [change.description() for change in changes], "policyChanges": deltas}


def inspect_edit(view, args):
    raw = sys.stdin.buffer.read(MAX_INPUT + 1)
    changes = patch_operations(view, parse_json(raw))
    context = configured_context(args.approval_context, edit=True)
    if args.mode == "before-edit":
        targets = production_targets(changes)
        if not targets and not args.identify:
            return "not-applicable", "No production Java operation requires TDD evidence"
        base = git_commit(view, args.base or "HEAD")
        identity = edit_identity(changes)
        if args.identify:
            return identify(view, base, identity, changes)
        auth = Authorization(view, base, identity, context)
        scopes = auth.scopes([item for item in changes if item.production_targets()]) if context else {}
        check_tdd(view, args, changes, base, scopes)
        return "pass", "TDD evidence is current for the edit"

    targets = [item for item in changes if item.operation in ("create", "move") and source_kind(item.path)]
    if not targets:
        return "not-applicable", "No Java creation or move to check"
    policy = Policy(view.read(POLICY))
    auth = None
    if context:
        base = git_commit(view, args.base or "HEAD")
        auth = Authorization(view, base, edit_identity(changes), context)
    for item in targets:
        properties = placement(view, policy, item.path)
        source, package, class_name = properties
        if not policy.allows(source, package, class_name):
            if auth:
                check_place(auth, policy, policy, item, properties)
                continue
            raise Violation(f"{item.path}: destination is not in the current Java policy; check its approval")
    return "pass", "Edited Java destinations match the placement policy"


def inspect_candidate(view, args):
    if args.base is None:
        base = view.git("rev-parse", "--verify", "HEAD^{commit}", allowed=(0, 128)).decode().strip()
        if not base:
            view.git("symbolic-ref", "HEAD")
            initial = changes_between(view, None)
            if all(change.path == POLICY for change in initial) and not args.identify:
                return "not-applicable", "Initial index has no Java sources or prior policy to compare"
            raise ValueError("A verified base is required for Java changes")
    else:
        base = git_commit(view, args.base)
    identity = index_identity(view) if view.kind == "index" else view.commit
    changes = changes_between(view, base)
    if args.identify:
        result = identify(view, base, identity, changes)
        if view.kind == "index" and index_identity(view) != identity:
            raise ValueError("The index changed while identifying Java changes")
        return result
    if not changes:
        if view.kind == "index" and index_identity(view) != identity:
            raise ValueError("The index changed while Java checks were running")
        return "not-applicable", "No applicable changed Java source or policy input in the Git candidate"
    previous = Candidate(base, cwd=view.root, seconds=8)
    old = Policy(previous.read(POLICY))
    new = Policy(view.read(POLICY))
    auth = Authorization(view, base, identity, configured_context(args.approval_context))
    # Surface a confirmed placement mismatch before asking for approval evidence.
    for item in changes:
        if item.operation == "modify" and source_kind(item.path) and item.path.endswith("/package-info.java"):
            placement(view, new, item.path)
    placements = [(item, placement(view, new, item.path)) for item in changes
                  if item.operation in ("create", "move") and source_kind(item.path)]
    scopes = auth.scopes(changes)
    check_policy(auth, old, new)
    for item, properties in placements:
        check_place(auth, old, new, item, properties)
    if not args.approval_only:
        check_tdd(view, args, changes, base, scopes)
    if view.kind == "index" and index_identity(view) != identity:
        raise ValueError("The index changed while Java checks were running")
    return "pass", "Candidate Java placement and required evidence agree"


def emit(args, status, reason):
    data = {"status": status, "reason": reason, "next": NEXT[args.mode] if EXIT[status] else None}
    if args.mode == "candidate" or not args.hook:
        # Keep manual and CI calls machine-readable; Git displays the same data.
        print(json.dumps(data, ensure_ascii=False))
        return EXIT[status]
    if not EXIT[status]:
        return 0
    message = f"Java {status}: {reason}\nNext: {data['next']}"
    if args.mode == "before-edit":
        output = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                        "permissionDecisionReason": message}}
    else:
        output = {"systemMessage": message,
                  "hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": message}}
    print(json.dumps(output, ensure_ascii=False))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("candidate", "before-edit", "after-edit"), default="candidate")
    parser.add_argument("--candidate", default="index")
    parser.add_argument("--base")
    parser.add_argument("--approval-only", action="store_true")
    parser.add_argument("--approval-context")
    parser.add_argument("--task")
    parser.add_argument("--identify", action="store_true")
    parser.add_argument("--hook", action="store_true")
    args = parser.parse_args()
    if args.mode == "candidate" and args.candidate == "work":
        parser.error("The candidate must be index or an explicit Git commit")
    if args.mode == "candidate" and args.candidate != "index" and not args.base:
        parser.error("An explicit commit requires --base")
    if args.identify and (args.hook or args.mode == "after-edit"):
        parser.error("Use --identify only for candidate or before-edit input")
    try:
        if args.mode == "candidate":
            view = Candidate(args.candidate, seconds=12)
            result = inspect_candidate(view, args)
        else:
            view = Candidate("work", seconds=5)
            result = inspect_edit(view, args)
        if args.identify:
            print(json.dumps(result, ensure_ascii=False))
            return 0
        return emit(args, *result)
    except Violation as error:
        return emit(args, "violation", str(error).splitlines()[0])
    except (ValueError, OSError, KeyError, AttributeError, TypeError, IndexError,
            StopIteration, re.error, subprocess.SubprocessError) as error:
        return emit(args, "unconfirmed", str(error).splitlines()[0] if str(error) else "Required input is unreadable")
    finally:
        tdd_core.DEADLINE = None


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    raise SystemExit(main())
