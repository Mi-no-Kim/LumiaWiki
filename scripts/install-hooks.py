"""Install/restore one Git hook without changing core.hooksPath or Codex trust."""

import argparse
import json
import os
from pathlib import Path
import shutil
import sys

import tdd_core as core

WRAPPER = b'''#!/bin/sh
# lumiawiki-tdd-hook-v1; preserves the existing hook and resolves each worktree.
hook_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ -f "$hook_dir/pre-commit.lumiawiki-original" ]; then
  "$hook_dir/pre-commit.lumiawiki-original" "$@" || exit $?
fi
root=$(git rev-parse --show-toplevel) || exit 2
# Worktrees predating this tool keep their original hook behavior.
if [ ! -f "$root/scripts/tdd-check.py" ]; then exit 0; fi
if [ "$OS" = "Windows_NT" ]; then
  exec python -B -X utf8 "$root/scripts/tdd-check.py" --candidate index
fi
exec python3 -B -X utf8 "$root/scripts/tdd-check.py" --candidate index
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remove", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    try:
        root = core.repository()
        directory = Path(core.git(root, "rev-parse", "--git-path", "hooks"))
        if not directory.is_absolute():
            directory = root / directory
        directory = directory.resolve()
        hook = directory / "pre-commit"
        backup = directory / "pre-commit.lumiawiki-original"
        metadata = directory / ".lumiawiki-pre-commit.json"
        if hook.is_symlink() or backup.is_symlink() or metadata.is_symlink():
            raise ValueError("Symbolic-link hook needs manual review")
        if args.status:
            print(json.dumps({"installed": metadata.exists(), "hookDirectory": str(directory), "codexTrustModified": False}))
            return 0
        if metadata.exists():
            data = json.loads(metadata.read_text(encoding="utf-8"))
            if not hook.exists() or core.digest(hook.read_bytes()) != data["wrapper"]:
                raise ValueError("Installed hook was modified; preserve and review it before restoring")
            if data["original"] is not None and (not backup.exists() or core.digest(backup.read_bytes()) != data["original"]):
                raise ValueError("Original hook backup changed; nothing was removed")
            if not args.remove:
                return 0
            if data["original"] is not None:
                os.replace(backup, hook)
            else:
                hook.unlink()
            metadata.unlink()
            return 0
        if args.remove:
            return 0
        if backup.exists():
            raise ValueError("Unowned hook backup exists; nothing was overwritten")
        directory.mkdir(parents=True, exist_ok=True)
        original = core.digest(hook.read_bytes()) if hook.exists() else None
        if original is not None:
            shutil.copy2(hook, backup)
        data = {"schema": 1, "original": original, "wrapper": core.digest(WRAPPER)}
        # Prepare metadata first, and restore original bytes if installation fails.
        try:
            core.write_json(metadata, data)
            hook.write_bytes(WRAPPER)
            hook.chmod(hook.stat().st_mode | 0o111)
        except OSError:
            if backup.exists():
                os.replace(backup, hook)
            elif original is None:
                hook.unlink(missing_ok=True)
            metadata.unlink(missing_ok=True)
            raise
        return 0
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        print("Hook installation unverified: " + str(error).splitlines()[0], file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
