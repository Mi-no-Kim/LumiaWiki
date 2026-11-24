# Issue 106 — Spring 파일 생성·관리 규칙과 검사 훅 도입

공통 절차: [Issue 공통 절차](<../../../../harness/Issue 공통 절차.md>)

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
- 현재 진행 위치: [최초 CI 검사 입력의 기준](#java-ci-bootstrap)
- 다음 행동: 3번 — Java CI 도입에 앞서 독립 승인 근거와 기준 판독기를 검토
- 막힌 조건: 4번·최종 검사 — 선행 기준을 수용한 뒤 #106 최종 제출 후보와 실제 CI를 대조한다.

<a id="acceptance-criteria"></a>

## 완료 조건과 확인 방법

<!-- issue-rule:completion
Issue별 최소 활동 기준과 전체 수용 조건을 기록한다. 판단 조건은 공통 절차, 조건별 기록 형식은 기록 지침을 따른다. -->

실제 제출 기준에서 승인 기록과 판독기를 읽을 수 있어야 한다. 후속 후보의 최초 워크플로와 관련 설정 파일은 승인 카탈로그의 지문과 대조한다. [Issue #106](https://github.com/Mi-no-Kim/LumiaWiki/issues/106)의 실제 훅·Phase 1·최종 후보 수용 조건은 [전체 Issue 기록](https://github.com/Mi-no-Kim/LumiaWiki/blob/cc2be365879ab4bcf550f6e7f8d8c6e9c0cea8f5/work/records/harness/issue-106/issue.md#acceptance-criteria)에 연결한다.

<a id="decisions"></a>

## 선행 반영의 승인 근거

[전체 Issue 기록](https://github.com/Mi-no-Kim/LumiaWiki/blob/cc2be365879ab4bcf550f6e7f8d8c6e9c0cea8f5/work/records/harness/issue-106/issue.md#decisions)에 Java 규칙의 결정과 Task 배정을 두고, 여기에는 선행 제출 판독에 필요한 승인 원천을 보존한다.

<a id="task-execution-conditions"></a>

### 승인 권한

- 위임 범위: 합의한 적용 범위와 강제 수준 안에서 검사 도구, 입력 데이터 형식, 오류 메시지와 재실행 방법, 검증용 코드의 구현을 정한다.
- 사전 승인: 최초 공개 HTTP API 목록과 공통 허용 경로·모듈 경계·예외의 범위 변경에는 프로젝트 결정권자 또는 명시적으로 위임받은 승인권자의 근거를 연결한다. 같은 후보에서 기준이나 승인 기록도 바꾸면 승인된 원천에 대조한다.

<a id="initial-http-approval"></a>

#### 최초 운영 공개 HTTP 계약 승인

- 결정: 프로젝트 결정권자인 사용자가 최초 공개 HTTP API의 전체 목록 `[]`와 기본 이력을 구현 제출 후보와 독립적으로 보존하는 계획에 동의했다.
- 근거: [격리한 Phase 1 Spring MVC 등록 대조](https://github.com/Mi-no-Kim/LumiaWiki/blob/cc2be365879ab4bcf550f6e7f8d8c6e9c0cea8f5/work/records/harness/issue-106/artifacts/task-003-execution.md#work-http-inventory)에서 운영 프로젝트 명시 매핑이 없었고, `GET /api/v1/_dev/foundation`은 개발 프로필 `local`·`test`에만 등록됐다. 사용자는 이 결과와 최초 빈 목록 제안을 확인한 뒤 “그렇게 하자”라고 답했다.
- 적용: [기계 판독용 승인 원천](artifacts/task-003-initial-http-approval.json)은 `http-106-003-initial`의 정확한 `scope.initialHttp: []`만 기록한다. 실행 시 구현 PR의 실제 base에서 이 파일과 Issue 앵커를 읽고, 검증한 전체 base 커밋 ID를 `source.ref`로 넣어 최초 목록에 연결한다.

<a id="java-ci-bootstrap"></a>

#### 최초 CI 검사 입력의 기준

- 근거: [Task 106-003에 위임한 CI 연결](#task-execution-conditions)과 사용자 계획 합의를 적용한다. 최초 빈 목록 결정은 [PR #115](https://github.com/Mi-no-Kim/LumiaWiki/pull/115)로 `52198b1`에 먼저 수용했다.
- 적용: 승인 판독기와 [최초 검사 설정의 정확한 파일 지문](<../../../../docs/details/development/java-ci-approvals.json>)을 구현 제출과 별도로 검수한다. 실제 부모 이력의 승인 판독기가 제출의 SHA와 Git 파일을 대조한다. 최초 설정 지문은 기준 전체 이력에서 워크플로 도입이 없고 후보에 승인한 전체 묶음이 추가될 때만 적용한다.
