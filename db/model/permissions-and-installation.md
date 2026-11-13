# 업무 권한·설치·생성 전 확인안

<a id="current"></a>

기존 migrator 소유/설치·app 비소유 업무 분리를 유지한다. 표별 업무 권한·교정용 소속 행 DELETE·총 8개 PK 보호와 한 파일 설치 M-A/N5는 확정 계약이다. region 작업용 이름 수정에는 UPDATE를 포함한다. 제약/GRANT는 [V1 DDL](../migration/V1__create_common_model.sql)을 원천으로 하며 사용자 구조/대상 확인 뒤 격리 검증과 승인한 로컬 적용을 완료했다. 실제 상태와 별도 승인한 역할/소유 준비는 [적용 결과](../migration/application-status.md#current)를 따른다. 실제 자료 작업은 계속 보류한다.

## A-A — 업무에 필요한 DML과 교정용 DELETE

| 대상                                                   | lumia_app 권한                 | 이유                                                                   |
| ------------------------------------------------------ | ------------------------------ | ---------------------------------------------------------------------- |
| season·game_patch·item_category·item_grade·weapon_type | SELECT, INSERT, UPDATE         | 일반 조회·등록·관리자 수정. 공통 PK의 실제 변경은 기존 guard로 거부    |
| region                                                 | SELECT, INSERT, UPDATE         | 지속 ID 등록·조회와 작업용 표시 이름 수정. 실제 PK 변경은 guard로 거부 |
| region_map_version                                     | SELECT, INSERT, UPDATE         | 구성 등록·부모 행 잠금·승인한 적용 시작 패치 교정                      |
| region_map_member                                      | SELECT, INSERT, UPDATE, DELETE | 같은 구성의 명시된 교정에서 소속 행 교체                               |

소속 행 DELETE는 지정 구성의 교정 업무에 한정한다. 공통 대상/지도 버전의 일반 삭제·TRUNCATE·TRIGGER·구조 변경·소유권·재위임 능력은 주지 않는다. 같은 DB 계정이 Spring을 거쳤는지는 DB가 구별하지 않으므로 서비스 밖 쓰기는 기존 검토된 예외 원칙을 따른다.

비교 대안 A-B는 app의 DELETE를 전혀 주지 않고 지역 구성 교정의 제거/교체 방식부터 다시 설계하는 안이다. 업무 계정의 제거 능력은 줄지만 지역 등장 목록의 교정과 소속 행 참조/보존 요구를 먼저 확정해야 한다. 반대로 모든 공통 표에 DELETE를 일괄 부여하는 안은 초기 추천 범위가 아니다.

lumia_migrator가 직접 생성하는 객체를 소유하고 설치한다. 별도 소유/조회/정비 역할·멤버십과 DEFAULT PRIVILEGES는 추가하지 않는다. IDENTITY INSERT는 비소유자 격리 검증으로 확인했고 시퀀스 전체 USAGE/UPDATE를 미리 부여하지 않는다. 직접 nextval/setval·명시 ID 복원은 조건부 예외로 남긴다.

## 총 8개 표의 PK 보호

기존 6개 공통 표의 보호는 그대로 유지한다. region_map_version/member의 id에도 기존 reject_common_pk_update 함수를 부착해 총 8개 표의 PK를 보호한다. 같은 내부 식별 계약과 함수를 사용해 규칙을 두 벌로 만들지 않기 위해서다. 보호 대상 확대는 M-A에 포함한 확정 계약이며 Spring 검사·LW001/고정 메시지·INVOKER/pg_catalog·PUBLIC EXECUTE 회수 계약은 변경하지 않는다.

| 새 대상               | 후보 trigger                            |
| --------------------- | --------------------------------------- |
| region_map_version.id | trg_region_map_version_reject_pk_update |
| region_map_member.id  | trg_region_map_member_reject_pk_update  |

공통 함수와 신규 표별 trigger는 항상 같은 실제 id 값의 변경만 거부한다. 지역 FK/시작 패치·이름·순서까지 PK guard로 고정하지 않는다. 실제 설치/비소유자 검증은 [적용 결과](../migration/application-status.md#current)를 따른다. 기존 6개만 DB 보호하고 새 두 표는 Spring 검사만 두는 대안은 직접 SQL 예외의 PK 검증 부담이 커 초기 추천하지 않는다.

## M-A — 초기 설치 한 파일

N5의 새 빈 격리 환경용 최초 파일은 V1__create_common_model.sql이다. 제약에 명시적인 이름을 부여하고 실제 제약별 이름은 DDL 초안에서 제시한다. 생성 의존 순서는 보호 함수/공개 실행권 회수 → 독립 표 season·region·item_category·item_grade → game_patch·weapon_type → region_map_version → region_map_member → 업무 권한이다. 자기 부모 FK는 item_category 생성과 함께 표현한다.

| 안       | 새 빈 환경의 파일 이름                                  | 원자/실패 범위                                                                                  |
| -------- | ------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| M-A 채택 | V1__create_common_model.sql                             | 함수·8개 표·제약·각자 guard·권한을 한 Flyway 트랜잭션에 설치. 실패하면 해당 초기 설치 전체 롤백 |
| M-B      | V1__create_common_core.sql + V2__create_region_maps.sql | 첫 단위는 함수/6개 표/guard/권한, 다음은 지역 2개 표/guard/권한. 두 번째 실패 시 첫 단위는 남음 |

M-A는 최초 8개 구조의 부분 설치를 줄이기 위한 선택이다. 표의 전체 구조와 실제 실행 대상/순번은 생성 직전에 재확인한다. 롤백 범위는 해당 마이그레이션의 함수·제품 표·제약·trigger·GRANT 단위이며 선행 bootstrap·DB/Flyway 관리 표까지 모두 되돌린다는 뜻이 아니다. M-B의 첫 설치만 성공한 상태도 제품 기능 완료로 표시할 수 없다.

함수 CREATE/공개 실행권 회수와 각 표 CREATE/자기 trigger는 합의한 같은 마이그레이션 트랜잭션 단위를 유지한다. N5의 최초 적용 검증은 새 격리 DB이며 정확한 실행 환경은 생성 직전 사용자에게 다시 확인받는다. 기존 DB의 Flyway 순번/소유/객체 충돌을 확인하고 승인한 준비 뒤 적용한다. 현재 로컬의 메타정보와 V1 성공은 [적용 결과](../migration/application-status.md#current)로 확인한다. 실제 자료 작업은 계속 보류한다.

plain CREATE로 충돌 시 중단하고 자동 교체·삭제·건너뛰기를 하지 않는다. 승인 전 새 DDL을 적용할 수 있는 Flyway/서버 시작·DB 통합 테스트도 실행하지 않는다. [C-A 참조](consumer-references.md#current)와 [L-A 잠금](writes-and-checks.md#catalog-locking)을 함께 적용하며 잠금 SQL/권한의 실제 검증 범위는 [적용 결과](../migration/application-status.md#current)를 따른다.

## 확인 순서

1. 확정한 R-A/U-A/A-A·C-A 참조·L-A 잠금·M-A 보호/설치를 유지하고 전체 구조의 실제 열/키·권한·실행 대상/순번을 정리한다.
2. 필요한 사실 입력과 Task 003/004 소비 참조를 확인하고 전체 열/관계·제약명/인덱스·trigger/권한·실행 대상과 실패 범위를 완성한다.
3. 실제 테이블 생성 직전에 [전체 구조 재확인](../migration/README.md#precreation-confirmation)을 받는다. 이 문서의 추천 선택만으로 생성하지 않는다.
4. 별도로 허용된 격리 환경에서 설치/왕복·참조/PK 보호·권한 허용/거부·실패 롤백을 검증한다. 기존 개발 DB 적용·실제 자료 등록은 해당 보류 해제/이관 확인 뒤 별도다.

동일 구조의 이전 검토를 생성 직전 확인으로 자동 대체하지 않는다. 사용자에게 보여준 뒤 구조가 바뀌면 영향을 받은 표/관계를 다시 제시한다.
