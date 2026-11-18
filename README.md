# 루미아 아일랜드 위키

게임 정보와 패치 이력을 조회하고, 아이템 제작·수집 루트와 피해량 계산을 지원하기 위한 위키 프로젝트다.

## 목표 기능

- 아이템 등 게임 대상의 정보와 변경 이력 조회
- 개별 패치노트의 변경 내용 정리
- 장비 조합·재료 수집·배달을 고려한 루트 계산
- 게임 규칙에 따른 피해량 계산과 변경 조건의 성능 비교
- AI를 활용한 패치노트 데이터 변환

제품 범위·공개 조건과 기능별 요구는 [프로젝트 목표와 범위](<docs/프로젝트 목표와 범위.md#current>) 및 연결된 제품 문서에서, 단계별 실현 범위·순서는 [현황에서 연결한 Phase 계획](<work/현황.md#harness-record-separation>)에서 관리한다.

## 현재 상태

요구사항과 7개 Phase의 계획을 문서로 정리한 단계다. 제품 기능 구현에는 아직 착수하지 않았다.

현재 진행 상황과 다음 작업은 [작업 현황](<work/현황.md#current>)에서 확인한다. 기술 구성과 설치·실행·테스트 방법은 실제 구현에 맞춰 추가한다.

## 프로젝트 구성

| 위치 | 내용 |
|---|---|
| [AGENTS.md](<AGENTS.md>) | AI의 작업 진입 지침 |
| [STRUCTURE.md](<STRUCTURE.md>) | 주요 파일·폴더의 위치와 역할을 안내하는 지도 |
| `docs/` | 제품 요구사항과 프로젝트 운영 기준 |
| `harness/` | 작업 절차와 문서·기록 양식 |
| `work/` | 계획, 진행 현황, 실제 논의·작업·검증 기록 |
| `harness-design/` | 별도로 관리하는 하네스 설계 도구. 아래 접근 제한 적용 |

<a id="start"></a>

## 시작하기

AI와 작업할 때는 원하는 결과와 대상, 허용 범위를 전달한다. 기존 작업을 이어가는 경우 담당 기록이나 관련 파일을 함께 지정한다.

- 제품 목표와 범위: [프로젝트 목표와 범위](<docs/프로젝트 목표와 범위.md#current>)
- 작업 찾기와 재개: [work 안내](<work/README.md#start>), [작업 현황](<work/현황.md#current>)
- AI 작업 지침: [AGENTS.md](<AGENTS.md>)
- 공통 작업 절차: [공용 절차](<harness/공용 절차.md#entry>)
- 프로젝트 구성: [스킬 현황](<harness/스킬 현황.md#current>) · [hook 현황](<harness/hook 현황.md#current>)

### 작업 절차 찾기

| 상황 | 시작점 |
|---|---|
| 새 Issue 작성 | [create-issue](<.agents/skills/create-issue/SKILL.md>) · [생성·등록](<harness/문서 관리.md#create>) |
| 확정 배정으로 Task 작성 | [create-task](<.agents/skills/create-task/SKILL.md>) · [배정 확인](<harness/문서 관리.md#task-create>) |
| 기존 작업 진행·재개 | [work 안내](<work/README.md#resume>) · 담당 기록의 현재 요약 |
| 추가·변경 요청 | [추가 요청 판단](<.agents/skills/triage-additional-request/SKILL.md>) |
| 결과 검수 | [작업 결과 검수](<.agents/skills/review-work/SKILL.md#common-review>) |

### hook 확인과 문제 해결

- 설치 상태·설치/해제: [Git hook 설치 안내](<harness/문서 관리.md#inventory-hook-install>)
- 검사 대상·명령: [공통 기록 검사](<harness/문서 관리.md#record-rule-comment-check>)
- 실패 시 점검·수정·재검사: [검사 실패 대응](<harness/문서 관리.md#record-check-failure>)

정의의 존재·설치·실제 자동 발동의 확인 범위는 [hook 현황](<harness/hook 현황.md#current>)에서 구분한다. 파일 위치는 [프로젝트 구조](STRUCTURE.md)에서 확인한다.

작업 결과와 변경 내용, 확인 범위·한계, 미해결 사항과 다음 행동은 대화와 담당 작업 기록에서 확인한다.

## 접근 제한: harness-design

**사용자의 명시적 요청 없이는 `harness-design/`에 접근하지 않는다.**

이 영역은 참고자료를 바탕으로 사용자와 설계를 결정하고 하네스를 생성·검증하기 위한 독립 도구다. 일반 위키 작업의 필수 입력으로 사용하지 않는다.

- 일반 작업의 읽기·검색·목록 조회·비교 대상에서 제외한다.
- 문서의 링크나 과거 지시를 따라 자동으로 접근하지 않는다.
- 접근 요청이 있으면 허용된 대상과 행동 범위에서만 수행한다.
- 현재 프로젝트 문서와 자동 비교·동기화하지 않는다.
- 새 위키 개발·운영 기록은 `work/`에서 관리한다.

관련 `.harness-state/`도 명시적으로 허용된 범위에서만 접근한다. 상세 기준은 [원천과 보존 경계](<docs/문서 관리 기준.md#harness-design-boundary>)를 따른다.
