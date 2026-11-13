# 공통 8개 표 적용 결과

<a id="current"></a>

승인한 [전체 구조](creation-review.md#current)를 새 격리 DB에서 검증한 뒤 기존 로컬 DB에 적용했다. 실제 게임 자료는 조사·변환·등록하지 않았으며 **로컬 제품 표 8개는 모두 0행**이다.

## 로컬 적용 대상과 결과

| 항목        | 확인 결과                                                                              |
| ----------- | -------------------------------------------------------------------------------------- |
| 실행 대상   | Docker desktop-linux / lumiawiki-db-1(e85f1d98b2a7), 127.0.0.1:5432 / lumiawiki/public |
| DB 서버     | PostgreSQL 18.6                                                                        |
| 적용        | Flyway V1__create_common_model.sql 성공, 설치자 lumia_migrator, checksum -995352012    |
| 제품 구조   | 8개 표·명시한 제약 60개·FK 6개·PK 보호 trigger 8개·공용 함수 1개                       |
| Java 접속   | lumia_app으로 실행 JAR의 Hibernate validate 성공                                       |
| 소유        | 제품 표·시퀀스·함수와 Flyway 관리 표는 lumia_migrator                                  |
| 유지한 소유 | DB는 lumiawiki, public 스키마는 pg_database_owner                                      |

DDL SHA-256: 1495d8a5085188f535865f9b46f51aa1c9a18480c1b49efd68df61c43f5b8ddd. 실행 JAR의 SQL과 원천 파일이 일치한다. 실제 열·제약·trigger·권한·소유·0행 대조는 [메타정보 근거](../../work/records/phase-001/issue-43/artifacts/task-001-local-metadata.json)를 따른다.

## 계정과 준비 범위

별도 승인에 따라 lumia_app·lumia_migrator LOGIN 역할을 최소 권한으로 생성하고 대상 DB/public의 PUBLIC 권한을 회수했다. app에는 8개 표 SELECT/INSERT/UPDATE와 region_map_member DELETE만 있다. 소유·DDL·TRUNCATE·재위임·시퀀스 일괄 권한·역할 멤버십은 부여하지 않았다.

빈 flyway_schema_history만 lumia_migrator로 소유권을 이관했다. 개인 .env의 누락/예제 app·Flyway 키 4개를 보완했고 기존 값은 유지했다. 비밀번호는 명령행·실행 출력·결과 문서에 포함하지 않았다. 볼륨 삭제·초기화와 기존 제품 객체의 교체는 수행하지 않았다.

## 격리 검증과 한계

단위 30건·전체 통합 11건(공통 모델 5·기존 최초 준비/앱 6)과 SpotlessCheck/실행 JAR 확인을 통과했다. 새 PostgreSQL 18.6의 합성 입력으로 다음 5개 공통 모델 통합 검사를 수행했다. 로컬에는 합성 입력도 등록하지 않았다.

- 최초 설치·8개 객체 소유·ALWAYS·FK·trigger·함수 권한·Flyway 재검증/재실행 없음.
- JPA 저장/조회·시각 절삭·지도 미확인/빈 구성/재사용·작업용 이름 분리·순환 거부·제약 오류 변환·지도 교정 실패 롤백.
- 비소유 app의 ID 발급·일반 수정과 IDENTITY/PK guard·UNIQUE/CHECK/FK·DDL/DELETE/TRUNCATE/trigger/역할 변경 거부.
- 충돌하는 기준 잠금의 대기/해제와 일반 SELECT 허용.
- 원천 DDL 뒤 강제 오류를 넣은 별도 격리 DB에서 제품 표·함수·권한 전체 롤백. Flyway 관리 표는 빈 상태로 남음.

ALWAYS 열의 id=id는 PostgreSQL이 428C9로 먼저 거부한다. id=DEFAULT로 새 ID를 발급하려는 갱신은 guard의 LW001로 거부됨을 확인했다. 다른 제약이 먼저 거부하면 그 오류를 유지한다. [IDENTITY](https://www.postgresql.org/docs/18/ddl-identity-columns.html)·[UPDATE](https://www.postgresql.org/docs/18/sql-update.html)·[오류 코드](https://www.postgresql.org/docs/18/errcodes-appendix.html)를 함께 참고한다.

이 검증은 실제 자료 적합성·제품 HTTP 화면·후속 003/004의 획득/아이템 참조 검증을 대신하지 않는다. 소비 표를 만들기 전 해당 서비스의 소속/구간 검사를 연결해야 한다. 실행 명령과 작업 수용은 [구현 안내](../model/implementation.md#current)·[담당 기록](../../work/records/phase-001/issue-43/artifacts/task-001-creation.md#verification)에서 관리한다.
