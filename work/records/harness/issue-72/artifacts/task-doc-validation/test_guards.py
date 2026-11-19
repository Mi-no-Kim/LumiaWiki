"""Regression checks for defects found by the separate code reviewer; no trial writes."""

from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
import workflow
import verify


class Guards(unittest.TestCase):
    def memory(self, documents, input_data=None):
        store = {str(Path('/memory') / key): value for key, value in documents.items()}
        ws = object.__new__(workflow.Workspace)
        ws.folder = Path('/memory/cases/example')
        ws.input = input_data or {}
        ws.path = lambda name: Path('/memory') / name
        ws.write = lambda name, value: store.__setitem__(str(ws.path(name)), value)
        original_text = workflow.text
        reader = lambda path: store[str(path)] if str(path) in store else original_text(path)
        return ws, store, reader

    def test_result_field_does_not_replace_work_confirmation(self):
        source = '- 확인: 할 일의 원래 확인\n<a id="result"></a>\n## 결과\n- 확인: 미실시\n'
        updated = workflow.replace_field(source, '확인', '실제 전체 판정')
        self.assertIn('- 확인: 할 일의 원래 확인', updated)
        self.assertIn('## 결과\n- 확인: 실제 전체 판정', updated)

    def test_refused_completion_does_not_partially_write(self):
        ws, store, reader = self.memory({'task.md': '<a id="result"></a>\n- 내용: 전\n- 확인: 전\n'})
        ws.check_task = lambda: {'issues': [], 'observations': []}
        before = deepcopy(store)
        with patch.object(workflow, 'text', reader), self.assertRaises(workflow.Refused):
            ws.complete_task()
        self.assertEqual(store, before)

    def test_unknown_work_cannot_supply_a_file_before_refusal(self):
        ws, store, reader = self.memory({'task.md': '<a id="work-known"></a>\n#### 기존 작업\n'},
                                       {'events': [{'id': 'supply', 'kind': 'supply', 'files': {'guide.md': 'new'}}]})
        before = deepcopy(store)
        with patch.object(workflow, 'text', reader), self.assertRaises(workflow.Refused):
            ws.use_event('supply', 'unknown')
        self.assertEqual(store, before)

    def test_revision_replaces_actual_newline_policy(self):
        parent = '- 적용 전달본: [기존](assignment.md)\n- 전달본 식별: r001\n```json\n{"criteria": []}\n```\n'
        event = {'id': 'revision', 'kind': 'revise', 'assignment_name': 'assignment-r002.md',
                 'assignment_text': 'new', 'revision': 'r002', 'parent_policy': {'criteria': [{'id': 'new'}]}}
        ws, store, reader = self.memory({'task.md': 'task', 'parent.md': parent}, {'events': [event]})
        ws._record_documents = lambda *args, **kwargs: {'task.md': kwargs['document'], 'execution.md': 'record'}
        with patch.object(workflow, 'text', reader):
            ws.use_event('revision', 'known')
        updated = store[str(ws.path('parent.md'))]
        self.assertEqual(workflow.block(updated), event['parent_policy'])
        self.assertIn('- 전달본 식별: r002', updated)

    def test_missing_revision_ids_do_not_compare_equal(self):
        ws, store, reader = self.memory({'task.md': 'task', 'parent.md': 'parent'})
        ws.active = lambda *args: Path('/memory/assignment.md')
        with patch.object(workflow, 'text', reader):
            self.assertIn('missing parent/task revision identifier', ws.revision_issues())

    def test_current_failed_work_and_remainder_block_completion(self):
        task = ('- 남은 결정: 없음\n- 막힌 조건: 없음\n<a id="work-known"></a>\n'
                '- [x] 수행·확인 완료\n')
        execution = '<a id="work-known"></a>\n- 확인: 필수 보존 확인 실패\n- 잔여: 미완료\n'
        ws, store, reader = self.memory({'task.md': task, 'execution.md': execution})
        ws.revision_issues = lambda: []
        ws.policy = lambda: {'criteria': [{'id': 'file'}]}
        ws.conditions = lambda conditions: {'issues': [], 'observations': []}
        with patch.object(workflow, 'text', reader), patch.object(Path, 'is_file', return_value=True):
            result = ws.check_task()
        self.assertIn('unverified work evidence: known', result['issues'])
        self.assertIn('unresolved work remainder: known', result['issues'])

    def test_record_defaults_incomplete_and_rejects_unresolved_done(self):
        task = ('- 수행 기록: 미생성\n<a id="work-known"></a>\n#### 준비\n'
                '- [ ] 수행·확인 완료\n- 수행 기록: execution.md#work-known — 미착수 예정 경로\n')
        ws, store, reader = self.memory({'task.md': task})
        with patch.object(workflow, 'text', reader):
            ws.record('known', '실제 준비', '관찰 중')
            self.assertIn('- [ ] 수행·확인 완료', store[str(ws.path('task.md'))])
            before = deepcopy(store)
            with self.assertRaises(workflow.Refused):
                ws.record('known', '아직 남음', '관찰', '미완료', done=True, verdict='충족')
            self.assertEqual(before, store)

    def test_nested_mock_receipt_is_preserved_as_an_event(self):
        event = {'id': 'choice', 'kind': 'choice', 'value': 'A'}
        value = json.dumps({'판정': '미확인', '관찰': json.dumps(event)}, ensure_ascii=False)
        self.assertIn(event, list(workflow.json_objects(value)))

    def test_missing_cli_case_is_not_success(self):
        tool = Path(__file__).resolve().parent / 'verify.py'
        run = tool.parent.parent / 'task-doc-suite-b'
        result = subprocess.run([sys.executable, '-B', str(tool), '--run', str(run), '--case', 'absent-case'],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)

    def test_parent_completion_is_checked_without_a_task(self):
        ws, store, reader = self.memory({'parent.md': '- 상태: 완료\n'})
        ws.snapshot = lambda: deepcopy(store)
        ws.creation_issues = lambda: ['missing result']
        ws.check_parent = lambda: {'issues': ['child required by parent']}
        with patch.object(verify, 'Workspace', return_value=ws), patch.object(verify, 'text', reader):
            result = verify.audit(Path('/memory/cases/example'))
        self.assertIn('child required by parent', result['issues'])

    def test_creation_reuses_answers_already_in_responsible_sources(self):
        source = '## 목적\n\n문서 대조\n\n## 기대 결과\n\n차이 목록\n\n## 조건\n```json\n{"criteria":[{"id":"result","kind":"exists","path":"result.md"}]}\n```\n'
        parent = '- 적용 전달본: [원본](assignment.md)\n- 생성 식별 확인: 확인 — P/T·경로·충돌 근거\n```json\n{"criteria":[]}\n```\n'
        ws, store, reader = self.memory({'parent.md': parent, 'assignment.md': source},
                                       {'goal': None, 'result': None, 'acceptance': None, 'creation': None})
        with patch.object(workflow, 'text', reader):
            self.assertEqual(ws.creation_issues(), [])

    def test_genuinely_missing_result_and_acceptance_remain_missing(self):
        source = '## 목적\n\n검토 준비\n\n## 기대 결과\n\n미정 — 담당 결과를 정하지 않았다.\n\n## 조건\n```json\n{"criteria":[]}\n```\n'
        parent = '- 적용 전달본: [원본](assignment.md)\n```json\n{"criteria":[]}\n```\n'
        ws, store, reader = self.memory({'parent.md': parent, 'assignment.md': source},
                                       {'goal':'검토 준비','result':None,'acceptance':None,
                                        'creation':{'parent':'P','task':'T','path_checked':True,'collision_checked':True}})
        with patch.object(workflow, 'text', reader):
            self.assertEqual(ws.creation_issues(), ['missing creation input: result','missing creation input: acceptance'])

    def test_only_source_events_are_preserved_as_events(self):
        event = {'id':'selection','kind':'choice','value':'A'}
        condition = {'id':'condition','kind':'choice','value':'A'}
        task = '- 수행 기록: 존재\n<a id="work-known"></a>\n#### 확인\n- [ ] 수행·확인 완료\n'
        execution = '<a id="work-known"></a>\n## 확인\n- 확인: ' + json.dumps([event,condition]) + '\n'
        ws, store, reader = self.memory({'task.md':task,'execution.md':execution}, {'initial_events':[event]})
        with patch.object(workflow,'text',reader),patch.object(Path,'exists',lambda p:p.name=='execution.md'):
            ws.record('known','현재 확인','실제 관찰')
        result=store[str(ws.path('execution.md'))]
        self.assertIn('selection', result)
        self.assertNotIn('condition', result)

    def test_receipt_code_context_keeps_raw_observation_unchanged(self):
        raw='실제 원문: [기록](guide.md#record)와 `인용`'
        encoded=workflow.inline_json({'판정':'충족','관찰':raw})
        self.assertEqual(workflow.parse_json_field(encoded)['관찰'],raw)
        self.assertNotIn('[기록]',verify.visible('- 확인: '+encoded))

    def test_unknown_creation_values_are_not_truthy_answers(self):
        source='## 목적\n\n검토 준비\n\n## 기대 결과\n\n미정 — 담당 결과 미확정\n\n## 조건\n```json\n{"criteria":[]}\n```\n'
        parent='- 적용 전달본: [원본](assignment.md)\n```json\n{"criteria":[]}\n```\n'
        ws,store,reader=self.memory({'parent.md':parent,'assignment.md':source},
            {'goal':'검토 준비','result':'미정','acceptance':'미확인',
             'creation':{'parent':'P','task':'T','path_checked':True,'collision_checked':True}})
        with patch.object(workflow,'text',reader):
            self.assertEqual(ws.creation_issues(),['missing creation input: result','missing creation input: acceptance'])


if __name__ == '__main__':
    unittest.main()
