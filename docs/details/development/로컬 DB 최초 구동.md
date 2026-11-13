# 로컬 DB 최초 준비·권한·비밀값

<a id="current"></a>

[개발 기준](<../../개발 기준.md#current>)의 주제별 상세다. 기준 채택과 실제 구현/검증·자료/DB 작업 재개를 구별한다.

<a id="pk-guard-role-install"></a>

## P1-O·C·T의 소유·접속·분리 적용 계약

로컬 접속은 migrator의 소유/설치와 app의 비소유 업무로 분리하고 최초 P1 설치 전에 준비한다(O-A/C-A/T-A). 새 환경용 파일은 구현했으며 역할·권한과 접속 분리를 격리 DB에서 검증했다. [검증 기록](../../../work/records/phase-001/issue-43/artifacts/task-001-bootstrap-verification.md#current)을 따른다. 실제 자료·기존 개발 DB/볼륨과 공통 도메인 표 구현은 보류한다.

| 주체                                | 확정한 소유·능력 경계                                                                                                                                                                        |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `lumia_migrator LOGIN`              | 공용 PK 보호 함수·여섯 공통 표·종속 IDENTITY 시퀀스를 소유하고 Flyway 설치를 수행. DB CONNECT·public USAGE/CREATE와 필요한 언어/설치 능력을 연결. DB/public 스키마 전체 소유는 요구하지 않음 |
| `lumia_app LOGIN`                   | 비소유 업무 접속. DB CONNECT·public USAGE와 승인한 업무의 표/열 DML만 부여. 소유/구조 관리 역할의 직접·간접 멤버십/SET ROLE·유효 public CREATE·표 TRIGGER·TRUNCATE·권한 재부여 능력 없음     |
| 초기 관리자 — 현재 `lumiawiki` 유지 | 역할 생성·필요한 최초 권한 연결을 담당하는 목적. 일반 앱/Flyway 접속에서 제외하며 기존 역할/DB/스키마를 자동 삭제·이름 변경·이관하지 않음                                                    |

migrator와 app 모두 NOSUPERUSER·NOCREATEDB·NOCREATEROLE·NOREPLICATION·NOBYPASSRLS로 두고 두 역할 사이 멤버십을 만들지 않는다. migrator는 소유 객체의 구조 변경 능력을 가지므로 PK guard가 설치자 자체까지 제한한다는 보장을 하지 않는다. 별도 NOLOGIN 소유 역할·SET ROLE 연결 초기화는 채택하지 않는다. 조회/예외 정비의 실제 역할·권한, 업무 표/열 DML·시퀀스 권한·기존 관리 표 이관·DEFAULT PRIVILEGES는 별도 확인한다.

C-A는 로컬 Spring 시작 시 Flyway를 유지하고 일반 서비스/JPA는 app, Flyway 전용 datasource는 migrator로 접속한다. `DB_BOOTSTRAP_USERNAME/PASSWORD`는 Compose 초기 관리자, `DB_APP_USERNAME/PASSWORD`는 spring.datasource, `DB_FLYWAY_USERNAME/PASSWORD`는 spring.flyway.user/password에 연결하는 이름/매핑을 확정한다. 호스트·포트·DB 이름을 공유하되 Flyway url/user/password를 명시하고 필수값 누락은 실행 입력에서 거부한다. Spring 실행에는 app/Flyway 쌍만 전달하고 bootstrap 값은 전달하지 않는다. 같은 Spring 프로세스가 두 비밀값을 보유한다는 한계를 유지하며 운영/배포의 실행·비밀값 공급은 별도다.

T-A에 따라 실제 DB 작업 보류 해제·필요 계약 확인 뒤, 최초 P1 보호 함수/표 마이그레이션 전에 역할·필요 권한·접속 분리를 준비한다. 기존 역할/객체·Flyway 관리 표의 소유/권한은 재개 후 확인하고 필요한 대상별 이관/복구를 먼저 확인받는다. 신규 함수/표는 선택한 소유자로 I-A 원자 설치하며 비소유 업무 접속에서 R-A/PK 보호를 검증한다.

빈 DB의 Compose 최초 초기화는 lumia_migrator·lumia_app과 최소 권한을 자동 준비한다(C-S-A). 기본 흐름은 개인 환경값 준비 → DB 시작 → 서버 시작이다. 역할 생성용 수동 SQL/별도 설정 명령을 일상 최초 구동에 추가하지 않는다. 파일/전달/실패는 F/V/R, 권한은 G, 인용/로그/기동은 Q/L/E·B1~B3를 따른다. 구조/보호 장치와 표별 업무 권한은 Flyway의 단일 원천으로 관리하며 전체 public 업무 권한·DEFAULT PRIVILEGES·게임 자료 등록은 포함하지 않는다. 현재 구현은 app/Flyway 접속을 분리한다. 기존 개발 DB의 실제 상태 확인·이관은 수행하지 않았다.

<a id="bootstrap-files-values-recovery"></a>

## C-S-F·V·R의 최초 준비 설계 계약

최초 파일 배치·대상별 전달·역할 준비의 실패/복구는 아래 F-A/V-A/R-A 계약을 따른다. 구현은 [쉘](../../../db/bootstrap/10-prepare-roles.sh)·[보조 SQL](../../../db/bootstrap/sql/prepare-roles.sql)·[Compose](../../../compose.yaml)·[실행기](../../../scripts/dev-api.mjs)를 따른다. 실제 자료·기존 개발 DB/볼륨과 공통 도메인 표 구현은 보류한다.

| 항목                | 채택 범위                                                                                                                                                                                                                                                         |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C-S-F-A 파일 배치   | `db/bootstrap/10-prepare-roles.sh` → `/docker-entrypoint-initdb.d/10-prepare-roles.sh`, `db/bootstrap/sql/prepare-roles.sql` → `/opt/lumia-bootstrap/prepare-roles.sql`에 각각 읽기 전용 마운트. 쉘이 보조 SQL을 한 번 호출하며 보조 SQL은 자동 실행 경로 밖에 둠 |
| C-S-V-A 비밀값 전달 | Git 제외 개인 루트 `.env`를 값 원천으로 유지. DB 최초 준비에는 bootstrap/app/Flyway 쌍을 명시 전달하고 Spring/Gradle/Java에는 app/Flyway 쌍만 전달. bootstrap/기타 관리자 DB 비밀값을 통째로 상속하거나 프런트에 전달하지 않음                                    |
| C-S-R-A 실패/복구   | 두 역할·승인할 최초 권한 준비를 한 psql 트랜잭션으로 처리하고 SQL 오류 시 롤백/실패 종료. 역할 충돌을 skip/ALTER/비밀번호 교체로 임의 해소하지 않음. 실제 상태 확인 뒤 개별 명시 복구 계획을 확인받음                                                             |

F-A bootstrap 파일은 UTF-8·BOM 없음·LF 방향으로 준비한다. 국소 개행 설정·실행/소싱 호환·쉘/SQL 본문과 마운트 구문은 구현 전 대조한다. 역할/최초 권한 준비 SQL만 bootstrap 원천으로 구별하고 구조/보호 장치·승인한 표별 업무 권한의 Flyway 원천에 복사/포함하지 않는다.

V-A는 로컬 개발의 기존 환경값 흐름을 유지하는 선택이며 컨테이너/프로세스 환경을 조회할 수 있는 주체에는 값이 노출될 수 있다는 한계를 유지한다. 실제 개인 `.env`를 자동 생성/덮어쓰거나 값을 문서/Git/출력에 넣지 않는다. 인용 방식·로그 제어 범위·최소 진단은 [Q-A·L-A·E-A](#bootstrap-quoting-log-contract)를 따르고 구체 로그값/진단·파일/환경 연결은 [B1~B3 채택 계약](#bootstrap-startup-contract)을 따른다. 구현·검증 범위는 새 격리 DB이며 운영 비밀값 공급은 이 결정에 포함하지 않는다.

R-A의 롤백은 역할/최초 권한 준비 단위에 한정한다. 앞선 initdb·초기 관리자·DB/디렉터리는 남을 수 있고 커밋 근처 연결 끊김은 실제 상태 확인 전 성공/롤백을 단정하지 않는다. 알려진 준비 실패/미확인 상태에서는 운영 절차로 후속 Flyway/업무 시작을 보류하고 상태 확인/명시 복구 뒤 진행한다. 확정 A에 따라 매 시작의 전수 검사/각 5초 계약은 제외하고 최초 설치/격리 검증과 기본 Flyway/JPA 기동 오류 처리를 사용한다. TCP healthcheck/기동 성공이 전체 권한이나 과거 준비 성공을 증명하지 않는다. 자동 볼륨/역할 삭제·비밀번호/권한 교체는 넣지 않는다.

[상세·담당/입력/시점·검증](../../../work/records/phase-001/issue-43/artifacts/task-001-bootstrap-contract.md#f4-bootstrap-details)을 따른다. 최초 권한은 [G-D-A/G-S-A](#bootstrap-initial-privileges), 인용/로그·파일/기동은 Q/L/E·B1~B3를 따른다. 업무 DML/시퀀스·현재 환경 이관/개별 복구는 해당 범위에서 확인한다. 실제 자료·기존 개발 DB/볼륨과 공통 도메인 표 구현은 보류한다.

<a id="bootstrap-initial-privileges"></a>

## C-S-G-D·G-S의 최초 권한 계약

새 lumiawiki DB의 최초 권한은 G-D-A/G-S-A의 아래 목록을 따른다. 역할·권한은 격리 DB에서 검증했으며 기존 환경의 조회·이관은 수행하지 않았다.

| 대상            | PUBLIC에서 회수            | lumia_app 직접 부여 | lumia_migrator 직접 부여 |
| --------------- | -------------------------- | ------------------- | ------------------------ |
| DB `lumiawiki`  | CONNECT, TEMPORARY, CREATE | CONNECT             | CONNECT                  |
| 스키마 `public` | USAGE, CREATE              | USAGE               | USAGE, CREATE            |
| 언어 `plpgsql`  | 기존 PUBLIC 권한 유지      | 별도 직접 부여 없음 | USAGE                    |

직접 부여에는 WITH GRANT OPTION·ADMIN OPTION을 추가하지 않으며 DB/public 소유 이전이나 새 역할 멤버십을 만들지 않는다. 초기 관리자의 기존 소유/슈퍼유저 능력은 유지한다. 언어·시스템 스키마·기본 자료형의 PUBLIC 권한은 그대로 두므로 app의 언어 USAGE 등 기본 유효 능력까지 모두 제거한 것으로 설명하지 않는다. 소유·직접 부여·PUBLIC·멤버십/SET ROLE 경로의 실제 유효 권한을 대조한다.

최초 app/migrator에는 DB CREATE·TEMPORARY를 주지 않는다. migrator의 CREATE는 기존 public 스키마 안의 객체 생성 능력이다. public 스키마·PL/pgSQL 누락이나 다른 스키마 생성 요구가 있으면 자동 설치/권한 확대 대신 중단해 확인받는다. 실제 Flyway 스키마/생성 설정과 시작 전 검사는 별도다.

위 부여와 PUBLIC 회수는 C-S-R-A의 두 역할/최초 권한 준비 트랜잭션에 포함한다. 롤백은 해당 역할/ACL 준비 단위이며 선행 DB/스키마와 기존 기본 ACL의 보존·복원을 구별한다. 초기 준비의 임시 표 생성 불허가 필요한 업무/도구와 충돌하면 격리 검증 근거와 필요한 범위를 먼저 제시하며 권한을 자동 추가하지 않는다.

표/열 업무 DML·시퀀스·전체 public 객체 권한·DEFAULT PRIVILEGES는 이 계약에 포함하지 않는다. migrator가 새 함수/표를 생성한 뒤 소유자로 갖는 설치 능력과 guard의 PUBLIC EXECUTE 회수는 기존 O-A·R-A·I-A를 따른다. 다른 DB/postgres/template·HBA·기존 환경의 권한/소유를 자동 변경하거나 접속이 모두 차단됐다고 보고하지 않는다.

[권한 상세·담당/입력/시점·검증](../../../work/records/phase-001/issue-43/artifacts/task-001-bootstrap-contract.md#f4-bootstrap-grants)을 따른다. SQL 인용/로그/진단은 [Q-A/L-A/E-A](#bootstrap-quoting-log-contract)와 [B1~B3](#bootstrap-startup-contract)에 정의한다. 업무 DML/시퀀스·현재 환경 이관/개별 복구는 해당 범위에서 확인한다. 실제 자료·기존 개발 DB/볼륨과 공통 도메인 표 구현은 보류한다.

<a id="bootstrap-quoting-log-contract"></a>

## C-S-Q·L·E의 SQL 인용·로그·진단 계약

최초 권한 SQL은 Q-A의 전용 인용, L-A의 트랜잭션 로그 제어, E-A의 고정 진단을 사용한다. 구현은 이 계약을 따르며 개인 비밀값·기존 DB/로그는 조회하지 않았다.

| 항목              | 채택 범위                                                                                                                                                                                                                                  |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| C-S-Q-A 정적 인용 | 보조 SQL이 psql의 `\getenv`로 환경값을 읽고 DB/역할 이름은 `:"name"`, 비밀번호는 `:'password'`로 인용. 채택 이름/필수값을 역할 쓰기 전에 확인하고 권한·명령문·PUBLIC 등은 고정 구문으로 유지                                               |
| C-S-L-A 로그 범위 | 초기 관리자 연결의 최초 준비 트랜잭션에서 비밀 SQL 전에 SET LOCAL로 필요한 로그 조건을 적용·확인. 실패/미확인이면 역할 생성 전에 중단. 커밋/롤백 뒤 세션 기본 설정 복원. DB 전역·업무 연결의 로그 정책과 app/migrator의 권한을 넓히지 않음 |
| C-S-E-A 최소 진단 | 셸/psql의 원문 SQL·오류·stdout/stderr를 출력/로그/첨부/임시 파일로 남기지 않고 검토한 고정 단계·결과·psql 종료값만 보고. 원문을 출력한 뒤 가리거나 SQLSTATE 모드의 원문 fallback을 그대로 통과시키지 않음                                  |

Q-A는 비밀번호를 명령행 인자·비밀번호 포함 URI·셸 문자열 치환·생성 SQL 파일에 삽입하는 방식이 아니다. 식별자/문자열 인용을 구별하고 이미 인용된 SQL/달러 본문 안의 변수 치환을 가정하지 않는다. 누락 변수를 기본/과거 값으로 대체하지 않는다. 후속 B2는 서버 SCRAM 저장을 채택하고 비밀번호의 새 길이/문자 제한·자동 변환은 추가하지 않는다. 특수 문자/개행/인코딩의 값 보존은 합성 입력으로 확인하며 클라이언트 사전 변환은 비채택 비교안이다.

로그 제어는 [B2](#bootstrap-startup-contract)의 8개 설정값·사전/사후 확인·진단 형식과 L-A의 트랜잭션 범위를 따른다. 격리 검증에서 설정 불일치 중단·트랜잭션 롤백·비밀값 출력 제한을 확인했다. 이 구간의 상세 진단은 줄어들며 로그 제어 실패 시 역할/권한 쓰기를 중단한다. 추가 감사/추적 경로의 자동 지원은 포함하지 않는다.

진단은 B2의 고정 단계/결과·psql 종료값 형식을 사용한다(E-A). 고정 진단과 실패 종료를 격리 검증했다. SQLSTATE를 추가하는 E-B는 비교 대안이며 bootstrap 진단을 API/PK guard 오류 계약에 자동 매핑하지 않는다.

인용과 로그 비노출은 별개다. 서버 로그·클라이언트 출력·환경/활동 조회를 구별하며 PANIC·감사 확장·외부 수집기·관리자/메모리 노출까지 자동 제어했다고 보장하지 않는다. [Q/L/E 상세](../../../work/records/phase-001/issue-43/artifacts/task-001-bootstrap-contract.md#f4-bootstrap-quoting-logs)과 [B1~B3 채택 상세](../../../work/records/phase-001/issue-43/artifacts/task-001-startup.md#f4-bootstrap-integrated)를 따른다. 실제 자료·기존 개발 DB/볼륨과 공통 도메인 표 구현은 보류한다.

<a id="bootstrap-startup-contract"></a>

## B1~B3의 최초 구동 통합 설계 계약

B1은 최초 설치/격리 검증과 Spring/Flyway/JPA 기본 기동 오류 처리를 사용한다. 별도 FlywayMigrationStrategy·매 기동 전수 검사·전용 5초 계약은 두지 않는다. B2/B3는 아래 SQL·로그·비밀값 전달 계약을 따른다. 최초 구동 파일·설정은 구현했으며 검증 근거는 [최초 구동 검증](../../../work/records/phase-001/issue-43/artifacts/task-001-bootstrap-verification.md#results)에 둔다.

| 항목                  | 확정한 구체 계약                                                                                                                                                                                                                                                                                                                                                                                                              |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| B1 최초 검증·기동     | A 확정: 최초 설치/격리 검증에서 app/migrator 인증·역할/권한·소유 및 정상/거부 동작을 확인하고 평소에는 기본 Flyway/JPA 기동을 사용. 전용 FlywayMigrationStrategy·매 기동 전수 검사·각 연결/검사 5초는 제외. 과도한 권한/소유 변화가 자동 탐지되지 않거나 app 오류 전에 Flyway가 성공할 수 있음. 알려진 초기화 실패/미확인의 후속 시작 보류는 운영 절차로 유지. TCP healthcheck는 서버 준비만 확인하며 test 프로필 격리를 유지 |
| B2 최초 SQL·비밀 처리 | 초기화 Unix socket/초기 관리자/DB를 명시하고 psql `-X --no-password --quiet --set=ON_ERROR_STOP=1 --single-transaction --file=...`로 보조 SQL을 한 번 실행. 사전 조건·로그 설정/재확인 뒤 역할/ACL 쓰기와 사후 검사. 새 길이/문자 제한·값 trim/변환 없이 서버 `password_encryption=scram-sha-256`를 준비 트랜잭션에 적용. 원문 stdout/stderr는 파일 없이 폐기하고 아래 고정 진단만 공개                                       |
| B3 파일·환경 연결     | 통합안의 Compose/Spring/예제 템플릿·읽기 전용 bind와 `create_host_path: false`·국소 LF 설정을 채택. 기존 실행 환경을 복사하고 `DB_BOOTSTRAP_USERNAME/PASSWORD`, 이전 `DB_USERNAME/PASSWORD`, `POSTGRES_USER/PASSWORD`, `PGUSER/PGPASSWORD`를 Gradle/Java 자식에서 제외. DB 접속값은 app/Flyway만 명시 연결하고 PATH/JAVA_HOME 등 일반 환경은 유지. 전체 환경 허용 목록 재구성은 비채택                                        |

B2 로그 설정은 `log_statement=none`, `log_min_duration_statement=-1`, `log_min_duration_sample=-1`, `log_transaction_sample_rate=0`, `log_min_error_statement=PANIC`, `log_min_messages=PANIC`, `log_parameter_max_length=0`, `log_parameter_max_length_on_error=0`의 8개다. 비밀 SQL 전에 SET LOCAL로 적용/재확인하고 트랜잭션 종료 뒤 원래 상태로 돌아가야 한다. 시작 시 결정되는 표본 추출을 고려해 변경 전 `log_transaction_sample_rate=0`도 사전 조건으로 요구하며 다르면 중단한다. 이미 결정된 표본 상태가 SET LOCAL만으로 취소된다고 가정하지 않는다. 일반 진단 손실과 비표준/PANIC·환경/활동 조회의 기존 한계를 유지한다.

B2 고정 진단은 입력 실패의 `stage=input_check result=failed`, psql 완료의 `stage=role_prepare result=ok|failed psql_exit=0|1|2|3` 형식을 사용한다. 코드가 없거나 허용 목록 밖이면 `stage=role_prepare result=unknown`으로 중단하고 원문 오류를 대체 출력하지 않는다. 실패를 성공 종료로 바꾸지 않는다. 셸/SQL의 사전·사후 검사와 출력 연결은 격리 DB에서 검증한다.

B3의 변수 우선순위는 기존 Node/Compose 동작을 유지한다. Node 실행기는 개인 `.env`를 읽으므로 관리자 값도 받지만 Gradle/Java 자식에는 제외한다. 알려지지 않은 모든 비밀값을 탐지한다는 보장은 하지 않으며 app/Flyway 두 쌍을 같은 Spring 프로세스가 보유하는 C-A 한계도 유지한다. 프런트에는 DB 접속값을 전달하지 않는다. 국소 개행 대상은 `db/bootstrap/*.sh text eol=lf`, `db/bootstrap/sql/*.sql text eol=lf`이며 실제 개인 `.env`를 자동 생성/덮어쓰지 않는다.

[확정한 흐름·파일/설정 발췌·실패 복구·검증 계획](../../../work/records/phase-001/issue-43/artifacts/task-001-startup.md#f4-bootstrap-integrated)을 따른다. 역할 준비 실패/커밋 불명은 자동 재실행하지 않고 실제 상태 확인 뒤 명시 복구한다. 현재 환경 이관/사건별 복구·공통 표 전체 DDL/버전·업무 DML/시퀀스·요청/예외 등 기존 잔여는 담당 Task에서 유지한다. 같은 선택을 재승인받지 않으며 새 판단이 필요하면 먼저 대안/이유를 제시한다. 실제 자료·기존 개발 DB/볼륨과 공통 도메인 표 구현은 보류한다.
