# 로컬 DB 최초 구동

<a id="current"></a>

빈 데이터 디렉터리에 PostgreSQL 18.6 DB를 처음 준비하는 절차다. 기존 DB 이관과 실제 게임 자료 등록은 포함하지 않는다. 역할·권한·인용/로그의 상세 계약은 [최초 구동 기준](<../../docs/details/development/로컬 DB 최초 구동.md#current>)을 따른다.

## 파일과 접속

| 파일                                           | 역할                                                             |
| ---------------------------------------------- | ---------------------------------------------------------------- |
| [10-prepare-roles.sh](10-prepare-roles.sh)     | 입력 검사 → 보조 SQL 한 번 실행 → 고정 결과와 종료값 반환        |
| [sql/prepare-roles.sql](sql/prepare-roles.sql) | 두 역할·최초 권한을 한 트랜잭션에서 준비하고 전후 조건 검사      |
| [Compose](../../compose.yaml)                  | 쉘은 초기화 디렉터리에, SQL은 자동 실행 경로 밖에 읽기 전용 연결 |

| 접속             | 사용자           | 환경변수 쌍                      |
| ---------------- | ---------------- | -------------------------------- |
| 최초 관리자      | `lumiawiki`      | `DB_BOOTSTRAP_USERNAME/PASSWORD` |
| 서비스           | `lumia_app`      | `DB_APP_USERNAME/PASSWORD`       |
| Flyway·객체 설치 | `lumia_migrator` | `DB_FLYWAY_USERNAME/PASSWORD`    |

app/migrator는 비슈퍼유저이며 서로 멤버십을 갖지 않는다. app에는 DB CONNECT·public USAGE, migrator에는 DB CONNECT·public USAGE/CREATE·plpgsql USAGE를 직접 부여한다. DB/public의 합의한 PUBLIC 권한을 회수하며 업무 표 DML은 해당 마이그레이션에서 별도로 정한다.

## 새 환경에서 실행

저장소 루트에서 실행한다. [.env.example](../../.env.example)을 개인 `.env`로 복사하고 세 비밀번호를 개인 값으로 지정한다. 사용자 이름과 DB 이름은 예제의 고정 이름을 유지한다. 개인 파일을 자동 생성하거나 덮어쓰지 않는다.

```text
docker compose -p lumiawiki up -d --wait --wait-timeout 90 db
node --env-file=.env scripts/dev-api.mjs
```

실행기는 일반 환경을 유지하면서 알려진 관리자·과거 공용 DB 변수를 Gradle/Java 자식에서 제외한다. 서비스와 Flyway는 같은 Spring 프로세스에서 각 전용 접속을 사용한다. 상세 전제·포트·웹 실행은 [루트 실행 안내](../../README.md#local-development)를 따른다.

## 실패와 기존 볼륨

- 입력 실패는 `stage=input_check result=failed`, SQL 실행 결과는 `stage=role_prepare result=ok|failed psql_exit=0|1|2|3`으로 보고한다. 허용된 종료값을 얻지 못하면 `result=unknown`으로 중단한다. 원문 SQL·오류·비밀번호는 출력하지 않는다.
- SQL 실패 시 역할·최초 권한 준비를 롤백한다. 앞서 만든 DB 디렉터리는 남을 수 있다. 실패/미확인이면 서버 시작을 보류하고 허용된 대상의 상태 확인·명시 복구를 먼저 진행한다.
- 기존 볼륨에서는 최초 hook이 다시 실행되지 않는다. `.env` 변경이나 재시작만으로 역할 이관·복구가 되지 않는다. 볼륨 삭제·역할 수정·권한 확대·비밀번호 교체를 자동 수행하지 않는다.
- TCP healthcheck는 서버 준비 확인이다. 모든 권한이나 과거 초기화 성공을 증명하지 않는다. 평소에는 기본 Flyway/JPA 기동을 사용하며 매 시작 전수 검사를 추가하지 않는다.

격리 검증 범위·결과와 한계는 [최초 구동 검증](../../work/records/phase-001/issue-43/artifacts/task-001-bootstrap-verification.md#results)을 따른다.
