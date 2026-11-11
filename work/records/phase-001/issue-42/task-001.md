# Task 42-001 — 프로젝트 골격·실행 환경·DB 연결

<a id="summary"></a>
## 현재 요약

- 제목: 프로젝트 골격·실행 환경·DB 연결
- GitHub sub-issue: [Mi-no-Kim/LumiaWiki #50](https://github.com/Mi-no-Kim/LumiaWiki/issues/50)
- 부모 Issue: [Issue #42](<issue.md#summary>)
- 상태: 완료
- 현재 진행 위치: 확정한 Task 1의 웹·서버·개발 DB·실행기·격리 검증 도구를 구현했다. 빌드·격리 검증·새 개발 DB 인증/재시작 보존과 사용자 시작 화면 확인을 마쳤다.
- 다음 행동: [PR #54](https://github.com/Mi-no-Kim/LumiaWiki/pull/54)를 부모 Issue 브랜치에 Squash 병합하고 반영 결과·Task 브랜치 정리를 확인한다. Task 002 이후는 예정이며 이번 요청에서 착수하지 않는다.

<a id="goal"></a>
## 목적과 허용 범위 및 완료 조건

후속 테스트·공통 골격이 사용할 웹·서버·개발 DB의 실행 기반을 만든다. 입력은 [기술 구성](<../../../../docs/details/development/기술 구성.md#stack>)·[DB 환경](<../../../../docs/details/development/DB 환경.md#layout>)·[서버 프로필](<../../../../docs/개발 기준.md#server-profiles>)이다.

- `frontend/`에 React 19.3.1·TypeScript 7.0.2·Vite 8.3.7, `backend/`에 Java 21·Spring Boot 4.1.2·Gradle Wrapper 9.9.1을 구성한다. 서버 생성 옵션·의존성은 기존 기준을 따른다.
- 루트 `compose.yaml`과 공식 `postgres:18.6`, 로컬 전용 바인딩·named volume 보존, 개인 `.env`와 비밀값 없는 `.env.example`을 준비한다. 환경변수를 로컬 Spring 프로세스에 전달할 실제 방법을 문서화한다.
- 공통/local/test 설정을 나누고 local 활성화를 공통 설정에 고정하지 않는다. 테스트의 실제 컨테이너 연결·실행 명령은 Task 002가 맡는다.
- 공용 `db/migration/`을 Gradle 리소스로 포함하고 Flyway·JPA validate·SQL 자동 초기화 never를 연결한다. 게임 테이블·자료와 원본 SQL은 변경하지 않는다.

완료 조건은 선택한 버전의 설치·웹/서버 빌드·로컬 실행·DB 접속 확인, 환경변수 전달과 비밀값 비추적, SQL의 JAR 포함·Boot Flyway 인식·재시작 시 이력 유지, 컨테이너 종료/재시작 후 볼륨 보존이다. 게임 스키마 없는 상태의 확인은 격리된 임시 검증용 migration으로 수행하고 제품 스키마로 남기지 않는다. 실제 검증법은 아래 확정 설계의 격리 복제·임시 DB 절차를 따른다. 실행 안내와 실제 경로는 README·STRUCTURE에 반영한다.

<a id="plan"></a>
## 계획과 예정 검증

1. JDK·Node·npm·Docker 엔진·포트와 기존 파일/설정을 확인한다. 도구의 버전 차이만으로 교체하지 않는다. 배포 메타데이터·호환성은 실제 설치 전에 확인하고 충돌은 해당 범위에서 판단한다.
2. 잠금 파일·Wrapper·기본 설정과 DB 구성을 마련하고 빌드·실행한다. 생성/환경 준비 예외의 대상·이유·검증을 기록하며 기능 로직을 앞당기지 않는다.
3. 정상 접속, 개인 값 누락/잘못된 접속의 실패, SQL 리소스/이력과 볼륨 보존을 확인한다. 기존 사용자 데이터 삭제나 볼륨 초기화는 하지 않는다.
4. 골격 직후 [Task 002](<task-002.md#plan>)에 테스트 실행 환경·최소 hook을 연결한다. 테스트 DB 분리의 실제 결과는 그 Task에서 확인하고 Issue 통합 수용에서 함께 대조한다.

### 구현 전 공유할 사용자 확인 목록

| 준비·조작 | 기대 결과·AI 확인 방법 |
|---|---|
| 개인 환경변수를 주입한 뒤 DB·서버·웹을 안내 명령으로 실행 | 웹 진입·서버 시작·개발 DB 접속이 성공. 빌드·접속 검사와 직접 실행으로 확인 |
| 컨테이너를 일반 종료한 뒤 재시작 | 기존 볼륨·Flyway 이력이 보존됨. 재시작 전후 내부 값 대조 |
| 별도 실행에서 필수 접속값 누락/잘못된 값 사용 | 비밀값 노출 없이 원인 확인 가능한 실패. 로그·종료 결과 대조 |

아래 명령·주소·후보 버전과 위 조작/기대 결과를 구현 전 계획으로 공유한다. 명령은 앞으로 구현할 사용 계약이며 현재 실행 가능한 기능이 아니다. 사용자 확인은 아직 미수행이다. 이번 범위는 기술 실행 골격이며 검색·상세·루트 화면은 Issue #44 이후 디자인을 따른다. 자체 검수와 커밋 전 별도 검수는 [검수 기준](<../../../../.agents/skills/review-work/SKILL.md#before-commit>)을 적용한다.

<a id="implementation-decisions"></a>
## Task 1 세부 결정 — 확정

2026-11-12 사용자 요청으로 현재 Task 1의 세부 사항만 확정했다. 기존 Task 1의 실행 준비를 구체화하는 변경이며 새 Task·브랜치·제품 요구를 추가하지 않는다. 후속 Task 002~004의 도구·설계 결정은 변경하지 않는다. 이번 변경은 계획 기록이며 구현·설치·DB 생성·커밋·push는 수행하지 않는다.

### 생성 방법과 최소 구성

- 서버는 Spring Initializr의 Gradle/Groovy·Java 21·Boot 4.1.2·Jar·YAML 생성물로 시작한다. Group `io.github.minokim`, package `io.github.minokim.lumiawiki`, artifact/name `lumiawiki-api`, version `0.0.1-SNAPSHOT`, description `Lumia Island Wiki API`를 사용한다. Wrapper는 9.9.1로 맞추고 서버 기본 의존성·Lombok·SpringDoc 3.2.0은 기존 기술 기준대로 선언한다. 생성 응답이 선택 버전을 제공하지 않으면 다른 버전으로 자동 교체하지 않고 해당 실패를 반환한다.
- 프런트는 버전 미지정 생성기를 실행하지 않고 React/Vite/TypeScript의 최소 파일과 manifest를 명시적으로 작성한다. `react`·`react-dom` 19.3.1, `vite` 8.3.7을 고정한다. TypeScript는 기존 병행 기준의 첫 단계로 `@typescript/native: npm:typescript@7.0.2`를 선언해 `tsc`를 사용한다. lint용 6.0 API 연결은 Task 004가 맡는다.
- Task 1 보조 devDependency는 `@vitejs/plugin-react` 6.3.0, `@types/react`·`@types/react-dom` 각각 19.3.0으로 고정한다. registry 메타데이터상 plugin-react는 Vite ^8·Node ^20.19 또는 >=22.12를 지원하며 React Compiler 관련 peer는 optional이므로 도입하지 않는다. 선택한 버전의 실제 설치/빌드 통과는 아직 미확인이다.
- `vite.config.mjs`를 사용해 Node 타입 패키지를 추가하지 않는다. 앱 TS는 strict·noEmit·target ES2022·module ESNext·moduleResolution Bundler·jsx react-jsx로 검사한다. 시작 화면은 제목과 실행 확인 문구만 둔다. Router·Query·제품 화면/기능·lint/포맷/CI·테스트 프레임워크는 이번에 구현하지 않는다.
- `frontend/package-lock.json`과 Gradle Wrapper 파일을 추적한다. 최초 선언 설치는 `npm --prefix frontend install`, 같은 잠금 파일의 재현 설치는 `npm --prefix frontend ci`다. 루트 품질 도구용 package.json은 Task 004의 담당으로 남긴다.

### 개인 설정과 서버 실행

- Node 기본 `--env-file=.env`로 루트 개인 파일을 읽고 `scripts/dev-api.mjs`가 필수 DB 변수·포트 범위를 검사한 뒤 backend Wrapper의 `bootRun`을 실행한다. dotenv 같은 추가 라이브러리는 사용하지 않는다. Windows에서는 저장소의 `gradlew.bat`, 다른 환경은 `gradlew`를 호출하며 작업 위치를 명시한다. 비밀값은 프로세스 환경으로 전달하고 명령 문자열·로그에 삽입하지 않는다.
- `.env.example`에는 DB_HOST·DB_PORT·DB_NAME·DB_USERNAME의 기존 기본값과 DB_PASSWORD 자리표시자만 둔다. `.env`는 Git 제외이며 자동 생성/덮어쓰기하지 않는다. 비밀번호의 실제 값은 개인 실행 입력이다. 누락·빈 값·예제 자리표시자는 변수 이름만 안내하고 서버 실행 전에 실패한다. 기존 프로세스 환경값이 있으면 Node/Compose의 동일한 우선순위로 사용한다.
- 실행기는 자식 프로세스에 `SPRING_PROFILES_ACTIVE=local`을 명시하고 서버를 127.0.0.1:8080에 바인딩한다. 환경변수로 서버 포트만 바꾸려면 `SERVER_PORT`를 사용한다. Ctrl+C와 자식 종료 코드는 전달하며 임의 재시작하지 않는다. 웹은 별도 명령/프로세스로 실행하고 DB 비밀번호를 웹 환경이나 번들로 전달하지 않는다.
- frontend는 `localhost:5173`·strictPort, preview는 `127.0.0.1:4173`·strictPort로 고정한다. API 8080/DB 5432 충돌도 다른 서비스를 종료하거나 임의 포트로 바꾸지 않고 실패를 안내한다. 필요한 로컬 포트 변경은 해당 실행값으로만 처리한다. 프록시·공통 API 골격은 Task 003에서 연결한다.

### DB·SQL·설정 경계

- Compose project는 `lumiawiki`, service는 `db`, named volume key는 기존 기준의 `postgres_data`다. 공식 postgres:18.6·127.0.0.1:${DB_PORT}:5432·/var/lib/postgresql을 사용한다. `pg_isready` healthcheck(5초 간격·5초 timeout·12회 retry·10초 start period)를 두고 준비 대기는 최대 90초로 제한한다.
- 개발 DB명/계정은 lumiawiki, 실제 암호는 개인 환경값이다. 일반 종료에는 볼륨을 보존하고 기존 볼륨/DB를 자동 초기화하지 않는다. Docker 엔진이 없으면 명확히 실패를 반환하며 설치·엔진 시작을 수행했다고 기록하지 않는다.
- `application.yaml`은 공통 JPA/Flyway/앱 설정, `application-local.yaml`은 개인 환경변수 참조, `src/test/resources/application-test.yaml`은 테스트 설정 틀로 구분한다. 공통 설정에는 활성 local·개인 암호·개발 DB 접속을 하드코딩하지 않는다. Task 002가 전용 테스트 DB 연결을 완성한다.
- `db/migration/`은 비어 있는 위치를 `.gitkeep`으로 추적하고 Gradle processResources가 이 경로의 `**/*.sql`만 빌드의 `db/migration/`으로 포함한다. JPA ddl-auto=validate·SQL init never·Flyway classpath:db/migration을 유지한다. 초기 게임 스키마나 가짜 업무 migration은 넣지 않는다.

### 생성 후 제공할 명령

모든 명령은 저장소 루트 기준이다. 현재는 계획된 사용 계약이며 명령을 구현·실행한 결과가 아니다.

| 목적 | 명령·관찰 위치 |
|---|---|
| DB 시작/준비 대기 | `docker compose -p lumiawiki up -d --wait --wait-timeout 90 db` |
| DB 일반 종료 | `docker compose -p lumiawiki down` (볼륨 보존) |
| API 로컬 실행 | `node --env-file=.env scripts/dev-api.mjs` → 127.0.0.1:8080 |
| 웹 실행 | `npm --prefix frontend run dev` → localhost:5173 |
| 웹 타입 검사 | `npm --prefix frontend run typecheck` → tsc --noEmit |
| 웹 빌드 | `npm --prefix frontend run build` → typecheck 후 vite build |
| 웹 빌드 확인 | `npm --prefix frontend run preview` → 127.0.0.1:4173 |
| 서버 빌드 | Windows: `backend\gradlew.bat -p backend bootJar`, 다른 환경: `backend/gradlew -p backend bootJar` |
| 기반 검증 | `node scripts/verify-bootstrap.mjs` → 아래 격리 검증 결과 |

Task 1의 서버 빌드는 bootJar이며 제품 테스트/hook 검증 완료를 뜻하지 않는다. 테스트 명령/연결은 골격 직후 Task 002가 준비한다. 서버의 성공 판정은 기동 로그·DB 접속으로 확인하며 제품 API나 health endpoint를 임의로 추가하지 않는다.

### Flyway·보존 검증 방법

1. `verify-bootstrap.mjs`는 `.tmp/issue-42/task-001/`의 실행별 하위 경로에 backend의 필요한 소스/Wrapper/빌드 설정만 복제한다. 원본과 복제 입력의 지문을 대조하고 build/cache·개인 .env·다른 작업·보존 영역은 복제/검색하지 않는다. 복제 루트의 `db/migration/V1__bootstrap_probe.sql`만 만들며 실제 원본 SQL 위치는 건드리지 않는다.
2. 합성 SQL은 검증 전용 `bootstrap_probe` 테이블과 고정 확인 행 하나를 만든다. 복제본의 동일 Gradle 리소스 설정으로 bootJar를 만들고 JAR 내부 `BOOT-INF/classes/db/migration/V1__bootstrap_probe.sql`의 바이트를 입력과 대조한다. 기본 경로를 임시로 덮는 제품용 우회 설정은 추가하지 않는다.
3. 검증용 postgres:18.6은 고유 Compose project와 별도 named volume·DB명/계정/일회성 암호로 실행하고 호스트 DB 포트는 비어 있는 임시 포트를 할당한다. 암호는 Git 제외 임시 설정/프로세스에만 두고 출력하지 않는다. 개발 lumiawiki DB/volume을 검증 대상으로 사용하지 않는다. 이 구성은 Task 002의 Testcontainers 도입을 대신하지 않는다.
4. 복제 JAR를 해당 DB에 실행해 Flyway 성공·검증 행·schema_history의 버전/성공 여부/checksum을 확인한다. 앱을 종료·재실행해 migration이 중복 적용되지 않고 행/이력이 보존되는지 확인한다. 이어 검증용 Compose를 일반 종료·재시작해 동일 볼륨의 행/이력을 다시 대조한다. 기동/DB 대기는 각각 최대 90초로 제한하고 초과는 실패로 반환한다.
5. 원본 backend의 정상 bootJar에는 합성 SQL이 없고 원본 db/migration에 검증 파일이 추가되지 않았는지 확인한다. 개발 연결 정상·암호 누락/잘못된 값의 안전한 실패와 프런트 dev/preview의 시작 화면도 확인한다. 실제 관찰은 자동 확인·AI 직접 실행/브라우저·사용자 확인으로 구분해 기록한다.
6. 정상 종료 후 입력 지문·명령·핵심 판정은 이 Task 기록에 남긴다. 생성 이력으로 해당 실행의 소유가 확인되는 임시 컨테이너/볼륨/파일만 정리하고 개발 데이터는 보존한다. 실패 시에는 필요한 재현 자료를 유지하고 원인/남은 리소스를 알린다.

### 결정 완료와 실행 확인의 구분

- Task 1의 범위·버전·생성 방식·보조 패키지·설정/실행 계약·포트/실패 처리·DB/리소스 경계·검증/정리 방식에 남은 설계 선택은 없다. 사용자에게 다시 골라 달라고 할 항목은 없다.
- 개인 DB 비밀번호의 실제 값은 실행 입력으로 남긴다. 환경에서 선택 버전이 제공되지 않거나 호환 충돌·포트 점유가 확인되면 해당 사실을 보고하고 필요한 영향만 다시 판단한다. 현재 그런 변경을 미리 승인/성공으로 처리하지 않는다.
- 앞선 읽기 전용 환경 확인에서 Node 24.13.0·npm 11.19.1, Docker 29.8.0·Compose 5.5.1을 관찰했고 Docker Linux 엔진 연결은 실패했다. Java의 현재 실행 상태, 패키지 설치/빌드·DB/Flyway·웹 동작·사용자 확인은 미확인이다. Docker 연결 실패는 설계 미정이 아닌 실행 선행 조건이다.
- Task 002의 테스트/hook, Task 003의 공통 웹/API, Task 004의 포맷/CI 상세는 이번 결정 대상에 포함하지 않는다. 실제 게임 자료 작업 보류는 유지한다.

근거: [Node env-file](https://nodejs.org/api/cli.html#--env-filefile) · [Boot Gradle bootRun](https://docs.spring.io/spring-boot/gradle-plugin/running.html) · [Gradle 리소스/파일 처리](https://docs.gradle.org/current/userguide/working_with_files.html) · [Compose 시작/준비 대기](https://docs.docker.com/reference/cli/docker/compose/up/). 패키지 버전/peer/optional 조건은 2026-11-12 npm registry의 해당 버전 메타데이터를 읽어 확인했으며 설치 성공의 근거로 사용하지 않는다.

- 결정 반영 확인: Task 1 본문과 부모/현황 요약 4개 파일의 로컬 참조·표식 79개와 공백을 확인했다. 기존 기술·DB 기준과 이번 세부 설계를 대조했으며 Task 002~004의 원문이 HEAD와 같음을 확인했다. 결정 기록은 미커밋이고 실행 검증은 수행하지 않았다.

<a id="implementation"></a>
## 구현 진행

- 2026-11-12 사용자 요청으로 확정한 Task 1 구현을 시작한다. 기존 미커밋 상세 결정 4개 기록을 보존하며 같은 Task에서 구현·검증·안내를 함께 처리한다. 후속 Task의 제품 기능·테스트/hook/CI는 구현하지 않는다.
- 구현 전 확인 목록 공유: 개인 설정으로 DB·서버·웹 시작, 일반 종료/재시작의 데이터·Flyway 이력 보존, 누락/잘못된 접속값의 안전한 실패를 위 목록대로 확인한다. 실제 실행 방법은 구현된 명령에 맞춰 결과에 제공한다.
- 초기 골격·설정·정적 시작 화면은 초기 환경 준비 예외로 생성·빌드·기동 검증한다. dev-api의 환경변수 검증/프로세스 전달 동작은 Node 기본 테스트로 실패→구현→통과를 확인한다. 검증 도구는 실제 격리 DB/JAR 입력으로 확인하며 환경 실패를 Red로 세지 않는다.

- 사용자 추가 지시: Spring Boot 파일은 사용자가 제공한다. 진행 중이던 backend bootJar는 중단(종료 1)했고 빌드 성공으로 판정하지 않는다. AI 생성 파일의 지문을 확인해 `.tmp/issue-42/task-001/server-before-user/`로 보존했다. 이후 보관 경로에서 확인한 공통 파일은 settings·Wrapper 3개·애플리케이션 Java의 총 5개다. build.gradle·Wrapper properties·application.yaml은 지문이 달라 원위치에 보존했다. 사용자 제공 파일의 도착 전 backend 생성/수정을 중단한다. 웹·Compose·실행기·검증 도구는 독립적으로 계속 구현한다. 제공 후 실제 서버 파일과 확정 설정/버전을 대조하고 필요한 연결만 수행한다.

<a id="verification"></a>
## 구현 결과와 실제 검증

- 입력: 사용자가 backend 제공 완료를 알린 뒤 제공된 build.gradle·application.yaml·HELP·기본 테스트를 기준으로 연결했다. 현재 없던 공통 파일 5개는 보관본에서 복원하고 local/test 설정을 작성했다. 제공된 의존성/테스트는 유지하며 PostgreSQL Flyway 모듈의 runtime 범위·Wrapper 9.9.1·SQL processResources·공통 JPA/Flyway 설정만 확정 기준에 맞췄다. 첫 생성 시도와 사용자 제공 전 빌드, 제공 직후 복원 도중의 빌드는 중단한 시도로 구별한다.
- Node 실행기 TDD: 기본 Node 테스트 4개(누락/예제 암호, 잘못된 포트, JDBC 옵션 주입/비밀값 비노출, 정상 접속값/local 프로필)를 스텁에서 실행해 실제 4개 실패를 확인한 뒤 구현해 4개 통과했다. 명령은 `node --test scripts/dev-api.test.mjs`, 초기 기준 HEAD는 `d8133e3`이다. 생성 골격/정적 화면/초기 설정은 기록한 환경 준비 예외로 빌드·실행을 확인했다.
- 웹: 확정 의존성 `npm --prefix frontend install --no-audit --no-fund` 성공(24 packages), TypeScript 7.0.2 검사와 Vite 8.3.7 build 성공. dev localhost:5173·preview 127.0.0.1:4173의 HTTP 200·문서 제목/root 요소를 확인했다. 첫 제한된 실행 환경에서는 접속 실패해 같은 코드의 로컬 접근 가능한 실행 환경으로 재시작했고 HTTP 검증을 통과했다. 실제 화면 렌더링 확인은 아래와 별개다.
- 서버: 기존 Oracle JDK 21.0.11·Wrapper 9.9.1로 `backend\gradlew.bat -p backend bootJar --console=plain` 성공. 루트 공용 SQL은 비어 있으며 게임 스키마/자료를 추가하지 않았다. 테스트 환경/hook은 Task 002에서 마련하며 사용자가 제공한 contextLoads 등 서버 테스트의 통과를 주장하지 않는다.
- 격리 검증: `JAVA_HOME`을 기존 JDK 21로, `GRADLE_USER_HOME`을 Git 제외 task 임시 캐시로 두고 `node scripts/verify-bootstrap.mjs`를 실행했다. 실행 `lw-bootstrap-9e35b63130aa`는 9개 서버 입력 파일의 원본/복제 지문·JAR SQL 바이트, Flyway 버전1/성공/checksum -1232980188과 `1|preserved` 행, 앱 재시작·Compose down/up 보존, 잘못된 암호의 비노출 실패, 실제 Node env-file/로컬 bootRun 실행, 제품 JAR/원본에 합성 SQL 미포함을 모두 확인했다. 소유 라벨을 확인한 해당 임시 컨테이너·볼륨은 제거했고 비밀 임시 설정은 내용을 비웠다. 실행 결과/입력 지문은 당시 담당 `.tmp/issue-42/task-001/lw-bootstrap-9e35b63130aa/result.json`에 기록했고 아래 정식 결과/지문으로 옮긴 뒤 임시 보고서를 정리했다.
- 실패와 복구: 첫 격리 실행 `lw-bootstrap-123be2f5df15`는 DB 재생성 후 임의 호스트 포트가 바뀌어 잘못된 암호 검사가 접속 실패로 어긋났다. 포트를 재조회하도록 수정했고 위 전체 실행에서 다시 통과했다. 별도 암호 실패 probe는 종료1·인증 실패·비밀값 비노출을 확인했다. 이전 실행의 소유 리소스도 확인 후 제거하고 비밀 Compose 설정을 비웠다. 원래 개발 volume은 정리 대상에 넣지 않았다.
- 비밀값/범위 확인: `.env`·node_modules·dist·backend/build·Task 임시는 Git 제외다. 개인 DB 암호가 frontend/dist에 포함되지 않았고 Node와 Compose가 읽은 설정 암호의 일치도 값 노출 없이 확인했다. Task 002~004 기록은 HEAD와 동일하다. README·STRUCTURE·담당/부모 기록 6개 문서의 현재 원천 참조 95개를 확인했고 보존 링크는 따라가지 않았다.
- 실제 개발 환경: Docker Desktop을 시작해 Linux 엔진 연결에 성공했다. 사용자가 개인 .env 설정 완료를 알린 뒤 개발 db 컨테이너는 healthy이나 서버 TCP 인증은 실패했다. 기존 종료 상태 lumiawiki-postgres-1과 새 lumiawiki-db-1이 기존 lumiawiki_postgres_data volume을 사용하며 .env 변경이 기존 계정 암호를 바꾸지 않음을 확인했다. 기존 컨테이너/데이터는 삭제하지 않고 암호를 맞추는 사용자 선택을 요청했다.
- 화면 확인 한계: 내장 브라우저는 초기 로컬 연결에 실패했고 Google Chrome 조작은 승인되지 않아 AI 브라우저 검증을 수행하지 못했다. 사용자에게 이유를 설명하고 Chrome 조작을 중단했다. 현재 두 주소의 HTTP 검증은 성공했으며 제목과 실행 준비 문구의 직접 화면 확인은 사용자에게 요청했다. HTTP 200을 실제 렌더링 성공으로 확대하지 않는다.
- 당시 남은 필수 확인: 실제 개발 DB의 재사용/신규 볼륨 선택과 인증 해소·서버 기동/재시작 보존. 화면 확인은 아래 사용자 응답으로 충족했다. 당시에는 Task 완료를 판정하지 않았으며 아래 재초기화/최종 판정에서 남은 조건을 대조했다. 소스/기록은 미커밋·원격 미게시다. Windows에서 실행했으며 다른 OS 실행은 미확인이다.

### 재대조용 입력 지문

격리 실행의 서버 입력은 아래 SHA-256으로 보존한다. 기준 commit은 `d8133e3`이고 서버/실행기/웹 변경은 아직 미커밋이다. 임시 출력만으로 검증 근거를 대체하지 않는다. 아래 서버 지문은 성공 실행 후 원본과 다시 대조했다. 실행기의 다른 OS 호출은 sh를 통한 Wrapper 실행으로 정리했으며 Windows 호출 경로는 검증 때와 같고 다른 OS 실행은 미확인이다.

| 입력 | SHA-256 |
|---|---|
| `backend/build.gradle` | `7d40889a9340e24fc7c99352ec573eb289857b50364f41b81aef59ec799499e9` |
| `backend/settings.gradle` | `46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9` |
| `backend/gradlew` | `a5a5c199ba02189ae8c46a334223371a20599d9c298ef65e7540ede4a3f72d59` |
| `backend/gradlew.bat` | `f17917f8dbe61182b149273ee78090fec1197442c3f38276af907bfa5190db16` |
| `backend/gradle/wrapper/gradle-wrapper.jar` | `3b8a25775a69158b5ad2b1d17a80a88dc7b40a352a73eb27d06c612a7ce68e98` |
| `backend/gradle/wrapper/gradle-wrapper.properties` | `ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943` |
| `backend/src/main/java/io/github/minokim/lumiawiki/LumiawikiApiApplication.java` | `656c97f12467804d5db08a98e2546d61667ce9461c566a8022f26c6d0867c705` |
| `backend/src/main/resources/application-local.yaml` | `a9f83af5c15034c2a3e15219c0e39e80d15db4deae77e864f3999216452243e5` |
| `backend/src/main/resources/application.yaml` | `4761c46d3f79db0632579511eac32ade8f1856703687973ddcb9d324cba5cc6e` |
| `scripts/dev-api.mjs` | `7929de355b3808b1f02ee2c9625318c5a4b6151dfba148346e203a8155cfe768` |
| `scripts/dev-api.test.mjs` | `00cc2a649e931e62c270e2a3093f39f088ac6aa6c2bbe43a032125ac83761ffb` |
| `scripts/verify-bootstrap.mjs` | `196600442ab6aa6f00f91e22955bb4174cdc7703065fac8785ec4b7fda188180` |
| `frontend/package.json` | `15859b72d5dfb7d32d5d3c4aeaac3d016f9a777970109dd52f94e93ebcda6d38` |
| `frontend/package-lock.json` | `49a00b7d18cdb137bfc5fb7ffc327cd41e8a495ec0a349f35dfdaac619b66ec0` |

### 사용자 화면 확인과 DB 저장 공간 확인

- 사용자가 개발/빌드 화면에서 ‘루미아 아일랜드 위키’ 제목과 ‘웹 실행 환경이 준비되었습니다.’ 문구가 정상 표시됐다고 답했다. 이는 사용자 직접 확인 결과이며 AI 브라우저 조작 성공으로 기록하지 않는다.
- 사용자는 Docker를 새로 하는데 기존 개발 DB 암호와 일치시켜야 하는 이유를 질문했다. 이 질문은 암호 변경/기존 데이터 삭제의 승인이 아니다. 기존 컨테이너 lumiawiki-postgres-1(종료)과 새 lumiawiki-db-1(실행)이 모두 기존 lumiawiki_postgres_data를 사용하는 사실을 재확인했다. 볼륨 생성일은 2026-10-11이며 Docker 재설치/새 컨테이너 생성 여부와 DB 저장 공간의 신규 여부는 구별한다.
- 원인은 확정한 Compose project lumiawiki와 logical volume postgres_data가 기존 physical volume 이름과 일치한 것이다. PostgreSQL 초기 암호 환경변수는 비어 있는 데이터 디렉터리의 최초 초기화에만 적용되므로 기존 계정의 암호는 바뀌지 않았다. Node와 Compose의 설정값 파싱 차이는 없는 것을 이미 확인했다.
- 앞선 두 선택지(기존 암호로 .env 정렬/DB 암호 변경)에 기존 볼륨을 보존하면서 새 빈 볼륨을 사용하는 대안을 빠뜨렸음을 설명했다. 완전히 새 DB라면 기존 암호와 맞출 필요가 없다. 이번 질문 응답에서는 계정 암호·볼륨 연결·DB 데이터를 변경하지 않는다. 새로운 저장 공간 사용 여부를 확인하면 영향 범위의 설계/실행 안내만 갱신한다.

### 기존 잔재 삭제와 개발 DB 재초기화

- 사용자 명시 지시: 기존 볼륨은 과거 잔재이므로 삭제 후 새로 만들어 진행해도 된다. 이는 기존 데이터 보존/암호 정렬 선택을 대체하는 이번 개발 DB 초기화 허용이며 일상 종료의 볼륨 보존 기준은 유지한다.
- 삭제 직전 `lumiawiki_postgres_data`의 이름·project 라벨과 연결 컨테이너가 `lumiawiki-postgres-1`, `lumiawiki-db-1` 둘뿐임을 확인했다. 이 두 컨테이너와 해당 볼륨만 제거하고 볼륨 조회 실패로 삭제를 확인했다. 다른 볼륨/바인드 원본·개인 .env는 삭제하지 않았다.
- 같은 Compose 구성과 현재 개인 .env로 빈 volume을 다시 생성해 개발 서버 연결·재시작 보존을 확인한다. 비밀번호 값은 출력하거나 기록하지 않는다.

<a id="result"></a>
## 최종 결과와 완료 판단

- 새 개발 volume 생성일은 2026-11-12(KST, Docker metadata `2026-11-11T17:08:00Z`)이다. 사용자 개인 .env로 local 프로필 서버가 DB 인증·Hikari 접속·Flyway 빈 migration 검증 후 8080에서 기동했다. API를 종료하고 Compose의 일반 down/up을 실행해 같은 volume 생성시각·DB OID·Flyway history table OID와 행 수가 유지됨을 대조했다. 이후 같은 서버 실행기로 재기동해 DB 연결·Flyway 검사·서버 시작을 재확인했다.
- 개발 재시작 전후 식별값: `16384|16385|0` → `16384|16385|0` (DB OID | history table OID | migration 행 수). 제품 SQL이 아직 없어 행 수 0은 예상 상태이며 게임 테이블/자료를 추가하지 않았다. 합성 행·checksum의 보존은 앞선 격리 검증으로 확인했다.
- 잠금 파일 재현: `npm --prefix frontend ci --no-audit --no-fund` 후 TypeScript 검사·Vite build를 다시 통과했다. 웹 dev/preview를 재실행해 두 URL의 HTTP 200과 API 8080 접근을 확인했다. 같은 빌드 자산의 제목/준비 문구는 사용자가 직접 정상 표시를 확인했다.
- 자체 검수: 실제 소스·확정 설계·실행 기록을 대조해 생성/버전/환경·개발 DB와 격리 DB 분리·비밀값/생성물 제외·SQL 원천/패키징·정상/실패/재시작·화면 확인·README/STRUCTURE와 부모 표시를 확인했다. Node 환경 검증 4개 테스트 통과와 기존 서버/웹/격리 검증 근거를 유효한 범위에서 재사용했다. Task 002~004 기록은 변경하지 않았다. 이번에는 커밋을 수행하지 않아 커밋 전 별도 검수/인덱스 상태 검사는 실행하지 않았다.
- 완료 판정: Task 1의 웹/서버 실행·개인 설정 전달·DB 접속·SQL JAR/Flyway 인식·앱/DB 재시작 보존·비밀값 보호·실행 안내 수용 조건을 충족했다. AI 브라우저 조작 제한은 사용자 직접 화면 확인 결과로 보완했으며 AI 직접 렌더링 검증으로 표시하지 않는다. Windows에서 검증했고 다른 OS 실행·후속 테스트/hook/CI·게임 기능/자료 검증은 이번 완료 범위 밖이다.
- 보존/정리: 정식 Task 본문에 실행 명령·기대/관찰·실패 원인/복구·DB 결과·입력 지문을 보존했다. 재현 확인이 끝난 두 격리 실행 디렉터리, 원래 서버 보관본(현 소스와 지문 일치), 생성 zip·개발 보존 임시 report의 총 5개 임시 대상을 경로/소유 확인 후 제거하고 부재를 확인했다. 현재 서버 실행과 재사용에 필요한 task Gradle cache는 유지한다. 개인 .env·새 개발 volume·사용 중인 서버/웹은 유지한다.
- 관련 반영: Task 완료를 부모 Issue/Phase 전체 완료로 전파하지 않는다. GitHub #50의 완료/라벨과 부모 요약을 로컬 결과에 맞추고 후속 Task는 예정으로 유지한다. 구현 완료 당시 소스는 미커밋이었으며 이번 제출에서도 Task 브랜치를 자동 통합하거나 삭제하지 않는다.

<a id="commit-review"></a>
## 구현 커밋 전 검수

- 2026-11-12 사용자 요청으로 Task 1 구현 결과의 검수·로컬 커밋을 진행한다. 기존 완료 작업의 제출 보완이며 새 Task/브랜치·동작 범위를 추가하지 않는다. 기준은 HEAD `d8133e3`과 확정 설계·최종 실행 결과다. 개인 .env·캐시·빌드 결과·임시 검증 출력·사용자 제공 HELP는 제출 대상에 넣지 않는다.
- 자체 검수: 현재 소스/설정·사용자 제공 서버의 보존·잠금 파일·명령/환경 전달·제품 SQL과 합성 SQL 분리·비밀값 비노출·종료/재시작·검증 근거·부모 상태를 대조했다. 생성 테스트의 실제 DB/Testcontainers 연결은 Task 002 범위이며 이번 bootJar/기반 검증의 성공을 서버 테스트 완료로 보고하지 않는다. 이전 최종 후보의 실행 지문이 같으면 유효한 설치/빌드/기동/보존/화면 확인 근거를 재사용한다.
- 실제 인덱스 후보의 자체·별도 검수와 완료 상태 검사를 마친 뒤 최종 제출 일치를 확인한다. 검수 중 변경이 생기면 영향받는 검사/근거를 다시 확인한다.

- 커밋 전 별도 검수 결과: HEAD `d8133e3` 대비 실제 인덱스 후보 33개 파일을 읽기 전용 에이전트가 검수했다. 코드/설정/문서·확정 설계/최종 결과·기술/DB/테스트/TDD/hook 기준을 대조해 필수 결함을 발견하지 못했다. Git 정규화 후 인덱스/작업 파일·기록된 구현 지문·로컬 참조 95개가 일치했고 공백 검사와 Node 테스트 4개를 통과했다. DB/서버/브라우저/네트워크는 새로 실행하지 않고 담당 기록의 실제 실행·사용자 확인 근거를 대조했다. 보존 영역·개인 설정·임시/빌드 결과에는 접근하지 않았다.
- 주 진행자 최종 확인: GitHub #50 Closed/Completed·unit:task/status:completed·milestone1, 부모 #42와 milestone1 Open, #51~#53 Open/Planned와 실제 하위 관계가 로컬 기록과 일치했다. 인덱스 Task 상태 검사도 완료와 일치했다. 상태 검사 도구의 첫 cp949 출력 인코딩 오류는 Python UTF-8 실행 옵션으로 해결했으며 검사기 자체는 변경하지 않았다. 실제 개인 DB 암호가 staged 33개 파일에 없음을 값 출력 없이 확인했다. 이후 검수 결과 요약만 추가한 후보의 나머지 파일/내용 일치를 재대조한다.

<a id="parent-integration"></a>
## 부모 Issue 통합

- 2026-11-12 사용자 요청: Task 1 push·PR 생성·부모 Issue 병합. 새 Task나 기능 변경이 아닌 기존 완료 결과의 통합이다. 검수된 구현 commit `95cafce`와 부모 Issue의 준비 commit `d8133e3`을 각각 담당 원격 브랜치에 push하고 실제 ref 일치를 확인했다.
- 실제 PR: [#54](https://github.com/Mi-no-Kim/LumiaWiki/pull/54), head `task/42-001-project-bootstrap`, base `issue/42-development-foundation`. 부모 base는 `d8133e3`이며 main/Phase의 필요한 선행 이력을 포함한다. 원격에 없던 부모 브랜치의 게시는 PR 대상 준비를 위한 것이다.
- 통합 범위/근거: Task 요구·수용 조건과 부모 직접 영향을 자체 확인했다. 구현 소스·검증 입력은 `95cafce`의 33개 파일 자체·별도 검수와 설치/빌드/기동/격리 DB/화면 확인의 유효한 근거를 재사용한다. 이번 후속 변경은 통합 위치·권한·절차를 기록한 문서뿐이며 실제 제출 후보의 별도 검수 후 반영한다.
- 병합 조건/방법: 최종 head/base 일치·부모 포함·충돌/필수 검사/미해결 의견을 확인하고 Squash merge한다. 통합 제목은 `task(42-001): 프로젝트 실행 환경과 DB 연결 기반 구축 (#54)`, 본문은 `Refs #50, #42`로 연결하고 자동 닫기를 사용하지 않는다. Task #50 완료를 부모 #42/Phase 완료로 전파하지 않는다.
- 병합 후 확인/정리: 실제 PR의 merged 상태·통합 commit 부모/제목·허용 일반 영역의 제출 head와 결과의 내용 일치, 추가/미보존 변경·의존하는 작업/PR 부재를 확인한다. 충족되면 로컬 부모를 fast-forward하고 이 Task의 원격/로컬 브랜치만 정리한다. 부모 Issue/Phase·main·로컬 보존 브랜치는 유지한다. 이 구역의 병합/정리 절차는 아직 실행 전 계획이며 정상 결과가 같으면 불필요한 추가 확인용 커밋을 만들지 않는다.

- 통합 기록 검수: 구현 `95cafce` 대비 인덱스 문서 4개를 자체·읽기 전용 별도 에이전트가 검수해 필수 결함을 발견하지 못했다. 인덱스/작업 파일 정규화 일치·로컬 참조/표식 79개·공백·Task 완료 상태를 확인했고 구현 소스는 변경되지 않았다. 실제 PR의 최초 head/base·CLEAN/MERGEABLE·검사/미해결 의견 부재는 주 진행자가 확인했으며 최종 head 갱신 후 병합 직전 다시 대조한다. 검수 결과 요약만 추가한 최종 후보의 일치를 자체 확인한다.
