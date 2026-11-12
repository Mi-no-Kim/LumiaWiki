"""Read-only TDD inspection. Never runs tests, modifies files, or calls the network."""

import sys

sys.dont_write_bytecode = True

import argparse
import json
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
                core.check_edit(root, core.patch_paths(event["tool_input"]["command"]), args.task)
            else:
                base = args.base or ("HEAD" if args.candidate == "index" else args.candidate + "^")
                core.check_candidate(root, args.candidate, args.task, base)
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
