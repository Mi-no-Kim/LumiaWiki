# Issue·Task 작업 기록의 실행 가이드와 반복 확인 방식 정비

<a id="summary"></a>

## 현재 요약

- 실제 GitHub Issue: [Mi-no-Kim/LumiaWiki #72](https://github.com/Mi-no-Kim/LumiaWiki/issues/72)
- 분류·브랜치: 독립 하네스 Issue. `issue/72-task-issue-guidance`, 분기 기준 `2992008c7de4eb11b843fa0d2f89e62352b657bc`.
- 상태: 진행 중
- 현재 진행 위치: [본문 정리와 정식 적용 계획](#plan)
- 다음 행동: 새 양식의 다섯 상태를 기준으로 기존 기록의 적용·전환 범위와 정식 반영안을 확정한다.
- 허용 범위·제약: 공통 Issue 모델과 새 양식·작성 방법을 우선하는 반영 방향을 합의했다. 현재는 정식 반영안 논의와 합의 갱신이며 양식 정식 교체·skill/hook 구현은 미착수다. 실제 객체 발급·외부 반영·제품 수행·커밋은 이번 범위에 없다.

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
- 현재 Issue hook의 보호 범위는 `start`·`state`·`position`·`completion` 네 주석과 명시 등록된 작성안·예시다. Task 본문 8개·수행 기록 1개 주석 보호와 신규 실제 기록의 자동 적용은 제안 단계다. 규칙 준수와 주석 변경 보호는 구분한다.

<a id="draft-map"></a>

## 현재 검토 파일

작성안·예시는 검토 자료이며 정식 양식 교체나 실제 작업 발급을 뜻하지 않는다. `artifacts/previous/`는 과거 원문·비교 자료다.

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

## 본문 정리와 정식 적용 계획

- [x] 본문을 현재 목표·합의·판정·잔여 중심으로 정리하고 유일한 수용·검증 근거와 참조를 보존한다.
- [ ] 공통 Issue 모델·새 양식 우선·다섯 상태 원칙에 맞춰 기존 기록의 적용·전환 기준을 확정한다.
- [ ] 합의한 범위에서 양식·입력·생성 지시서·공통 절차·수행 기록 양식을 현행 원천에 반영하고 skill의 참조·역할을 맞춘다.
- [ ] Issue/Task 주석 검사와 자동 대상 판별을 두 실행 지점에 연결한다. 신규 실제 기록의 표준 경로·도입 기준과 작성안/예시·예외의 명시 등록을 구분하는 방안을 확정한다.
- [ ] 생성·갱신·종료 흐름과 기존 검사 회귀, 실제 hook 발동을 검증하고 자체·필요한 별도 검수 및 skill/hook 현황을 맞춘다. 실제 Task에서의 운영 효과는 별도로 확인한다.

본문 정리는 완료했고 공통 Issue 모델·새 양식 우선·다섯 상태 원칙을 수용했다. 기존 기록의 적용 범위와 정식 반영안은 논의 중이며 양식·skill·hook의 실제 교체·구현은 아직 수행하지 않았다.

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

<a id="result"></a>

## 결과와 잔여

작성안 정비·Issue 생성 skill·Issue 주석 보호와 제한된 현행 절차 보완은 반영됐다. 새 양식의 정식 적용·Task 주석 검사·자동 대상 판별·실제 운영 효과 확인은 남아 있으며 #72 전체는 진행 중이다. 다음 판단은 공통화·새 양식 우선·다섯 상태 원칙에 따른 기존 기록 적용 기준과 정식 반영안이다.
