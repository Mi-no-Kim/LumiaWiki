---
name: issue-resume
description: 중단 또는 전환 뒤 기존 Issue의 실제 단계, 하위 Task 결과, 의존 관계와 승인 근거를 대조해 재개 또는 대기를 판단한다.
---

# Issue 재개

<!-- inventory-dependencies: ["harness/공용 절차.md", "harness/Issue 공통 절차.md", "harness/문서 관리.md", ".agents/skills/issue-run/SKILL.md"] -->

1. [공용 재개 기준](<../../../harness/공용 절차.md#operation-commands>)을 사용한다. [Issue 진행 기준](<../../../harness/Issue 공통 절차.md#selection-rules>)에 따라 본문 단계, 보유한 Task의 실제 관계·상태·결과와 유효한 결정·권한을 대조한다.
2. 발급·통합 등 마지막 결과가 불분명하면 [부분 반영 복구](<../../../harness/문서 관리.md#recovery>)를 적용한다. [3단계의 대기 조건](<../../../harness/Issue 공통 절차.md#step-3>)을 계속 충족하며 결합 결과가 계류 중이면 Issue의 대기 위치와 다음 확인을 기록한다. 준비나 생성이 미완료라면 실제 첫 미완료 단계와 다음 행동을 반환한다.
3. 현재 위치, 마지막으로 확인된 결과, 막힌 조건과 다음 행동을 반환한다. 실행 요청의 대상·전제·권한이 유효하면 [issue-run](../issue-run/SKILL.md)으로 같은 Issue의 다음 행동을 이어간다.
