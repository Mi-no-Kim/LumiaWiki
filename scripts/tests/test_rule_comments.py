"""Frozen legacy enrollment and automatic protection of real new record paths."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from harness_inventory import Candidate
from rule_comments import ALL_PROFILES, PLAN_PROFILES, PROFILES, POLICY, comments, inspect, plan_fingerprint, record_names

LEGACY = 'work/records/harness/issue-1/issue.md'
ISSUE = 'work/records/issues/issue-2/issue.md'
TASK = 'work/records/issues/issue-2/task-001.md'
EXECUTION = 'work/records/issues/issue-2/artifacts/task-001-execution.md'
PLAN = 'work/records/issues/issue-2/artifacts/task-001-plan.md'
ASSIGNMENT = 'work/records/issues/issue-2/artifacts/task-001-assignment.md'
VALID_ASSIGNMENT = (
    '## 목적\n\n기록을 확인한다.\n\n## 기대 결과\n\n확인 근거를 남긴다.\n\n'
    '## 이미 정해진 조건\n\n없음\n\n## Task에서 결정할 사항\n\n미정\n\n'
    '## 완료 조건과 확인 방법\n\n- 완료 조건: 결과를 기록한다.\n  - 확인 방법: 실제 기록과 대조한다.\n'
)


def values(profile):
    prefix, rules, _ = ALL_PROFILES[profile]
    return {r: f'<!-- {prefix}:{r}\nKeep {r}.\n-->' for r in rules}


def body(profile, state='예정'):
    summary = '' if profile == 'execution' else f'## 현재 요약\n\n- 상태: {state}\n\n'
    return '# Fictional record\n\n' + summary + '\n\n'.join(values(profile).values()) + '\n'


class CurrentRecordTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='current-record-rules-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.env = {**os.environ, 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
                    'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONUTF8': '1'}
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fictional record test')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'core.autocrlf', 'false')
        self.policy = {'schema': 1, 'legacyRecords': [LEGACY], 'profiles': {}, 'targets': [], 'revisions': []}
        for profile, (_, _, source) in PROFILES.items():
            self.write(source, '# Source\n\n```markdown\n' + body(profile) + '```\n')
            self.policy['profiles'][profile] = {'source': source, 'comments': values(profile)}
            self.policy['targets'].append({'path': source, 'profile': profile, 'mode': 'template'})
        self.write(LEGACY, '# Existing record without new comments\n')
        self.save()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8', newline='')

    def save(self):
        self.write(POLICY, json.dumps(self.policy, ensure_ascii=False))

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], env=self.env, check=True, capture_output=True)

    def errors(self, candidate='work', previous=None):
        view = Candidate(candidate, cwd=self.root, seconds=15)
        old = Candidate(previous, cwd=self.root, seconds=15) if previous else None
        return inspect(view, old)

    def commit(self):
        self.git('add', '--', 'harness', 'work')
        self.git('-c', 'core.hooksPath=' + str(self.root / 'no-hooks'), 'commit', '-qm', 'Fixture adoption')

    def adopt_separate_plans(self, compatible=()):
        self.policy.update(schema=2, compatibleTasks=list(compatible), taskPlanMigrations={})
        for profile, (_, _, source) in PLAN_PROFILES.items():
            self.write(source, '# Source\n\n```markdown\n' + body(profile) + '```\n')
            self.policy['profiles'][profile] = {'source': source, 'comments': values(profile)}
            self.policy['targets'].append({'path': source, 'profile': profile, 'mode': 'template'})
        self.save()

    def write_assignment(self, number='001', issue_evidence=''):
        self.write(ASSIGNMENT.replace('001', number), VALID_ASSIGNMENT)
        self.write(ISSUE, body('issue') + issue_evidence + f'\n<a id="assignment-{number}"></a>\n'
                   f'\n- 전달사항: [확정 전달사항](artifacts/task-{number}-assignment.md) (`r001`).\n')

    def separate_task(self, plan='미작성', state='예정', approved_plan=None):
        text = (body('task-with-plan', state) + '\n- 상세 계획: ' + plan
                + '\n- 적용 전달본: [r001](artifacts/task-001-assignment.md)\n'
                + '- 현재 진행 위치: [배정](#assignment)\n- 다음 행동: 상세 계획을 작성한다.\n'
                + '- 전달본 식별: `r001`\n- 기준 기록: [배정](issue.md#assignment-001)\n'
                + '- 현재 합의: 기록 대조를 진행한다.\n\n<a id="assignment"></a>\n<a id="summary"></a>\n')
        if approved_plan is not None:
            text += ('\n<a id="plan-agreement"></a>\n'
                     + '- 합의 근거: 사용자가 r001의 계획에 동의했다.\n'
                     + '- 계획 지문: ' + plan_fingerprint(approved_plan.encode()) + '\n')
        return text

    def plan_body(self, agreed='합의 — [근거](../task-001.md#plan-agreement)', checked=' ', evidence='미생성'):
        return (
            values('task-plan')['recording'] + '\n'
            '- Task: [Task](../task-001.md#summary)\n'
            '- 적용 전달본: [r001](task-001-assignment.md)\n'
            f'- 계획 합의: {agreed}\n'
            '\n<a id="stage-verify"></a>\n\n## 1. stage-verify — 확인\n\n'
            '- 태그: 검수\n'
            f'- [{checked}] 단계 완료\n'
            '- 선행 입력: 없음\n- 완료 기준: 결과\n- 확인: 대조\n'
            '- 확인·결정 지점: 없음\n'
            f'- 수행 기록: {evidence}\n\n'
            '### 세부 작업\n\n1. 실제 결과와 기준을 대조한다.\n'
        )

    def test_only_new_tasks_require_separate_plan_format(self):
        self.write(TASK, body('task'))
        self.commit()
        self.adopt_separate_plans((TASK,))
        self.assertEqual([], self.errors(previous='HEAD'))
        new_task = TASK.replace('001', '002')
        self.write(new_task, body('task'))
        self.assertTrue(any('separate-task-rule' in error for error in self.errors(previous='HEAD')))
        self.write(new_task, self.separate_task().replace('task-001-assignment.md', 'task-002-assignment.md')
                   .replace('issue.md#assignment-001', 'issue.md#assignment-002'))
        self.write_assignment('002')
        self.assertEqual([], self.errors(previous='HEAD'))
        self.commit()
        self.policy['compatibleTasks'].append(new_task)
        self.save()
        self.write(new_task, body('task'))
        self.assertTrue(any('adoption and migration' in error for error in self.errors(previous='HEAD')))

    def test_separate_plan_link_order_and_completion_are_checked(self):
        self.adopt_separate_plans()
        linked = '[계획](artifacts/task-001-plan.md)'
        self.write(TASK, self.separate_task(linked))
        self.assertTrue(any('linked Task plan is missing' in error for error in self.errors()))
        self.write_assignment()
        self.write(PLAN, self.plan_body(agreed='제안'))
        self.assertEqual([], self.errors())
        self.write(TASK, self.separate_task(linked) + '\n- [x] 단계 완료\n')
        self.assertTrue(any('only in the plan' in error for error in self.errors()))
        self.write(TASK, self.separate_task(linked).replace('[배정](#assignment)', '[단계](artifacts/task-002-plan.md#stage-verify)'))
        self.assertTrue(any('current position must link' in error for error in self.errors()))
        self.write(TASK, self.separate_task(linked))
        self.write(PLAN, self.plan_body().replace('## 1.', '## 2.'))
        self.assertTrue(any('sequential stage order' in error for error in self.errors()))
        anchor = '<a id="stage-verify"></a>'
        self.write(PLAN, self.plan_body().replace(anchor, '') + '\n' + anchor + '\n')
        self.assertTrue(any('unique stage anchors' in error for error in self.errors()))
        self.write(PLAN, self.plan_body(checked='x'))
        self.assertTrue(any('confirmed execution evidence' in error for error in self.errors()))
        completed = self.plan_body(checked='x', evidence='[근거](task-001-execution.md#work-verify)')
        self.write(PLAN, completed)
        self.write(EXECUTION, body('execution') + '\n<a id="work-verify"></a>\n'
                   '- 할 일: [단계](task-001-plan.md#stage-verify)\n- 확인: 단계 결과를 검수했다.\n')
        self.write(TASK, self.separate_task(linked, state='완료', approved_plan=completed))
        self.assertEqual([], self.errors())
        self.write(PLAN, self.plan_body())
        self.assertTrue(any('completion is missing or inconsistent' in error for error in self.errors()))

    def test_individual_migration_needs_approval_and_preserves_state(self):
        self.write(TASK, body('task', '진행 중'))
        self.adopt_separate_plans((TASK,))
        self.commit()
        self.write(TASK, self.separate_task(state='진행 중'))
        self.assertTrue(any('task-rule:' in error for error in self.errors(previous='HEAD')))
        self.policy['taskPlanMigrations'][TASK] = ISSUE + '#approved-migration'
        self.save()
        with self.assertRaisesRegex(ValueError, 'Approval record reference'):
            self.errors(previous='HEAD')
        self.write_assignment(issue_evidence='\n<a id="approved-migration"></a>\n')
        self.assertEqual([], self.errors(previous='HEAD'))
        self.write(TASK, self.separate_task(state='예정'))
        self.assertTrue(any('must preserve the current state' in error for error in self.errors(previous='HEAD')))

    def test_individual_migration_preserves_completed_work_and_original_anchors(self):
        original = (
            body('task', '진행 중') + '\n<a id="work-previous"></a>\n\n'
            '#### 확인 완료\n\n- [x] 수행·확인 완료\n'
            '- 수행 기록: [근거](artifacts/task-001-execution.md#work-previous).\n'
        )
        evidence = body('execution') + '\n<a id="work-previous"></a>\n'
        self.write(TASK, original)
        self.write(EXECUTION, evidence + '- 할 일: [기존 할 일](../task-001.md#work-previous)\n')
        self.adopt_separate_plans((TASK,))
        self.commit()
        self.policy['taskPlanMigrations'][TASK] = ISSUE + '#approved-migration'
        self.save()
        self.write_assignment(issue_evidence='\n<a id="approved-migration"></a>\n')
        linked = '[계획](artifacts/task-001-plan.md)'
        self.write(TASK, self.separate_task(linked, '진행 중'))
        self.write(PLAN, self.plan_body())
        errors = self.errors(previous='HEAD')
        self.assertTrue(any('preserve completed work' in error for error in errors))
        self.assertTrue(any('preserve existing Task work anchors' in error for error in errors))
        self.write(TASK, self.separate_task(linked, '진행 중') + '\n<a id="work-previous"></a>\n')
        self.write(EXECUTION, evidence + '\n<a id="work-new"></a>\n'
                   '- 할 일: [대체 단계](task-001-plan.md#stage-verify)\n')
        self.write(PLAN, self.plan_body(checked='x', evidence='[대체 근거](task-001-execution.md#work-new)'))
        self.assertTrue(any('preserve completed work' in error for error in self.errors(previous='HEAD')))
        completed = self.plan_body(checked='x', evidence='[근거](task-001-execution.md#work-previous)')
        self.write(PLAN, completed)
        self.assertTrue(any('confirmed execution evidence' in error for error in self.errors(previous='HEAD')))
        self.write(EXECUTION, evidence + '- 할 일: [단계](task-001-plan.md#stage-verify)\n'
                   '- 확인: 기존 수행 근거를 대조했다.\n')
        self.write(TASK, self.separate_task(linked, '진행 중', approved_plan=completed)
                   + '\n<a id="work-previous"></a>\n')
        self.assertEqual([], self.errors(previous='HEAD'))

    def test_new_task_without_plan_still_requires_assignment_and_next_action(self):
        self.adopt_separate_plans()
        valid = self.separate_task()
        self.write_assignment()
        self.write(TASK, valid)
        self.assertEqual([], self.errors())
        missing = '\n'.join(line for line in valid.splitlines()
                            if not line.startswith(('- 적용 전달본:', '- 다음 행동:'))) + '\n'
        self.write(TASK, missing)
        errors = self.errors()
        self.assertTrue(any('one existing assignment' in error for error in errors))
        self.assertTrue(any('one next action' in error for error in errors))

    def test_assignment_contents_and_current_summary(self):
        self.adopt_separate_plans()
        self.write_assignment()
        valid = self.separate_task()
        self.write(TASK, valid)
        self.assertEqual([], self.errors())
        self.write(ASSIGNMENT, '')
        self.assertTrue(any('five input sections' in error for error in self.errors()))
        self.write(ASSIGNMENT, VALID_ASSIGNMENT.replace('  - 확인 방법: 실제 기록과 대조한다.\n', ''))
        self.assertTrue(any('confirmation method' in error for error in self.errors()))
        for valid_value, incomplete in (
            ('없음', '- 조건: '),
            ('미정', '- 결정할 사항: '),
            ('기록을 확인한다.', '[원문](issue.md)'),
        ):
            self.write(ASSIGNMENT, VALID_ASSIGNMENT.replace(valid_value, incomplete))
            self.assertTrue(any('section is missing required content' in error for error in self.errors()))
        self.write(ASSIGNMENT, VALID_ASSIGNMENT.replace('없음', '`없음`').replace('미정', '`미정`'))
        self.assertEqual([], self.errors())
        self.write(ASSIGNMENT, VALID_ASSIGNMENT)
        self.write(TASK, valid.replace('기록 대조를 진행한다.', '[배정](artifacts/task-001-assignment.md)'))
        self.assertTrue(any('summary beyond links' in error for error in self.errors()))
        self.write(TASK, valid.replace('식별: `r001`', '식별: `r002`'))
        self.assertTrue(any('revision differs' in error for error in self.errors()))
        self.write(TASK, valid)
        self.write(ISSUE, (self.root / ISSUE).read_text(encoding='utf-8').replace('(`r001`).', '(`r002`).'))
        self.assertTrue(any('same revision' in error for error in self.errors()))

    def test_plan_fingerprint_binds_agreed_content_but_not_progress(self):
        self.adopt_separate_plans()
        self.write_assignment()
        linked = '[계획](artifacts/task-001-plan.md)'
        agreed = self.plan_body()
        self.write(TASK, self.separate_task(linked, approved_plan=agreed))
        self.write(PLAN, self.plan_body(agreed='합의'))
        self.assertTrue(any('link to the owning Task agreement' in error for error in self.errors()))
        self.write(TASK, self.separate_task(linked))
        self.write(PLAN, agreed)
        self.assertTrue(any('one recorded plan fingerprint' in error for error in self.errors()))
        approved = self.separate_task(linked, approved_plan=agreed)
        self.write(TASK, approved.replace('- 합의 근거: 사용자가 r001의 계획에 동의했다.\n', ''))
        self.assertTrue(any('agreement response or reference' in error for error in self.errors()))
        self.write(TASK, approved)
        self.assertEqual([], self.errors())
        self.write(PLAN, agreed.replace('완료 기준: 결과', '완료 기준: 다른 결과'))
        self.assertTrue(any('fingerprint differs' in error for error in self.errors()))
        progress = self.plan_body(checked='x', evidence='[근거](task-001-execution.md#work-verify)')
        self.write(PLAN, progress)
        evidence = (body('execution') + '\n<a id="work-verify"></a>\n'
                    '- 할 일: [단계](task-001-plan.md#stage-verify)\n')
        self.write(EXECUTION, evidence)
        self.assertTrue(any('recorded verification notes' in error for error in self.errors()))
        self.write(EXECUTION, evidence + '- 확인: 단계 결과를 검수했다.\n')
        self.assertEqual([], self.errors())
        self.write(PLAN, self.plan_body(agreed='제안'))
        self.assertTrue(any('execution requires an agreed plan' in error for error in self.errors()))

    def test_unchanged_historical_verdict_keeps_its_existing_evidence(self):
        self.adopt_separate_plans()
        self.write_assignment()
        linked = '[계획](artifacts/task-001-plan.md)'
        historical = self.plan_body(agreed='합의', checked='x', evidence='[근거](task-001-execution.md#work-verify)')
        self.write(PLAN, historical)
        self.write(EXECUTION, body('execution') + '\n<a id="work-verify"></a>\n'
                   '- 할 일: [단계](task-001-plan.md#stage-verify)\n')
        self.write(TASK, self.separate_task(linked, state='완료'))
        self.git('add', '--', PLAN)
        self.commit()
        self.assertEqual([], self.errors(previous='HEAD'))
        self.write(PLAN, historical.replace('완료 기준: 결과', '완료 기준: 다른 결과'))
        self.assertTrue(any('link to the owning Task agreement' in error for error in self.errors(previous='HEAD')))

    def test_existing_untracked_record_is_exempt_without_edit(self):
        before = (self.root / LEGACY).read_bytes()
        self.assertIn(LEGACY, record_names(Candidate('work', cwd=self.root)))
        self.assertEqual([], self.errors())
        self.assertEqual(before, (self.root / LEGACY).read_bytes())

    def test_new_issue_task_and_execution_are_automatically_enrolled(self):
        for name, profile in [(ISSUE, 'issue'), (TASK, 'task'), (EXECUTION, 'execution')]:
            self.write(name, body(profile))
        self.assertEqual([], self.errors())
        for name, profile in [(ISSUE, 'issue'), (TASK, 'task'), (EXECUTION, 'execution')]:
            self.write(name, '# Entire comment set removed\n')
            self.assertTrue(any(name in error for error in self.errors()))
            self.write(name, body(profile))

    def test_phase_and_harness_issue_locations_are_also_automatic(self):
        for parent in ['phase-001/issue-3', 'harness/issue-4']:
            name = 'work/records/' + parent + '/issue.md'
            self.write(name, '# Missing protected rules\n')
            self.assertTrue(any(name in error for error in self.errors()))
            self.write(name, body('issue'))
        self.assertEqual([], self.errors())

    def test_completed_new_record_stays_protected(self):
        self.write(ISSUE, body('issue', '완료'))
        self.assertEqual([], self.errors())
        self.write(ISSUE, body('issue', '완료').replace(values('issue')['start'], ''))
        self.assertTrue(self.errors())

    def test_current_five_states_and_legacy_values_are_separate(self):
        for state in ['예정', '진행 중', '중단', '완료', '취소']:
            self.write(TASK, body('task', state))
            self.assertEqual([], self.errors(), state)
        for state in ['검증 중', '대기', '보류', '미정']:
            self.write(TASK, body('task', state))
            self.assertTrue(any('current state' in e for e in self.errors()), state)
        self.write(TASK, body('task'))
        self.write(LEGACY, '## 현재 요약\n- 상태: 검증 중\n')
        self.assertEqual([], self.errors())

    def test_quoted_or_duplicate_state_is_not_a_valid_current_summary(self):
        raw = body('task').replace('- 상태: 예정', '```text\n- 상태: 예정\n```')
        self.write(TASK, raw)
        self.assertTrue(self.errors())
        self.write(TASK, body('task').replace('- 상태: 예정', '- 상태: 예정\n- 상태: 완료'))
        self.assertTrue(self.errors())
        self.write(TASK, body('task').replace('- 상태: 예정', '- 상태:\n예정'))
        self.assertTrue(self.errors())

    def test_state_examples_in_html_attributes_and_raw_text_are_not_summaries(self):
        from rule_comments import check_state
        summary = '## 현재 요약\n- 상태: 예정\n'
        for wrapper in ['<div title="\n{}">', '<xmp>\n{}</xmp>', '<textarea>\n{}</textarea>', '<![CDATA[\n{}]]>', '```markdown\n{}\n```', '`\n{}`']:
            self.assertTrue(check_state(wrapper.format(summary).encode('utf-8')), wrapper)

    def test_declared_previous_issue_policy_cannot_disappear(self):
        self.policy['legacyIssuePolicy'] = 'harness/issue-rule-comments.json'
        self.save()
        with self.assertRaises(ValueError):
            self.errors()

    def test_current_cli_runs_without_optional_legacy_policy_or_records(self):
        # The formal configuration must work in a fresh checkout without the
        # old local policy or its untracked historical attachments.
        (self.root / LEGACY).unlink()
        for candidate in ['work', 'index']:
            if candidate == 'index':
                self.git('add', '--', 'harness')
            result = subprocess.run([sys.executable, '-B', '-X', 'utf8',
                                     str(SCRIPTS / 'check-rule-comments.py'),
                                     '--candidate', candidate], cwd=self.root,
                                    env=self.env, capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(0, result.returncode, result.stderr)

    def test_cli_keeps_previously_present_issue_policy_protection(self):
        old = 'harness/issue-rule-comments.json'
        self.write(old, '{}')
        self.commit()
        (self.root / old).unlink()
        result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(SCRIPTS / 'check-rule-comments.py'), '--candidate', 'work'], cwd=self.root, env=self.env, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(2, result.returncode)
        self.assertIn('Previously protected Issue policy', result.stderr)

    def test_comment_changes_duplicates_nested_and_quotes(self):
        for profile in PROFILES:
            for rule, value in values(profile).items():
                for replacement in ['', value.replace('Keep', 'Alter'), value * 2, '<!-- outer\n' + value + '\n-->']:
                    with self.subTest(profile=profile, rule=rule):
                        source = PROFILES[profile][2]
                        self.write(source, '# Source\n```markdown\n' + body(profile).replace(value, replacement) + '```\n')
                        self.assertTrue(self.errors())
                        self.write(source, '# Source\n```markdown\n' + body(profile) + '```\n')
            quoted = '```markdown\n' + body(profile) + '```\n'
            self.assertEqual(({}, []), comments(quoted.encode(), profile))

    def test_code_and_raw_html_do_not_supply_live_rules(self):
        for wrapper in ['```markdown\n{}\n```', '<textarea>{}</textarea>', '<div title="{}"></div>']:
            self.assertEqual(({}, []), comments(wrapper.format(body('task')).encode(), 'task'))

    def test_index_uses_staged_policy_and_bytes_not_worktree(self):
        self.write(TASK, body('task'))
        self.git('add', '--', 'harness', 'work')
        self.write(TASK, '# Broken worktree\n')
        self.assertEqual([], self.errors('index'))
        self.assertTrue(self.errors('work'))
        self.git('add', '--', TASK)
        self.write(TASK, body('task'))
        self.assertTrue(self.errors('index'))
        self.assertEqual([], self.errors('work'))

    def test_frozen_legacy_list_cannot_capture_new_records(self):
        self.commit()
        self.write(ISSUE, '# Not a valid current issue\n')
        self.policy['legacyRecords'].append(ISSUE)
        self.save()
        self.assertTrue(any('frozen legacy list changed' in e for e in self.errors(previous='HEAD')))

    def test_profile_reset_or_source_target_removal_is_rejected(self):
        self.commit()
        self.policy['profiles']['task']['comments']['start'] = values('task')['start'].replace('Keep', 'Change')
        self.save()
        self.assertTrue(any('baseline changed' in e for e in self.errors(previous='HEAD')))
        self.policy['targets'] = self.policy['targets'][1:]
        self.save()
        with self.assertRaises(ValueError):
            self.errors(previous='HEAD')

    def test_deleted_new_record_is_not_silently_unenrolled(self):
        self.write(ISSUE, body('issue'))
        self.commit()
        (self.root / ISSUE).unlink()
        self.assertTrue(any('protected file is missing' in e for e in self.errors(previous='HEAD')))

    def test_reference_mode_is_confined_to_explicit_examples(self):
        name = 'harness/examples/task-reference.md'
        self.write(name, body('task', '<미확정 참조>'))
        self.policy['targets'].append({'path': name, 'profile': 'task', 'mode': 'reference'})
        self.save()
        self.assertEqual([], self.errors())
        self.policy['targets'][-1]['path'] = TASK
        self.save()
        with self.assertRaises(ValueError):
            self.errors()

    def test_unknown_artifacts_and_phase_bodies_are_not_records(self):
        for name in ['work/records/phase-001/phase.md', 'work/records/issues/issue-2/artifacts/task-doc-suite/cases/sample/task.md', 'work/records/issues/issue-2/artifacts/task-input.md']:
            self.write(name, '# Historical input\n')
        self.assertEqual([], self.errors())

    def test_unsafe_legacy_paths_and_directory_wildcards_are_invalid(self):
        for value in ['work/records/harness/**', '../outside.md', 'harness-design/issue.md', 'work/records/harness/issue-1/../issue.md']:
            self.policy['legacyRecords'] = [value]
            self.save()
            with self.assertRaises(ValueError):
                self.errors()

    def test_scoped_user_revision_is_exact_and_needs_real_anchor(self):
        self.write(TASK, body('task'))
        approval = 'work/records/issues/issue-2/artifacts/revision.md'
        self.write(approval, '<a id="decision"></a>\nActual fixture instruction\n')
        before = values('task')['start']
        replacement = before.replace('Keep', 'Revise')
        self.write(TASK, body('task').replace(before, replacement))
        self.policy['revisions'] = [{'path':TASK,'profile':'task','rule':'start','before':before,'replacement':replacement,'approval':approval+'#decision'}]
        self.save()
        self.assertEqual([], self.errors())
        self.policy['revisions'][0]['approval'] = approval + '#missing'
        self.save()
        with self.assertRaises(ValueError):
            self.errors()

    def test_cli_and_hook_feedback_use_the_shared_policy(self):
        self.write(TASK, '# No protected comments\n')
        script = SCRIPTS / 'check-rule-comments.py'
        result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(script), '--candidate', 'work'], cwd=self.root, env=self.env, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(2, result.returncode, result.stderr)
        event = json.dumps({'hook_event_name':'PostToolUse','tool_name':'apply_patch'})
        result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(script), '--hook'], cwd=self.root, env=self.env, input=event, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(0, result.returncode)
        self.assertEqual('block', json.loads(result.stdout)['decision'])
        self.assertIn('task-rule:', json.loads(result.stdout)['reason'])


if __name__ == '__main__':
    unittest.main()
