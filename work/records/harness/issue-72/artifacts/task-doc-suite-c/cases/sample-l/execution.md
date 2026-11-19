# Task T — 가상 시험 수행 기록

- Task: [Task T](task.md#sequence)
- 기록 기준: [Task 공통 절차](../../../task-common-procedure-draft.md#recording-proposal)

<!-- execution-rule:recording
Task당 한 파일을 쓰고 이 주석은 머리말에 한 번만 둔다. 착수한 할 일은 구역 구조만 주석 없이 추가해 본문과 왕복 연결하고 실제 내용으로 채운다.
할 일의 태그·배정 조건에 따라 실제 조치·선택과 이유·근거를 남긴다. 파일 수정 없는 논의도 기록하고 제안·미결·합의·철회를 구별한다.
논의·사용자 결정은 실제 응답으로, AI 결정은 명시 위임·실제 선택으로 확인한다. 필수 논의를 생략하지 않는다.
확인은 계획·전달본을 참조하고 실제 대상·방법·관찰·판정·근거·한계를 남긴다. 변경본은 검증한 버전·범위를 식별하고 달라진 영향만 다시 확인한다.
진행·검수·수용에 필요한 결정은 Task에 결론·이유·조건·상세 링크를 남긴다. 공통 상세는 한 구역만 참조하며 잔여는 해당 할 일의 미해결·재개 조건이다.
보완·재시도는 같은 구역을 갱신한다. 식별자는 순서와 구별하고 삭제·분할·병합에도 수행·판단/실패 근거·당시 기준·본문 연결을 보존한다.
코드·diff·테스트 원문·명령별 로그를 복사·누적하지 않는다. 미발생 승인·결과나 단순 확인용 증명 파일을 만들지 않는다.
세부 작성 조건은 위 기록 기준을 따르고 생성 양식으로 돌아가지 않는다.
-->


<a id="work-recover"></a>
## 입력된 기존 작업의 실제 상태 대조·보완

- 할 일: [본문](task.md#work-recover)

- 조치·판단: 가상 사전 상태 입력이며 이 실행에서 과거에 수행한 사실이 아니다. / 현재 조치: 기존 Task·수행 기록과 work-recover/work-close 식별자는 초기화하지 않고 실제 입력·대상·부모 배정과 대조했다. 기존 가상 사전 상태는 이번 실행의 과거 수행 사실이 아니다. / 현재 조치: 실제 시작 안내와 상세 원문을 읽고 중복·링크 문자열·명시 표식·허용 범위·기존 변경을 대조했다. / 현재 조치: 저장된 링크 보정은 유지하고 아직 남은 중복 제거만 실제 수행한다. 추가 사용자 문장은 비충돌이므로 보존한다. / 현재 조치: 현재 원문·허용 범위·선택 근거를 확인한 뒤 start.md에 필요한 문안·링크 변경을 실제 저장했다.
- 확인: `{"판정": "충족", "관찰": "사전 확인 근거는 아직 없다. / 현재 확인: {\"initial_task_state\": \"중단\", \"initial_actual_check\": {\"issues\": [\"unfinished planned work\", \"condition failed: layout\", \"condition failed: detail-5\", \"condition failed: detail-6\", \"unverified work evidence: recover\", \"unresolved work remainder: recover\", \"missing work evidence: close\"], \"observations\": [{\"id\": \"link\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"layout\", \"satisfied\": false, \"observation\": \"\"}, {\"id\": \"guide\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"choice\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"user-note\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"detail-5\", \"satisfied\": false, \"observation\": \"\"}, {\"id\": \"detail-6\", \"satisfied\": false, \"observation\": \"\"}]}} / 현재 확인: {\"assignment\": \"assignment.md\", \"revision\": \"r001\", \"start_link_targets\": [\"guide.md#recording\"], \"guide_anchors\": [\"recording\"], \"guide_exists\": true, \"allowed_writes\": [\"start.md\"], \"user_delta\": {}}; 원문의 기록 위치 설명은 guide.md에서 보존한다. / 현재 확인: 링크는 이미 recording으로 저장돼 있으나 저장 뒤 검증 근거가 없었고 중복 설명은 아직 남아 있었다. 이전 다음 행동을 실제 잔여에 맞췄다. / 현재 확인: {\"write\": {\"written\": [\"start.md\"]}, \"actual_conditions\": {\"issues\": [], \"observations\": [{\"id\": \"link\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"layout\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"guide\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"choice\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"user-note\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"detail-5\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"detail-6\", \"satisfied\": true, \"observation\": \"\"}]}}; 변경하지 않은 원문과 기존 사용자 문장도 실제로 재대조했다."}`
- 잔여: 없음

<a id="work-close"></a>
## 전체 결과·종료 확인

- 할 일: [본문](task.md#work-close)

- 조치·판단: 기존 전체 결과·종료 체크와 실제 근거를 대조했다. 초기 미충족을 그대로 보존하고 목표 완료를 재판정한다. / 현재 조치: Task의 실제 결과·원문 보존·관리 연결·필수 확인과 종료 범위를 현재 배정에 대조했다. 시험 폴더 외의 반영·발급·커밋은 범위에 없다. / 현재 조치: complete_task 뒤 부모 원문이 동일함을 확인했다. check_parent로 부모의 실제 전체 조건과 전달본 대응을 독립 대조했다.
- 확인: `{"판정": "충족", "관찰": "{\"issues\": [\"unfinished planned work\", \"condition failed: layout\", \"condition failed: detail-5\", \"condition failed: detail-6\", \"unverified work evidence: recover\", \"unresolved work remainder: recover\", \"missing work evidence: close\"], \"observations\": [{\"id\": \"link\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"layout\", \"satisfied\": false, \"observation\": \"\"}, {\"id\": \"guide\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"choice\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"user-note\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"detail-5\", \"satisfied\": false, \"observation\": \"\"}, {\"id\": \"detail-6\", \"satisfied\": false, \"observation\": \"\"}]} / 현재 확인: {\"issues\": [], \"observations\": [{\"id\": \"link\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"layout\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"guide\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"choice\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"user-note\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"detail-5\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"detail-6\", \"satisfied\": true, \"observation\": \"\"}]} / 현재 확인: {\"task_check\": {\"issues\": [], \"observations\": [{\"id\": \"link\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"layout\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"guide\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"choice\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"user-note\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"detail-5\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"detail-6\", \"satisfied\": true, \"observation\": \"\"}]}, \"parent_unchanged_after_child\": true, \"parent_check\": {\"issues\": [], \"observations\": [{\"id\": \"child-result\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"link\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"layout\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"guide\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"choice\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"user-note\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"detail-5\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"detail-6\", \"satisfied\": true, \"observation\": \"\"}]}}"}`
- 잔여: 없음
