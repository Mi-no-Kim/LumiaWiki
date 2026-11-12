# GitHub 라벨 기준

<a id="current"></a>

## 적용

로컬 Issue·Task를 GitHub에 표시할 때 사용하는 라벨의 이름·설명·색상·적용 규칙을 둔다. 작업 단위와 상태의 의미는 [기록 체계](<작업 기록 체계.md#current>)가 소유한다. Phase는 milestone으로 구분하며 이 라벨의 적용 대상은 GitHub Issue·Task다.

<a id="labels"></a>

## 라벨 목록

| 라벨                 | 설명                             | 색상      |
| -------------------- | -------------------------------- | --------- |
| `unit:issue`         | 로컬 Issue에 대응하는 과제       | `#5319E7` |
| `unit:task`          | 로컬 Task에 대응하는 실행 단위   | `#1D76DB` |
| `status:planned`     | 예정                             | `#EDEDED` |
| `status:in-progress` | 진행 중                          | `#0075CA` |
| `status:verifying`   | 검증 중                          | `#FBCA04` |
| `status:blocked`     | 구체 조건에 막혀 대기            | `#D93F0B` |
| `status:on-hold`     | 추진을 미룬 보류                 | `#BFDADC` |
| `status:completed`   | 자기 완료 조건 충족              | `#0E8A16` |
| `status:cancelled`   | 목표 달성으로 처리하지 않고 취소 | `#6E7781` |

<a id="apply"></a>

## 적용 규칙

- Issue·Task마다 단위 라벨 하나와 상태 라벨 하나를 적용한다. 상태는 해당 로컬 기록에서 가져오며 부모 상태를 자식에게 복사하지 않는다.
- 상태가 바뀌면 이전 상태 라벨을 교체한다. Phase 소속은 milestone으로 연결한다.
- 라벨 적용 전에 실제 존재 여부를 확인한다. 생성·정의 변경은 [허용된 저장소 변경 범위](<details/operations/권한과 실행 범위.md>)에서 수행하며, 이 기준 밖의 기존 라벨을 일괄 삭제하거나 이름을 바꾸지 않는다.
- 이름·설명·색상은 이 목록을 원본으로 관리한다. 게시 양식에는 적용할 라벨과 이 기준의 연결만 둔다.

등록 항목은 [GitHub 라벨 안내](https://docs.github.com/en/rest/issues/labels#create-a-label)를 참고한다. 실제 라벨 생성·변경 여부는 문서 정의와 구별한다.
