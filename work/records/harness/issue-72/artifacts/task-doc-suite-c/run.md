# 네 개선 반영과 문서 시험 C의 최종 결과

<a id="summary"></a>
## 현재 결론

사용자가 요청한 네 개선을 ② 완료·부모 수용 검사 → ③ 읽기 전용 재검증 → ① 실행·판정 분리 → ④ 충돌 사례 추가 순서로 반영했다. 기존 12개와 추가 3개, 총 **15개 사례·17개 입력**을 새 C 묶음에서 수행했다. 입력 부족 사례의 세 변형 때문에 입력 수가 사례 수보다 두 개 많다.

별도 문맥의 검토자가 원래 조건·입력·실제 파일·조작 코드와 거절 근거를 대조해 **보완 후 현재 결과를 수용**했다. 필수 미해결 사항은 없다. 모든 과제를 완료 상태로 만든 것이 아니라 미생성·중단·진행 중·취소가 필요한 사례는 그 상태를 유지했다.

## 반영한 개선

| 순서 | 반영 내용 | 원천 |
|---|---|---|
| ② | 할 일은 미완료가 기본이며 실제 판정·관찰·잔여를 확인해 명시적으로 완료한다. Task 완료는 현재 전달본·필수 미결정·막힘·작업별 근거·실제 결과를 검사한다. 부모는 자기 조건과 실제 결과를 별도 재검사한다. 조건 거절은 무변경이다. | [조작·수용 검사](../task-doc-validation/workflow.py) |
| ③ | 기존 결과의 주석·상태·연결·실제 조건을 파일 변경 없이 검사한다. 없는 케이스는 성공으로 반환하지 않는다. 판정은 해당 실행에 고정한 원래 정의를 사용한다. | [정합성 검사](../task-doc-validation/verify.py) · [판정자용 대조](../task-doc-validation/judge.py) |
| ① | 실행자는 입력·지침·조작 API를 받고 행동을 선택한다. 판정자는 실행 후 원래 기대 조건과 실제 파일·관찰을 대조한다. 실행자의 성공 문구만으로 수용하지 않는다. | [실행자 코드](actor.py) · [역할과 API](../task-doc-validation/README.md) |
| ④ | 전달본 불일치, 같은 문장의 사용자 수정, 실제 조건과 완료 표시의 모순을 추가했다. 거절·보존·실제 보완 또는 제한을 확인했다. | [추가 충돌 사례](../task-document-conflict-test-cases.md) |

## 입력·정보 전달과 검수 경계

- 실행자는 `cases/`의 중립 입력·현재 문서, 제공한 Task 지침과 조작 API를 받았다. `sealed/`의 예상 상태·사건 원문·원래 정의와 과거 점수표는 직접 읽지 않았다. 필요한 모의 사건은 제공 API로 해당 시점에 전달받았다.
- 판정자는 실행 종료 후 [고정 정의](sealed/source-cases.json), [예상 매핑](sealed/oracle.json), [사건](sealed/events.json)과 실제 관리·대상 파일, 조작 코드, 검사 결과를 읽기 전용으로 대조했다.
- 역할은 같은 모델의 별도 문맥이다. 재수행은 입력·요구 정정 피드백을 받은 같은 실행자 문맥에서 했다. OS 접근 차단·다른 모델·실제 사용자 승인으로 확대하지 않는다.
- [B 묶음](../task-doc-suite-b/run.md#results)은 기계 통과 뒤 의미 결함이 드러나 수용 보류한 원문으로 유지했다. 부족 입력의 전 원천 부재, 원래 A/B 대안, 실제 계획 병합, 취소의 부모 잔여, 사건·관찰 사실성, 보완 전 양쪽 수용 거절을 바로잡아 C에서 다시 수행했다.
- 실제 게임 자료·제품·DB·GitHub·정식 Issue/Task 발급·커밋·CI·현행 양식 교체는 이번 시험 범위가 아니다. P/T와 중립 입력 이름은 시험용 식별이다.

<a id="results"></a>
## 사례별 최종 판정과 실제 상태

| 사례 | 입력·근거 | 현재 판정 | 시험용 Task 상태 |
|---|---|---|---|
| TC-01 정상 흐름 | [sample-a](cases/sample-a/task.md#result) | 생성·원래 A/B 비교·선택·반영·별도 부모 수용 충족 | 완료 |
| TC-02 생성 정보 부족 | [결과·기준](cases/sample-b/return.md) · [수용 기준](cases/sample-c/return.md) · [생성 근거](cases/sample-d/return.md) | 담당 원천 전체의 실제 부족과 세 변형의 거절 충족 | 미생성 3개 |
| TC-03 방법 선정 | [sample-e](cases/sample-e/task.md#result) | 비교·모의 선택·후속 조건·실행 범위 보존 충족 | 완료 |
| TC-04 후속 자료 | [sample-f](cases/sample-f/task.md#result) | 자료 제공을 새 편집 권한으로 바꾸지 않음 | 중단 |
| TC-05 무응답 | [sample-g](cases/sample-g/task.md#result) | 질문·권고를 선택으로 바꾸지 않음 | 중단 |
| TC-06 추가 비교 | [sample-h](cases/sample-h/task.md#result) | 추가 요청·원래 두 후보·선택·계획 갱신 충족 | 완료 |
| TC-07 배정 개정 | [sample-i](cases/sample-i/task.md#result) | 이전 원본 보존·불일치 거절·r002 채택·부모 조건 유지 충족 | 완료 |
| TC-08 계획 재구성 | [sample-j](cases/sample-j/task.md#result) | 미착수 intro를 link에 병합하고 완료 inspect 원문·식별자 보존 | 진행 중 |
| TC-09 확인 실패 | [sample-k](cases/sample-k/task.md#result) | 같은 작업에서 실제 오류 보완·재확인 충족 | 완료 |
| TC-10 중단 복구 | [sample-l](cases/sample-l/task.md#result) | 저장·미수행·미확인을 구별하고 사용자 문장 보존 | 완료 |
| TC-11 문서 이동 | [sample-m](cases/sample-m/execution.md) | 조기 체크 정정 후 실제 이동·양방향 링크·보존 충족 | 완료 |
| TC-12 취소 | [sample-n](cases/sample-n/task.md#result) · [부모](cases/sample-n/parent.md) | 취소와 부모의 필수 잔여·미결정·다음 행동 연결 충족 | 취소 |
| TC-13 전달본 충돌 | [sample-o](cases/sample-o/task.md#result) | 불일치 거절·원본 보존·확정 개정 채택·실제 보완 충족 | 완료 |
| TC-14 사용자 수정 충돌 | [sample-p](cases/sample-p/task.md#result) | 겹친 수정 보존·미제공 답 유지·반영 제한 충족 | 중단 |
| TC-15 허위 완료 | [sample-q](cases/sample-q/execution.md) | 실제 조건 실패와 Task·부모 양쪽 거절·무변경 뒤 실제 보완 충족 | 완료 |

17개 입력의 실제 상태는 완료 9개·미생성 3개·중단 3개·진행 중 1개·취소 1개다. 이 표의 충족은 해당 상황에서 요구한 행동과 제한의 충족이다. 미생성·중단·취소 과제의 원래 목표까지 달성한 것으로 쓰지 않는다.

## 확인 결과와 재검증 방법

- 분리 검수에서 발견한 필드 오갱신·부모 개정 누락·거절의 부분 반영·미해결 기록 수용·식별 누락·빈 검사 성공 등을 보완했고 [회귀 검사 15개](../task-doc-validation/test_guards.py)가 통과했다.
- `verify.py`: 17개 입력, 정합성 위반 0건, 종료값 0.
- `judge.py`: 15개 사례·17개 입력, 고정 조건 대조 위반 0건, 종료값 0.
- 별도 검토자는 기계 결과 외에 실제 정보 부재·후보 비교·계획 병합·부모 잔여·모의 사건과 원문 사실성을 직접 대조했고 필수 잔여가 없다고 판정했다. 검토자의 명령 전후 C 묶음 전체 바이트도 같았다.

```text
python -B -X utf8 work/records/harness/issue-72/artifacts/task-doc-validation/test_guards.py
python -B -X utf8 work/records/harness/issue-72/artifacts/task-doc-validation/verify.py --run work/records/harness/issue-72/artifacts/task-doc-suite-c
python -B -X utf8 work/records/harness/issue-72/artifacts/task-doc-validation/judge.py --run work/records/harness/issue-72/artifacts/task-doc-suite-c
```

## 보완 이력의 해석과 잔여

TC-11은 최초 실행부터 무결했던 사례가 아니다. 실행자 helper가 조사만 마친 시점에 이동 작업의 체크를 조기에 완료로 넣었고 실제 이동 전에 미완료로 정정했다. 이후 실제 이동·참조 보정·최종 확인 뒤 완료했다. 경위와 helper의 기본값 정정이 수행 기록·코드에 남아 있으며 별도 검토자는 이를 구별해 현재 결과를 수용했다. 이를 최초 실행의 순서 위반이 없었다는 근거로 쓰지 않는다.

이번 요청 범위의 미실행·필수 확인 잔여는 없다. 기존 A·실제 사용자 A안 응답을 받은 TC-01·수용 보류한 B의 자료는 보존한다. 정식 채택과 실제 운영의 효과는 별도 범위다. 실제 담당 원천은 [Issue #72](../../issue.md#task-generation-test)다.
