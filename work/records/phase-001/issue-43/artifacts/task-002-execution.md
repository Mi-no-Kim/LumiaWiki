# Task 43-002 수행 기록

- Task: [Task 43-002 본문](../task-002.md#summary)
- 기록 기준: [Task 공통 절차](https://github.com/Mi-no-Kim/LumiaWiki/blob/77bc4229f882943d20b9539c5a25ccd9f5769643/harness/Task%20%EA%B3%B5%ED%86%B5%20%EC%A0%88%EC%B0%A8.md#recording-proposal)

<!-- execution-rule:recording
Task당 한 파일을 쓰고 이 주석은 머리말에 한 번만 둔다. 착수한 할 일은 구역 구조만 주석 없이 추가해 본문과 왕복 연결하고 실제 내용으로 채운다.
할 일의 태그·배정 조건에 따라 실제 조치·선택과 이유·근거를 남긴다. 파일 수정 없는 논의도 기록하고 제안·미결·합의·철회를 구별한다.
논의·사용자 결정은 실제 응답으로, AI 결정은 명시 위임·실제 선택으로 확인한다. 필수 논의를 생략하지 않는다.
확인은 계획·전달본을 참조하고 실제 대상·방법·관찰·판정·근거·한계를 남긴다. 변경본은 검증한 버전·범위를 식별하고 달라진 영향만 다시 확인한다.
진행·검수·수용에 필요한 결정은 Task에 결론·이유·조건·상세 링크를 남긴다. 공통 상세는 한 구역만 참조하며 잔여는 해당 할 일의 미해결·재개 조건이다.
보완·재시도는 같은 구역을 갱신한다. 식별자는 순서와 구별하고 삭제·분할·병합에도 수행·판단/실패 근거·당시 기준·본문 연결을 보존한다.
코드·diff·테스트 원문·명령별 로그를 복사·누적하지 않는다. 미발생 승인·결과나 단순 확인용 증명 파일을 만들지 않는다.
세부 작성 조건은 위 기록 기준을 따르고 생성 양식으로 돌아가지 않는다.
-->

<a id="work-contract"></a>

## 저장·참조·원본/캐시 계약과 확인 경로를 합의한다

- 할 일: [Task 본문의 해당 할 일](../task-002.md#work-contract)

- 조치·판단: 배정 대조와 저장 계약의 설계·검수 근거다. 적용할 순서는 [Task의 전체 수행 계획](../task-002.md#execution-plan)을 따른다.
  - **배정과 재개.** `4da7318`을 기준으로 설계 논의를 재개했다. `d6adc6f`의 부모 Issue와 최초 Task에서 아이템 기본 정보·버전, 능력치 원본·표시 캐시, 스킬 대상·지정 버전·연결별 JSON의 저장·조회 범위와 완료 조건을 확인했다. 별도 확정 전달본의 식별과 확정 근거는 미확인이다. [부모의 배정 기록](../issue.md#assignment-basis) · [Task의 전달사항 참조](../task-002.md#assignment)
  - **아이템·버전 키와 기본키.** `f18fee4`에서 별도 버전 ID인 A안과 `(item_id, 기준패치_id)`를 복합 기본키로 쓰는 B안을 비교했다. A안은 기존 단일 `BIGINT` 식별 방식과 맞고 귀속 행의 특정 버전 참조가 간단하다. 조회 성능의 우열은 측정하지 않았다. 재개 후 `item_stat`의 복합 기본키와 별도 ID·업무 키 `UNIQUE`도 비교했다. 각 테이블에 별도 기본키를 두고 `item_stat`의 버전·능력치 종류 중복은 `UNIQUE`로 막는다. [확정 계약](../task-002.md#version-key-proposal)
  - **스킬 참조 검사.** 복합 외래 키와 서비스 사전 검증, DB 트리거와 서비스 사전 검증, 단일 외래 키와 서비스의 조합 검사를 비교했다. 복합 외래 키는 모든 DB 쓰기 경로에서 소속과 기준 패치를 검사하며 참조 대상에 복합 `UNIQUE`가 필요하다. 트리거는 참조 대상 갱신과 동시 변경 경로도 다뤄야 한다. 단일 외래 키는 ID의 존재를 확인하므로 서비스 밖의 쓰기에 조합 검사가 추가로 필요하다.
  - **스킬의 연결 개수와 물리 배치.** 같은 스킬 대상은 한 아이템 버전에 한 번만 연결한다. 두 복합 외래 키와 참조 대상의 `UNIQUE`는 [확정 배치](../task-002.md#skill-reference-layout)를 따른다. 설명용 사례에서 패치 3의 아이템 버전이 패치 1의 스킬 버전을 재사용하면 연결 기준 패치는 3이다. `from_game_patch_id`는 기존 지도 버전의 시작 패치 명명을 따른다. Flyway가 DB 제약을 선언하고 서비스가 저장 전에 검사한다. 참조 열마다 쓰기 담당 연관관계 하나를 두는 [JPA 매핑](#item-skill-jpa-mapping)을 적용한다.
  - **검색 노출과 삭제·복귀.** 패치별 노출 이력과 아이템 단위 공통 설정을 비교했다. `searchable`은 아이템 단위로 두고 생략 시 `true`를 사용한다. 숨김 값 `false`는 그대로 저장한다. 존재 상태를 별도 이력에 두면 구성 복제를 줄일 수 있고 조회 때 두 이력을 결합해야 한다. 삭제·복귀는 새 아이템 버전으로 기록하고 `is_deleted`의 기본값은 `false`다. 서비스는 삭제 입력을 `true`로 저장한다. 검증에서 필드를 생략하는 DB 쓰기와 서비스 등록이 같은 기본값을 사용하는지 비교한다. 최초 추가와 복귀 사건의 구분은 별도 담당이다. 패치별 `false → true → false`는 설명용 사례다. [확정 계약](../task-002.md#item-existence)
  - **능력치 원본과 표시 캐시.** 서비스에서 같은 트랜잭션으로 갱신하는 안, DB 트리거로 갱신하는 안, 캐시를 무효화해 조회 때 재생성하는 안을 비교했다. 원본과 캐시는 같은 서비스 트랜잭션에서 갱신한다. 별도 1:1 테이블과 비교해 상세 조회에서 같은 버전 행을 읽는 `item_version.stat_json`을 사용한다. 종류 ID를 키로 쓰는 객체와 배열을 비교해 표시 순서를 보존하는 배열을 사용한다. 빈 배열 `[]`를 기본값으로 두고 저장하는 값에 종류별 공통 순서를 적용한다. [확정 계약](../task-002.md#stat-cache-transaction)
  - <a id="stat-display-order-proposal"></a>**능력치 정렬과 캐시 갱신.** 캐시를 만들거나 갱신할 때 공통 순서를 적용한다. 상세 조회는 배열 순서를 그대로 사용해 반복 정렬을 줄인다. [확정 계약](../task-002.md#stat-cache-transaction)
    - 공통 순서의 원천은 `stat_type.sort_order`다. 순서값이 바뀐 종류를 참조하는 `item_stat`에서 아이템 버전 ID를 찾아 해당 버전의 캐시만 다시 만든다. 한 버전에 여러 변경 종류가 있어도 캐시는 한 번 갱신한다.
    - `stat_type`의 `name`과 `sort_order`는 각각 `NOT NULL`·`UNIQUE`다. 기존 등급과 같은 정수형 `BIGINT`를 쓰고 작은 `sort_order`부터 표시한다. 이름 뒤 `(%)`가 붙은 종류는 별도 행으로 관리한다. 실제 목록과 순서값은 #45 입력 뒤 정한다. [기존 등급 정렬](../../../../../db/migration/V1__create_common_model.sql) · [능력치 종류 기준](<../../../../../docs/details/product/아이템 탐색과 상세.md#stat-information>)
    - `item_stat.stat_type_id`가 해당 종류를 참조한다. `stat_json` 배열의 항목 필드는 `statTypeId`와 `value`다. 이름과 정렬값의 원천은 `stat_type`이다. `statTypeId`의 API 표현은 [공통 ID 기준](<../../../../../docs/details/development/공통 DB 모델.md#internal-identifiers>)을 따르고 `value`의 수치 표현은 [정밀도와 값 보존](<../../../../../docs/개발 기준.md#stat-numeric>) 검토 뒤 확정한다.
    - 능력치 저장은 `stat_type` 테이블에 `SHARE`, 순서 정정은 `SHARE ROW EXCLUSIVE`를 먼저 잡는다. 이어 영향받는 기존 `item_version` 행을 ID 오름차순으로 잠근다. 새 버전의 원본·캐시 생성도 정렬 기준 잠금부터 잡는다. 저장과 순서 정정이 같은 업무에 있으면 처음부터 정정 모드를 잡는다. 대기가 끝나면 기존 `READ COMMITTED` 업무 경로에서 최신 순서와 원본을 읽는다. [카탈로그 잠금 규칙](../../../../../db/model/writes-and-checks.md#catalog-locking) · [PostgreSQL 잠금 충돌 표](https://www.postgresql.org/docs/18/explicit-locking.html#TABLE-LOCK-COMPATIBILITY)
    - 검증 예시. 공통 순서가 A·B·C일 때 C·A 순으로 저장 요청한 아이템과 B·A 순으로 요청한 아이템의 캐시는 각각 A·C와 A·B다. 상세 조회는 그 배열 순서대로 반환한다. 공통 순서를 정정하면 해당 종류를 가진 버전의 배열 순서가 반영되고 원본 능력치 값이 보존되는지도 확인한다. 캐시 저장에 실패하면 순서와 캐시가 모두 이전 상태로 돌아가는지 확인한다. [예정 검증](../task-002.md#verification)
  - **검증 경로.** Spring 서비스 빈을 직접 호출하고 격리 PostgreSQL에서 저장·재조회, 제약별 거부와 롤백을 확인한다. 빈 DB 설치와 V1 적용 DB 갱신은 별도 사례다. 갱신 전후 공통 데이터의 ID·값·참조가 보존되는지 대조한다. [기존 공통 카탈로그 통합 테스트](../../../../../backend/src/test/java/io/github/minokim/lumiawiki/catalog/CommonCatalogIntegrationTests.java)를 참고하고 화면은 #44에 인계한다. [예정 검증](../task-002.md#verification)
  - **입력 오류.** 필드 사유만으로는 어떤 동작과 대상을 처리했는지 구분하기 어렵다. `API_INPUT_INVALID`에 동작·대상 종류와 알려진 ID·필드별 사유를 담는다. [공통 구조](../task-002.md#input-error-context)에 따른 스킬 오류와 재현 입력은 [확정 사례](#skill-error-cases-proposal)에 기록한다.
  - **자료 의존 제안.** 능력치에 공통 `NUMERIC` 정밀도를 적용하는 방식과 종류별로 검증하는 방식, API의 JSON 숫자와 십진 문자열, 스킬 JSON의 공통 필수 키와 효과 유형별 필수 키를 비교했다. 선택은 #45의 실제 수치·JSON·설명을 확인한 뒤 검토하는 초기 제안이었다. 현재 능력치 선택은 [Task의 남은 결정](../task-002.md#remaining-decisions), 계산용 스킬 JSON의 필드·값 범위는 [P3 계획](../../../phase-003/phase.md#goal)을 따른다.
  - <a id="p1-storage-schema-draft"></a>**P1 저장 스키마와 JPA 매핑.** 일곱 표의 이름과 아래 필드명을 적용한다. 일곱 표 모두 자동 발급 `BIGINT id`를 기본키로 두고, 제약 이름은 [기존 V1](../../../../../db/migration/V1__create_common_model.sql)의 `pk_`·`nn_`·`uq_`·`ck_`·`fk_` 관례를 따른다. #45 입력과 별도 결정이 필요한 세부는 [Task의 미결 항목](../task-002.md#remaining-decisions)을 따른다.

    | 표 | 필드와 저장 조건 |
    | --- | --- |
    | `item` | `searchable BOOLEAN NOT NULL DEFAULT TRUE`. 모든 패치에 적용하는 검색 노출 설정이다. |
    | `item_version` | `item_id → item`, `from_game_patch_id → game_patch`, `category_id → item_category`는 필수 참조다. `is_deleted BOOLEAN NOT NULL DEFAULT FALSE`를 적용한다. `name TEXT NOT NULL`에는 기본값을 두지 않는다. DB와 서비스에서 누락·빈 문자열·공백 문자만 있는 이름을 거부하고 정상 이름은 보존한다. SQL과 Java의 공백 판단 기준을 검증 사례에 맞춘다. `stat_json JSONB NOT NULL DEFAULT '[]'::jsonb`와 `CHECK (jsonb_typeof(stat_json) = 'array')`를 적용한다. 캐시 열 생략은 `[]`를 저장하고 SQL `NULL`, JSON `null`, 객체·스칼라는 거부한다. `image_path TEXT`는 [초기 NULL과 필수 전환 조건](../task-002.md#storage-nullability)을 따른다. 공통 이미지 루트 기준의 상대 경로로 보존한다. |
    | `stat_type` | `name TEXT COLLATE "C"`와 `sort_order BIGINT`는 각각 `NOT NULL`이다. 유일 제약은 `uq_stat_type_name`과 `uq_stat_type_sort_order`다. 실제 순서값은 #45 입력을 확인한다. |
    | `item_stat` | `item_version_id → item_version`, `stat_type_id → stat_type`, `value NUMERIC`은 필수다. `NUMERIC(p,s)`는 #45 입력을 확인한다. 순서 정정용 `item_stat(stat_type_id, item_version_id)` 인덱스를 함께 둔다. |

    <a id="item-skill-schema-names"></a>

    | 테이블명 | 필드명 | 의미 |
    | --- | --- | --- |
    | `item_skill_definition` | `id` | 아이템 스킬 원본의 지속 ID이자 기본키. |
    | `item_skill_definition_version` | `id`, `item_skill_definition_id` | 원본 버전의 기본키와 소속 원본 참조. |
    | `item_skill_definition_version` | `from_game_patch_id` | 해당 스킬 설명이 적용되기 시작한 패치. |
    | `item_skill_definition_version` | `internal_name`, `description` | 내부 이름과 설명 원문. 둘 다 `TEXT`. |
    | `item_version_skill_link` | `id`, `item_version_id` | 연결의 기본키와 소속 아이템 버전 참조. |
    | `item_version_skill_link` | `item_version_patch_id` | 소속 아이템 버전의 기준 패치. `item_version.from_game_patch_id`에서 가져온다. |
    | `item_version_skill_link` | `item_skill_definition_id`, `item_skill_definition_version_id` | 사용할 아이템 스킬 원본과 지정 버전 참조. |
    | `item_version_skill_link` | `description TEXT` | P1 임시 표시 설명. `NULL` 허용, 미입력 시 빈 상태. |

    스킬 원본·원본 버전의 필드와 연결의 기본키·참조는 `NOT NULL`이다. [P1 배정 범위](task-002-assignment.md#assignment-revision)를 따른다.

    <a id="item-skill-link-description"></a>**P1 임시 연결 설명.** 계산용 구조가 마련되기 전 아이템 버전별 스킬 설명을 표시하기 위한 필드다. `item_version_skill_link.description`을 표시하고 값이 `NULL`이나 빈 문자열이면 설명을 빈 상태로 표시한다. 스킬 버전의 설명 원문은 해당 버전에 보존한다. [제품 표시 기준](<../../../../../docs/details/product/게임 데이터 변경 관리.md#item-skills>) [P3 전환 검토](../../../phase-003/phase.md#entry-decisions)에서 기존 원문을 보존할 위치와 이관 방법, 임시 필드를 교체할 시점을 정한다.

    | 제약 이름 | 적용할 관계 |
    | --- | --- |
    | `uq_item_version_item_patch` · `uq_item_version_owner_identity` · `uq_item_version_id_patch` | `item_version`의 `UNIQUE(item_id, from_game_patch_id)`, `UNIQUE(item_id, id)`, `UNIQUE(id, from_game_patch_id)`. |
    | `uq_item_skill_definition_version_owner_id` · `uq_item_skill_definition_version_start_patch` | `item_skill_definition_version`의 `UNIQUE(item_skill_definition_id, id)`와 `UNIQUE(item_skill_definition_id, from_game_patch_id)`. 패치당 버전 제약은 한 원본에 같은 시작 패치의 중복 버전을 막는다. |
    | `uq_item_stat_version_type` · `uq_item_version_skill_link_item_definition` | 각각 `item_stat(item_version_id, stat_type_id)`, `item_version_skill_link(item_version_id, item_skill_definition_id)`의 유일 제약. |
    | `fk_item_version_skill_link_definition_version` | `(item_skill_definition_id, item_skill_definition_version_id) → item_skill_definition_version(item_skill_definition_id, id)`. 원본 ID의 직접 참조는 `item_skill_definition.id`를 가리킨다. |
    | `fk_item_version_skill_link_item_patch` | `(item_version_id, item_version_patch_id) → item_version(id, from_game_patch_id)`. 연결 기준 패치의 직접 참조는 `game_patch.id`를 가리킨다. |

    [Task 43-003의 R2 계약](../task-003.md#activity)은 재료의 아이템 ID와 지정 버전 ID를 함께 저장한다. 두 값의 소속을 검사하는 참조 대상은 **확정한** `item_version(item_id, id)`다. 별도 PK가 있어도 이 열 조합을 참조하므로 복합 `UNIQUE`를 둔다. 실제 제작 관계의 외래 키 배치는 43-003에서 검토한다. 재현 사례는 같은 재료의 (M, M0) 저장 성공과 다른 재료의 (N, M0) 저장 거부다. 조회 패치에 유효한 재료 버전을 선택하는지는 결합 조회에서 확인한다. [기존 결정의 비교 근거](../task-002.md#version-key-proposal)

    - <a id="item-skill-jpa-mapping"></a>**JPA 매핑.** `ItemVersion`은 `item_id`, `from_game_patch_id`, `category_id`로 `Item`, `GamePatch`, `ItemCategory`를 참조한다. `ItemStat`은 `item_version_id`, `stat_type_id`로 `ItemVersion`, `StatType`을 참조한다. `ItemSkillDefinitionVersion`은 `item_skill_definition_id`, `from_game_patch_id`로 `ItemSkillDefinition`, `GamePatch`를 참조한다.
    - `ItemVersionSkillLink`는 `itemVersion` → `item_version_id`, `itemVersionPatch` → `item_version_patch_id`, `itemSkillDefinition` → `item_skill_definition_id`, `itemSkillDefinitionVersion` → `item_skill_definition_version_id`로 매핑한다. 네 엔티티의 참조는 [RegionMapMember](../../../../../backend/src/main/java/io/github/minokim/lumiawiki/catalog/RegionMapMember.java)처럼 필수 지연 로딩 `@ManyToOne`이고 기본키는 [CatalogRow](../../../../../backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogRow.java)의 `Long`·IDENTITY를 따른다. 연결 패치는 서비스에서 소속 아이템 버전으로부터 가져오고 복합 외래 키는 Flyway에서 선언한다. [저장·재조회와 거부 사례](../task-002.md#verification)
    - **값과 표시 캐시.** JPA의 능력치 값은 `BigDecimal`을 사용한다. 캐시는 순서가 있는 JSONB 배열로 매핑하고 같은 트랜잭션에서 갱신한다. 캐시의 숫자 표현과 JSONB 바인딩은 #45 수치의 왕복으로 확인한다. 순서 정정 시 [확정한 인덱스](../task-002.md#stat-cache-transaction)로 영향받는 버전을 찾아 같은 버전의 캐시를 한 번만 다시 만든다. 잠금 검증은 같은 아이템의 저장이 순차 처리되고 서로 다른 아이템의 저장은 병행되는지 대조한다. 순서 정정과 능력치 저장이 각각 먼저 잠글 때 후행 작업의 대기도 확인한다. 두 작업이 끝나면 캐시에 새 값과 새 순서가 모두 남아야 한다.
    - **같은 패치 정정.** 대상 버전의 아이템 ID와 시작 패치를 유지한 채 입력을 고친다. 능력치 원본과 캐시는 같은 트랜잭션에서 갱신한다. 실제 게임 변경은 새 버전을 추가하고 이전 버전을 보존한다. [제품 기준](<../../../../../docs/details/product/게임 데이터 변경 관리.md#change-and-correction>) · [정정 및 실패 재현 조건](../task-002.md#verification)
  - <a id="skill-error-cases-proposal"></a>**스킬 입력 오류와 재현 사례.** [42-003의 공통 응답](../../issue-42/task-003.md#implementation-decisions)과 [기존 `FieldError(field, code, message)`](../../../../../backend/src/main/java/io/github/minokim/lumiawiki/common/api/ApiFailure.java)를 사용한다. HTTP에 연결하면 `400 ProblemDetail`의 상위 `code`는 `API_INPUT_INVALID`이며 `requestId`와 `fieldErrors`를 반환한다. 업무 맥락은 상위 `operation`과 `target`에 담는다.
    - 재현 자료는 기존 아이템 버전 `42`, 스킬 A의 유효 버전 A1·A2, 별도 스킬 B의 유효 버전 B1이다. 각 사례는 같은 초기 상태에서 시작하고 링크의 기준 패치는 소속 아이템 버전에서 파생한다.

    | 사례와 재현 입력 | 업무 동작·대상 | 필드·사유 코드·메시지 |
    | --- | --- | --- |
    | 설명 누락. 기존 스킬 A의 새 버전에 설명을 생략하거나 `null`로 입력한다. | `CREATE_SKILL_VERSION` · `SKILL_VERSION`. 새 버전 ID는 아직 없으므로 생략한다. | `description` · `SKILL_DESCRIPTION_REQUIRED` · 스킬 설명 원문을 입력해 주세요. |
    | 다른 스킬의 버전. 아이템 버전 42의 첫 연결에 스킬 A와 버전 B1을 입력한다. | `UPDATE_ITEM_VERSION` · `ITEM_VERSION`, ID `"42"`. | `skills[0].skillVersionId` · `SKILL_VERSION_OWNER_MISMATCH` · 선택한 스킬의 버전이 아닙니다. |
    | 중복 연결. 아이템 버전 42에 (A, A1), (A, A2)를 순서대로 입력한다. | `UPDATE_ITEM_VERSION` · `ITEM_VERSION`, ID `"42"`. | `skills[1].skillId` · `DUPLICATE_SKILL_LINK` · 같은 스킬은 한 번만 연결할 수 있습니다. |

    - Spring 서비스는 업무 사유를 반환한다. HTTP 입력 검증이 먼저 설명 누락을 거부하는 경우에도 같은 필드·사유 코드를 반환하도록 매핑을 확인한다. 실패한 등록 뒤 새 스킬 버전이 없고, 실패한 수정 뒤 기존 연결이 그대로인지 새 트랜잭션에서 재조회한다.
    - 격리 PostgreSQL에 직접 쓰는 사례로 `NOT NULL`, 스킬 원본·버전 소속 복합 외래 키, 아이템 버전과 스킬 원본의 조합 `UNIQUE`를 각각 확인한다. 소속 아이템 버전과 다른 연결 기준 패치는 패치 복합 외래 키에서 별도 재현한다.
  - **스킬 저장 범위 개정.** P1은 설명 원문과 스킬 버전 연결을 보존한다. 스킬 연결의 계산용 JSON 구조와 검증은 실제 지원 효과·수식·입력을 확인할 P3로 이월했다. `item_version.stat_json`은 P1의 능력치 표시 캐시다. [부모의 배정 결정](../issue.md#skill-storage-assignment-revision) · [개정 전달사항](task-002-assignment.md#assignment-revision).
  - <a id="storage-nullability-detail"></a>**스킬 필수값과 이미지 참조.** 설명 원문을 포함한 P1 스킬 필드의 필수값 누락은 해당 버전·연결의 등록을 보류하는 조건이다. 이미지 자료를 확보하는 동안 아이템 버전을 저장·조회할 수 있도록 이미지 참조는 `NULL`을 허용한다. [#45의 이미지 등록과 과거 참조 보존](../../issue-45/issue.md#task-outline)으로 필요한 파일을 확보하고, 전환 대상의 모든 기존 버전에 실제 파일을 가리키는 경로가 채워졌는지 확인한 뒤 `NOT NULL` 제약을 적용한다. [Task의 현재 합의](../task-002.md#storage-nullability)
  - <a id="skill-link-timing"></a>**스킬 연결 시점.** 연결 저장 서비스는 공통 잠금 규칙에 따라 `game_patch`의 `SHARE` 잠금 아래 시작 패치의 `sort_order`를 비교한다. 공통 패치 순서 정정은 기존 저장 경로의 `CatalogReferenceCheck`에서 연결을 재검사하고 무효가 되면 같은 트랜잭션을 롤백한다. [공통 잠금 규칙](../../../../../db/model/writes-and-checks.md#catalog-locking) · [문자열 검사 계약](../task-002.md#search-visibility)
  - **정정 권한.** 같은 패치의 정정에서 목록 미입력은 유지, 명시한 빈 목록은 비우기로 처리한다. 이번 일곱 표 중 앱은 `item_stat`과 `item_version_skill_link`만 삭제할 수 있다. ID만 있는 `item_skill_definition`은 조회·등록만 허용하고 신규 표의 PK 변경은 기존 `reject_common_pk_update` 보호를 적용한다. [공통 권한·보호](../../../../../db/model/permissions-and-installation.md#current)
  - <a id="initial-verification"></a>**최초 구현과 검증.** [Task의 최초 범위](../task-002.md#work-storage)를 합성 입력으로 확인한다. 명령은 `.\backend\gradlew.bat -p backend test --offline`과 `.\backend\gradlew.bat -p backend integrationTest --offline`이다. 각 사례는 독립 상태에서 확인한다. [기존 검증 환경](../../../../../db/model/implementation.md#current)
    - **스킬 패치.** 패치 1.0.3 아이템에 1.0.1·1.0.3·1.0.4의 스킬 버전을 각각 연결한다. 앞선 두 연결은 저장 후 새 트랜잭션에서도 지정 버전과 기준 패치가 각각 유지된다. 1.0.4는 서비스가 거부하고, 이미 연결된 1.0.1 패치를 1.0.5로 옮기는 정정도 롤백한다.
    - **연결 제약.** 다른 스킬 원본의 버전, 아이템 버전과 다른 연결 패치, 같은 스킬의 중복 연결을 각각 DB에 직접 저장한다. 두 복합 외래 키와 `UNIQUE`가 해당 입력을 각각 거부한다.
    - **문자열.** 필수 문자열에 `NULL`, 빈 문자열, 탭·줄바꿈·전각 공백만 있는 값을 각각 입력해 서비스와 DB가 거부하는지 확인한다. `" 테스트검 "`은 그대로 재조회한다. 같은 능력치 이름과 같은 순서값도 각각 거부한다.
    - **정정과 롤백.** 한 버전에 연결한 스킬 A·B 중 B를 제거하면 A만 남고 버전 ID와 다른 패치의 연결을 보존한다. 독립 사례에서 B 제거 뒤 후속 쓰기를 강제로 실패시키면 새 트랜잭션에서 A·B가 모두 남아야 한다.
    - **기본값과 캐시.** 세 열을 생략하면 `searchable = true`, `is_deleted = false`, `stat_json = []`다. 캐시의 SQL `NULL`, JSON `null`, 객체·스칼라 저장은 DB가 거부한다.
    - **설치·갱신·권한.** 빈 격리 DB와 합성 공통 데이터가 있는 V1 DB에서 후속 마이그레이션과 JPA 검증이 통과하고 V1 데이터의 ID·값·참조가 보존되어야 한다. 앱 계정의 링크 삭제는 허용되고 아이템 버전 삭제와 PK 변경은 거부된다.
- 확인: 최초 배정은 `d6adc6f`, A/B 비교와 A안 확정은 `f18fee4`를 대조했다. 재개 후의 원천은 이전 Codex 대화 `현재 상태 확인`(`01a1f493-395e-7bb2-9876-3b1f6db2027c`)의 다음 기록이다.
  - 배정 대조·재개 `01a1f4a4-a4c9-7c81-96a9-fa95fb0a1e88`, 테이블별 키 `01a1f79b-43df-7db0-a899-edd227f598d8`.
  - 스킬 검사 `01a1f4be-ffd4-7323-9b1d-75526db468bf`, 연결 개수 `01a1f79d-bc3d-7350-861a-7ac8e8c808bb`, 외래 키 배치 `01a1f7ad-b0eb-7fc3-8bb3-3ece84000635`. 스킬 연결의 JPA 매핑·검증 조건은 현재 대화의 `01a1f9e1-899e-7b22-803e-210b4b96375b`에서 확인했다.
  - 검색 노출 `01a1f4c9-678e-73f3-8d00-3d0b91ee9773`, 삭제·복귀 `01a1f4cc-1b75-7ca1-874a-36b99c7e8f61`. 두 필드의 기본값은 현재 대화의 `01a1f9e4-3e6d-7a33-8618-d2639a38dbae`, 아이템 이름의 필수값과 빈 값 처리는 `01a1f9e5-a39f-73e3-a4c2-bf685b207e0b`에서 확인했다.
  - 트랜잭션 `01a1f4cd-b86e-77e2-a4a6-59bf94fe6d41`, 캐시 위치 `01a1f783-aa7d-7121-925f-2c8a530ed89b`, 배열 `01a1f7a1-038a-7db2-b837-97e88371e22f`, 공통 순서 `01a1f7a2-755b-7661-a667-e997da8e4ec8`.
  - 검증 경로 `01a1f69e-4d95-7622-8d3f-2ca8479cbba3`, 입력 오류 `01a1f7a9-04ba-7460-8cd9-608264242fda`.
  - 재료 참조 대상 키 확정은 Codex 대화 `01a1f7af-7572-7462-96e6-257e3ff7201f`의 `01a1f881-1b32-7e33-b35e-f0b769d4326a`에서 확인했다.
  - <a id="skill-storage-scope-confirmation"></a>스킬 저장 범위 개정은 같은 대화에서 `01a1f8bc-4d12-7bc1-807d-3b4ef0084455`의 범위 제안과 `01a1f8c0-1ae9-7421-9421-13f489a631ee`의 확정으로 확인했다.
  - 개정 배정·공통 참조 계약·Task 004의 기대 결과와 [전체 계획 확인 조건](https://github.com/Mi-no-Kim/LumiaWiki/blob/77bc4229f882943d20b9539c5a25ccd9f5769643/harness/Task%20%EA%B3%B5%ED%86%B5%20%EC%A0%88%EC%B0%A8.md#sequence-rules)을 대조했다. 최초 범위와 여섯 합성 사례, #45 의존 결정 시점, 격리 검증·인계·제출 단계와 권한 조건을 확인해 첫 할 일의 완료 조건을 충족한다고 판정했다.
  - 스킬 필수값과 이미지 참조 전환 조건은 같은 대화의 `01a1f8d9-108e-70e1-a331-a23ee81574be`에서 확인했다. 캐시를 저장할 때 공통 순서를 적용하기로 한 근거는 같은 대화의 `01a1f8de-b7b0-7e13-abaa-a8e2a9c3cd5c`다.
  - 공통 순서의 원천과 캐시 갱신 범위는 같은 대화의 `01a1f8e3-13cc-7010-801d-5c7f91500ebe`, 종류의 필수·유일 제약과 캐시 필드는 `01a1f97a-5508-7aa3-b225-748d3b7cc084`, 잠금 순서는 `01a1f9a4-604c-76b3-9f7f-d14691f629c8`, 잠금 모드는 `01a1f9ad-64cc-7e13-a1dc-2586c9f03681`에서 확인했다. 빈 배열 기본값은 `01a1f9e7-018c-7242-ae8c-ead5a36b8a8c`에서 기존 결정임을 확인했고, JSONB·배열 제약은 `01a1fbaf-acbe-7cd3-9c8d-21d07eca700a`에서 확정했다.
  - 스킬 오류 세 건의 사유와 재현 사례는 같은 대화의 `01a1f901-7428-7bd2-b146-2aadb12f06d1`에서 확정했다. 연결 설명의 임시 용도는 같은 대화의 `01a1f948-77eb-7801-8f7e-6461a54da607`에서 확인했다. 임시 연결 설명의 원문 대체는 이전 대화 턴 `01a1f95b-b72f-7c90-905a-ab02a9a989b8`에서 합의했다가 `01a1f961-d6b5-7e13-987f-62db9a5ff665`에서 빈 상태 표시로 정정했다. 같은 턴에서 원본당 기준 패치의 버전은 하나로 확정했다.
  - 스키마·JPA·정정·기본 검증은 현재 대화의 `01a1fbb9-8652-74a0-aa08-bf762b0a56db`, 스킬 시점·문자열·권한과 인덱스·최초 구현·합성 재현 조건은 `01a1fbe7-1c39-75b0-9afa-7978bdd1ec8f`에서 확정했다. 제품 구현·DB 실행·동작 검증은 미수행이다.
  - <a id="execution-plan-agreement"></a>현재 대화의 `01a1fbea-62f1-7110-a699-0ac8a786f671`에서 [전체 수행 계획](../task-002.md#execution-plan)의 순서를 확정했다. 첫 할 일의 문서 검수와 완료 처리를 허용한 범위이며 제품 구현은 대기한다.
- 잔여: 첫 할 일의 잔여는 없다. 이후 진행은 [저장 구현](#work-storage)에서 확인한다.

<a id="work-storage"></a>

## 최초 6개 표의 저장·조회 구현

- 할 일: [Task 본문의 저장 구현](../task-002.md#work-storage)
- 조치·판단: 사용자 착수 지시에 따라 최초 6개 표에 [V2 SQL](../../../../../db/migration/V2__create_item_storage.sql), JPA 매핑, Spring의 버전 단위 등록·정정·재조회와 공통 패치 순서 재검사를 작성했다. 기준 패치 이후에 시작한 스킬 버전은 저장 시 거부하고 이미 연결된 버전을 무효화하는 패치 순서 정정도 같은 트랜잭션에서 거부한다. #45에 의존하는 필드·능력치 원본과 값이 채워진 캐시는 후속 범위다.
- 확인: 제품 Flyway 경로에 V2가 없는 상태에서 추가한 포장 검사가 의도대로 실패했다. V2와 구현 작성 뒤 PostgreSQL 없는 단위 검사 35건, Spotless, bootJar가 통과했다. 실행 JAR에 담긴 V1·V2 SQL과 각각의 원천을 바이트 단위로 대조했다. JDBC 연결 없이 Hibernate 14개 엔티티 메타모델 구성과 저장·조회 HQL 5개의 파싱을 확인했다. 이 확인 범위는 실제 PostgreSQL에서의 DDL 적용·JPA validate·동작 검증 전까지다.
- 잔여: 최초 6개 범위는 [격리 통합 검증](#isolated-v2-results)까지 마쳤다. #45에 의존하는 필드·능력치 원본·값이 있는 캐시의 구현과 검증이 남았다.

<a id="storage-creation-review"></a>

### 전체 구조와 첫 실행 대상

- DDL 원천은 [V2 SQL](../../../../../db/migration/V2__create_item_storage.sql)이며 SHA-256은 `69c407f9191555c5c0ceeed62296f44fda9874776b311e75698d2e3cc01940d6`이다. 6개 `BIGINT GENERATED ALWAYS AS IDENTITY` PK, 필수 참조와 RESTRICT·비지연 FK 9개, 비지연 UNIQUE 8개, CHECK 5개, PK 보호 트리거 6개를 선언했다. PK·UNIQUE 인덱스로 조합을 보장한다. 4개 필수 문자열은 빈 문자열과 Unicode White_Space만 있는 값을 거부한다. `stat_json JSONB`는 기본값 `[]`와 배열 제약을 적용한다.
- `lumia_migrator`로 Flyway를 실행해 신규 객체를 소유한다. `lumia_app`은 모든 신규 표를 조회·등록할 수 있고 `item_skill_definition`을 제외한 표를 수정할 수 있다. 삭제는 `item_version_skill_link`에만 허용한다. V2 실패 시 V2에서 생성하는 표·제약·인덱스·트리거·GRANT 전체가 롤백된다. 앞서 적용한 V1과 부트스트랩·Flyway 관리 표는 유지된다.
- 사용자는 로컬 Docker Desktop `desktop-linux`의 새 Testcontainers `postgres:18.6` 인스턴스에서 `lumiawiki/public`과 `catalog_item_upgrade/public`에 대한 V2 통합 검증만 승인했다. 기존 개발 DB 적용은 승인 범위에서 제외했다.

<a id="isolated-v2-results"></a>

### 두 격리 DB의 V2 통합 검증 결과

- 실행: 위 SHA-256과 일치하는 V2로 `.\backend\gradlew.bat -p backend '-PtddReportDir=build/reports/item-storage-v2' integrationTest --tests 'io.github.minokim.lumiawiki.catalog.CommonCatalogIntegrationTests.itemStorage*' --offline`을 실행했다. PostgreSQL 18.6 컨테이너 `c9a5e31e131b`의 `127.0.0.1:56642`를 사용했다. JUnit XML의 연결 로그와 네 실행 사례를 대조했다.
- 빈 `lumiawiki/public`: Flyway V1→V2 신규 설치와 JPA 검증, 재실행 시 실행할 마이그레이션 0건을 확인했다. 버전·스킬 저장과 재조회, 같은 패치 정정·실패 롤백, 후속 스킬 버전과 기존 연결을 깨는 패치 순서 정정의 거부, 기본값·배열·문자열 제약·복합 FK·UNIQUE·권한·PK 보호가 통과했다.
- `catalog_item_upgrade/public`: Flyway V1 적용 뒤 합성 시즌·패치·분류를 등록하고 V2로 갱신했다. 기존 행의 ID·값·참조 보존과 신규 아이템의 저장·재조회, 현재 마이그레이션 버전 2를 확인했다.
- 판정: 선택한 통합 검사 4건 모두 통과했다. 실행에 사용한 임시 컨테이너는 종료 후 제거됐다. 기존 개발 DB는 이번 실행 대상에 포함하지 않았다.

<a id="initial-storage-commit-review"></a>

### 최초 6개 표 제출 후보 검수

- 자체·별도 검수: 기준 `fae9ccb`에서 SQL·Java·테스트 15개와 관련 기록 4개를 대조했다. Task 43-004와 분량 검사 메모는 후보 밖에 보존했다. 별도 검수에서 확인한 Task 본문의 오래된 동작 검증 문구를 격리 검증 결과에 맞췄다. 필수 DDL·구현 결함은 발견되지 않았다.
- 회귀 확인: 제출 후보의 검증 사본에서 V2 리소스와 새 필수 문자열·스킬 연결 동작이 빠진 경우 기존 단위 테스트에서 예상한 단언 실패 5건을 재현했다. 같은 테스트로 실제 후보의 단위 테스트 35건, SpotlessCheck, bootJar 통과를 확인했다. 이 재현은 커밋 검수에서 수행한 새 실행이다.
- 근거 승계: 후보에서 빌드한 Java 본체 클래스 42개, 테스트 클래스 16개와 V2 SQL을 이전 격리 검증 실행의 빌드와 바이트 단위로 대조했다. 두 격리 DB 통합 4건의 결과를 재사용했다. 확인한 롤백은 업무 정정과 패치 순서 교정이다. V2 설치 실패 주입과 #45 의존 능력치 범위는 이번 검증에 포함하지 않았다.

<a id="remaining-storage-design"></a>

### 공식 1.0.0 아이템 표 기준 후속 저장 설계안

- 할 일: [43-002의 남은 저장 범위](../task-002.md#remaining-decisions). 입력은 [공식 1.0.0 아이템 표](https://docs.google.com/spreadsheets/d/e/2PACX-1vTjbw1TSUfgr0KwrMIW0YSjvYvtQEHnFrHX54Qgz-DpbPPtxz801OAL7dQKgkigAB6EHktuYYgZGRsG/pubhtml)다.
- 확정 조건: 공식 표를 기준 원천으로 사용한다. 최대 중첩 수량의 미확인 값은 `NULL`을 허용한다. 공통 표시 순서의 실제 값은 필요한 시점에 사용자에게 확인한다. 아래 물리 구조와 값 표현은 구현 전 대조할 설계안이다.

#### 아이템 버전의 등급·장비 부위·최대 중첩 수량

| 열 | 자료형·제약 제안 | 관측값과 처리 |
| --- | --- | --- |
| `item_version.grade_id` | `BIGINT`, 기존 `item_grade.id`의 FK. 삭제 제한, 즉시 검사. 완성된 아이템 버전의 신규 등록과 정정에는 등급이 필수다. | 공식 표 651행 모두 등급 1개가 있다. 일반·고급·희귀·영웅·전설은 등급 목록에 한 번씩 연결한다. 패치에서 등급이 바뀌면 새 아이템 버전에 새 등급 ID를 저장한다. 공유 등급의 이름·순서는 [기존 등급 계약](../../../../../db/model/table-layout.md#item-grade)을 적용한다. |
| `item_version.equipment_slot` | `TEXT NULL`과 5개 허용값 `WEAPON`, `CHEST`, `HEAD`, `ACCESSORY`, `LEG`. 확인된 장비는 부위를 채우고, 비장비임이 확인된 아이템은 `NULL`이다. | 1.0.0의 팔과 이후 장식을 동일한 부위 `ACCESSORY`로 연결한다. 명칭 전환 패치는 별도 미확인이다. 공식 표의 무기 종류와 옷·머리·팔·다리를 매핑하고 재료·음식 같은 확인된 비장비는 부위 없이 다룬다. 분류가 불명확한 행은 확인 대상으로 넘긴다. [제품 부위 기준](<../../../../../docs/details/product/아이템 탐색과 상세.md#item-information>) |
| `item_version.max_stack_size` | `INTEGER NULL`, 값이 있으면 양의 정수. 기본값 없음. | 현재 공식 표에 값이 없다. 확보한 실제 값만 연결하고 미확인 값은 `NULL`로 보존한다. 비중첩 아이템의 값도 관련 원본 해석을 확인한 뒤 채운다. |

- 후속 마이그레이션에서는 `grade_id`를 처음에 NULL 허용으로 추가해 기존 V2 행의 조회를 보존한다. 기존 행의 등급과 부위는 출처를 대조해 함께 보완한다. 이행 중 기존 행의 빈 부위는 미확인 상태로 다룬다. 완료된 신규·정정 입력에는 서비스가 실재 등급을 요구한다. 기존 행의 등급이 모두 채워진 시점에 DB `NOT NULL`을 별도 반영할 수 있다. 참조 자체는 즉시 FK 검사에 들어간다.
- 부위 열의 DB CHECK는 허용 값 집합을 검사한다. 장비인지와 어떤 부위인지의 대응은 #45의 검증된 분류 매핑에서 확인한다. 현재 종류 트리의 표시 이름은 별도로 변경될 수 있으므로 저장한 부위 값은 버전의 필드로 조회한다. 공식 표의 기존 팔 표기와 후속 장식 표기의 표시 시점은 #44에서 같은 논리 부위에 연결한다.
- 같은 패치 정정은 버전 ID와 기존 이력을 보존한다. 일부 필드의 정정에서 최대 중첩 수량의 입력을 생략하면 기존 값을 유지하고, 확인된 실제 수량이나 명시적인 미확인 상태를 전달한 경우 그 값으로 갱신한다. 존재 상태만 바꾸는 새 버전은 직전 구성의 셋을 함께 승계한다.

#### 능력치 원본·값의 표현과 표시 캐시

- `item_stat`은 `id BIGINT GENERATED ALWAYS AS IDENTITY`를 PK로 둔다. `item_version_id BIGINT NOT NULL`과 `stat_type_id BIGINT NOT NULL`은 각각 `item_version.id`, `stat_type.id`를 참조한다. FK는 삭제 제한·갱신 무동작·즉시 검사다. `UNIQUE(item_version_id, stat_type_id)`와 순서 정정 탐색용 인덱스 `(stat_type_id, item_version_id)`를 둔다. 기존 PK 보호 트리거를 재사용하고 앱 계정의 조회·등록·수정·삭제를 허용한다.
- `value NUMERIC NOT NULL`과 Java `BigDecimal`을 제안한다. 공식 표에서 고정값 −0.5~1,080, 백분율 0.2~200%, 소수 둘째 자리까지 관측했다. 이 범위를 1.0.0의 왕복 검사에 사용한다. 정밀도·스케일을 지정하지 않은 `NUMERIC`은 입력을 지정 자릿수로 반올림하는 과정이 없으므로 이후 패치의 소수도 보존한다. SQL에서 `NaN`과 양·음의 무한대를 거부하고 Java에서 유효한 십진수를 받는다. [PostgreSQL NUMERIC 규칙](https://www.postgresql.org/docs/18/datatype-numeric.html)
- 능력치 종류는 확인된 이름과 단위로 식별한다. 예를 들어 고정 방어 관통과 백분율 방어 관통은 각각 `방어 관통`, `방어 관통 (%)`에 연결하고, `5%`의 원본 값은 `5`다. `(고유)`와 레벨당 표기는 역할을 구별하는 데 보존한다. 철자 차이의 통합, 잘린 백분율, 설치 아이템의 시야 범위는 #45에서 원문 의미를 확인한 뒤 대응 규칙을 정한다.
- 캐시는 기존 [원본·표시 캐시 계약](../task-002.md#stat-cache-transaction)을 따른다. `item_stat`에서 같은 버전의 행을 읽어 `stat_type.sort_order` 순서로 JSONB 배열을 다시 만든다. 항목의 `statTypeId`는 ID 문자열, `value`는 JSON 숫자로 두고 서버에서 `BigDecimal`로 읽는다. 예시 캐시 항목은 `{"statTypeId":"42","value":0.02}`다. API DTO에서 소수값을 문자열 `"0.02"`로 전달하는 안을 제안한다. 이 형태는 화면이 부동소수점으로 변환하지 않고 값을 표시할 수 있게 한다. [공통 API ID 규칙](<../../../../../docs/details/development/공통 DB 모델.md#internal-identifiers>) · [PostgreSQL JSONB 수치 표현](https://www.postgresql.org/docs/18/datatype-json.html)
- 원본과 캐시를 같은 Spring 트랜잭션으로 저장한다. 같은 패치의 정정에서 능력치 입력을 생략하면 기존 원본을 유지하고, 빈 목록은 원본 제거와 캐시 `[]`로 반영한다. 새 버전의 구성이 유지되는 경우 직전 버전의 원본과 함께 캐시를 생성한다. 능력치 저장과 공통 순서 변경은 기준 잠금 뒤 버전 행을 ID 순서로 잠그는 기존 계약을 그대로 사용한다. 실제 `sort_order` 값은 초기 실자료 종류 목록에 순서값을 붙이는 시점에 사용자에게 확인한다.

#### 구현 뒤 확인할 사례

| 확인 | 기대 결과 |
| --- | --- |
| V2 기존 행과 신규 아이템 | 등급 없는 이전 행은 조회된다. 완성된 신규 버전에는 존재하는 등급을 요구한다. 장비의 부위는 허용값으로 저장되며, 확인한 비장비에는 부위가 비어 있다. |
| 최대 중첩 미확인·보완 | `NULL`이 재조회된다. 양의 실제 값을 같은 버전에 채울 수 있고 0과 음수는 거부한다. 생략한 정정은 기존 값을 보존한다. |
| 값·관계·전달 | `-0.5`, `0.02`, `0.2%`, `200%`, `1080`과 소수 셋째 자리 이상의 합성 값이 DB·Java·캐시·API에서 의도한 값으로 왕복한다. JavaScript 안전 정수 범위를 넘는 능력치 종류 ID도 문자열로 보존한다. 누락 참조, 같은 종류 중복, 비유한 숫자는 거부된다. |
| 목록과 트랜잭션 | 대표 합성 순서에서 원본·캐시가 일치한다. 같은 패치 정정과 캐시 재생성 실패의 롤백, 순서 변경과 저장의 경합, 명시적 빈 목록의 `[]`가 기대대로 동작한다. |

- 잔여: 등급의 이행 조건, 부위의 표현, 수치 저장·API안을 구현 전 대조한다. 실제 표시 순서와 #45의 보완값은 각각 필요한 시점에 확인한다. 표를 생성하는 실행에는 [전체 구조와 실행 대상 확인](../../../../../db/migration/README.md#precreation-confirmation)을 적용한다.

<a id="followup-storage-implementation"></a>

### 후속 저장·조회 구현과 DB 없는 확인

- 할 일: [43-002 저장 구현](../task-002.md#work-storage). 사용자는 [공식 1.0.0 기준 후속 설계안](#remaining-storage-design)의 구현을 지시했고, 실제 DB 적용 전에 변경 구조와 실행 대상을 확인하기로 했다.
- 반영: [V3 SQL](../../../../../db/migration/V3__complete_item_storage.sql)과 `ItemCatalogService`에 버전별 등급·부위·최대 중첩 수량, `item_stat` 원본, 표시 캐시 갱신과 재조회 DTO를 구현했다. 기존 V2 행의 빈 등급·부위·중첩 수량은 그대로 읽는다. 완성된 신규 버전과 같은 패치 정정에는 유효한 등급을 요구한다. 명시적 중첩 `NULL`과 입력 생략을 구분하며, 공개 값 DTO는 능력치 ID와 십진값을 문자열로 제공한다.
- 확인: 제품 Flyway 경로에 V3가 없을 때 포장 테스트가 명시한 단언에서 실패했다. 구현 뒤 DB 없는 단위 테스트 41건과 bootJar 빌드를 통과했다. JAR의 V1·V2 SQL은 기존 원천과 같고 V3는 현재 원천과 바이트 단위로 일치했다. JDBC 연결 없이 Hibernate 엔티티 15개, `equipment_slot`의 TEXT·능력치의 NUMERIC 매핑, 저장 관련 HQL 6개를 확인했다. 변경 Java 파일 포맷은 일치했다. 전체 작업 폴더의 Spotless 검사에서는 기존 미수정 Java 파일의 CRLF 차이가 보고됐다.
- 후속 확인: [두 격리 DB의 V3 통합 검증](#isolated-v3-results)과 [조회·참조 계약 인계](#storage-handoff)를 마쳤다.

<a id="v3-precreation-review"></a>

### V3 생성 직전 확인 대상

- [V3 전체 SQL](../../../../../db/migration/V3__complete_item_storage.sql)의 SHA-256은 `610622a531770994696ee295da6bc360e2a27ae48358acd08dc354fb1867a6bd`다. `item_version`에 기본값 없는 NULL 허용 열 3개를 추가한다. `grade_id BIGINT`는 `item_grade(id)` FK이며 삭제 제한·갱신 무동작·즉시 검사다. `equipment_slot TEXT`는 `WEAPON`, `CHEST`, `HEAD`, `ACCESSORY`, `LEG`만 받는다. `max_stack_size INTEGER`는 값이 있으면 1 이상이다. V3는 기존 행에 세 값을 채우지 않으며, 서비스에서 완성된 새 버전과 정정에 등급을 요구한다.
- 신규 `item_stat`은 `id BIGINT GENERATED ALWAYS AS IDENTITY` PK, 필수 `item_version_id BIGINT`와 `stat_type_id BIGINT` FK, 정밀도·스케일 지정 없는 필수 `value NUMERIC`으로 구성한다. 두 FK는 삭제 제한·갱신 무동작·즉시 검사다. 한 버전에 종류 하나당 한 행을 허용하고, 비유한 숫자를 CHECK로 거부한다. `(stat_type_id, item_version_id)` 인덱스와 기존 PK 보호 함수의 트리거를 추가한다. 앱 계정 `lumia_app`에는 이 표의 조회·등록·수정·삭제 권한을 부여한다. V3는 `lumia_migrator`가 적용하며 실패 시 V3가 추가한 열·표·제약·인덱스·트리거·권한이 한 트랜잭션에서 돌아간다.
- 제안 실행 대상은 로컬 Docker Desktop `desktop-linux`의 새 Testcontainers `postgres:18.6` 하나다. 컨테이너 5432는 임의의 로컬 포트에 매핑한다. `lumiawiki/public`에서는 빈 DB의 V1→V2→V3 설치와 통합 사례를 점검한다. 같은 컨테이너의 `catalog_item_upgrade/public`에서는 합성 V1 행과 V2 아이템 버전을 저장한 뒤 V3로 갱신해 기존 ID·필드, 새 필드의 NULL, 보완 정정을 대조한다.
- 대상 통합 검사는 `.\backend\gradlew.bat -p backend integrationTest --tests 'io.github.minokim.lumiawiki.catalog.CommonCatalogIntegrationTests.itemStorage*' --offline`에서 선택되는 6건이다. 캐시 쓰기 실패는 첫 격리 DB에 합성 행 한 개에만 적용되는 테스트용 CHECK를 추가하고 사례 직후 제거해서 검증한다. 기존 개발 DB와 실제 게임 자료는 실행 범위에서 제외한다.

<a id="isolated-v3-results"></a>

### 두 격리 DB의 V3 통합 검증 결과

- 실행: 사용자가 위 두 격리 대상을 승인한 뒤 기록한 SHA-256과 일치하는 V3로 `.\backend\gradlew.bat -p backend '-PtddReportDir=build/reports/item-storage-v3-isolated' integrationTest --tests 'io.github.minokim.lumiawiki.catalog.CommonCatalogIntegrationTests.itemStorage*' --offline`을 실행했다. PostgreSQL 18.6 컨테이너 `efc549b127d7`의 `127.0.0.1:50081`만 사용했으며, JUnit XML의 접속 로그와 6개 사례를 대조했다.
- 빈 `lumiawiki/public`: Flyway V1→V2→V3 설치와 JPA 검증 및 재실행 시 마이그레이션 0건을 확인했다. 기존 스킬 저장·참조·정정, 등급 FK·부위·중첩 수량·비유한 능력치 제약, PK 보호와 앱 권한 검사를 통과했다.
- `lumiawiki/public`의 능력치 동작: 부호·소수 값의 정확한 왕복, 후속 버전의 값·부위·중첩 수량 승계, 빈 목록의 원본 삭제와 캐시 `[]`를 확인했다. 테스트용 CHECK로 캐시 쓰기를 실패시켰을 때 기존 원본과 캐시가 함께 보존됐으며 테스트용 제약은 사례 뒤 제거했다. 저장이 먼저인 경우와 순서 정정이 먼저인 경우 모두 후행 업무의 잠금 대기와 최종 캐시의 새 값·순서 일치를 검증했다.
- `catalog_item_upgrade/public`: V1의 합성 공통 자료와 V2 아이템 버전을 준비하고 V3로 갱신했다. 기존 버전의 ID·참조·이름·빈 캐시와 새 필드의 `NULL`이 유지됐으며, 같은 버전에 등급을 채우는 정정과 신규 저장·조회를 확인했다.
- 판정: 선택한 통합 검사 6건 모두 통과했다. 임시 컨테이너 제거를 확인했다. 기존 개발 DB에는 접속하지 않았고 실제 게임 자료나 공식 표시 순서는 등록하지 않았다.

<a id="storage-handoff"></a>

## V3 조회·참조 계약 인계

[격리 검증](#isolated-v3-results)에서 확인한 저장 결과를 아래 두 작업의 입력으로 넘긴다. 실제 아이템 값·공식 능력치 표시 순서는 자료 확인 후 정한다.

<a id="handoff-search-detail"></a>

### Issue #44 검색과 기본 상세

- P1 개별 아이템 페이지는 v1.0.0 정보만 표시한다. [Phase 001 검색·상세 범위](../../phase.md#agreed-search-detail-scope). 현재 `ItemCatalogService.getItemVersion`은 내부 아이템 **버전 ID**로 스냅샷을 읽는다. 검색, 조회 패치 Q에서의 유효 버전 선택, HTTP 경로는 후속 구현 범위다. 응답에 ID를 내보낼 때는 문자열로 전달한다. 아이템 전체의 `searchable`과 버전별 `is_deleted`는 각각 검색 노출과 그 버전에서의 삭제 상태를 뜻한다.
- 등급·장착 부위·최대 중첩 수량은 버전별 값이다. 최대 중첩 수량 NULL은 미확인 상태다. V2에서 이관한 등급 미확정 행에서는 장착 부위 NULL도 미확정일 수 있다. 장착하지 않는 아이템의 부위는 NULL이다. 공식 표의 ‘팔’과 후속 ‘장식’은 ACCESSORY에 대응한다. 장비 분류 명칭이 바뀐 패치의 경계는 미확인이다.
- 능력치는 저장 시 확정한 배열 순서대로 읽는다. 내부 반환값 stats는 능력치 종류 ID와 정확한 십진값을 문자열로 제공하고, 종류 이름과 순서는 `listStatTypes`에서 읽는다. 이름이 ' (%)'로 끝나는 종류의 값은 퍼센트 점수로 저장한다(5%는 '5'). 원본/캐시가 비어 있으면 빈 목록을 읽는다.
- 스킬에 표시하는 문구는 연결 행의 `displayDescription`이다. NULL이면 빈 문자열로 표시하며 빈 문자열 직접 입력도 빈 표시를 유지한다. 원문은 링크가 가리키는 스킬 버전의 `originalDescription`으로 별도 보존한다. [#44 선행 입력](../../issue-44/issue.md#plan).

<a id="handoff-integrated-verification"></a>

### Task 43-004 유효 버전과 참조·갱신 검증

- 조회 패치 Q에서 `game_patch.sort_order` 기준으로 Q 이하에 시작한 가장 최근 아이템 버전을 선택한다. 해당 버전 ID로 스킬 연결을 읽고, 연결 행의 기준 패치는 아이템 버전의 시작 패치와 일치시킨다. 연결이 가리킨 스킬 버전의 소속과 시작 패치를 확인한다. 스킬 버전은 해당 아이템 버전의 시작 패치 이전 또는 같은 패치에 유효해야 한다. 참조는 연결에 저장된 정확한 스킬 버전을 따른다.
- 예를 들어 아이템 I0가 P1에서 시작해 P0의 스킬 S0를 가리키고, 능력치만 바뀐 I1이 P3에서 S0를 이어받으면, P2 조회는 I0·P1 연결·S0, P4 조회는 I1·P3 연결·S0를 읽는다. 소속이 다른 스킬과 아이템 버전보다 나중 패치에 시작한 스킬 참조는 거부한다.
- 같은 패치의 입력 정정은 아이템 및 아이템 버전 ID를 유지한다. 능력치·스킬 목록 생략은 기존 값 보존, 빈 목록은 모두 삭제다. 최대 중첩 수량 변경 생략은 기존 값 보존, `MaxStackChange(null)`은 NULL로 정정한다. 공통 능력치 순서를 바꾸면 영향을 받는 과거·현재 버전의 배열을 재구성한다.
- 아이템 버전 저장은 패치와 `stat_type`의 `SHARE` 잠금 뒤 상위 `item` 행을 잠근다. 같은 아이템의 저장은 순차 처리되며 서로 다른 아이템의 일반 저장은 병행할 수 있다. 능력치 순서 정정은 `stat_type`의 SHARE ROW EXCLUSIVE 잠금 뒤 영향받는 `item_version`을 ID 오름차순으로 잠근다. 격리 검증에서 능력치 저장과 순서 정정의 두 실행 순서, 캐시 실패 시 원본과 캐시의 동시 롤백을 확인했다. Task 43-004는 다른 저장 관계를 붙인 결합 조회·갱신에서 이 계약을 다시 확인한다. [43-004 검증 범위](../task-004.md#plan).

<a id="v3-candidate-review"></a>

## V3 제출 후보 검수

- 범위는 `94f53cf` 이후 V3 구현·테스트 11개와 담당 실행 기록·Task·Phase 001·현황 4개다. #44·43-004에 추가한 인계 링크, 기존 43-004 변경과 #45의 자료 입력 기록은 후보에서 제외했다. 실제 Git 인덱스와 브랜치에 적용한 변경은 없다.
- 임시 복사본에서 V3의 테스트 대상 동작을 제거한 상태로 단위 테스트 41건 중 지정한 단언 6건의 실패를 확인했다. 후보 코드를 복원해 41건 통과, Spotless와 bootJar 성공을 확인했다. 이전 [격리 통합 검사 6건](#isolated-v3-results)의 Java 클래스 지문(제품 51개·테스트 17개)과 Flyway SQL 바이트가 후보와 일치했다. 이번 검수에서 DB를 다시 실행하지 않았다.
- 별도 검수와 자체 대조에서 V2 이관 아이템의 등급이 NULL이면 `recordItemExistence`가 `gradeId` 입력 오류를 내고 삭제·복귀 버전을 남기지 않는 결함을 확인했다. 상태 변경은 직전 구성을 승계한다는 [합의](../task-002.md#item-existence)를 깨뜨린다. 완성된 신규 입력의 등급 검사는 유지하고, 상태만 바뀌는 경로에서 기존 NULL 승계를 보장한 뒤 새 회귀 사례로 확인해야 한다. [현재 서비스](../../../../../backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemCatalogService.java).
- 격리 결과는 능력치 저장 중 캐시 실패의 롤백과 저장·순서 정정의 양방향 잠금 대기를 확인했다. 당시에는 순서 정정 자체에서 캐시가 실패하는 롤백과 일반 저장 두 건의 잠금 범위가 미확인이었다. 같은 아이템의 버전별 쓰기는 상위 `item` 행 잠금으로 직렬화된다. [확인 계획](../task-002.md#verification).
- 검수 지적은 [보완과 재검증](#v3-existence-regression)에 연결한다.

<a id="v3-existence-regression"></a>

## V2 이관 행의 상태 변경 보완과 V3 재검증

- 수정: 삭제·복귀 버전은 직전 아이템 버전의 등급을 승계한다. V2에서 이관해 등급이 `NULL`인 경우 그 값을 유지한다. 완성된 새 아이템·새 버전과 입력 정정에는 유효한 등급을 계속 요구한다. V3 SQL의 지문과 승인된 실행 구조는 동일하다.
- 단위: 최종 테스트 소스에 기존 후보 코드를 넣어 단위 테스트 42건 중 등급 승계 단언 1건이 실패함을 확인했다. 수정 코드를 복원해 42건 통과와 Spotless·bootJar 성공을 확인했다.
- 격리 재검증: 로컬 PostgreSQL 18.6 임시 컨테이너 `f0a14b348941`의 `127.0.0.1:64602`에서 `itemStorage` 통합 사례 8건을 모두 통과했다. `lumiawiki/public`에서는 V1→V2→V3와 권한·트랜잭션을, `catalog_item_upgrade/public`에서는 이관 아이템의 삭제·복귀 후 새 버전 ID·패치·`NULL` 등급 승계와 원래 버전 보존을 확인했다. 임시 컨테이너를 제거했다. 개발 DB 적용과 실제 자료 등록은 수행하지 않았다.
- 롤백: 능력치 순서 정정 중 뒤쪽 버전의 캐시 갱신을 테스트용 CHECK로 실패시켰다. 재조회한 종류 이름·순서, 과거·현재 버전의 캐시와 능력치 원본이 모두 유지됐다. 제약을 제거한 뒤 같은 순서 정정이 두 버전 캐시에 반영됐다.
- 잠금: 일반 저장 두 건이 같은 버전 또는 같은 아이템의 서로 다른 버전을 수정하면 둘째 업무가 상위 아이템 행 잠금에서 기다렸다. 다른 아이템의 실제 변경은 첫 업무의 트랜잭션이 열린 상태에서 커밋됐고, 완료 뒤 각 원본 값과 캐시가 일치했다. 능력치 저장과 순서 정정 사이의 양방향 대기도 재확인했다.
- 검수: 자체·별도 대조에서 완성 입력의 등급 필수 검사, V2 이관 상태의 승계, 두 롤백 기준값의 DB 재조회, 서로 다른 아이템의 실제 값 변경을 확인했다.
- 검증 기준 확정: 사용자는 같은 아이템의 여러 패치를 동시에 정정할 필요가 없다고 판단했다. 같은 아이템은 버전이 달라도 순차 저장하고 서로 다른 아이템의 일반 저장은 병행한다. 상위 `item` 행 잠금은 기존 버전 정정과 그 값을 이어받는 새 버전 저장의 순서를 보장한다. 기존 격리 테스트 `itemStorageSerializesWritesForOneItemAndAllowsOtherItemsToProceed`가 [확정된 기준](../task-002.md#verification)을 충족하는 근거다.

<a id="v3-local-submission"></a>

## V3 로컬 커밋 범위

- 사용자가 확정한 같은 아이템의 순차 저장과 서로 다른 아이템의 병행 저장 기준을 반영한다. 저장 코드·테스트·Flyway SQL은 [격리 재검증](#v3-existence-regression)의 대상과 같다.
- 현재 작업 브랜치에 V3 구현·테스트와 43-002 실행 기록·Task·Phase 001·현황을 담는다. #44·43-004의 인계 링크와 별도 작업, #45 자료 확인 변경은 작업 트리에 보존한다.
- 이 제출의 승인 범위는 로컬 커밋이다. 원격 제출과 부모 통합에는 별도 작업이 남아 있다.

<a id="v2-v3-pr-verification"></a>

## 원격 부모 기준 제출 검증

- 원격 부모는 `76e2622`다. 43-002의 V2·V3 코드, 관련 기준과 완료 기록을 현재 부모의 파일에 맞춰 선별했다.
- 제출 복사본에서 V2 SQL을 빼 포장 단언 1건의 실패를 확인했다. V2 SQL을 복원한 최종 후보의 단위 테스트 42건이 통과했다. 기존 두 격리 DB의 결과는 앞의 재검증 근거를 사용한다.

<!-- tdd-plan -->
```json
{
  "schema": 1,
  "cycles": [
    {
      "id": "initial-item-storage",
      "kind": "behavior",
      "expectation": "V2가 제품 Flyway 경로에 들어가고 필수 문자열·스킬 소속·중복·패치 시점·설명 보존 계약을 검증한다.",
      "targets": [
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogErrors.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogReferenceCheck.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CommonCatalogStore.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/Item.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemCatalogService.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemSkillDefinition.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemSkillDefinitionVersion.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemSkillReferenceCheck.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersion.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersionSkillLink.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/StatType.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/common/api/ApiFailure.java",
        "db/migration/V2__create_item_storage.sql"
      ],
      "tests": [
        "backend/src/test/java/io/github/minokim/lumiawiki/catalog/CommonCatalogIntegrationTests.java",
        "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemCatalogServiceTests.java"
      ],
      "settings": [
        "db/migration/V1__create_common_model.sql",
        "db/bootstrap/10-prepare-roles.sh",
        "db/bootstrap/sql/prepare-roles.sql",
        "backend/src/main/resources/application-local.yaml"
      ],
      "adapter": "junit",
      "command": [
        "backend/gradlew.bat",
        "-p",
        "backend",
        "-PtddReportDir={report}",
        "test",
        "--offline"
      ],
      "expectedFailures": [
        "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.packagesTheItemMigrationAtTheProductFlywayLocation()",
        "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rejectsMissingAndBlankSkillDescriptionsWithTheAgreedContext()",
        "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.checksRequiredItemAndStatTypeNamesBeforeWriting()",
        "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.separatesMismatchedOwnersDuplicateLinksAndFutureVersions()",
        "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.keepsTheSelectedSkillVersionAndOriginalAndTemporaryDescriptionsDistinct()"
      ]
    },
    {
      "id": "followup-item-storage-v3",
      "kind": "behavior",
      "expectation": "V3 포장, 기존 V2 조회와 등급 입력, 중첩 NULL·생략 구분, 능력치 정확한 값·정렬·중복과 순서 변경을 검증한다.",
      "targets": [
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogErrors.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CommonCatalogStore.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemCatalogService.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersion.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/EquipmentSlot.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemStat.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemStatCache.java",
        "db/migration/V3__complete_item_storage.sql"
      ],
      "tests": [
        "backend/src/test/java/io/github/minokim/lumiawiki/catalog/CommonCatalogIntegrationTests.java",
        "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemCatalogServiceTests.java",
        "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemStorageMigrationTests.java"
      ],
      "settings": [
        "db/migration/V1__create_common_model.sql",
        "db/migration/V2__create_item_storage.sql",
        "db/bootstrap/10-prepare-roles.sh",
        "db/bootstrap/sql/prepare-roles.sql",
        "backend/src/main/resources/application-local.yaml"
      ],
      "adapter": "junit",
      "command": [
        "backend/gradlew.bat",
        "-p",
        "backend",
        "-PtddReportDir={report}",
        "test",
        "--offline"
      ],
      "expectedFailures": [
        "io.github.minokim.lumiawiki.catalog.ItemStorageMigrationTests.packagesTheFollowupMigrationAtTheProductFlywayLocation()",
        "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.readsLegacyDetailsWithUnknownGradeAndRequiresGradeForNewCompleteInput()",
        "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.distinguishesStackSizePreservingSettingAndClearing()",
        "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.preservesExactDecimalsAndBigIdsInTheSortedCacheView()",
        "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rejectsDuplicatesAndUnknownStatTypesBeforeReplacingTheOriginals()",
        "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rebuildingOrderLocksAffectedVersionsAndKeepsTheOriginalValues()"
      ]
    },
    {
      "id": "legacy-existence-v3-verified",
      "kind": "behavior",
      "expectation": "등급 미확정 V2 이관 아이템의 삭제·복귀 경로가 직전 구성을 보존하고, 완성된 아이템 등록·정정은 유효한 등급을 계속 요구한다.",
      "targets": [
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogErrors.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CommonCatalogStore.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemCatalogService.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersion.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/EquipmentSlot.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemStat.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemStatCache.java",
        "db/migration/V3__complete_item_storage.sql"
      ],
      "tests": [
        "backend/src/test/java/io/github/minokim/lumiawiki/catalog/CommonCatalogIntegrationTests.java",
        "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemCatalogServiceTests.java",
        "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemStorageMigrationTests.java"
      ],
      "settings": [
        "db/migration/V1__create_common_model.sql",
        "db/migration/V2__create_item_storage.sql",
        "db/bootstrap/10-prepare-roles.sh",
        "db/bootstrap/sql/prepare-roles.sql",
        "backend/src/main/resources/application-local.yaml"
      ],
      "adapter": "junit",
      "command": [
        "backend/gradlew.bat",
        "-p",
        "backend",
        "-PtddReportDir={report}",
        "test",
        "--offline"
      ],
      "expectedFailures": [
        "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.preservesUnknownLegacyGradeWhenOnlyExistenceChanges()"
      ]
    },
    {
      "id": "v2-v3-pr-replay",
      "kind": "behavior",
      "expectation": "원격 부모 기준으로 V2 포장과 V3까지 포함한 전체 아이템 저장·조회 후보에서 최종 단위 테스트를 재검증한다.",
      "targets": [
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogErrors.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogReferenceCheck.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CommonCatalogStore.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/EquipmentSlot.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/Item.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemCatalogService.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemSkillDefinition.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemSkillDefinitionVersion.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemSkillReferenceCheck.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemStat.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemStatCache.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersion.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersionSkillLink.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/StatType.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/common/api/ApiFailure.java",
        "db/migration/V2__create_item_storage.sql",
        "db/migration/V3__complete_item_storage.sql"
      ],
      "tests": [
        "backend/src/test/java/io/github/minokim/lumiawiki/catalog/CommonCatalogIntegrationTests.java",
        "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemCatalogServiceTests.java",
        "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemStorageMigrationTests.java"
      ],
      "settings": [
        "backend/src/main/resources/application-local.yaml",
        "db/bootstrap/10-prepare-roles.sh",
        "db/bootstrap/sql/prepare-roles.sql",
        "db/migration/V1__create_common_model.sql",
        "db/migration/V2__create_item_storage.sql"
      ],
      "adapter": "junit",
      "command": [
        "backend/gradlew.bat",
        "-p",
        "backend",
        "-PtddReportDir={report}",
        "test",
        "--offline"
      ],
      "expectedFailures": [
        "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.packagesTheItemMigrationAtTheProductFlywayLocation()"
      ]
    }
  ]
}
```

<!-- tdd-evidence -->
```json
{
  "schema": 1,
  "receipts": [
    {
      "id": "initial-item-storage",
      "kind": "behavior",
      "spec": "743d89c4922364d89a10c183c841b88b57aef4774c97ec5e5a960a5edc89ebc6",
      "worktree": "0bfa41ec5bab85c8b93c",
      "baseline": "fae9ccb50869545aff68a0b3b34deac6db0c45f6",
      "task": "work/records/phase-001/issue-43/artifacts/task-002-execution.md",
      "finished": true,
      "red": {
        "runId": "f213ac54b7aa4ec7b0b192da7c8a943e",
        "started": 1795233663.7384868,
        "finishedAt": 1795233692.9292154,
        "command": [
          "backend/gradlew.bat",
          "-p",
          "backend",
          "-PtddReportDir={report}",
          "test",
          "--offline"
        ],
        "exitCode": 1,
        "result": {
          "tests": 35,
          "failures": 5,
          "errors": 0,
          "skipped": 0,
          "names": [
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapDuplicatesAreRejectedBeforeReplacement()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchBoundaryZeroAndNinetyNineAreAccepted()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapQueryDistinguishesUnknownFromConfirmedEmpty()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.knownBusinessConstraintsUseExistingInputError()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.seasonKeepsUnknownMetadataAndComputesWideOrder()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchBoundsAreRejectedBeforeWriting()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchUsesSeasonOrderAndTruncatesSubseconds()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.workingRegionRenameDoesNotChangeMapHistory()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.dependentFailureRollsBackTheSpringTransactionBoundary()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.unexpectedPkGuardRemainsAnInternalFailure()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.categoryCycleIsRejectedUnderTheTreeLock()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.badNamesAndReversedDatesAreRejected()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.dependentReferenceFailureIsPropagated()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.missingMapRegionsAreRejected()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapQueryReturnsPublicNamesOnly()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.writeTransactionUsesReadCommitted()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.missingQueryPatchHasNoMapResult()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.nullMapAndConfirmedEmptyMapRemainDifferent()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.mapSelectionAndMembersUseOneQueryWithoutReaderLocks()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.writersAcquireBasisLocksInTheAgreedOrder()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.rowProjectionPreservesLargeIdsAndPublicNames()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rejectsMissingAndBlankSkillDescriptionsWithTheAgreedContext()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.separatesMismatchedOwnersDuplicateLinksAndFutureVersions()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.checksRequiredItemAndStatTypeNamesBeforeWriting()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.packagesTheItemMigrationAtTheProductFlywayLocation()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.keepsTheSelectedSkillVersionAndOriginalAndTemporaryDescriptionsDistinct()",
            "io.github.minokim.lumiawiki.FoundationApiTests.internalFailureRedactsResponsesAndLogs()",
            "io.github.minokim.lumiawiki.FoundationApiTests.unsupportedMethodKeeps405()",
            "io.github.minokim.lumiawiki.FoundationApiTests.normalAndEmptyResponsesHaveServerOwnedRequestIds()",
            "io.github.minokim.lumiawiki.FoundationApiTests.slowResponseUsesOneSecondDelay()",
            "io.github.minokim.lumiawiki.FoundationApiTests.badInputAndMissingUseProblemDetail()",
            "io.github.minokim.lumiawiki.FoundationApiTests.mvcValidationAndParsingRemain400()",
            "io.github.minokim.lumiawiki.FoundationApiTests.profileGatesDevEndpoint()",
            "io.github.minokim.lumiawiki.TestEnvironmentTests.junitMockitoAndMockMvcRunWithoutDocker()",
            "io.github.minokim.lumiawiki.TestEnvironmentTests.beanValidationRejectsInputBeforeCallingTheCollaborator()"
          ],
          "failedNames": [
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rejectsMissingAndBlankSkillDescriptionsWithTheAgreedContext()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.separatesMismatchedOwnersDuplicateLinksAndFutureVersions()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.checksRequiredItemAndStatTypeNamesBeforeWriting()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.packagesTheItemMigrationAtTheProductFlywayLocation()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.keepsTheSelectedSkillVersionAndOriginalAndTemporaryDescriptionsDistinct()"
          ]
        },
        "manifest": {
          ".codex/hooks.json": "afb95b34e8d441cbd42a7535736128ce520e2ab9c016211d1739a0b40ff4e900",
          ".gitattributes": "4437511f6b3b866745490f0fcd2332d1e6194980fc028232ce0a84cec608d85b",
          "backend/build.gradle": "52b40fbbcdbb75b4ee5d5997811157a0ed61562cbd87c9eb6c3d859a88dd7960",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogErrors.java": "007c174d53aa1922cab1892729cbf1fa29d59eac17ffd5ac890a300998d41a0f",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogReferenceCheck.java": "1fb4aea7e2d2af5d50d81f813e657b90acf136a8dcacc1fc19ac7adf9dbd7ffd",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CommonCatalogStore.java": "67accea047ba46f5e4247a540693752271bb565c4a2a793aca726da369bd906b",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/Item.java": "58a6bda3b7d01969a9e6958c7063f16f61467989a6faac4392d999a8b4de461f",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemCatalogService.java": "f6f183b789032e35d4d6d796fe0671b2876ecc12c494d063208112bc05508a50",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemSkillDefinition.java": "1e26d5216f230379aeff168536eefcadb9e5d4947d26c678d17c0bb0fde3d747",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemSkillDefinitionVersion.java": "4040ace621d202a2937d1f1244e2b89a69434f5bdabc73aa78f9a7ebdae3e448",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemSkillReferenceCheck.java": "c961bf297e544df14aba90c4e2a274cad3acec34309fd9c20158eff47c8b8c12",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersion.java": "f85801bdde00227d1db384c8f4be8e76a1fa632190f1f5b43e8e6a890bfa5f72",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersionSkillLink.java": "c7c41f41c8c05ed3714e5340c3effbbefc7eeb4138664ca35cf4bcfdad818ad1",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/StatType.java": "4c9b1f7bba977042504fe03133223e8d5c1f703b0c1567e49c8ed9b3893ef4ce",
          "backend/src/main/java/io/github/minokim/lumiawiki/common/api/ApiFailure.java": "d01ace83a4a170451b4cac7a4c7a4f8fd668dd2b669069bd8a4c39691a41243a",
          "backend/src/main/resources/application-local.yaml": "e161d9789956b24211bc886419f0d2791c634be0238e82678a3575fbeeb46144",
          "backend/src/main/resources/application.yaml": "d10d1ef05ddbec053c30bf2bc705e4c5f19a2b688baccd61a4f48af556bb40e0",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/CommonCatalogIntegrationTests.java": "7039b8f1dd95b6a74872f2961125def89a13b2332206f81c76d2fd8e9796031e",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemCatalogServiceTests.java": "dd8edc56f7f891a0776d48fe8626cfd0a307d5a7e8d85f178cd5543a8b7a24ba",
          "backend/src/test/resources/application-test.yaml": "e6aa7eb8da29c749b63e7330c634631d82f8710dc4fb6dee5ef883df1ce12e72",
          "db/bootstrap/10-prepare-roles.sh": "832e9921588251e3a658fadc276ff7d3b46a46b110c45ae7a16cd4eb7819914a",
          "db/bootstrap/sql/prepare-roles.sql": "160a624d9577848f6e61404ad3e52791c6a395af56186fec08e852f3f88ff8d4",
          "db/migration/V1__create_common_model.sql": "1495d8a5085188f535865f9b46f51aa1c9a18480c1b49efd68df61c43f5b8ddd",
          "db/migration/V2__create_item_storage.sql": null,
          "frontend/package-lock.json": "e54e76e4ab1a402d4df0827152d1bf5c62142cd59e2798518b7ed2715931fc97",
          "frontend/package.json": "aae2e6358d704e1807f860f58272e3f8024cfdc092860bd0b0b4f7d58e76a228",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "2e55a2050f22641deaad0ac4b9b6723ad76aadab22ab037b9d38b1697a458367",
          "frontend/vitest.config.mjs": "f07e4974ad24bc562f5a975e8af587eb6fdfb402863825c718cfdf9a8b684eec",
          "package-lock.json": "539f24e43b65266883d2aa1a83428d75484cf059eeedcedf4043d09dc6d8a5e3",
          "package.json": "0e57b51524c8151aafb0155a93c5f61c30901819bde6cee895c0106f6dfcab85",
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": false
      },
      "final": {
        "runId": "105e597bef474198969027947b8e6e96",
        "started": 1795233693.7439709,
        "finishedAt": 1795233706.9631214,
        "command": [
          "backend/gradlew.bat",
          "-p",
          "backend",
          "-PtddReportDir={report}",
          "test",
          "--offline"
        ],
        "exitCode": 0,
        "result": {
          "tests": 35,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "names": [
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapDuplicatesAreRejectedBeforeReplacement()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchBoundaryZeroAndNinetyNineAreAccepted()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapQueryDistinguishesUnknownFromConfirmedEmpty()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.knownBusinessConstraintsUseExistingInputError()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.seasonKeepsUnknownMetadataAndComputesWideOrder()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchBoundsAreRejectedBeforeWriting()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchUsesSeasonOrderAndTruncatesSubseconds()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.workingRegionRenameDoesNotChangeMapHistory()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.dependentFailureRollsBackTheSpringTransactionBoundary()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.unexpectedPkGuardRemainsAnInternalFailure()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.categoryCycleIsRejectedUnderTheTreeLock()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.badNamesAndReversedDatesAreRejected()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.dependentReferenceFailureIsPropagated()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.missingMapRegionsAreRejected()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapQueryReturnsPublicNamesOnly()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.writeTransactionUsesReadCommitted()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.missingQueryPatchHasNoMapResult()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.nullMapAndConfirmedEmptyMapRemainDifferent()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.mapSelectionAndMembersUseOneQueryWithoutReaderLocks()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.writersAcquireBasisLocksInTheAgreedOrder()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.rowProjectionPreservesLargeIdsAndPublicNames()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rejectsMissingAndBlankSkillDescriptionsWithTheAgreedContext()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.separatesMismatchedOwnersDuplicateLinksAndFutureVersions()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.checksRequiredItemAndStatTypeNamesBeforeWriting()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.packagesTheItemMigrationAtTheProductFlywayLocation()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.keepsTheSelectedSkillVersionAndOriginalAndTemporaryDescriptionsDistinct()",
            "io.github.minokim.lumiawiki.FoundationApiTests.internalFailureRedactsResponsesAndLogs()",
            "io.github.minokim.lumiawiki.FoundationApiTests.unsupportedMethodKeeps405()",
            "io.github.minokim.lumiawiki.FoundationApiTests.normalAndEmptyResponsesHaveServerOwnedRequestIds()",
            "io.github.minokim.lumiawiki.FoundationApiTests.slowResponseUsesOneSecondDelay()",
            "io.github.minokim.lumiawiki.FoundationApiTests.badInputAndMissingUseProblemDetail()",
            "io.github.minokim.lumiawiki.FoundationApiTests.mvcValidationAndParsingRemain400()",
            "io.github.minokim.lumiawiki.FoundationApiTests.profileGatesDevEndpoint()",
            "io.github.minokim.lumiawiki.TestEnvironmentTests.junitMockitoAndMockMvcRunWithoutDocker()",
            "io.github.minokim.lumiawiki.TestEnvironmentTests.beanValidationRejectsInputBeforeCallingTheCollaborator()"
          ],
          "failedNames": []
        },
        "manifest": {
          ".codex/hooks.json": "afb95b34e8d441cbd42a7535736128ce520e2ab9c016211d1739a0b40ff4e900",
          ".gitattributes": "4437511f6b3b866745490f0fcd2332d1e6194980fc028232ce0a84cec608d85b",
          "backend/build.gradle": "52b40fbbcdbb75b4ee5d5997811157a0ed61562cbd87c9eb6c3d859a88dd7960",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogErrors.java": "007c174d53aa1922cab1892729cbf1fa29d59eac17ffd5ac890a300998d41a0f",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogReferenceCheck.java": "1fb4aea7e2d2af5d50d81f813e657b90acf136a8dcacc1fc19ac7adf9dbd7ffd",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CommonCatalogStore.java": "67accea047ba46f5e4247a540693752271bb565c4a2a793aca726da369bd906b",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/Item.java": "58a6bda3b7d01969a9e6958c7063f16f61467989a6faac4392d999a8b4de461f",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemCatalogService.java": "4d4b91cc61ac004ae6140492f5b052d4cb2dc12f63b84ce07fe89fcd917b29c1",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemSkillDefinition.java": "1e26d5216f230379aeff168536eefcadb9e5d4947d26c678d17c0bb0fde3d747",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemSkillDefinitionVersion.java": "4040ace621d202a2937d1f1244e2b89a69434f5bdabc73aa78f9a7ebdae3e448",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemSkillReferenceCheck.java": "c961bf297e544df14aba90c4e2a274cad3acec34309fd9c20158eff47c8b8c12",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersion.java": "f85801bdde00227d1db384c8f4be8e76a1fa632190f1f5b43e8e6a890bfa5f72",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersionSkillLink.java": "c7c41f41c8c05ed3714e5340c3effbbefc7eeb4138664ca35cf4bcfdad818ad1",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/StatType.java": "4c9b1f7bba977042504fe03133223e8d5c1f703b0c1567e49c8ed9b3893ef4ce",
          "backend/src/main/java/io/github/minokim/lumiawiki/common/api/ApiFailure.java": "d01ace83a4a170451b4cac7a4c7a4f8fd668dd2b669069bd8a4c39691a41243a",
          "backend/src/main/resources/application-local.yaml": "e161d9789956b24211bc886419f0d2791c634be0238e82678a3575fbeeb46144",
          "backend/src/main/resources/application.yaml": "d10d1ef05ddbec053c30bf2bc705e4c5f19a2b688baccd61a4f48af556bb40e0",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/CommonCatalogIntegrationTests.java": "7039b8f1dd95b6a74872f2961125def89a13b2332206f81c76d2fd8e9796031e",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemCatalogServiceTests.java": "dd8edc56f7f891a0776d48fe8626cfd0a307d5a7e8d85f178cd5543a8b7a24ba",
          "backend/src/test/resources/application-test.yaml": "e6aa7eb8da29c749b63e7330c634631d82f8710dc4fb6dee5ef883df1ce12e72",
          "db/bootstrap/10-prepare-roles.sh": "832e9921588251e3a658fadc276ff7d3b46a46b110c45ae7a16cd4eb7819914a",
          "db/bootstrap/sql/prepare-roles.sql": "160a624d9577848f6e61404ad3e52791c6a395af56186fec08e852f3f88ff8d4",
          "db/migration/V1__create_common_model.sql": "1495d8a5085188f535865f9b46f51aa1c9a18480c1b49efd68df61c43f5b8ddd",
          "db/migration/V2__create_item_storage.sql": "69c407f9191555c5c0ceeed62296f44fda9874776b311e75698d2e3cc01940d6",
          "frontend/package-lock.json": "e54e76e4ab1a402d4df0827152d1bf5c62142cd59e2798518b7ed2715931fc97",
          "frontend/package.json": "aae2e6358d704e1807f860f58272e3f8024cfdc092860bd0b0b4f7d58e76a228",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "2e55a2050f22641deaad0ac4b9b6723ad76aadab22ab037b9d38b1697a458367",
          "frontend/vitest.config.mjs": "f07e4974ad24bc562f5a975e8af587eb6fdfb402863825c718cfdf9a8b684eec",
          "package-lock.json": "539f24e43b65266883d2aa1a83428d75484cf059eeedcedf4043d09dc6d8a5e3",
          "package.json": "0e57b51524c8151aafb0155a93c5f61c30901819bde6cee895c0106f6dfcab85",
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": true
      }
    },
    {
      "id": "followup-item-storage-v3",
      "kind": "behavior",
      "spec": "d30c5f9c09c538ac2257fb1f8739ece729ee2665272dec987f246a5fbab6fa8e",
      "worktree": "49877d18df02111ef90a",
      "baseline": "94f53cfa0f59a859bcbc98714d62ac17852ca6bf",
      "task": "work/records/phase-001/issue-43/artifacts/task-002-execution.md",
      "finished": true,
      "red": {
        "runId": "7c6ef485a63241199e241644777b0f1e",
        "started": 1795249292.4736767,
        "finishedAt": 1795249318.21225,
        "command": [
          "backend/gradlew.bat",
          "-p",
          "backend",
          "-PtddReportDir={report}",
          "test",
          "--offline"
        ],
        "exitCode": 1,
        "result": {
          "tests": 41,
          "failures": 6,
          "errors": 0,
          "skipped": 0,
          "names": [
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapDuplicatesAreRejectedBeforeReplacement()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchBoundaryZeroAndNinetyNineAreAccepted()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapQueryDistinguishesUnknownFromConfirmedEmpty()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.knownBusinessConstraintsUseExistingInputError()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.seasonKeepsUnknownMetadataAndComputesWideOrder()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchBoundsAreRejectedBeforeWriting()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchUsesSeasonOrderAndTruncatesSubseconds()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.workingRegionRenameDoesNotChangeMapHistory()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.dependentFailureRollsBackTheSpringTransactionBoundary()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.unexpectedPkGuardRemainsAnInternalFailure()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.categoryCycleIsRejectedUnderTheTreeLock()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.badNamesAndReversedDatesAreRejected()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.dependentReferenceFailureIsPropagated()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.missingMapRegionsAreRejected()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapQueryReturnsPublicNamesOnly()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.writeTransactionUsesReadCommitted()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.missingQueryPatchHasNoMapResult()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.nullMapAndConfirmedEmptyMapRemainDifferent()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.mapSelectionAndMembersUseOneQueryWithoutReaderLocks()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.writersAcquireBasisLocksInTheAgreedOrder()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.rowProjectionPreservesLargeIdsAndPublicNames()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rejectsMissingAndBlankSkillDescriptionsWithTheAgreedContext()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.separatesMismatchedOwnersDuplicateLinksAndFutureVersions()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.distinguishesStackSizePreservingSettingAndClearing()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rebuildingOrderLocksAffectedVersionsAndKeepsTheOriginalValues()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.preservesExactDecimalsAndBigIdsInTheSortedCacheView()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.checksRequiredItemAndStatTypeNamesBeforeWriting()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.packagesTheItemMigrationAtTheProductFlywayLocation()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rejectsDuplicatesAndUnknownStatTypesBeforeReplacingTheOriginals()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.readsLegacyDetailsWithUnknownGradeAndRequiresGradeForNewCompleteInput()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.keepsTheSelectedSkillVersionAndOriginalAndTemporaryDescriptionsDistinct()",
            "io.github.minokim.lumiawiki.catalog.ItemStorageMigrationTests.packagesTheFollowupMigrationAtTheProductFlywayLocation()",
            "io.github.minokim.lumiawiki.FoundationApiTests.internalFailureRedactsResponsesAndLogs()",
            "io.github.minokim.lumiawiki.FoundationApiTests.unsupportedMethodKeeps405()",
            "io.github.minokim.lumiawiki.FoundationApiTests.normalAndEmptyResponsesHaveServerOwnedRequestIds()",
            "io.github.minokim.lumiawiki.FoundationApiTests.slowResponseUsesOneSecondDelay()",
            "io.github.minokim.lumiawiki.FoundationApiTests.badInputAndMissingUseProblemDetail()",
            "io.github.minokim.lumiawiki.FoundationApiTests.mvcValidationAndParsingRemain400()",
            "io.github.minokim.lumiawiki.FoundationApiTests.profileGatesDevEndpoint()",
            "io.github.minokim.lumiawiki.TestEnvironmentTests.junitMockitoAndMockMvcRunWithoutDocker()",
            "io.github.minokim.lumiawiki.TestEnvironmentTests.beanValidationRejectsInputBeforeCallingTheCollaborator()"
          ],
          "failedNames": [
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.distinguishesStackSizePreservingSettingAndClearing()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rebuildingOrderLocksAffectedVersionsAndKeepsTheOriginalValues()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.preservesExactDecimalsAndBigIdsInTheSortedCacheView()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rejectsDuplicatesAndUnknownStatTypesBeforeReplacingTheOriginals()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.readsLegacyDetailsWithUnknownGradeAndRequiresGradeForNewCompleteInput()",
            "io.github.minokim.lumiawiki.catalog.ItemStorageMigrationTests.packagesTheFollowupMigrationAtTheProductFlywayLocation()"
          ]
        },
        "manifest": {
          ".codex/hooks.json": "afb95b34e8d441cbd42a7535736128ce520e2ab9c016211d1739a0b40ff4e900",
          ".gitattributes": "4437511f6b3b866745490f0fcd2332d1e6194980fc028232ce0a84cec608d85b",
          "backend/build.gradle": "52b40fbbcdbb75b4ee5d5997811157a0ed61562cbd87c9eb6c3d859a88dd7960",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogErrors.java": "537109cdfc37381686d9cee6d470c9981504532be9d4313213179dd26f85486e",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CommonCatalogStore.java": "c55377ac784e38abca53bee65f146a3be8d38140fd96d8e1041c88e952c2889d",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/EquipmentSlot.java": "3692de42555019909fa7a34a296c47da5aa7ce14dcf2614b4846e0d34a76cc2e",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemCatalogService.java": "b1808ed25eb0f44d4764d52fbcb7b8712fabb3998e477eafe1ee9bb7debf6366",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemStat.java": "e2baeb9d858eccbbb6704b99b6c18ec4a4df0846a954f40bfe2ba4bb2b81ed64",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemStatCache.java": "903c7cf66969111f1174d4580c6f3e42090cb7918fc42a920a839ac0d7bf97b9",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersion.java": "953b08cf4d20a78ac2169e84555a8037fa01823864e1b8304248c9940a21aa76",
          "backend/src/main/resources/application-local.yaml": "e161d9789956b24211bc886419f0d2791c634be0238e82678a3575fbeeb46144",
          "backend/src/main/resources/application.yaml": "d10d1ef05ddbec053c30bf2bc705e4c5f19a2b688baccd61a4f48af556bb40e0",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/CommonCatalogIntegrationTests.java": "a5f28730d07e5b28ff855086e79292ab1a2206c01812ed5dfa3f9c2cf4f2c309",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemCatalogServiceTests.java": "49c82cb985373040a065e8567e4d60695ec48d5e8f1dd7cb90d6556f55232fdd",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemStorageMigrationTests.java": "ec2c92db072cf981c6f81cbefdab5e9f328b36e2d59d7bf59ef0060a4ee27028",
          "backend/src/test/resources/application-test.yaml": "e6aa7eb8da29c749b63e7330c634631d82f8710dc4fb6dee5ef883df1ce12e72",
          "db/bootstrap/10-prepare-roles.sh": "832e9921588251e3a658fadc276ff7d3b46a46b110c45ae7a16cd4eb7819914a",
          "db/bootstrap/sql/prepare-roles.sql": "160a624d9577848f6e61404ad3e52791c6a395af56186fec08e852f3f88ff8d4",
          "db/migration/V1__create_common_model.sql": "1495d8a5085188f535865f9b46f51aa1c9a18480c1b49efd68df61c43f5b8ddd",
          "db/migration/V2__create_item_storage.sql": "69c407f9191555c5c0ceeed62296f44fda9874776b311e75698d2e3cc01940d6",
          "db/migration/V3__complete_item_storage.sql": null,
          "frontend/package-lock.json": "e54e76e4ab1a402d4df0827152d1bf5c62142cd59e2798518b7ed2715931fc97",
          "frontend/package.json": "aae2e6358d704e1807f860f58272e3f8024cfdc092860bd0b0b4f7d58e76a228",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "2e55a2050f22641deaad0ac4b9b6723ad76aadab22ab037b9d38b1697a458367",
          "frontend/vitest.config.mjs": "f07e4974ad24bc562f5a975e8af587eb6fdfb402863825c718cfdf9a8b684eec",
          "package-lock.json": "539f24e43b65266883d2aa1a83428d75484cf059eeedcedf4043d09dc6d8a5e3",
          "package.json": "0e57b51524c8151aafb0155a93c5f61c30901819bde6cee895c0106f6dfcab85",
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": false
      },
      "final": {
        "runId": "9ccf704380d34463b6c9d88d3b8f359e",
        "started": 1795249319.0735228,
        "finishedAt": 1795249332.5298145,
        "command": [
          "backend/gradlew.bat",
          "-p",
          "backend",
          "-PtddReportDir={report}",
          "test",
          "--offline"
        ],
        "exitCode": 0,
        "result": {
          "tests": 41,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "names": [
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapDuplicatesAreRejectedBeforeReplacement()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchBoundaryZeroAndNinetyNineAreAccepted()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapQueryDistinguishesUnknownFromConfirmedEmpty()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.knownBusinessConstraintsUseExistingInputError()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.seasonKeepsUnknownMetadataAndComputesWideOrder()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchBoundsAreRejectedBeforeWriting()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchUsesSeasonOrderAndTruncatesSubseconds()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.workingRegionRenameDoesNotChangeMapHistory()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.dependentFailureRollsBackTheSpringTransactionBoundary()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.unexpectedPkGuardRemainsAnInternalFailure()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.categoryCycleIsRejectedUnderTheTreeLock()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.badNamesAndReversedDatesAreRejected()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.dependentReferenceFailureIsPropagated()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.missingMapRegionsAreRejected()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapQueryReturnsPublicNamesOnly()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.writeTransactionUsesReadCommitted()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.missingQueryPatchHasNoMapResult()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.nullMapAndConfirmedEmptyMapRemainDifferent()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.mapSelectionAndMembersUseOneQueryWithoutReaderLocks()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.writersAcquireBasisLocksInTheAgreedOrder()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.rowProjectionPreservesLargeIdsAndPublicNames()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rejectsMissingAndBlankSkillDescriptionsWithTheAgreedContext()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.separatesMismatchedOwnersDuplicateLinksAndFutureVersions()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.distinguishesStackSizePreservingSettingAndClearing()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rebuildingOrderLocksAffectedVersionsAndKeepsTheOriginalValues()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.preservesExactDecimalsAndBigIdsInTheSortedCacheView()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.checksRequiredItemAndStatTypeNamesBeforeWriting()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.packagesTheItemMigrationAtTheProductFlywayLocation()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rejectsDuplicatesAndUnknownStatTypesBeforeReplacingTheOriginals()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.readsLegacyDetailsWithUnknownGradeAndRequiresGradeForNewCompleteInput()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.keepsTheSelectedSkillVersionAndOriginalAndTemporaryDescriptionsDistinct()",
            "io.github.minokim.lumiawiki.catalog.ItemStorageMigrationTests.packagesTheFollowupMigrationAtTheProductFlywayLocation()",
            "io.github.minokim.lumiawiki.FoundationApiTests.internalFailureRedactsResponsesAndLogs()",
            "io.github.minokim.lumiawiki.FoundationApiTests.unsupportedMethodKeeps405()",
            "io.github.minokim.lumiawiki.FoundationApiTests.normalAndEmptyResponsesHaveServerOwnedRequestIds()",
            "io.github.minokim.lumiawiki.FoundationApiTests.slowResponseUsesOneSecondDelay()",
            "io.github.minokim.lumiawiki.FoundationApiTests.badInputAndMissingUseProblemDetail()",
            "io.github.minokim.lumiawiki.FoundationApiTests.mvcValidationAndParsingRemain400()",
            "io.github.minokim.lumiawiki.FoundationApiTests.profileGatesDevEndpoint()",
            "io.github.minokim.lumiawiki.TestEnvironmentTests.junitMockitoAndMockMvcRunWithoutDocker()",
            "io.github.minokim.lumiawiki.TestEnvironmentTests.beanValidationRejectsInputBeforeCallingTheCollaborator()"
          ],
          "failedNames": []
        },
        "manifest": {
          ".codex/hooks.json": "afb95b34e8d441cbd42a7535736128ce520e2ab9c016211d1739a0b40ff4e900",
          ".gitattributes": "4437511f6b3b866745490f0fcd2332d1e6194980fc028232ce0a84cec608d85b",
          "backend/build.gradle": "52b40fbbcdbb75b4ee5d5997811157a0ed61562cbd87c9eb6c3d859a88dd7960",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogErrors.java": "537109cdfc37381686d9cee6d470c9981504532be9d4313213179dd26f85486e",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CommonCatalogStore.java": "c55377ac784e38abca53bee65f146a3be8d38140fd96d8e1041c88e952c2889d",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/EquipmentSlot.java": "3692de42555019909fa7a34a296c47da5aa7ce14dcf2614b4846e0d34a76cc2e",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemCatalogService.java": "3a5c2d31aaf4a572825021fa1761c8868decb17207e22f39684e5d7d70e8dc38",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemStat.java": "e2baeb9d858eccbbb6704b99b6c18ec4a4df0846a954f40bfe2ba4bb2b81ed64",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemStatCache.java": "903c7cf66969111f1174d4580c6f3e42090cb7918fc42a920a839ac0d7bf97b9",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersion.java": "953b08cf4d20a78ac2169e84555a8037fa01823864e1b8304248c9940a21aa76",
          "backend/src/main/resources/application-local.yaml": "e161d9789956b24211bc886419f0d2791c634be0238e82678a3575fbeeb46144",
          "backend/src/main/resources/application.yaml": "d10d1ef05ddbec053c30bf2bc705e4c5f19a2b688baccd61a4f48af556bb40e0",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/CommonCatalogIntegrationTests.java": "a5f28730d07e5b28ff855086e79292ab1a2206c01812ed5dfa3f9c2cf4f2c309",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemCatalogServiceTests.java": "49c82cb985373040a065e8567e4d60695ec48d5e8f1dd7cb90d6556f55232fdd",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemStorageMigrationTests.java": "ec2c92db072cf981c6f81cbefdab5e9f328b36e2d59d7bf59ef0060a4ee27028",
          "backend/src/test/resources/application-test.yaml": "e6aa7eb8da29c749b63e7330c634631d82f8710dc4fb6dee5ef883df1ce12e72",
          "db/bootstrap/10-prepare-roles.sh": "832e9921588251e3a658fadc276ff7d3b46a46b110c45ae7a16cd4eb7819914a",
          "db/bootstrap/sql/prepare-roles.sql": "160a624d9577848f6e61404ad3e52791c6a395af56186fec08e852f3f88ff8d4",
          "db/migration/V1__create_common_model.sql": "1495d8a5085188f535865f9b46f51aa1c9a18480c1b49efd68df61c43f5b8ddd",
          "db/migration/V2__create_item_storage.sql": "69c407f9191555c5c0ceeed62296f44fda9874776b311e75698d2e3cc01940d6",
          "db/migration/V3__complete_item_storage.sql": "610622a531770994696ee295da6bc360e2a27ae48358acd08dc354fb1867a6bd",
          "frontend/package-lock.json": "e54e76e4ab1a402d4df0827152d1bf5c62142cd59e2798518b7ed2715931fc97",
          "frontend/package.json": "aae2e6358d704e1807f860f58272e3f8024cfdc092860bd0b0b4f7d58e76a228",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "2e55a2050f22641deaad0ac4b9b6723ad76aadab22ab037b9d38b1697a458367",
          "frontend/vitest.config.mjs": "f07e4974ad24bc562f5a975e8af587eb6fdfb402863825c718cfdf9a8b684eec",
          "package-lock.json": "539f24e43b65266883d2aa1a83428d75484cf059eeedcedf4043d09dc6d8a5e3",
          "package.json": "0e57b51524c8151aafb0155a93c5f61c30901819bde6cee895c0106f6dfcab85",
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": true
      }
    },
    {
      "id": "legacy-existence-v3-verified",
      "kind": "behavior",
      "spec": "b05267c80669e225f111956212768e4ae44d83c3d53dc7da966e9f0245f6a127",
      "worktree": "49877d18df02111ef90a",
      "baseline": "94f53cfa0f59a859bcbc98714d62ac17852ca6bf",
      "task": "work/records/phase-001/issue-43/artifacts/task-002-execution.md",
      "finished": true,
      "red": {
        "runId": "54e422a54696480f9972b02eed73c72a",
        "started": 1795250701.0369153,
        "finishedAt": 1795250714.9592147,
        "command": [
          "backend/gradlew.bat",
          "-p",
          "backend",
          "-PtddReportDir={report}",
          "test",
          "--offline"
        ],
        "exitCode": 1,
        "result": {
          "tests": 42,
          "failures": 1,
          "errors": 0,
          "skipped": 0,
          "names": [
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapDuplicatesAreRejectedBeforeReplacement()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchBoundaryZeroAndNinetyNineAreAccepted()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapQueryDistinguishesUnknownFromConfirmedEmpty()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.knownBusinessConstraintsUseExistingInputError()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.seasonKeepsUnknownMetadataAndComputesWideOrder()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchBoundsAreRejectedBeforeWriting()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchUsesSeasonOrderAndTruncatesSubseconds()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.workingRegionRenameDoesNotChangeMapHistory()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.dependentFailureRollsBackTheSpringTransactionBoundary()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.unexpectedPkGuardRemainsAnInternalFailure()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.categoryCycleIsRejectedUnderTheTreeLock()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.badNamesAndReversedDatesAreRejected()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.dependentReferenceFailureIsPropagated()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.missingMapRegionsAreRejected()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapQueryReturnsPublicNamesOnly()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.writeTransactionUsesReadCommitted()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.missingQueryPatchHasNoMapResult()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.nullMapAndConfirmedEmptyMapRemainDifferent()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.mapSelectionAndMembersUseOneQueryWithoutReaderLocks()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.writersAcquireBasisLocksInTheAgreedOrder()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.rowProjectionPreservesLargeIdsAndPublicNames()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.preservesUnknownLegacyGradeWhenOnlyExistenceChanges()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rejectsMissingAndBlankSkillDescriptionsWithTheAgreedContext()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.separatesMismatchedOwnersDuplicateLinksAndFutureVersions()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.distinguishesStackSizePreservingSettingAndClearing()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rebuildingOrderLocksAffectedVersionsAndKeepsTheOriginalValues()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.preservesExactDecimalsAndBigIdsInTheSortedCacheView()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.checksRequiredItemAndStatTypeNamesBeforeWriting()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.packagesTheItemMigrationAtTheProductFlywayLocation()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rejectsDuplicatesAndUnknownStatTypesBeforeReplacingTheOriginals()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.readsLegacyDetailsWithUnknownGradeAndRequiresGradeForNewCompleteInput()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.keepsTheSelectedSkillVersionAndOriginalAndTemporaryDescriptionsDistinct()",
            "io.github.minokim.lumiawiki.catalog.ItemStorageMigrationTests.packagesTheFollowupMigrationAtTheProductFlywayLocation()",
            "io.github.minokim.lumiawiki.FoundationApiTests.internalFailureRedactsResponsesAndLogs()",
            "io.github.minokim.lumiawiki.FoundationApiTests.unsupportedMethodKeeps405()",
            "io.github.minokim.lumiawiki.FoundationApiTests.normalAndEmptyResponsesHaveServerOwnedRequestIds()",
            "io.github.minokim.lumiawiki.FoundationApiTests.slowResponseUsesOneSecondDelay()",
            "io.github.minokim.lumiawiki.FoundationApiTests.badInputAndMissingUseProblemDetail()",
            "io.github.minokim.lumiawiki.FoundationApiTests.mvcValidationAndParsingRemain400()",
            "io.github.minokim.lumiawiki.FoundationApiTests.profileGatesDevEndpoint()",
            "io.github.minokim.lumiawiki.TestEnvironmentTests.junitMockitoAndMockMvcRunWithoutDocker()",
            "io.github.minokim.lumiawiki.TestEnvironmentTests.beanValidationRejectsInputBeforeCallingTheCollaborator()"
          ],
          "failedNames": [
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.preservesUnknownLegacyGradeWhenOnlyExistenceChanges()"
          ]
        },
        "manifest": {
          ".codex/hooks.json": "afb95b34e8d441cbd42a7535736128ce520e2ab9c016211d1739a0b40ff4e900",
          ".gitattributes": "4437511f6b3b866745490f0fcd2332d1e6194980fc028232ce0a84cec608d85b",
          "backend/build.gradle": "52b40fbbcdbb75b4ee5d5997811157a0ed61562cbd87c9eb6c3d859a88dd7960",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogErrors.java": "537109cdfc37381686d9cee6d470c9981504532be9d4313213179dd26f85486e",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CommonCatalogStore.java": "c55377ac784e38abca53bee65f146a3be8d38140fd96d8e1041c88e952c2889d",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/EquipmentSlot.java": "3692de42555019909fa7a34a296c47da5aa7ce14dcf2614b4846e0d34a76cc2e",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemCatalogService.java": "3a5c2d31aaf4a572825021fa1761c8868decb17207e22f39684e5d7d70e8dc38",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemStat.java": "e2baeb9d858eccbbb6704b99b6c18ec4a4df0846a954f40bfe2ba4bb2b81ed64",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemStatCache.java": "903c7cf66969111f1174d4580c6f3e42090cb7918fc42a920a839ac0d7bf97b9",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersion.java": "953b08cf4d20a78ac2169e84555a8037fa01823864e1b8304248c9940a21aa76",
          "backend/src/main/resources/application-local.yaml": "e161d9789956b24211bc886419f0d2791c634be0238e82678a3575fbeeb46144",
          "backend/src/main/resources/application.yaml": "d10d1ef05ddbec053c30bf2bc705e4c5f19a2b688baccd61a4f48af556bb40e0",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/CommonCatalogIntegrationTests.java": "d077d94d547fd8ac592c13053df8faa475a21ed9165fed1e777f557385d69633",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemCatalogServiceTests.java": "6a169be5655dd5331b0dc7138ef80e2eca1e5bac37a522d23f3f7638ac78481c",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemStorageMigrationTests.java": "ec2c92db072cf981c6f81cbefdab5e9f328b36e2d59d7bf59ef0060a4ee27028",
          "backend/src/test/resources/application-test.yaml": "e6aa7eb8da29c749b63e7330c634631d82f8710dc4fb6dee5ef883df1ce12e72",
          "db/bootstrap/10-prepare-roles.sh": "832e9921588251e3a658fadc276ff7d3b46a46b110c45ae7a16cd4eb7819914a",
          "db/bootstrap/sql/prepare-roles.sql": "160a624d9577848f6e61404ad3e52791c6a395af56186fec08e852f3f88ff8d4",
          "db/migration/V1__create_common_model.sql": "1495d8a5085188f535865f9b46f51aa1c9a18480c1b49efd68df61c43f5b8ddd",
          "db/migration/V2__create_item_storage.sql": "69c407f9191555c5c0ceeed62296f44fda9874776b311e75698d2e3cc01940d6",
          "db/migration/V3__complete_item_storage.sql": "610622a531770994696ee295da6bc360e2a27ae48358acd08dc354fb1867a6bd",
          "frontend/package-lock.json": "e54e76e4ab1a402d4df0827152d1bf5c62142cd59e2798518b7ed2715931fc97",
          "frontend/package.json": "aae2e6358d704e1807f860f58272e3f8024cfdc092860bd0b0b4f7d58e76a228",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "2e55a2050f22641deaad0ac4b9b6723ad76aadab22ab037b9d38b1697a458367",
          "frontend/vitest.config.mjs": "f07e4974ad24bc562f5a975e8af587eb6fdfb402863825c718cfdf9a8b684eec",
          "package-lock.json": "539f24e43b65266883d2aa1a83428d75484cf059eeedcedf4043d09dc6d8a5e3",
          "package.json": "0e57b51524c8151aafb0155a93c5f61c30901819bde6cee895c0106f6dfcab85",
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": false
      },
      "final": {
        "runId": "29d9a605d21e4a298cc2063cfceb19b3",
        "started": 1795250715.5319042,
        "finishedAt": 1795250726.5997987,
        "command": [
          "backend/gradlew.bat",
          "-p",
          "backend",
          "-PtddReportDir={report}",
          "test",
          "--offline"
        ],
        "exitCode": 0,
        "result": {
          "tests": 42,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "names": [
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapDuplicatesAreRejectedBeforeReplacement()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchBoundaryZeroAndNinetyNineAreAccepted()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapQueryDistinguishesUnknownFromConfirmedEmpty()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.knownBusinessConstraintsUseExistingInputError()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.seasonKeepsUnknownMetadataAndComputesWideOrder()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchBoundsAreRejectedBeforeWriting()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchUsesSeasonOrderAndTruncatesSubseconds()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.workingRegionRenameDoesNotChangeMapHistory()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.dependentFailureRollsBackTheSpringTransactionBoundary()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.unexpectedPkGuardRemainsAnInternalFailure()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.categoryCycleIsRejectedUnderTheTreeLock()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.badNamesAndReversedDatesAreRejected()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.dependentReferenceFailureIsPropagated()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.missingMapRegionsAreRejected()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapQueryReturnsPublicNamesOnly()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.writeTransactionUsesReadCommitted()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.missingQueryPatchHasNoMapResult()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.nullMapAndConfirmedEmptyMapRemainDifferent()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.mapSelectionAndMembersUseOneQueryWithoutReaderLocks()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.writersAcquireBasisLocksInTheAgreedOrder()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.rowProjectionPreservesLargeIdsAndPublicNames()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.preservesUnknownLegacyGradeWhenOnlyExistenceChanges()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rejectsMissingAndBlankSkillDescriptionsWithTheAgreedContext()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.separatesMismatchedOwnersDuplicateLinksAndFutureVersions()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.distinguishesStackSizePreservingSettingAndClearing()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rebuildingOrderLocksAffectedVersionsAndKeepsTheOriginalValues()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.preservesExactDecimalsAndBigIdsInTheSortedCacheView()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.checksRequiredItemAndStatTypeNamesBeforeWriting()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.packagesTheItemMigrationAtTheProductFlywayLocation()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rejectsDuplicatesAndUnknownStatTypesBeforeReplacingTheOriginals()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.readsLegacyDetailsWithUnknownGradeAndRequiresGradeForNewCompleteInput()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.keepsTheSelectedSkillVersionAndOriginalAndTemporaryDescriptionsDistinct()",
            "io.github.minokim.lumiawiki.catalog.ItemStorageMigrationTests.packagesTheFollowupMigrationAtTheProductFlywayLocation()",
            "io.github.minokim.lumiawiki.FoundationApiTests.internalFailureRedactsResponsesAndLogs()",
            "io.github.minokim.lumiawiki.FoundationApiTests.unsupportedMethodKeeps405()",
            "io.github.minokim.lumiawiki.FoundationApiTests.normalAndEmptyResponsesHaveServerOwnedRequestIds()",
            "io.github.minokim.lumiawiki.FoundationApiTests.slowResponseUsesOneSecondDelay()",
            "io.github.minokim.lumiawiki.FoundationApiTests.badInputAndMissingUseProblemDetail()",
            "io.github.minokim.lumiawiki.FoundationApiTests.mvcValidationAndParsingRemain400()",
            "io.github.minokim.lumiawiki.FoundationApiTests.profileGatesDevEndpoint()",
            "io.github.minokim.lumiawiki.TestEnvironmentTests.junitMockitoAndMockMvcRunWithoutDocker()",
            "io.github.minokim.lumiawiki.TestEnvironmentTests.beanValidationRejectsInputBeforeCallingTheCollaborator()"
          ],
          "failedNames": []
        },
        "manifest": {
          ".codex/hooks.json": "afb95b34e8d441cbd42a7535736128ce520e2ab9c016211d1739a0b40ff4e900",
          ".gitattributes": "4437511f6b3b866745490f0fcd2332d1e6194980fc028232ce0a84cec608d85b",
          "backend/build.gradle": "52b40fbbcdbb75b4ee5d5997811157a0ed61562cbd87c9eb6c3d859a88dd7960",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogErrors.java": "537109cdfc37381686d9cee6d470c9981504532be9d4313213179dd26f85486e",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CommonCatalogStore.java": "c55377ac784e38abca53bee65f146a3be8d38140fd96d8e1041c88e952c2889d",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/EquipmentSlot.java": "3692de42555019909fa7a34a296c47da5aa7ce14dcf2614b4846e0d34a76cc2e",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemCatalogService.java": "e69d7b8babe23f2322cdd910fb7a8e8fc54ea5006cc0999cd7159fbbd3916d74",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemStat.java": "e2baeb9d858eccbbb6704b99b6c18ec4a4df0846a954f40bfe2ba4bb2b81ed64",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemStatCache.java": "903c7cf66969111f1174d4580c6f3e42090cb7918fc42a920a839ac0d7bf97b9",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersion.java": "953b08cf4d20a78ac2169e84555a8037fa01823864e1b8304248c9940a21aa76",
          "backend/src/main/resources/application-local.yaml": "e161d9789956b24211bc886419f0d2791c634be0238e82678a3575fbeeb46144",
          "backend/src/main/resources/application.yaml": "d10d1ef05ddbec053c30bf2bc705e4c5f19a2b688baccd61a4f48af556bb40e0",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/CommonCatalogIntegrationTests.java": "d077d94d547fd8ac592c13053df8faa475a21ed9165fed1e777f557385d69633",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemCatalogServiceTests.java": "6a169be5655dd5331b0dc7138ef80e2eca1e5bac37a522d23f3f7638ac78481c",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemStorageMigrationTests.java": "ec2c92db072cf981c6f81cbefdab5e9f328b36e2d59d7bf59ef0060a4ee27028",
          "backend/src/test/resources/application-test.yaml": "e6aa7eb8da29c749b63e7330c634631d82f8710dc4fb6dee5ef883df1ce12e72",
          "db/bootstrap/10-prepare-roles.sh": "832e9921588251e3a658fadc276ff7d3b46a46b110c45ae7a16cd4eb7819914a",
          "db/bootstrap/sql/prepare-roles.sql": "160a624d9577848f6e61404ad3e52791c6a395af56186fec08e852f3f88ff8d4",
          "db/migration/V1__create_common_model.sql": "1495d8a5085188f535865f9b46f51aa1c9a18480c1b49efd68df61c43f5b8ddd",
          "db/migration/V2__create_item_storage.sql": "69c407f9191555c5c0ceeed62296f44fda9874776b311e75698d2e3cc01940d6",
          "db/migration/V3__complete_item_storage.sql": "610622a531770994696ee295da6bc360e2a27ae48358acd08dc354fb1867a6bd",
          "frontend/package-lock.json": "e54e76e4ab1a402d4df0827152d1bf5c62142cd59e2798518b7ed2715931fc97",
          "frontend/package.json": "aae2e6358d704e1807f860f58272e3f8024cfdc092860bd0b0b4f7d58e76a228",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "2e55a2050f22641deaad0ac4b9b6723ad76aadab22ab037b9d38b1697a458367",
          "frontend/vitest.config.mjs": "f07e4974ad24bc562f5a975e8af587eb6fdfb402863825c718cfdf9a8b684eec",
          "package-lock.json": "539f24e43b65266883d2aa1a83428d75484cf059eeedcedf4043d09dc6d8a5e3",
          "package.json": "0e57b51524c8151aafb0155a93c5f61c30901819bde6cee895c0106f6dfcab85",
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": true
      }
    },
    {
      "id": "v2-v3-pr-replay",
      "kind": "behavior",
      "spec": "4f5b19c164e9f9e466735db74c84717356883f53130fd47db7bf6e6c1f0e6f3d",
      "worktree": "9c5b61a0976cea826df5",
      "baseline": "76e26221ce8b334b462273660c9b4b7e79a81e01",
      "task": "work/records/phase-001/issue-43/artifacts/task-002-execution.md",
      "finished": true,
      "red": {
        "runId": "813ef309c1c0483d8d20f6c6ffc5f17a",
        "started": 1795257899.097055,
        "finishedAt": 1795257917.2466304,
        "command": [
          "backend/gradlew.bat",
          "-p",
          "backend",
          "-PtddReportDir={report}",
          "test",
          "--offline"
        ],
        "exitCode": 1,
        "result": {
          "tests": 42,
          "failures": 1,
          "errors": 0,
          "skipped": 0,
          "names": [
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapDuplicatesAreRejectedBeforeReplacement()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchBoundaryZeroAndNinetyNineAreAccepted()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapQueryDistinguishesUnknownFromConfirmedEmpty()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.knownBusinessConstraintsUseExistingInputError()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.seasonKeepsUnknownMetadataAndComputesWideOrder()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchBoundsAreRejectedBeforeWriting()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchUsesSeasonOrderAndTruncatesSubseconds()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.workingRegionRenameDoesNotChangeMapHistory()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.dependentFailureRollsBackTheSpringTransactionBoundary()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.unexpectedPkGuardRemainsAnInternalFailure()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.categoryCycleIsRejectedUnderTheTreeLock()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.badNamesAndReversedDatesAreRejected()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.dependentReferenceFailureIsPropagated()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.missingMapRegionsAreRejected()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapQueryReturnsPublicNamesOnly()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.writeTransactionUsesReadCommitted()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.missingQueryPatchHasNoMapResult()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.nullMapAndConfirmedEmptyMapRemainDifferent()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.mapSelectionAndMembersUseOneQueryWithoutReaderLocks()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.writersAcquireBasisLocksInTheAgreedOrder()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.rowProjectionPreservesLargeIdsAndPublicNames()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.preservesUnknownLegacyGradeWhenOnlyExistenceChanges()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rejectsMissingAndBlankSkillDescriptionsWithTheAgreedContext()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.separatesMismatchedOwnersDuplicateLinksAndFutureVersions()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.distinguishesStackSizePreservingSettingAndClearing()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rebuildingOrderLocksAffectedVersionsAndKeepsTheOriginalValues()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.preservesExactDecimalsAndBigIdsInTheSortedCacheView()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.checksRequiredItemAndStatTypeNamesBeforeWriting()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.packagesTheItemMigrationAtTheProductFlywayLocation()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rejectsDuplicatesAndUnknownStatTypesBeforeReplacingTheOriginals()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.readsLegacyDetailsWithUnknownGradeAndRequiresGradeForNewCompleteInput()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.keepsTheSelectedSkillVersionAndOriginalAndTemporaryDescriptionsDistinct()",
            "io.github.minokim.lumiawiki.catalog.ItemStorageMigrationTests.packagesTheFollowupMigrationAtTheProductFlywayLocation()",
            "io.github.minokim.lumiawiki.FoundationApiTests.internalFailureRedactsResponsesAndLogs()",
            "io.github.minokim.lumiawiki.FoundationApiTests.unsupportedMethodKeeps405()",
            "io.github.minokim.lumiawiki.FoundationApiTests.normalAndEmptyResponsesHaveServerOwnedRequestIds()",
            "io.github.minokim.lumiawiki.FoundationApiTests.slowResponseUsesOneSecondDelay()",
            "io.github.minokim.lumiawiki.FoundationApiTests.badInputAndMissingUseProblemDetail()",
            "io.github.minokim.lumiawiki.FoundationApiTests.mvcValidationAndParsingRemain400()",
            "io.github.minokim.lumiawiki.FoundationApiTests.profileGatesDevEndpoint()",
            "io.github.minokim.lumiawiki.TestEnvironmentTests.junitMockitoAndMockMvcRunWithoutDocker()",
            "io.github.minokim.lumiawiki.TestEnvironmentTests.beanValidationRejectsInputBeforeCallingTheCollaborator()"
          ],
          "failedNames": [
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.packagesTheItemMigrationAtTheProductFlywayLocation()"
          ]
        },
        "manifest": {
          ".codex/hooks.json": "816cb983d2faded1df2b58fc7da4b371c5990800df09768b324a8674448e31d4",
          ".gitattributes": "4437511f6b3b866745490f0fcd2332d1e6194980fc028232ce0a84cec608d85b",
          "backend/build.gradle": "52b40fbbcdbb75b4ee5d5997811157a0ed61562cbd87c9eb6c3d859a88dd7960",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogErrors.java": "537109cdfc37381686d9cee6d470c9981504532be9d4313213179dd26f85486e",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogReferenceCheck.java": "1fb4aea7e2d2af5d50d81f813e657b90acf136a8dcacc1fc19ac7adf9dbd7ffd",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CommonCatalogStore.java": "c55377ac784e38abca53bee65f146a3be8d38140fd96d8e1041c88e952c2889d",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/EquipmentSlot.java": "3692de42555019909fa7a34a296c47da5aa7ce14dcf2614b4846e0d34a76cc2e",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/Item.java": "58a6bda3b7d01969a9e6958c7063f16f61467989a6faac4392d999a8b4de461f",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemCatalogService.java": "e69d7b8babe23f2322cdd910fb7a8e8fc54ea5006cc0999cd7159fbbd3916d74",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemSkillDefinition.java": "1e26d5216f230379aeff168536eefcadb9e5d4947d26c678d17c0bb0fde3d747",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemSkillDefinitionVersion.java": "4040ace621d202a2937d1f1244e2b89a69434f5bdabc73aa78f9a7ebdae3e448",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemSkillReferenceCheck.java": "c961bf297e544df14aba90c4e2a274cad3acec34309fd9c20158eff47c8b8c12",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemStat.java": "e2baeb9d858eccbbb6704b99b6c18ec4a4df0846a954f40bfe2ba4bb2b81ed64",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemStatCache.java": "903c7cf66969111f1174d4580c6f3e42090cb7918fc42a920a839ac0d7bf97b9",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersion.java": "953b08cf4d20a78ac2169e84555a8037fa01823864e1b8304248c9940a21aa76",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersionSkillLink.java": "c7c41f41c8c05ed3714e5340c3effbbefc7eeb4138664ca35cf4bcfdad818ad1",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/StatType.java": "4c9b1f7bba977042504fe03133223e8d5c1f703b0c1567e49c8ed9b3893ef4ce",
          "backend/src/main/java/io/github/minokim/lumiawiki/common/api/ApiFailure.java": "d01ace83a4a170451b4cac7a4c7a4f8fd668dd2b669069bd8a4c39691a41243a",
          "backend/src/main/resources/application-local.yaml": "e161d9789956b24211bc886419f0d2791c634be0238e82678a3575fbeeb46144",
          "backend/src/main/resources/application.yaml": "d10d1ef05ddbec053c30bf2bc705e4c5f19a2b688baccd61a4f48af556bb40e0",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/CommonCatalogIntegrationTests.java": "d077d94d547fd8ac592c13053df8faa475a21ed9165fed1e777f557385d69633",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemCatalogServiceTests.java": "6a169be5655dd5331b0dc7138ef80e2eca1e5bac37a522d23f3f7638ac78481c",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemStorageMigrationTests.java": "ec2c92db072cf981c6f81cbefdab5e9f328b36e2d59d7bf59ef0060a4ee27028",
          "backend/src/test/resources/application-test.yaml": "e6aa7eb8da29c749b63e7330c634631d82f8710dc4fb6dee5ef883df1ce12e72",
          "db/bootstrap/10-prepare-roles.sh": "832e9921588251e3a658fadc276ff7d3b46a46b110c45ae7a16cd4eb7819914a",
          "db/bootstrap/sql/prepare-roles.sql": "160a624d9577848f6e61404ad3e52791c6a395af56186fec08e852f3f88ff8d4",
          "db/migration/V1__create_common_model.sql": "1495d8a5085188f535865f9b46f51aa1c9a18480c1b49efd68df61c43f5b8ddd",
          "db/migration/V2__create_item_storage.sql": null,
          "db/migration/V3__complete_item_storage.sql": "610622a531770994696ee295da6bc360e2a27ae48358acd08dc354fb1867a6bd",
          "frontend/package-lock.json": "e54e76e4ab1a402d4df0827152d1bf5c62142cd59e2798518b7ed2715931fc97",
          "frontend/package.json": "aae2e6358d704e1807f860f58272e3f8024cfdc092860bd0b0b4f7d58e76a228",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "2e55a2050f22641deaad0ac4b9b6723ad76aadab22ab037b9d38b1697a458367",
          "frontend/vitest.config.mjs": "f07e4974ad24bc562f5a975e8af587eb6fdfb402863825c718cfdf9a8b684eec",
          "package-lock.json": "539f24e43b65266883d2aa1a83428d75484cf059eeedcedf4043d09dc6d8a5e3",
          "package.json": "0e57b51524c8151aafb0155a93c5f61c30901819bde6cee895c0106f6dfcab85",
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": false
      },
      "final": {
        "runId": "fcb2d327d0fa4573bf8f383d7b1402d2",
        "started": 1795257917.894904,
        "finishedAt": 1795257927.5326977,
        "command": [
          "backend/gradlew.bat",
          "-p",
          "backend",
          "-PtddReportDir={report}",
          "test",
          "--offline"
        ],
        "exitCode": 0,
        "result": {
          "tests": 42,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "names": [
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapDuplicatesAreRejectedBeforeReplacement()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchBoundaryZeroAndNinetyNineAreAccepted()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapQueryDistinguishesUnknownFromConfirmedEmpty()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.knownBusinessConstraintsUseExistingInputError()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.seasonKeepsUnknownMetadataAndComputesWideOrder()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchBoundsAreRejectedBeforeWriting()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.patchUsesSeasonOrderAndTruncatesSubseconds()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.workingRegionRenameDoesNotChangeMapHistory()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.dependentFailureRollsBackTheSpringTransactionBoundary()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.unexpectedPkGuardRemainsAnInternalFailure()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.categoryCycleIsRejectedUnderTheTreeLock()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.badNamesAndReversedDatesAreRejected()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.dependentReferenceFailureIsPropagated()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.missingMapRegionsAreRejected()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.mapQueryReturnsPublicNamesOnly()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogServiceTests.writeTransactionUsesReadCommitted()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.missingQueryPatchHasNoMapResult()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.nullMapAndConfirmedEmptyMapRemainDifferent()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.mapSelectionAndMembersUseOneQueryWithoutReaderLocks()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.writersAcquireBasisLocksInTheAgreedOrder()",
            "io.github.minokim.lumiawiki.catalog.CommonCatalogStoreTests.rowProjectionPreservesLargeIdsAndPublicNames()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.preservesUnknownLegacyGradeWhenOnlyExistenceChanges()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rejectsMissingAndBlankSkillDescriptionsWithTheAgreedContext()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.separatesMismatchedOwnersDuplicateLinksAndFutureVersions()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.distinguishesStackSizePreservingSettingAndClearing()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rebuildingOrderLocksAffectedVersionsAndKeepsTheOriginalValues()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.preservesExactDecimalsAndBigIdsInTheSortedCacheView()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.checksRequiredItemAndStatTypeNamesBeforeWriting()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.packagesTheItemMigrationAtTheProductFlywayLocation()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.rejectsDuplicatesAndUnknownStatTypesBeforeReplacingTheOriginals()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.readsLegacyDetailsWithUnknownGradeAndRequiresGradeForNewCompleteInput()",
            "io.github.minokim.lumiawiki.catalog.ItemCatalogServiceTests.keepsTheSelectedSkillVersionAndOriginalAndTemporaryDescriptionsDistinct()",
            "io.github.minokim.lumiawiki.catalog.ItemStorageMigrationTests.packagesTheFollowupMigrationAtTheProductFlywayLocation()",
            "io.github.minokim.lumiawiki.FoundationApiTests.internalFailureRedactsResponsesAndLogs()",
            "io.github.minokim.lumiawiki.FoundationApiTests.unsupportedMethodKeeps405()",
            "io.github.minokim.lumiawiki.FoundationApiTests.normalAndEmptyResponsesHaveServerOwnedRequestIds()",
            "io.github.minokim.lumiawiki.FoundationApiTests.slowResponseUsesOneSecondDelay()",
            "io.github.minokim.lumiawiki.FoundationApiTests.badInputAndMissingUseProblemDetail()",
            "io.github.minokim.lumiawiki.FoundationApiTests.mvcValidationAndParsingRemain400()",
            "io.github.minokim.lumiawiki.FoundationApiTests.profileGatesDevEndpoint()",
            "io.github.minokim.lumiawiki.TestEnvironmentTests.junitMockitoAndMockMvcRunWithoutDocker()",
            "io.github.minokim.lumiawiki.TestEnvironmentTests.beanValidationRejectsInputBeforeCallingTheCollaborator()"
          ],
          "failedNames": []
        },
        "manifest": {
          ".codex/hooks.json": "816cb983d2faded1df2b58fc7da4b371c5990800df09768b324a8674448e31d4",
          ".gitattributes": "4437511f6b3b866745490f0fcd2332d1e6194980fc028232ce0a84cec608d85b",
          "backend/build.gradle": "52b40fbbcdbb75b4ee5d5997811157a0ed61562cbd87c9eb6c3d859a88dd7960",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogErrors.java": "537109cdfc37381686d9cee6d470c9981504532be9d4313213179dd26f85486e",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogReferenceCheck.java": "1fb4aea7e2d2af5d50d81f813e657b90acf136a8dcacc1fc19ac7adf9dbd7ffd",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CommonCatalogStore.java": "c55377ac784e38abca53bee65f146a3be8d38140fd96d8e1041c88e952c2889d",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/EquipmentSlot.java": "3692de42555019909fa7a34a296c47da5aa7ce14dcf2614b4846e0d34a76cc2e",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/Item.java": "58a6bda3b7d01969a9e6958c7063f16f61467989a6faac4392d999a8b4de461f",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemCatalogService.java": "e69d7b8babe23f2322cdd910fb7a8e8fc54ea5006cc0999cd7159fbbd3916d74",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemSkillDefinition.java": "1e26d5216f230379aeff168536eefcadb9e5d4947d26c678d17c0bb0fde3d747",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemSkillDefinitionVersion.java": "4040ace621d202a2937d1f1244e2b89a69434f5bdabc73aa78f9a7ebdae3e448",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemSkillReferenceCheck.java": "c961bf297e544df14aba90c4e2a274cad3acec34309fd9c20158eff47c8b8c12",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemStat.java": "e2baeb9d858eccbbb6704b99b6c18ec4a4df0846a954f40bfe2ba4bb2b81ed64",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemStatCache.java": "903c7cf66969111f1174d4580c6f3e42090cb7918fc42a920a839ac0d7bf97b9",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersion.java": "953b08cf4d20a78ac2169e84555a8037fa01823864e1b8304248c9940a21aa76",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersionSkillLink.java": "c7c41f41c8c05ed3714e5340c3effbbefc7eeb4138664ca35cf4bcfdad818ad1",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/StatType.java": "4c9b1f7bba977042504fe03133223e8d5c1f703b0c1567e49c8ed9b3893ef4ce",
          "backend/src/main/java/io/github/minokim/lumiawiki/common/api/ApiFailure.java": "d01ace83a4a170451b4cac7a4c7a4f8fd668dd2b669069bd8a4c39691a41243a",
          "backend/src/main/resources/application-local.yaml": "e161d9789956b24211bc886419f0d2791c634be0238e82678a3575fbeeb46144",
          "backend/src/main/resources/application.yaml": "d10d1ef05ddbec053c30bf2bc705e4c5f19a2b688baccd61a4f48af556bb40e0",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/CommonCatalogIntegrationTests.java": "d077d94d547fd8ac592c13053df8faa475a21ed9165fed1e777f557385d69633",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemCatalogServiceTests.java": "6a169be5655dd5331b0dc7138ef80e2eca1e5bac37a522d23f3f7638ac78481c",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemStorageMigrationTests.java": "ec2c92db072cf981c6f81cbefdab5e9f328b36e2d59d7bf59ef0060a4ee27028",
          "backend/src/test/resources/application-test.yaml": "e6aa7eb8da29c749b63e7330c634631d82f8710dc4fb6dee5ef883df1ce12e72",
          "db/bootstrap/10-prepare-roles.sh": "832e9921588251e3a658fadc276ff7d3b46a46b110c45ae7a16cd4eb7819914a",
          "db/bootstrap/sql/prepare-roles.sql": "160a624d9577848f6e61404ad3e52791c6a395af56186fec08e852f3f88ff8d4",
          "db/migration/V1__create_common_model.sql": "1495d8a5085188f535865f9b46f51aa1c9a18480c1b49efd68df61c43f5b8ddd",
          "db/migration/V2__create_item_storage.sql": "69c407f9191555c5c0ceeed62296f44fda9874776b311e75698d2e3cc01940d6",
          "db/migration/V3__complete_item_storage.sql": "610622a531770994696ee295da6bc360e2a27ae48358acd08dc354fb1867a6bd",
          "frontend/package-lock.json": "e54e76e4ab1a402d4df0827152d1bf5c62142cd59e2798518b7ed2715931fc97",
          "frontend/package.json": "aae2e6358d704e1807f860f58272e3f8024cfdc092860bd0b0b4f7d58e76a228",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "2e55a2050f22641deaad0ac4b9b6723ad76aadab22ab037b9d38b1697a458367",
          "frontend/vitest.config.mjs": "f07e4974ad24bc562f5a975e8af587eb6fdfb402863825c718cfdf9a8b684eec",
          "package-lock.json": "539f24e43b65266883d2aa1a83428d75484cf059eeedcedf4043d09dc6d8a5e3",
          "package.json": "0e57b51524c8151aafb0155a93c5f61c30901819bde6cee895c0106f6dfcab85",
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": true
      }
    }
  ]
}
```
