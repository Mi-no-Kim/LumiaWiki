# 공통 DB 식별·참조·저장 계약

<a id="current"></a>

[개발 기준](<../../개발 기준.md#current>)의 주제별 상세다. 기준 채택과 실제 구현/검증·자료/DB 작업 재개를 구별한다.

<a id="internal-identifiers"></a>

## 공통 내부 ID

| 경계           | 기준                                                          |
| -------------- | ------------------------------------------------------------- |
| DB 내부        | PostgreSQL `BIGINT` + DB의 IDENTITY 자동 발급                 |
| Java 서버 내부 | `Long`                                                        |
| API·프런트     | 식별 ID는 JSON 문자열로 전달하고 TypeScript `string`으로 취급 |

ID의 API 표현은 DTO 경계에서 명시하고 수량·능력치나 모든 Long 필드를 전역 문자열로 바꾸지 않는다. `BIGINT` 전체 범위가 JavaScript 안전 정수 범위보다 넓으므로 ID의 값이 왕복 과정에서 바뀌지 않도록 한다. DB 쓰기를 담당하도록 정한 도구는 같은 ID 발급 방식을 사용한다.

지속적인 대상과 특정 버전의 ID를 구분해 참조한다. 시즌 번호·버전 표기/정렬식·지역 정렬값과 별도 게임 코드/관리 코드 필드를 두지 않는 의미 규칙은 [제품 식별 기준](<../product/게임 데이터 변경 관리.md#identity-information>)을 따른다. 내부 ID로 이 숫자들을 대체하거나 계산하지 않는다.

Task 43-001의 공통 대상 내부 ID는 `BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY`로 두고, 시즌 번호와 패치의 `(소속 시즌 ID, 메이저 번호, 마이너 번호)` 조합에는 각각 업무 UNIQUE를 둔다. 이 범위는 F1의 확정 결정이며, [담당 Task의 키 계약](../../../work/records/phase-001/issue-43/artifacts/task-001-common-model.md#f1-keys)을 따른다. 내부 ID의 PK와 업무상 중복 방지를 구별하고 지정한 번호·정렬값을 ID로 대체하지 않는다.

[M1~M3 저장 계약](#common-six-storage-contract)은 업무 번호 INTEGER·정렬값 BIGINT·이름 TEXT와 추가 필수값/검사·종류 이름 유일성 범위를 정의한다. 실제 제약 배치·업무 허용 범위·그 밖의 정렬값 유일성/NULL/FK/삭제 정책은 담당 미정이다. 버전/연결 행의 키·참조 일치 검사는 각 저장 Task에서 결정하고 복원/명시 ID·시퀀스 보정은 필요 시점에 다룬다. IDENTITY는 유일성이나 ID 불변성을 대신하지 않는다. 실제 스키마·Java 매핑·DTO는 해당 과제에서 구현하고 자동 발급·값 왕복·참조 정합성을 검증한다.

근거: [PostgreSQL IDENTITY](https://www.postgresql.org/docs/18/ddl-identity-columns.html) · [정수 자료형](https://www.postgresql.org/docs/18/datatype-numeric.html) · [JavaScript 안전 정수 범위](https://tc39.es/ecma262/multipage/numbers-and-dates.html#sec-number.max_safe_integer).

<a id="common-reference-rules"></a>

### 공통 참조·핵심 필수값·삭제의 채택 범위

Task 43-001의 일반 공통 참조는 DB FK를 `NOT DEFERRABLE`로 검사하고, 참조 중인 공통 대상의 삭제는 `ON DELETE RESTRICT`로 거부한다. ON UPDATE는 NO ACTION을 적용한다. 일반 FK는 SQL 명령이 끝날 때 참조가 맞아야 하며, 같은 트랜잭션의 다음 명령에서 대상을 만들 예정이라는 이유로 검사를 미루지 않는다. 실제 FK 열은 각 저장 계약을 따르고 제약 이름은 DDL 작성 전에 정한다.

| 항목                                   | 확정한 기준                                                      |
| -------------------------------------- | ---------------------------------------------------------------- |
| 시즌 번호                              | 기준 원본의 필수값으로 NOT NULL                                  |
| 패치의 소속 시즌 ID·메이저/마이너 번호 | 기준 원본의 필수값으로 NOT NULL                                  |
| 완성된 아이템 버전의 종류 ID           | 필수 참조로 NOT NULL. 실제 저장 계약은 담당 아이템 Task와 연결   |
| 확인된 최상위 종류의 부모              | parent_id NULL로 표현. 미확인/생략된 부모를 루트로 간주하지 않음 |

핵심 필수값이 미확인인 행은 기준 원본에 선등록하지 않는다. 미확인 입력의 보관 위치·처리 절차·별도 상태 필드는 미정이다. M1의 추가 필수값과 별개로 날짜/실제 이름·기타 NULL 허용은 각각 확인하며 실제 0인 메이저/마이너와 미확인 대체값을 구별한다.

참조 중 삭제 제한은 게임 내 삭제·검색 제외 처리와 구별한다. 자기 부모 CHECK와 공통 PK 일반 변경 금지 정책은 [F4-S2·S3의 채택 범위](<DB 갱신과 보호.md#outside-service-sql>)를 따른다. 공통 8개 표의 보호·업무 권한은 [설치 계약](../../../db/model/permissions-and-installation.md#current)을 따른다. 후속 복합 FK·미참조 행 삭제와 복원/시퀀스 보정은 각 담당 범위에서 정한다. [담당 검토와 검사 시점 예시](../../../work/records/phase-001/issue-43/artifacts/task-001-common-model.md#f3-timing)를 따르며, 정책 채택을 실제 DB 작업의 허용이나 검증 완료로 표시하지 않는다.

<a id="common-six-storage-contract"></a>

### M1~M3의 공통 6개 표 저장 계약

M1~M3와 [공통 8개 표의 저장 구조](../../../db/model/table-layout.md#current)·N1~N5는 확정 계약이다. D3는 category_id의 필수 FK + UNIQUE, D4는 지속 지역 ID·작업용 이름과 지도 구성/소속 행의 패치 이력이다. D1의 5개 메타정보 NULL 등록과 지정 목록/조회 패치의 중복 금지를 유지한다. 메이저·마이너 각각 0~99는 사용자 확인을 받은 범위이며 CHECK와 패치 정렬값 UNIQUE를 적용한다. 실제 자료 조사·제품 도메인 구현·DB 동작 검증은 미수행이다.

| 표            | M1 채택 필드/자료형·필수값                                                                                                              | 계속 미정인 범위                                                                     |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| season        | season_number INTEGER NOT NULL, display_name TEXT NOT NULL, season_name TEXT, sort_order BIGINT NOT NULL, start_date/end_date DATE      | 실제 이름·시작/종료일 NULL 허용(D1). 실제 값은 미확인                                |
| game_patch    | season_id BIGINT NOT NULL, major_no/minor_no INTEGER NOT NULL, version_name TEXT, sort_order BIGINT NOT NULL, applied_at timestamptz(0) | 이름/적용 시각 NULL 허용(D1). 번호 각각 0~99 CHECK·정렬 UNIQUE 확정                  |
| region        | display_name TEXT NOT NULL·UNIQUE. 공개 이름 name TEXT NOT NULL·정렬값 sort_order BIGINT NOT NULL은 지도 소속 행에 저장                 | 작업용 이름과 공개 이름은 독립. 지도 구성 안 이름/정렬 중복 금지, 실제 목록은 미확인 |
| item_category | name TEXT NOT NULL, parent_id BIGINT는 확인된 루트만 NULL                                                                               | 무기 연결은 D3, 긴 순환/동시성 수단은 변경 계약                                      |
| item_grade    | name TEXT NOT NULL, sort_order BIGINT NOT NULL                                                                                          | 목록 안 동명·동순위 금지(D2). 실제 목록·시작값/간격 미확인. 관리자 판단과 기본 검사  |
| weapon_type   | name TEXT NOT NULL, category_id BIGINT NOT NULL FK + UNIQUE                                                                             | 종류와 일대일 대응, 무기 종류 목록 안 동명 금지(D2). 실제 대응 목록·제약명은 미확인  |

M1은 업무 값의 기본 0/빈 문자열·누락 이름의 자동 대체를 두지 않는다. 표시 이름/실제 시즌명·별도 패치 이름을 구별하고 실제 0인 번호는 명시 입력한다. 이름의 새 길이 제한·자동 trim/대소문자 변환/Unicode 정규화·동명 병합을 추가하지 않는다. BIGINT 정렬값에도 모든 Long의 API 문자열화를 확대하지 않는다. region은 지속 ID를 유지하고 지역 전체 지도 구성 버전/소속 행의 두 표를 추가하는 R-A 방향을 사용한다. 실제 열·키·참조와 생성 대상 전체 구조는 [물리안](../../../db/model/region-layout.md#current)에서 재확인한다.

M2는 정렬값을 별도 저장하고 Spring에서 기존 식으로 계산/검증한다. `시즌 번호 >= 1`, 시즌 `sort_order = season_number::bigint + 9`, 패치 `메이저/마이너 >= 0`, 지역 `sort_order >= 10`/10의 배수, 양쪽 날짜가 확인된 시즌 기간의 `end_date >= start_date`, 저장 이름의 빈 문자열/기본 공백만인 값 거부를 확정한다. 기본 공백 검사의 예인 `btrim(name) <> ''`를 모든 Unicode 공백 정책으로 확대하지 않는다. 지역 검사/열은 D4의 최종 배치와 맞춘다. D1의 5개 필드는 NULL 등록을 허용하며 나머지 필수값과 값이 있는 이름의 빈값 검사는 유지한다.

패치 정렬은 참조 season의 정렬값으로 계산한다. FK가 이 수식까지 보장하거나 다른 행 참조 CHECK/생성 열로 계속 일치한다고 가정하지 않는다. 부모 시즌/번호 교정의 영향·동시성/롤백·서비스 밖 예외 SQL의 같은 규칙 준수는 다음 변경 계약에서 다룬다. 읽을 때만 계산하는 안·생성 열 일괄 적용·추가 업무 trigger는 자동 채택하지 않는다.

M3는 같은 부모 아래 종류 이름 중복과 루트끼리의 동명 중복을 금지하고 다른 부모 아래 같은 이름은 허용한다. UNIQUE NULLS NOT DISTINCT (parent_id, name)와 N2의 name COLLATE "C"를 적용한다. 구체 제약별 이름은 DDL 초안에서 제시한다. 별도 parent_id 인덱스를 기본 추가하지 않고 복합 UNIQUE로 조회가 충족되는지 대조하며 PK/UNIQUE 중복 인덱스를 추가하지 않는다. 실제 충돌은 임의 병합/변경 없이 입력·교정 계약으로 반환한다.

[채택 필드표·검사/관계·담당/입력/시점·검증](../../../work/records/phase-001/issue-43/artifacts/task-001-common-model.md#common-six-contract)을 따른다. region.display_name은 작업용·필수·빈값/중복 금지이며 업무 수정은 허용하고 공개 응답에서는 제외한다. 공개 이름과 자동 동기화하거나 지도 이력/획득 참조를 바꾸지 않는다. N1은 시즌 표시/실제 이름·패치 이름의 추가 UNIQUE 없음, N2는 [중복 검사 이름의 C 비교](../../../db/model/ranges-and-uniqueness.md#name-comparison)다. N3~N4의 서비스/저장소·격리 통합 테스트/재현 절차와 일반 오류·기존 설정에 따른 대기 계약은 [갱신 계약](../../../db/model/writes-and-checks.md#failure-and-verification)을 따른다. N5는 명시적 제약 이름·새 빈 격리 환경의 V1__create_common_model.sql 한 파일이며 실제 제약별 이름/실행 환경은 생성 직전 제시한다. 합의한 구현 파일 작성과 DB 없는 테스트는 허용하며 실제 자료·DB 작업은 보류한다.
