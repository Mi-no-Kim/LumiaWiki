# Task 42-002 — 테스트 실행 환경·최소 TDD hook

<a id="summary"></a>
## 현재 요약

- 제목: 테스트 실행 환경·최소 TDD hook
- GitHub sub-issue: [Mi-no-Kim/LumiaWiki #51](https://github.com/Mi-no-Kim/LumiaWiki/issues/51)
- 부모 Issue: [Issue #42](<issue.md#summary>)
- 상태: 예정
- 현재 진행 위치: 테스트 버전·실행/근거 형식·hook 연결 방식을 확정했다. Node 업데이트·구현·실측은 미수행이다.
- 다음 행동: 구현 요청 시 Node 24.22.3 적용과 기존 기반 재검증부터 진행하고 아래 확정 명령·hook을 구현한다.

<a id="goal"></a>
## 목적과 허용 범위 및 완료 조건

[테스트 기준](<../../../../docs/details/development/테스트와 TDD.md#current>)과 [최소 hook 기준](<../../../../docs/details/development/TDD hook.md#minimum>)을 실제로 연결한다. Task 001의 웹·서버·환경 설정을 입력으로 삼는다.

- 서버 JUnit·Mockito·MockMvc, DB Testcontainers의 전용 `postgres:18.6`, 프런트 Vitest·React Testing Library와 DOM 환경을 연결한다. 테스트 상태를 분리하고 DB 없는 단위 테스트에 컨테이너를 강제하지 않는다.
- 테스트 실행 래퍼가 실제 실행된 테스트·결과·순서·작업/worktree·대상/테스트/설정/잠금 파일 지문을 기록한다. 테스트 미발견·환경 오류를 Red로 인정하지 않는다.
- 공유 읽기 전용 검사기를 Codex `PreToolUse`와 Git `pre-commit` 두 지점에 연결한다. 기존 hook·신뢰 설정을 보존하고 지원 트리거·해제 방법을 확인한다. 초기는 경로 판독 가능한 `apply_patch`를 대상으로 한다.
- Red 편집 허용권과 완료 사이클의 Red/Green 이력을 구별한다. Green 후 새 동작에는 새 Red/예외를 요구하고 코드·테스트·관련 설정 변경은 기존 Green을 무효화한다.
- 문서/환경 준비·순수 리팩터링·정정 예외와 부분 스테이징 후보 대조, 기검수 squash/merge·다른 worktree의 내용 대응/회귀 검증을 구현한다. 근거 보존은 담당 기록에 간결히 남기며 보존 영역을 사용하지 않는다.

완료 조건은 [hook 수용 사례 1~7](<../../../../docs/details/development/TDD hook.md#acceptance>)의 실제 정상/거부/미확인 판정, Windows·worktree 및 실제 Codex 편집/Git 커밋 경로의 동작, 개발 DB/볼륨과 테스트 DB의 분리, 후속 작업이 재사용할 명령·근거·예외/해제 안내다. 검사기 자체는 테스트·수정·커밋을 수행하지 않고 작업 상태도 바꾸지 않는다. 실제 커밋 경로 검증은 격리된 임시 저장소/후보로 수행한다.

<a id="plan"></a>
## 계획과 예정 검증

1. 아래 확정 버전을 설치·잠금하고 정상 테스트와 의도한 실패를 실행한다. 초기 환경 예외와 검사기 자신의 동작 개발에 필요한 TDD 근거를 구분한다.
2. 유효 Red·Green·예외/통합 근거의 상태 전이와 후보 내용 대응을 작은 검사 단위로 구현한다. 모든 쓰기 경로를 차단한다고 주장하지 않는다.
3. 아래 목록과 공식 수용 사례를 같은 입력으로 자동 검사·직접 경로 실행에 연결한다. 테스트 시간과 hook 시간은 분리한다.
4. TDD 검사 비용은 AI/서브에이전트/네트워크 0회, 전체 저장소 탐색 없이 명시 대상만 읽기, 호출당 3초 이내 목표, 성공 무출력·실패 5줄 이내를 실측한다. 초과·판정 불능은 미확인으로 처리하고 범위/실행 시점을 조정한다. Task 004의 포맷 비용은 별도다.

### 구현 전 공유할 사용자 확인 목록

| 준비·조작 | 기대 결과 |
|---|---|
| 격리된 동작 예제에서 Red 없이 편집, 실제 Red 후 편집 | 최초 거부·유효 Red 후 허용. 테스트 작성·조회는 허용 |
| Green 후 같은 과거 Red로 새 편집, 이후 코드/테스트/설정 변경 | 새 사이클 요구·기존 Green 재사용 거부 |
| 유효한 검증 후보와 같은/다른 부분 스테이징을 제출 검사 | 동일 후보 허용·미검증 후보는 미확인. 자동 수정/스테이징 없음 |
| 테스트 0개·Docker 실패·대화상 통과 선언, 문서/등록 예외 | 가짜 Red/Green 생성 불가·적법한 비동작 흐름은 통과 |
| 격리 worktree/통합 후보에서 원본 지문·근거 비교 | 진행 중 Red 권한 공유 금지·유효 통합 근거 승계·누락/변경은 추가 확인 |
| 테스트 DB 실행과 hook 해제/복원 | 개발 DB 보존·기존 hook 유지·실행 비용/실패 안내 확인 |

실제 명령·대상 경로·지원 설정은 구현 전에 공유한다. 실제 사용자 확인은 미수행이다. 커밋 전 자체·별도 검수는 [공통 검수 절차](<../../../../.agents/skills/review-work/SKILL.md#before-commit>)를 따른다.

<a id="implementation-decisions"></a>
## 확정한 구현 세부 사항 — 2026-11-12

사용자의 남은 Task 일괄 결정 요청을 #42의 실행 준비로 처리했다. 이 설계 결정 당시 새 작업 단위·브랜치·설치·구현·커밋은 만들지 않았다. 아래는 구현 기준이며 실행 성공의 근거가 아니다. 이후 검수·커밋·전환은 부모 Issue의 후속 기록과 구별한다.

### 환경·테스트 명령

| 항목 | 확정 기준 |
|---|---|
| Node·npm | 사용자 선택은 Node **24.22.3 LTS** 업데이트, npm **11.19.1** 유지. jsdom 31의 Node 조건 `^24.15.0`을 충족한다. 현재 설치 24.13.0과 구별하며 Task 001의 당시 검증 버전을 소급 변경하지 않음 |
| 프런트 테스트 | Vitest **5.1.0**, jsdom **31.0.0**, `@testing-library/react` **16.3.3**, DOM **10.4.2**, jest-dom **7.0.1**, user-event **14.6.9**. 정확한 버전과 잠금 파일을 함께 관리 |
| 서버 테스트 | Boot 4.1.2의 관리 버전 사용: JUnit Jupiter **6.0.3**, Mockito **5.23.0**, Testcontainers **2.0.5**. `spring-boot-testcontainers`·JUnit/PostgreSQL 모듈을 연결하고 별도 버전 override를 하지 않음 |
| 테스트 DB | `postgres:18.6`, `@ServiceConnection`, 임의 포트·테스트 컨텍스트 단위 컨테이너. reuse·고정 포트·개발 `.env`·개발 볼륨을 사용하지 않음 |
| DB 확인 사례 | 생성된 contextLoads를 test 프로필·integration 태그로 전환. test 전용 Flyway 위치에 반복 마이그레이션 `R__test_connection_probe.sql`을 두고 JDBC 쓰기/읽기를 확인. 제품 migration·엔티티·JAR에는 합성 테이블을 넣지 않음 |
| 프런트 명령 | `npm --prefix frontend run test` → `vitest run`, `test:watch` → `vitest`. jsdom·jest-dom 설정, 테스트별 cleanup/mock 복원·독립 QueryClient. 초기 커버리지 수치·snapshot 의무 없음 |
| 서버 명령 | backend Wrapper `test`는 integration 태그 제외, `integrationTest`는 같은 테스트 소스에서 integration 태그만 실행. DB 없는 테스트에 Docker를 강제하지 않음 |
| 도구 테스트 | 기존 `node --test scripts/dev-api.test.mjs` 유지. Python 도구는 표준 `unittest` 사용. Node 변경 뒤 기존 도구 테스트·프런트 `npm ci`/typecheck/build·서버 실행기의 환경 전달을 재확인 |

### 검사기·근거·연결

- Python **3.14 계열 표준 라이브러리**로 `scripts/tdd-run.py`(실행/기록), `scripts/tdd-check.py`(읽기 전용), `scripts/install-hooks.py`(설치/복원)를 분리한다. 현재 로컬 3.14.2를 재사용한다. 별도 Python 패키지·가상 환경은 요구하지 않는다.
- 실행 계약은 `python -X utf8 scripts/tdd-run.py --task <기록> --cycle <식별자> --phase red|green -- <명령과 인수>`, 후보 검사는 `python -X utf8 scripts/tdd-check.py --candidate index|<commit>`으로 한다. 실제 구현 때 도움말·실행 사례를 제공한다.
- 사이클 입력은 담당 Task의 fenced JSON 구역에 식별자·기대 동작·대상/테스트 경로·명령 배열·예상 실패·예외 사유를 기록한다. 별도 계획 원본은 만들지 않는다. 실행 결과는 `.tmp/issue-42/task-002/tdd/<worktree-식별자>/`에 두되 다른 Task는 자기 임시 위치를 사용한다.
- 결과 어댑터는 JUnit XML(Gradle·Node JUnit reporter), Vitest JSON, Python unittest JSON이다. Python은 표준 `TestResult`를 확장한 작은 reporter를 두어 실행 식별자·실행 수·assertion failure·error·skip을 출력하고 tdd-run이 읽는다. 매 실행의 새 보고서·실행 수·지정 테스트 assertion 실패를 대조한다. 기존 보고서·Gradle 실행 생략·컴파일/기동 오류·0개 테스트는 Red/Green이 아니다. 기대 실패의 의미는 사람이 검수한다.
- 최초 래퍼/reporter 연결은 초기 테스트 환경 준비로 기록하고 검사기의 동작 구현과 구별한다. 자기 실행 경로가 준비되기 전 도구 동작의 실제 unittest 실패/통과는 실행 명령·순서·실행 수·실패 이유·기준 commit·파일 지문과 함께 담당 기록에 보존해 검수한다. 연결 뒤 같은 통제 fixture를 래퍼로 새로 실행해 자기 검증하되, 이전 실행을 사후 생성한 기계 Red/Green으로 표시하지 않는다. 이 경계는 제품 기능의 hook 선행 조건을 면제하지 않는다.
- SHA-256으로 대상·테스트·관련 설정·잠금 파일 내용을 묶고 실행 순서·기준 commit·명령·worktree를 기록한다. Red 권한은 현재 worktree/사이클만 소유하며 Green 뒤 종료한다. 최종 후보의 최소 근거는 담당 기록에 보존하고 임시 파일 없이도 다시 대조할 수 있게 한다.
- 동작 경로는 backend main·frontend src·실행 도구·DB SQL과 동작 설정을 명시한다. 테스트 작성·문서·정적 디자인·초기 환경 준비는 기존 예외를 따른다. 미분류 변경은 자동 면제하지 않는다. 부분 스테이징은 실제 index 내용/설정, PR은 실제 commit을 읽으며 작업 파일의 Green을 무조건 재사용하지 않는다.
- Codex는 추적하는 `.codex/hooks.json`의 `PreToolUse`/`apply_patch` 연결을 사용한다. 실행 위치가 하위 폴더여도 Git 루트를 구해 절대 경로로 검사기를 실행하고 Windows 명령을 별도 지정한다. TDD PreToolUse의 외부 제한 시간은 5초, 내부 판정 제한은 3초로 둔다. 내부 제한 전에 판정할 수 없으면 명시적 거부 응답으로 미확인을 반환한다. 프로세스 종료·Codex 자체 시간 초과가 편집을 허용할 수 있으므로 이를 거부 성공으로 기록하지 않고 실제 경로에서 구별해 검증한다. 해당 지원 미확인은 첫 기능 착수 조건을 충족하지 않는다.
- Git 설치기는 유효 hook 위치·기존 내용/해시를 확인·백업하고 **기존 hook → TDD 검사** 순서로 연결한다. 전역 설정을 바꾸거나 기존 hook을 덮어쓰지 않는다. 중복 설치는 무변경, 해제는 자기 wrapper가 그대로인 경우만 복원한다. worktree마다 실행 루트를 구하고 근거를 분리한다.
- 프로젝트 신뢰와 hook 정의의 신뢰는 실제 사용자 환경에서 확인한다. 기존 사용자/플러그인 hook도 합쳐질 수 있으므로 설정 파일 부재만으로 hook 부재를 단정하지 않는다. 자동 신뢰·우회 옵션·Stop hook은 추가하지 않는다. Task 004는 같은 Git 진입점 뒤에 읽기 전용 형식 검사를 연결한다.

### 결정 완료와 실행 확인의 경계

선택해야 할 버전·명령·저장 형식·연결 방식은 정했다. 현재 Codex 데스크톱의 실제 trigger/신뢰 동작, 기존 hook과의 공존, Windows/worktree·부분 후보·통합 근거·실측 비용은 위 수용 사례로 구현 시 확인한다. 지원 불가/실측 실패는 해당 근거와 대안을 반환하며 자동 통과시키지 않는다. **이 Task의 필수 검증 전에는 첫 제품 기능 동작 구현을 시작하지 않는다.**

근거: [Node 배포 목록](https://nodejs.org/dist/index.json) · [jsdom 31 메타데이터](https://registry.npmjs.org/jsdom/31.0.0) · [Vitest 환경](https://vitest.dev/guide/environment) · [Boot Testcontainers](https://docs.spring.io/spring-boot/reference/testing/testcontainers.html) · [Codex 공식 hooks](https://learn.chatgpt.com/docs/hooks). 버전/peer 조건은 2026-11-12 npm registry·Boot BOM을 조회한 결과이며 설치·실행은 미수행이다.
