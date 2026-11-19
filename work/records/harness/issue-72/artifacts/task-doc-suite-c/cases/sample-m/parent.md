# 시험용 부모 P

가상 시험이며 실제 번호·승인으로 쓰지 않는다.

- 상태: 완료
- 적용 전달본: [전달사항](assignment.md)
- 전달본 식별: r001
- 보유 Task: [Task T](task.md#summary) — 완료; 실제 자식 결과를 전체 조건과 별도로 대조했다.
- 수용 판정: {"issues": [], "observations": [{"id": "child-result", "satisfied": true, "observation": ""}, {"id": "old-location", "satisfied": true, "observation": ""}, {"id": "new-location", "satisfied": true, "observation": ""}, {"id": "link-0", "satisfied": true, "observation": ""}, {"id": "link-1", "satisfied": true, "observation": ""}, {"id": "link-2", "satisfied": true, "observation": ""}, {"id": "body", "satisfied": true, "observation": ""}]}
- 생성 식별 확인: 확인 — 이 시험의 P/T·저장 위치·충돌 부재를 제공한다.
- 다음 행동: 이 시험의 실제 결과·독립 수용 근거를 판정자에게 인계한다.
- 잔여: 없음 — 현재 전체 조건을 실제 파일·Task 근거와 별도로 검사해 수용했다. 가상 시험의 범위다.

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
