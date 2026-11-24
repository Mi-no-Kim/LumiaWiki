# Java 편집·커밋 검사 실행

<a id="current"></a>

[Java 작성·관리 규칙](<Java 작성과 관리.md>)과 [공통 정책](java-policy.json)은 아래 검사에서 같은 입력으로 사용한다.

| 시점 | 확인 | 다음 행동 |
| --- | --- | --- |
| Codex `apply_patch` 편집 전 | 대상이 운영 Java이면 현재 사이클의 실제 Red 또는 Task의 적용 범위에서 확인한 TDD 예외가 필요하다. | 거부 메시지의 대상에서 Red를 실행하거나 예외 근거를 확인한 뒤 편집을 다시 시도한다. |
| Codex `apply_patch` 직후 | 생성·이동 목적지의 경로, 패키지와 주 타입 이름을 확인한다. | 알림을 읽고 파일의 목적지·패키지·이름 또는 승인 근거를 확인한다. |
| Git 커밋 전 | 실제 인덱스의 생성·이동, 범위와 승인, 운영 Java의 TDD 근거를 대조한다. 적용되는 정책 변경도 확인한다. | 수정한 뒤 다시 스테이징하고 실제 인덱스의 승인·TDD 근거를 확인한다. |

Codex가 신뢰한 로컬 저장소에서 프로젝트 훅을 활성화한다. 현재 지원 편집 도구는 `apply_patch`다. 셸·IDE 편집은 실제 Git 인덱스에서 검사한다. Git은 기존 사용자 훅과 현황·기록·주석 검사를 순서대로 실행한 뒤 Java를 확인한다. [설치·해제와 기존 훅 보존](<../../../harness/문서 관리.md#inventory-hook-install>)

운영 `package-info.java`도 패키지 애너테이션 변경을 감지할 수 있도록 편집·커밋의 TDD 확인에 포함한다. 패키지 설명 파일에 최상위 타입을 선언하면 위반으로 처리한다.

<a id="candidate"></a>

## 승인 확인과 재실행

스테이징을 마친 뒤 실제 후보 식별자, 기준 커밋, 변경 경로와 정책 변경을 확인한다.

```text
python -B -X utf8 scripts/check-java.py --candidate index --identify
python -B -X utf8 scripts/check-java.py --candidate index --approval-context <승인-확인-파일>
python -B -X utf8 scripts/check-java.py --base <기준-커밋> --candidate <제출-커밋> --approval-only --approval-context <승인-확인-파일>
```

`--approval-only`는 CI에서 동일한 배치·승인 판정을 호출하는 방식이다. CLI는 JSON `status`·`reason`·`next`를 출력한다. 통과와 적용 대상 없음은 종료 코드 0, 위반은 1, 미확인은 2다. 적용 범위가 없는 Git 후보는 작업 트리에 미추적 백엔드가 있어도 Git 후보로 판정한다.

호출 환경에서 실제 Task 범위와 승인·위임·예외의 원천과 유효성을 독립 확인한 뒤 작업 트리 밖의 신뢰된 JSON 파일로 제공한다. Git 훅은 `LUMIA_JAVA_APPROVAL_CONTEXT`의 절대 경로를 사용한다. 파일의 `candidateId`와 `baseRevision`은 검사 대상의 `--identify` 결과와 일치해야 한다. 승인 목록 검색이 완전하다고 확인한 경우에만 `approvalsComplete`를 `true`로 보낸다. 확인된 Task 변경마다 필요한 경우 `tddExceptions`에 승인받은 사이클 ID 배열을 넣는다. 형식과 범위는 [승인 근거 규격](<Java 작성과 관리.md#input>)을 따른다.

원천의 `ref`는 기준의 이력에 있는 전체 Git 커밋 ID와 기록 경로·앵커, 또는 호출 환경에서 독립 확인한 `event:` 승인 식별자를 사용한다. 호출자가 제공한 승인 확인 파일을 CI 제출 패치에서 가져오지 않는다. 로컬 Git 이력에 없는 이벤트의 진위와 결정권 확인은 이 파일을 제공하는 환경이 맡는다. 인덱스 내용이 바뀌면 새 식별자에 맞춰 근거를 대조한다. 편집 예외는 `--mode before-edit --identify`에 해당 `apply_patch` 이벤트 JSON을 표준 입력으로 전달해 편집 대상 식별자에 연결하고, 편집 훅의 `LUMIA_JAVA_EDIT_APPROVAL_CONTEXT`에 절대 경로를 제공한다.

<a id="submission-contract"></a>

## 제출 후보의 모듈·HTTP 계약 검사

`Java contract` 워크플로에서 제출 승인, 회귀 검증과 백엔드 계약의 개별 결과를 확인한다. PR 검사는 이벤트의 기준·헤드가 체크아웃한 합성 후보의 두 부모와 일치해야 한다. 일반 push는 이벤트의 이전 SHA, 수동 실행은 검증할 정확한 기준 SHA를 사용한다. 트리에 추적된 백엔드가 없는 경우에도 승인 검사와 변경 입력에 영향을 받는 실제 Java·Spring 회귀는 실행한다.

```text
python -B -X utf8 scripts/check-java-submission.py --base <기준-SHA> --candidate <후보-SHA>
gradle --no-daemon -p scripts/java-contract test
```

승인 판독기는 PR의 실제 기준에서 가져온다. [최초 HTTP 승인](<../../../work/records/harness/issue-106/issue.md#initial-http-approval>)과 [초기 CI 입력 지문](java-ci-approvals.json)을 코드 도입 전에 신뢰된 기준 이력에 수용한다. 추가 후보의 독립 승인 확인은 해당 기준 이력 또는 결정권자가 확인한 [후보에 묶인 승인 파일](#candidate)을 사용한다. 원격 실행에서 외부 확인이 필요하면 승인 자료를 관리하는 실행 환경이 저장소 변수 `LUMIA_JAVA_APPROVAL_CONTEXT`로 같은 JSON을 제공한다. 후보의 파일에는 승인 권한이 없고 승인 변수에는 비밀을 넣지 않는다. 검사 자체나 워크플로가 바뀌면 병합 실행자가 최종 지문과 개별 검사 기록을 승인 근거와 직접 대조한다.

모듈 검사는 컴파일된 타입 참조와 컴파일러가 해석한 소스 참조를 함께 확인한다. HTTP 검사는 실제 Spring 기본·운영·허용 개발 프로필을 기동하고 등록한 명시 메서드·경로를 [승인 목록](java-http-api.json)과 대조한다. 검증 DB는 격리된 CI PostgreSQL을 쓴다. 조건이나 라우터 소유를 판독할 수 없으면 미확인으로 실패한다. 새 저장소나 다른 통합 기준에서 최초 도입을 검증할 때에도 승인 판독기와 승인 원천이 실제 비교 기준에 먼저 있어야 한다.

<a id="tdd"></a>

## TDD 근거 기록

신규 Task에는 같은 Issue의 `artifacts/task-<순번>-tdd-plan.json`과 `artifacts/task-<순번>-tdd-evidence.json`을 상대 경로로 연결한다. Phase 1 기존 기록의 인라인 JSON은 해당 파일에 보존한다. 새 기록은 첨부 형식을 사용한다. 한 입력의 기존 블록과 첨부를 동시에 선언하면 미확인이다.

```text
python -B -X utf8 scripts/tdd-run.py --task <Task-경로> --activate
python -B -X utf8 scripts/tdd-run.py --task <Task-경로> --cycle <사이클> --phase red
python -B -X utf8 scripts/tdd-run.py --task <Task-경로> --cycle <사이클> --phase green --export
```

실행 명령과 기대 실패를 계획에 선언한다. 테스트 환경 오류나 테스트가 0건인 실행은 Red로 인정하지 않는다. Green은 Red에서 실제 실행된 테스트가 모두 통과해야 하며 관련 테스트를 더 실행할 수 있다. 순수 리팩터링은 승인 근거와 변경 전 `before` 및 변경 후 `verify`에서 같은 테스트의 통과를 연결한다. 바뀐 운영 Java는 해당 사이클의 `targets`에 포함하고, Red 또는 `before`부터 후보까지 해당 파일이 실제 바뀌었는지 확인한다. 검증한 테스트·설정·코드가 바뀌면 필요한 실행을 다시 확인한다. `--export`로 보존한 근거는 관련 변경과 함께 검증한 후보에 포함한다.

Phase 1 결합에서는 기존 포맷·공통 기록·TDD 등록을 함께 유지한다. 기존 Phase 1 Codex TDD 명령에는 `--non-java`를 전달해 운영 Java 판정을 이 문서의 훅에 맡긴다. Git에서는 공통 훅을 바깥쪽에 설치하면 기존 Phase 1 훅의 운영 Java 판정만 공통 훅에 위임하고 나머지 TDD는 유지한다. 기존 설치의 순서를 바꿀 때는 바깥쪽부터 기존 절차에 따라 해제한 뒤 사용자 훅을 보존해 다시 연결한다.
