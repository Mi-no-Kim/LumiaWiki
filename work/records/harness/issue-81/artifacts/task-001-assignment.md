# Task 81-001 확정 전달사항

- 태그: 실행, 검수, 커밋

<a id="purpose"></a>

## 목적

GitHub가 기본 Ubuntu 이미지를 바꿔도 하네스 현황 검사의 실행 환경이 달라지지 않게 한다.

<a id="result"></a>

## 기대 결과

main에서 분기한 독립 작업 브랜치의 Ubuntu CI 러너가 24.04를 사용한다.

<a id="scope"></a>

## 이미 정해진 조건

- 조건: Ubuntu 러너만 24.04로 고정한다. Python·Windows·실행 조건은 유지한다.
  - 적용 범위: `.github/workflows/harness-inventory.yml`.
  - 확정 근거: [부모 Issue의 배정](../issue.md#ubuntu-assignment).
- 조건: 43-002와 분리하고 실제 검사 결과를 확인한다. 병합은 보류한다.
  - 적용 범위: 환경 수정·검사·제출.
  - 확정 근거: [부모 Issue의 배정](../issue.md#ubuntu-assignment).

<a id="decisions"></a>

## Task에서 결정할 사항

추가 결정 없음. 브랜치 이름 훅은 부모 Issue 후속 검토 범위다.

<a id="acceptance"></a>

## 완료 조건과 확인 방법

- 완료 조건: Ubuntu 설정 변경이 24.04 지정에 한정되고 Ubuntu·Windows 현황 검사가 통과한다.
  - 확인 방법: 원격 main 기준의 워크플로 차이와 GitHub Actions의 실제 결과를 대조한다.
