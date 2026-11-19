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


<a id="work-survey"></a>
## 두 원문의 중복과 현재 링크·허용 조건을 대조한다

- 할 일: [본문](task.md#work-survey)

- 조치·판단: 실제 시작 안내와 상세 원문을 읽고 중복·링크 문자열·명시 표식·허용 범위·기존 변경을 대조했다.
- 확인: `{"판정": "충족", "관찰": "{\"assignment\": \"assignment.md\", \"revision\": \"r001\", \"start_link_targets\": [\"guide.md#record\"], \"guide_anchors\": [\"recording\"], \"guide_exists\": true, \"allowed_writes\": [\"start.md\"], \"user_delta\": {}}; 원문의 기록 위치 설명은 guide.md에서 보존한다."}`
- 잔여: 없음

<a id="work-decide"></a>
## 처음 읽는 사람·반복 사용자의 관점으로 A/B를 보완 비교하고 선택을 확인한다

- 할 일: [본문](task.md#work-decide)

- 조치·판단: A안은 "작업 상태와 상세 기록의 작성 방법을 확인하세요."와 상세 링크만 두어 설명의 원천을 guide.md에 모은다. B안은 짧은 설명 문장도 두지 않고 기록 방법 링크만 남긴다. 두 안 모두 기존 상세 두 문장의 중복을 줄이며 링크는 guide.md#recording으로 맞춘다. A는 처음 읽는 사람에게 링크에서 무엇을 확인할지 알려 주지만 안내 한 문장을 더 관리해야 한다. B는 반복 사용자의 빠른 접근과 간결함에 유리하지만 링크 이름만으로 기록의 범위를 짐작해야 한다. 두 안 모두 상세 원문은 guide.md 한 곳에 보존한다. 첫 방문자의 용도 이해까지 확보하는 A를 권고하되 지정한 모의 사용자 역할의 선택 전에는 확정하지 않는다. / 모의 사건을 입력으로 확인했다. 실제 사용자 승인이 아니다. 보존한 모의 사건: `{"id": "extra", "kind": "request", "value": "아직 고르지 않겠다. 처음 읽는 사람과 반복 사용자의 관점에서 더 비교해 달라."}` / 현재 조치: 처음 읽는 사람에게 A는 짧은 설명 한 문장이 현재 상태·상세 기록의 작성법을 찾는 목적을 알려 준다. B는 기록 방법 링크만 남겨 더 짧지만 방문자가 링크 이름만으로 용도를 짐작해야 한다. 반복 사용자에게 B는 매번 읽을 설명이 없는 간결한 탐색점이고 A의 한 문장은 이미 아는 정보일 수 있다. 두 안의 상세 목적지는 같고 모두 기존 상세 두 문장을 제거하므로 중복 감소에는 차이가 없다. 첫 방문자의 이해 비용까지 낮추는 A를 권고하지만 반복 사용자 중심을 택하면 B도 요구 범위 안의 대안이다. / 현재 조치: apply_files before required choice의 보호 조건을 실제 호출로 확인했다. / 모의 사건을 입력으로 확인했다. 실제 사용자 승인이 아니다. 보존한 모의 사건: `{"id": "extra", "kind": "request", "value": "아직 고르지 않겠다. 처음 읽는 사람과 반복 사용자의 관점에서 더 비교해 달라."}` 보존한 모의 사건: `{"id": "selection", "kind": "choice", "value": "A", "reason": "짧은 안내로 링크 용도를 알린다."}` / 현재 조치: 실제 전달받은 모의 선택과 후보의 적용 범위를 대조했다.
- 확인: `{"판정": "충족", "관찰": "실제 start.md는 guide.md#record를 가리키며 guide.md의 명시 표식은 recording이다. 현재의 두 설명은 guide.md와 중복된다. 상세 원문·표식은 보존한다. 후보의 후속 조건은 선택 응답·현재 편집 허용·원문 보존·반영 후 링크/문안 재대조다. / 전달받은 모의 사건: {\"id\": \"extra\", \"kind\": \"request\", \"value\": \"아직 고르지 않겠다. 처음 읽는 사람과 반복 사용자의 관점에서 더 비교해 달라.\"} / 현재 확인: 추가 요청의 두 관점으로 A/B를 실제 보완 비교했다. 권고와 선택은 별개이며 extra는 선택·편집 범위 변경이 아니다. 후속 조건은 별도 selection 응답, 상세 원문 보존, 실제 반영 후 두 설명 제거·한 문장/링크 조건과 표식 재대조다. / 현재 확인: Refused: [\"condition failed: choice\"]; 거절 전후 snapshot 동일, 파일 무변경. / 전달받은 모의 사건: {\"id\": \"selection\", \"kind\": \"choice\", \"value\": \"A\", \"reason\": \"짧은 안내로 링크 용도를 알린다.\"} / 현재 확인: 지정 주체 역할의 choice 사건과 이유를 확인했다. request/supply를 선택으로 해석하지 않았다."}`
- 잔여: 없음

<a id="work-apply"></a>
## 선택과 허용 조건을 갖춘 안내를 반영하고 관련 영향을 확인한다

- 할 일: [본문](task.md#work-apply)

- 조치·판단: 현재 원문·허용 범위·선택 근거를 확인한 뒤 start.md에 필요한 문안·링크 변경을 실제 저장했다.
- 확인: `{"판정": "충족", "관찰": "{\"write\": {\"written\": [\"start.md\"]}, \"actual_conditions\": {\"issues\": [], \"observations\": [{\"id\": \"link\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"layout\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"guide\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"choice\", \"satisfied\": true, \"observation\": \"\"}]}}; 변경하지 않은 원문과 기존 사용자 문장도 실제로 재대조했다."}`
- 잔여: 없음

<a id="work-close"></a>
## 전체 결과·보존·종료와 부모의 별도 수용 조건을 확인한다

- 할 일: [본문](task.md#work-close)

- 조치·판단: Task의 실제 결과·원문 보존·관리 연결·필수 확인과 종료 범위를 현재 배정에 대조했다. 시험 폴더 외의 반영·발급·커밋은 범위에 없다. / 현재 조치: complete_task 뒤 부모 원문이 동일함을 확인했다. check_parent로 부모의 실제 전체 조건과 전달본 대응을 독립 대조했다.
- 확인: `{"판정": "충족", "관찰": "{\"issues\": [], \"observations\": [{\"id\": \"link\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"layout\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"guide\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"choice\", \"satisfied\": true, \"observation\": \"\"}]} / 현재 확인: {\"task_check\": {\"issues\": [], \"observations\": [{\"id\": \"link\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"layout\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"guide\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"choice\", \"satisfied\": true, \"observation\": \"\"}]}, \"parent_unchanged_after_child\": true, \"parent_check\": {\"issues\": [], \"observations\": [{\"id\": \"child-result\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"link\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"layout\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"guide\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"choice\", \"satisfied\": true, \"observation\": \"\"}]}}"}`
- 잔여: 없음
