"""Exercise installed Git branch hooks with disposable local and bare repositories."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[2]
ARCHIVE = "codex/local-history-before-init"
LEGACY = "codex/legacy-work"
EVENTS = ("reference-transaction", "pre-push")
FILES = ("scripts/install-harness-hooks.py", "scripts/check-branch-names.py",
         "scripts/hooks/reference-transaction", "scripts/hooks/pre-push")


class BranchHookTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="branch-hooks-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name) / "local"
        self.remote = self.root.parent / "remote.git"
        self.root.mkdir()
        self.env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        self.env.pop("GIT_DEFAULT_REF_FORMAT", None)
        self.git("init", "-q", "--template=", "-b", "main")
        self.git("config", "user.name", "Branch hook fixture")
        self.git("config", "user.email", "hook@example.invalid")
        self.git("commit", "-qm", "Main fixture", "--allow-empty")
        self.git("branch", LEGACY)
        self.git("init", "-q", "--template=", "--bare", str(self.remote))
        self.git("remote", "add", "fixture", str(self.remote))
        for name in FILES:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(PROJECT / name, path)

    def run_process(self, *args, cwd=None, check=True):
        result = subprocess.run(args, cwd=cwd or self.root, env=self.env, capture_output=True,
                                text=True, encoding="utf-8", errors="replace", timeout=30)
        if check:
            self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def git(self, *args, **kwargs):
        return self.run_process("git", *args, **kwargs)

    def install(self, event, *args):
        return self.run_process(sys.executable, "-B", "-X", "utf8",
                                "scripts/install-harness-hooks.py", "--hook", event, *args)

    def change_branch(self, event, *args, check=True):
        return self.run_process(sys.executable, "-B", "-X", "utf8",
                                "scripts/check-branch-names.py", event, *args, check=check)

    def deny(self, *args, detail=None, cwd=None):
        result = self.git(*args, check=False, cwd=cwd)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("Branch names:", result.stderr)
        if detail:
            self.assertIn(detail, result.stderr)

    def oid(self, ref, cwd=None):
        result = self.git("show-ref", "--verify", "--hash", ref, cwd=cwd, check=False)
        return result.stdout.strip() if result.returncode == 0 else None

    def create_archive(self):
        self.git("switch", "-q", "--orphan", "archive-fixture")
        self.git("commit", "-qm", "Archive root fixture", "--allow-empty")
        self.git("commit", "-qm", "Archive tip fixture", "--allow-empty")
        self.git("branch", ARCHIVE)
        self.git("switch", "-q", "main")
        self.git("branch", "-D", "archive-fixture")

    def test_checks_branch_creation_and_normal_updates(self):
        self.install("reference-transaction")
        for name in ("phase/001-fixture", "issue/81-fixture", "task/81-002-fixture-r2"):
            with self.subTest(name=name):
                self.git("branch", name)
                self.assertIsNotNone(self.oid("refs/heads/" + name))
        for name in ("feature/invalid", "task/81-02-invalid", "issue/81-abcdefcodexfix",
                     "task/81-002-fixture-CoDeX", ARCHIVE):
            with self.subTest(name=name):
                self.deny("branch", name)
                self.assertIsNone(self.oid("refs/heads/" + name))
        self.deny("switch", "-c", "codex/forbidden")
        self.deny("worktree", "add", "-b", "codex/linked", str(self.root.parent / "denied"))
        self.git("switch", "-q", "task/81-002-fixture-r2")
        self.git("commit", "-qm", "Normal update", "--allow-empty")
        self.git("branch", "-f", LEGACY, "HEAD")
        self.assertEqual(self.oid("refs/heads/" + LEGACY),
                         self.oid("refs/heads/task/81-002-fixture-r2"))
        self.git("switch", "-q", LEGACY)
        self.git("commit", "-qm", "Existing local branch update", "--allow-empty")

    def test_rename_rejects_invalid_target_and_preserves_source(self):
        self.install("reference-transaction")
        self.git("branch", "task/81-002-good")
        original = self.oid("refs/heads/task/81-002-good")
        for mode in ("rename", "copy"):
            result = self.change_branch(mode, "task/81-002-good", "task/81-002-CoDeX", check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("contains the reserved text", result.stderr)
        self.assertEqual(self.oid("refs/heads/task/81-002-good"), original)
        self.assertIsNone(self.oid("refs/heads/task/81-002-CoDeX"))
        result = self.change_branch("rename", "task/81-002-good", LEGACY, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.oid("refs/heads/task/81-002-good"), original)
        self.assertIsNotNone(self.oid("refs/heads/" + LEGACY))
        self.change_branch("rename", LEGACY, "task/81-002-cleaned")
        self.assertIsNone(self.oid("refs/heads/" + LEGACY))
        self.assertIsNotNone(self.oid("refs/heads/task/81-002-cleaned"))
        self.change_branch("copy", "task/81-002-cleaned", "task/81-002-copy")
        self.assertEqual(self.oid("refs/heads/task/81-002-cleaned"),
                         self.oid("refs/heads/task/81-002-copy"))
        self.git("branch", "-D", "task/81-002-cleaned")

    def test_existing_archive_ref_stays_local_and_unchanged(self):
        self.create_archive()
        ref = "refs/heads/" + ARCHIVE
        before = self.oid(ref)
        self.install("reference-transaction")
        self.deny("branch", "-D", ARCHIVE, detail="preserved local archive")
        self.deny("branch", "-m", ARCHIVE, "task/81-002-renamed", detail="preserved local archive")
        result = self.change_branch("rename", ARCHIVE, "task/81-002-renamed", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("archive cannot be moved", result.stderr)
        self.deny("update-ref", ref, "HEAD", detail="preserved local archive")
        self.assertEqual(self.oid(ref), before)
        self.assertIsNone(self.oid("refs/heads/task/81-002-renamed"))
        self.git("show", "-s", ARCHIVE)

    def test_checks_remote_target_and_allows_ordinary_tags_and_cleanup(self):
        self.git("push", "fixture", "main:refs/heads/" + LEGACY)
        self.install("pre-push")
        normal = "refs/heads/task/81-002-valid"
        invalid = "refs/heads/task/81-002-preCoDeXpost"
        self.git("push", "fixture", "HEAD:" + normal)
        self.deny("push", "fixture", "HEAD:" + invalid, detail="contains the reserved text")
        self.assertIsNone(self.oid(invalid, cwd=self.remote))
        self.git("commit", "-qm", "Updated normal branch", "--allow-empty")
        self.git("push", "fixture", "HEAD:" + normal)
        self.deny("push", "fixture", "HEAD:refs/heads/" + LEGACY)
        self.git("push", "fixture", "--delete", LEGACY)
        self.assertIsNone(self.oid("refs/heads/" + LEGACY, cwd=self.remote))
        self.git("tag", "codex-release-fixture")
        self.git("push", "fixture", "refs/tags/codex-release-fixture")
        self.assertIsNotNone(self.oid("refs/tags/codex-release-fixture", cwd=self.remote))
        self.git("push", "fixture", "HEAD@{1 minute ago}:refs/heads/issue/81-reflog")

    def test_rejects_archive_aliases_and_history_in_tag_or_branch(self):
        self.create_archive()
        self.git("branch", "task/81-002-alias", ARCHIVE)
        self.git("tag", "-am", "Archive tag", "archive-fixture-tag", ARCHIVE)
        self.git("switch", "-q", "task/81-002-alias")
        self.git("commit", "-qm", "Archive descendant", "--allow-empty")
        self.install("pre-push")
        target = "refs/heads/task/81-002-archive"
        old = self.git("rev-parse", ARCHIVE + "^").stdout.strip()
        for source in (ARCHIVE, "HEAD", "task/81-002-alias", old):
            with self.subTest(source=source):
                self.deny("push", "fixture", f"{source}:{target}", detail="archive")
                self.assertIsNone(self.oid(target, cwd=self.remote))
        self.deny("push", "fixture", "refs/tags/archive-fixture-tag", detail="archive")
        self.assertIsNone(self.oid("refs/tags/archive-fixture-tag", cwd=self.remote))
        self.git("push", "fixture", "main")
        self.assertIsNotNone(self.oid("refs/heads/main", cwd=self.remote))
        # The archive's identity is retained even if its original ref disappears.
        self.git("branch", "-m", ARCHIVE, "task/81-002-moved-archive")
        self.assertIsNone(self.oid("refs/heads/" + ARCHIVE))
        self.deny("push", "fixture", "task/81-002-moved-archive:" + target, detail="archive")
        self.assertIsNone(self.oid(target, cwd=self.remote))
        self.git("fetch", "--depth=1", "fixture", "main")
        self.assertEqual(self.git("rev-parse", "--is-shallow-repository").stdout.strip(), "true")
        self.deny("push", "fixture", "main:refs/heads/issue/81-shallow", detail="full commit history")

    def test_existing_hooks_receive_stdin_and_are_restored(self):
        script = b'#!/bin/sh\ncat >"$1.received"\n[ ! -f deny-hook ] || exit 17\n'
        hooks = self.root / ".git/hooks"
        hooks.mkdir(exist_ok=True)
        for event in EVENTS:
            original = hooks / event
            original.write_bytes(script)
            original.chmod(0o755)
            self.install(event)
            status = json.loads(self.install(event, "--status").stdout)
            self.assertTrue(status["previousHook"])
            self.install(event)
        self.git("branch", "issue/81-from-stdin")
        self.assertIn("refs/heads/issue/81-from-stdin", (self.root / "prepared.received").read_text())
        self.git("push", "fixture", "HEAD:refs/heads/issue/81-remote-stdin")
        self.assertIn("refs/heads/issue/81-remote-stdin", (self.root / "fixture.received").read_text())
        self.deny("branch", "codex/after-original")
        self.deny("push", "fixture", "HEAD:refs/heads/issue/81-CoDeX")
        (self.root / "deny-hook").touch()
        self.assertNotEqual(self.git("branch", "issue/81-old-hook-veto", check=False).returncode, 0)
        self.assertNotEqual(self.git("push", "fixture", "HEAD:refs/heads/issue/81-veto",
                                     check=False).returncode, 0)
        for event in EVENTS:
            self.install(event, "--remove")
            self.assertEqual((hooks / event).read_bytes(), script)
            self.assertFalse(json.loads(self.install(event, "--status").stdout)["installed"])
        if os.name != "nt":
            for event in EVENTS:
                (hooks / event).chmod(0o644)
                self.install(event)
            self.git("branch", "issue/81-inactive-hook")
            self.git("push", "fixture", "HEAD:refs/heads/issue/81-inactive-hook")
            for event in EVENTS:
                self.install(event, "--remove")
                self.assertFalse(os.access(hooks / event, os.X_OK))

    def test_linked_worktree_without_checker_uses_installed_hook(self):
        linked = self.root.parent / "linked"
        for event in EVENTS:
            self.install(event)
        self.git("worktree", "add", "-qb", "issue/81-linked", str(linked))
        self.assertFalse((linked / "scripts/check-branch-names.py").exists())
        self.deny("branch", "issue/81-CoDeX", cwd=linked)
        self.deny("push", "fixture", "HEAD:refs/heads/issue/81-CoDeX", cwd=linked)
        self.git("branch", "issue/81-normal", cwd=linked)


    def test_primary_checkout_installs_from_same_repository_worktree(self):
        self.create_archive()
        linked = self.root.parent / "source"
        self.git("worktree", "add", "-qb", "task/81-002-source", str(linked))
        for name in FILES:
            source = linked / name
            source.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(self.root / name, source)
        installer = (sys.executable, "-B", "-X", "utf8", str(linked / FILES[0]))
        other = self.root.parent / "other"
        other.mkdir()
        self.git("init", "-q", "--template=", cwd=other)
        rejected = self.run_process(*installer, "--hook", "pre-push",
                                    "--source-worktree", str(other), check=False)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("must share the target Git repository", rejected.stderr)
        self.assertFalse((self.root / ".git/hooks/pre-push").exists())
        for event in EVENTS:
            self.run_process(*installer, "--hook", event, "--source-worktree", str(linked))
            status = json.loads(self.run_process(*installer, "--hook", event, "--status").stdout)
            self.assertTrue(status["installed"])
        self.deny("branch", "issue/81-CoDeX", cwd=linked)
        self.deny("push", "fixture", f"{ARCHIVE}:refs/heads/issue/81-archive", detail="archive")
        self.git("push", "fixture", "main")
        for event in EVENTS:
            self.run_process(*installer, "--hook", event, "--remove")
            self.assertFalse((self.root / ".git/hooks" / event).exists())


if __name__ == "__main__":
    unittest.main()
