# Task 003 — 최소 TDD hook 기준

- 상태: 채택. 최초 검수의 필수 보완 2건을 수정하고 자체·별도 재검수에서 추가 필수 문제가 없음을 확인했다. [재검수 결과](<../task-003.md#tdd-hook-rereview>)를 따른다. hook 코드·설정·Git hook 등록은 수행하지 않았다.
- 담당: [Task 003](<../task-003.md#tdd-automation-handoff>). 구현·검증 시점은 첫 기반 구축 과제 초반이며 첫 기능 구현의 선행 조건이다.
- 확인일: 2026-11-11. P1 동작 개발의 실수·증거 누락 방지가 목적이며 TDD의 의미적 타당성을 완전히 자동 증명하는 장치로 보지 않는다.

<a id="research"></a>
## 조사에서 가져올 것과 조정할 것

사용자가 제시한 Velog 글은 계획 문서를 기준으로 Red·Green 전담 에이전트를 나누고, 실패 테스트·최소 구현·검토를 순서대로 진행하는 사례다. 실제 hook 설정·검사 코드의 예시는 없다. 아래 평가는 우리 기존 절차·비용 조건에 맞춘 제안이다.

| 글의 접근 | 이번 제안 |
|---|---|
| 테스트 작성·구현 전담 에이전트 분리 | 개발 사이클은 단일 에이전트를 기본으로 하고 기존 커밋 전 자체·별도 검수는 유지 |
| 무조건 실패시키는 코드도 Red로 사용 | 기대 동작을 실행·검증하는 실제 실패를 요구. 강제 실패 자리표시자·컴파일 확인만으로 Red를 인정하지 않음 |
| 구현 중 테스트 수정 제한 | 기대값 정정은 요구 근거·이유를 남겨 처리하며 변경된 테스트에는 이전 근거를 재사용하지 않음 |
| Green 보고 뒤 계획 항목 완료 표시 | Green은 테스트 근거일 뿐 Task 수용·상태 변경·검수·PR·통합을 자동 완료하지 않음 |

Kent Beck의 Canon TDD도 예상 시나리오를 정리한 뒤 실행 가능한 테스트 하나씩 구현·통과시키는 흐름이며 무검증 커버리지나 기대값을 구현 결과로 대체하는 방식을 경계한다. 이 원칙과 기존 화면 설계 선행 기준을 함께 사용한다.

Codex 공식 문서에서는 `PreToolUse`가 `apply_patch` 편집을 실행 전에 차단할 수 있고 `exec_command`도 `Bash` 별칭으로 관찰할 수 있음을 확인했다. 다만 모든 경로의 완전한 강제 경계는 아니며 `PostToolUse`는 이미 일어난 변경을 되돌리지 않는다. `Stop`의 차단은 추가 모델 턴을 만들므로 초기 구성에서 제외한다. 실제 설치 환경의 hook 활성화·신뢰·Windows 실행은 기반 구축에서 확인한다.

<a id="minimum"></a>
## 검사 시점·조건

현재 규칙은 [실제 TDD hook 기준](<../../../../../docs/details/development/TDD hook.md#minimum>)으로 옮겼다. 조사·재검수 이력과 실제 구현의 구분은 유지한다.

<a id="exceptions"></a>
## 적용·예외

현재 규칙은 [실제 TDD hook 기준](<../../../../../docs/details/development/TDD hook.md#exceptions>)으로 옮겼다. 조사·재검수 이력과 실제 구현의 구분은 유지한다.

<a id="evidence"></a>
## 근거·재사용

현재 규칙은 [실제 TDD hook 기준](<../../../../../docs/details/development/TDD hook.md#evidence>)으로 옮겼다. 조사·재검수 이력과 실제 구현의 구분은 유지한다.

<a id="cost"></a>
## 비용 기준

현재 규칙은 [실제 TDD hook 기준](<../../../../../docs/details/development/TDD hook.md#cost>)으로 옮겼다. 조사·재검수 이력과 실제 구현의 구분은 유지한다.

<a id="acceptance"></a>
## 첫 기반 구축 수용 사례

현재 규칙은 [실제 TDD hook 기준](<../../../../../docs/details/development/TDD hook.md#acceptance>)으로 옮겼다. 조사·재검수 이력과 실제 구현의 구분은 유지한다.

## 조사 근거

- [사용자 제시 글 — Antigravity와 Claude Code로 TDD+SDD 하네스 구축하기](https://velog.io/@jinhyoung9380/Antigravity%EC%99%80-Claude-Code%EB%A1%9C-TDDSDD-%ED%95%98%EB%84%A4%EC%8A%A4-%EA%B5%AC%EC%B6%95%ED%95%98%EA%B8%B0)
- [Kent Beck — Canon TDD](https://newsletter.kentbeck.com/p/canon-tdd)
- [Codex 공식 hooks — 도구별 범위·신뢰·Stop 동작](https://learn.chatgpt.com/docs/hooks)
- [Git 공식 githooks — pre-commit 실행·종료값·우회](https://git-scm.com/docs/githooks#_pre_commit)
- [기존 Issue #36의 비용·확대 조건](<../../../harness/issue-36/issue.md#pending>) · [기존 검수 절차](<../../../../../.agents/skills/review-work/SKILL.md#common-review>)
