# P1 통합 확인과 잔여 정리

<a id="summary"></a>

## 현재 요약

- 제목: P1 통합 확인과 잔여 정리
- 실제 GitHub Issue: [Mi-no-Kim/LumiaWiki #48](https://github.com/Mi-no-Kim/LumiaWiki/issues/48)
- 소속 Phase: [Phase 001](../phase.md#summary)
- 상태: 예정
- 현재 진행 위치: 합의한 목표·수용 조건·의존 관계와 Task 구성 윤곽으로 정식 Issue를 등록했다. 구현·실제 자료 작업과 하위 Task 생성은 수행하지 않았다.
- 다음 판단/행동: 필요 기능·실제 자료와 각 Issue의 검증 근거가 준비되면 직접 수행 계획을 구체화한다. Task는 두지 않는다.
- 작성 근거: [Task 005](../issue-15/task-005.md#summary) · [전체 실행 순서](../issue-15/artifacts/task-005-issue-outline.md#sequence). 실제 자료 작업 보류를 유지한다.

<a id="goal"></a>

## 목표와 범위

각 과제의 검증 결과와 실제 v1.0.0 자료를 결합해 P1 여섯 완료 조건의 연결·충족/미확인·필수 잔여를 확인하고 후속으로 넘길 범위를 연결한다.

<a id="plan"></a>

## 선행 결과와 필요한 입력

- 필요 기능·실제 자료와 각 Issue의 검증/교정 근거, 실행 가능한 화면·내부 검사 환경이 준비돼야 한다. 기존의 유효한 검증 결과를 재사용한다.
- [자료 Issue](../issue-45/issue.md#data)의 기본 화면 자료 대조와 [제작](../issue-46/issue.md#crafting)/[루트](../issue-47/issue.md#route)의 계산·정정 반영 결과를 받는다.

<a id="integration"></a>

## P1 통합 확인과 잔여 정리

Task 없이 Issue에서 직접 수행하기로 합의했다. 기존 과제의 완료·검증 근거와 실제 입력을 확인하고 자료 등록→검색·상세→제작·루트→교정 후 관련 결과 재확인의 연결을 확인한다.

<a id="acceptance"></a>

### 합의한 수용 조건

- 실제 v1.0.0 자료로 [P1의 여섯 완료 조건](../phase.md#completion-criteria) 각각의 근거·판정을 연결하고 필수 미해결/미확인을 해소한다. 통제한 입력의 성공만으로 실제 자료 수용을 판정하지 않는다.
- 전체 내부 검사·대표 화면 확인과 화면에서 사용자와 함께 수행한 자료 대조 결과를 구분해 확인한다. 사용자 확인이 필수인 항목은 실제 확인 전 완료로 판정하지 않는다.
- 기본 자료·조회·제작·루트와 Java/Spring 교정 뒤의 관련 결과가 일치하고 기준/과거 정보·원자료·참조가 보존된다. 후속 범위와 미정의 담당/시점을 연결한다.

이 Issue의 수용 결과는 Phase 자체의 최종 수용·종료 처리와 구분해 연결한다. 검증 중 필요한 수정은 담당 기능/자료 과제로 연결하고 그 영향의 근거를 재확인한다. 전체 테스트를 새로 복제하거나 검수 증명 문서를 추가하는 Issue로 만들지 않는다.

<a id="pending"></a>

## Task 선후 관계와 남은 결정

- Task 없이 Issue에서 직접 수행한다. 준비된 근거·입력을 확인하고 전체 흐름/정정 영향·미확인을 확인한 뒤 필수 잔여와 후속을 정리한다.
- 검증 중 수정이 필요하면 담당 과제에 연결하고 달라진 영향만 재확인한다. Phase 자체의 최종 수용·종료는 해당 Phase 기록에서 별도로 판단한다.
- 실제 자료 적용 환경과 후속 운영의 API 문서 노출·SPA fallback·권한/로그/백업·이미지 저장소 전환 조건은 필요한 담당·시점에 연결하며 P1 전체 공개 운영 기능으로 확대하지 않는다.

<a id="related"></a>

## 기준·검증 배정

[P1 완료 조건](../phase.md#completion-criteria) · [Task 004 검증 계획](../issue-15/artifacts/task-004-verification-plan.md) · [후속 배정](../issue-15/artifacts/task-005-handoff-requirements.md#case-owners)
