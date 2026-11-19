# 시험용 부모 P

가상 시험이며 실제 번호·승인으로 쓰지 않는다.

- 상태: 진행 중
- 적용 전달본: [전달사항](assignment.md)
- 전달본 식별: r001
- 보유 Task: [Task T](task.md#summary) — 중단; 제한 근거는 자식 현재 요약에 있다.
- 수용 판정: 미수용 — 실제 전체 조건이 미충족이며 자식의 준비·대조를 전체 목표 달성으로 처리하지 않는다.
- 생성 식별 확인: 확인 — 이 시험의 P/T·저장 위치·충돌 부재를 제공한다.
- 다음 행동: 제공자 역할에서 현재 편집 허용과 A/B 선택을 확정하면 영향받는 계획·조건을 다시 확인한다.
- 잔여: 상세 자료는 확보했으나 편집 허용·A/B 선택이 없고 현재 링크가 불일치한다.

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
      "id": "source",
      "kind": "exists",
      "path": "guide.md"
    },
    {
      "id": "link",
      "kind": "links",
      "path": "start.md"
    },
    {
      "id": "choice",
      "kind": "choice",
      "value": "A"
    }
  ]
}
```

<a id="children"></a>
## 자식과 현재 위치

자식 상태만으로 전체 수용을 판단하지 않는다.
