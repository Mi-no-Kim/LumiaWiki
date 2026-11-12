# DB·실행 환경·SQL 배치 기준

<a id="current"></a>

## 적용

로컬 개발은 PostgreSQL 공식 `postgres:18.6` + Docker Compose, 로컬 Spring Boot·React/Vite로 구성한다. 운영 배포 구성은 별도 설계한다. 기준 채택은 DB 실행·접속·마이그레이션 검증 완료를 뜻하지 않는다. 선택 근거는 [Task 003 기록](../../../work/records/phase-001/issue-15/artifacts/task-003-db-environment.md#current)에 보존한다.

<a id="layout"></a>

## 소스 배치·공용 SQL

| 경로                | 역할                                                                                                 |
| ------------------- | ---------------------------------------------------------------------------------------------------- |
| `backend/`          | Spring Boot·Gradle 프로젝트 위치 확정. 로컬 JDK·Wrapper 또는 IDE로 실행하며 공용 환경변수 전달       |
| `frontend/`         | React·Vite·TypeScript 프로젝트 위치 확정. 로컬 npm으로 실행                                          |
| `db/migration/`     | backend 밖에서 공통 관리하는 DB 구조 변경 SQL 원천 위치 확정. Python 등 다른 도구의 사용 가능성 반영 |
| 루트 `compose.yaml` | 합의한 PostgreSQL 컨테이너·개인 `.env` 기반 개발 환경 관리                                           |

화면·API·DB SQL을 역할에 맞는 폴더에서 관리한다. DB 실행 설정은 루트에서 함께 찾기 쉽게 두는 안이며 운영 배포의 컨테이너 구성은 별도 결정한다. 실제 기반 구축 때 생성한 경로를 프로젝트 구조 안내에 반영한다.

사용자는 Python 등에서도 DB를 업데이트할 가능성을 들어 SQL을 backend 밖에 두는 배치를 채택했다. SQL 원천은 공용 `db/migration/`에 한 번만 관리한다. Gradle 리소스 처리로 해당 SQL을 빌드 결과의 `db/migration/`에 포함하고 Spring Boot 시작 시 `classpath:db/migration`의 Flyway 자동 실행으로 적용한다. 이는 이미 선택한 Spring Boot Flyway와 공용 SQL 배치를 연결하는 구현 기준이며 별도 실행 도구를 다시 고르는 항목이 아니다. 외부 SQL의 리소스 포함·기본 Flyway 경로 지원은 공식 문서에서 확인했으며 구체 설정·패키징 검증은 후속 기반 구축에서 한다. 저장소 안에 SQL 사본을 따로 관리하지 않는다.

Python의 업데이트가 아이템 자료 등록·정정이면 DB에 대한 데이터 처리이며, 테이블 구조 변경은 공통 SQL과 Spring Boot Flyway 이력으로 관리한다. 독립 Flyway CLI는 외부 도구 사용 가능성을 확인한 근거이며 현재 실행 계획에 추가하지 않는다. Python 환경·스크립트를 지금 도입하는 결정도 하지 않았다. 게임 자료 등록의 구체 수단·정정 기록은 Task 004와 해당 후속 설계의 담당 범위를 유지한다. 기존 첨부 SQL 원자료도 보존한다.

<a id="db-config"></a>

## 보존·접속·환경변수

| 항목             | 확정한 기준                                                                                                            |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------- |
| 데이터 저장      | Compose named volume `postgres_data`를 PostgreSQL 18 이미지의 `/var/lib/postgresql`에 연결                             |
| 일상 종료·초기화 | 일반 종료는 `docker compose down`으로 볼륨 유지. 볼륨 삭제를 수반하는 초기화는 별도 수동 작업으로 분리                 |
| 백업             | 중요한 등록 데이터는 `pg_dump`로 보존하고 필요한 데이터의 삭제·초기화 전에 백업. 자동 백업 체계는 운영 설계에서 구체화 |
| 접속 주소        | 로컬 API·관리 도구에서 `127.0.0.1:5432`, 컨테이너 포트는 5432. 호스트 포트 충돌 시 환경변수로 조정                     |
| DB·계정          | DB 이름 `lumiawiki`, 초기 개발 계정 `lumiawiki`. 로컬 개발에서는 앱·Flyway가 같은 계정 사용                            |
| 비밀번호         | 개발자 개인 값으로 지정하고 실제 값은 Git에 포함하지 않음                                                              |
| 구조 변경        | 합의한 Spring Boot Flyway로 적용. JPA는 `ddl-auto=validate`, 기본 SQL 자동 초기화는 `spring.sql.init.mode=never`       |

환경변수는 `DB_HOST=127.0.0.1`, `DB_PORT=5432`, `DB_NAME=lumiawiki`, `DB_USERNAME=lumiawiki`, `DB_PASSWORD=<개인 값>`을 기준으로 한다. JDBC URL 예시는 `jdbc:postgresql://127.0.0.1:5432/lumiawiki`이며 실제 설정은 위 변수로 구성한다. Compose는 `DB_PORT`를 로컬 포트에, `DB_NAME`·`DB_USERNAME`·`DB_PASSWORD`를 `POSTGRES_DB`·`POSTGRES_USER`·`POSTGRES_PASSWORD`에 명시적으로 연결한다. 로컬에만 바인딩한다.

루트 `.env`는 개인 실행값으로 Git에서 제외하고 `.env.example`에는 변수 이름·기본값·비밀번호 자리표시자만 커밋한다. Compose는 `.env` 값을 사용하고, 로컬 Spring Boot 실행에는 IDE 또는 개발 실행 명령을 통해 같은 변수들을 프로세스 환경변수로 전달한다. 루트 `.env`만 두면 Spring Boot가 자동으로 읽는다고 가정하지 않는다. 실제 로더·실행 설정은 후속 기반 구축에서 구현·검증하며 추가 라이브러리나 도구를 지금 채택하지 않는다. DB 비밀번호를 프런트 환경변수에 포함하지 않는다.

공식 이미지의 `POSTGRES_USER`는 초기 슈퍼유저를 생성하므로 계정 공용은 로컬 개발 초기 단순화 선택이다. 운영의 계정·권한·비밀값 공급은 배포 설계에서 구분한다. 이미지 초기화 변수는 빈 데이터 디렉터리의 최초 생성에 적용되며 기존 DB의 계정·DB 이름을 `.env` 수정만으로 변경하는 방식은 사용하지 않는다. named volume 보존은 별도 덤프 백업과 구별한다.

- [PostgreSQL 이미지·초기화 변수·저장 경로](https://hub.docker.com/_/postgres) · [Compose 종료·볼륨 옵션](https://docs.docker.com/reference/cli/docker/compose/down/) · [Compose 환경변수](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/) · [Spring 외부 설정](https://docs.spring.io/spring-boot/reference/features/external-config.html) · [PostgreSQL 덤프 백업](https://www.postgresql.org/docs/18/backup-dump.html)

프로필·테스트 분리는 [서버 환경별 설정](<../../개발 기준.md#server-profiles>)과 [테스트 기준](<테스트와 TDD.md#current>)을 따른다. 실제 리소스 포함·JAR 내 SQL·Boot 시작 시 Flyway 적용과 재시작·볼륨 보존·테스트 DB 분리는 첫 기반 구축에서 확인한다.
