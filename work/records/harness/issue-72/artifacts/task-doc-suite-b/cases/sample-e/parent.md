# 시험용 부모 P

가상 시험이며 실제 번호·승인으로 쓰지 않는다.

- 상태: 완료
- 적용 전달본: [전달사항](assignment.md)
- 전달본 식별: r001
- 보유 Task: [Task T](task.md#summary)
- 수용 판정: {"issues": [], "observations": [{"id": "child-result", "satisfied": true, "observation": ""}, {"id": "criteria-수동", "satisfied": true, "observation": ""}, {"id": "criteria-로컬", "satisfied": true, "observation": ""}, {"id": "criteria-재현", "satisfied": true, "observation": ""}, {"id": "criteria-준비", "satisfied": true, "observation": ""}, {"id": "criteria-범위", "satisfied": true, "observation": ""}, {"id": "criteria-후속", "satisfied": true, "observation": ""}, {"id": "method", "satisfied": true, "observation": ""}]}

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

<a id="children"></a>
## 자식과 현재 위치

자식 상태만으로 전체 수용을 판단하지 않는다.
