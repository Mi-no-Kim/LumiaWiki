# Task 43-002 전달사항 예시

> 전달본 보존·본문 참조·지문 계산을 확인하기 위한 검토 자료다. 실제 Task 43-002의 확정 전달본·승인·실행 지시가 아니다. 네 묶음은 고정 커밋의 기존 배정을 재구성했다.

- 전달본: r001 (예시)
- 확정 근거: 예시 전용. 실제 Task에 대한 확정·승인 기록 없음.
- 이전 전달본: 없음
- 개정 이유·합의: 초판 예시

원천: 커밋 `76e26221ce8b334b462273660c9b4b7e79a81e01`의 [Issue #43 배정](https://github.com/Mi-no-Kim/LumiaWiki/blob/76e26221ce8b334b462273660c9b4b7e79a81e01/work/records/phase-001/issue-43/issue.md#task-outline)·[Task 범위·조건](https://github.com/Mi-no-Kim/LumiaWiki/blob/76e26221ce8b334b462273660c9b4b7e79a81e01/work/records/phase-001/issue-43/task-002.md#goal). 아래 기준 문서는 같은 커밋에서 식별한다.

<a id="purpose"></a>
## 배정 근거·목적

- 배정 근거: Issue #43의 아이템/스킬 버전과 원본·캐시 저장/조회 배정.
- 목적: 후속 기능에서 아이템·능력치·스킬 정보를 같은 기준으로 저장·조회할 수 있게 한다.

<a id="result"></a>
## 담당 결과

- 아이템·능력치·스킬의 DB 구조·Java 저장/조회 코드와 검증 근거·후속 사용 계약.

<a id="scope"></a>
## 수행 범위·이미 결정된 사항

- 수행 범위: 해당 정보의 저장·조회·기본 수정을 위한 설계·구현·검증. 실제 행동은 아래 현재 허용 범위를 따른다.
- 경계·제약: 화면·실제 자료 등록·제작/획득/배달 관계·결합 조회/갱신·스킬 수식 실행은 담당 범위 밖이다.
- 선행 입력·의존: [Task 43-001의 반영 결과](https://github.com/Mi-no-Kim/LumiaWiki/blob/76e26221ce8b334b462273660c9b4b7e79a81e01/work/records/phase-001/issue-43/task-001.md#closure-status)의 공통 참조·버전 계약을 사용한다. 실제 값에 의존하는 설계는 [#45의 필요한 입력 확인](https://github.com/Mi-no-Kim/LumiaWiki/blob/76e26221ce8b334b462273660c9b4b7e79a81e01/work/records/phase-001/issue-43/issue.md#data-timing) 결과를 관련 설계값 확정·구현 전에 받으며, 미확보 시 의존하는 설계값 확정·구현·완료 판정만 제한한다. 실제 자료 조사 보류를 유지하고 #45 전체 완료를 선행 조건으로 삼지 않는다.

| 결정 내용 | 적용 범위 | 근거 |
|---|---|---|
| 현재 허용은 계획·관련 기록·GitHub 하위 등록/표시 정리다. 실제 자료 작업은 보류하며 제품 구현·DB 변경 권한으로 확대하지 않는다. | 준비와 실제 변경 | [Issue의 계획 범위](https://github.com/Mi-no-Kim/LumiaWiki/blob/76e26221ce8b334b462273660c9b4b7e79a81e01/work/records/phase-001/issue-43/issue.md#plan-scope) 및 위 Task 조건 |
| 버전별 귀속 행을 보관한다. 변경 없는 스킬 버전·연결 JSON을 재사용하고 새 연결에는 소속 아이템 버전의 기준 패치를 기록한다. 독립 연결 버전·별도 최신 원본 사본은 만들지 않는다. | 아이템 버전·스킬 연결 | [Issue가 연결한 공유 계약](https://github.com/Mi-no-Kim/LumiaWiki/blob/76e26221ce8b334b462273660c9b4b7e79a81e01/work/records/phase-001/issue-43/issue.md#pending)·[채택한 결정](https://github.com/Mi-no-Kim/LumiaWiki/blob/76e26221ce8b334b462273660c9b4b7e79a81e01/work/records/phase-001/issue-43/task-002.md#activity) |
| 스킬 대상과 버전을 구별하고 한 아이템에 여러 스킬을 연결할 수 있다. 연결은 스킬 대상·특정 스킬 버전·게임 패치를 직접 참조하며, 지정 버전의 소속 대상과 연결 대상이 같아야 한다. JSON은 연결에 두고 이름·설명은 스킬 버전에 보존한다. 실제 설명은 지정한 버전을 따른다. | 스킬·연결의 귀속과 참조 계약 | [기존 스킬 참조 요구](https://github.com/Mi-no-Kim/LumiaWiki/blob/76e26221ce8b334b462273660c9b4b7e79a81e01/docs/details/product/게임%20데이터%20변경%20관리.md#item-skills) |
| 아이템 버전은 종류 ID 하나를 필수 참조한다. 종류 이름·계층만 바뀌면 새 아이템 버전을 만들지 않고 아이템의 소속 종류 변경은 버전으로 보존한다. | 종류 참조·버전 변경 | [Issue 수용 조건](https://github.com/Mi-no-Kim/LumiaWiki/blob/76e26221ce8b334b462273660c9b4b7e79a81e01/work/records/phase-001/issue-43/issue.md#acceptance)·[배정 계약](https://github.com/Mi-no-Kim/LumiaWiki/blob/76e26221ce8b334b462273660c9b4b7e79a81e01/work/records/phase-001/issue-43/task-002.md#plan) |
| 수치는 NUMERIC/BigDecimal로 다루고 5%는 5로 저장한다. 같은 버전의 같은 능력치 종류는 중복 등록하지 않는다. item_stat을 원본, stat_json을 원본에서 만든 표시 캐시로 두며 자료 의존 값을 가정하지 않는다. | 능력치 저장·매핑·캐시 | [Issue가 받은 공통 기준](https://github.com/Mi-no-Kim/LumiaWiki/blob/76e26221ce8b334b462273660c9b4b7e79a81e01/work/records/phase-001/issue-43/issue.md#plan)·[능력치 규칙](https://github.com/Mi-no-Kim/LumiaWiki/blob/76e26221ce8b334b462273660c9b4b7e79a81e01/docs/details/product/아이템%20탐색과%20상세.md#stat-information) |
| JSON은 jsonb/JSON 트리, 설명은 원문 문자열로 둔다. 중복 객체 키는 트리 변환·DB 저장 전에 감지한다. JSON 값 보존은 공백·객체 키 순서의 원문 보존과 구분한다. | 스킬 JSON 입력·저장·조회 | [배정의 기존 선택](https://github.com/Mi-no-Kim/LumiaWiki/blob/76e26221ce8b334b462273660c9b4b7e79a81e01/work/records/phase-001/issue-43/task-002.md#plan)·[JSON 기준](https://github.com/Mi-no-Kim/LumiaWiki/blob/76e26221ce8b334b462273660c9b4b7e79a81e01/docs/개발%20기준.md#skill-json) |
| 특정 버전의 입력 오류 정정을 새 실제 게임 패치로 만들지 않는다. | 기본 수정·버전 보존 | [변경·정정 기준](https://github.com/Mi-no-Kim/LumiaWiki/blob/76e26221ce8b334b462273660c9b4b7e79a81e01/docs/details/product/게임%20데이터%20변경%20관리.md#change-and-correction) |

상세 이유·대안·논의는 Issue가 채택한 위 원천에서 확인한다.

<a id="acceptance"></a>
## 완료 조건·확인 방법

Task 전체 결과의 수용 기준이다. 현재 허용된 계획 정리와 전체 완료는 구분한다.

| 완료 조건 | 확인 방법 |
|---|---|
| 합의한 버전·연결 기준으로 저장·조회되고 값과 입력/참조 검사가 보존된다. | 저장 입력·조회 결과와 위 수치/JSON 규칙을 대조하고 잘못된 입력·참조의 거부를 확인한다. |
| 같은 버전의 원본/캐시가 일치하고 다른 버전의 정상 정보가 유지된다. | 원본·캐시와 수정 전후·버전별 결과를 대조한다. |
| 후속 검색·상세와 결합 조회/갱신에 필요한 계약이 전달된다. | 담당 결과·참조·갱신 계약을 후속 과제의 배정과 대조한다. |
