"""Check branch refs from the Git reference-transaction and pre-push hooks."""

import os
import re
import subprocess
import sys

BRANCH_PREFIX = "refs/heads/"
ARCHIVE = BRANCH_PREFIX + "codex/local-history-before-init"
WORK_NAME = r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
BRANCH_NAME = re.compile(rf"(?:main|phase/[0-9]{{3,}}-{WORK_NAME}"
                         rf"|issue/[1-9][0-9]*-{WORK_NAME}"
                         rf"|task/[1-9][0-9]*-[0-9]{{3,}}-{WORK_NAME})")


def is_zero(oid):
    return bool(oid) and not oid.strip("0")


def check_name(ref):
    name = ref.removeprefix(BRANCH_PREFIX)
    if "codex" in name.lower():
        raise ValueError(f"'{name}' contains the reserved text 'codex'.")
    if not BRANCH_NAME.fullmatch(name):
        raise ValueError(f"'{name}' must follow main, phase/<number>-<name>, "
                         "issue/<number>-<name>, or task/<issue>-<number>-<name>.")


def check_transaction(archive, state, updates):
    if state != "prepared":
        return
    for old, new, ref in updates:
        if not ref.startswith(BRANCH_PREFIX):
            continue
        if archive and ref.lower() == ARCHIVE:
            if ref == ARCHIVE and old == new and not is_zero(new):
                continue
            raise ValueError(f"'{ARCHIVE.removeprefix(BRANCH_PREFIX)}' is a preserved local archive.")
        if is_zero(new) or not is_zero(old):
            continue
        try:
            check_name(ref)
        except ValueError:
            # Git also sends a zero old OID when it updates an existing ref blindly.
            if not ref_exists(ref):
                raise


def git(*args):
    # Inspect only locally available objects and their original ancestry.
    env = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_NO_REPLACE_OBJECTS="1")
    return subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env, timeout=10)


def ref_exists(ref):
    existing = git("for-each-ref", "--format=%(refname)", ref)
    if existing.returncode != 0:
        raise ValueError(f"Could not check whether '{ref}' already exists.")
    return ref in existing.stdout.splitlines()


def archive_commit():
    if not ref_exists(ARCHIVE):
        return None
    commit = git("rev-parse", "--verify", "--quiet", ARCHIVE + "^{commit}")
    if commit.returncode != 0:
        raise ValueError("Could not resolve the local archive commit.")
    return commit.stdout.strip()


def check_archive(archive, oid, destination):
    commit = git("rev-parse", "--verify", "--quiet", oid + "^{commit}")
    if commit.returncode == 1:
        # An ordinary tag can point to a blob or a tree.
        if git("cat-file", "-e", oid).returncode == 0:
            return
    if commit.returncode != 0:
        raise ValueError(f"Could not inspect the outgoing object for '{destination}'.")
    relation = git("merge-base", archive, commit.stdout.strip())
    if relation.returncode == 0:
        raise ValueError(f"'{destination}' would send history from the local-only archive.")
    if relation.returncode != 1:
        raise ValueError(f"Could not check archive ancestry for '{destination}'.")


def check_push(archive, updates):
    outgoing = []
    for source, oid, destination, _ in updates:
        if is_zero(oid):
            continue
        if source.lower() == ARCHIVE:
            raise ValueError("The local history archive cannot be pushed.")
        if destination.startswith(BRANCH_PREFIX):
            check_name(destination)
        outgoing.append((oid, destination))
    if not archive or not outgoing:
        return
    history = git("rev-parse", "--is-shallow-repository")
    if history.returncode != 0 or history.stdout.strip() != "false":
        raise ValueError("Verifying the local archive requires full commit history.")
    for oid, destination in outgoing:
        check_archive(archive, oid, destination)


def change_branch(event, arguments):
    if len(arguments) != 2:
        raise ValueError(f"Usage: check-branch-names.py {event} <old-name> <new-name>")
    source, target = arguments
    check_name(BRANCH_PREFIX + target)
    if (BRANCH_PREFIX + source).lower() == ARCHIVE:
        raise ValueError("The local history archive cannot be moved or copied.")
    flag = "--move" if event == "rename" else "--copy"
    return subprocess.run(["git", "branch", flag, "--", source, target]).returncode


def read_updates(max_splits):
    for line in sys.stdin.buffer:
        yield line.rstrip(b"\r\n").decode("utf-8", "backslashreplace").rsplit(" ", max_splits)


def main():
    try:
        event, *arguments = sys.argv[1:]
        if event in ("rename", "copy"):
            return change_branch(event, arguments)
        if event == "archive-pin":
            # The installed push hook recognizes this history even after a native ref rename.
            print(archive_commit() or "")
            return 0
        if event == "reference-transaction":
            archive, state = arguments
            check_transaction(archive, state, read_updates(2))
        elif event == "pre-push":
            archive, _remote_name, _remote_url = arguments
            check_push(archive, read_updates(3))
        else:
            raise ValueError("Unknown branch check command.")
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(f"Branch names: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
