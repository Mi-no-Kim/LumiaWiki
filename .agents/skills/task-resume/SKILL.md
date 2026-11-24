---
name: task-resume
description: 중단이나 전환 뒤 기존 Task의 계획, 작업 폴더, 마지막 실행, 검수 근거와 승인 범위를 대조해 실행·대기·확인을 판단한다.
---

# Task 재개

<!-- inventory-dependencies: ["harness/공용 절차.md", "harness/Task 공통 절차.md", "harness/문서 관리.md", ".agents/skills/task-run/SKILL.md"] -->

1. [공용 재개 기준](<../../../harness/공용 절차.md#operation-commands>)과 [Task 착수·재개 확인](<../../../harness/Task 공통 절차.md#start-check>)을 사용한다. Task 본문과 적용 전달본을 대조하고 형식별 계획·실제 합의·현재 체크를 읽는다.
2. 해당 워크트리의 실제 변경, 마지막으로 검증한 결과, 남은 작업과 권한을 대조한다. 신규 형식은 계획 지문의 일치 여부를 확인한다. 부분 반영·불분명한 외부 결과는 [복구 절차](<../../../harness/문서 관리.md#recovery>)로 확인하고 기존 결과와 유효한 검수 근거를 재사용한다.
3. 확인한 위치·막힘·다음 행동을 반환하고, 요청과 현재 권한이 허용하는 확인된 다음 행동은 [task-run](../task-run/SKILL.md)으로 이어간다.
