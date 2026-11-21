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


<a id="work-compare"></a>
## 두 원문을 읽고 수동 대조와 로컬 검사 방법을 비교한다

- 할 일: [본문](task.md#work-compare)

- 조치·판단: 수동 방법은 두 원문의 상대 경로와 recording 표식을 읽어 대조한다. 준비 비용이 작고 의미·중복·현재 두 문서 범위를 함께 볼 수 있지만 반복 재현과 누락 방지는 검토자에 의존한다. 로컬 검사 방법은 경로·표식을 자동 추출해 대상 존재를 검사하므로 다수 문서의 반복 재현에 유리하다. 반면 검사기 준비·오탐 처리·실행 환경 유지가 필요하고 문안의 의미나 중복까지 결정하지 못한다. 판단 기준은 두 문서라는 현재 범위, 준비 비용, 재현 요구, 의미 확인 가능성이다. 현 범위에서는 수동을 권고하되 지정 주체 응답 전에는 선정하지 않는다.
- 확인: `{"판정": "충족", "관찰": "실제 원문을 읽어 start.md의 guide.md#record와 guide.md의 recording 표식 차이를 확인했다. 두 설명 문장도 중복된다. 이 비교의 후속 조건: 범위가 늘거나 반복 재현 요구가 생기면 로컬 방법의 준비·허용을 별도 논의한다. 현재 파일 수정·검사기 작성·실행은 하지 않았다."}`
- 잔여: 없음

<a id="work-decide"></a>
## 비교 기준과 후속 조건을 제시하고 방법 선택 응답을 확인한다

- 할 일: [본문](task.md#work-decide)

- 조치·판단: 수동/로컬의 비교·권고·후속 조건과 현재 허용 범위를 제시하고 지정 주체에 선택을 질문했다. / 모의 사건을 입력으로 확인했다. 실제 사용자 승인이 아니다. 보존한 모의 사건: `{"id": "method", "kind": "choice", "value": "manual", "reason": "두 파일에서 추가 환경 없이 경로·표식을 대조한다."}` / 현재 조치: 실제 전달받은 모의 선택과 후보의 적용 범위를 대조했다.
- 확인: `{"판정": "충족", "관찰": "방법 비교는 실행 허용이 아니다. 아직 방법 선택 응답은 미제공이다. / 전달받은 모의 사건: {\"id\": \"method\", \"kind\": \"choice\", \"value\": \"manual\", \"reason\": \"두 파일에서 추가 환경 없이 경로·표식을 대조한다.\"} / 현재 확인: 지정 주체 역할의 choice 사건과 이유를 확인했다. request/supply를 선택으로 해석하지 않았다."}`
- 잔여: 없음

<a id="work-close"></a>
## 선정·이유·한계·후속 조건과 범위 보존을 대조한다

- 할 일: [본문](task.md#work-close)

- 조치·판단: Task의 실제 결과·원문 보존·관리 연결·필수 확인과 종료 범위를 현재 배정에 대조했다. 시험 폴더 외의 반영·발급·커밋은 범위에 없다. / 현재 조치: complete_task 뒤 부모 원문이 동일함을 확인했다. check_parent로 부모의 실제 전체 조건과 전달본 대응을 독립 대조했다.
- 확인: `{"판정": "충족", "관찰": "{\"issues\": [], \"observations\": [{\"id\": \"criteria-수동\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"criteria-로컬\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"criteria-재현\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"criteria-준비\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"criteria-범위\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"criteria-후속\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"method\", \"satisfied\": true, \"observation\": \"\"}]} / 현재 확인: {\"task_check\": {\"issues\": [], \"observations\": [{\"id\": \"criteria-수동\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"criteria-로컬\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"criteria-재현\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"criteria-준비\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"criteria-범위\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"criteria-후속\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"method\", \"satisfied\": true, \"observation\": \"\"}]}, \"parent_unchanged_after_child\": true, \"parent_check\": {\"issues\": [], \"observations\": [{\"id\": \"child-result\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"criteria-수동\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"criteria-로컬\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"criteria-재현\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"criteria-준비\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"criteria-범위\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"criteria-후속\", \"satisfied\": true, \"observation\": \"\"}, {\"id\": \"method\", \"satisfied\": true, \"observation\": \"\"}]}}"}`
- 잔여: 없음
