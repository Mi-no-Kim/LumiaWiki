# 프로젝트 구조

일반 프로젝트 영역의 주요 파일·폴더와 역할을 안내한다. 상세 기준·작업 목록·진행 상태는 각 담당 문서에서 관리한다.

```text
lumia_island_wiki/
├── AGENTS.md                       AI 작업 지침과 문서 진입점
├── README.md                       프로젝트 소개와 시작 안내
├── STRUCTURE.md                    주요 경로와 역할
├── .agents/skills/                 Issue·Task 생성, 요청 판단·검수·응답 형식의 AI 스킬
├── .codex/hooks.json               Codex 편집 전 TDD·편집 뒤 포맷과 기록 주석·상태 검사
├── package.json                    공통 품질·포맷·검사 명령과 루트 Prettier
├── .vscode/                        저장 시 Prettier·Spotless 설정과 권장 확장
├── backend/                        Spring Boot API·Gradle Wrapper·공통/local/test 설정
├── frontend/                       React·Vite 웹 시작 화면·manifest·잠금 파일
├── db/migration/                   backend 밖에서 관리하는 공용 Flyway SQL
├── compose.yaml                    PostgreSQL 로컬 개발 환경
├── .env.example                    비밀값 없는 개인 설정 양식 (.env는 Git 제외)
├── .github/workflows/             영역별 품질·테스트·빌드와 하네스 현황 CI 정의
├── scripts/                        서버 실행·TDD·현황 검사·Git hook 설치·격리 검증 도구
│   ├── tdd-run.py                  실제 테스트 실행·근거 기록/보존
│   ├── tdd-check.py                읽기 전용 편집/제출 후보 검사
│   ├── tdd_core.py                 경로·후보·결과·worktree 근거 처리
│   ├── test-python.py              표준 unittest JSON reporter
│   ├── install-hooks.py            기존 Git hook 연결·해제/복원
│   ├── check-harness-inventory.py 실제 work/index/commit 원천과 현황 대조(읽기 전용)
│   ├── check-work-records.py       변경 후보의 기록 날짜·근거 위치 검사와 100줄 경고
│   ├── check-rule-comments.py     Issue·Task·수행 기록의 공통 주석·상태 검사 진입점
│   ├── rule_comments.py            신규 표준 기록 자동 발견·고정 기존 기록 제외·주석/상태 대조
│   ├── harness_inventory.py       후보·경계·등록·지문·확인 상태 판독
│   ├── install-harness-hooks.py   기존 Git hook 보존·중복 설치·복원
│   ├── hooks/                    품질·현황·기록 pre-commit과 자동 닫기 commit-msg 정의
│   ├── quality/                    허용 경로·포맷·인덱스 검사·편집 hook·CI 분류 실행기
│   └── tests/                      TDD·현황의 정상/거부·후보/worktree·hook 공존·복원 테스트
├── docs/                           제품 요구와 운영 기준
│   ├── 프로젝트 목표와 범위.md     제품 목표·범위·품질과 공개 조건
│   ├── 개발 기준.md                기술·검증 기준 진입점과 서버·데이터 공통 기준
│   ├── 하네스 운영 기준.md         운영 기준의 적용 범위와 읽기 안내
│   ├── Git 작업 기준.md            Git 공통 기준과 상세 기준 선택
│   ├── GitHub 저장소 설정 기준.md   GitHub 옵션의 기준값과 기능 지원 범위
│   ├── GitHub 라벨 기준.md          라벨 이름·설명·색상과 적용 규칙
│   ├── details/                    주제별 상세 기준·요구
│   │   ├── operations/             권한·검증과 전체 평가·검수·실패·개선
│   │   ├── product/                제품 주제별 상세 요구
│   │   ├── development/            기술·DB 환경·테스트/TDD·코드 품질 기준
│   │   └── git/                    브랜치 관리·작업 커밋·PR·병합 기준
│   ├── 작업 기록 체계.md           작업 단위·소유·경로·상태
│   ├── 작업 기록 작성 기준.md      기록할 정보·작성 시점·사전 논의·전환·종료
│   ├── 문서 관리 기준.md           문서 원천·제품 요구와 계획의 관계·보존 경계
│   ├── 문서 참조와 변경 기준.md    참조·이력·정정·변경 영향
│   └── history/                    중요한 요구 변경과 논의 근거의 연결
├── harness/                        수행 절차와 재사용 양식
│   ├── 공용 절차.md                요청부터 수행·확인·결과 반환까지
│   ├── 작업별 절차.md              계획·변경·리뷰 등 작업 종류별 행동
│   ├── 문서 관리.md                문서·기록의 작성·갱신·복구 절차
│   ├── 스킬 현황.md               등록된 스킬·적용 조건·원천
│   ├── hook 현황.md               등록된 hook·실행 조건·원천
│   ├── Git 작업 절차.md            브랜치·커밋·PR·병합 수행
│   ├── Issue 생성 지시서.md        공통 Issue 최초 작성·Phase 연결 처리
│   ├── Issue 공통 절차.md          네 단계·Task 배정·전체 수용
│   ├── Task 생성 지시서.md         확정 전달사항으로 최초 Task 작성
│   ├── Task 공통 절차.md           전체 계획·실행·기록·종료
│   ├── rule-comments.json         고정 기존 기록·정식 주석 기준·명시 개정
│   ├── examples/                  정식 양식의 공용 예시
│   └── templates/                 본문·입력·수행 기록, GitHub 게시, PR 양식
│       ├── issue-input.md / issue.md  Issue 생성 입력 / 최초 본문
│       ├── task-input.md / task.md    확정 배정 전달사항 / 최초 Task 본문
│       └── task-execution.md          첫 할 일 착수 때 수행 기록 최초 생성
└── work/                           실제 계획·진행·작업 근거
    ├── README.md                   기록 탐색과 사용 안내
    ├── 현황.md                     현재 작업과 예정의 조회
    └── records/                    실제 계획과 작업 기록
        ├── phase-001/…             제품 Phase와 소속 Issue·Task
        ├── issues/                 독립 제품 Issue
        └── harness/                독립 하네스 정비 Issue
```

| 세부 위치                                                                                                                                                               | 역할                                      |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| [`.agents/skills/create-issue/`](.agents/skills/create-issue/SKILL.md) · [`.agents/skills/create-task/`](.agents/skills/create-task/SKILL.md)                           | Issue·Task 최초 작성·입력 확인의 진입점   |
| [`.agents/skills/triage-additional-request/`](.agents/skills/triage-additional-request/SKILL.md) · [`.agents/skills/review-work/`](.agents/skills/review-work/SKILL.md) | 추가 요청의 작업 단위 판단과 결과 검수    |
| `harness/스킬 현황.md` · `harness/hook 현황.md`                                                                                                                         | 등록 항목·적용 조건·원천·확인 범위의 조회 |
| `work/records/phase-001/`부터 `phase-007/`까지                                                                                                                          | Phase별 계획과 실제 하위 작업 기록의 위치 |
| 담당 Issue 직하 `task-<순번>.md`                                                                                                                                        | Task 본문                                 |
| 담당 Issue의 `artifacts/task-<순번>-assignment.md`                                                                                                                      | 확정 배정 전달사항 원본                   |
| 담당 Issue의 `artifacts/task-<순번>-execution.md`                                                                                                                       | 착수 후 수행 기록                         |

식별·소유·경로는 [기록 체계](<docs/작업 기록 체계.md#paths>), 작성·검사·실패 대응은 [문서 관리](<harness/문서 관리.md#entry>)에서 확인한다.

제품 범위는 [프로젝트 목표와 범위](<docs/프로젝트 목표와 범위.md#current>), 작업 기록의 위치는 [work 안내](work/README.md#start)와 [현황](work/현황.md#current)에서 더 자세히 확인할 수 있다.
