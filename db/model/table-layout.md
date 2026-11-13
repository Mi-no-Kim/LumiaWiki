# 전체 8개 표의 구조 검토

<a id="current"></a>

8개 표 저장 구조와 N1~N5는 확정 계약이다. 메이저·마이너 각각 0~99는 사용자 확인을 받은 범위이며 패치 정렬값 UNIQUE를 적용한다. [공통 계약](common-tables.md#current)과 [D1](names-and-dates.md#current)·[D2](ranges-and-uniqueness.md#current)를 함께 읽는다. 제약 이름은 [V1 DDL](../migration/V1__create_common_model.sql), 실제 설치 대상과 검증은 [적용 결과](../migration/application-status.md#current)가 소유한다. 실제 자료 작업은 계속 보류한다.

## 전체 생성 검토 대상

| 표                 | 전체 필드/제약의 담당 구역                     | 역할                               |
| ------------------ | ---------------------------------------------- | ---------------------------------- |
| season             | [시즌](#season)                                | 시즌 번호·이름·정렬·기간           |
| game_patch         | [패치](#game-patch)                            | 시즌 내 패치와 정렬·적용 시각      |
| region             | [지역 대상](#region)                           | 지속 지역 ID·작업용 표시 이름      |
| item_category      | [종류](#item-category)                         | 현재 이름·부모 트리                |
| item_grade         | [등급](#item-grade)                            | 등급 목록·표시 순서                |
| weapon_type        | [무기 종류](#weapon-type)                      | 종류와 일대일로 연결되는 별도 대상 |
| region_map_version | [지도 구성 버전](region-layout.md#map-version) | 전체 지도 구성의 시작 패치         |
| region_map_member  | [지도 소속 행](region-layout.md#map-member)    | 해당 구성의 등장 지역·이름·순서    |

각 행의 필드/NULL·키·제약은 연결한 구역에서 한 번만 관리한다. 후속 획득 본행은 이 8개 표에 포함하지 않으며 [C-A 참조](consumer-references.md#current)를 공통 입력으로 넘긴다. 생성 직전에는 아래 6개 표와 지역 문서의 2개 표를 한 전체 구조로 다시 확인받는다.

## 공통 표기

- 아래 6개 표는 public 스키마의 표이며 각각 `id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY`를 포함한다. 각 필드표에서는 공통 id만 생략했다.
- 필드 기본값은 ID 발급 외에 두지 않는다. TEXT는 값이 있을 때 빈 문자열/기본 공백만인 값을 거부하며 자동 trim·이름 합성·정규화를 하지 않는다. N2에 따라 중복 검사 대상인 region.display_name·item_category.name·item_grade.name·weapon_type.name·region_map_member.name에 COLLATE "C"를 명시한다. 대소문자·앞뒤 공백·Unicode 표현이 다른 문자열은 구별하며 검색 정규화와 혼용하지 않는다.
- FK는 NOT DEFERRABLE·ON DELETE RESTRICT·ON UPDATE NO ACTION을 적용한다.
- 일반 UNIQUE는 U-A의 즉시 검사 기준을 적용한다. 초기 여러 행 자리교환은 제외하며 세부 의미는 [갱신 대안](writes-and-checks.md#unique-timing)에서 함께 확인한다.

<a id="season"></a>

## season

| 열            | 자료형  | NULL | 검사·역할                                                |
| ------------- | ------- | ---- | -------------------------------------------------------- |
| season_number | INTEGER | 불가 | UNIQUE, 1 이상                                           |
| display_name  | TEXT    | 불가 | 표시 이름. 추가 UNIQUE 없음(N1)                          |
| season_name   | TEXT    | 허용 | 실제 이름, 표시 이름으로 대체하지 않음                   |
| sort_order    | BIGINT  | 불가 | season_number+9와 일치. 추가 UNIQUE는 기본 후보에서 제외 |
| start_date    | DATE    | 허용 | 날짜 그대로 보존                                         |
| end_date      | DATE    | 허용 | 양쪽 날짜가 있으면 start_date 이상                       |

<a id="game-patch"></a>

## game_patch

| 열           | 자료형         | NULL | 검사·역할                              |
| ------------ | -------------- | ---- | -------------------------------------- |
| season_id    | BIGINT         | 불가 | season.id FK                           |
| major_no     | INTEGER        | 불가 | 0~99 CHECK. 사용자 확인 범위           |
| minor_no     | INTEGER        | 불가 | 0~99 CHECK. 실제 0도 명시 입력         |
| version_name | TEXT           | 허용 | 번호 표기와 별도. 추가 UNIQUE 없음(N1) |
| sort_order   | BIGINT         | 불가 | 기존 식으로 계산/검증. UNIQUE          |
| applied_at   | timestamptz(0) | 허용 | UTC·초 단위. 저장 전에 초 미만 절삭    |

`(season_id, major_no, minor_no)`와 sort_order는 각각 UNIQUE다. 메이저·마이너는 각각 0~99 CHECK를 적용한다. 이 범위는 사용자 확인에 근거하며 실제 자료 조사/등록이나 DB 제약 생성은 수행하지 않았다. 부모 시즌 값을 참조하는 계산은 Spring 업무에서 처리하며 행 CHECK 하나가 그 관계를 보장한다고 주장하지 않는다.

<a id="region"></a>

## region

| 열           | 자료형 | NULL | 검사·역할                                  |
| ------------ | ------ | ---- | ------------------------------------------ |
| display_name | TEXT   | 불가 | 작업용 표시 이름. 빈값 금지·목록 안 UNIQUE |

같은 지역의 ID를 시즌 사이 유지한다. display_name은 작업 중 대상을 구별하기 위한 내부 표시 값이며 공개 API·화면 출력에 포함하지 않는다. 공개 조회의 이름·순서는 [지도 구성의 소속 행](region-layout.md#current)을 사용한다. 작업용 이름과 소속 행 이름은 자동 동기화하지 않으며 작업용 이름만 수정해도 지도 새 버전·과거 구성·획득 참조에는 영향을 주지 않는다. 작업용 이름을 업무 식별 키나 게임 코드로 사용하지 않는다.

<a id="item-category"></a>

## item_category

| 열        | 자료형 | NULL | 검사·역할                                               |
| --------- | ------ | ---- | ------------------------------------------------------- |
| name      | TEXT   | 불가 | 현재 이름                                               |
| parent_id | BIGINT | 허용 | item_category.id FK. 확인된 루트만 NULL, 자기 부모 금지 |

`UNIQUE NULLS NOT DISTINCT (parent_id, name)`를 적용한다. 형제·루트의 동명 금지와 다른 부모의 동명 허용을 표현한다. 긴 순환은 [서비스 검사](writes-and-checks.md#hierarchy)로 구별하고 깊이·특정 루트 ID·이름에 따른 무기 판정을 추가하지 않는다.

<a id="item-grade"></a>

## item_grade

| 열         | 자료형 | NULL | 검사·역할                                          |
| ---------- | ------ | ---- | -------------------------------------------------- |
| name       | TEXT   | 불가 | 등급 목록 안 UNIQUE                                |
| sort_order | BIGINT | 불가 | 등급 목록 안 UNIQUE. 시작값·간격의 추가 CHECK 없음 |

관리자 판단과 기본 검사로 같은 ID의 값을 수정한다. 교정/변경을 자동 판별하는 필드·전용 guard는 추가하지 않는다.

<a id="weapon-type"></a>

## weapon_type

| 열          | 자료형 | NULL | 검사·역할                    |
| ----------- | ------ | ---- | ---------------------------- |
| name        | TEXT   | 불가 | 무기 종류 목록 안 UNIQUE     |
| category_id | BIGINT | 불가 | item_category.id FK + UNIQUE |

category_id로 확정한 일대일 대응을 직접 저장한다. 무기 종류마다 종류 1개, 종류에는 무기 종류 최대 1개를 표현한다. 종류 이름과 무기 종류 이름은 자동 동기화하지 않는다.

## 제약·인덱스와 확인 잔여

PK/UNIQUE가 만드는 인덱스와 같은 인덱스를 중복 추가하지 않는다. 종류의 부모 조회는 위 복합 UNIQUE, 패치의 시즌 조회는 번호 조합 UNIQUE, 무기 종류의 분류 참조는 category_id UNIQUE를 먼저 대조한다. 그 밖의 FK/조회 인덱스는 필요한 조회와 실행 근거가 있을 때 제안한다.

N1은 시즌 표시 이름·실제 시즌명·패치 이름에 추가 UNIQUE를 두지 않는 계약이다. N2의 이름 비교·N5의 명시적 제약 이름과 새 빈 환경의 V1__create_common_model.sql 한 파일 설치를 적용한다. 실제 제약별 이름은 DDL 초안에서 구조와 함께 제시한다. [N3~N4의 구현/확인·실패 경계](writes-and-checks.md#failure-and-verification)를 따르며 실제 테이블 생성 직전에는 이 계약과 [지역 구조](region-layout.md#current)·[권한/설치](permissions-and-installation.md#current)를 한 전체 구조로 다시 제시하고 [사용자 확인](../migration/README.md#precreation-confirmation)을 받는다. 설계 수용을 실행 승인으로 확대하지 않는다.
