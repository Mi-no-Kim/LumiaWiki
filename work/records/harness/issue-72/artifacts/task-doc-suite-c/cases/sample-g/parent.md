# 시험용 부모 P

가상 시험이며 실제 번호·승인으로 쓰지 않는다.

- 상태: 진행 중
- 적용 전달본: [전달사항](assignment.md)
- 전달본 식별: r001
- 보유 Task: [Task T](task.md#summary) — 중단; 제한 근거는 자식 현재 요약에 있다.
- 수용 판정: 미수용 — 실제 전체 조건이 미충족이며 자식의 준비·대조를 전체 목표 달성으로 처리하지 않는다.
- 생성 식별 확인: 확인 — 이 시험의 P/T·저장 위치·충돌 부재를 제공한다.
- 다음 행동: 현재 A/B 후보·권고·영향을 보존한 상태로 지정 주체의 모의 선택을 기다린다.
- 잔여: 모의 사용자 역할의 A/B 응답이 없고 후보 준비 뒤 남은 독립 활동이 없다.

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

<a id="children"></a>
## 자식과 현재 위치

자식 상태만으로 전체 수용을 판단하지 않는다.
