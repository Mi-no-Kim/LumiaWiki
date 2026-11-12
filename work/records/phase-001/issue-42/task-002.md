# Task 42-002 — 테스트 실행 환경·최소 TDD hook

<a id="summary"></a>

## 현재 요약

- GitHub sub-issue: [#51](https://github.com/Mi-no-Kim/LumiaWiki/issues/51)
- 부모: [Issue #42](issue.md#summary)
- 상태: 완료
- 결과: 테스트 환경·TDD 검사기와 실제 Codex/Git hook의 수용 조건을 충족했다. 상위 변경 반영과 현황·hook 결합도 확인했다.
- 다음 행동: 부모 통합·브랜치 정리는 [PR #59](https://github.com/Mi-no-Kim/LumiaWiki/pull/59)의 실제 상태를 따른다. Task 003~004는 별도 작업이다.

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

## 실행 입력과 검증 근거

- [구현 계약·확정 환경](artifacts/task-002-verification.md#implementation-decisions)
- [TDD 실행 계획·정식 receipt](artifacts/task-002-tdd.md#tdd-plan): 실행기의 `--task` 입력으로 사용한다.
- [실제 Codex 편집 검증](artifacts/task-002-verification.md#host-acceptance)
- [상위 반영·Git hook 결합 검증](artifacts/task-002-verification.md#parent-integration)
- [PR 후보 회귀 확인](artifacts/task-002-verification.md#pr-ci)
- [제출 후보 검수·근거 보존](artifacts/task-002-verification.md#submission-review)

<a id="handoff"></a>

## 결과와 잔여

- PR 결합 후보의 도구 테스트 69개가 통과했다. 웹·서버와 실제 Codex 편집/Git 제출 경로는 동일 입력의 기존 검증 근거를 재사용했다.
- 기존 실행 근거는 동일 입력에 한해 재사용했고, 임시 실행 상태 없이 정식 receipt로 제출 후보를 대조했다.
- 사용자 직접 조작은 미수행이다. 부모 Issue 전체의 수용은 남아 있다.
