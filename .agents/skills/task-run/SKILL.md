---
name: task-run
description: 기존 Task의 계획과 실행 권한을 확인하고 승인된 다음 행동을 실행해 결과, 검수 근거와 진행 상태를 기록한다.
---

# Task 실행

<!-- inventory-dependencies: ["harness/공용 절차.md", "harness/Task 공통 절차.md", ".agents/skills/review-work/SKILL.md"] -->

1. [공용 실행 기준](<../../../harness/공용 절차.md#operation-commands>)과 [Task 착수 확인](<../../../harness/Task 공통 절차.md#start-check>)을 사용한다. 부모 확정 전달본, 본문 안내 주석, 실제 브랜치·선행 결과·권한을 대조한다. 종전 Task는 본문 계획과 체크를, 신규 Task는 별도 계획·실제 합의·계획 지문을 확인한다.
2. 승인된 실행을 진행한다. 세부 작업마다 자가검수하고, 단계 완료·Task 종료 전에는 [review-work](../review-work/SKILL.md#common-review)로 자가·별도 검수와 근거를 연결한다. 필수 조건이 미확인인 판정과 그 판정에 의존하는 다음 행동은 보류한다.
3. 실제 결과와 검수는 수행 기록에 남기고 단계 체크는 해당 형식의 원본에서 갱신한다. 본문의 현재 위치·다음 행동·막힘을 맞춘다. 전체 수용은 [Task 종료 기준](<../../../harness/Task 공통 절차.md#completion-rules>)에 대조한다.
