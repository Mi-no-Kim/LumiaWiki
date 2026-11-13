# Task 43-001 — 로컬 최초 구동·설정·실패 대응

<a id="current"></a>

최초 구동 흐름, 파일/설정과 최초 설치 검증·실패/재시작을 확인할 때. 담당 상태·수용 판단은 [Task 43-001](../task-001.md#summary), 전체 길잡이는 [설계 안내](task-001-shared-version-references.md#summary)를 따른다. 아래 채택·비채택·미정을 구별하며 승인한 공통 구조의 구현·격리 검증·로컬 적용은 [생성 결과](task-001-creation.md#current)를 따른다. 실제 자료 작업은 계속 보류한다.

현재 구동은 [로컬 DB 최초 구동 기준](<../../../../../docs/details/development/로컬 DB 최초 구동.md#bootstrap-startup-contract>)과 아래 A 채택 범위를 따른다. 현재 검사 시점과 제외한 전수 검사/각 5초 계약을 비채택 비교안과 혼용하지 않는다.

<a id="startup-minimum-proposal"></a>

## 최초 구동·권한·비밀값 전달 계약

로컬 최초 구동은 최초 설치/격리 검증과 Spring/Flyway/JPA 기본 기동 오류 처리를 사용한다(A). 별도 FlywayMigrationStrategy·매 기동 전수 검사·전용 5초 계약은 두지 않는다. 계정/소유·고정 권한·B2/B3의 비밀 보호를 적용하며 승인한 공통 구조의 구현·격리 검증·로컬 적용은 [생성 결과](task-001-creation.md#current)를 따른다. 실제 자료 작업은 계속 보류한다.

### 최초 구동 구현 범위

| 영역           | 유지할 것                                                                                                                                                                                | 처음부터 확장하지 않을 것                                                                                                                   |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 계정과 소유    | 기존 초기 관리자, lumia_migrator의 구조 설치/소유, lumia_app의 비소유 업무 접속. 새 두 역할은 비슈퍼유저·DB/역할 생성 등 관리 능력 없음, 상호 멤버십 없음                                | 별도 NOLOGIN 소유자·조회/정비 계정·역할 계층을 추가하지 않음                                                                                |
| 최초 고정 권한 | 새 lumiawiki DB의 PUBLIC CONNECT/TEMPORARY/CREATE 회수와 app/migrator CONNECT. public의 PUBLIC USAGE/CREATE 회수와 app USAGE·migrator USAGE/CREATE, migrator plpgsql USAGE 유지          | PUBLIC 권한 회수 자체를 되돌리지 않음. 현재 필요한 고정 SQL과 실제 동작을 검증하며 범용 권한 감사 엔진으로 확장하지 않음                    |
| 업무 표 권한   | 표를 구현할 때 그 업무에 필요한 app 표/열 권한만 해당 Flyway 변경과 함께 검토. migrator가 생성 객체를 소유하고 기존 P1 보호 유지                                                         | 전체 public의 일괄 DML·미래 표 DEFAULT PRIVILEGES·불필요한 시퀀스/관리 권한을 미리 부여하지 않음. 구체 목록은 실제 표/업무가 정해질 때 확인 |
| 비밀값 전달    | Git 제외 개인 루트 .env, DB 초기화에는 세 목적의 접속값, Gradle/Java에는 app/Flyway만 전달. B3의 기존 환경 유지·알려진 관리자 DB 변수 제외와 변수 우선순위 유지. 프런트에는 DB 값 미전달 | 개인 .env 생성/덮어쓰기, 전체 환경 허용 목록 재작성, Compose secrets/외부 비밀 관리 체계 도입은 하지 않음                                   |
| 비밀 SQL 보호  | Q-A 전용 인용·L-A 준비 트랜잭션 로그 제어·E-A 고정 진단과 B2의 SCRAM/로그 8개를 현재 경로의 한 구현 단위로 유지                                                                          | 비밀번호를 SQL에 전달하는 방식을 유지한 채 로그 보호만 제거하지 않음. 이미 정한 옵션을 개별 승인 질문으로 재발행하지 않음                   |

평문 비밀번호를 담은 CREATE ROLE은 서버 로그 등에 남을 수 있으므로 인용과 비밀 로그 보호는 별개다. B2는 모든 서비스에 보편적으로 필요한 설정 묶음이라는 뜻이 아니라, **현재 선택한 비밀번호 SQL 실행 경로를 유지하는 조건에서 함께 유지할 보호**다. 환경변수 방식의 컨테이너/프로세스 조회 노출, 같은 Spring 프로세스가 app/Flyway 두 비밀값을 갖는 한계도 그대로다. [PostgreSQL CREATE ROLE 주의사항](https://www.postgresql.org/docs/18/sql-createrole.html)

### 축소안의 최초 구동 흐름과 파일 범위

1. 개발자가 개인 .env의 필수값을 준비한다. 기존 실행기의 입력 검사로 누락을 거부하고 관리자/과거 접속값으로 자동 대체하지 않는다.
2. Compose로 DB를 시작한다. 빈 데이터 디렉터리의 최초 hook에서 기존 쉘/보조 SQL 한 쌍이 두 역할과 최초 권한을 한 트랜잭션으로 준비한다. 알려진 실패/미확인 상태에서는 서버 실행을 보류한다.
3. 최초 준비가 완료되고 DB TCP 준비를 확인한 뒤 기존 개발 실행기로 Spring을 시작한다. TCP healthcheck는 DB 접속 준비만 뜻하며 권한 전체 검증의 대체가 아니다.
4. Spring 기본 Flyway 기동에서 migrator로 승인한 마이그레이션을 적용하고, app으로 JPA 검증/업무 접속을 수행한다. B1 전용 FlywayMigrationStrategy와 매 기동 전수 검사/각 5초 계약을 만들지 않는다.
5. 정상 재시작은 기존 볼륨과 계정을 유지하고 기본 Flyway/JPA 경로를 이용한다. .env 변경으로 기존 계정 비밀번호를 바꾸거나 최초 hook을 다시 실행하는 방식은 사용하지 않는다.

공식 이미지는 빈 디렉터리에서만 최초 hook을 실행하며 중간 실패 후 재시작이 나머지 초기화를 이어서 수행하지 않는다. 이 때문에 실패한 최초 준비를 healthy/재시작만으로 완료 처리하지 않는 원칙은 유지한다. [PostgreSQL 공식 이미지 초기화](https://hub.docker.com/_/postgres)

구현 재개 시 파일 범위는 기존 채택 배치를 유지한다. db/bootstrap/10-prepare-roles.sh와 자동 실행 경로 밖 db/bootstrap/sql/prepare-roles.sql을 읽기 전용으로 연결하고 UTF-8/BOM 없음/LF로 준비한다. 기존 compose.yaml·.env.example·application-local.yaml·scripts/dev-api.mjs를 필요한 연결만 수정하며 공통 구조/업무 권한 SQL은 db/migration 단일 원천에 둔다. 새 구동 프레임워크·권한 검사 전용 모듈·복구 실행기를 추가하지 않는 안이다. 현재는 이 파일들을 생성/수정하지 않았다.

### 결론 A와 비교 대안 B

| 항목                    | A: 축소안 — 채택                                                                                                                                                           | B: 매 기동 전수 검사 — 비교 대안                                                                                |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| 검사 시점/수단          | 최초 설치·격리 검증에서 역할/권한·소유·정상/거부 동작을 확인하고 평소 기동은 Spring/Flyway/JPA 기본 실패 처리 사용                                                         | 매 기동 전 인증·역할 속성/상속·PUBLIC ACL·직접/유효 권한·소유 충돌을 자체 검사하고 각 5초/재시도 없음 계약 유지 |
| 추천 이유와 부담        | 별도 검사 코드·판정 규칙·설정 변경에 따른 유지 부담을 줄임. 현재 지정 관리자 중심 로컬 개발에 맞춤                                                                         | 권한 변화나 잘못된 접속을 마이그레이션 전에 더 넓게 드러내지만 검사 코드와 전용 실패 계약을 계속 관리해야 함    |
| 줄어드는 보장           | 과도한 권한/상속/소유 변화가 기동 시 자동 탐지되지 않을 수 있음. app 인증/권한이 잘못돼도 migrator의 마이그레이션이 먼저 성공할 수 있고 이후 app/JPA 시작이 실패할 수 있음 | 검사 대상 문제는 Flyway 호출 전에 중단하도록 설계. 기본 접속 오류 처리보다 넓은 검사 범위를 유지                |
| 실패/미확인 준비의 취급 | 실패 시 후속 시작 보류·상태 확인 뒤 복구라는 R-A 원칙은 운영 절차로 유지. 모든 독립 실행/재시작을 기계적으로 차단·검증하는 보장은 하지 않음                                | 기존 B1 전수 검사로 후속 시작을 제한. 모든 부분 초기화 상태의 식별을 별도 자동 복구로 확대하지는 않음           |

기동은 Spring/Flyway/JPA의 기본 경로를 사용한다. 기본 성공은 전체 권한의 정확성이나 최초 준비 이력의 성공을 증명하지 않는다. 알려진 실패/미확인의 후속 시작 보류는 운영 절차이며 모든 독립 실행의 기계적 차단을 보장하지 않는다. 역할/권한·인용/로그·비밀값 전달은 O/C/T·C-S-F/V/G/Q/L/E·B2/B3를 따른다. [Spring Boot 기본 실행·별도 접속](https://docs.spring.io/spring-boot/how-to/data-initialization.html)

### 나중으로 미룰 것과 실패 대응

매 기동 전체 권한/소유 상태 감사는 필요성이 생길 때 또는 공개 운영 경계를 설계할 때 재검토한다. 별도 조회/정비 역할·소유 역할 계층, 외부 secrets 공급·별도 마이그레이션 프로세스, 범용 기존 DB 이관/자동 복구 도구도 지금 첫 기능의 선행 조건으로 추가하지 않는다. 이들은 현재 미정/비채택인 확장 범위이며 새로 취소한 채택 결정이 아니다.

기존 DB를 계속 사용할 때 필요한 상태 확인·최소 이관 자체는 미루지 못한다. T-A의 최초 P1 설치 전 분리 조건을 유지하고, DB 조회 보류 해제 뒤 해당 환경의 실제 상태에 맞는 작은 이관안을 먼저 확인받는다. 빈 새 DB 검증에 기존 환경 전체 이관 도구 완성을 요구하지 않는다.

실패 대응은 입력 오류 정정, 최초 역할/권한 준비의 해당 트랜잭션 롤백, 기본 Flyway/JPA 오류에 따른 시작 실패, 상태 확인 뒤 명시 복구로 한정한다. 자동 볼륨 삭제·역할/암호 교체·Flyway clean/repair/baseline·재시도/자동 재실행을 넣지 않는다. 이미 성공한 마이그레이션이나 앞서 생성된 DB 디렉터리까지 전체 최초 구동이 한꺼번에 롤백됐다고 표시하지 않는다.

### 담당·필요 입력·확인 시점

| 남은 확인                    | 담당·필요 입력                                                                                                                             | 확인 시점                                                                                          |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| 기동 검사 범위               | 최초 설치 검증과 기본 기동. 매 기동 전수 검사·전용 5초 계약 없음                                                                           | 확정. 최초 구동 구현·격리 검증은 검증 기록 참조                                                             |
| 구체 업무 권한·파일/DDL 연결 | 001이 실제 표/업무·기존 배치에 맞는 한 구현안을 제시, 004가 후속 결합 검증                                                                 | 해당 구현 재개 뒤 파일 생성/적용 전 필요한 선택 확인. 이미 확정한 이름/옵션 재승인은 요구하지 않음 |
| 기존 환경 상태·대상별 이관   | 001의 허용된 DB 조회 결과·보존 대상, 사용자 확인                                                                                           | DB 조회 보류 해제 뒤, 해당 환경 최초 P1 설치 전                                                    |
| 최소 동작 검증               | 001의 빈 격리 환경 역할/권한 준비·migrator 설치/app 동작, 누락/잘못된 접속·실패/롤백·비밀 출력 제한·정상 재시작 사례. 004는 후속 결합 확인 | 최초 구동 구현·격리 검증 수행. 도메인 결합 검증은 해당 구현 후 |

최초 구동 파일과 app/Flyway 분리는 구현했다. 격리 DB의 동작 검증은 [검증 기록](task-001-bootstrap-verification.md#results)을 따른다. 개인 비밀값·기존 개발 DB/볼륨·실제 자료는 사용하지 않았다. D1~D4와 담당 미정은 [남은 결정](task-001-pending.md#remaining-review)을 따른다.

<a id="f4-bootstrap-integrated"></a>

## 최초 구동 통합 검토안 — 흐름·파일/설정·실패 복구

현재 구동 계약은 [A안](#startup-minimum-proposal)의 최초 설치 검증/기본 기동이다. 역할 분리·고정 권한·B2/B3를 적용하고 별도 매 기동 전수 검사나 전용 5초 계약은 두지 않는다. 아래에는 흐름·파일/설정·실패 대응과 검증 계획을 둔다.

이 문서는 최초 구동 계약과 실패 대응을 설명한다. 실제 구현은 아래 원천 파일, 검증 결과는 [최초 구동 검증](task-001-bootstrap-verification.md#results)을 따른다. 승인한 공통 구조의 구현·격리 검증·로컬 적용은 [생성 결과](task-001-creation.md#current)를 따른다. 실제 자료 작업은 계속 보류한다.

### 확정 규칙

| 범위                | 유지할 합의·적용 한계                                                                                                                                                                                                                                                                          |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 접속·소유           | O-A/C-A/T-A: 초기 관리자 `lumiawiki`, 소유/설치 `lumia_migrator`, 비소유 업무 `lumia_app`. 로컬 Spring 시작 시 별도 Flyway 접속. 실제 재개 뒤 최초 P1 마이그레이션 전에 분리. 두 업무/설치 역할의 제한·멤버십 금지도 유지. [소유·접속·시점](task-001-bootstrap-contract.md#f4-pk-role-binding) |
| 새 환경의 정상 흐름 | C-S-A: 개인 환경값 준비 → DB 시작 → 서버 시작. **빈 데이터 디렉터리 최초 생성에만** 역할/최소 권한 자동 준비. 기존 볼륨은 이 절차로 이관하지 않음. [자동 준비 범위](task-001-bootstrap-contract.md#f4-pk-bootstrap)                                                                            |
| 파일·전달           | F-A/V-A: 쉘과 자동 실행 경로 밖 보조 SQL의 읽기 전용 마운트, UTF-8/BOM 없음/LF. 개인 `.env`에서 DB에는 bootstrap/app/Flyway 쌍, Spring/Gradle/Java에는 app/Flyway 쌍만 전달. [파일·전달 계약](task-001-bootstrap-contract.md#f4-bootstrap-details)                                             |
| 최초 권한           | G-D-A/G-S-A: 대상 DB/public의 PUBLIC 권한 회수와 승인된 CONNECT/USAGE/CREATE만 명시 부여. 시스템/언어 기본 PUBLIC 권한 유지. 업무 표/열 DML·시퀀스·DEFAULT PRIVILEGES는 자동 포함하지 않음. [권한 목록](task-001-bootstrap-contract.md#f4-bootstrap-grants)                                    |
| SQL·로그·진단       | Q-A/L-A/E-A: psql 환경값 읽기/전용 인용, 최초 준비 트랜잭션의 로그 조건 적용·확인 뒤 비밀 SQL, 고정 단계·결과·psql 종료값만 공개. GUC 8개 등 구체 설정은 후속 B2로 설계 채택. [채택 범위](task-001-bootstrap-contract.md#f4-bootstrap-quoting-logs)                                            |
| 실패·복구           | R-A: 역할/최초 권한은 한 트랜잭션, 오류 시 롤백·중단. 실패/미확인 상태에서는 후속 Flyway/업무 서버를 진행하지 않음. 실제 상태 확인 뒤 검토된 명시 복구. 자동 skip/ALTER/비밀번호 교체·볼륨 삭제 없음                                                                                           |
| 구조·제품 자료      | 구조/PK guard와 승인할 표별 업무 권한은 `db/migration/`의 Flyway 원천. bootstrap에는 역할/최초 권한만 둠. JPA validate·기본 SQL init never 유지. 실제 게임 자료 조사·등록·교정은 계속 보류                                                                                                     |

### 정상 흐름

| 순서                   | 담당·처리                                                                                                              | 성공/중단 경계                                                                                                                                      |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. 개인 값 준비        | 개발자가 갱신될 `.env.example`을 참고해 개인 `.env`를 직접 준비. DB 이름/세 역할 이름은 합의값, 비밀번호는 개인 값     | 값을 요청·출력하거나 기존 개인 파일을 자동 덮어쓰지 않음. 필수값 누락·빈 값·예제 값·이름 불일치는 시작 전에 거부                                    |
| 2. DB 시작             | 기존 Compose 명령을 유지. 빈 디렉터리이면 공식 entrypoint가 initdb·초기 관리자/DB 생성 뒤 쉘을 호출                    | 이미지/볼륨/로컬 바인딩 유지. B1의 TCP healthcheck는 서버 접속 준비만 나타내며 역할/권한 수용을 대신하지 않음                                       |
| 3. 최초 역할 준비      | 쉘이 보조 SQL을 한 번 호출. 한 트랜잭션에서 사전 조건·로그 조건 확인 → 두 역할 생성 → 승인한 ACL 연결 → 사후 조건 확인 | B2의 설정/검사 실패나 이름 충돌은 비밀 SQL 전 또는 해당 트랜잭션에서 중단. 커밋 성공 뒤 고정 성공 진단만 공개                                       |
| 4. 서버 실행·입력 연결 | 기존 Node 실행기로 local 프로필·app/Flyway 접속값을 Java에 전달                                                        | B3에 따라 bootstrap/이전 관리자 접속값을 자식 환경에서 제외. DB 접속 실패를 관리자 계정으로 우회하지 않음                                           |
| 5. 기본 Flyway 기동    | Spring 기본 자동 구성으로 migrator의 승인된 마이그레이션 적용. B1 전용 사전 검사/클래스 없음                           | Flyway 실패는 기본 기동 오류로 처리. app 인증/권한 오류는 그 뒤 발견될 수 있으며 성공한 마이그레이션이 남을 수 있음                                 |
| 6. 구조 적용·기동 수용 | migrator로 승인된 Flyway 적용 → app의 JPA validate → 정상 서버 기동                                                    | 기존 F/I 원자 설치·충돌 중단을 유지. 업무 권한은 해당 표/기능의 승인 목록에 따라 별도 연결. 서버 정상 기동은 실제 게임 자료 준비 완료를 뜻하지 않음 |

빈 새 DB의 정상 사용 명령은 아래 두 개다. 기존 볼륨은 최초 hook이 다시 실행되지 않으므로 별도 상태 확인·이관 없이 전환하지 않는다. 프런트는 별도 터미널에서 실행하고 DB 비밀값을 전달하지 않는다.

```text
docker compose -p lumiawiki up -d --wait --wait-timeout 90 db
node --env-file=.env scripts/dev-api.mjs
```

최초 준비는 공식 entrypoint의 빈 디렉터리 분기에서 수행되므로 `.env` 변경/컨테이너 재시작으로 기존 역할을 고치지 않는다. 실제 `postgres:18.6`의 entrypoint/마운트/종료 동작은 재개 뒤 격리 검증한다. [공식 entrypoint의 초기화 분기·스크립트 처리](https://github.com/docker-library/postgres/blob/master/docker-entrypoint.sh)

<a id="f4-bootstrap-integrated-files"></a>

### 파일·설정과 관련 발췌

구현 원천은 [.env.example](../../../../../.env.example)·[Compose](../../../../../compose.yaml)·[쉘](../../../../../db/bootstrap/10-prepare-roles.sh)·[SQL](../../../../../db/bootstrap/sql/prepare-roles.sql)·[실행기](../../../../../scripts/dev-api.mjs)·[Spring local](../../../../../backend/src/main/resources/application-local.yaml)이다. 아래 발췌는 설명용이며 실행할 때 원천 파일을 사용한다.

| 파일                                                | 역할·관련 발췌                                                                                                                          | 적용 범위                                                                         |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `.env.example`                                      | 아래 3개 접속 쌍/공통 주소 템플릿으로 전환. 개인 `.env`는 개발자가 직접 갱신                                                            | 변수 이름/매핑은 합의. 예제 템플릿의 구체 내용도 B3로 설계 채택                    |
| `compose.yaml`                                      | 아래 명시 environment·두 bind mount·TCP healthcheck로 연결. 이미지/포트/볼륨/기존 검사 주기는 유지                                      | 경로/전달 범위는 합의. 마운트 구문·TCP 검사도 B1/B3로 설계 채택                    |
| `db/bootstrap/10-prepare-roles.sh`                  | 입력 검사 → 외부 SQL 한 번 실행 → 고정 진단·성공/실패 반환. 실행되거나 소싱되어도 부모 셸에 추적/옵션/변수를 남기지 않는 내부 실행 범위 | 파일 역할은 합의. 구체 실행 옵션/출력은 B2, 개행 설정은 B3로 채택                  |
| `db/bootstrap/sql/prepare-roles.sql`                | 아래 인용·역할·ACL 발췌와 사전/사후 검사, B2 로그/저장 암호화 설정. 역할/최초 권한만 포함                                               | Q-A·G 권한 목록은 합의. 본문 발췌·설정값은 B2로 설계 채택. 완성 본문은 구현 원천, 결과는 검증 기록 |
| `scripts/dev-api.mjs`                               | 기존 환경 검증을 새 app/Flyway 쌍으로 전환. 승인한 이름/필수값을 검사하고 알려진 관리자 환경값을 자식에서 제외                          | 목적별 전달은 합의. 제외 방식/기존 환경 보존도 B3로 설계 채택                      |
| `backend/src/main/resources/application-local.yaml` | 아래 app datasource와 명시 Flyway url/user/password. 비밀번호 기본값/이전 관리자 fallback 없음                                          | C-A 매핑은 합의. 구체 YAML도 B3로 설계 채택                                        |
| 별도 시작 검사 클래스                               | B1 전용 FlywayMigrationStrategy/전수 검사 클래스는 초기 구현 대상에서 제외                                                              | 기본 Flyway 기동과 최초 설치/격리 검증 사용. 새 완료 표/마커·검사 프레임워크 없음  |
| `.gitattributes`·`README.md`·관련 검증              | bootstrap 두 파일에 국소 LF 설정, 실행 안내를 새 변수/실패 분기로 수정. 기존 도구/격리 검증을 연결                                      | B3의 국소 설정 채택. 국소 LF·안내·격리 검증 반영                   |

`.env.example`의 검토용 내용이다. 실제 비밀번호는 없으며 길이·문자 집합을 새로 제한하거나 값을 trim/변환하는 정책은 제안하지 않는다. NUL은 환경값으로 전달할 수 없으며 특수 문자·개행·UTF-8의 공통 전달 가능 범위는 합성 값으로 검증한다. 불일치가 확인되면 값을 몰래 변환하지 않고 수정안을 제시한다.

```dotenv
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=lumiawiki
DB_BOOTSTRAP_USERNAME=lumiawiki
DB_BOOTSTRAP_PASSWORD=CHANGE_ME
DB_APP_USERNAME=lumia_app
DB_APP_PASSWORD=CHANGE_ME
DB_FLYWAY_USERNAME=lumia_migrator
DB_FLYWAY_PASSWORD=CHANGE_ME
```

Compose의 관련 설정 초안이다. 보조 SQL은 자동 실행 디렉터리 밖에 두고, bind source가 없으면 디렉터리를 자동 생성하지 않고 실패한다.

```yaml
services:
  db:
    environment:
      POSTGRES_DB: ${DB_NAME:?DB_NAME is required}
      POSTGRES_USER: ${DB_BOOTSTRAP_USERNAME:?DB_BOOTSTRAP_USERNAME is required}
      POSTGRES_PASSWORD: ${DB_BOOTSTRAP_PASSWORD:?DB_BOOTSTRAP_PASSWORD is required}
      DB_APP_USERNAME: ${DB_APP_USERNAME:?DB_APP_USERNAME is required}
      DB_APP_PASSWORD: ${DB_APP_PASSWORD:?DB_APP_PASSWORD is required}
      DB_FLYWAY_USERNAME: ${DB_FLYWAY_USERNAME:?DB_FLYWAY_USERNAME is required}
      DB_FLYWAY_PASSWORD: ${DB_FLYWAY_PASSWORD:?DB_FLYWAY_PASSWORD is required}
    volumes:
      - postgres_data:/var/lib/postgresql
      - type: bind
        source: ./db/bootstrap/10-prepare-roles.sh
        target: /docker-entrypoint-initdb.d/10-prepare-roles.sh
        read_only: true
        bind:
          create_host_path: false
      - type: bind
        source: ./db/bootstrap/sql/prepare-roles.sql
        target: /opt/lumia-bootstrap/prepare-roles.sql
        read_only: true
        bind:
          create_host_path: false
    healthcheck:
      test:
        - CMD-SHELL
        - pg_isready -h 127.0.0.1 -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"
```

`${...:?}`는 빈 값/누락만 거부하므로 쉘·실행기의 예제 값/이름 검사까지 대신하지 않는다. healthcheck는 임시 Unix socket 서버를 정상 TCP 서버로 혼동하지 않으려는 B1 채택 설계다. 역할/ACL의 정확성은 최초 설치/격리 검증과 필요한 실제 복구 확인으로 다루며 매 시작 전수 검사를 추가하지 않는다. [Compose bind mount 구문](https://docs.docker.com/reference/compose-file/services/#volumes) · [pg_isready의 검사 한계](https://www.postgresql.org/docs/18/app-pg-isready.html)

Spring local 설정의 관련 부분 초안이다. common의 Flyway 위치/JPA validate/SQL init never와 기존 Swagger·로그 설정은 유지한다.

```yaml
spring:
  datasource:
    url: jdbc:postgresql://${DB_HOST}:${DB_PORT}/${DB_NAME}
    username: ${DB_APP_USERNAME}
    password: ${DB_APP_PASSWORD}
  flyway:
    url: jdbc:postgresql://${DB_HOST}:${DB_PORT}/${DB_NAME}
    user: ${DB_FLYWAY_USERNAME}
    password: ${DB_FLYWAY_PASSWORD}
```

Boot의 기본 Flyway 실행과 전용 url/user/password 설정을 사용한다. 별도 FlywayMigrationStrategy 검사는 만들지 않는다. 실제 접속은 격리 검증에서 확인하며 test 프로필 격리는 유지한다. [Spring Boot 기본 Flyway 실행·전용 접속](https://docs.spring.io/spring-boot/how-to/data-initialization.html)

### 쉘·SQL 본문과 최초 설치 검증

쉘은 비밀값 처리 전부터 xtrace/원문 출력이 꺼진 내부 범위에서 실행한다. 초기화용 Unix socket과 초기 관리자/DB를 명시하고, 다음 옵션으로 보조 SQL을 한 번 호출하는 B2 채택 설계다. 비밀번호를 인자에 넣지 않는다. 입력 검사는 호출 전에 수행하고 psql 원문 stdout/stderr는 파일 없이 폐기한다. 아래 호출만 단독 실행할 수 있는 완성 쉘로 제공하는 것은 아니다.

```text
psql -X --no-password --quiet --set=ON_ERROR_STOP=1 --single-transaction
     --host=/var/run/postgresql --username=<POSTGRES_USER> --dbname=<POSTGRES_DB>
     --file=/opt/lumia-bootstrap/prepare-roles.sql
```

`-X`로 psqlrc를 배제하고 `--single-transaction`이 트랜잭션을 담당하므로 보조 SQL에 별도 BEGIN/COMMIT을 중복하지 않는다. echo/trace/원문 로그 파일을 추가하지 않는다. 셸은 입력 실패면 `stage=input_check result=failed`, psql 완료면 `stage=role_prepare result=ok|failed psql_exit=0|1|2|3`의 허용된 고정 값만 출력하는 채택 설계다. 비정상 종료를 0으로 바꾸지 않으며 코드가 없으면 `stage=role_prepare result=unknown`으로 중단한다. 다른 종료값은 숫자를 그대로 공개해 원문 오류를 대체하지 않고 `unknown`으로 분류한다. API 오류/LW001과 연결하지 않는다. [psql 옵션·종료 상태](https://www.postgresql.org/docs/18/app-psql.html)

다음 SQL은 **B2를 포함한 본문 발췌**다. 필수값/고정 이름은 쉘에서 확인하고, SQL에서는 현재 관리자/DB·UTF-8 인코딩·두 역할의 미존재·허용한 표준 로그 경로를 비밀 SQL 전에 검사한다. 트랜잭션 시작 때 적용되는 표본 추출을 고려해 변경 전 `log_transaction_sample_rate=0`도 요구하고 다르면 중단하는 채택 설계다. 트랜잭션 안에서 값을 0으로 바꾸기만 하면 이미 결정된 표본 상태도 취소된다고 판단하지 않는다. SET LOCAL 뒤 모든 설정값을 `current_setting`으로 대조하고 하나라도 불일치하면 오류로 중단한다. 아래 역할/ACL 뒤에도 역할 속성·멤버십/유효 권한/PUBLIC ACL을 검사해 불일치 시 같은 트랜잭션을 롤백한다. 이 사전/사후 검사를 생략한 실행 파일로 사용하지 않는다.

```sql
\getenv db_name POSTGRES_DB
\getenv app_user DB_APP_USERNAME
\getenv app_password DB_APP_PASSWORD
\getenv migrator_user DB_FLYWAY_USERNAME
\getenv migrator_password DB_FLYWAY_PASSWORD

-- B2 설계 채택: 사전 조건 검사 후, 비밀 SQL 전에 적용/재확인.
SET LOCAL log_statement = 'none';
SET LOCAL log_min_duration_statement = -1;
SET LOCAL log_min_duration_sample = -1;
SET LOCAL log_transaction_sample_rate = 0;
SET LOCAL log_min_error_statement = 'panic';
SET LOCAL log_min_messages = 'panic';
SET LOCAL log_parameter_max_length = 0;
SET LOCAL log_parameter_max_length_on_error = 0;
SET LOCAL password_encryption = 'scram-sha-256';

CREATE ROLE :"migrator_user" LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
  NOREPLICATION NOBYPASSRLS PASSWORD :'migrator_password';
CREATE ROLE :"app_user" LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
  NOREPLICATION NOBYPASSRLS PASSWORD :'app_password';

REVOKE CONNECT, TEMPORARY, CREATE ON DATABASE :"db_name" FROM PUBLIC;
GRANT CONNECT ON DATABASE :"db_name" TO :"app_user", :"migrator_user";
REVOKE USAGE, CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO :"app_user";
GRANT USAGE, CREATE ON SCHEMA public TO :"migrator_user";
GRANT USAGE ON LANGUAGE plpgsql TO :"migrator_user";
```

실행에는 사전·사후 검사를 포함한 구현 SQL 전체를 사용한다. B2는 로그값 8개와 서버 SCRAM 저장 방식 등을 묶어 채택했으며 개별 설정값 선택을 반복하지 않는다.

로그 설정은 준비 트랜잭션에만 적용되고 종료 뒤 원래 상태로 돌아간다. ordinary SQL/error/duration/sample 경로와 바인딩 값을 함께 다루는 채택 설계이며 이 구간의 상세 진단이 줄어든다. PANIC·관리자 활동 조회·덤프·추가 감사/외부 수집기까지 비노출로 보장하지 않는다. 비표준 경로/조건 미확인은 비밀 SQL 전에 중단·반환하며 새 감사 기능을 초기 구동에 추가하지 않는다. 서버의 SCRAM 저장은 SQL 처리 순간의 원문 비밀번호를 없애는 수단이 아니다. [로그 설정](https://www.postgresql.org/docs/18/runtime-config-logging.html) · [SET LOCAL 범위](https://www.postgresql.org/docs/18/sql-set.html) · [비밀번호 저장 방식](https://www.postgresql.org/docs/18/runtime-config-connection.html#GUC-PASSWORD-ENCRYPTION)

B1의 검증은 최초 설치/격리 검증과 필요한 이관 수용에서 수행한다. 매 시작 전수 검사나 전용 5초 계약을 만들지 않는다.

- app/Flyway의 합의한 DB/역할 인증과 역할 제한·멤버십/권한·소유를 최초 설치 검증에서 대조한다.
- migrator의 구조 적용, app의 승인한 업무 동작과 금지된 구조/PK 변경 거부를 해당 마이그레이션/업무의 검증에 연결한다.
- 잘못된 입력/접속과 Flyway/JPA 실패, 정상 재시작·비밀값 전달을 확인한다. app 오류 전에 Flyway가 성공할 수 있으므로 성공한 변경까지 자동 롤백됐다고 표시하지 않는다.
- 알려진 bootstrap 실패/미확인은 운영 절차로 후속 시작을 보류하고 상태 확인/명시 복구 뒤 진행한다. 기본 기동 성공만으로 과거 준비 성공이나 모든 권한의 정확성을 증명하지 않는다.

<a id="f4-bootstrap-integrated-decisions"></a>

### B1~B3의 결론과 비교 대안

B1은 최초 설치 검증/기본 기동을 사용하고 B2/B3는 아래 계약을 따른다. Java 자식 환경은 기존 환경을 유지하며 알려진 관리자 DB 변수를 제외한다. 전체 환경 허용 목록 재구성은 비교 대안이다. 새 판단은 대안과 이유를 먼저 확인하고 승인한 공통 구조의 구현·격리 검증·로컬 적용은 [생성 결과](task-001-creation.md#current)를 따른다. 실제 자료 작업은 계속 보류한다.

| 항목                        | 확정·이유                                                                                                                                                                                                                                                                                                                           | 비채택 비교 대안·부담                                                                                                                                                                                                                         |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| B1. 최초 검증·기동          | 결론: 최초 설치/격리 검증과 Spring/Flyway/JPA 기본 기동. 전용 FlywayMigrationStrategy·매 기동 전수 검사·각 5초 계약은 제외. app 오류 전에 Flyway가 성공할 수 있음을 수용                                                                                                                                                            | 매 기동 전수 검사 또는 별도 명령 검사. 더 넓은 사전 탐지가 가능하지만 전용 검사·호출 경로·실패 계약의 유지 부담이 있어 초기 구현에서 제외                                                                                                     |
| B2. 최초 SQL 실행·비밀 처리 | **위 고정 psql 옵션·8개 SET LOCAL 로그값/재확인·서버 SCRAM 저장·고정 진단 형식**을 하나의 기술 설계로 채택. 기존 Q/L/E와 R-A를 직접 연결하고 추가 비밀번호 변환 도구 없이 현재 두 역할을 검토하기 쉬움. 비밀번호에 새 길이/문자 제한·자동 변환은 추가하지 않음                                                                      | 로그 적용을 현재 상태별로 계산하거나 클라이언트에서 SCRAM 표현을 먼저 만들어 SQL로 전달. 전자는 변경 설정 수를 줄이지만 분기/검증이 늘고, 후자는 SQL의 평문 노출을 줄이지만 별도 생성 수단·값/검증값 취급 검증이 필요. 같은 Q/L/E 경계는 유지 |
| B3. 파일·환경 연결          | **제시한 Compose/Spring/예제 템플릿과 국소 LF, 기존 환경을 복사하되 알려진 관리자 DB 변수 제거**. `DB_BOOTSTRAP_USERNAME/PASSWORD`, 이전 `DB_USERNAME/PASSWORD`, `POSTGRES_USER/PASSWORD`, `PGUSER/PGPASSWORD`를 Java/Gradle 자식에서 제외하고 app/Flyway만 명시 연결. PATH/JAVA_HOME 등 일반 환경을 보존해 기존 실행기 영향을 줄임 | Java 자식 환경 전체를 허용 목록으로 새로 구성. 제외 누락을 줄일 수 있지만 Windows/Java/프록시/개발 환경의 필요한 변수를 더 수집·검증해야 함. 어느 안도 개인 `.env` 전체를 프런트에 전달하지 않음                                              |

확정한 B3는 Node/Compose의 기존 환경변수 우선순위를 임의 변경하지 않는다. 개인 `.env`와 터미널의 덮어쓰기가 다르면 입력 검증·해당 연결의 기본 인증 오류로 드러내며 값은 출력하지 않는다. 매 시작 전체 역할/권한 검사를 약속하지 않는다. 알려지지 않은 모든 환경 비밀을 자동 탐지한다는 보장은 하지 않는다. bootstrap 파일의 국소 개행 채택 설계는 `db/bootstrap/*.sh text eol=lf`, `db/bootstrap/sql/*.sql text eol=lf`다.

<a id="f4-bootstrap-integrated-recovery"></a>

### 실패·복구 — R-A를 적용하는 하나의 절차

실패 단계와 실제 반영 범위를 먼저 구별한다. 다음은 복구 방향의 문서 초안이며 관리자 SQL·삭제·재실행을 미리 허용하는 명령 목록이 아니다.

| 관찰 상태                         | 남을 수 있는 상태·중단 범위                                                                                | 복구 검토/재개 조건                                                                                                                                                                         |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 입력/마운트 실패                  | 해당 준비가 아직 쓰기 전인지 확인. 이미지 초기화가 시작됐으면 디렉터리/초기 관리자는 남을 수 있음          | 입력/파일 연결만 고친 뒤, 비어 있는 새 환경인지 부분 초기화 환경인지 먼저 구별. 후자는 아래 상태 확인 절차를 거침                                                                           |
| 역할/권한 SQL 실패                | 해당 트랜잭션의 역할/ACL 변경은 롤백. initdb·초기 관리자·DB 디렉터리는 남을 수 있음. 후속 Flyway/서버 중단 | 보류 해제 뒤 승인된 관리자 조회로 두 역할·대상 ACL을 확인. 둘 다 미생성이며 사전 조건이 맞으면 같은 준비 단위의 명시 재실행안을 검토. 일부 존재/충돌이면 필요한 차이만 별도 복구안으로 확인 |
| 커밋 근처 단절/종료 불명          | 성공·롤백을 단정하지 않음. 컨테이너 재시작/healthy로 복구 완료 처리하지 않음                               | 실제 역할/ACL을 확인하고 완료 상태인지 부분/충돌인지 구별한 후 명시 복구/재개 판단. blind 재실행·비밀번호 자동 교체 없음                                                                    |
| Spring 기본 기동의 입력/접속 실패 | 해당 기본 입력/접속 오류로 기동 실패. app 오류 전에 migrator의 마이그레이션이 이미 성공했을 수 있음        | 입력 정정 또는 허용된 상태 확인 뒤 명시 복구. 권한/소유 변화 전체의 기동 시 자동 탐지를 보장하지 않으며 기존 DB는 대상별 이관안을 검토                                                      |
| Flyway/JPA 검증 실패              | 실패한 마이그레이션 단위의 원자성은 기존 I-A 계약대로 확인. 앞서 성공한 다른 마이그레이션은 남을 수 있음   | 원인·Flyway 이력/소유·실제 스키마를 대조하고 수정/재개안 확인. 자동 clean/repair/baseline·기존 성공 SQL 덮어쓰기·볼륨 삭제로 해결하지 않음                                                  |
| 정상 기동 뒤 재시작               | 기존 볼륨의 최초 준비 스크립트는 다시 실행되지 않음                                                        | 기본 Flyway/JPA 기동 사용. 알려진 실패/미확인은 운영 절차로 확인/복구 뒤 진행. 재시작이 자료 등록·권한 확대·복구 실행을 허용하지 않음                                                       |

### 담당·필요 입력·결정 시점과 검증

| 남은 범위                                                     | 담당·필요 입력                                                                                                                     | 결정/확인 시점                                                                                              |
| ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| B1~B3 채택 설계의 구현/검증                                   | Task 43-001이 채택 계약에 맞춰 구현/검증 준비, 004는 접속/후속 업무 결합 검증 담당. 현재 코드/합의·공식 문법·합성 검증 사례가 입력 | B1~B3 선택은 완료. 최초 구동 구현·격리 검증은 검증 기록 참조. 새 업무 판단은 먼저 확인                        |
| 실제 DB 재개·현재 환경 이관/사건 복구                         | 001이 허용된 조회 범위/보존·차이·복구안을 준비, 004가 후속 시작/결합 확인. 실제 상태는 재개 승인 뒤에만 확인                       | 통합안 수용과 별도로 DB 보류 해제 필요. 현재 환경의 실제 이관/복구는 대상별 검토 뒤, 최초 P1 설치 전에 준비 |
| 공통 표 전체 DDL·버전/파일·업무 권한·요청/예외·다른 Task 미정 | 각 담당 Task가 기존 미정 표의 입력/책임을 유지                                                                                     | 최초 역할 준비와 분리해 해당 구현 전 확인. 묶음이 도메인 설계/자료 사실·운영 배포를 자동 확정하지 않음      |

재개 후 확인할 사례는 기존 001/004 계획을 보완하며 대체하지 않는다. 현재는 아래 동작 검증을 수행하지 않았다.

1. 빈 격리 환경에서 두 명령으로 역할/ACL 최초 준비/검증 → 기본 migrator Flyway → app JPA/기동이 연결되고 관리자 값이 Java/Gradle/프런트로 넘어가지 않음.
2. 기존/부분 초기화 볼륨·입력/마운트 누락·잘못된 접속과 마이그레이션 실패에서 해당 실패/반영 범위를 구별하고 자동 역할 보정은 하지 않음. 최초 검증에서 권한/소유를 대조하고 알려진 실패는 운영 절차로 보류. app 오류 전에 Flyway 성공이 가능한 A의 한계도 확인.
3. 인용 문자·달러·역슬래시·공백·한글·개행 등 합성 입력의 값 보존과 정상 인증, 예상 SQL 실패/단절의 로그·출력 제한·롤백 범위를 확인. 비밀 SQL 전에 로그 조건이 맞고 트랜잭션 뒤 원상태이며 원문 임시 파일이 없음.
4. Windows checkout의 LF/두 hook 실행 방식·SQL 단일 호출·비소유 역할 권한·설정 누락 시 관리자 fallback 없음·IDE/실행기의 기본 기동·정상 재시작을 확인. test 프로필 격리를 보존.

검증 범위는 B1~B3의 기동/실패·비밀값 전달·격리 동작이다. 문서 SQL 발췌나 공식 문서 확인을 실제 적용·비노출·복구 성공의 근거로 사용하지 않는다.
