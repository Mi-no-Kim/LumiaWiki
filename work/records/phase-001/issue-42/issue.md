# 실행·개발·검증 기반

<a id="summary"></a>
## 현재 요약

- 제목: 실행·개발·검증 기반
- 실제 GitHub Issue: [Mi-no-Kim/LumiaWiki #42](https://github.com/Mi-no-Kim/LumiaWiki/issues/42)
- 소속 Phase: [Phase 001](<../phase.md#summary>)
- 상태: 진행 중
- 현재 진행 위치: 하위 Task 001~004(GitHub #50~#53)를 등록했고 Task 001의 실행 기반 구현·검증을 완료했다. Task 002~004는 예정이며 실제 게임 자료 작업과 후속 Task 구현은 수행하지 않았다.
- 다음 판단/행동: [Task 001 결과](<task-001.md#result>)를 반환한다. Task 001 구현 `95cafce`와 준비 `d8133e3`을 push했고 [PR #54](https://github.com/Mi-no-Kim/LumiaWiki/pull/54)로 이 Issue에 통합한다. 후속 Task는 예정으로 유지한다. Issue 전체 수용은 아직 충족 판정하지 않았다.
- 작성 근거: [Task 005](<../issue-15/task-005.md#summary>) · [전체 실행 순서](<../issue-15/artifacts/task-005-issue-outline.md#sequence>). 실제 자료 작업 보류를 유지한다.

<a id="goal"></a>
## 목표와 범위

선택한 기술과 버전으로 실행·개발·검증 환경을 마련해 후속 기능 과제가 사용할 수 있게 한다. 프로젝트·DB 접속·테스트/hook·공통 골격·품질/CI를 맡는다.

<a id="plan"></a>
## 선행 결과와 필요한 입력

- 선행 계획 Issue #15의 완료와 PR #49의 병합(commit `1a4df18`), 부모 Phase 브랜치의 원격/로컬 일치를 2026-11-12에 확인했다. #42는 기존 등록을 재사용하며 중복 Issue를 만들지 않는다.
- [Task 003 기술·공통 전제](<../issue-15/task-003.md#summary>)와 [Phase의 첫 기능 착수 조건](<../phase.md#tdd-readiness>)을 입력으로 사용한다. 실제 게임 자료는 필요 입력으로 강제하지 않는다.

<a id="foundation"></a>
## 실행·개발·검증 기반

<a id="task-outline"></a>
### 보유 Task

| 로컬 Task / GitHub sub-issue | 담당 결과·선후 관계 |
|---|---|
| [Task 42-001: 프로젝트 골격·실행 환경·DB 연결](<task-001.md#summary>) / [#50](https://github.com/Mi-no-Kim/LumiaWiki/issues/50) | 웹·서버·개발 DB 실행, 공통/local/test 설정 틀·SQL 리소스·보존 확인. 첫 실행 단위 |
| [Task 42-002: 테스트 실행 환경·최소 TDD hook](<task-002.md#summary>) / [#51](https://github.com/Mi-no-Kim/LumiaWiki/issues/51) | Task 001 골격 직후 테스트 명령·전용 DB·hook 연결/실측. 첫 제품 기능 동작 구현의 선행 조건 |
| [Task 42-003: 공통 웹·API·이미지 제공 골격](<task-003.md#summary>) / [#52](https://github.com/Mi-no-Kim/LumiaWiki/issues/52) | Task 001·002 뒤 공통 연결/오류/로그/문서/이미지를 확인. 제품 시각 디자인은 Issue #44 |
| [Task 42-004: 코드·문서 검사·포맷·CI 연결](<task-004.md#summary>) / [#53](https://github.com/Mi-no-Kim/LumiaWiki/issues/53) | 로컬 명령·Task 002 hook을 입력으로 품질·포맷·CI 연결. 최종 CI는 Task 003까지 포함한 후보로 확인 |

<a id="acceptance"></a>
### 합의한 수용 조건

- 웹·서버·DB가 선택한 구성으로 실행되고 개발/테스트 DB·설정이 분리된다. 공통 API·오류·이미지 제공 골격을 후속 과제가 사용할 수 있다.
- 테스트·hook은 실제 동작하고 첫 기능 구현의 착수 조건을 충족한다. 예외·검사 근거·실측 비용도 [채택 기준](<../issue-15/task-003.md#tdd-automation-handoff>)에 맞게 확인한다.
- 로컬 검사·테스트·빌드 및 CI 독립 실행을 확인한다. 정상 통과와 통제한 실패가 CI 결과에 반영되고 TypeScript 호환 검사·문서/일괄/자동 포맷·제출 후보 검사가 연결된다.

테이블 설계·게임 자료 등록과 실제 제품 기능은 이 Issue의 완료로 판정하지 않는다. 기반은 위 네 Task와 공통 골격의 범위로 구성한다.

<a id="pending"></a>
## Task 선후 관계와 남은 결정

- Task 001 → Task 002 순으로 진행한다. 첫 제품 기능의 동작 구현은 Task 002의 hook 필수 검증 완료 뒤 시작한다.
- Task 003의 동작 구현은 Task 002 뒤 진행한다. Task 004는 Task 001 뒤 설계를 준비하고 Task 002의 hook을 보존해 연결한다. CI는 로컬 명령 준비 후 연결하고 Issue 완료 전에 최종 기반 후보의 실제 통과/실패를 확인한다.
- CI 도구·트리거·명령·영향 영역 판별, 보조 패키지 버전과 실제 실행 명령은 담당 설계에서 기존 채택 조건 안으로 구체화한다.

<a id="related"></a>
## 기준·검증 배정

[상세 배정 요구](<../issue-15/artifacts/task-005-handoff-requirements.md#requirements>) · [Task 003 인계](<../issue-15/artifacts/task-003-handoff.md#handoff-decisions>)

<a id="preparation"></a>
## 준비 범위와 검증

- 2026-11-12 요청: #42 준비와 하위 Task 등록. 종료된 #15의 추가 수정이 아닌 #42의 실행 준비로 처리한다. 이번 변경은 계획·등록 기록이며 제품 구현, 실제 자료 조사·확보·처리, 커밋·push·PR·병합은 수행 범위에 포함하지 않는다.
- 기존 #42 Open·Phase milestone #1·단위/예정 라벨, 하위 Task 미등록과 일반 작업 영역의 미커밋 변경 부재를 확인한 뒤 `issue/42-development-foundation`을 부모 Phase에서 분기했다.
- 준비의 수용 조건: 네 Task의 목표·범위·자기 완료 조건·입력·미정/결정 시점·실행/검증 순서, 실제 sub-issue 부모 관계·milestone·라벨·상태·원본 경로, Phase/현황과 첫 기능 착수 조건의 연결을 대조한다. 구현 성과나 Issue 완료를 판정하는 검증과 구별한다.
- Task별 사용자 확인 목록은 계획 초안이다. 구현 직전 실제 명령·주소·대상을 확정해 공유하며 자동 검사·AI 직접 조작·사용자 확인 결과를 구분한다. 현재 실제 도구 호환 설치·빌드·DB·hook·CI·화면 동작은 미확인이다.
- 준비 검증 결과(2026-11-12): 자체 내용 대조로 네 Task의 담당 범위·수용 조건·선후 관계·미정/결정 시점과 기존 기술/hook/품질 인계를 확인했다. 변경/신규 Markdown 7개와 로컬 참조·표식 92개, 등록 번호·공백을 확인했다. GitHub #42는 Open·unit:issue/status:in-progress, #50~#53은 Open·unit:task/status:planned·실제 부모 #42이며 모두 milestone #1에 속한다. Task·Issue의 실제 저장 본문과 Phase 설명 반영도 대조했다. 구현·실행 검증이나 Issue 전체 완료를 뜻하지 않는다. 등록 검증 당시 로컬 기록은 미커밋·원격 미게시였으며 GitHub 원본 표시는 실제 로컬 경로다.

<a id="preparation-review"></a>
## 준비 결과 검수와 Task 전환

- 추가 요청(2026-11-12): 준비 내용 검수·커밋 후 첫 Task로 전환한다. #42의 준비 결과 제출과 기존 Task 선택이며 새 Issue/Task는 만들지 않는다. 기존 미커밋 7개 파일을 같은 목적의 준비 기록 커밋으로 보존한다. push·PR·병합과 제품 구현은 수행하지 않는다.
- 자체 검수: 합의한 네 Task의 경계·완료 조건·선후 관계와 기술/테스트/hook/품질 인계를 대조했다. Task 003에서 오류 응답의 내부정보 비노출과 서버 로그 진단을 구별하고 통제된 예제로 과거 이미지 경로 보존을 확인하도록 보완했다. 실제 설치·실행 검증은 해당 Task에서 수행한다.
- 별도 검수 결과: HEAD `255cb0c` 대비 실제 제출 후보 7개 파일을 읽기 전용 에이전트가 검수했다. 기술 구성·DB·테스트/TDD·hook·품질 기준과 로그/프로필/JPA/이미지·Task 003/005 인계를 대조해 필수 결함을 발견하지 못했다. 인덱스/작업 파일 일치·로컬 참조/표식 92개·staged 공백 검사도 확인했다. GitHub 실제 조회는 주 진행자의 근거를 사용했으며 실제 설치·DB·hook·CI 실행은 문서 검수 범위 밖이다. 검수 결과 요약 추가 뒤 정확성과 최종 후보 일치를 자체 확인한다.
- 전환 계획: 준비 결과를 Issue 브랜치에서 커밋·검증한 뒤 그 commit을 직접 부모로 `task/42-001-project-bootstrap`을 분기한다. 부모 Issue·다른 Task는 종료하지 않는다. Task 001은 구현 미착수의 예정 상태를 유지하고 첫 행동은 실제 도구·기존 설정 확인과 생성/실행 명령 구체화다.
- 복귀/관련 갱신: Task 결과는 해당 Task에서 기록하고 이후 부모 Issue로 통합할 때 필요한 최신 부모·수용 조건을 확인한다. 이번 검수 보완과 부모 요약은 허용된 GitHub 게시 범위에 맞춰 갱신하며 아직 원격에 없는 원본은 로컬 경로로 표시한다.
