# 루미아 아일랜드 위키

게임 정보와 패치 이력을 조회하고, 아이템 제작·수집 루트와 피해량 계산을 지원하기 위한 위키 프로젝트다.

## 목표 기능

- 아이템 등 게임 대상의 정보와 변경 이력 조회
- 개별 패치노트의 변경 내용 정리
- 장비 조합·재료 수집·배달을 고려한 루트 계산
- 게임 규칙에 따른 피해량 계산과 변경 조건의 성능 비교
- AI를 활용한 패치노트 데이터 변환

제품 범위·공개 조건과 기능별 요구는 [프로젝트 목표와 범위](<docs/프로젝트 목표와 범위.md#current>) 및 연결된 제품 문서에서, 단계별 실현 범위·순서는 [현황에서 연결한 Phase 계획](<work/현황.md#harness-record-separation>)에서 관리한다.

## 현재 상태

요구사항과 7개 Phase의 계획을 정리하고 웹·API 서버·개발 DB의 실행 기반을 구축하고 있다. 게임 자료와 검색·계산 등 제품 기능은 아직 구현하지 않았다.

현재 진행 상황과 다음 작업은 [작업 현황](<work/현황.md#current>)에서 확인한다. 기반 구축의 검증 결과와 남은 확인은 [Task 42-001](<work/records/phase-001/issue-42/task-001.md#implementation>)에 기록한다.

## 프로젝트 구성

| 위치 | 내용 |
|---|---|
| [AGENTS.md](<AGENTS.md>) | AI의 작업 진입 지침 |
| [STRUCTURE.md](<STRUCTURE.md>) | 주요 파일·폴더의 위치와 역할을 안내하는 지도 |
| `docs/` | 제품 요구사항과 프로젝트 운영 기준 |
| `harness/` | 작업 절차와 문서·기록 양식 |
| `work/` | 계획, 진행 현황, 실제 논의·작업·검증 기록 |
| `backend/` | Java 21·Spring Boot API 서버와 Gradle Wrapper |
| `frontend/` | React·TypeScript·Vite 시작 화면 |
| `db/migration/` | Flyway 공용 SQL 원천. 현재 게임 스키마는 미등록 |
| `compose.yaml` | PostgreSQL 로컬 개발 환경 |
| `scripts/` | 서버 실행기와 격리 기반 검증 도구 |
| `harness-design/` | 별도로 관리하는 하네스 설계 도구. 아래 접근 제한 적용 |

<a id="start"></a>

## 시작하기

AI와 작업할 때는 원하는 결과와 대상, 허용 범위를 전달한다. 기존 작업을 이어가는 경우 담당 기록이나 관련 파일을 함께 지정한다.

- 제품 목표와 범위: [프로젝트 목표와 범위](<docs/프로젝트 목표와 범위.md#current>)
- 작업 찾기와 재개: [work 안내](<work/README.md#start>), [작업 현황](<work/현황.md#current>)
- AI 작업 지침: [AGENTS.md](<AGENTS.md>)
- 공통 작업 절차: [공용 절차](<harness/공용 절차.md#entry>)
- 애플리케이션 개발 기준: [공통 개발 기준](<docs/개발 기준.md#current>)
- 프로젝트 구성: [스킬 현황](<harness/스킬 현황.md#current>) · [hook 현황](<harness/hook 현황.md#current>)

작업 결과와 변경 내용, 확인 범위·한계, 미해결 사항과 다음 행동은 대화와 담당 작업 기록에서 확인한다.

## 접근 제한: harness-design

**사용자의 명시적 요청 없이는 `harness-design/`에 접근하지 않는다.**

이 영역은 참고자료를 바탕으로 사용자와 설계를 결정하고 하네스를 생성·검증하기 위한 독립 도구다. 일반 위키 작업의 필수 입력으로 사용하지 않는다.

- 일반 작업의 읽기·검색·목록 조회·비교 대상에서 제외한다.
- 문서의 링크나 과거 지시를 따라 자동으로 접근하지 않는다.
- 접근 요청이 있으면 허용된 대상과 행동 범위에서만 수행한다.
- 현재 프로젝트 문서와 자동 비교·동기화하지 않는다.
- 새 위키 개발·운영 기록은 `work/`에서 관리한다.

관련 `.harness-state/`도 명시적으로 허용된 범위에서만 접근한다. 상세 기준은 [원천과 보존 경계](<docs/문서 관리 기준.md#harness-design-boundary>)를 따른다.

<a id="local-development"></a>
## 로컬 실행

JDK 21, Node.js 24 LTS, npm과 실행 중인 Docker Desktop의 Linux 엔진이 필요하다. Java는 기존 설치를 사용하고 Gradle은 저장소 Wrapper 9.9.1로 실행한다. 웹 직접 의존성은 manifest와 잠금 파일의 버전으로 설치한다.

1. `.env.example`을 루트 `.env`로 복사하고 `DB_PASSWORD`를 개인 값으로 바꾼다. `$` 등 특별 문자가 들어간 값은 작은따옴표로 감싸 Node와 Compose에서 동일하게 읽도록 한다. 비밀번호를 채팅·문서·Git에 넣지 않는다. `.env`는 자동 생성하거나 덮어쓰지 않는다.
2. `npm --prefix frontend ci`로 웹 의존성을 설치한다.
3. 다음 DB 명령을 실행한 뒤 API와 웹 명령을 각각 별도 터미널에서 실행한다.

```text
docker compose -p lumiawiki up -d --wait --wait-timeout 90 db
node --env-file=.env scripts/dev-api.mjs
npm --prefix frontend run dev
```

웹은 `http://localhost:5173/`, API 서버는 `http://127.0.0.1:8080`, DB는 `127.0.0.1:5432`를 사용한다. 현재 웹은 실행 확인용 정적 시작 화면이며 API 기능 경로는 후속 Task에서 마련한다. 포트가 이미 사용 중이면 기존 서비스를 종료하거나 임의 포트로 바꾸지 않고 실패한다. DB 포트는 `.env`의 `DB_PORT`, 서버 포트는 실행 환경의 `SERVER_PORT`로 조정할 수 있다. 개인 DB 환경값을 웹 프로세스에 전달하지 않는다.

서버 실행기는 Node의 기본 env-file 기능으로 접속값을 읽고 local 프로필을 명시한다. 누락/예제 비밀번호·잘못된 포트는 Java 시작 전에 거부한다. `JAVA_HOME`이 필요하면 기존 JDK 21 설치 경로로 지정한다. common/local/test 설정을 구분하며 테스트 전용 DB 연결·테스트/hook 환경은 Task 002의 담당이다.

## 빌드와 기반 확인

```text
npm --prefix frontend run typecheck
npm --prefix frontend run build
npm --prefix frontend run preview
node --test scripts/dev-api.test.mjs
node scripts/verify-bootstrap.mjs
```

빌드 화면은 `http://127.0.0.1:4173/`에서 확인한다. Windows 서버 빌드는 `backend\gradlew.bat -p backend bootJar`, 다른 환경에서는 `sh backend/gradlew -p backend bootJar`다. 생성 JAR는 `backend/build/libs/lumiawiki-api-0.0.1-SNAPSHOT.jar`다. 서버 단위/DB 테스트의 실행·자동 검사는 Task 002에서 연결하며 bootJar 통과가 테스트 완료를 뜻하지 않는다.

기반 검증 도구는 `.tmp/issue-42/task-001/`의 격리 복제본에만 합성 SQL을 만들어 JAR 포함·Flyway 적용·앱/DB 재시작 보존·잘못된 암호·실제 env-file/bootRun을 확인한다. 개발 DB에 합성 테이블을 만들지 않는다. 성공하면 소유를 확인한 임시 컨테이너/볼륨을 정리하고 비밀값 없는 결과·입력 지문을 남긴다. 실패하면 안내한 실행별 임시 경로와 재현 리소스를 유지한다. 실제 제품 SQL은 `db/migration/`에서 한 번만 관리하고 Gradle이 빌드 리소스에 포함한다.

일반 DB 종료는 `docker compose -p lumiawiki down`이며 named volume과 데이터를 보존한다. 볼륨을 삭제하는 초기화 명령은 일상 종료에 사용하지 않는다. 중요한 데이터를 삭제·초기화하기 전에는 별도 백업이 필요하다.
