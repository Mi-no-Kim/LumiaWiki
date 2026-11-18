# 시험용 전달사항

- 태그: 조사, 논의, 결정, 실행, 검수

## 목적

두 문서의 링크 점검 방법을 비교하고 선정·이유·후속 조건을 정리한다.

## 기대 결과

두 문서의 링크 점검 방법을 비교하고 선정·이유·후속 조건을 정리한다.

## 이미 정해진 조건

이 문서의 허용 대상·선행 입력·완료 조건을 따른다. 모의 사용자 사건은 실제 사용자 승인으로 쓰지 않는다.

## Task에서 결정할 사항

수동 대조와 로컬 검사 방식을 비교한 뒤 모의 사용자 역할이 선택한다.

## 완료 조건과 확인 방법

다음 조건 정의를 실제 파일·선택 근거와 대조한다. 생성 입력의 사본을 Task 현재 값으로 바꾸지 않는다.

```json
{
  "allowed_writes": [],
  "criteria": [
    {
      "id": "criteria-수동",
      "kind": "contains",
      "path": "execution.md",
      "value": "수동"
    },
    {
      "id": "criteria-로컬",
      "kind": "contains",
      "path": "execution.md",
      "value": "로컬"
    },
    {
      "id": "criteria-재현",
      "kind": "contains",
      "path": "execution.md",
      "value": "재현"
    },
    {
      "id": "criteria-준비",
      "kind": "contains",
      "path": "execution.md",
      "value": "준비"
    },
    {
      "id": "criteria-범위",
      "kind": "contains",
      "path": "execution.md",
      "value": "범위"
    },
    {
      "id": "criteria-후속",
      "kind": "contains",
      "path": "execution.md",
      "value": "후속"
    },
    {
      "id": "method",
      "kind": "choice",
      "value": "manual"
    }
  ]
}
```
