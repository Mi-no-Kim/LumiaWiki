# 문서 시험의 조작과 읽기 전용 검증

기존 작성안의 조건을 시험 파일에서 확인하는 보조 도구다. 제품 운영·현행 양식·skill·hook에 적용하지 않는다. 기존 시험 묶음은 보존하고 새 실행은 별도 폴더에 준비한다. 생성 주체와 판정 주체는 별도 문맥이며 같은 모델의 역할 분리다. 파일 접근의 보안 격리나 다른 모델의 검증을 뜻하지 않는다.

## 순서와 역할

1. 완료·부모 수용 검사: `record()`의 기본값은 미완료다. `complete_task()`는 실제 조건·미결정·체크와 근거·전달본·막힘을 확인한다. 실패하면 아무 파일도 바꾸지 않고 `Refused`를 반환한다. 부모는 자동으로 닫지 않는다. `accept_parent()`가 부모 원천의 조건과 실제 대상·Task 결과를 별도로 재검사한다.
2. 읽기 전용 검증: 아래 명령은 파일을 수정하지 않고 현재 상태·조건·주석·연결을 대조한다. 새 실행을 만들지 않아도 기존 결과를 검사할 수 있다.
3. 실행자: 지정한 입력과 작성안만 읽고 실제 작업을 선택한다. 예상 상태·점수표·기존 출력은 전달하지 않는다. 모의 사건은 `use_event()`로 해당 시점에 받아 기록한다. 실제 사용자 승인으로 쓰지 않는다.
4. 판정자: 실행 후 원래 기대 조건과 실제 파일·변경·검사 결과를 읽기 전용으로 대조한다. 실행자가 작성한 성공 문구만으로 통과시키지 않는다.

```text
python -B -X utf8 work/records/harness/issue-72/artifacts/task-doc-validation/verify.py --run work/records/harness/issue-72/artifacts/task-doc-suite-c
python -B -X utf8 work/records/harness/issue-72/artifacts/task-doc-validation/verify.py --run work/records/harness/issue-72/artifacts/task-doc-suite-c --case sample-a
```

종료값 0은 현재 문서의 정합성 확인, 1은 위반이다. 중단·취소·미생성은 기대될 수 있으므로 사례별 수용 판정은 별도 검토자가 한다. 관리 문서의 링크와 오류를 포함한 시험 입력을 구별한다.

## 실행자에게 제공할 API

`workflow.py`의 `Workspace(case_folder)`로 한 입력 묶음만 연다. `input.json`, `parent.md`, `assignment*.md`와 현재 대상 파일을 읽는다. 기존 Task가 있으면 현재 상태와 실제 파일·기록을 대조하며 초기화하지 않는다. 신규 Task는 다음처럼 생성하고 생성 직후 상태·수행 기록 부재를 확인한다.

```python
from workflow import Workspace, Refused, field, set_field, text
ws = Workspace(case_folder)
receipt = ws.create_task()  # 필요한 생성 입력이 없으면 Refused, Task는 미생성
```

- `set_plan([(work_id, title, tags), ...])`: 전체 수행 계획을 작성·갱신한다. 기존 수행 식별자·연결을 유지한다. 할 일 개수·종류는 배정에 맞춰 정한다.
- `summary(state, location, next_action, blocked='없음')`: 실제 상태·위치·다음 행동·막힘을 갱신한다. 계획·논의에 착수하면 진행 중으로 맞춘다.
- `record(work_id, action, observation, remaining='없음', done=False, verdict=None)`: 첫 실제 할 일 착수 때 수행 기록을 만들고 이후에는 동일 파일의 구역을 추가·갱신한다. 실제 확인을 갖춘 뒤에만 `done=True, verdict='충족'`을 지정하고 해당 할 일의 잔여는 `없음`으로 시작해야 한다. 확인에는 현재 판정·관찰을 함께 기록한다. 확인 실패·기존 모의 사건과 근거는 보존한다. 전체 과제의 남은 일은 Task 현재 요약·결과에서 관리한다.
- `use_event(event_id, work_id)`: 입력에 열거한 사건 하나를 모의 사용자/제공자 역할에서 전달받는다. 미래 자료의 원문은 전달 시점 전 입력에 포함하지 않는다. 사건의 원문은 수행 기록에 남는다. 선택·자료 제공·추가 요청·부모 개정·취소를 서로 구별한다.
- `apply_files({relative_path: desired_text})`: 현재 허용 대상·선행 자료·선택 근거·부모와 Task의 전달본·동시 수정 충돌을 확인한 뒤 반영한다. 거절은 무변경이다. 직접 파일 쓰기로 이 조건을 우회하지 않는다.
- `move_file(source, destination)`: 허용된 한 파일의 원본·목적 절대 경로와 충돌을 확인하고 이동한다. 상대 링크는 별도로 보정·확인한다.
- `adopt_revision()`: 부모가 이미 확정해 제공한 개정본을 읽고 Task 참조를 맞춘다. 기존 전달본·수행 근거를 보존하고 영향받는 계획·확인도 함께 갱신한다. 새 배정을 대신 정하지 않는다.
- `check_task()`, `check_parent()`: 쓰기 없이 현재 조건의 실제 관찰·미충족을 반환한다. 체크·성공 문구만 믿지 않는다.
- `complete_task()`: 전체 결과를 수용하고 Task만 완료한다. 먼저 각 할 일의 실제 확인·기록, 필수 미결정·막힘, 결과 조건·종료 처리를 갖춘다.
- `accept_parent()`: Task 완료 뒤에도 부모가 바뀌지 않았음을 확인하고, 부모의 실제 전체 조건을 별도로 검사한 후 수용한다.
- `snapshot()`: 거절·읽기 전용 확인 전후에 파일이 바뀌지 않았는지 자동 계산으로 대조한다. 사용자에게 지문 관리 절차를 요구하지 않는다.

`Refused.issues`는 실제 거절 이유다. 거절 전후 `snapshot()`이 같은지 확인하고 필요한 원인·관찰·해소 조건을 기존 수행 기록에 남긴다. 조건이 미충족이면 관련 행동만 제한한다. 다른 허용 활동이 있으면 계속한다. 자료 확보를 새 권한으로, 추가 비교를 선택으로, 취소를 목표 달성으로 바꾸지 않는다.

## 전달 범위

실행자는 이 안내·`workflow.py`·`verify.py`, 지정한 `cases/` 입력, 필요한 Task 작성안만 읽는다. `prepare.py`, `sealed/`의 사건 원문·판정표, 과거 시험 결과는 읽지 않는다. 사건 전달 함수와 판정자는 각자 필요한 원천에 접근한다. 이 제한은 역할 지시이며 OS 수준의 접근 차단은 아니다.

## 판정자 전용과 회귀 검사

실행을 마친 뒤 판정자만 다음 명령으로 해당 실행의 고정 정의·예상 조건을 실제 파일과 대조한다. 판정 명령은 살아 있는 컨트롤러의 최신 사례를 가져오지 않고 해당 묶음의 `sealed/source-cases.json`을 사용하며 파일을 수정하지 않는다. 기계 대조와 원래 사례의 의미 검수는 구별한다.

```text
python -B -X utf8 work/records/harness/issue-72/artifacts/task-doc-validation/judge.py --run work/records/harness/issue-72/artifacts/task-doc-suite-c
python -B -X utf8 work/records/harness/issue-72/artifacts/task-doc-validation/test_guards.py
```

생성 판단은 입력의 특정 키 유무만 보지 않고 실제 담당 원천에 이미 있는 답을 재사용한다. 원천에도 없는 미정·미확인은 확정값으로 세지 않는다. 관찰 JSON은 코드 문맥으로 표시하고 원문 값 자체에 렌더링용 문자를 끼우지 않는다. 사건 보존은 실제 공급 원천의 사건과 일치하는 객체만 대상으로 하며 조건 정의를 사건으로 쓰지 않는다.
