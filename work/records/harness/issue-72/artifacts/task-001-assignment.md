# Task 72-001 전달사항

- 전달본 식별: r001
- 배정 원본: ../issue.md#live-registration-validation
- 확정 근거: 사용자의 “누락된 status:paused·status:cancelled 라벨을 등록하고, 실제 GitHub Issue·Task 생성과 부모 연결까지 검증해줘.” 요청. Task 생성·연결 검증의 배정 결과를 그대로 전달한다.
- 식별·경로: work/records/harness/issue-72/task-001.md. Issue #72의 보유 목록·직하 파일과 GitHub sub-issue 조회에서 기존 Task가 없음을 확인해 001을 배정한다.
- 태그: 검수

## 목적
실제 Task 본문·GitHub sub-issue 생성과 부모 Issue #72 연결이 정합한지 확인할 등록 검증용 Task를 마련한다.

## 기대 결과
실제 번호·URL이 연결된 로컬 Task와 GitHub sub-issue, 실제 부모 관계, 단위·상태 라벨과 원본/배정 참조를 갖춘다. 생성 직후에는 예정·본작업 미착수로 유지한다.

## 이미 정해진 조건
- 대상 저장소는 Mi-no-Kim/LumiaWiki, 실제 부모 Issue는 #72다. 독립 하네스 Issue 아래이므로 milestone은 설정하지 않는다.
- 로컬 Task 순번 001과 GitHub 발급 번호를 구별한다. 본문은 이 전달본과 부모 배정 근거를 참조한다.
- 본작업 실행·제품 구현·DB 변경·브랜치 조작·push·PR은 수행하지 않는다. 수행 기록은 생성하지 않는다.
- 생성·연결 확인을 마치면 검증용 객체를 취소 사유와 함께 닫고 기록·번호·부모 관계를 보존한다. Task의 자기 완료나 부모 #72 전체 완료로 처리하지 않는다.

## Task에서 결정할 사항
미정 — 후속 본작업의 상세 계획은 착수 요청이 있을 때 합의한다. 이번 요청은 생성·연결 검증까지만 수행한다.

## 완료 조건과 확인 방법
- 로컬 Task와 GitHub 번호·URL 및 실제 부모 #72가 일치한다. Task 조회와 부모의 sub-issue 재조회로 대조한다.
- unit:task·status:planned, milestone 없음과 게시 원본/배정 참조가 로컬 기록과 일치한다. 생성 직후 본작업 미착수와 수행 기록 부재를 확인한다.
- 검증 종료 후 취소 상태·사유와 반영 결과를 기록한다. 실제 Task 본작업의 수행·수용을 완료로 만들지 않는다.
