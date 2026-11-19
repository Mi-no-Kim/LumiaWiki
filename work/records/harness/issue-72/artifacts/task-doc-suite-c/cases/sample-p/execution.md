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

- 조치·판단: 가상 사전 상태 입력이며 이 실행에서 과거에 수행한 사실이 아니다. / 현재 조치: 기존 Task·수행 기록과 work-recover/work-close 식별자는 초기화하지 않고 실제 입력·대상·부모 배정과 대조했다. 기존 가상 사전 상태는 이번 실행의 과거 수행 사실이 아니다. / 현재 조치: 실제 시작 안내와 상세 원문을 읽고 중복·링크 문자열·명시 표식·허용 범위·기존 변경을 대조했다. / 현재 조치: apply_files against overlapping user change의 보호 조건을 실제 호출로 확인했다.
- 확인: `{"판정": "불충족", "관찰": "사전 확인 근거는 아직 없다. / 현재 확인: {\"initial_task_state\": \"진행 중\", \"initial_actual_check\": {\"issues\": [\"unfinished planned work\", \"condition failed: link: guide.md#record\", \"condition failed: layout\", \"unverified work evidence: recover\", \"unresolved work remainder: recover\", \"missing work evidence: close\"], \"observations\": [{\"id\": \"link\", \"satisfied\": false, \"observation\": \"guide.md#record\"}, {\"id\": \"layout\", \"satisfied\": false, \"observation\": \"\"}, {\"id\": \"guide\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"choice\", \"satisfied\": true, \"observation\": \"\"}]}} / 현재 확인: {\"assignment\": \"assignment.md\", \"revision\": \"r001\", \"start_link_targets\": [\"guide.md#record\"], \"guide_anchors\": [\"recording\"], \"guide_exists\": true, \"allowed_writes\": [\"start.md\"], \"user_delta\": {\"start.md\": \"# 시작 안내\\n\\n사용자 수정: 이 설명은 원문을 유지하며 별도 합의 전 줄이지 마세요.\\n자세한 수행 내용은 별도 수행 기록에 남깁니다.\\n\\n[기록 방법 보기](guide.md#record)\\n\"}}; 원문의 기록 위치 설명은 guide.md에서 보존한다. / 현재 확인: Refused: [\"concurrent edit conflict: start.md\"]; 거절 전후 snapshot 동일, 파일 무변경."}`
- 잔여: 거절 이유가 해소된 뒤에만 의존 행동을 재개한다.

<a id="work-close"></a>
## 전체 결과·종료 확인

- 할 일: [본문](task.md#work-close)

- 조치·판단: 기존 전체 결과·종료 체크와 실제 근거를 대조했다. 초기 미충족을 그대로 보존하고 목표 완료를 재판정한다. / 현재 조치: complete_task with user conflict unresolved의 보호 조건을 실제 호출로 확인했다. / 현재 조치: accept_parent with user conflict unresolved의 보호 조건을 실제 호출로 확인했다.
- 확인: `{"판정": "불충족", "관찰": "{\"issues\": [\"unfinished planned work\", \"condition failed: link: guide.md#record\", \"condition failed: layout\", \"unverified work evidence: recover\", \"unresolved work remainder: recover\", \"missing work evidence: close\"], \"observations\": [{\"id\": \"link\", \"satisfied\": false, \"observation\": \"guide.md#record\"}, {\"id\": \"layout\", \"satisfied\": false, \"observation\": \"\"}, {\"id\": \"guide\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"choice\", \"satisfied\": true, \"observation\": \"\"}]} / 현재 확인: Refused: [\"unresolved required decision\", \"unfinished planned work\", \"condition failed: link: guide.md#record\", \"condition failed: layout\", \"unverified work evidence: recover\", \"unresolved work remainder: recover\", \"unverified work evidence: close\", \"unresolved work remainder: close\"]; 거절 전후 snapshot 동일, 파일 무변경. / 현재 확인: Refused: [\"condition failed: child-result\", \"condition failed: link: guide.md#record\", \"condition failed: layout\"]; 거절 전후 snapshot 동일, 파일 무변경."}`
- 잔여: 거절 이유가 해소된 뒤에만 의존 행동을 재개한다.
