# Task 43-001 — 공통 식별·시즌/패치·지역·분류

<a id="summary"></a>

## 현재 요약

- 상태: 완료
- 부모: [Issue #43](issue.md#summary) · GitHub: [Task #67](https://github.com/Mi-no-Kim/LumiaWiki/issues/67)

<a id="plan"></a>
<a id="result"></a>

## 실제 결과

아이템 등 후속 자료가 공통으로 참조할 시즌·패치·지역·분류의 저장 기반을 구현했다.

| 구현한 표                                | 저장·조회하는 내용                                      |
| ---------------------------------------- | ------------------------------------------------------- |
| `season`·`game_patch`                    | 시즌·패치 번호, 이름, 정렬 순서와 기간·적용 시각        |
| `region`                                 | 패치가 달라져도 유지되는 지역 식별자와 작업용 이름      |
| `region_map_version`·`region_map_member` | 패치별 지도 구성과 그 구성에 속한 지역의 공개 이름·순서 |
| `item_category`                          | 현재 아이템 종류와 상하위 분류 관계                     |
| `item_grade`                             | 등급 이름과 표시 순서                                   |
| `weapon_type`                            | 무기 종류와 아이템 종류의 대응 관계                     |

Java 서비스에 등록·수정·조회를 구현했다. 중복·잘못된 참조·분류 순환·기존 식별자 변경을 거부하고, 조회 패치에 유효한 지도 구성을 선택한다. 확정 계약은 [설계 안내](artifacts/task-001-shared-version-references.md#summary), 코드와 사용법은 [DB 구현 안내](../../../../db/model/implementation.md#current)에 있다.

<a id="verification"></a>

### 검증·적용 결과

- 단위 30건·격리 통합 11건으로 저장·조회, 입력/참조 거부, 권한 경계, 잠금과 실패 시 되돌림을 확인했다. 포맷·실행 JAR 검사도 통과했다.
- 검증 후 승인한 로컬 `lumiawiki/public`에 8개 표를 적용했다. 설치 계정과 업무 계정을 분리하고, Java 매핑·구조·소유·권한을 대조했다. 실제 게임 자료는 넣지 않아 제품 표는 모두 0행이다.
- 이 결과로 Task 자체 수용을 완료했다. [상세 검증·수용 근거](artifacts/task-001-creation.md#acceptance)를 따른다. Issue 준비와 Task 실행 변경의 [브랜치 분리](artifacts/issue-43-change-ownership.md#current)도 마쳤다.
- 종료 안내 기록·공용 절차 보완은 [제출 후보의 자체·별도 검수](artifacts/task-001-creation.md#submission-review)와 문서 검사를 통과했다. 후속 운영 효과는 미확인이다.

<a id="decisions"></a>
<a id="closure-status"></a>

## 현재 남은 일

- 제출·통합: 최근 기록·절차 정정의 원격 반영과 Task 001의 PR·부모 Issue 통합·브랜치 정리가 남아 있다.
- 후속 구현: 공통 8개 표의 미정은 없다. 아이템·능력치·스킬은 Task 002, 제작·획득·배달 관계는 003, 결합 조회·갱신은 004 담당이다. 세부 결정은 [담당별 잔여](artifacts/task-001-pending.md#remaining-review)를 따른다. Task 002는 001의 부모 통합·정리 뒤 착수한다.
- 자료·실행 제약: 실제 게임 자료 작업은 계속 보류한다. 신규 구조는 생성 직전에 전체 구조와 정확한 실행 대상을 확인받는다.

## 다음 행동

자체·별도 검수를 마친 변경을 제출하고 부모 Issue 대상 PR을 만든다. 이번 요청에서 Task 001의 커밋·push·GitHub 갱신·squash 통합·브랜치 정리까지 승인받았다. 실제 자료와 추가 DB 작업은 계속 보류한다.
