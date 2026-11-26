"""Read-only TDD inspection. Never runs tests, modifies files, or calls the network."""

import sys

sys.dont_write_bytecode = True

import argparse
import json
import os
import queue
import threading
import time

import tdd_core as core


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", default="index")
    parser.add_argument("--base")
    parser.add_argument("--task")
    parser.add_argument("--hook", action="store_true")
    parser.add_argument("--non-java", action="store_true", help="Leave production Java to the Java hook")
    args = parser.parse_args()
    result = queue.Queue()
    core.DEADLINE = time.monotonic() + 2.7

    def inspect():
        try:
            root = core.repository()
            if args.hook:
                event = json.loads(sys.stdin.read(2_000_001))
                if event.get("tool_name") != "apply_patch":
                    raise ValueError("Unexpected hook tool; verify the matcher")
                paths = core.patch_paths(event["tool_input"]["command"])
                if args.non_java:
                    paths = [path for path in paths if not core.production_java(core.edit_path(root, path))]
                core.check_edit(root, paths, args.task)
            else:
                base = args.base or ("HEAD" if args.candidate == "index" else args.candidate + "^")
                paths = None
                split = args.candidate == "index" and os.environ.get("LUMIA_JAVA_TDD_SPLIT") == "1"
                if args.non_java or split:
                    paths = [path for path in core.changed_paths(root, args.candidate, base)
                             if not core.production_java(path)]
                core.check_candidate(root, args.candidate, args.task, base, names=paths)
            result.put(None)
        except Exception as error:
            result.put(str(error).splitlines()[0])

    threading.Thread(target=inspect, daemon=True).start()
    try:
        reason = result.get(timeout=2.8)
    except queue.Empty:
        reason = "TDD inspection exceeded its internal deadline; verify the candidate"
    if reason:
        if args.hook:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason + "; run the declared TDD cycle."}}, ensure_ascii=False))
            # Structured policy output is a successful protocol response, even on denial.
            return 0
        else:
            print("TDD unverified: " + reason + "\nNext: run the declared tests for this exact candidate.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
