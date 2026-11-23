# Issue 95 — Phase 001 백엔드 변경 승인 재검토 및 정정

공통 절차: [Issue 공통 절차](<../../../../harness/Issue 공통 절차.md>)

기록 지침: 본문의 규칙 주석 · [기록 작성 기준](<../../../../docs/작업 기록 작성 기준.md#recording-boundary>)

<!-- issue-rule:recording
Issue별 체크와 실제 기록은 이 본문에서 관리한다. 공통 문서에는 Issue별 체크·실적을 쓰지 않는다. 공통 판단 조건은 공통 절차를 따른다.
현재 유효한 값·이유·근거·한계·남은 일을 갱신한다. 단계 기록은 수행·확인 요지와 상세 위치를 연결하고 미수행이면 그대로 적는다.
상세 원자료는 담당 Task나 기존 근거에 한 번만 두며 같은 항목의 실행 경과를 누적하지 않는다. 대상은 커밋·실행 ID·내용 지문으로 식별하고 기록 날짜를 추가하지 않는다.
전달된 입력과 추가 필요 자료를 구분하고 미정·미확인의 확인/결정 방법·필요 시점을 남긴다. 입력 원문·순서·불확실성, 링크·표식·규칙 식별자를 유지한다.
모든 `issue-rule:` 주석은 해당 조건에서 준수한다. 식별자는 규칙을 구분하며, 그 자체로 변경 보호·훅 검사 대상을 늘리지 않는다.
변경 보호 대상은 `issue-rule:start`·`issue-rule:state`·`issue-rule:position`·`issue-rule:completion` 네 주석이다. 사용자가 명시적으로 변경을 요청한 범위 외에는 이 네 주석의 식별자·내용·경계를 수정·삭제하지 않는다. -->

<!-- issue-rule:start
착수·재개·조건 변경·주요 단계 전환·수용 판단 전에 공통 절차와 해당 단계 규칙을 읽고 본문·실제 상태를 대조한다. -->

<a id="summary"></a>

## 현재 요약

<!-- issue-rule:state
상태는 '- 상태: 값' 한 줄에 예정·진행 중·중단·완료·취소 중 하나만 쓴다. 검사와 필수 종료 처리를 모두 마친 뒤에만 완료로 바꾼다. -->

<!-- issue-rule:position
현재 진행 위치는 현재 요약을 제외한 본문 안 실제 작업·근거 구역의 링크 하나만 쓴다. 표시명·번호·표식을 맞추고 설명·결과·다음 행동을 덧붙이지 않는다. -->

<!-- issue-rule:summary
다음 행동은 `N번 — 대상과 행동` 형식으로 현재 허용된 행동 하나를 쓴다.
막힌 조건에는 제한 번호·행동·미충족·해소 조건과 상세 위치를 연결한다. 번호 미정이어도 아는 조건을 유지하고, 제한 미확인은 확인 대상·방법을 적는다. 후속 단계의 막힘을 현재 단계의 허용된 보완 금지로 확대하지 않는다.
현재 하려는 행동의 진행 단계나 허용 범위를 판단할 수 없으면 현재 위치는 실제 확인 구역 링크로, 다음 행동은 `미정 — 진행 단계·허용 범위 확인 필요`로 쓴다.
공통 절차의 완료·취소·미완료 인계 처리를 마쳐 남은 행동이 없을 때만 현재 위치를 실제 종료 근거 링크로, 다음 행동을 `없음 — 같은 근거 링크`로 쓴다. 미완료 인계의 재개 행동은 유지한다. -->

- 상태: 진행 중
- 현재 진행 위치: [3. Task 생성](#step-3)
- 다음 행동: 3번 — 95-003에서 Phase 파일별 처리와 격리 검증 기준 확정
- 막힌 조건: 후속 정정 — 파일별 승인 미발생 — 다섯 Task 등록 및 조사 후 사용자가 항목별 결정

<a id="sequence"></a>

## 진행 순서

<a id="step-1"></a>

### 1. 입력·준비 확인

- [x] 단계 완료
- 공통 절차: [1. 입력·준비 확인](<../../../../harness/Issue 공통 절차.md#step-1>)
- 진행 기록: GitHub Issue 및 milestone 연결을 확인하고 최신 Phase SHA에서 별도 워크트리를 분기했다.
- 상세 기록: [결정 목록](#decisions)

<a id="purpose"></a>

#### 목적

일반 갱신을 Spring이 담당한다는 역할 분담이 구체적인 Spring 설계·구현 승인으로 확대 해석된 경위를 확인한다. 초기 사용자 제공 파일과 이후 파일 변경을 실제 diff, 당시 사용자 발언과 대조해 Phase 001의 승인 기록과 변경을 정정한다.

<a id="expected-results"></a>

#### 기대 결과

작업과 복구 근거의 보존, 파일·변경별 출처 대조, 사용자 승인 목록, 정정된 Phase 백엔드와 격리 검증 결과, 관련 기록과 #43 재개 조건을 갖춘다. 다섯 Task를 새 Issue에 squash 병합하고, 전체 수용 뒤 Phase에 merge commit으로 통합해 원래 대화에 인계한다.

<a id="conditions"></a>

#### 이미 정해진 조건

- 조건: Phase 백엔드, 직접 연결된 실행 설정·Compose·마이그레이션·기록을 다룬다. frontend는 최초 유입을 조사하고 정정 필요성과 영향을 보고한다. #42는 조사 대상이고 #43 전용 변경은 읽기 전용이다.
  - 적용 범위: 변경 출처 조사와 Phase 정정
  - 확정 근거: [사용자 과제 배정](codex://threads/01a2087d-5143-7523-86d6-a03744fed8e5)
- 조건: 조사 기준은 Phase `cc7338c`와 #43 `1dc6fa1`이다. 최신 원격 Phase SHA에서 별도 워크트리를 분기한다. 기존 문서 변경 6개, 철회 패치와 복원 검증한 V1 백업을 보존한다. Phase 검증은 격리 환경에서 수행하고 개발 DB·서비스 변경은 별도 승인을 받는다. 정정 항목은 Issue와 Task 등록 뒤 사용자가 결정한다.
  - 적용 범위: 보존·분기·검증·실행 권한
  - 확정 근거: [사용자 과제 배정](codex://threads/01a2087d-5143-7523-86d6-a03744fed8e5)
- 조건: 43-003에서 한 요청 안의 신규 행끼리 중복·겹침이 있거나 기존 행과 충돌하면 신규 행 전부를 저장하지 않고 기존 행을 보존한다. 별도 동시 요청은 먼저 커밋된 행을 보존하고 충돌 요청을 거부한다. Spring 설계·구현, #69 사용자 수용·종료 및 #45 자료 작업은 보류한다. #43의 Phase 병합과 Phase의 main 병합은 제외한다.
  - 적용 범위: 원래 대화의 재개 및 관련 작업
  - 확정 근거: [사용자 과제 배정](codex://threads/01a2087d-5143-7523-86d6-a03744fed8e5)
- 조건: Phase 검수 뒤 [43-003 마무리와 43-004 준비](codex://threads/01a20764-c112-72f3-9e64-9b461020cf7a)로 인계한다. 그 대화에서 로컬 변경을 보존하고 정정된 Phase → `issue/43-item-persistence` → `task/43-003-item-relations-r2` 순서로 반영한 뒤 승인된 #43·43-003 정정을 재개한다.
  - 적용 범위: Phase 병합 후 인계·재개
  - 확정 근거: [사용자 과제 배정](codex://threads/01a2087d-5143-7523-86d6-a03744fed8e5)

<a id="scope"></a>

#### 대상·범위·권한

- 생성 근거: [사용자 요청](codex://threads/01a2087d-5143-7523-86d6-a03744fed8e5)에서 Phase 001 하위 과제로 명시
- 부모 Phase: [Phase 001](../phase.md#summary)
- GitHub Issue: [Mi-no-Kim/LumiaWiki #95](https://github.com/Mi-no-Kim/LumiaWiki/issues/95) · milestone #1 확인
- 대상·입력: 42-001 기록과 「Find next work item」에서 시작한다. 파일별 원본·승인 및 영향은 조사에서 확인한다.
- 범위·권한: 등록·조사·격리 검증·조건 충족 뒤 제출과 Phase 병합. 정정 대상은 Task 3의 사용자 결정 후 실행한다.
- 적용 지침: AGENTS.md, Git 작업 기준, 기록 관리 절차 및 검수 스킬
- 준비 근거: milestone #1과 원격 Phase `cc7338c16bf3ef4fd3fb0b758bb41d048f6e1dff` 확인. 별도 워크트리 `.tmp/issue-95-backend-approval` 및 브랜치 `issue/95-backend-approval` 분기 확인.

<a id="plan"></a>

#### 완료 조건과 확인 방법

<!-- issue-rule:completion
Issue별 최소 활동 기준과 전체 수용 조건을 기록한다. 판단 조건은 공통 절차, 조건별 기록 형식은 기록 지침을 따른다. -->

<!-- issue-rule:criteria
최소 활동 기준과 Issue 전체 수용 조건은 조건별 한 행에 적는다.
1단계의 상세 범위·전체 수용 조건이 미정이면 결정 항목·필요 시점을 연결하고 2단계의 결정 근거로 갱신한다. 별도 착수 판정값은 만들지 않는다. -->

<a id="activity-criteria"></a>

##### 시작할 논의의 최소 기준

| 완료 조건                                      | 확인 방법                                      |
| ---------------------------------------------- | ---------------------------------------------- |
| 요청·범위·기준 SHA·보존 대상 및 결정 주체 식별 | 사용자 요청과 원격 Phase·milestone을 대조한다. |

<a id="acceptance-criteria"></a>

##### Issue 전체의 수용 조건

| 완료 조건                              | 확인 방법                                                                       |
| -------------------------------------- | ------------------------------------------------------------------------------- |
| 다섯 Task의 실제 등록·부모 연결과 반영 | GitHub 번호·URL과 로컬 순번, Task PR의 squash SHA, Task별 판정·한계를 확인한다. |
| 출처·승인 근거와 실제 정정 일치        | 당시 발언·최초 유입·diff와 정정 승인 항목을 대조하고 미확인을 표시한다.         |
| 격리 검증·자체 및 별도 검수·CI 확인    | 설정·빌드·기동·DB의 영향 범위, 실행 근거, V5 호환 조건과 CI를 대조한다.         |
| Phase 병합과 원래 대화 인계            | merge commit, 실제 diff, 병합 후 CI 및 #43 반영 순서와 재개 조건을 확인한다.    |

<a id="step-2"></a>

### 2. 논의·결정

- [x] 단계 완료
- 공통 절차: [2. 논의·결정](<../../../../harness/Issue 공통 절차.md#step-2>)
- 진행 기록: 사용자가 확정한 배정을 연결했다. 정정 항목의 사용자 결정은 Task 3에서 진행한다.
- 상세 기록: [결정](#decisions) · [Task 배정](#task-creation)

<a id="step-3"></a>

### 3. Task 생성

- [x] 단계 완료
- 공통 절차: [3. Task 생성](<../../../../harness/Issue 공통 절차.md#step-3>)
- 진행 기록: 다섯 Task의 번호·제목·부모 #95·milestone #1을 GitHub에서 다시 읽어 로컬 순번과 대조했다. 각 Task의 결과 반영은 진행 중이다.

<a id="task-creation"></a>

<!-- issue-rule:task-records
배정 정보와 실제 생성 정보를 구분한다. 2단계에서 배정을 확정할 때 담당 결과·근거 결정을 채운다.
실제 생성 후 Task 링크·생성 조건 충족 근거·남은 실행 제한을 연결한다. 미확정 배정은 미정, 미생성 Task는 미생성으로 둔다.
상세 계획·진행·검증의 원본은 Task가 소유한다. 생성 허용 여부와 결과 준비 중의 위치·체크·다음 행동은 공통 절차의 3단계를 따른다. -->

전달사항 작성 전 [경로·식별 기준](<../../../../docs/작업 기록 체계.md#paths>)으로 순번 충돌을 확인하고, Task 식별자·저장 경로·확인 근거를 배정 결정에 남겨 Task 생성 입력으로 넘긴다.

- 담당 결과: 작업 상태와 증거 보존
  - 근거 결정: [Task 배정의 근거](#assignment-decision)
  - 전달사항: [95-001 r001](artifacts/task-001-assignment.md)
  - Task: [95-001](task-001.md#summary) · [GitHub #96](https://github.com/Mi-no-Kim/LumiaWiki/issues/96) · [PR #101](https://github.com/Mi-no-Kim/LumiaWiki/pull/101) 반영
- 담당 결과: 변경 출처와 승인 범위 대조
  - 근거 결정: [Task 배정의 근거](#assignment-decision)
  - 전달사항: [95-002 r001](artifacts/task-002-assignment.md)
  - Task: [95-002](task-002.md#summary) · [GitHub #97](https://github.com/Mi-no-Kim/LumiaWiki/issues/97) · [PR #102](https://github.com/Mi-no-Kim/LumiaWiki/pull/102) 반영
- 담당 결과: 정정 범위 확정
  - 근거 결정: [Task 배정의 근거](#assignment-decision)
  - 전달사항: [95-003 r001](artifacts/task-003-assignment.md)
  - Task: [95-003](task-003.md#summary) · [GitHub #98](https://github.com/Mi-no-Kim/LumiaWiki/issues/98)
- 담당 결과: Phase 백엔드 정정과 격리 검증
  - 근거 결정: [Task 배정의 근거](#assignment-decision)
  - 전달사항: [95-004 r001](artifacts/task-004-assignment.md)
  - Task: [95-004](task-004.md#summary) · [GitHub #99](https://github.com/Mi-no-Kim/LumiaWiki/issues/99)
- 담당 결과: 기록 정정과 통합 후보 검수
  - 근거 결정: [Task 배정의 근거](#assignment-decision)
  - 전달사항: [95-005 r001](artifacts/task-005-assignment.md)
  - Task: [95-005](task-005.md#summary) · [GitHub #100](https://github.com/Mi-no-Kim/LumiaWiki/issues/100)

<a id="step-4"></a>

### 4. 최종 검사

- [ ] 단계 완료
- 공통 절차: [4. 최종 검사](<../../../../harness/Issue 공통 절차.md#step-4>)
- 진행 기록: 미수행
- 상세 기록: [전체 수용 조건](#acceptance-criteria) · [검토·수용·종료 기록 위치](#decisions)

<!-- issue-rule:review-records
검토·수용·종료가 실제로 발생할 때만 초기 질문 목록 뒤에 `검토·수용·종료 기록`을 만든다. 미수행 상태에는 빈 결과 구역·미래 표식을 만들지 않는다.
각 수용 조건에 확인 기록·판정·이유·근거·한계를 연결하고 실제 종료 처리·반영/미반영·잔여·재개 조건·다음 행동을 현재 내용으로 갱신한다.
개별 Task의 검증 전문은 연결하고 중복 작성하지 않는다. 사실·관찰 기록과 새 결정의 추가는 구분한다. -->

<a id="decisions"></a>

## 결정

<!-- issue-rule:decisions
질문 원문·순서는 유지한다. 질문별 결정 내용·이유·자료·근거와 누가 어떤 방식으로 확정했는지는 이 구역에 기록한다. 다른 구역에는 적용 내용과 근거 결정 링크를 둔다. -->

<a id="assignment-decision"></a>

### Task 배정의 근거

사용자가 작업과 증거 보존, 변경 출처와 승인 범위 대조, 정정 범위 확정, Phase 백엔드 정정과 격리 검증, 기록 정정과 통합 후보 검수를 순서대로 배정했다. 파일별 결정은 Task 3에서 사용자가 확정한다.
