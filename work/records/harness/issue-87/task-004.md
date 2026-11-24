# Task 87-004 — Issue·Task 공통 검수 규칙 도입

- 태그: 조사, 논의, 결정, 실행, 검수

<!-- separate-task-rule:recording
이 본문은 현재 결론·상태·다음 행동을 관리한다.
배정 원문은 적용 전달본에서, 세부 순서와 단계 완료 체크는 별도 계획에서, 실제 검증·복구 근거는 수행 기록에서 관리한다.
착수·재개·단계 전환·수용 전에 Task 공통 절차를 따라 계획·실제 상태·권한을 대조한다.
-->

공통 절차: [Task 공통 절차](<../../../../harness/Task 공통 절차.md#separate-plan>)
GitHub sub-issue(실제 연결 시): [Mi-no-Kim/LumiaWiki #93](https://github.com/Mi-no-Kim/LumiaWiki/issues/93)

<a id="summary"></a>

## 현재 요약

- 상태: 완료
- 현재 진행 위치: [결과](#result)
- 다음 행동: 없음 — [완료 근거](artifacts/task-004-execution.md#work-handoff).
- 막힌 조건: 없음. 4/4단계 완료.

<a id="assignment"></a>

## 전달사항 참조

- 부모 Issue: [Issue #87](issue.md#summary)
- 적용 전달본: [확정 전달사항](artifacts/task-004-assignment-r002.md)
- 전달본 식별: `r002`
- 기준 기록: [Issue #87의 배정·생성 근거](issue.md#assignment-004)

<a id="decisions"></a>

## 계획과 합의

- 상세 계획: [합의된 전체 계획](artifacts/task-004-plan.md)
- 현재 합의: 저장소 공통 검수 규칙을 도입하고 Task 생성·착수·재개·완료에 필요한 기록 확인을 보강한다. [검수 규칙 도입](issue.md#decision-5)과 [배정 개정](issue.md#decision-6)을 적용한다.
  - **검수 시점** 세부 작업마다 진행 AI가 자가검수하고, Task의 각 계획 단계와 Task·Issue 종료 전에는 진행 AI와 서브에이전트가 검수한다. 필수 근거가 부족하면 완료를 보류하고 유효한 근거를 재사용한다. 기존 완료 판정은 당시 기준으로 보존한다.
  - **생성·전달본 확인** 본문에서 목표·확정 조건·완료 기준·다음 행동을 확인할 수 있도록 하고, 기존 입력 양식에 따라 확정 전달본의 필수 내용과 적용 참조를 검사한다.
  - **주석·계획 확인** 착수·재개·단계 전환·완료 때 주석이 안내하는 행동과 실제 적용을 대조한다. 별도 계획 형식은 계획 연결과 실제 합의 근거를 확인한 뒤 의존 실행을 진행하고, 종전 형식은 본문의 계획과 단계 체크를 기준으로 삼는다.
  - **완료 확인** 기존 양식을 사용해 두 Task 형식과 Issue 종료를 대조한다. 특히 여러 세부 작업의 자가검수, 계획·합의 근거 누락 및 빈 전달본을 검사한다. 규칙 변경 후보를 현행 기준으로 자가·별도 검수하고 확정 결과를 [87-002](task-002.md#summary)에 전달한다.
  - **세부 설계 합의** 계획 지문 자동화와 검수·기록 통제를 유지하고 반복을 줄이는 [1단계 설계 및 진행 방식](artifacts/task-004-execution.md#baseline-proposals)에 사용자와 합의했다.
  <a id="plan-agreement"></a>

  - 합의 근거: 사용자가 “4단계 계획과 87-004 전용 워크트리 사용에 동의해”라고 응답했다. 적용 범위는 r002의 4단계 계획과 부모 Issue 기반 전용 워크트리다. 기존 87-002 변경을 보존하고, 세부 작업마다 자가검수하며, 각 단계 완료 전에 서브에이전트 검수를 받는다. 결정이 필요한 부분은 사용자와 합의한다.
  - 계획 지문: c82db52711d3cb16e510fc81d34f01499c0e60913059ca6cc52b4ceaa291bfbb
- 수행 기록: [4단계 수행·확인](artifacts/task-004-execution.md#work-handoff)

<a id="result"></a>

## 결과

- 판정: r002 충족. 공통 검수·기록 통제를 구현·검수하고 [PR #94](https://github.com/Mi-no-Kim/LumiaWiki/pull/94)를 부모에 반영했다. 87-002의 선행 입력 인계를 확인했다.
- 근거·한계·잔여: [4단계 검수와 인계 기준](artifacts/task-004-execution.md#work-handoff). 전체 회귀에서 실패한 브랜치 훅 2건의 단독 재확인과 실제 설치 훅 확인 범위, 부모 반영·87-002 인계의 확인 범위를 기록했다.
