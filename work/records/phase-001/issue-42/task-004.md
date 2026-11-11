# Task 42-004 — 코드·문서 검사·포맷·CI 연결

<a id="summary"></a>
## 현재 요약

- 제목: 코드·문서 검사·포맷·CI 연결
- GitHub sub-issue: [Mi-no-Kim/LumiaWiki #53](https://github.com/Mi-no-Kim/LumiaWiki/issues/53)
- 부모 Issue: [Issue #42](<issue.md#summary>)
- 상태: 예정
- 현재 진행 위치: 도구 버전·명령·포맷 연결·CI 트리거/영향 영역/runner를 확정했다. 설정·CI 실행은 미수행이다.
- 다음 행동: Task 002의 검증된 hook에 아래 품질 검사를 연결하고 Task 003까지 포함한 최종 후보로 CI를 검증한다.

<a id="goal"></a>
## 목적과 허용 범위 및 완료 조건

[코드 품질 기준](<../../../../docs/details/development/코드 품질.md#current>)과 [기술 인계](<../issue-15/artifacts/task-003-handoff.md#handoff-decisions>)를 로컬·제출 후보·CI에서 실행할 수 있게 한다.

- 서버 Spotless·google-java-format, 프런트 Prettier·ESLint/React Hooks·eslint-config-prettier·별도 TypeScript 타입 검사를 연결한다. TypeScript 7.0.2의 `@typescript/native` alias와 `typescript` 이름의 `@typescript/typescript6` 6.0.x 병행은 실제 배포·API 호환성을 확인한다. 두 컴파일러로 타입 검사를 중복하지 않는다.
- 루트 도구와 단일 Prettier 버전으로 `npm run format`, `format:docs`, `format:check`를 마련한다. Markdown proseWrap preserve·embeddedLanguageFormatting off를 적용한다.
- 관리 대상은 현재 안내·docs·harness·work와 제품 코드의 명시 허용 목록이다. 보존 영역은 경로 수집 전 제외하고 원자료·과거 원문/검증 첨부·SQL·잠금 파일·생성/빌드/캐시는 자동 수정하지 않는다.
- `apply_patch` 후 `PostToolUse`는 허용된 해당 파일만 포맷하고, 저장 시 포맷·명시 명령과 함께 사용한다. 기존 TDD hook 뒤 별도 단계로 연결하고 후보 형식 검사는 읽기 전용으로 인덱스 내용/설정을 확인한다. 자동 스테이징·hook의 테스트/설치/AI/네트워크 호출·상시 감시기는 추가하지 않는다.
- 로컬 명령과 잠금 파일/Wrapper를 입력으로 CI 검사·테스트·빌드를 독립 실행한다. 영향 영역은 프런트·서버/DB·문서/공통 도구를 구별하고 공통 설정 변경은 필요한 양쪽 검사를 실행한다. 저장소 보호 옵션은 바꾸지 않는다.

완료 조건은 TSX/Hooks 정상·실패의 타입/lint 검증, 문서/Java 생성·수정 후 포맷 및 일괄 재실행 무변경, 부분 스테이징·실패/중복 호출·기존 hook 보존·지문 대응, 명령별 안내·실측 비용, 실제 CI 정상 통과와 통제한 검사/테스트 실패 반영이다. CI 통과는 TDD·별도 검수·Task 수용을 대신하지 않는다.

<a id="plan"></a>
## 계획과 예정 검증

1. 아래 확정 설계에 Task 002 hook·실행 결과 계약을 연결한다. GitHub Actions를 채택하며 현재 구현·실행된 사실과 구별한다.
2. 확정 버전·허용 파일 목록·실행기로 로컬 정상/실패를 확인한다. TypeScript 병행 구성을 바꿀 필요가 있으면 공식 직접 지원 근거와 호환 실행으로 판단한다.
3. 포맷의 경로 정규화·범위 밖 쓰기·재귀/중복 호출을 확인한다. 보존 영역 제외는 허용/거부 경로의 합성 입력으로 확인하며 실제 영역을 읽거나 열거하지 않는다. 임시 복제 검증용 원자료의 바이트도 대조한다.
4. Windows의 포맷/Gradle 시간과 TDD 검사 시간을 분리해 기록한다. 성공 무출력·짧은 실패 안내, 시간 초과/경로 판독 불능의 미확인·제출 차단·편집 복구를 확인한다. 포맷 후 내용으로 검사/테스트 근거를 다시 맞춘다.
5. 준비된 명령을 CI에 연결한다. Task 003 결과도 포함한 최종 기반 후보로 정상 실행과 격리된 실패 후보의 검사/테스트 실패를 확인하고 run·commit·판정을 남긴다. 실제 원격 실행 권한이 없으면 로컬 성공으로 대체하지 않고 잔여로 반환한다.

### 구현 전 공유할 사용자 확인 목록

| 준비·조작 | 기대 결과 |
|---|---|
| 허용 문서/Java 예제 생성·수정, 일괄 포맷 반복 | 대상만 포맷·재실행 무변경·보존/원자료 미접근 |
| 유효/무효 TSX·Hooks 예제와 부분 스테이징 후보 검사 | 올바른 타입/lint 엔진으로 정상/실패 판정·후보 내용 기준 검사 |
| 포맷 실패·중복 호출·시간 초과의 통제된 재현 | 조용한 성공·명확한 실패·임의 설치/수정/재시도 없음·기존 hook 유지 |
| CI 정상 후보와 통제한 검사/테스트 실패 후보 실행 | 독립 설치/검사/테스트/빌드 성공과 해당 실패가 run에 반영 |

실제 명령·트리거·후보 주소는 구현 전에 공유한다. 현재 자동 검사·AI 직접 실행·사용자 확인은 미수행이다. 제출 전 [자체·별도 검수](<../../../../.agents/skills/review-work/SKILL.md#before-commit>)를 적용한다.

<a id="implementation-decisions"></a>
## 확정한 구현 세부 사항 — 2026-11-12

이 구역은 #42의 실행 준비에서 확정한 설계다. 결정 당시 설정 작성·설치·원격 CI 실행·커밋은 수행하지 않았다.

### 도구·명령·포맷

| 항목 | 확정 기준 |
|---|---|
| 프런트/문서 | 루트 Prettier **3.10.0** 단일 설치. frontend ESLint **10.14.0**, `@eslint/js` **10.0.1**, typescript-eslint **8.72.2**, react-hooks **7.1.1**, eslint-config-prettier **10.1.8** |
| TypeScript | 기존 `@typescript/native: npm:typescript@7.0.2`의 tsc 유지. lint API는 `typescript: npm:@typescript/typescript6@6.0.2`. flat config `eslint.config.mjs`, JS/TS 권장 규칙·React Hooks 적용. typecheck는 7.0.2로 한 번 |
| Java | Gradle Spotless **8.11.0** + google-java-format **2.0.0**, Java 21. `spotlessApply`·`spotlessCheck` 연결. Gradle/기존 도구 외 별도 분석 서버 없음 |
| 루트 명령 | `format`, `format:docs`, `format:check`, `check:frontend`, `check:backend`, `test:tools`, `check`. `check`는 format:check → 도구 테스트 → frontend 검사 → backend 검사로 실행하며 실패 시 중단 |
| 영역별 검사 | frontend는 lint·Vitest run·build(기존 build에 typecheck가 포함되므로 별도 중복 실행하지 않음), backend는 spotlessCheck·test·integrationTest·bootJar. 독립 typecheck 명령은 유지. test:tools는 Node 기본 테스트와 Python unittest. Docker는 backend 통합 검사 때만 필요 |

- Node 실행기에서 관리 파일 허용 목록을 공유한다. 루트 현재 안내(AGENTS/README/STRUCTURE), 루트 package.json·Prettier 설정·compose.yaml, `.github/workflows/`·`.codex/hooks.json`·저장소 편집기 설정, 현재 docs/harness/work Markdown·JSON·YAML, scripts의 JS/MJS/JSON, frontend의 소스/설정·HTML/CSS, backend Java·관리 YAML을 포함한다. Python은 단위 테스트·문법 검사로 확인하며 Prettier에 넘기지 않는다. Markdown 옵션은 기존 기준을 따른다.
- 보존 영역은 파일 수집 전에 제외한다. 원자료·과거 원문/검증 첨부·`artifacts/`와 별도 표시한 증거 경로, SQL·잠금 파일·Wrapper·생성물·캐시는 자동 포맷하지 않는다. 허용 목록 밖 추가 파일은 분류를 요구한다. 제외 폴더의 실제 열거 대신 합성 경로로 차단을 검증한다.
- `.codex/hooks.json`의 `PostToolUse`/`apply_patch`는 정규화한 변경 파일 중 허용된 생존 파일만 포맷한다. 파일별 잠금·재진입 방지, 성공 무출력·짧은 실패 안내를 적용한다. 서버 파일은 대상 한정 Spotless 실행 경로를 구현·검증한다. 불가능하면 전체 서버 자동 실행으로 넓히지 않고 조정안을 반환한다.
- 편집기 저장 시 Prettier/Java 포맷 안내와 설정을 제공한다. Git 진입점은 기존 hook → TDD → 읽기 전용 형식 검사 순서다. 부분 스테이징은 index의 내용·설정에 대응하는 임시 후보에서 확인하고 작업 파일을 고치거나 자동 stage하지 않는다.
- hook은 미리 설치된 도구만 쓴다. 사전 준비 명령으로 Java formatter 의존성도 받아 두고 hook에서는 Gradle offline으로 실행한다. 자동 다운로드·설치·재시도는 하지 않는다. PostToolUse는 파일을 모아 Prettier/Java를 각각 한 번 호출하고 내부 제한을 15초/60초, 합산 제한 80초·외부 hook 제한 90초의 초기값으로 둔다. Task 002의 PreToolUse 5초와 다른 설정이며 실제 비용을 따로 기록한다. 비용 초과·실패는 미확인/제출 차단이며 이미 한 편집은 복구할 수 있다. TDD 3초 목표와 따로 측정한다.

### CI 계약

- GitHub Actions `.github/workflows/quality.yml`, runner **ubuntu-24.04**, Node **24.22.3**·npm **11.19.1**, Temurin **21**, Python **3.14.2**, 저장소 Gradle Wrapper를 사용한다. 로컬 Oracle JDK를 교체하지 않는다. 루트/frontend는 각각 잠금 파일과 `npm ci`를 사용한다.
- 사용자 선택: PR `opened/synchronize/reopened`(대상 `main`, `phase/**`, `issue/**`), 해당 부모 브랜치 `push`, `workflow_dispatch`. Task 브랜치의 모든 push에는 실행하지 않는다. 수동 실행은 전체 영역 검사다.
- 기본 브랜치는 `main`이며 현재 workflow가 없다. GitHub의 수동 실행은 workflow가 기본 브랜치에도 있어야 활성화된다. Task 004에서는 트리거 선언과 PR/부모 push의 실제 실행을 검증하고, 수동 실행 실측은 [Phase의 main 통합 뒤 확인](<../phase.md#ci-manual-followup>)으로 연결한다. 수동 실행을 위해 main에 선행 병합하는 범위는 이번 계획에 추가하지 않는다.
- workflow 전체의 paths 필터는 사용하지 않는다. `changes` → `tools`/`docs`/`frontend`/`backend` → 항상 실행하는 `quality` 집계 job으로 구성한다. 집계는 필요한 job의 성공과 의도한 skip만 허용하고 실패/취소/분류 오류를 성공으로 바꾸지 않는다. 수동 실행·비교 기준 누락·분류 불능은 전체 검사한다.
- PR은 base/head 차이, push는 before/after 차이를 사용하고 rename/delete의 양쪽 경로를 반영한다. 경로 분류 전에 보존 영역을 제외한다. frontend 변경은 frontend, backend·db 변경은 backend, docs/harness/work·현재 안내는 docs, 공통 scripts·hook·품질/CI/루트 설정·잠금 변경은 tools와 관련 양쪽 검사를 실행한다. 미분류 경로는 전체 검사한다. 프로젝트 검사에는 해당 영역 전체 테스트·빌드를 포함한다.
- CI는 위 로컬 명령을 독립 실행한다. 로컬 worktree의 임시 TDD 근거·개인 `.env`를 요구하거나 가짜 Red를 만들지 않는다. TDD 제출 근거 확인은 기존 로컬/PR 검수 절차를 유지한다. CI에서 커밋 hook은 설치하지 않는다.
- 권한은 `contents: read`, 같은 ref의 오래된 실행은 concurrency로 취소한다. 배포·비밀값 입력·보호 설정 변경은 없다. npm/Gradle 캐시는 잠금/빌드 설정을 기준으로 사용하고 실패 시 테스트 보고서만 7일 보관한다. 개인 환경·DB 암호·전체 로그를 artifact에 넣지 않는다.
- 정상 최종 후보의 전체 통과와 격리된 lint/테스트 실패 PR의 해당 실패를 확인한다. run URL·commit·job 판정을 기록하며 검증 PR은 본류에 병합하지 않는다. 실제 브랜치/게시 작업은 Task 구현 요청의 허용 범위와 기존 Git 절차로 처리한다.

### Actions 고정 버전

태그의 공식 commit을 2026-11-12 조회했다. 구현에서는 전체 SHA로 고정하고 옆에 버전을 표시한다. 설치/runner 실행 호환성은 아직 검증하지 않았다.

| Action | 버전 | SHA |
|---|---|---|
| actions/checkout | v7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| actions/setup-node | v7.1.0 | `949feb2413d6458794dcd2491c4babbbce0c15c1` |
| actions/setup-java | v6.2.0 | `77dd5b2ce225ea11469928ac317850245a74ae78` |
| actions/setup-python | v7.1.0 | `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` |
| gradle/actions/setup-gradle | v6.4.1 | `8da46b539cd8fe6ab27ca75128919a18d757604c` |
| actions/upload-artifact | v7.0.2 | `cf430e030ddbb5b0abf93d22962f4752f3646cd9` |

선택할 도구·실행 시점·명령·범위는 정했다. 실제 TS API 병행·부분 후보·자동 포맷/복원·비용·CI 성공/실패는 구현 시 확인한다. 근거: [GitHub 이벤트·수동 실행 조건](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch) · [Spotless Gradle](https://github.com/diffplug/spotless/tree/main/plugin-gradle) · [google-java-format 2.0.0](https://github.com/google/google-java-format/tree/v2.0.0) · [기존 품질 기준](<../../../../docs/details/development/코드 품질.md#current>). npm/Maven/공식 action 태그 조회는 실행 성공 근거와 구별한다.
