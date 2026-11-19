"""Exercise closing guards with disposable histories and real commit-msg hooks."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from github_closing import event_violations, range_violations, violations

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / 'scripts/check-github-closing.py'
INSTALLER = ROOT / 'scripts/install-harness-hooks.py'


class ClosingTextTests(unittest.TestCase):
    def test_incident_and_keyword_reference_variants(self):
        for keyword in ('close', 'closes', 'closed', 'fix', 'fixes', 'fixed', 'resolve', 'resolves', 'resolved'):
            for reference in ('#72', 'owner/repo#72', 'https://github.com/owner/repo/issues/72'):
                for wrapper in ('{}: {}', '**{}:** **{}**', '{}: ({})', '{}\r\n{}'):
                    with self.subTest(keyword=keyword, reference=reference, wrapper=wrapper):
                        self.assertTrue(violations(wrapper.format(keyword.upper(), reference), 'test'))
        self.assertTrue(violations('fix: #72 1차 하네스 개선 적용과 동일 입력 비교', 'incident'))
        self.assertTrue(violations('설명\n\nFixed #72, resolves other/repo#5', 'body'))

    def test_descriptions_refs_and_unrelated_words_are_safe(self):
        for text in ('fix: 계산 오류 수정\n\nRefs #72', 'fix: 계산 오류 수정 (#72)',
                     'issue(72): 결과 통합 (#77)\n\nRefs #72', 'prefixes #72',
                     'unresolved #72', 'fixed-point #72', '닫기 키워드 fix의 의미', 'REFS owner/repo#72'):
            with self.subTest(text=text):
                self.assertEqual([], violations(text, 'safe'))


class ClosingIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='closing guard ')
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.git('init', '--quiet')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'user.name', 'Closing guard test')
        self.git('config', 'core.autocrlf', 'false')
        self.base = self.new_commit('chore: 기반')

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args]).decode('utf-8').strip()

    def new_commit(self, message):
        self.git('-c', 'core.hooksPath=/dev/null', 'commit', '--quiet', '--allow-empty', '-m', message)
        return self.git('rev-parse', 'HEAD')

    def cli(self, *args):
        return subprocess.run([sys.executable, '-B', '-X', 'utf8', str(CLI), '--repo', str(self.repo), *args],
                              capture_output=True, text=True, encoding='utf-8')

    def install(self, *args):
        return subprocess.run([sys.executable, '-B', '-X', 'utf8', str(INSTALLER), '--hook', 'commit-msg', *args],
                              cwd=self.repo, capture_output=True, text=True, encoding='utf-8')

    def copy_hook_sources(self):
        for name in ('scripts/check-github-closing.py', 'scripts/github_closing.py', 'scripts/hooks/commit-msg'):
            target = self.repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    def real_commit(self, message):
        path = self.repo / 'message with spaces.txt'
        path.write_bytes(message.encode('utf-8'))
        return subprocess.run(['git', '-C', str(self.repo), 'commit', '--quiet', '--allow-empty',
                               '--cleanup=verbatim', '--file', str(path)], capture_output=True)

    def test_range_checks_earlier_commit_body_and_excludes_existing_base(self):
        bad = self.new_commit('chore: 수정\n\nFIX: #72')
        head = self.new_commit('fix: 계산 오류 수정\n\nRefs #72')
        failures = range_violations(self.repo, self.base, head)
        self.assertEqual(1, len(failures))
        self.assertIn(bad, failures[0])
        self.assertEqual([], range_violations(self.repo, bad, head))

    def test_side_branch_commit_is_checked(self):
        original = self.git('branch', '--show-current')
        self.git('switch', '--quiet', '-c', 'side')
        bad = self.new_commit('fix: #72')
        self.git('switch', '--quiet', original)
        self.new_commit('chore: 다른 변경')
        self.git('-c', 'core.hooksPath=/dev/null', 'merge', '--quiet', '--no-ff', 'side', '-m', 'chore: 통합')
        self.assertIn(bad, range_violations(self.repo, self.base, 'HEAD')[0])
        self.assertEqual([], event_violations(self.repo, {}, 'workflow_dispatch'))

    def test_pr_title_body_and_commits_all_checked(self):
        self.new_commit('chore: 수정\n\nCloses #7')
        head = self.new_commit('chore: 최종 요약')
        payload = {'pull_request': {'title': 'FIX: #72', 'body': '설명\nResolves other/repo#8',
                                   'base': {'sha': self.base}, 'head': {'sha': head}}}
        failures = event_violations(self.repo, payload, 'pull_request')
        self.assertEqual(3, len(failures))
        self.assertTrue(any(x.startswith('PR title:') for x in failures))
        self.assertTrue(any(x.startswith('PR body:') for x in failures))
        self.assertTrue(any(x.startswith('commit ') for x in failures))

    def test_push_checks_only_new_history(self):
        bad = self.new_commit('fix: #72')
        head = self.new_commit('fix: 계산 오류 수정\n\nRefs #72')
        self.assertEqual([], event_violations(self.repo, {'before': bad, 'after': head}, 'push'))
        self.assertTrue(event_violations(self.repo, {'before': '0' * 40, 'after': head}, 'push'))

    def test_message_cli_handles_crlf_bom_and_missing_input(self):
        path = self.repo / 'message.txt'
        path.write_bytes(b'\xef\xbb\xbf' + 'fix: 계산 오류 수정\r\n\r\nRefs #72\r\n'.encode('utf-8'))
        self.assertEqual(0, self.cli('--message-file', str(path)).returncode)
        path.write_bytes(b'\xef\xbb\xbfFIX:\r\n#72\r\n')
        self.assertEqual(1, self.cli('--message-file', str(path)).returncode)
        path.unlink()
        self.assertEqual(2, self.cli('--message-file', str(path)).returncode)

    def test_pr_file_is_checked_even_with_no_new_commits(self):
        path = self.repo / 'PR.txt'
        path.write_text('chore: 요약\n\nFixes: #72', encoding='utf-8')
        self.assertEqual(1, self.cli('--base', self.base, '--head', self.base, '--pr-file', str(path)).returncode)
        path.write_text('chore: 요약\n\nRefs #72', encoding='utf-8')
        self.assertEqual(0, self.cli('--base', self.base, '--head', self.base, '--pr-file', str(path)).returncode)

    def test_bad_event_and_unreadable_range_fail_closed(self):
        path = self.repo / 'event.json'
        path.write_text('{"pull_request": {"title": "safe"}}', encoding='utf-8')
        self.assertEqual(2, self.cli('--event-file', str(path), '--event-name', 'pull_request').returncode)
        self.assertEqual(2, self.cli('--base', 'absent-ref').returncode)
        self.assertEqual(2, self.cli('--base', '').returncode)
        path.write_text('{', encoding='utf-8')
        self.assertEqual(2, self.cli('--event-file', str(path), '--event-name', 'push').returncode)

    def test_shallow_range_is_unconfirmed(self):
        self.new_commit('fix: #72')
        self.new_commit('chore: 최종 요약')
        clone = self.repo / 'shallow clone'
        subprocess.run(['git', 'clone', '--quiet', '--no-checkout', '--depth=1', self.repo.as_uri(), str(clone)],
                       check=True, capture_output=True)
        subprocess.run(['git', '-C', str(clone), 'fetch', '--quiet', '--depth=1', 'origin', self.base],
                       check=True, capture_output=True)
        with self.assertRaisesRegex(ValueError, 'shallow boundary'):
            range_violations(clone, self.base, 'HEAD')

    def test_real_commit_rejects_closing_and_allows_refs(self):
        self.copy_hook_sources()
        self.assertEqual(0, self.install().returncode)
        for newline in ('\n', '\r\n'):
            with self.subTest(newline=repr(newline)):
                before = self.git('rev-parse', 'HEAD')
                self.assertNotEqual(0, self.real_commit('fix: #72' + newline).returncode)
                self.assertEqual(before, self.git('rev-parse', 'HEAD'))
                self.assertEqual(0, self.real_commit(('fix: 계산 오류 수정\n\nRefs #72\n').replace('\n', newline)).returncode)

    def test_previous_hook_changes_message_before_guard_and_is_restored(self):
        self.copy_hook_sources()
        hook = self.repo / '.git/hooks/commit-msg'
        original = b'#!/bin/sh\nprintf "fix: #72\\n" > "$1"\n'
        hook.write_bytes(original)
        hook.chmod(0o755)
        self.assertEqual(0, self.install().returncode)
        before = self.git('rev-parse', 'HEAD')
        self.assertNotEqual(0, self.real_commit('chore: 안전한 원문').returncode)
        self.assertEqual(before, self.git('rev-parse', 'HEAD'))
        self.assertEqual(0, self.install('--remove').returncode)
        self.assertEqual(original, hook.read_bytes())

    def test_previous_hook_failure_is_preserved(self):
        self.copy_hook_sources()
        hook = self.repo / '.git/hooks/commit-msg'
        hook.write_bytes(b'#!/bin/sh\necho prior-hook-rejected >&2\nexit 7\n')
        hook.chmod(0o755)
        self.assertEqual(0, self.install().returncode)
        result = self.real_commit('chore: 안전한 원문')
        self.assertNotEqual(0, result.returncode)
        self.assertIn(b'prior-hook-rejected', result.stderr)

    def test_missing_checker_and_changed_wrapper_fail_closed(self):
        self.copy_hook_sources()
        self.assertEqual(0, self.install().returncode)
        (self.repo / 'scripts/check-github-closing.py').unlink()
        self.assertNotEqual(0, self.real_commit('chore: 안전한 원문').returncode)
        hook = self.repo / '.git/hooks/commit-msg'
        changed = hook.read_bytes() + b'\n# changed\n'
        hook.write_bytes(changed)
        self.assertEqual(2, self.install('--remove').returncode)
        self.assertEqual(changed, hook.read_bytes())

    def test_install_remove_does_not_touch_other_hook(self):
        self.copy_hook_sources()
        other = self.repo / '.git/hooks/pre-commit'
        metadata = self.repo / '.git/hooks/.harness-inventory-pre-commit.json'
        original = b'#!/bin/sh\nexit 9\n'
        other.write_bytes(original)
        metadata.write_bytes(b'existing metadata untouched\n')
        self.assertEqual(0, self.install().returncode)
        self.assertEqual(0, self.install('--remove').returncode)
        self.assertEqual(original, other.read_bytes())
        self.assertEqual(b'existing metadata untouched\n', metadata.read_bytes())


if __name__ == '__main__':
    unittest.main()
