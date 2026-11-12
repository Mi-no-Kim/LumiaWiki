# Task 42-004 — 코드·문서 검사·포맷·CI 연결

<a id="summary"></a>

## 현재 요약

- 제목: 코드·문서 검사·포맷·CI 연결
- GitHub sub-issue: [Mi-no-Kim/LumiaWiki #53](https://github.com/Mi-no-Kim/LumiaWiki/issues/53)
- 부모 Issue: [Issue #42](issue.md#summary)
- 상태: 진행 중
- 현재 진행 위치: 품질·포맷·후보 검사·CI를 구현하고 로컬·별도 검수·실제 PR/부모 패턴 push 정상 실행과 통제 실패 반영을 확인했다. [draft PR #63](https://github.com/Mi-no-Kim/LumiaWiki/pull/63)의 WIP 후보이며 새 PostToolUse의 실제 호스트 자동 실행 확인이 남아 있다.
- 다음 행동: 새 PostToolUse를 검토·신뢰한 환경에서 실제 apply_patch 뒤 문서·Java 자동 포맷을 재확인한다. [근거와 잔여](artifacts/task-004-implementation.md#remote-ci)를 사용하며 Task 자기 수용은 진행 중으로 유지한다.

<a id="goal"></a>

## 목적과 허용 범위 및 완료 조건

[코드 품질 기준](<../../../../docs/details/development/코드 품질.md#current>)과 [기술 인계](../issue-15/artifacts/task-003-handoff.md#handoff-decisions)를 로컬·제출 후보·CI에서 실행할 수 있게 한다.

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

| 준비·조작                                          | 기대 결과                                                         |
| -------------------------------------------------- | ----------------------------------------------------------------- |
| 허용 문서/Java 예제 생성·수정, 일괄 포맷 반복      | 대상만 포맷·재실행 무변경·보존/원자료 미접근                      |
| 유효/무효 TSX·Hooks 예제와 부분 스테이징 후보 검사 | 올바른 타입/lint 엔진으로 정상/실패 판정·후보 내용 기준 검사      |
| 포맷 실패·중복 호출·시간 초과의 통제된 재현        | 조용한 성공·명확한 실패·임의 설치/수정/재시도 없음·기존 hook 유지 |
| CI 정상 후보와 통제한 검사/테스트 실패 후보 실행   | 독립 설치/검사/테스트/빌드 성공과 해당 실패가 run에 반영          |

실제 명령·트리거와 확인 목록을 공유했으며 실행 안내는 README, 후보는 PR #63이다. 자동 검사·AI 직접 실행·CI 결과는 아래 근거를 따르고 사용자 직접 확인은 미수행이다. 제출 전 [자체·별도 검수](../../../../.agents/skills/review-work/SKILL.md#before-commit)를 적용한다.

<a id="implementation-decisions"></a>

## 확정 구현 계약

도구 버전·명령·포맷/후보 검사·CI 계약은 [구현 계약](artifacts/task-004-implementation.md#implementation-decisions)을 따른다. [현재 확인과 잔여](artifacts/task-004-implementation.md#verification)와 [정식 TDD 근거](artifacts/task-004-tdd.md)를 함께 사용한다.

<a id="verification"></a>

## 현재 결과와 잔여

- 로컬 프런트 lint·13개 테스트·타입/빌드와 서버 포맷·단위/격리 DB 통합 테스트·bootJar를 확인했다. 최종 내용 대응·전체 로컬 명령과 자체/별도 검수를 통과했다. 실제 CI의 정상 통과와 통제 실패 반영도 확인했다.
- 기존 TDD PreToolUse의 실제 거부·허용은 유지된다. 새 PostToolUse의 직접 실행은 검증했고, 현재 대화에서 편집 뒤 자동 실행되는 실제 호스트 확인은 미충족이다. 새 정의의 검토·신뢰와 재확인이 필요하다.
- 새 PostToolUse 실제 호스트 확인 전에는 자기 수용·부모 Issue 완료를 판정하지 않는다. 사용자 직접 확인은 미수행이다.
