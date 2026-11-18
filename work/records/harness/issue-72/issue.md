# Issue·Task 작업 기록의 실행 가이드와 반복 확인 방식 정비

<a id="summary"></a>

## 현재 요약

- 실제 GitHub Issue: [Mi-no-Kim/LumiaWiki #72](https://github.com/Mi-no-Kim/LumiaWiki/issues/72)
- 분류·브랜치: 독립 하네스 Issue. `issue/72-task-issue-guidance`, 분기 기준 `2992008c7de4eb11b843fa0d2f89e62352b657bc`.
- 상태: 진행 중
- 현재 진행 위치: [생성 요청 범위와 GitHub 등록](#creation-registration-scope)
- 다음 행동: 커밋 보존을 마친 뒤 별도 생성 요청에 새 기준을 적용하고 실제 발급·연결 쓰기와 전체 운영 효과를 확인한다. 보류한 CLI·초안 상태 일반화의 검증은 남아 있다.
- 허용 범위·제약: 사용자가 생성 기준과 관련 변경의 검증·필요 보완·커밋을 요청했다. 같은 Issue의 후속 변경으로 처리하며 GitHub 기능·권한·라벨·milestone·sub-issue 조회는 읽기 전용으로 확인한다. 실제 GitHub 객체 발급·원격 #72 갱신·push·PR은 이번 커밋·검증 범위에 포함하지 않는다. 기존 기록 형식과 당시 근거를 유지한다.

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
- 검증 한계: 실제 GitHub 발급·부모 연결 쓰기와 실패 후 복구의 전체 실행은 미확인이다. 행동 추적·읽기 전용 조회를 실제 발급 성공으로 확대하지 않는다. 두 skill의 과거 동작 근거와 재확인 필요 표시는 보존한다. 기본 스킬 검증기는 PyYAML 부재로 실행할 수 없어 기존 Prettier YAML 파서와 이름·설명·미완성 표식 대조로 대신한다.
- 실제 조회: gh 2.101.0으로 Mi-no-Kim/LumiaWiki의 이슈 기능과 접근 권한, #72의 Open·unit:issue/status:in-progress 및 자식 0개, sub-issue 조회 성공과 Phase milestone 7개를 확인했다. 기본 샌드박스의 연결 실패 후 확장 권한의 GET만 사용했다. 신규 생성에 쓰는 unit:issue·unit:task·status:planned는 존재한다. status:paused·status:cancelled는 원격에 없어 후속 상태 전환 시 준비가 필요하다.
- 원격 반영: 이번 기준 정리 결과는 로컬 원천과 기록에 반영하며 원격 #72에는 미반영이다. 기존 CLI·초안 상태 일반화와 실제 운영 효과 확인의 잔여는 유지한다.

<a id="owned-tasks"></a>

## 보유 Task와 관련 과제

발급한 하위 Task는 없다. 관련 과제: [Git/GitHub #1](../issue-1/issue.md#summary), [기록 부담 #19](../issue-19/issue.md#summary)·[#60](../issue-60/issue.md#summary), [상태 검사 #36](../issue-36/issue.md#summary).

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

<a id="result"></a>

## 결과와 잔여

신규 양식·skill·공통 검사 원천의 정식 반영은 완료됐다. 1차 원천 17개를 실제 적용했다. 동일 입력 네 사례에서 오경고·진단 개선과 기존 보호 유지를 확인했고 실제 저장소 회귀 106개를 통과했다. 최종 제출 후보의 필수 검수와 원격 본문 대조를 마쳤다. 이번 적용의 실제 커밋은 Git 이력으로 식별한다. #72 전체는 진행 중이다. 실제 Task의 생성·계획 합의·수행 기록·완료·부모 수용을 포함한 운영 효과 확인은 남아 있다.
