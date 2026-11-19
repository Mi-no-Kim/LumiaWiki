# 시험용 전달사항

- 태그: 조사, 논의, 결정, 실행, 검수

## 목적

시작 안내의 링크·중복을 정리하고 선택·확인 근거를 남긴다.

## 기대 결과

시작 안내의 링크·중복을 정리하고 선택·확인 근거를 남긴다.

## 이미 정해진 조건

이 문서의 허용 대상·선행 입력·완료 조건을 따른다. 모의 사용자 사건은 실제 사용자 승인으로 쓰지 않는다.

## Task에서 결정할 사항

A는 짧은 설명 한 문장과 기록 방법 링크, B는 기록 방법 링크만 남기는 안이다. 두 안 모두 상세 두 문장의 중복을 줄인다. 모의 사용자 역할이 비교 뒤 선택하며 AI 권고는 선택을 대신하지 않는다.

## 완료 조건과 확인 방법

다음 조건 정의를 실제 파일·선택 근거와 대조한다. 생성 입력의 사본을 Task 현재 값으로 바꾸지 않는다.

```json
{
  "allowed_writes": [
    "start.md"
  ],
  "required_sources": [
    "guide.md"
  ],
  "criteria": [
    {
      "id": "link",
      "kind": "links",
      "path": "start.md"
    },
    {
      "id": "layout",
      "kind": "equals",
      "path": "start.md",
      "value": "# 시작 안내\n\n작업 상태와 상세 기록의 작성 방법을 확인하세요.\n\n[기록 방법 보기](guide.md#recording)\n"
    },
    {
      "id": "guide",
      "kind": "equals",
      "path": "guide.md",
      "value": "# 기록 안내\n\n<a id=\"recording\"></a>\n## 기록 방법\n\nTask 본문은 현재 상태와 계획을 관리합니다.\n자세한 수행 내용은 별도 수행 기록에 남깁니다.\n"
    },
    {
      "id": "choice",
      "kind": "choice",
      "value": "A"
    }
  ]
}
```
