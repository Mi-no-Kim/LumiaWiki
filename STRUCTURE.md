# 프로젝트 구조

일반 프로젝트 영역의 주요 파일·폴더와 역할을 안내한다. 상세 기준·작업 목록·진행 상태는 각 담당 문서에서 관리한다.

```text
lumia_island_wiki/
├── AGENTS.md                       AI 작업 지침과 문서 진입점
├── README.md                       프로젝트 소개와 시작 안내
├── STRUCTURE.md                    주요 경로와 역할
├── .agents/skills/                 요청 판단·검수·응답 형식의 AI 스킬
├── .github/workflows/             하네스 현황 후보 검사·격리 테스트의 CI 정의
├── scripts/                       하네스 현황 검사·Git hook 설치와 격리 검증 도구
│   ├── check-harness-inventory.py 실제 work/index/commit 원천과 현황 대조(읽기 전용)
│   ├── check-work-records.py       변경 후보의 기록 날짜·근거 위치 검사와 100줄 경고
│   ├── harness_inventory.py       후보·경계·등록·지문·확인 상태 판독
│   ├── install-harness-hooks.py   기존 Git hook 보존·중복 설치·복원
│   ├── hooks/pre-commit           프로젝트 관리 Git hook 정의
│   └── tests/                    정상/누락·부분 후보·경계·hook 공존 테스트
├── docs/                           제품 요구와 운영 기준
│   ├── 프로젝트 목표와 범위.md     제품 목표·범위·품질과 공개 조건
│   ├── 하네스 운영 기준.md         운영 기준의 적용 범위와 읽기 안내
│   ├── Git 작업 기준.md            Git 공통 기준과 상세 기준 선택
│   ├── GitHub 저장소 설정 기준.md   GitHub 옵션의 기준값과 기능 지원 범위
│   ├── GitHub 라벨 기준.md          라벨 이름·설명·색상과 적용 규칙
│   ├── details/                    주제별 상세 기준·요구
│   │   ├── operations/             권한·검증과 전체 평가·검수·실패·개선
│   │   ├── product/                제품 주제별 상세 요구
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
│   └── templates/                  로컬 Phase·Issue·Task, GitHub 게시, PR 양식
└── work/                           실제 계획·진행·작업 근거
    ├── README.md                   기록 탐색과 사용 안내
    ├── 현황.md                     현재 작업과 예정의 조회
    └── records/                    실제 계획과 작업 기록
        ├── phase-001/…             제품 Phase와 소속 Issue·Task
        ├── issues/                 독립 제품 Issue
        └── harness/                독립 하네스 정비 Issue
```

| 세부 위치 | 역할 |
|---|---|
| `work/records/phase-001/`부터 `phase-007/`까지 | Phase별 계획과 실제 하위 작업 기록의 위치 |

제품 범위는 [프로젝트 목표와 범위](<docs/프로젝트 목표와 범위.md#current>), 작업 기록의 위치는 [work 안내](<work/README.md#start>)와 [현황](<work/현황.md#current>)에서 더 자세히 확인할 수 있다.
