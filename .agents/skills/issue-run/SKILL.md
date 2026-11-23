---
name: issue-run
description: 기존 Issue의 승인된 다음 행동을 실행하고 Task 배정, 생성 연계, 결과 대기, 전체 수용과 진행 상태를 관리한다.
---

# Issue 실행

<!-- inventory-dependencies: ["harness/공용 절차.md", "harness/Issue 공통 절차.md", ".agents/skills/create-task/SKILL.md", ".agents/skills/review-work/SKILL.md"] -->

1. [공용 실행 기준](<../../../harness/공용 절차.md#operation-commands>)으로 대상·요청 범위·권한을 확인한다. [Issue 공통 절차](<../../../harness/Issue 공통 절차.md#selection-rules>)와 본문 주석에 따라 현재 단계·준비·선행 조건을 대조한다.
2. Issue에 승인된 다음 행동을 진행한다. 확정 배정과 생성 권한이 있는 경우 [create-task](../create-task/SKILL.md)로 등록까지 연결한다. 하위 Task의 내부 실행·검증·체크는 그 Task의 기록·실행 권한과 절차를 사용한다.
3. [3단계의 대기 조건](<../../../harness/Issue 공통 절차.md#step-3>)이 충족된 상태에서 하위 결과가 아직 준비되지 않았으면 결과 대기 위치와 다음 확인을 기록한다. 준비나 생성이 미완료라면 실제 첫 미완료 단계와 다음 행동을 유지한다. 필수 하위 결과와 근거가 준비되면 [전체 수용](<../../../harness/Issue 공통 절차.md#completion-rules>) 조건별로 실제 결과를 대조하고 [review-work](../review-work/SKILL.md#common-review)로 자가·별도 검수를 연결한다. Issue 종료와 GitHub 반영은 적용 절차와 권한을 확인한다.
