# 시험용 부모 P

가상 시험이며 실제 번호·승인으로 쓰지 않는다.

- 상태: 진행 중
- 적용 전달본: [전달사항](assignment.md)
- 전달본 식별: r001
- 보유 Task: [Task T](task.md#summary) — 취소; 맡았던 링크·중복 문제 해소는 미충족이다.
- 수용 판정: 미수용 — 자식 취소는 목표 달성이 아니다. 실제 전체 조건을 검사했으며 필수 링크·중복 결과와 최종 선택이 남는다.
- 생성 식별 확인: 확인 — 이 시험의 P/T·저장 위치·충돌 부재를 제공한다.
- 다음 행동: 취소된 자식의 후보·원문·취소 근거를 보존하고 부모 담당 역할이 대체 작업 또는 범위 변경을 판단한다. 판단 전에는 전체 완료로 처리하지 않는다.
- 잔여: 필수 링크·중복 문제 해소와 최종 안내 방식이 미완료다. 대체 작업 배정 또는 범위 변경은 미정이며 새 선택·Task를 만들지 않았다.

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
