---
name: task-plan
description: 기존 Task의 확정 전달본을 기준으로 수행 단계, 검증 방법, 사용자 확인 지점을 계획하고 실제 합의를 기록한다.
---

# Task 계획

<!-- inventory-dependencies: ["harness/공용 절차.md", "harness/Task 공통 절차.md", "harness/templates/task-plan.md", "scripts/check-rule-comments.py"] -->

1. [공용 계획 기준](<../../../harness/공용 절차.md#operation-commands>)으로 정식 Task와 요청 범위를 확인한다. 실제 부모 기준 기록·확정 전달본·본문 주석을 대조하고 [실행 전 전체 계획](<../../../harness/Task 공통 절차.md#sequence-rules>)을 적용한다.
2. 종전 형식은 본문에, 별도 계획 형식은 [Task 계획 절차](<../../../harness/Task 공통 절차.md#separate-plan>)와 [계획 양식](<../../../harness/templates/task-plan.md#body>)에 단계·검증을 둔다. 새 합의가 필요하면 영향을 제시하고 제안과 현재 적용 합의를 구별한다.
3. 실제 합의가 있을 때 해당 근거를 기록한다. 별도 계획 지문은 절차가 지정한 [검사 도구](../../../scripts/check-rule-comments.py)로 계산해 본문 합의 구역에 기록한다. 배정 범위 변경은 [부모 협의](<../../../harness/Task 공통 절차.md#revision>)로 연결한다. 현재 계획·남은 결정·다음 행동을 반환한다.
