# Task 42-004 구현 계약과 확인

[담당 Task](../task-004.md#summary)

<a id="implementation-decisions"></a>

## 확정한 구현 세부 사항

이 구역은 #42의 실행 준비에서 확정한 설계다. 결정 당시 설정 작성·설치·원격 CI 실행·커밋은 수행하지 않았다.

### 도구·명령·포맷

| 항목        | 확정 기준                                                                                                                                                                                                                                                              |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 프런트/문서 | 루트 Prettier **3.10.0** 단일 설치. frontend ESLint **10.14.0**, `@eslint/js` **10.0.1**, typescript-eslint **8.72.2**, react-hooks **7.1.1**, eslint-config-prettier **10.1.8**                                                                                       |
| TypeScript  | 기존 `@typescript/native: npm:typescript@7.0.2`의 tsc 유지. lint API는 `typescript: npm:@typescript/typescript6@6.0.2`. flat config `eslint.config.mjs`, JS/TS 권장 규칙·React Hooks 적용. typecheck는 7.0.2로 한 번                                                   |
| Java        | Gradle Spotless **8.11.0** + google-java-format **2.0.0**, Java 21. `spotlessApply`·`spotlessCheck` 연결. Gradle/기존 도구 외 별도 분석 서버 없음                                                                                                                      |
| 루트 명령   | `format`, `format:docs`, `format:check`, `check:frontend`, `check:backend`, `test:tools`, `check`. `check`는 format:check → 도구 테스트 → frontend 검사 → backend 검사로 실행하며 실패 시 중단                                                                         |
| 영역별 검사 | frontend는 lint·Vitest run·build(기존 build에 typecheck가 포함되므로 별도 중복 실행하지 않음), backend는 spotlessCheck·test·integrationTest·bootJar. 독립 typecheck 명령은 유지. test:tools는 Node 기본 테스트와 Python unittest. Docker는 backend 통합 검사 때만 필요 |

- Node 실행기에서 관리 파일 허용 목록을 공유한다. 루트 현재 안내(AGENTS/README/STRUCTURE), 루트 package.json·Prettier 설정·compose.yaml, `.github/workflows/`·`.codex/hooks.json`·저장소 편집기 설정, 현재 docs/harness/work Markdown·JSON·YAML, scripts의 JS/MJS/JSON, frontend의 소스/설정·HTML/CSS, backend Java·관리 YAML을 포함한다. Python은 단위 테스트·문법 검사로 확인하며 Prettier에 넘기지 않는다. Markdown 옵션은 기존 기준을 따른다.
- 보존 영역은 파일 수집 전에 제외한다. 원자료·과거 원문/검증 첨부·`artifacts/`와 별도 표시한 증거 경로, SQL·잠금 파일·Wrapper·생성물·캐시는 자동 포맷하지 않는다. 허용 목록 밖 추가 파일은 분류를 요구한다. 제외 폴더의 실제 열거 대신 합성 경로로 차단을 검증한다.
- `.codex/hooks.json`의 `PostToolUse`/`apply_patch`는 정규화한 변경 파일 중 허용된 생존 파일만 포맷한다. 파일별 잠금·재진입 방지, 성공 무출력·짧은 실패 안내를 적용한다. 서버 파일은 대상 한정 Spotless 실행 경로를 구현·검증한다. 불가능하면 전체 서버 자동 실행으로 넓히지 않고 조정안을 반환한다.
- 편집기 저장 시 Prettier/Java 포맷 안내와 설정을 제공한다. Git 진입점은 기존 hook → TDD → 읽기 전용 형식 검사 순서다. 부분 스테이징은 index의 내용·설정에 대응하는 임시 후보에서 확인하고 작업 파일을 고치거나 자동 stage하지 않는다.
- hook은 미리 설치된 도구만 쓴다. 사전 준비 명령으로 Java formatter 의존성도 받아 두고 hook에서는 Gradle offline으로 실행한다. 자동 다운로드·설치·재시도는 하지 않는다. PostToolUse는 파일을 모아 Prettier/Java를 각각 한 번 호출하고 내부 제한을 15초/60초, 합산 제한 80초·외부 hook 제한 90초의 초기값으로 둔다. Task 002의 PreToolUse 5초와 다른 설정이며 실제 비용을 따로 기록한다. 비용 초과·실패는 미확인/제출 차단이며 이미 한 편집은 복구할 수 있다. TDD 3초 목표와 따로 측정한다.

### CI 계약

- GitHub Actions `.github/workflows/quality.yml`, runner **ubuntu-24.04**, Node **24.22.3**·npm **11.19.1**, Temurin **21**, Python **3.14.2**, 저장소 Gradle Wrapper를 사용한다. 로컬 Oracle JDK를 교체하지 않는다. 루트/frontend는 각각 잠금 파일과 `npm ci`를 사용한다.
- 사용자 선택: PR `opened/synchronize/reopened`(대상 `main`, `phase/**`, `issue/**`), 해당 부모 브랜치 `push`, `workflow_dispatch`. Task 브랜치의 모든 push에는 실행하지 않는다. 수동 실행은 전체 영역 검사다.
- 기본 브랜치는 `main`이며 현재 workflow가 없다. GitHub의 수동 실행은 workflow가 기본 브랜치에도 있어야 활성화된다. Task 004에서는 트리거 선언과 PR/부모 push의 실제 실행을 검증하고, 수동 실행 실측은 [Phase의 main 통합 뒤 확인](../phase.md#ci-manual-followup)으로 연결한다. 수동 실행을 위해 main에 선행 병합하는 범위는 이번 계획에 추가하지 않는다.
- workflow 전체의 paths 필터는 사용하지 않는다. `changes` → `tools`/`docs`/`frontend`/`backend` → 항상 실행하는 `quality` 집계 job으로 구성한다. 집계는 필요한 job의 성공과 의도한 skip만 허용하고 실패/취소/분류 오류를 성공으로 바꾸지 않는다. 수동 실행·비교 기준 누락·분류 불능은 전체 검사한다.
- PR은 base/head 차이, push는 before/after 차이를 사용하고 rename/delete의 양쪽 경로를 반영한다. 경로 분류 전에 보존 영역을 제외한다. frontend 변경은 frontend, backend·db 변경은 backend, docs/harness/work·현재 안내는 docs, 공통 scripts·hook·품질/CI/루트 설정·잠금 변경은 tools와 관련 양쪽 검사를 실행한다. 미분류 경로는 전체 검사한다. 프로젝트 검사에는 해당 영역 전체 테스트·빌드를 포함한다.
- CI는 위 로컬 명령을 독립 실행한다. 로컬 worktree의 임시 TDD 근거·개인 `.env`를 요구하거나 가짜 Red를 만들지 않는다. TDD 제출 근거 확인은 기존 로컬/PR 검수 절차를 유지한다. CI에서 커밋 hook은 설치하지 않는다.
- 권한은 `contents: read`, 같은 ref의 오래된 실행은 concurrency로 취소한다. 배포·비밀값 입력·보호 설정 변경은 없다. npm/Gradle 캐시는 잠금/빌드 설정을 기준으로 사용하고 실패 시 테스트 보고서만 7일 보관한다. 개인 환경·DB 암호·전체 로그를 artifact에 넣지 않는다.
- 정상 최종 후보의 전체 통과와 격리된 lint/테스트 실패 PR의 해당 실패를 확인한다. run URL·commit·job 판정을 기록하며 검증 PR은 본류에 병합하지 않는다. 실제 브랜치/게시 작업은 Task 구현 요청의 허용 범위와 기존 Git 절차로 처리한다.

### Actions 고정 버전

태그의 공식 commit을 조회했다. 구현에서는 전체 SHA로 고정하고 옆에 버전을 표시한다. 계약 확정 당시 설치/runner 실행 호환성은 미검증이었으며 현재 결과는 아래 실제 CI 근거를 따른다.

| Action                      | 버전   | SHA                                        |
| --------------------------- | ------ | ------------------------------------------ |
| actions/checkout            | v7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| actions/setup-node          | v7.1.0 | `949feb2413d6458794dcd2491c4babbbce0c15c1` |
| actions/setup-java          | v6.2.0 | `77dd5b2ce225ea11469928ac317850245a74ae78` |
| actions/setup-python        | v7.1.0 | `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` |
| gradle/actions/setup-gradle | v6.4.1 | `8da46b539cd8fe6ab27ca75128919a18d757604c` |
| actions/upload-artifact     | v7.0.2 | `cf430e030ddbb5b0abf93d22962f4752f3646cd9` |

선택할 도구·실행 시점·명령·범위는 정했다. 실제 TS API 병행·부분 후보·자동 포맷/복원·비용·CI 성공/실패는 구현 시 확인한다. 근거: [GitHub 이벤트·수동 실행 조건](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch) · [Spotless Gradle](https://github.com/diffplug/spotless/tree/main/plugin-gradle) · [google-java-format 2.0.0](https://github.com/google/google-java-format/tree/v2.0.0) · [기존 품질 기준](<../../../../docs/details/development/코드 품질.md#current>). npm/Maven/공식 action 태그 조회는 실행 성공 근거와 구별한다.

<a id="verification"></a>
## 현재 확인과 잔여

- 부모 기준 `8a21c74`에서 작업한다. 신규 제품 기능·게임 자료·배포·저장소 보호 설정은 변경 범위에 없다.
- 로컬 프런트 lint·13개 테스트·TypeScript 7.0.2 타입 검사/제품 빌드, 서버 포맷·단위 9개·격리 DB 통합 1개·bootJar를 확인했다. 정확한 최종 후보와 실제 CI는 아래 후속 결과로 대응한다.
- 실제 TSX 정상 후보의 lint/typecheck는 0, 잘못된 타입과 조건부 Hooks 후보는 각각 TS2322·react-hooks/rules-of-hooks로 1이었다. 합성 파일은 제거했다. lint는 설치된 6.0.2 API를 사용하고 타입 명령은 native alias의 7.0.2 실행 파일을 명시한다.
- Java 범위 시험에서 spotlessFiles 속성은 설치 버전에서 다른 합성 파일까지 포맷했다. 공식 spotlessIdeHook의 절대 경로 목록으로 변경한 뒤 대상 포맷·다른 파일 바이트 보존·재실행 무변경을 확인했다. offline 준비 후 1개 파일 호출은 1455ms였다. 합성 Java 두 파일은 제거했다.
- 루트 Prettier는 기존 checkout 줄바꿈을 존중하는 endOfLine auto와 proseWrap preserve·embeddedLanguageFormatting off를 사용한다. 최초 적용 중 한 TSX 체인의 두 번째 명시 포맷이 필요했고, 이후 전체 무변경 여부를 다시 확인한다.
- 기존 하네스 CI의 부모 record blob 준비 코드는 의미를 보존해 scripts/quality/record-base.py로 추출했다. 새 품질 테스트에 필요한 Node·루트 잠금 설치와 선언된 backend 의존 경로를 기존 sparse checkout에 추가한다.
- 기존 PreToolUse는 실제 apply_patch를 유효한 예외 입력이 없다는 이유로 거부했다. 입력을 갱신·활성화한 뒤 동일 편집을 허용했다. 새 PostToolUse는 실행기 직접/격리 시험과 현재 대화의 자동 실행을 구별한다. 실제 apply_patch의 합성 JSON은 자동 포맷되지 않았고 제거했으며, 새 정의의 검토·신뢰와 실제 호스트 재확인은 남아 있다. 기존 신뢰를 자동 수정하거나 우회하지 않는다.
- 도구의 초기 Red 12개, 실제 hook 전달/시간 초과 Red 2개→Green과 현재 입력 회귀는 [정식 TDD 기록](task-004-tdd.md)에 보존한다. 완료하지 않은 호스트·원격 CI 확인은 성공으로 표시하지 않는다.

## 독립 검수와 제출

- 자체 대조는 확정 계약과 실제 파일·명령·정식 receipt·현재 인덱스를 기준으로 수행했다. 보존 영역은 조회/수집 전에 제외했고, 원자료/artifacts/SQL/lock/Wrapper를 자동 포맷하지 않았다. 프런트 기존 동작은 포맷·보안 regex 의도 주석 외 변경하지 않았다.
- 별도 읽기 전용 검토자 `/root/review_quality_ci`는 HEAD `8a21c74` 대비 실제 staged 후보를 검수했다. 초기 6개 필수 보완은 staged 실행기, Windows 대소문자 잠금, 내부 절대 경로, 미분류 marker, Wrapper 준비/네트워크, 개별 상태 파일 링크 경계였다. 회귀 Red 뒤 수정했으며 재검수에서 해당 사례를 격리 실행으로 확인하고 새 필수 결함을 발견하지 못했다. 프런트 12파일의 JSX 변환 후 JS AST도 동일했다.
- 검토자는 최종 `quality-final-integration-v3` run `5cac5dc2deb14d3abdb9f23255114cf5`의 spec·manifest와 실제 index의 일치를 확인했다. 도구 105개가 실패/error 0이며 Windows file-symlink 권한 1개는 skip이고 Linux CI 확인 대상이다. 새 경로 분류 gate도 신규 미분류만 차단하고 기존 legacy 경로는 유지함을 확인했다.
- 루트 `npm run check`가 포맷→Node 4개/Python 105개/기존 검수 도구→프런트 lint·13개·타입/빌드→서버 포맷·테스트/격리 DB 통합·bootJar→문서/현황/기록 순서로 통과했다. 입력이 같은 서버 결과는 Gradle의 유효한 up-to-date 결과를 재사용했다. 기존 장문 기록의 길이 경고는 차단 실패와 구별한다.
- 인덱스의 staged 모듈·내용·설정으로 형식을 확인했고 원본 작업 파일을 고치지 않았다. 실제 설치 pre-commit은 정상 후보를 종료 0으로 허용했다(7957ms, TDD와 형식 포함). 별도 index의 README 포맷 위반은 파일을 식별해 종료 2로 거부했다. 실제 index SHA-256은 전후 같았고 선행 TDD wrapper SHA-256도 재설치 전후 같았다.
- Git/Windows Wrapper 속성·Gradle/배치 파일 지문은 CRLF 동등성을 실제 Red→Green으로 확인했다. Java는 UNIX 줄바꿈을 명시해 Windows 작업 파일·인덱스·Linux의 후보 형식을 일치시켰다. `format:prepare`가 배포본을 명시적으로 준비하고 hook은 그 배포본만 직접 offline 실행한다. 미준비 fixture에서 Wrapper 미호출을 확인했다.
- 기록·현황·공백 검사를 통과했다. 현재 source와 별도 검수의 코드·조건을 보존한 결과/한계 갱신은 자체 대조하고 검수 근거를 재사용한다.
- 원격 정상/통제 실패 CI는 아래 근거로 확인했고 새 PostToolUse의 실제 호스트 자동 실행은 아직 미확인이다. WIP는 이 잔여를 보존해 실제 CI를 실행할 진행 후보이며 Task 자기 수용은 진행 중이다. 수동 실행 실측은 Phase의 main 통합 뒤 조건을 유지한다. 실제 CI 실행 URL·commit·job 판정은 수행 후 연결한다.

<a id="remote-ci"></a>
## 실제 CI와 현재 인계

검증한 구현 commit은 `86569c684a632a2f69296dd0b6d2e287ad2e1fba`다. 후속 변경은 이 코드·설정·수용 조건을 보존한 관찰/기록 갱신이며 정상 결과로 자기 수용을 완료하지 않는다.

| 실제 입력·이벤트 | 실행·관찰·판정 |
|---|---|
| 정상 PR #63, 구현 commit `86569c6` | [품질 CI](https://github.com/Mi-no-Kim/LumiaWiki/actions/runs/43217304661)의 changes/tools/docs/frontend/backend/quality 전부 성공. [별도 회귀](https://github.com/Mi-no-Kim/LumiaWiki/actions/runs/43217304862)의 Ubuntu·Windows도 성공 |
| 부모 패턴 push, 같은 구현 commit | 격리 `issue/42-ci-push-fixture`에서 [push CI](https://github.com/Mi-no-Kim/LumiaWiki/actions/runs/43218226280) 6개 job 전부 성공. 새 ref 비교 기준 누락의 전체 검사도 관찰 |
| lint 실패 PR #64, commit `3bfb8178c6b8bf5af37f4a68e11316eafad12f57` | [실행](https://github.com/Mi-no-Kim/LumiaWiki/actions/runs/43217663817)에서 추가 파일의 no-unused-vars 오류로 frontend 실패·quality 실패, 나머지 필요한 job 성공 |
| 테스트 실패 PR #65, commit `988349beb950849603438847bf34f02db51070be` | [실행](https://github.com/Mi-no-Kim/LumiaWiki/actions/runs/43217674243)에서 통제 assertion 1개 실패·기존 13개 통과, frontend/quality 실패·나머지 필요한 job 성공 |

- 통제 후보는 같은 정상 tree에 검수한 파일 하나씩만 추가해 별도 index/commit-tree로 만들었다. 제품 수용 후보나 가짜 TDD Green이 아니다. 별도 에이전트는 fixture 두 원문의 포맷·lint·수집 경로를 검수했다. 로컬에서도 lint 종료 1과 환경 오류 없는 Vitest assertion 실패 1개를 먼저 확인했다.
- PR #64·#65는 병합하지 않고 닫았다. 두 Task 검증 브랜치와 부모 push 검증 브랜치의 실제 head를 대조한 뒤 원격·존재하는 로컬 검증 브랜치만 삭제했다. 정상 Task 브랜치와 실제 index는 보존했다.
- Linux tools job에서 상태 파일 symlink 보호 사례가 실제 통과했다. Windows의 같은 파일 symlink 권한 skip과 Linux의 Windows 대소문자 전용 skip은 환경별 조건과 구별한다.
- PR #65의 별도 [Windows 회귀](https://github.com/Mi-no-Kim/LumiaWiki/actions/runs/43217677524)는 Git ls-files 조회가 남은 1.266초 제한을 초과해 한 사례가 실패했다. 같은 하네스 입력의 정상 PR·lint PR Windows 회귀는 통과했다. 재실행 API는 토큰 권한 부족으로 거부됐으며 그 실행을 성공으로 바꾸지 않는다. 품질 CI의 통제 assertion·집계 실패 확인과 이 별도 회귀의 시간 초과를 구별해 보존한다.
- 비용은 TDD의 전체 구현 후보 검사 1300ms, 사전 준비된 Java 한 파일 포맷 1640ms, 설치 pre-commit 전체 7957ms였다. formatter 비용을 TDD 3초 목표에 합쳐 판정하지 않는다.
- 남은 필수 확인: 앱에서 새 PostToolUse 정의를 검토·신뢰한 뒤 실제 apply_patch로 문서·Java 자동 포맷을 확인한다. 정의/직접 실행/기존 PreToolUse 거부·허용과 현재 대화의 자동 PostToolUse 실행은 별개다. 같은 합성 JSON의 실제 편집 뒤 자동 포맷되지 않은 것을 두 번 관찰했으며 원인은 신뢰/세션 적용 등으로 확정하지 않았다. 앱·전역 신뢰를 자동 변경하거나 우회하지 않았다.
- Task는 진행 중이다. 작업·테스트 입력·준비 캐시·정식 receipt와 필요한 Git 제외 임시는 호스트 재개를 위해 유지한다. main·Phase·부모 Issue에 병합하거나 저장소 보호 설정을 바꾸지 않았다. 수동 실행 실측은 기존 Phase의 main 통합 뒤 조건으로 남긴다.
