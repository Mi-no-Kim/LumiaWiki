# 시즌·아이템 DB 구조와 저장·조회 코드 구현

<a id="summary"></a>

## 현재 요약

- 제목: 시즌·아이템 DB 구조와 저장·조회 코드 구현
- 실제 GitHub Issue: [Mi-no-Kim/LumiaWiki #43](https://github.com/Mi-no-Kim/LumiaWiki/issues/43)
- 소속 Phase: [Phase 001](../phase.md#summary)
- 상태: 진행 중
- 현재 진행 위치: Task 001의 공통 8개 표/Java·격리/로컬 검증 결과를 [PR #71](https://github.com/Mi-no-Kim/LumiaWiki/pull/71)로 이 Issue 브랜치에 반영했고 전용 Task 브랜치를 정리했다. 단위 30·통합 11건의 [생성/검증 결과](artifacts/task-001-creation.md#current)와 PR CI 8개 통과를 확인했다. [Task 43-002](task-002.md#result)는 아이템·능력치·스킬 저장·조회 구현, 격리 DB 검증과 계약 인계를 완료했고 [PR #79](https://github.com/Mi-no-Kim/LumiaWiki/pull/79)의 부모 통합과 병합 후 CI를 확인했다. [Task 43-003](task-003.md#summary)은 [PR #91](https://github.com/Mi-no-Kim/LumiaWiki/pull/91)로 V4·V5를 병합했고 [기존 개발 DB의 V2~V5 적용](artifacts/task-003-execution.md#development-db-v5)을 마쳤다. 004는 예정이다. 실제 자료 작업은 보류한다.
- 허용 범위: 승인한 PR #91 부모 병합과 기존 개발 DB `lumiawiki/public`의 V2~V5 적용을 마쳤다. 실제 자료 조사·등록·교정은 보류한다.
- 다음 판단/행동: 선행 기준을 반영했다. [Task 43-005](task-005.md#summary)의 정정 후보를 검수해 부모 PR로 제출한다. 43-003 저장 합의와 실제 자료 작업 보류를 유지한다.
- 작성 근거: [Task 005](../issue-15/task-005.md#summary) · [전체 실행 순서](../issue-15/artifacts/task-005-issue-outline.md#sequence). 실제 자료 작업 보류를 유지한다.

<a id="parent-integration"></a>

### 최신 Phase 반영

- 대상·이유: 기존 Issue `76e26221ce8b334b462273660c9b4b7e79a81e01`에 main `77bc4229f882943d20b9539c5a25ccd9f5769643`을 포함한 직계 부모 Phase `72c27a11dcb878c945914992ae2054125d8bba73`를 결합한다. Task 001의 공통 8개 표·Java·완료 결과와 기존 Task 본문을 보존한다.
- 충돌 판단: 종료 상태의 실제 확인 안내와 main의 Task 자기 수용/부모 수용·재검증 기준을 함께 유지한다. DB 문서와 스킬 문서의 포맷 지원을 결합하고, 기존 원문·자료/증거 제외는 유지한다. hook 현황의 기존 Issue 검증 근거는 보존하며 바뀐 조합은 재확인 필요로 표시한다. 고정 기존 기록 36개 목록은 변경하지 않는다.
- 검증 결과·한계: Phase의 스크립트 회귀 179개·별도 상태 회귀 8개를 동일 원천 범위에서 재사용했다. 달라진 경로 분류는 품질 회귀 21개(환경 조건으로 1개 제외)와 `node --test scripts/quality-db-docs.test.mjs` 3개를 통과했다. [최소 실행 근거](artifacts/parent-integration-tdd.md)의 현재 후보 대응과 인덱스의 현황·주석·기록·형식 검사를 확인했다. 자체·별도 검수로 문서/원천 결합을 확인하며 실제 게임 자료·DB 확인과 원격 CI는 수행하지 않는다.

<a id="java-ci-prepared-issue"></a>

### 43-005 제출을 위한 Phase 선행 기준

- 순서: [Phase의 승인된 단계별 반영](../phase.md#java-ci-staged-rollout)에 따라 별도 계획과 첨부 TDD를 읽을 수 있는 부모 기준을 먼저 반영한다. 43-005 정정을 부모에 반영한 뒤 Java CI를 도입한다.
- 사용자 확정 범위: [43-005 파일별 승인](codex://threads/01a20764-c112-72f3-9e64-9b461020cf7a)에 따라 catalog 운영 Java 31개·전용 테스트 5개를 삭제하고 공통 `ApiFailure`의 catalog 전용 확장만 복원한다. 공통 오류 응답·부트스트랩·실행 설정·V1~V5 SQL 및 43-003의 저장 결과 합의를 보존한다.
- 확인 범위: 43-005 전용 기록과 실행 근거를 읽는 도구를 확인하고, 기존 #43의 제품 코드·DB를 보존한다. Java CI 최초 설치 승인 파일 12개와 그 이력은 활성화 단계까지 유보한다.
- 후보 검사 결과: [경로 분류 TDD 근거](artifacts/parent-integration-tdd.md) 21건 중 20건이 통과했고 Windows 심볼릭 링크 관련 1건은 제외됐다. DB 문서 분류 Node 회귀 3건도 통과했다.
- 검증: [Phase 선행 Quality](https://github.com/Mi-no-Kim/LumiaWiki/actions/runs/45778467394)를 확인했다. 같은 검사기 입력의 회귀 근거는 재사용하고 #43의 경로 분류와 실제 인덱스를 별도로 확인한다.

<a id="goal"></a>

## 목표와 범위

시즌·게임 패치·지역과 아이템 관련 정보를 보존하고 같은 기준 패치로 저장·수정·조회할 수 있는 DB 구조와 코드를 만든다. 기능별 검색/제작/루트 동작과 실제 원자료 변환·등록은 해당 Issue에 연결한다.

<a id="plan"></a>

## 선행 결과와 필요한 입력

- [실행 기반](../issue-42/issue.md#foundation)의 DB 접속·테스트·공통 API 구성이 필요하다. 화면은 검색·기본 상세 Issue가 맡고 여기서는 저장값·왕복·참조 정합성을 확인한다.
- [Task 001의 정보·보존 요구](../issue-15/artifacts/task-001-discussion-details.md#handoff-decisions)와 공통 자료형 기준을 따른다. 실제 값 의존 설계에는 [자료 Issue의 입력 확인](../issue-45/issue.md#data) 결과를 받으며 자료 Issue 전체 완료를 기다리지 않는다.

<a id="database"></a>

## 시즌·아이템 DB 구조와 저장·조회 코드 구현

<a id="task-creation"></a>
<a id="task-outline"></a>

### 보유 Task

로컬 Task 5개를 이 Issue에 등록하고 GitHub sub-issue 관계를 확인했다. 각 Task의 번호·URL·상태와 실행·검증 계획은 해당 Task 원본에서 관리한다.

| Task                                                                       | 맡는 결과                                         | 상태    |
| -------------------------------------------------------------------------- | ------------------------------------------------- | ------- |
| [Task 43-001: 공통 식별·시즌/패치·지역·분류](task-001.md#summary)          | 공유 관계 선행 검토와 공통 참조·정렬·분류 기반    | 완료    |
| [Task 43-002: 아이템·능력치·스킬 저장/조회](task-002.md#summary)           | 아이템/스킬 버전과 원본·캐시의 저장/조회          | 완료    |
| [Task 43-003: 제작·획득·배달 관계 저장/조회](task-003.md#summary)          | 같은 패치의 제작·획득·배달 관계와 상태            | 진행 중 |
| [Task 43-004: 유효 버전 조회·참조 일치·갱신 처리](task-004.md#summary)     | 관계 결합의 유효 이력 조회·기본 수정·일치 검증    | 예정    |
| [Task 43-005: catalog 구현 철회와 V1~V5 DB 기반 보존](task-005.md#summary) | `catalog` 철회·기존 공통 API와 V1~V5 DB 기반 보존 | 진행 중 |

<a id="assignment-005"></a>

### Task 43-005 catalog 구현 철회 배정

- 확정 근거: [이 대화에서의 사용자 결정과 Task 생성 요청](codex://threads/01a20764-c112-72f3-9e64-9b461020cf7a). 사용자는 현재 `catalog` 작성을 허용한 적이 없다고 확인했고, 구현 철회와 V1~V5 DB 기반 보존을 하나의 #43 하위 Task로 정했다. [#95 인계](../issue-95/artifacts/task-005-execution.md#catalog-handoff)를 배정 근거로 사용한다.
- 전달사항: [확정 전달사항](artifacts/task-005-assignment.md) (`r001`).
- 식별·등록: `43-005`, [Task 본문](task-005.md#summary). 부모 보유 목록과 추적·작업 파일, 등록 전 실제 GitHub 하위 목록의 43-001~004를 대조했고 005와 충돌하는 기존 Task가 없음을 확인했다. [GitHub #125](https://github.com/Mi-no-Kim/LumiaWiki/issues/125)의 부모는 #43이고 milestone은 #1이다.
- 수용과 의존: 43-001·002·003의 `catalog` 변경 영향을 맡되 기존 SQL·공통 API 및 합의한 저장 결과를 보존한다. 연결 파일별 처리와 제출 순서는 실행 전에 확정한다. 이번 결정은 Task 생성과 등록까지다.

<a id="acceptance"></a>

### 합의한 수용 조건

- 시즌 1·v1.0.0을 포함한 합의 모델을 저장·조회할 수 있고 식별값·정렬값·관계가 구별된다. 스키마와 Java/API 값 왕복이 채택 기준을 충족한다. 실제 게임 자료 전체 등록은 자료 Issue가 담당한다.
- 버전 관리 대상은 조회 패치의 유효한 이력을 선택하고 과거 상태를 보존한다. 종류 이름·상하위 관계는 버전 없이 현재 기준을 사용하고 아이템 자체의 소속 종류 ID 변경 이력은 보존한다. 스킬 동시 참조·삭제 전 상태·노출 구분·필요 참조의 일치를 확인하며 현재값의 별도 원본 사본을 전제하지 않는다.
- 기본 수정과 원본/캐시 갱신이 일치하고 검색·제작·루트가 사용할 저장/조회 결과와 인터페이스가 준비된다. 수식 실행·버전 선택기 등 후속 기능은 추가하지 않는다.

실제 수치 범위·소수 정밀도·미확인 날짜 허용·JSON 필수 내용 등 자료 의존 결정은 구현 전에 제공 자료를 확인한다. 자료 Issue의 입력 확인 결과가 필요한 부분은 그 결과를 받되, 자료 Issue 전체 완료를 선행 조건으로 삼지 않는다. 현재 보류 중인 자료를 조사하거나 값을 가정하지 않는다.

<a id="pending"></a>

## Task 선후 관계와 남은 결정

- 큰 순서는 공통 구조 → 아이템 → 관련 관계 → 결합 조회/갱신이다. 이력·참조·캐시 일치는 각 관계의 첫 설계부터 반영하고 Task 43-004에서 결합 확인한다.
- 공유 버전·참조 관계는 Task 43-001에서 아이템·스킬·제작/획득까지 먼저 검토한다. 물리 설계·세부 규칙은 각 담당 Task의 구현 전에 확인한다.
- 미정은 [Task 43-001](task-001.md#decisions)·[002](task-002.md#decisions)·[003](task-003.md#decisions)·[004](task-004.md#decisions)의 담당·필요 입력·결정 시점을 따른다. 담당 배정은 AI의 임의 결정이나 자료 보류 해제를 허용하지 않는다.
- [43-003 장착 부위 정정 배정](#equipment-slot-assignment-revision)을 제작·획득·배달 설계 검토보다 먼저 수행한다.
- [기존 책임 배정](../issue-45/issue.md#ownership)에 따라 #43은 공통 저장·기본 수정·참조/캐시 일치를, #45는 실제 등록·교정 실행·실패 복구와 자료 수용을 맡는다. 자료 Issue에서 필요한 선행 코드 보완도 수행할 수 있다.

<a id="plan-scope"></a>

## 계획 범위와 사용자 결정 방식

- Issue 준비/등록과 Task 실행 변경의 분리 뒤 승인한 Task 001의 제출·부모 squash 통합·브랜치 정리를 마쳤다. 완료한 결과·기존 보존 커밋과 승인한 DB 범위를 유지하며 새 제품 목표나 Task를 추가하지 않는다. Issue/Phase 전체 통합과 실제 자료는 보류한다. 기존 개발 DB V2~V5 적용은 이후 별도로 승인받아 마쳤다.
- 새 선택은 내용·대안·추천 이유·장단점/영향·필요 입력을 사용자에게 먼저 제시한다. 응답 전에는 그 선택을 확정하거나 의존하는 스키마·검증 규칙·동작을 구현하지 않는다. 기존 합의와 새 선택을 구별한다.
- 실제 자료 조사·확보·변환·등록·교정은 계속 보류한다. 통제한 검증 입력과 실제 게임 자료는 구별하고 자료 의존 미정은 임의 값으로 채우지 않는다. 입력 부족은 영향을 받는 구현·완료 판정만 제한한다.
- 확정한 공통 키·관계 개수·일반 참조/필수값과 F4·S1~S3를 유지한다. 공통 8개 표/제약·보호/권한 수단과 오류 계약은 확정/구현했다. 후속 관계·캐시 갱신·API/응답·수량/JSON은 각 담당 Task의 미정이다. 이번 통합은 완료한 Task 001 결과와 직접 관련된 기록/절차 보완만 포함한다.

<a id="equipment-slot-assignment-revision"></a>

### Task 43-003 장착 부위 정정 배정

사용자 합의로 장착 부위의 중복 저장을 정정한다. [43-002에서 반영한 V3](task-002.md#result)의 `equipment_slot`을 후속 마이그레이션으로 제거하고, `category_id`로 이어진 분류 역할과 계층으로 조회 부위를 판단한다. 같은 분류 ID의 이름 변경은 장착 부위를 유지한다. 같은 저장 코드의 변경을 분리해 검증할 수 있도록 43-003 첫 할 일로 배정한다. 적용 범위와 수용 조건은 [개정 전달본](artifacts/task-003-assignment.md#equipment-slot-revision)에 둔다.

<a id="assignment-basis"></a>
<a id="skill-storage-assignment-revision"></a>

### Task 43-002 스킬 저장 범위 확정

P1은 아이템 버전과 지정 스킬 버전의 연결, 해당 버전의 설명 원문과 임시 표시 설명을 저장한다. 계산용 연결 JSON은 P3에서 실제 계산 입력을 바탕으로 설계한다. [개정 배정](artifacts/task-002-assignment.md#assignment-revision)

<a id="conditions"></a>

격리 검증은 합성 자료를 사용하며, 실제 DB에 표를 생성하기 전에는 전체 구조와 정확한 실행 대상을 확인한다.

<a id="execution"></a>

## 공통 실행·검증 절차

1. 필요한 원천·선행 코드·현재 수용 조건을 확인하고, 새 선택과 자료 의존 항목을 [담당 Task의 미정](#pending)에 대조한다. 필요한 선택은 사용자에게 먼저 요청한다.
2. 합의한 조작·입력·기대 결과를 사용자 확인 목록으로 공유한 뒤, 실패 테스트 → 최소 구현 → 통과 → 리팩터링을 수행한다. 통제한 검증 입력은 실제 게임 자료와 구별한다. 계획 준비에서 테스트 자료를 생성하거나 실행하지 않는다.
3. 공용 `db/migration/`의 Flyway·Java 매핑·저장/조회 계약을 기존 기준에 맞춰 검증한다. DB 없는 검사는 `backend\gradlew.bat -p backend test`, 격리 PostgreSQL/Flyway 검사는 `backend\gradlew.bat -p backend integrationTest`를 사용한다. 후자는 기존 Testcontainers·test 프로필을 사용하고 개발 DB·개인 `.env`·개발 볼륨을 건드리지 않는다.
4. 수용하려는 후보에는 기존 `npm run check:backend`의 포맷·테스트·빌드를 적용한다. 문서·API·프런트 변경이 생기면 해당 영역의 기존 검사를 연결한다. 대상별 테스트 클래스·필터·실행 명령은 코드/계약 결정 뒤 확정하고 구현 전에 공유한다.
5. 자동 검사·AI 직접 확인·사용자 확인 결과를 구분한다. 미확인·입력 부족이 필수 완료 조건에 영향을 주면 해당 Task를 완료로 판정하지 않는다. 커밋을 준비할 때는 기존 자체·별도 에이전트 검수 절차를 적용한다.

화면은 기존 배정대로 [#44 검색·기본 상세](../issue-44/issue.md#search-detail)가 맡는다. #43은 저장값·왕복·참조 정합성과 재현 가능한 요청/응답 또는 실행 절차를 확인하며 #44의 완성을 선행 조건으로 추가하지 않는다. 외부 API·개발 전용 확인 경로가 필요한지는 사용자와 먼저 정한다. 제품 화면에서 같은 자료를 확인하는 결과는 #44·#45, 제작·루트 결과는 #46·#47에서 연결한다. 내부 검사를 화면 확인으로 표시하지 않는다.

<a id="data-timing"></a>

## 실제 자료 작업이 이루어지는 단계

| 단계                               | 시점과 선행 조건                                                                                                                              | 담당·현재 상태                                                                                               |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| 설계에 필요한 실제 입력 확인       | #43의 특정 컬럼/검증·관계 설계에 실제 값이 필요해질 때 요청 가능. 사용자 재개 지시와 대상·제공 위치·출처·기준 버전·해석/허용 범위를 먼저 확인 | #45의 제공 입력 확인 Task 윤곽. #43 전체 완료·#44 화면 완성을 기다릴 필요는 없지만 현재 보류라 실행하지 않음 |
| 실제 DB 등록·교정·원자료/출처 연결 | 보류 해제·제공 입력, 필요한 저장/검증 구조와 등록/교정 수단, #44의 확인용 검색·기본 상세가 준비된 뒤                                          | #45. 테이블별 진행에 따라 등록·화면 대조·교정을 연결하며 현재 미착수                                         |
| 실제 자료로 제작·루트 결과 대조    | 합의한 큰 순서에 따라 기준 자료 등록·화면 대조 뒤, 해당 기능·입력과 화면이 준비된 때                                                          | #46·#47, 전체 연결/잔여는 #48. 현재 후속 단계                                                                |

구현 파일 작성·격리 DB 검증·현재 DB 조회/적용과 위 실제 자료 단계의 [재개 시점](https://github.com/Mi-no-Kim/LumiaWiki/blob/9b8773ed5a26b799eac971ea8fe60949e14c4d0a/work/records/phase-001/issue-43/artifacts/task-001-pending.md#resume-timing)을 구별한다. 최초 구동 B1~B3는 구현·격리 검증을 수행했다. 실제 입력 확인은 필요한 공통 저장 계약 검토와 병행할 수 있지만 자료 보류 해제가 먼저 필요하다.

변환 산출물 형식·검증·보관·교정 수단과 구체 처리 순서는 #45의 준비에서 실제 제공 자료를 입력으로 정한다. Task 계획 작성과 구현 준비는 자료 보류 해제를 뜻하지 않는다. 필요한 입력이 도착하지 않으면 해당 스키마/검증·완료 판정만 제한한다. 실제 자료가 필요한 부분을 임의 값이나 통제한 검증 성공으로 대체해 #43 또는 P1 전체를 완료로 표시하지 않는다.

<a id="preparation-verification"></a>

## Task 계획과 공유 관계 검토의 확인 범위

- 네 Task의 실행/검증 계획과 담당 미정은 [목적별 상세](https://github.com/Mi-no-Kim/LumiaWiki/blob/9b8773ed5a26b799eac971ea8fe60949e14c4d0a/work/records/phase-001/issue-43/artifacts/task-001-shared-version-references.md#summary)를 따른다. [복원/정비](https://github.com/Mi-no-Kim/LumiaWiki/blob/9b8773ed5a26b799eac971ea8fe60949e14c4d0a/work/records/phase-001/issue-43/artifacts/task-001-pending.md#conditional-exceptions)는 필요 시점에 다룬다. 001의 합의 파일과 승인한 격리/로컬 DB 적용을 마쳤으며 실제 자료 작업은 계속 보류한다.
- 최초 구동 구현·격리 DB 검증은 [Task 001 결과](task-001.md#verification)를 따른다. 공통 도메인 구현과 기록/절차 보완을 PR #71로 이 Issue 브랜치에 통합했고 반영 결과를 대조했다. 후속 본행·결합 조회/자료·제품 API 검증과 Issue 전체 수용은 남아 있다. GitHub sub-issue 4개 등록/관계·상태를 유지한다.

<a id="related"></a>

## 기준·검증 배정

[Task 003 데이터 인계](../issue-15/artifacts/task-003-handoff.md#handoff-decisions) · [대표 사례 배정](https://github.com/Mi-no-Kim/LumiaWiki/blob/9b8773ed5a26b799eac971ea8fe60949e14c4d0a/work/records/phase-001/issue-15/artifacts/task-005-handoff-requirements.md#case-owners) · [검증 사례 V01~V12](../issue-15/artifacts/task-004-verification-plan.md#cases)
