# Issue·Task 작업 기록의 실행 가이드와 반복 확인 방식 정비

<a id="summary"></a>

## 현재 요약

- 실제 GitHub Issue: [Mi-no-Kim/LumiaWiki #72](https://github.com/Mi-no-Kim/LumiaWiki/issues/72)
- 분류·브랜치: 독립 하네스 Issue. PR #77의 수용 실패 보완은 분기 기준 `77bb1185dee414a6cc8ab5f5a1372dafa79e23da`의 `issue/72-task-issue-guidance-r2`로 진행했고 PR #78로 병합됐다.
- 상태: 완료
- 현재 진행 위치: [결과와 잔여](#result)
- 다음 행동: 없음 — [결과와 잔여](#result).
- 허용 범위·제약: 사용자가 실제 운영 근거와 격리 시범을 결합한 수용 판단을 바탕으로 종료 처리를 승인했다. 응답 유실과 사전 승인은 모의 환경에서 검증했다.

<a id="goal"></a>

## 문제와 목표 및 수용 기준

규칙·합의·양식·브랜치/등록 절차를 확인하지 않고 임의로 진행하는 문제를 줄인다. 로컬 Issue·Task를 간결한 계획과 현재 기록으로 정비하고, 행동 전·재개·조건 변경·전환·수용 판단에서 필요한 지침과 실제 준비를 대조하도록 한다.

수용 판단에서는 목표·범위·완료 조건, 유효한 결정의 이유·권한·제약, 실제 검증·잔여가 보존되는지 확인한다. Issue의 배정·전체 수용과 Task의 상세 계획·실행·자기 수용을 구분하고, 양식 작성·검수 통과를 실제 생성·운영 성공으로 확대하지 않는다. 본문의 같은 항목은 [기록 경계](<../../../../docs/작업 기록 작성 기준.md#recording-boundary>)에 따라 현재 내용으로 갱신한다.

<a id="activity"></a>

<a id="small-work-rules"></a>

## 현재 합의와 제약

- Phase 하위·독립 Issue는 같은 본문·규칙 주석과 입력·준비 확인 → 논의·결정 → Task 생성 → 최종 검사의 네 단계를 사용한다. 독립 Issue는 부모 Phase 행만 생략하고 공통 생성 근거를 남긴다. 생성 준비는 Phase 진행 AI 또는 독립 요청을 받은 AI가 맡고 같은 create-issue skill을 사용한다. 초기 질문의 원문·순서와 목록 확인/배정 전 답 확정, 필수 준비 부족 시 시작·재개 제한은 유지한다.
- 두 유형 모두 개별 실행·검증은 Task에 배정하고 Issue는 전체 결과를 수용한다. Issue는 배정 결과·범위·완료 조건/확인 방법·원본·식별을 확정한다. Task의 설계·방법·상세 계획과 조사 결론은 생성 후 Task에서 다룰 사항으로 구분하며, 그 미정만으로 생성을 막지 않는다. 배정 변경은 부모에서 판단하고 기존 전달본 보존·개정·참조와 영향 확인을 처리한다. Task 본문에 배정 원문 사본을 따로 관리하지 않는다.
- 정식 반영은 이번에 합의한 새 양식·작성 방법을 우선하여 기존 양식·지시서를 교체하는 방향이다. 기존 필드·구성·설명을 관성적으로 합치거나 복원하지 않는다. 실제 기록의 사실·승인·검증 근거와 원본은 형식 교체와 구분해 보존하며, 충돌하는 현행 작성 규칙·참조는 같은 반영 범위에서 정합성을 맞춘다.
- Task 본문은 현재 요약·전달사항 참조·계획과 합의·결과의 네 구역이다. 첫 할 일 실행 전 전체 계획을 합의하고 위임 범위 안에서 갱신한다. 할 일은 행동 단위와 복수 태그로 표현하며 태그·계획 합의로 실행 권한을 추가하지 않는다.
- 상세 수행 기록은 Task당 한 파일에서 착수한 할 일의 같은 구역을 갱신한다. 필요한 논의·선택·실제 확인과 실패/보완 근거를 보존하고 진행 판단에 필요한 결론·이유·조건만 본문에 연결한다. 생성 양식은 최초 작성에만 쓰고 이후에는 실제 문서의 규칙 주석과 공통 절차를 따른다.
- 정식 상태 체계는 새 양식의 예정·진행 중·중단·완료·취소 다섯 값으로 정했다. 신규·미착수만 예정이며 전환 시 실제 활동·중단·완료 상태를 초기화하지 않는다. 현행 기준·검사기·라벨의 전환과 기존 기록 적용 범위는 정식 반영에서 맞춘다. 지문 계산·기대값 관리를 일반 작성의 필수 절차로 요구하지 않으며 과거 계산 근거는 당시 원문과 구분해 보존한다.
- 현행 정식 양식·두 생성 skill·공통 주석 검사와 신규 표준 기록 자동 발견은 `22854d6`에 반영됐다. Issue 보호 4개·Task 8개·수행 기록 1개와 고정 기존 기록 예외를 유지한다. [정식 반영 근거](artifacts/formalization-verification.md). 이번 추가 요청으로 1차 범위 17개를 실제 원천에 적용했다. 새 CLI·초안 상태 일반화는 미반영이다.

<a id="draft-map"></a>

## 정식 원천과 보존 검토 자료

현재 작성 원천은 [harness 양식](../../../../harness/templates/issue.md)·[공통 절차](../../../../harness/Issue%20공통%20절차.md)·[생성 skill](../../../../.agents/skills/create-issue/SKILL.md)이다. 아래 작성안·예시와 `artifacts/previous/`는 당시 검토 근거로 보존하며 현재 작성 원천으로 되돌리지 않는다.

| 용도 | 현재 파일 |
|---|---|
| Issue 입력·최초 생성 | [입력 양식](artifacts/issue-creation-input-draft.md) · [생성 지시서](artifacts/issue-file-creation-guide-draft.md) |
| Issue 본문·진행 | [본문 양식](artifacts/issue-body-template-draft.md) · [공통 절차](artifacts/issue-common-procedure-draft.md) |
| Issue 예시 | [#42 입력](artifacts/issue-creation-input-example-42.md) · [#42 본문](artifacts/issue-body-example-42.md) |

<a id="task-file-layout"></a>

| 용도 | 현재 파일 |
|---|---|
| Task 배정·최초 생성 | [입력 양식](artifacts/task-creation-input-draft.md) · [생성 지시서](artifacts/task-file-creation-guide-draft.md) |
| Task 진행·기록 | [공통 절차](artifacts/task-common-procedure-draft.md) · [본문 양식](artifacts/task-body-template-draft.md) · [수행 기록 양식](artifacts/task-execution-template-draft.md) · [구조 합의](artifacts/task-structure-agreement.md) |
| 배정 참조 예시 | [43-002 입력](artifacts/task-creation-input-example-43-002.md) · [43-002 본문](artifacts/task-body-example-43-002.md) |
| 논의·갱신·수행 예시 | [DB 논의 입력](artifacts/task-creation-input-example-db-method.md) · [DB 논의 본문](artifacts/task-body-example-db-method.md) · [수행 중 Task](artifacts/task-body-example-recording.md) · [수행 기록](artifacts/task-execution-example.md) |

<a id="plan"></a>

<a id="pending"></a>

## 정식 반영 현황과 1차 후속 계획

- [x] 새 양식·작성 지시서·공통 절차·생성 skill·공통 주석/상태 검사와 현황을 정식 반영했다. 근거는 `22854d6`과 [정식 반영·한계](artifacts/formalization-verification.md)다.
- [x] 현재 미추적 기록·시험 원문과 시범 핵심 자료를 `4b37114`에 보존했다. JSON 41개는 좁은 Git 속성으로 index와 원문 바이트를 맞췄다. [보존 기준](artifacts/pilot-2/baseline.md).

<a id="phase-1-plan"></a>

### 1차 원천 반영과 효과 비교

- [x] 기준 상태는 446bc75에 보존돼 있고 사용자 요청으로 17개 원천의 실제 적용·비교를 진행한다. 종전 후보 준비 근거는 [비교 자료](artifacts/pilot-2/phase-1/comparison.md)에 보존한다.
- [x] 기준 446bc75의 적용 전 코드를 고정하고 네 입력과 지문을 보존했다.
- [x] 17개를 실제 원천에 반영하고 같은 네 입력을 실제 저장소의 검사기로 대조했다. 짧은 Task 오경고는 제거됐고 긴 본문 경고·주석 위반 거부는 유지됐으며 의존 오류에 실제 파일명이 표시됐다. CLI·초안 상태 일반화는 계속 보류한다.
- [x] 실제 저장소 회귀 106개, work/index 현황·기록·주석 검사, 최종 참조 190개와 보호 경계를 대조하고 별도 검수의 필수 조건을 충족했다.
- [x] 실제 개선·한계를 Issue와 GitHub에 반영하고 게시 후 본문·상태·라벨을 대조했다. 실제 제출 커밋은 Git 이력으로 식별한다.

새 명시 초안 CLI·초안 상태 규칙의 일반화는 후속으로 보류한다. 실제 링크 경계·지원 환경, 별도 문맥의 생성·재개·종료 행동과 사전 논의/정식 기록 경계를 추가 확인해야 한다. 자동 hook 발동·정식 업무 전체 성공은 기존 직접 호출 결과로 대신하지 않는다. 이번 요청으로 1차 범위만 실제 적용하며 위 후속 기능은 계속 보류한다.

<a id="creation-registration-scope"></a>

### 생성 요청 범위와 GitHub 등록

- 사용자 합의: “Issue나 Task를 생성하라고 하면 본문 작성과 GitHub 등록까지 포함하고, 실제 작업 착수는 별도로 하는 걸로 기준을 정리해줘.”를 현재 생성 범위로 채택했다. 기존 Issue·Task 생성 안내의 후속 정리이며 별도 작업 단위를 만들지 않는다.
- 반영 범위: [생성 기본 범위](<../../../../docs/작업 기록 체계.md#creation-scope>)를 원천으로 [등록 절차](<../../../../harness/문서 관리.md#create>), 두 본문 생성 지시서, Issue의 Task 생성 단계와 두 생성 skill을 맞췄다. 기본 생성과 명시적 초안/본문만·외부 등록 제한을 구별하고, Issue 실제 번호 확보와 Task 로컬 순번·GitHub 번호의 차이, 부분 등록 복구와 본작업 미착수 경계를 유지했다.
- 확인 결과: 번호 없는 독립 Issue, 상세 계획이 미정인 Task, 본문만 요청, 부분 실패 재개, 생성과 착수의 동시 지시를 별도 에이전트가 행동 추적했다. 동시 지시에도 다시 요청을 기다리게 하는 충돌을 발견해 담당 원천과 직접 사용처 6곳을 보완했다. 최종 index의 변경 9개와 작업 파일 일치, 명시적 제한·번호·부모 관계·미착수/동시 착수의 구분을 자체·별도 검수해 추가 필수 결함을 발견하지 못했다. index의 현황·주석·작업 기록·공백 검사, 스킬 형식 대체 검사와 변경 참조/표식 25개를 확인했다. 기록 길이 경고만 남았으며 Task 종료 상태 검사는 독립 Issue여서 해당하지 않는다.
- 검증 한계: 커밋 46346b4의 행동 추적·읽기 조회 이후 아래 실등록 검증에서 독립 Issue 발급과 기존 부모 #72 아래 Task 발급·연결·취소 종료 쓰기를 확인했다. Phase/milestone 설정·오류 주입 후 복구·상세 계획과 본작업 수행·부모 전체 수용은 미검증이다. 스킬 형식 검사는 PyYAML 부재로 기존 Prettier YAML 파서와 이름·설명·미완성 표식 대조로 대신한다.
- 실제 조회: 커밋 46346b4의 읽기 확인에서 gh 2.101.0·이슈 기능·접근 권한·기본 생성 라벨·Phase milestone 7개와 sub-issue 조회를 확인했다. 당시 없던 status:paused·status:cancelled는 아래 실등록 검증에서 추가·재조회했으며 #72의 실제 자식도 0개에서 검증용 #74 한 개로 바뀌었다.
- 원격 반영: 생성 기준 변경의 원격 #72 본문 게시와 Git push는 수행하지 않았다. 이번 검증의 라벨·Issue #73·Task #74와 #72의 실제 자식 관계는 반영·재조회했다. 기존 CLI·초안 상태 일반화와 전체 본작업 운영 효과 확인의 잔여는 유지한다.

<a id="live-registration-validation"></a>

### 실제 라벨·Issue·Task 등록 검증

- 요청·범위: 사용자가 누락 라벨 등록과 실제 Issue·Task 생성·부모 연결 검증을 직접 요청했다. 독립 하네스 검증용 Issue와 #72 아래의 Task 72-001을 등록해 생성 직후 예정·미착수 상태와 실제 연결을 확인하고, 검증 후 취소로 닫아 보존한다.
- 라벨: status:paused(D93F0B)·status:cancelled(6E7781)를 기준 설명과 함께 실제 등록하고 조회해 일치를 확인했다.
- Task 배정·확정 근거: 위 사용자 요청의 결과·범위를 [전달사항 r001](artifacts/task-001-assignment.md)에 확정했다. 직하 기록·보유 목록과 원격 자식이 없음을 대조해 순번 001과 경로 `work/records/harness/issue-72/task-001.md`를 배정했다. 상세 본작업 계획·수행은 맡기지 않는다.
- 발급·검증 결과: [독립 검증 Issue #73](../issue-73/issue.md#registration-validation-result)과 [Task 72-001 / GitHub #74](task-001.md#result)의 실제 생성·게시·로컬 기록을 확인했다. Task #74의 부모 #72를 양방향 재조회했고 생성 직후 Open·예정 라벨·본문/원본·배정 참조와 본작업 미착수·수행 기록 부재를 확인했다. 두 검증 객체는 취소 종료 후 Closed/Not planned·status:cancelled·본문과 부모 관계를 재조회했다. [실제 응답 근거](artifacts/live-registration-verification.json)를 보존했으며 삭제하지 않았다.
- 부모 수용의 구분: 취소한 자식 #74로 GitHub의 #72 진척률이 1/1·100%가 되었지만 #72는 Open·진행 중을 유지했다. 이 진척률을 부모의 전체 완료·수용으로 해석하지 않는다.
- 검수 결과: 현재 index 6개 파일을 자체·별도 에이전트가 대조했고 별도 검토자가 원격 두 라벨·#73·#74·부모 #72를 GET으로 재조회했다. 부모 보유 목록의 낡은 예정 표시는 취소로 정정했고 추가 필수 결함은 발견하지 못했다. 현황·주석·기록·공백 검사와 Task 상태 취소 대조를 통과했다. 본작업 수행 기록은 없으며 분량 경고만 남았다.
- 검증 한계·반영: 독립 하네스 경로와 기존 부모 연결·초기 미착수·취소 종료를 확인했다. Phase/milestone 설정과 실패 주입 복구, Task 본작업의 계획·수행·수용은 포함하지 않았다.

<a id="github-publication-spec"></a>

### GitHub 게시 명세와 생성 순서 정비

- 합의·범위: GitHub Issue는 과제 전체의 명세, Task는 배정 작업의 명세로 작성한다. 사용자가 검토한 최종 초안을 반영하되 담당자·저장소 행을 빼고 공통 작성 규칙을 한곳에 모은다. 실행 대상 저장소 확인은 등록 맥락에서 처리한다. 후속 요청에 따라 댓글·PR을 결과 공유 수단으로 지정한 문구를 삭제하고 참고 자료의 일반 원칙만 유지한다.
- 반영: 두 게시 양식은 목적·범위/조건·산출물/완료 기준과 필요한 질문·자료를 담는다. Task는 실제 확정 전달사항·배정 근거와 결정/실행 경계를 대조한다. 등록 정보는 작성자용으로 구분하고 진행·결과·세부 계획을 생성 본문의 고정 항목으로 복제하지 않는다. 번호 없는 Issue도 전체 로컬 본문과 게시 명세를 먼저 검증한 뒤 발급하고 실제 번호·정식 경로·링크를 보정하도록 기준·절차·지시서·생성 skill을 맞췄다.
- 검수: 기존 원입력 적용·실패 경로 대조는 유효한 근거로 유지했다. 이번 보완 4개 파일과 직접 사용처를 자체·별도 에이전트가 재대조해 Phase 범위 충돌 해소와 추가 필수 결함 부재를 확인했다. 두 카탈로그 현황·주석·공백·참조/표식 166개 검사를 통과했으며 기록 길이 경고만 남았다. 댓글·PR로 결과 공유 위치를 지정하는 새 의무는 없고, 기존 Git 닫기 기준의 참조만 유지한다.
- 범위 충돌 보완: [공용 GitHub 반영](<../../../../harness/문서 관리.md#github-update>)의 갱신 대상에 내용·상태·관계를 포함하고 Issue·Task 생성 본문에만 게시 명세 규칙을 적용하도록 명확히 했다. [Phase 게시 양식](../../../../harness/templates/github-phase.md)의 기존 계획·판단·검증·결과 설명 갱신을 보존한다. 결과 공유 위치를 댓글·PR로 지정하는 문구는 삭제했다. 별도 검수에서 기존 Phase 설명 갱신 기준이 보존됨을 재확인했다.
- 제출 범위: 이번 게시 명세·규칙 정리와 필요한 동반 변경 10개 파일을 같은 목적의 커밋으로 제출한다. 과거 실등록 기록·근거와 무관한 변경은 포함하지 않으며 실제 인덱스 후보의 내용·현황·필수 검수 일치를 확인한다.
- 검증 한계: 77125ac의 실제 등록 근거는 이전 양식·순서에 대한 관찰이다. 새 기준의 실등록 전에는 두 생성 skill을 stale로 구분했다. 현재 확인 범위는 [새 기준 실등록 검증](#live-registration-a79e1f8)을 따르며, Phase 소속·실패 복구·본작업 운영 효과 확인으로 확대하지 않는다.

<a id="live-registration-a79e1f8"></a>

### 새 게시 기준 실등록 검증

- 요청·범위: 사용자가 a79e1f8 기준의 실제 Issue·Task 생성·부모 연결 검증과 본작업 미착수를 명시했다. 독립 검증 Issue는 생성만 하며 Task는 이번 검증을 소유하는 기존 #72 아래에 둔다. 검증 후 취소 사유를 남겨 닫고 기록·번호·관계를 보존한다.
- Task 배정·확정 근거: 이번 요청의 결과·범위를 [Task 72-002 전달사항 r001](artifacts/task-002-assignment.md)에 확정했다. 실제 직하 파일·보유 목록과 원격 자식에서 기존 001/#74만 확인해 002를 배정했다. 실제 부모 #72는 Open·진행 중이며 milestone은 없다. 이 배정은 생성·연결 검증까지로 본작업 계획·수행을 맡기지 않는다.
- 발급 전 확인: 전체 Issue 초안·Task 본문·확정 전달사항·게시 명세를 실제 발급 전에 대조했다. Issue 주석 10개·Task 주석 8개와 초기 예정·미체크·미착수, 필수 주석 누락 거부를 확인했다. [검증 요약](artifacts/task-002-registration-verification.json)에는 이 확인 결과와 초기/종료 관찰·한계를 남긴다. 자동 skill 선택·hook 발동 확인은 아니다.
- 실제 결과: [독립 검증 Issue #75](../issue-75/issue.md#registration-validation-result)와 [Task 72-002 / GitHub #76](task-002.md#result)을 생성·게시했다. 발급 후 실제 번호·정식 경로·링크와 자동 주석 검사를 확인하고 본문·예정 라벨·milestone 없음·미착수를 재조회했다. Task #76의 부모 #72를 양방향 조회했다. 두 객체는 취소 사유를 본문에 반영해 Closed/Not planned·status:cancelled로 닫고 부모 관계까지 재조회해 보존했다. 수행 기록은 생성하지 않았다.

- 부모 상태·한계: GitHub는 취소한 자식도 닫힌 것으로 계산해 #72의 진척률이 2/2·100%가 되었지만 부모는 Open·진행 중을 유지했다. 새 검증 Issue #75 아래에 Task를 만들거나 그 Issue의 논의·배정 단계를 진행하지 않았다. Phase 소속 milestone 설정·오류 주입 복구·Task 본작업·부모 전체 수용은 미검증이다.

- 최종 확인: 발급 전 대조·실제 등록·번호 보정·부모 양방향 조회·취소 종료를 확인했고 현황·주석·기록·참조 검사를 통과했다. 두 생성 skill의 확인된 실등록 범위는 verified로 유지한다. 검증 당시 생성·게시 원천 버전은 a79e1f8이며 이번 요약 정리는 새 원격 검증 실행이 아니다.

- 근거 최소화: 이번 사용자 요청에 따라 [기록 경계](<../../../../docs/작업 기록 작성 기준.md#recording-boundary>)에 기준 버전·대상/관계·확인 결과/한계와 복원하기 어려운 관찰을 우선 요약하도록 정리했다. 이번 근거는 초기/종료 상태와 판정만 남기고 원문·요청·응답 중복 사본을 제거했다. 확정 전달사항 원문과 기존 검증 범위는 유지했다. 원본 대비 사실 보존과 기준 변경을 자체·별도 검수했고 최종 파일·근거 연결과 관련 검사 통과를 확인했다.

- 제출 범위: 이번 실등록 기록과 근거 최소화·보존 기준 변경 7개 파일을 같은 목적의 커밋으로 제출한다. 실제 인덱스의 취소 상태·최소 근거·검증 범위와 별도 검수 일치를 확인하며, 이전 실등록 원문을 별도 사본으로 다시 포함하지 않는다.

<a id="owned-tasks"></a>

## 보유 Task와 관련 과제

- [Task 72-002: 새 게시 명세·부모 연결 확인](task-002.md#summary) — 취소 · GitHub #76 · 부모 #72 확인 · 취소 종료 재조회 확인 · 본작업 미착수
- [Task 72-001: 등록 검증용 생성·부모 연결 확인](task-001.md#summary) — 취소 · GitHub #74 · 실제 부모 #72 연결·종료 재조회 확인

 관련 과제: [Git/GitHub #1](../issue-1/issue.md#summary), [기록 부담 #19](../issue-19/issue.md#summary)·[#60](../issue-60/issue.md#summary), [상태 검사 #36](../issue-36/issue.md#summary).

<a id="verification"></a>

## 확인 결과와 근거

<a id="task-generation-test"></a>

- Task 생성·문서 관리: [C의 실행·판정](artifacts/task-doc-suite-c/run.md#results)을 보완 후 수용했고 검증된 규칙을 현행 기준·절차·양식 9개 파일에 반영해 자체·별도 검수했다. [반영 범위·한계](artifacts/verification-evidence.md#task-procedure-application). [중단된 과거 시험](artifacts/task-generation-test.md)은 성공 근거에서 제외한다.
<a id="task-common-review"></a>

- Task 작성안: 본문 네 구역·동적 계획·단일 수행 기록과 머리말 규칙 주석을 정비했다. [수행 기록 검수 근거](artifacts/verification-evidence.md#task-common-review). 문안·시험 검수를 실제 Task의 운영 효과로 확대하지 않는다.
<a id="issue-question-confirmation-timing"></a>

- Issue 생성 skill: 같은 모델의 새 문맥에서 3번 원입력으로 목록 확인/답 확정 시점·원문·주석·초기값을 확인했다. [명시적 가상 적용과 검수 한계](artifacts/verification-evidence.md#issue-question-confirmation-timing). 자동 선택·실제 파일 작성·발급·운영은 미확인이다.
<a id="issue-rule-comment-hooks"></a>

- Issue 주석 hook: 기존 73개 회귀, 임시 저장소의 실제 pre-commit 다섯 사례와 기록된 로컬 대화에서의 PostToolUse 자동 거부·원복을 확인했다. [대상·실행 식별·환경·한계](artifacts/verification-evidence.md#issue-rule-comment-hooks). 이 근거는 Task 보호나 다른 환경의 성공을 뜻하지 않는다.
- 최초 문안 수용·과거 지문·철회안의 구별은 [보존 근거](artifacts/verification-evidence.md#phase-issue-acceptance)에 둔다. 작성안·동작 확인의 범위를 유지하고 새 현재 지문값으로 갱신하지 않는다.
- 본문 정리: 현재 합의·권한·수용/검증 한계를 자체·별도 대조했고 참조·기록 검사와 같은 모델의 별도 문맥 검수를 마쳤다. 기존 Issue 주석·skill/hook 현황 검사도 통과했으며 본문 외 기존 파일과 과거 지문값을 보존했다.

<a id="pilot-2-adoption"></a>

- 격리 시범: 전체 제안은 안내 2개·하네스 20개 파일이다. 전체 회귀 114개 후 마지막 보완 영향 26개, 직접 호출 18개와 링크 294개를 확인했다. [당시 제안·근거](artifacts/pilot-2/baseline.md). 이 수치를 실제 AI 행동 개선율로 환산하지 않는다.
- 실제 적용 비교: 기준 446bc75에서 1차 원천 17개를 적용했다. 같은 입력에서 짧은 Task 오경고는 사라지고, 실제 긴 본문 경고·주석 위반 거부는 유지되며 의존 오류에 실제 파일명이 나온다. [동작 비교와 적용 근거](artifacts/pilot-2/applied/report.md). 후보 축소와 실제 동작 개선을 구별한다.
- GitHub 반영: 이번 실제 적용 결과를 게시하기 전 원격 본문이 이전 준비안과 같음을 확인했다. 게시 후 실제 적용·동작 비교 본문이 준비안과 일치하며 OPEN·unit:issue·status:in-progress를 유지함을 확인했다. 로컬 소스와 커밋은 push하지 않았다.

<a id="crlf-state-fix"></a>

### PR #77의 CRLF 상태 검사 보완

- 문제·재현: `861e9ef`의 Task 상태 정규식은 Git 인덱스에 남은 CRLF의 `\r`을 처리하지 못한다. LF/CRLF 원문을 그대로 스테이징하는 회귀를 먼저 추가했고, 수정 전 LF의 다섯 상태는 통과하지만 CRLF의 다섯 상태는 모두 미확인 오류로 거부됨을 확인했다.
- 수정: [상태 검사기](../../../../.agents/skills/review-work/scripts/check_task_status.py)는 인덱스 원문을 읽은 뒤 CRLF를 LF로 정규화해 판독한다. [회귀 검사](../../../../.agents/skills/review-work/scripts/test_check_task_status.py)는 다섯 상태·두 줄바꿈의 실제 인덱스 바이트와 검사 후 인덱스 불변도 확인한다.
- 검증·제출: 수정 후 상태 검사 회귀 8개와 하네스 회귀 106개, 총 114개가 통과했다. LF·CRLF의 다섯 상태와 원문 바이트·인덱스 불변을 확인했고 기존 중복·여러 줄·미지원 상태 거부와 Windows 출력·고정 예외/이전 후보 호환을 유지했다. 별도 검토자가 새 회귀를 원본/수정 구현에 교대로 적용해 실패 검출과 수정 후 통과를 재현했고 자체·별도 검수에서 추가 필수 결함을 발견하지 못했다. 제출 후보의 현황·주석·기록·공백 검사와 작업 파일/인덱스 일치를 확인했으며 기존 분량 경고만 남았다.
- 잔여: 이번 보완은 상태 판독 회귀 수정이며 Phase 소속·실패 복구·Task 본작업과 부모 전체 수용의 미검증을 해소하지 않는다. PR 병합과 #72 전체 완료를 처리하지 않는다.

<a id="closing-reference-guard"></a>

### 자동 닫기 재발 방지

- 원인·복구: PR #77의 merge commit은 `77bb118`이다. 기존 작업 커밋 `02fb9df`의 `fix: #72`가 main 유입 시 닫기 표현으로 해석돼 #72가 자동 종료됐다(이벤트 `36627206883`). PR 닫기 연결 목록이 비어도 커밋의 영향을 배제할 수 없었다. 진행 중 판단에 맞춰 다시 열고 Open·status:in-progress를 확인했으며 [PR #77](https://github.com/Mi-no-Kim/LumiaWiki/pull/77)에 원인·복구를 남겼다.
- 결정·범위: `fix` 유형은 유지하고 제목은 한국어 요약, 연결은 별도 `Refs #번호` 행으로 분리한다. 아홉 닫기 키워드·대소문자·콜론과 실제 참조 결합을 검사한다. URL·단순 Markdown 포장은 보수적으로 차단하며 GitHub 파서 완전 재현으로 주장하지 않는다.
- 반영: 공용 메시지/범위 검사기를 로컬 `commit-msg`와 PR 제목·본문·base..head 전체 커밋 검사에 재사용한다. 기존 main 이력은 소급 차단하지 않는다. installer는 hook 하나씩 독립 설치·원본 보존/복구하며, CI는 전체 이력과 PR edited 이벤트·원문 JSON 입력을 사용한다. 실제 통합 메시지는 병합 직전에 별도 확인한다.
- 검증·상태: 새 회귀 15개를 포함한 하네스 121개가 통과했고 신규 15개는 별도 검토자가 독립 통과했다. 현황·기록·공백·YAML 구문과 문서 참조 125개를 대조했으며 두 별도 검토자의 필수 지적은 없었다. 실제 저장소에 commit-msg를 설치하고 `git hook run`으로 사고 표현 거부·정상 Refs 통과와 HEAD/인덱스 불변을 확인했다. 최초 전체 실행의 기존 분기 호환 사례 1회 실패는 단독·전체 재실행에서 재현되지 않았고, 다음 실패의 원인을 볼 수 있도록 해당 assertion의 stderr 진단을 보완했다. 원격 CI·필수 상태 검사 설정·실제 GitHub 자동 닫기 재시험은 이번 로컬 확인으로 대신하지 않는다.

<a id="result"></a>

## 결과와 잔여

- 정식 반영: 신규 Issue·Task 양식과 생성 skill, 공통 검사 원천을 반영했다. [1차 원천 반영](#phase-1-plan)의 17개 변경과 실제 저장소 회귀 106개, [새 게시 기준의 실제 등록](#live-registration-a79e1f8)을 대조했다. [자동 닫기 보완 PR #78](https://github.com/Mi-no-Kim/LumiaWiki/pull/78)은 main의 77bc422에 반영됐다.
- 실제 운영 수용: [#87](../issue-87/issue.md#review-acceptance-closure)의 생성·승인·계획·수행·재개·Task 완료·부모 수용, [#95](https://github.com/Mi-no-Kim/LumiaWiki/pull/105)의 Phase 소속과 하위 Task 연결을 확인했다. #95의 생성 전 확인 누락은 당시 사례의 검증 한계로 남긴다.
- 보완 수용: [Issue·Task 격리 등록과 복구](artifacts/verification-evidence.md#registration-recovery-trials)에서 모의 승인 전 쓰기 0건, 응답 유실 뒤 기존 번호 복구, 중복 발급 방지, 부모와 milestone 연결 및 로컬 기록 일치를 확인했다. Task 부모 요약의 모순은 원시험을 보존한 별도 복사본에서 한 줄을 보완한 뒤 재검증했다.
- 종료 판정: 기존 실제 근거와 합의한 격리 시범의 범위를 자체·별도 검수해 수용했고 사용자가 종료 처리를 승인했다. 응답 유실 복구의 실제 GitHub 장애 상황은 미검증으로 남긴다. 보류된 초안 CLI와 초안 상태 일반화는 별도 제안 범위다.
