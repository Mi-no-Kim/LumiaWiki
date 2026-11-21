# Task 43-002 배정 개정 — 아이템 스킬 저장 범위

<a id="assignment-revision"></a>

- 적용 근거는 [Issue #43의 배정 개정](../issue.md#skill-storage-assignment-revision)이다. 최초 배정은 `d6adc6f`의 [Task 43-002](https://github.com/Mi-no-Kim/LumiaWiki/blob/d6adc6f0eaf3a3111a09ea14e37ba6491f378dc1/work/records/phase-001/issue-43/task-002.md#goal)다.
- [P1](../../phase.md#agreed-data-scope)은 스킬 버전에 설명 원문을 저장하고 아이템 버전·기준 패치와 스킬 대상·지정 버전을 연결한다. [임시 연결 설명의 표시 규칙](#temporary-display-description)과 능력치 원본·표시 캐시 저장 계약을 적용한다.
- [P3](../../../phase-003/phase.md#goal)에서 실제 계산 규칙과 입력에 맞춰 스킬 연결의 계산용 JSON 필드·값 범위를 정하고 저장·검증한다. P3의 계산용 JSON은 P3 수용 조건으로 확인한다.

<a id="temporary-display-description"></a>

## P1 임시 연결 설명의 표시 규칙

연결의 임시 `description`을 표시한다. 값이 `NULL`이거나 빈 문자열이면 설명은 빈 상태다. 지정 스킬 버전의 설명 원문은 해당 버전에 보존한다. [확정 근거](task-002-execution.md#item-skill-link-description)

<a id="acceptance"></a>

## 개정된 스킬 저장 완료 조건

- 한 아이템 버전의 여러 스킬을 저장한 뒤 각 연결의 임시 설명과 지정 스킬 버전의 설명 원문을 읽고, 임시 설명은 저장한 값대로 표시되고 `NULL`이나 빈 문자열이면 빈 상태인지 확인한다.
- 잘못된 스킬 대상·버전 조합과 잘못된 연결 기준 패치, 같은 스킬의 중복 연결을 거부한다.
- 새 아이템 버전의 연결은 해당 아이템 버전과 기준 패치를 보존한다. 능력치나 재료만 바뀌면 기존 지정 버전과 연결의 임시 설명 값을 이어받는다.
