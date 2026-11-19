# 시험용 전달사항

- 태그: 조사, 논의, 결정, 실행, 검수

## 목적

시작 안내의 링크·중복을 정리하고 선택·확인 근거를 남긴다.

## 기대 결과

시작 안내의 링크·중복을 정리하고 선택·확인 근거를 남긴다.

## 이미 정해진 조건

이 문서의 허용 대상·선행 입력·완료 조건을 따른다. 모의 사용자 사건은 실제 사용자 승인으로 쓰지 않는다.

## Task에서 결정할 사항

주어진 선택·위임 범위 안에서 판단하고 미제공 결정은 만들지 않는다.

## 완료 조건과 확인 방법

다음 조건 정의를 실제 파일·선택 근거와 대조한다. 생성 입력의 사본을 Task 현재 값으로 바꾸지 않는다.

```json
{
  "allowed_writes": [
    "start.md",
    "index.md",
    "guides/recording.md"
  ],
  "allowed_moves": [
    [
      "guide.md",
      "guides/recording.md"
    ]
  ],
  "criteria": [
    {
      "id": "old-location",
      "kind": "missing",
      "path": "guide.md"
    },
    {
      "id": "new-location",
      "kind": "exists",
      "path": "guides/recording.md"
    },
    {
      "id": "link-0",
      "kind": "links",
      "path": "start.md"
    },
    {
      "id": "link-1",
      "kind": "links",
      "path": "index.md"
    },
    {
      "id": "link-2",
      "kind": "links",
      "path": "guides/recording.md"
    },
    {
      "id": "body",
      "kind": "equals",
      "path": "guides/recording.md",
      "value": "# 기록 안내\n\n<a id=\"recording\"></a>\n## 기록 방법\n\nTask 본문은 현재 상태와 계획을 관리합니다.\n자세한 수행 내용은 별도 수행 기록에 남깁니다.\n\n[시작 안내로 돌아가기](../start.md)\n"
    }
  ]
}
```
