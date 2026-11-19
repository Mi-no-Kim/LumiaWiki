# 시험용 부모 P

가상 시험이며 실제 번호·승인으로 쓰지 않는다.

- 상태: 완료
- 적용 전달본: [전달사항](assignment.md)
- 전달본 식별: r001
- 보유 Task: [Task T](task.md#summary)
- 수용 판정: {"issues": [], "observations": [{"id": "child-result", "satisfied": true, "observation": ""}, {"id": "old-location", "satisfied": true, "observation": ""}, {"id": "new-location", "satisfied": true, "observation": ""}, {"id": "link-0", "satisfied": true, "observation": ""}, {"id": "link-1", "satisfied": true, "observation": ""}, {"id": "link-2", "satisfied": true, "observation": ""}, {"id": "body", "satisfied": true, "observation": ""}]}

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

<a id="children"></a>
## 자식과 현재 위치

자식 상태만으로 전체 수용을 판단하지 않는다.
