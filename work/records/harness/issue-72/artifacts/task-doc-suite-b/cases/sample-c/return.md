# 생성 입력 보완 반환

- 관찰: create_task 호출은 Refused: ["missing creation input: acceptance"]
- 보존: 거절 전후 snapshot 동일. Task·수행 기록 미생성, 부모·대상 원문 무변경.
- 필요한 보완: ["missing creation input: acceptance"]. 누락 답은 다른 원천에 없다는 입력을 유지하며 추론하지 않는다.
- 다음 행동: 제공자가 누락 생성 입력을 확정한 뒤 생성 여부를 다시 판단한다.
