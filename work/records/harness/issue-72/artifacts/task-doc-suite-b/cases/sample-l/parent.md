# 시험용 부모 P

가상 시험이며 실제 번호·승인으로 쓰지 않는다.

- 상태: 완료
- 적용 전달본: [전달사항](assignment.md)
- 전달본 식별: r001
- 보유 Task: [Task T](task.md#summary)
- 수용 판정: {"issues": [], "observations": [{"id": "child-result", "satisfied": true, "observation": ""}, {"id": "link", "satisfied": true, "observation": ""}, {"id": "layout", "satisfied": true, "observation": ""}, {"id": "guide", "satisfied": true, "observation": ""}, {"id": "choice", "satisfied": true, "observation": ""}, {"id": "user-note", "satisfied": true, "observation": ""}, {"id": "detail-5", "satisfied": true, "observation": ""}, {"id": "detail-6", "satisfied": true, "observation": ""}]}

<a id="assignment"></a>
## 배정과 전체 수용 조건

```json
{
  "criteria": [
    {
      "id": "child-result",
      "kind": "task_complete"
    },
    {
      "id": "link",
      "kind": "links",
      "path": "start.md"
    },
    {
      "id": "layout",
      "kind": "contains",
      "path": "start.md",
      "value": "작업 상태와 상세 기록의 작성 방법을 확인하세요."
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
    },
    {
      "id": "user-note",
      "kind": "contains",
      "path": "start.md",
      "value": "이 안내는 내부 작업자를 위한 것입니다."
    },
    {
      "id": "detail-5",
      "kind": "absent_text",
      "path": "start.md",
      "value": "Task 본문은 현재 상태와 계획을 관리합니다."
    },
    {
      "id": "detail-6",
      "kind": "absent_text",
      "path": "start.md",
      "value": "자세한 수행 내용은 별도 수행 기록에 남깁니다."
    }
  ]
}
```

<a id="children"></a>
## 자식과 현재 위치

자식 상태만으로 전체 수용을 판단하지 않는다.
