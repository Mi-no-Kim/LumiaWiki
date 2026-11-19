# 생성 입력 보완 반환

- 관찰: create_task 호출은 Refused: ["missing creation input: creation"]
- 보존: 거절 전후 snapshot 동일. Task·수행 기록 미생성, 부모·대상 원문 무변경.
- 원천 확인: input.json뿐 아니라 현재 assignment의 목적·기대 결과·조건과 parent의 생성 확인·조건을 읽고 확보된 답을 재사용했다.
- 필요한 보완: Task 식별·저장 위치·기존 파일 충돌 확인 근거를 제공해야 한다. 현재 원천에서 미정·빈 조건·미확인임을 대조했으며 추론하지 않는다.
- 다음 행동: 제공자가 누락 생성 입력을 확정한 뒤 생성 여부를 다시 판단한다.
