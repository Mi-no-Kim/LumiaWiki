# 공통 8개 표 생성 전 확인안

<a id="current"></a>

합의한 DDL의 전체 구조와 승인한 실행 범위다. 구조 원천은 [V1 DDL](V1__create_common_model.sql)이며 실제 상태는 [적용 결과](application-status.md#current)에서 확인한다.

## 승인 범위와 실행 대상

사용자는 이 구조와 순서대로 새 격리 PostgreSQL 18.6에서 먼저 검증한 뒤 기존 로컬 lumiawiki DB에 8개 표를 추가하도록 승인했다. 실제 게임 자료 조사·등록은 계속 보류한다. 구조나 대상이 바뀌거나 승인 범위 밖의 기존 객체 변경이 필요하면 먼저 확인받는다.

| 구분           | 대상                                                                                   | 상태                                                 |
| -------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| 최초 적용 검증 | 새 Testcontainers PostgreSQL 18.6, lumiawiki/public. 기존 개발 볼륨 미사용             | DDL·JPA·권한·조회/저장·잠금·업무/설치 롤백 검증 통과 |
| 로컬 적용      | Docker desktop-linux / lumiawiki-db-1(e85f1d98b2a7), 127.0.0.1:5432 / lumiawiki/public | Flyway V1 적용·JPA 검증·메타정보 대조 완료           |

로컬 준비는 별도 승인한 두 로그인 역할 생성·최소 권한/PUBLIC 권한 회수·빈 flyway_schema_history의 migrator 소유 이관 범위다. 개인 .env의 app/Flyway 값은 출력 없이 사용하고 누락/예제 키만 보완했다. 기존 개인 설정과 DB/public 소유자는 유지한다.

## 전체 열 구조

모든 표는 public 소속이며 id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY를 포함한다. 아래에서 ?는 NULL 허용, 표시 없는 열은 NOT NULL이다. ID 발급 외의 기본값은 없다.

| 표                 | id 외 전체 열                                                                                                           |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| season             | season_number INTEGER, display_name TEXT, season_name TEXT?, sort_order BIGINT, start_date DATE?, end_date DATE?        |
| game_patch         | season_id BIGINT, major_no INTEGER, minor_no INTEGER, version_name TEXT?, sort_order BIGINT, applied_at TIMESTAMPTZ(0)? |
| region             | display_name TEXT                                                                                                       |
| item_category      | name TEXT, parent_id BIGINT?                                                                                            |
| item_grade         | name TEXT, sort_order BIGINT                                                                                            |
| weapon_type        | name TEXT, category_id BIGINT                                                                                           |
| region_map_version | from_game_patch_id BIGINT                                                                                               |
| region_map_member  | map_version_id BIGINT, region_id BIGINT, name TEXT, sort_order BIGINT                                                   |

region.display_name은 필수·빈값/중복 금지의 작업용 이름이다. 공개 API/화면에 포함하지 않고, 공개 이름·순서는 지도 소속 행에서 읽는다. 두 이름은 자동 동기화하지 않는다.

## 관계와 참조

| FK                                                       | 개수/의미                                                      |
| -------------------------------------------------------- | -------------------------------------------------------------- |
| game_patch.season_id → season.id                         | 패치마다 시즌 1개, 시즌에는 패치 여러 개                       |
| item_category.parent_id → item_category.id               | 부모 0~1개. 확인된 최상위만 NULL, 자식 여러 개                 |
| weapon_type.category_id → item_category.id               | 무기 종류마다 종류 1개, 종류에는 무기 종류 최대 1개            |
| region_map_version.from_game_patch_id → game_patch.id    | 구성마다 시작 패치 1개, 패치에는 시작 구성 최대 1개            |
| region_map_member.map_version_id → region_map_version.id | 소속 행마다 구성 1개, 구성에는 소속 행 0개 이상                |
| region_map_member.region_id → region.id                  | 소속 행마다 지속 지역 1개. 같은 구성에서는 같은 지역 중복 금지 |

6개 FK는 비지연 검사·ON DELETE RESTRICT·ON UPDATE NO ACTION이다. 종류의 긴 순환과 패치 정렬식/후속 소속 검사는 Spring 업무 계약을 함께 따른다.

## 유일성·검사·조회 의미

| 표                 | UNIQUE·CHECK                                                                                                            |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| season             | season_number UNIQUE/1 이상. sort_order=season_number::bigint+9. 양쪽 날짜가 있으면 종료일≥시작일                       |
| game_patch         | (season_id, major_no, minor_no) UNIQUE, sort_order UNIQUE. 메이저·마이너 각각 0~99                                      |
| region             | display_name UNIQUE                                                                                                     |
| item_category      | UNIQUE NULLS NOT DISTINCT(parent_id, name), 자기 부모 금지                                                              |
| item_grade         | name UNIQUE, sort_order UNIQUE. 순서의 추가 시작값/간격 CHECK 없음                                                      |
| weapon_type        | name UNIQUE, category_id UNIQUE                                                                                         |
| region_map_version | from_game_patch_id UNIQUE                                                                                               |
| region_map_member  | (map_version_id, region_id), (map_version_id, name), (map_version_id, sort_order) 각각 UNIQUE. 순서는 10 이상·10의 배수 |

- 값이 있는 이름은 빈 문자열/기본 공백만인 값을 거부한다. 자동 trim·대소문자/Unicode 정규화는 하지 않는다.
- 중복 검사 대상 이름 5개 열은 COLLATE "C"를 사용한다. 시즌 표시/실제 이름·패치 이름에는 추가 UNIQUE를 두지 않는다.
- 모든 UNIQUE는 비지연 검사다. PK/UNIQUE 인덱스 외 추가 인덱스는 없다.
- 패치 정렬식은 시즌 정렬×10000+메이저×100+마이너이며 Spring에서 계산/검증한다. 적용 시각은 저장 전에 초 미만을 절삭한다.
- 지도 구성은 시작 패치 이상·다음 구성 시작 패치 미만에 적용한다. 앞선 구성이 없으면 미확인, 구성은 있고 소속 0개면 확인된 빈 지도다.
- DDL에 명시한 PK·NOT NULL·UNIQUE·CHECK·FK의 60개 제약 이름은 SQL을 단일 원천으로 사용한다. [공통 상세](../model/table-layout.md#current)·[지도 상세](../model/region-layout.md#current)를 함께 읽는다.

## 보호·권한·설치 범위

- 함수 public.reject_common_pk_update(): SECURITY INVOKER, search_path=pg_catalog, PUBLIC 실행권 회수.
- 8개 표에 trg_<표명>_reject_pk_update AFTER UPDATE 행 trigger. 실제 id 변경만 LW001로 거부하며 WHEN/UPDATE OF는 두지 않는다.
- lumia_migrator가 함수·표·시퀀스를 소유/설치한다. lumia_app은 8개 표 SELECT/INSERT/UPDATE, 소속 행에만 교정용 DELETE를 받는다.
- 함수·8개 표·제약·trigger·GRANT는 Flyway 한 파일의 트랜잭션으로 설치한다. 충돌 시 중단하며 기존 객체를 교체/삭제/건너뛰지 않는다.
- 실패 롤백은 해당 마이그레이션 단위다. 선행 bootstrap·DB/볼륨·기존 Flyway 관리 표까지 삭제하지 않는다.
- 함수 직접 EXECUTE·시퀀스 일괄 권한·DEFAULT PRIVILEGES·소유/DDL/TRUNCATE/재위임 권한을 app에 추가하지 않는다.

## 실행 순서와 중단 조건

1. 사용자에게 위 구조와 대상의 최종 확인 및 기존 로컬 DB 메타정보 조회/적용 범위를 확인받는다. 현재 승인 범위는 위와 같다.
2. 필요한 읽기 전용 메타정보로 기존 표·함수·Flyway 이력·역할/권한·소유를 확인한다. 게임 자료 행은 조회하지 않는다.
3. N5대로 새 격리 DB에 먼저 동일 DDL을 설치하고 권한·IDENTITY/PK guard·JPA/저장/조회·실패/롤백의 필요한 검증을 수행한다.
4. 개발 대상이 합의한 전제와 일치하고 충돌이 없을 때 동일 구조를 적용한다. 기존 객체/역할·소유·이력의 다른 변경이 필요하면 변경안과 필요한 입력을 먼저 제시한다.
5. 실제 생성 결과·검증/미확인·정확한 실행 대상과 적용 DDL 지문을 목적별 DB 문서와 담당 작업 기록에 반영한다.

검토 DDL SHA-256: 1495d8a5085188f535865f9b46f51aa1c9a18480c1b49efd68df61c43f5b8ddd. 내용이나 대상이 달라지면 영향을 받은 범위를 다시 제시한다. 실제 자료 작업과 자동 볼륨 삭제/초기화는 허용 범위에 넣지 않는다.
