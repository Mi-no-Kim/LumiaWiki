# Task 43-002 — 아이템·능력치·스킬 저장/조회

- 태그: 논의, 결정, 실행, 검수, 커밋

<!-- task-rule:tags
Task 태그는 전체 활동의 요약이고 할 일 태그는 해당 행동의 표시다. 조사·논의·결정·실행·검수·커밋 중 필요한 여러 개를 쉼표로 구분한다.
계획에 있는 할 일의 태그를 Task 태그에 반영하고 계획을 바꿀 때 함께 맞춘다. 태그는 상태·권한·위임을 추가하지 않는다.
진행 AI가 배정·합의 범위 안에서 태그를 보완·정정하며 현재값은 이 Task에서 관리한다. 생성 입력을 현재값 사본으로 고치지 않는다.
완료된 행동의 태그도 유지하며 실제 완료는 체크와 근거로 구별한다.
Task 태그를 모든 할 일에 일괄 적용하지 않는다. 각 행동의 태그와 그 행동에 적용되는 배정·합의·권한 조건을 함께 확인한다.
조사: 허용된 자료의 사실·근거를 정리한다. 조사 결과만으로 미위임 선택을 확정하지 않는다.
논의: 근거·대안·영향을 사용자에게 제시하고 응답·논의 내용을 확인한다. 질문만 제시하거나 무응답인 상태를 논의 완료로 처리하지 않는다.
결정: 배정·합의에서 정한 주체만 선택한다. AI는 명시적으로 위임된 범위에서만 결정하고 근거를 남긴다. 주체·위임이 불명확하면 확인한다.
실행: 합의한 변경을 실제 대상에 반영하는 행동이다. 허용 범위·선행 조건·필요한 논의와 결정을 확인한 뒤 의존 실행을 한다.
검수: 완료 기준과 태그에 실제 행동·논의/결정 근거가 맞는지 대조하고 결함·미확인을 남긴다.
커밋: 실제 후보의 필수 검수·보완과 권한·실행 조건을 충족한 뒤 수행한다. 조건부 계획을 실행 허용으로 해석하지 않는다.
여러 태그의 조건은 해당 행동에 함께 적용한다. 그 행동에 필요한 논의·결정 근거가 없으면 해당 논의·결정의 완료 처리, 그 선택의 확정, 그에 의존하는 실행을 제한한다.
전체 계획·공통 준비를 갖춘 상태에서 이미 허용된 독립 조사·준비는 계속할 수 있다. 같은 논의·결정 근거는 재사용하며 재승인을 요구하지 않는다.
태그 누락·추가·삭제로 기존 논의·결정·권한 조건을 없애거나 확대하지 않는다. 불명확한 태그는 미정·미확인과 필요한 확인을 남기고 근거를 확인한다.
-->

공통 절차: [Task 공통 절차](https://github.com/Mi-no-Kim/LumiaWiki/blob/77bc4229f882943d20b9539c5a25ccd9f5769643/harness/Task%20%EA%B3%B5%ED%86%B5%20%EC%A0%88%EC%B0%A8.md)

GitHub sub-issue: [Mi-no-Kim/LumiaWiki #68](https://github.com/Mi-no-Kim/LumiaWiki/issues/68). 부모 Issue #43의 기존 하위 Issue이며 로컬 Task 순번과 GitHub 번호는 별개다.

<!-- task-rule:recording
이 본문은 현재 유효한 계획·합의·상태·전체 결과를 관리한다.
같은 항목은 현재 내용으로 갱신하고 상세 수행 과정은 수행 기록에 둔다.
할 일 안의 세부 선택·대안 비교·논의 근거는 해당 수행 기록에 둔다.
후속 행동·검수·수용 판단·진행 조건에 필요한 결정은 현재 합의에 결론·핵심 이유·조건과 상세 기록 링크를 남긴다.
미정·제안·확정·실제 수행을 구별하고 미발생 승인이나 결과를 채우지 않는다.
본문의 task-rule 주석은 갱신 중에도 유지하고 해당 조건에서 준수한다.
-->

<!-- task-rule:start
착수·재개·조건 변경·주요 전환·수용 판단 전에 현재 계획과 해당 행동에 필요한
입력·권한·선행 결과·등록·브랜치 등의 실제 상태를 확인한다.
부족한 조건에 의존하는 행동은 제한하고 해소 조건을 남긴다.
전체 계획과 공통 준비를 갖췄다면 이미 허용된 독립적인 일은 진행할 수 있다.
-->

<a id="summary"></a>

## 현재 요약

<!-- task-rule:summary
상태는 예정·진행 중·중단·완료·취소 중 실제 상태 하나를 쓴다.
신규·미착수만 예정으로 두고 기존 실제 상태를 초기화하지 않는다.
현재 위치는 실제 작업·근거 구역으로 연결한다.
다음 행동은 현재 허용된 행동을, 막힌 조건은 제한·해소 조건·근거를 적는다.
상태의 상세 의미·전환과 종료 판단은 공통 절차를 따른다.
-->

- 상태: 완료
- 현재 진행 위치: [후속 저장·조회 구현과 두 격리 DB의 V3 통합 검증](artifacts/task-002-execution.md#isolated-v3-results)과 [#44·43-004 계약 인계](artifacts/task-002-execution.md#storage-handoff)를 마쳤고 [V2 이관 행의 삭제·복귀를 보완·검증](artifacts/task-002-execution.md#v3-existence-regression)했다.
- 다음 행동: [부모 Issue](issue.md#summary)로 통합할 PR을 제출한다.
- 막힌 조건: V3 실행 승인은 위 두 임시 PostgreSQL DB의 검증에 한정된다. 실제 자료 등록·교정과 기존 개발 DB 적용은 보류한다.

<a id="assignment"></a>

## 전달사항 참조

<!-- task-rule:assignment
입력 양식이 아닌 실제 확정 전달사항과 부모의 배정 기록을 읽어 대조한다.
배정 원문의 사본을 이 본문에서 별도로 관리하지 않는다.
배정된 결과·범위·기존 결정·완료 조건·권한을 바꿔야 하면 Issue에서 변경을 합의하고
기존 전달본을 보존한 새 개정본과 참조 갱신·영향 확인을 처리한다.
-->

- 부모 Issue: [Issue #43](issue.md#summary)
- 적용 전달본: [스킬 저장·검증 범위 개정](artifacts/task-002-assignment.md#assignment-revision). 최초 배정은 `d6adc6f`의 [부모 보유 Task·수용 조건](https://github.com/Mi-no-Kim/LumiaWiki/blob/d6adc6f0eaf3a3111a09ea14e37ba6491f378dc1/work/records/phase-001/issue-43/issue.md#acceptance)과 [최초 Task의 목적·범위·완료 조건](https://github.com/Mi-no-Kim/LumiaWiki/blob/d6adc6f0eaf3a3111a09ea14e37ba6491f378dc1/work/records/phase-001/issue-43/task-002.md#goal)에서 확인했다.
- 전달본 식별·근거: 최초 배정 `d6adc6f` · [부모의 배정 개정과 확정 근거](issue.md#skill-storage-assignment-revision).
- 기준 기록: [Issue #43의 기존 합의와 배정 근거](issue.md#assignment-basis) · [Task 배정·등록 기록](issue.md#task-creation).

최초 배정에 개정 전달사항을 적용한다. 최초 배정 당시의 별도 정식 전달본은 미확인이다.

<a id="sequence"></a>
<a id="plan"></a>
<a id="decisions"></a>

## 계획과 합의

<!-- task-rule:plan
첫 할 일 실행 전에 목표 달성부터 필요한 검증·검수·허용된 커밋·종료까지
전체 계획을 수립·합의한다. 배정 합의와 현재 전체 계획의 제안/합의·적용 범위·근거를 구별한다.
계획 합의를 실행 권한의 추가로 해석하지 않는다.
조사 후 정할 선택은 결정 시점과 후속 계획을 구체화할 시점을 포함한다.
합의·위임 범위 안에서는 할 일을 조정하고 중요한 변경 이유·근거를 남긴다.
논의 응답·새 사실·조건 변경으로 판단이나 계획이 달라지면 다음 관련 행동 전에
해당 합의·남은 결정·할 일·확인 방법·태그·연결을 현재 내용으로 갱신한다.
다음 행동·막힘이 달라지면 현재 요약도 맞추고 상세 수행 근거는 보존한다.
기존 합의·범위·완료 기준·권한을 바꾸거나 필수 확인을 생략해야 하면 관련 실행 전에 논의한다.
사용자 확인 조건에 도달하면 관련 실행 전에 확인하고 통상적인 조정마다 재승인을 요구하지 않는다.
-->

- 대상·준비: [대상·준비와 현재 권한](#preparation)을 따른다.
- 현재 합의: [적용 계약과 확정한 설계](#activity)를 따른다.
- 남은 결정: [남은 결정과 필요한 입력](#remaining-decisions)을 따른다. A안으로 해결된 키 방식과 후속 세부 선택을 구별한다.
- Task 전체 확인: 최초 배정을 [완료 기준과 확인 계획](#verification)에 대조했다.
- 수행 기록: [배정 대조·설계 논의와 결정 근거](artifacts/task-002-execution.md#work-contract).

<a id="goal"></a>
<a id="preparation"></a>
<a id="conditional-guidance"></a>

### 대상·준비와 현재 권한

담당 결과는 아이템 기본 정보·버전, 능력치 원본·표시 캐시, 스킬 연결과 지정 버전의 설명 원문을 저장·조회하는 것이다. 검색 일치 규칙·화면 구성·수식 해석/실행은 이 Task에서 결정하지 않는다.

- 선행 기반: [Task 43-001의 완료·후속 인계](task-001.md#closure-status)를 적용한다.
- 부모·브랜치: 부모 Issue의 변경은 `4da7318`로 반영했다. `task/43-002-item-storage`에서 저장·조회 구현과 검증을 마쳤다.
- 입력: 기존 [아이템·능력치 요구](https://github.com/Mi-no-Kim/LumiaWiki/blob/9b8773ed5a26b799eac971ea8fe60949e14c4d0a/docs/details/product/%EC%95%84%EC%9D%B4%ED%85%9C%20%ED%83%90%EC%83%89%EA%B3%BC%20%EC%83%81%EC%84%B8.md#stat-information), [스킬 연결 요구](<../../../../docs/details/product/게임 데이터 변경 관리.md#item-skills>), [개발 기준의 스킬 저장](<../../../../docs/개발 기준.md#skill-json>)·[능력치 수치](<../../../../docs/개발 기준.md#stat-numeric>)와 확정 계약을 사용한다.
- 현재 권한: 최초 6개 표와 후속 저장·조회 구현, [지정된 두 격리 DB의 V2 검증](artifacts/task-002-execution.md#storage-creation-review) 및 [V3 검증](artifacts/task-002-execution.md#v3-precreation-review)을 허용받았다. 실제 자료 등록과 기존 개발 DB 적용은 보류한다.
- 자료 의존: [공식 1.0.0 아이템 표](https://docs.google.com/spreadsheets/d/e/2PACX-1vTjbw1TSUfgr0KwrMIW0YSjvYvtQEHnFrHX54Qgz-DpbPPtxz801OAL7dQKgkigAB6EHktuYYgZGRsG/pubhtml)를 기준으로 설계한다. 최대 중첩 수량은 미확인 상태를 허용한다. 나머지 결정은 각각에 필요한 입력이 확인된 범위에서 확정한다.
- 화면·확인 경로: [공통 검증 경계](issue.md#execution)에 따라 제품 화면은 #44가 맡고 이 Task는 [Spring 서비스와 격리 PostgreSQL](#storage-verification-path)에서 저장·조회를 확인한다. [최초 검증의 입력·기대 결과·재현 명령](artifacts/task-002-execution.md#initial-verification)을 합의했다.
- 신규 구조 실행: [부모의 실행 조건](issue.md#conditions)에 따라 실제 생성 직전에 전체 구조와 정확한 실행 대상을 사용자에게 확인받는다.

<a id="activity"></a>

### 현재 합의

#### 선행 계약과 적용 범위

- [공유 버전·참조 계약](https://github.com/Mi-no-Kim/LumiaWiki/blob/9b8773ed5a26b799eac971ea8fe60949e14c4d0a/work/records/phase-001/issue-43/artifacts/task-001-version-references.md#agreed)에 따라 귀속 행은 버전별로 보관하고 분류는 현재 기준을 적용한다. 아이템 자체의 종류 변경은 버전으로 보존하고, 완성된 버전은 [종류 하나를 필수로 참조](https://github.com/Mi-no-Kim/LumiaWiki/blob/9b8773ed5a26b799eac971ea8fe60949e14c4d0a/work/records/phase-001/issue-43/artifacts/task-001-common-model.md#f2-cardinality)한다.
- [공통 모델](https://github.com/Mi-no-Kim/LumiaWiki/blob/9b8773ed5a26b799eac971ea8fe60949e14c4d0a/work/records/phase-001/issue-43/artifacts/task-001-common-model.md#current)의 내부 ID·참조·필수값·보호/권한을 적용한다. 별도의 최신 원본 사본이나 게임 제공 코드·관리용 코드 필드는 두지 않는다. 재료의 대상·특정 버전 참조와 상위 구성 갱신은 공유 계약을 따르며 [제작 관계 구현](task-003.md#summary)은 Task 43-003이 맡는다.
- 능력치는 `NUMERIC`/`BigDecimal`을 사용하고 표시 캐시 `item_version.stat_json`은 JSON 배열로 저장한다. P1은 아이템 스킬 원본의 버전에 설명 원문을 저장하고, 아이템 버전의 연결에 사용할 스킬 원본·버전과 기준 패치를 보관한다. P1 상세는 [연결의 임시 표시 설명](artifacts/task-002-execution.md#item-skill-link-description)을 표시한다. 값이 `NULL`이나 빈 문자열이면 설명을 빈 상태로 표시한다. 계산용 연결 JSON과 임시 설명의 전환은 [P3](../../phase-003/phase.md#entry-decisions)에서 다룬다.

<a id="version-key-proposal"></a>
<a id="primary-keys"></a>

#### 아이템·버전 키와 테이블별 기본키

- 일곱 테이블에 자동 발급 `BIGINT id` 기본키와 기존 PK 변경 방지 함수를 적용한다. 신규 표의 앱 `DELETE`는 `item_stat`과 `item_version_skill_link`에 한정하고, `item_skill_definition`은 조회·등록만 허용한다. [저장 구조와 제약 이름](artifacts/task-002-execution.md#p1-storage-schema-draft)
- `UNIQUE(item_id, from_game_patch_id)`로 같은 기준 패치의 버전 중복을 막고, 귀속 행은 `item_version_id`로 연결한다. `item_stat`은 `UNIQUE(item_version_id, stat_type_id)`로 같은 버전의 능력치 종류 중복을 막는다.
- `item_version`에 `UNIQUE(item_id, id)`를 둔다. 재료 아이템과 버전의 소속 일치를 검사하는 복합 외래 키의 참조 대상이다. 제작 관계의 실제 외래 키 배치는 43-003에서 검토한다. [제약 비교와 검증 사례](artifacts/task-002-execution.md#work-contract)

<a id="search-visibility"></a>
<a id="item-existence"></a>

#### 아이템 이름과 검색 노출·존재 상태

- `item_version.name`은 기본값 없는 `TEXT NOT NULL`로 둔다. 아이템 이름·능력치 종류 이름·스킬 원본 버전의 내부 이름과 설명 원문은 SQL과 Java에서 같은 [Unicode `White_Space` 목록](https://www.unicode.org/Public/17.0.0/ucd/PropList.txt)으로 검사한다. 누락·빈 문자열·공백만 있는 값은 거부하고 정상 입력은 그대로 보존한다.
- `item.searchable`은 `BOOLEAN NOT NULL DEFAULT TRUE`로 두고 모든 패치에 공통 적용한다. 숨김 아이템을 등록할 때는 `false`를 저장한다. 검색 노출과 게임 내 존재 상태는 [제품 기준](<../../../../docs/details/product/아이템 탐색과 상세.md#preview-and-detail>)에 따라 독립적으로 판정한다.
- 같은 패치의 입력 정정은 해당 버전의 아이템 ID와 시작 패치를 유지한다. 능력치·스킬 연결은 목록을 생략하면 유지하고 명시한 제거만 반영한다. 실제 게임 변경과 삭제·복귀는 새 버전으로 기록하고 이전 버전을 보존한다. 상태만 바뀌면 이전 구성을 이어받고 `is_deleted BOOLEAN NOT NULL DEFAULT FALSE`에 삭제는 `true`, 복귀는 `false`를 저장한다. [정정과 버전 보존](<../../../../docs/details/product/게임 데이터 변경 관리.md#change-and-correction>)

<a id="stat-cache-transaction"></a>

#### 능력치 원본과 표시 캐시

- `item_stat`을 저장·수정한 결과로 같은 아이템 버전의 `item_version.stat_json`을 만들어 같은 DB 트랜잭션에서 저장한다. 어느 쪽이든 실패하면 함께 되돌려 원본과 상세 표시가 일치하게 한다.
- `item_version.stat_json`은 `JSONB NOT NULL`로 두고 `CHECK (jsonb_typeof(stat_json) = 'array')`로 배열만 허용한다. 저장·갱신할 때 능력치 종류의 공통 순서로 배열을 구성한다. 상세 조회는 저장된 배열 순서를 그대로 사용한다. 배열의 각 항목에 능력치 종류 ID인 `statTypeId`와 능력치 값인 `value`를 담는다. 기본값은 `[]`이며 능력치가 없으면 같은 빈 배열을 저장한다. [정렬 및 배열 필드 근거](artifacts/task-002-execution.md#stat-display-order-proposal)
- `stat_type.name TEXT COLLATE "C"`와 `sort_order BIGINT`는 각각 `NOT NULL`·`UNIQUE`다. 순서 정정 시 `item_stat(stat_type_id, item_version_id)` 인덱스로 영향받는 현재·과거 버전을 찾아 같은 트랜잭션에서 캐시를 다시 만든다. 인덱스는 `item_stat`과 함께 추가한다.
- 능력치 저장은 `stat_type`에 `SHARE`, 공통 순서 정정은 `SHARE ROW EXCLUSIVE`를 먼저 잡는다. 그다음 영향받는 기존 `item_version` 행을 잠근다. 잠금 대기가 끝나면 최신 순서와 원본을 읽어 캐시를 만든다. 아이템 버전 저장은 상위 `item` 행을 잠가 같은 아이템의 쓰기를 순차 처리한다. 서로 다른 아이템의 일반 저장은 병행할 수 있다. [잠금 적용 근거](artifacts/task-002-execution.md#stat-display-order-proposal)

<a id="storage-verification-path"></a>
<a id="input-error-context"></a>

#### 저장·조회 검증과 입력 오류

- 확인 경로는 Spring 서비스 빈과 격리 PostgreSQL이다. 서비스 동작과 DB 제약은 [확인 계획](#verification)에, 경로를 선택한 이유와 참고 테스트는 [수행 기록](artifacts/task-002-execution.md#work-contract)에 둔다.
- 입력 오류에는 공통 코드 `API_INPUT_INVALID`, 업무 동작, 대상 종류·확인된 ID와 필드별 사유를 담아 오류 원인을 구분한다. HTTP API에 연결할 때 기존 `ProblemDetail`을 사용한다.
- 설명 원문 누락, 스킬과 지정 버전의 소속 불일치, 같은 스킬 중복 연결은 각각 `SKILL_DESCRIPTION_REQUIRED`, `SKILL_VERSION_OWNER_MISMATCH`, `DUPLICATE_SKILL_LINK`로 구분한다. [동작·오류 필드·재현 입력](artifacts/task-002-execution.md#skill-error-cases-proposal)

<a id="skill-reference-validation"></a>
<a id="skill-reference-layout"></a>

#### 아이템 스킬의 버전과 연결 제약

같은 아이템 스킬 원본에는 기준 패치에서 시작하는 버전을 최대 한 개 둔다. `item_skill_definition_version`의 `UNIQUE(item_skill_definition_id, from_game_patch_id)`로 보장한다. 스킬이 바뀌지 않은 패치는 기존 버전을 이어서 사용한다.

| 연결 행의 필수 참조                | 복합 외래 키가 확인하는 관계                                |
| ---------------------------------- | ----------------------------------------------------------- |
| 스킬 원본 ID · 원본 버전 ID        | 지정한 버전이 연결의 아이템 스킬 원본에 속한다.             |
| 아이템 버전 ID · 연결 기준 패치 ID | 연결의 기준 패치가 소속 아이템 버전의 기준 패치와 일치한다. |

- 두 참조 대상의 열 조합에는 각각 `UNIQUE`를 둔다. 스킬 원본과 기준 패치의 직접 외래 키도 둔다. 한 아이템 버전에 같은 원본의 스킬은 한 번만 연결할 수 있도록 아이템 버전 ID와 스킬 원본 ID의 조합에 `UNIQUE`를 둔다. [테이블명과 필드명](artifacts/task-002-execution.md#item-skill-schema-names)
- DB는 소속과 연결 기준 패치의 조합을 검사한다. 서비스는 소속 아이템 버전에서 기준 패치를 가져오고 `game_patch.sort_order`로 같거나 앞선 패치에서 시작한 스킬 버전만 연결한다. 공통 패치 순서 정정도 같은 트랜잭션에서 기존 연결을 대조해 위반 시 되돌린다. [시점 검사와 잠금](artifacts/task-002-execution.md#skill-link-timing)
- [R3-A](https://github.com/Mi-no-Kim/LumiaWiki/blob/9b8773ed5a26b799eac971ea8fe60949e14c4d0a/work/records/phase-001/issue-43/artifacts/task-001-version-references.md#r3)에 따라 새 아이템 버전에는 새 연결 행을 기록한다. 스킬 내용이 같으면 지정 버전을 재사용한다. 능력치나 재료만 바뀌면 기존 연결의 임시 설명 값도 이어받는다. 스킬 버전과 연결의 기준 패치는 서로 다를 수 있다.
- `ItemVersion`, `ItemStat`, `ItemSkillDefinitionVersion`, `ItemVersionSkillLink`의 필수 참조는 지연 로딩 `@ManyToOne`으로 매핑한다. 각 연관관계는 자기 외래 키 열 하나를 쓰고 기본키는 `CatalogRow`의 `Long`·IDENTITY를 따른다. 복합 외래 키는 Flyway에서 선언한다. [엔티티별 매핑](artifacts/task-002-execution.md#item-skill-jpa-mapping)

<a id="storage-nullability"></a>

#### 스킬 필수값과 아이템의 선택 필드

- P1 아이템 스킬의 원본·원본 버전과 연결의 기본키·참조는 `NOT NULL`로 둔다. 연결의 임시 `description`에는 `NULL`을 허용한다. 원본 설명이 미확인인 스킬 버전과 그 연결의 등록은 보류한다.
- 아이템 버전의 이미지 참조는 초기 `NULL`을 허용한다. 현재·과거 아이템 버전의 필요한 이미지를 모두 확보하고 유효한 경로를 채운 뒤 `NOT NULL`로 전환한다. [결정 근거와 전환 확인](artifacts/task-002-execution.md#storage-nullability-detail)
- 아이템의 최대 중첩 수량은 `NULL`을 허용한다. 공식 출시 표에 수량이 없으므로 확인되지 않은 값은 `NULL`로 저장할 수 있게 설계하고, 관련 자료에서 실제 값이 확인되면 채운다. [후속 저장 설계](artifacts/task-002-execution.md#remaining-storage-design)

<a id="remaining-decisions"></a>

### 남은 결정과 필요한 입력

공통 계약은 [Task 43-001의 인계](task-001.md#decisions)를 따른다. 설계 합의 후 실제 자료가 필요한 항목은 다음과 같다.

[후속 저장 설계](artifacts/task-002-execution.md#remaining-storage-design)에 따라 버전별 등급 FK·부위, 최대 중첩 수량의 NULL 허용, 능력치 원본·표시 캐시와 십진수 DTO를 구현했다.

| 남은 결정                         | 판단 기준·필요 입력                                                                                                                                                            | 결정 주체·시점                             |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------ |
| 기존 V2 행의 등급·부위와 실제 값  | 기존 행의 공란은 조회할 수 있다. 실제 자료를 대조해 지속 등급 참조와 장비 부위를 보완하며 비장비는 부위를 NULL로 저장한다.                                                     | #45의 자료 준비·검증 뒤                    |
| 최대 중첩 수량의 실제 값·범위     | 아이템별 값과 범위는 관련 자료가 갖춰지는 시점에 #45에서 확인한다. 미확인 상태는 [확정한 NULL 허용](#storage-nullability)을 적용한다.                                          | #45에서 자료 준비에 맞춰 보완              |
| 능력치 종류 목록의 원문 표기·단위 | 저장은 `NUMERIC`·`BigDecimal`, 캐시는 JSON 숫자, API DTO는 십진수 문자열을 사용한다. #45는 미확정 원문 표기·단위를 대조하고 [Task 004](task-004.md#summary)에서 결합 확인한다. | 해당 값의 등록·수용 전                     |
| 능력치 공통 표시 순서             | 기존 `stat_type.sort_order`로 캐시를 정렬한다. 실제 종류 목록에 순서값을 붙일 때 사용자에게 확인한다.                                                                          | 실제 순서 확정이 필요한 시점에 사용자 확인 |

부족한 입력은 그 값에 의존하는 선택·구현·수용을 제한한다. [#45 자료 확인 범위](../issue-45/issue.md#data)를 따른다.

<a id="verification"></a>

### 완료 기준과 확인 계획

기존 Task의 완료 기준은 담당 저장/조회·매핑·참조 검사·원본/캐시 일치·값 보존과 후속 사용 계약의 확인이다. 해당 범위를 [Issue 전체 수용 조건](issue.md#acceptance)과 연결한다.

아래 사례는 [개정 배정의 완료 조건](artifacts/task-002-assignment.md#acceptance)을 반영한다. [V2](artifacts/task-002-execution.md#isolated-v2-results)·[V3 격리 검증](artifacts/task-002-execution.md#isolated-v3-results)을 수행했다. [V3 통합 사례 8건을 재검증](artifacts/task-002-execution.md#v3-existence-regression)했다. 같은 아이템의 순차 저장과 서로 다른 아이템의 병행 저장을 확인했고, 사용자가 이 동작을 검증 기준으로 확정했다.

[후속 필드와 능력치 확인 사례](artifacts/task-002-execution.md#remaining-storage-design)는 기존 V2 행, 최대 중첩 수량의 미확인·보완, 수치 왕복과 트랜잭션 경계를 포함한다.

| 검증·사용자 확인 사례                                   | 기대 결과와 확인 방법                                                                                                                                                                                                                                                                                                                                                           |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 필수 문자열과 이름 중복                                 | SQL·Java에서 `NULL`, 빈 문자열, 공백만 있는 값의 거부와 정상 원문 보존을 대조한다. 능력치 종류의 같은 이름·순서값도 각각 거부한다. [최초 검증 입력](artifacts/task-002-execution.md#initial-verification)                                                                                                                                                                       |
| 기본 정보·복수 스킬·설명 원문 저장/재조회               | 새 트랜잭션에서 아이템·시작 패치·종류, 능력치 원본의 두 참조, 스킬 원본 버전의 소속·시작 패치를 확인한다. 표시용 조회는 연결의 임시 설명을 저장한 대로 읽고 `NULL`이나 빈 문자열은 빈 상태로 표시한다. 지정 버전의 설명 원문은 별도로 보존한다. V02·V11                                                                                                                         |
| 스킬 원본의 패치당 버전 1개                             | 같은 원본·같은 기준 패치의 중복 버전은 거부한다. 같은 원본의 다른 기준 패치와 다른 원본의 같은 기준 패치는 각각 등록할 수 있다.                                                                                                                                                                                                                                                 |
| 스킬 필수값 누락                                        | 설명 원문이나 참조가 `NULL`이면 DB가 거부한다. 서비스에 설명 원문을 누락해 저장을 요청한 경우 해당 스킬 버전과 연결이 등록되지 않는지 확인한다.                                                                                                                                                                                                                                 |
| 이미지 참조와 전환 조건                                 | 이미지 미등록 아이템 버전을 저장·조회할 수 있고, 이미지가 등록된 과거 버전의 경로는 그대로 조회된다. 전환 시 기존 버전에 `NULL`과 유효하지 않은 경로가 남아 있는지 확인하고, 전환 뒤 `NULL` 저장을 거부하는지 확인한다.                                                                                                                                                         |
| 같은 종류의 능력치 중복, 백분율과 채택 범위의 소수 입력 | 중복을 수용하지 않고 5%는 5로 저장. 승인한 정밀도/API 표현에서 왕복·기본 합산·원본/캐시가 일치. V02                                                                                                                                                                                                                                                                             |
| 스킬 연결 JPA 매핑과 복합 외래 키                       | 패치 1.0.3의 아이템 버전에 패치 1.0.1의 스킬 버전을 연결해 저장한다. 다시 읽을 때 연결 기준 패치는 1.0.3이고 지정 스킬 버전은 1.0.1인지 확인한다. DB 직접 저장에서는 잘못된 스킬 원본·버전 조합과 잘못된 아이템 버전·패치 조합을 각각 거부해야 한다. [재현 조건](artifacts/task-002-execution.md#item-skill-jpa-mapping)                                                        |
| 잘못된 스킬 참조와 중복 연결                            | 다른 스킬에 속한 버전과 같은 스킬의 중복 연결은 서비스 검증과 DB 제약에서 거부한다. 서비스는 소속 아이템 버전에서 기준 패치를 가져오며, 잘못된 패치 조합을 직접 저장하면 DB 제약이 거부한다. 실패 뒤 기존 연결을 재조회해 보존을 확인한다. V02·V11                                                                                                                              |
| Spring 서비스의 입력 거부                               | [세 가지 재현 입력](artifacts/task-002-execution.md#skill-error-cases-proposal)으로 공통 코드, 업무 동작·대상, 실패 필드·사유를 확인한다. HTTP 연결 시 `ProblemDetail`이 같은 사유를 전달하는지 대조한다.                                                                                                                                                                       |
| 같은 패치 정정과 실제 패치 변경                         | 같은 패치의 정정 뒤 아이템 ID·시작 패치·버전 ID와 버전 수가 유지되고 원본/캐시가 일치한다. 실제 패치 변경은 새 버전을 추가하고 이전 버전을 보존한다. DB에 같은 아이템·같은 패치 버전을 직접 추가하면 거부한다. 캐시 저장 실패 뒤 새 트랜잭션에서 원본과 캐시가 이전과 같은지 확인한다. 능력치 제거를 지원할 경우 마지막 행을 빼면 원본이 비고 캐시가 `[]`인지 확인한다. V11·V12 |
| 스킬 시작 패치와 패치 순서 정정                         | 아이템 버전과 같거나 앞선 스킬 버전의 저장을 허용한다. 이후 스킬 버전은 서비스에서 거부하고 기존 연결이 무효가 되는 패치 순서 정정은 롤백한다. [재현 입력](artifacts/task-002-execution.md#initial-verification)                                                                                                                                                                |
| 표시 캐시 저장·재조회                                   | 서로 다른 입력 순서로 저장해도 DB의 배열에는 공통 순서대로 `statTypeId`와 `value`가 들어간다. 상세 조회 순서는 저장한 배열과 일치한다. 캐시 열을 생략하면 `[]`를 저장하고 조회에서도 `[]`를 반환한다. SQL `NULL`, JSON `null`, 객체나 스칼라 값을 명시한 저장은 DB가 거부해야 한다.                                                                                             |
| 능력치 공통 순서 정정                                   | 순서가 바뀐 종류를 가진 현재·과거 버전의 캐시만 다시 만든다. 능력치 원본 값은 보존한다. 캐시 갱신 실패 시 순서와 캐시가 함께 이전 상태를 유지하는지 확인한다.                                                                                                                                                                                                                   |
| 능력치 저장·순서 정정의 동시 실행                       | 같은 아이템의 저장 두 건은 버전이 같거나 달라도 상위 `item` 행 잠금에서 순차 처리한다. 서로 다른 아이템의 일반 저장은 `SHARE` 잠금 아래 병행할 수 있어야 한다. 저장이 끝나면 능력치 원본과 캐시 배열이 일치해야 한다. 저장과 순서 정정은 양쪽이 각각 먼저 잠기는 경우를 재현해 후행 대기와 최종 배열의 새 값·새 순서를 확인한다.                                                |
| 능력치·재료만 바뀌어 새 아이템 버전 생성                | 새 버전에 속한 연결 행을 보관하고 기존 지정 스킬 버전과 연결의 임시 설명 값을 이어받는다. 연결 패치는 새 아이템 버전의 기준 패치이며, 이후 변경 없는 조회 Q로 덮어쓰지 않음. 독립 연결 버전은 만들지 않음. R3-A·V11                                                                                                                                                             |
| 종류 이름/계층 변경과 아이템 자체 소속 변경             | 같은 종류의 표시 변경은 기존 아이템 버전·재료·스킬 연결을 유지하고 과거/현재 모두 현재 분류 사용. 아이템 자체가 C에서 D로 이동하면 새 아이템 버전은 D, 과거 버전은 C 참조를 보존. K-D·V11                                                                                                                                                                                       |
| 완성된 아이템 버전의 단일 종류 소속                     | 유효한 종류 한 개를 참조한다. 종류 ID `NULL` 또는 없는 ID는 DB가 거부한다. 서비스 입력도 누락·잘못된 참조를 거부한다. F2-B·F3·V11                                                                                                                                                                                                                                               |
| 아이템 삭제·복귀와 검색 노출                            | 필드를 생략한 저장은 `searchable = true`, `is_deleted = false`를 사용한다. 명시한 검색 제외 `false`와 삭제 `true`를 보존하고 DB에서 두 필드의 명시적 `NULL`을 각각 거부한다. 복귀 버전은 `is_deleted = false`로 저장한다. 각 패치의 이전 정보와 공통 검색 노출 설정을 확인한다. 화면 표시는 #44에서 확인한다.                                                                   |

빈 격리 DB 설치와 V1까지 적용한 격리 DB의 갱신을 각각 확인한다. 갱신 전후 기존 공통 데이터의 ID·값·참조를 대조하고 새 구조에서 JPA 검증과 저장·재조회를 확인한다. 자동 검사·AI 직접 확인·사용자 확인을 구분하며, 화면은 #44의 [공통 검증 경계](issue.md#execution)를 따른다.

<a id="execution-plan"></a>

### 전체 수행 계획

<!-- task-rule:execution
전체 수행 계획은 ### 제목으로, 각 할 일은 #### 행동 제목과 복수 태그·완료 체크·할 일·확인·수행 기록으로 작성한다.
조사·실행·구현·논의·결정·검수·커밋 등 이 과제에 필요한 행동과 담당 결과를 드러낸다.
같은 결과·근거로 충족되는 행동은 묶을 수 있으며 모든 행동 종류를 필수로 넣지 않는다.
할 일은 의미 있는 결과와 필요한 확인·보완·기록까지 묶고 명령·파일마다 나누지 않는다.
첫 할 일 착수 때 공통 절차의 수행 기록 최초 생성 안내로 Task당 한 파일을 만든다.
이후에는 생성된 수행 기록의 주석과 구역 구조를 사용하며 본문·수행 기록 양식을 다시 찾지 않는다.
실제 결과·필수 확인·보완·기록을 갖춘 뒤에만 할 일을 완료 표시한다.
할 일 삭제·분할·병합에도 수행 사실·유효한 근거·원래 식별자와 연결을 보존한다.
-->

합의한 진행 순서는 최초 6개 표 구현 → #45 입력에 의존하는 범위 구현 → 격리 검증·후속 계약 인계 → 허용된 범위의 제출·종료다. 적용 조건과 권한은 [대상·준비](#preparation), 합의 근거는 [수행 기록](artifacts/task-002-execution.md#execution-plan-agreement)에 둔다.

<a id="work-contract"></a>

#### 저장·참조·원본/캐시 계약과 확인 경로를 합의한다

- 태그: 논의, 결정, 검수
- [x] 수행·확인 완료
- 할 일: [저장 스키마·JPA 매핑](artifacts/task-002-execution.md#p1-storage-schema-draft), [최초 구현·합성 검증](artifacts/task-002-execution.md#initial-verification)과 #45 입력에 의존하는 결정 시점을 합의한다.
- 확인: 개정 배정의 저장·참조·캐시 계약, 최초 6개 표와 합성 검증, #45 의존 결정 시점, 전체 계획의 검증·인계·제출 단계와 실행 조건을 대조해 충족을 확인했다.
- 수행 기록: [배정 대조·설계 합의와 검수](artifacts/task-002-execution.md#work-contract).

<a id="work-storage"></a>

#### 승인된 저장 구조와 매핑·저장/조회를 구현한다

- 태그: 실행, 검수
- [x] 수행·확인 완료
- 할 일: 먼저 `item`·`item_version`·`stat_type`·아이템 스킬 3개 표의 후속 Flyway 구조, JPA 매핑, Spring 서비스 저장·재조회·기본 정정을 구현한다. 최초 범위는 `stat_json`의 `[]` 기본값과 배열 제약을 포함한다. 이후 [필드별 설계 결정](#remaining-decisions)에 따라 등급·부위·NULL을 허용하는 최대 중첩 수량, `item_stat`과 값이 있는 캐시를 구현한다.
- 확인: [합의한 재현 사례](artifacts/task-002-execution.md#initial-verification)로 의도한 실패와 구현 후 통과를 대조한다. Flyway 실행 전에는 [전체 구조와 정확한 실행 대상 확인](../../../../db/migration/README.md#precreation-confirmation)을 적용한다.
- 수행 기록: [V2 격리 검증](artifacts/task-002-execution.md#isolated-v2-results) · [후속 구현과 DB 없는 검사](artifacts/task-002-execution.md#followup-storage-implementation) · [V3 격리 검증](artifacts/task-002-execution.md#isolated-v3-results).

<a id="work-verification"></a>

#### 전체 확인 사례를 검증하고 후속 계약을 인계한다

- 태그: 실행, 검수
- [x] 수행·확인 완료
- 할 일: 승인한 격리 DB에서 빈 DB 설치와 기존 V1 상태에서의 갱신을 각각 검증한다. 기존 공통 데이터 보존과 JPA 매핑, [참조·설명·캐시·잠금 사례](#verification) 및 회귀를 확인한다. #44에 표시·조회 계약을, Task 004에 참조·갱신 계약을 인계한다. 로컬 DB 적용은 격리 검증이 끝난 뒤 승인된 구조·대상에서 수행한다.
- 확인: [빈 설치·기존 V1/V2 갱신·동작](artifacts/task-002-execution.md#isolated-v3-results)을 확인했다. 공개 화면은 #44, 실제 자료 등록·교정은 #45의 결과와 대조한다.
- 수행 기록: [격리 검증 결과](artifacts/task-002-execution.md#isolated-v3-results)와 [#44·43-004 계약 인계](artifacts/task-002-execution.md#storage-handoff)를 마쳤다. [V3 보완 검증](artifacts/task-002-execution.md#v3-existence-regression)은 사용자가 확정한 저장 잠금 기준을 충족한다.

<a id="work-submission"></a>

#### 결과를 검수하고 Task 자체 완료를 기록한다

- 태그: 검수, 커밋
- [x] 수행·확인 완료
- 할 일: [별도 검수 기준](../../../../docs/details/operations/별도 검수.md)에 따라 결과를 검수하고, 필수 보완·검증 근거·자기 수용을 기록해 부모에 제출할 수 있게 한다.
- 확인: 실제 후보와 검수·검증 근거가 일치하고 반영·미반영·잔여가 기록됐는지 확인한다. Task 자기 수용과 Issue 전체 수용을 구별한다.
- 수행 기록: V2 `94f53cf`, V3 `04f8a3c`의 구현·검증 범위를 대조했다. 저장 잠금 기준을 확정했고, [V3 후보 검수](artifacts/task-002-execution.md#v3-candidate-review)와 [보완·재검증](artifacts/task-002-execution.md#v3-existence-regression)을 근거로 Task 자체 결과를 수용했다.

<a id="transition"></a>
<a id="result"></a>

## 결과

<!-- task-rule:completion
실제 전체 결과를 적용 전달사항의 완료 조건별로 대조하고 판정·근거·한계·잔여를 기록한다.
자기 수용과 필수 확인·관련 반영·보존·정리·종료 처리를 충족한 뒤 완료로 바꾼다.
할 일 체크·커밋·부모 Issue의 완료가 Task의 완료를 대신하지 않는다.
중단·취소·인계 시에는 실제 상태·이유·영향·보존 결과·잔여·해소/재개 조건과 다음 행동을 남긴다.
-->

- 내용: [최초 V2와 후속 V3](#work-storage)의 마이그레이션·매핑·저장·조회·정정 구현을 작성했다.
- 확인: [두 격리 DB의 V2 통합 검사 4건](artifacts/task-002-execution.md#isolated-v2-results), [최종 단위 검사 42건과 V3 격리 통합 검사 8건](artifacts/task-002-execution.md#v3-existence-regression)을 통과했다.
- 자기 수용: 담당 저장·조회·참조 검사, 원본과 표시 캐시의 일치 및 후속 인계를 확인해 완료로 판정한다.
- 후속: PR 제출, 부모 통합 확인과 브랜치 정리가 남았다. 기존 개발 DB 적용과 실제 자료 등록은 보류한다.
