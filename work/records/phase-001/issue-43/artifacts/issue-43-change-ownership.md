# Issue #43 변경 소유와 브랜치 배치

<a id="current"></a>

[책임 원천](<../../../../../docs/작업 기록 체계.md#ownership>)과 [기존 합의](../../issue-15/artifacts/task-005-issue-outline.md#issues)에 따라 변경 목적을 대조했다. 실제 자료 작업은 계속 보류한다.

## Issue 담당

Issue #43은 목표/범위·전체 수용 조건, 네 Task의 분해·계획 준비·등록/선후 관계, 부모·현황의 진행 표시를 맡는다. Issue 준비 커밋에는 issue.md·Task 001~004의 계획/등록 정보·Phase/현황과 이 대조 기록을 둔다. Task의 자기 완료 사실은 유지하며 실제 구현/검증은 보존된 Task 원본으로 연결한다. 사후 분리를 과거의 사전 준비로 기록하지 않는다.

## Task 43-001 담당

공유 버전/참조의 상세 합의, 시즌/패치·지역/분류의 저장 계약과 최초 구동, DDL·Java 저장/조회·권한/검사, 관련 테스트·DB 문서와 실행 근거는 Task 001 담당이다. 제품 구현에 필요한 실행기/검사 도구와 관련 기준·인계 문서의 동반 보완도 같은 Task에 둔다.

| 변경 묶음 | 소유·이유 |
| --- | --- |
| Issue43 본문·네 Task 정의/등록·Phase/현황 | Issue 준비·보유 관계/전체 수용과 현재 상태 표시 |
| Task001 본문의 상세 실행 계약/근거 연결 | Task 자기 계획·실행/검증·완료의 원천. Issue 준비본은 실제 완료 사실과 보존된 상세 원본을 연결하며 Task 브랜치에서 로컬 실행 근거와 함께 읽음 |
| Task001 artifacts·공유 계약과 제품/개발 기준 보완 | Task001의 상세 결정·검증과 그 직접 영향 |
| backend·db·Compose·환경 예제·실행/검사 도구 | Task001의 공통 저장/조회·최초 구동 구현/검증 |
| README·STRUCTURE·관련 인계/도구 현황 | Task001 구현을 사용하는 데 필요한 직접 안내/원천 대응 |

## 브랜치 배치와 보존

- 부모: phase/001-item-foundation의 0239caa에서 issue/43-item-persistence의 준비/등록 커밋을 만든다.
- Task: 그 Issue 준비 커밋에서 task/43-001-common-storage를 분기하고 Task 담당 변경만 배치한다.
- 보존: 49c39d4·45ec5d7·9b8773e는 기존 task/43-001-common-model과 로컬 codex/preserved-43-before-split에 그대로 남긴다. 기존에 게시한 ref를 덮어쓰거나 삭제하지 않는다.
- 원본: [보존 커밋](https://github.com/Mi-no-Kim/LumiaWiki/tree/9b8773ed5a26b799eac971ea8fe60949e14c4d0a). 공통 모델·실행 근거는 이 원본과 새 Task 브랜치에서 찾는다.

이번 요청에서는 PR·병합·DB 작업을 하지 않는다. Issue 브랜치에 Task 코드가 반영됐거나 Issue/Phase가 완료됐다고 판정하지 않는다. Task 001 자기 결과 완료와 이후 통합/부모 수용은 구별한다. 후속 002~004와 #45 실제 자료 작업은 기존 담당·보류 조건을 유지한다.
