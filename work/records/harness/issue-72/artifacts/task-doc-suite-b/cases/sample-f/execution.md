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


<a id="work-source"></a>
## 미제공 상세 원문을 확보하고 실제 내용을 대조한다

- 할 일: [본문](task.md#work-source)

- 조치·판단: 실제 시작 안내와 상세 원문을 읽고 중복·링크 문자열·명시 표식·허용 범위·기존 변경을 대조했다. / 모의 사건을 입력으로 확인했다. 실제 사용자 승인이 아니다. 보존한 모의 사건: {"id": "supply", "kind": "supply", "files": {"guide.md": "# 기록 안내\n\n<a id=\"recording\"></a>\n## 기록 방법\n\nTask 본문은 현재 상태와 계획을 관리합니다.\n자세한 수행 내용은 별도 수행 기록에 남깁니다.\n"}} / 현재 조치: 실제 시작 안내와 상세 원문을 읽고 중복·링크 문자열·명시 표식·허용 범위·기존 변경을 대조했다. / 현재 조치: 실제 시작 안내와 상세 원문을 읽고 중복·링크 문자열·명시 표식·허용 범위·기존 변경을 대조했다.
- 확인: {"판정": "충족", "관찰": "{\"assignment\": \"assignment.md\", \"revision\": \"r001\", \"start_link_targets\": [\"guide.md#record\"], \"guide_anchors\": [], \"guide_exists\": false, \"allowed_writes\": [], \"user_delta\": {}}; 원문의 기록 위치 설명은 guide.md에서 보존한다. / 전달받은 모의 사건: {\"id\": \"supply\", \"kind\": \"supply\", \"files\": {\"guide.md\": \"# 기록 안내\\n\\n<a id=\\\"recording\\\"></a>\\n## 기록 방법\\n\\nTask 본문은 현재 상태와 계획을 관리합니다.\\n자세한 수행 내용은 별도 수행 기록에 남깁니다.\\n\"}} / 현재 확인: {\"assignment\": \"assignment.md\", \"revision\": \"r001\", \"start_link_targets\": [\"guide.md#record\"], \"guide_anchors\": [\"recording\"], \"guide_exists\": true, \"allowed_writes\": [], \"user_delta\": {}}; 원문의 기록 위치 설명은 guide.md에서 보존한다. / 현재 확인: {\"assignment\": \"assignment.md\", \"revision\": \"r001\", \"start_link_targets\": [\"guide.md#record\"], \"guide_anchors\": [\"recording\"], \"guide_exists\": true, \"allowed_writes\": [], \"user_delta\": {}}; 원문의 기록 위치 설명은 guide.md에서 보존한다."}
- 잔여: 없음

<a id="work-assess"></a>
## 자료 확보와 편집 권한·선택 조건을 구별한다

- 할 일: [본문](task.md#work-assess)

- 조치·판단: apply_files before source의 보호 조건을 실제 호출로 확인했다. / 현재 조치: apply_files after source의 보호 조건을 실제 호출로 확인했다. / 현재 조치: 자료의 실제 부재는 해소했지만 allowed_writes는 여전히 비어 있고 choice 사건은 없다. 확보 원문을 읽어 recording 표식과 현재 record 링크의 차이를 확인했다. / 현재 조치: 현재 확보 자료와 allowed_writes·choice 근거를 다시 대조했다.
- 확인: {"판정": "충족", "관찰": "Refused: [\"write not allowed: start.md\", \"missing required source: guide.md\", \"condition failed: choice\"]; 거절 전후 snapshot 동일, 파일 무변경. / 현재 확인: Refused: [\"write not allowed: start.md\", \"condition failed: choice\"]; 거절 전후 snapshot 동일, 파일 무변경. / 현재 확인: 자료 제공을 새 편집 허용이나 사용자 선택으로 해석하지 않았다. 준비 결과와 남은 질문을 반환한다. / 현재 확인: guide.md는 실제 존재하고 recording 표식을 확인했다. allowed_writes는 빈 목록이며 선택 사건은 여전히 없다. 자료 제공과 권한·선택 구별 검수는 마쳤다."}
- 잔여: 없음 — 이 검수 할 일의 잔여는 없다. 전체 반영·선택·수용의 미충족은 Task 요약·결과에 남는다.

<a id="work-close"></a>
## 허용된 준비의 결과와 미충족을 보존해 반환한다

- 할 일: [본문](task.md#work-close)

- 조치·판단: complete_task with unavailable authority and choice의 보호 조건을 실제 호출로 확인했다.
- 확인: Refused: ["unresolved required decision", "unfinished planned work", "condition failed: link: guide.md#record", "condition failed: choice", "missing work evidence: close"]; 거절 전후 snapshot 동일, 파일 무변경.
- 잔여: 거절 이유가 해소된 뒤에만 의존 행동을 재개한다.
