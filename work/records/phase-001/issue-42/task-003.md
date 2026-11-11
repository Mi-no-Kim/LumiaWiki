# Task 42-003 — 공통 웹·API·이미지 제공 골격

<a id="summary"></a>
## 현재 요약

- 제목: 공통 웹·API·이미지 제공 골격
- GitHub sub-issue: [Mi-no-Kim/LumiaWiki #52](https://github.com/Mi-no-Kim/LumiaWiki/issues/52)
- 부모 Issue: [Issue #42](<issue.md#summary>)
- 상태: 예정
- 현재 진행 위치: 공통 연결 계약·버전·확인 화면·오류/이미지 처리 세부 사항을 확정했다. 구현과 브라우저 검증은 미수행이다.
- 다음 행동: Task 002의 필수 검증 후 아래 계약으로 확인 화면을 먼저 마련하고 공통 동작을 구현한다.

<a id="goal"></a>
## 목적과 허용 범위 및 완료 조건

[API·프런트 기준](<../../../../docs/details/development/기술 구성.md#api-common>)과 [공통 서버·이미지 기준](<../../../../docs/개발 기준.md#jpa-query-boundary>)에 따라 후속 검색·상세가 재사용할 기술 골격을 만든다.

- Router Data Mode·ScrollRestoration, TanStack Query·공통 fetch/DTO/ProblemDetail 처리, CSS Modules·CSS 변수의 연결을 마련한다. Router loader와 중복 조회 계층을 만들지 않는다.
- 상대 `/api/v1` 호출과 Vite `/api` 개발 프록시를 연결한다. 전면 CORS 허용을 추가하지 않는다. 서버는 엔티티 직접 반환 대신 DTO·서비스 트랜잭션/조회 경계와 OSIV 비활성을 따른다.
- MVC ProblemDetail·공통 예외 처리를 연결하고 200/400/404/500, 입력 오류 필드·내부정보 비노출과 적절한 서버 로그를 확인한다. 로그/문서 설정은 공통/local/test로 구분한다.
- SpringDoc 3.2.0·Swagger UI의 로컬 확인과 `frontend/public/images/` 상대 경로 조합·이미지 미등록/실패 대체 표시를 마련한다. 통제한 예제만 사용하며 실제 게임 이미지를 확보하지 않는다. 예제 이미지 교체 시 새 파일명/경로를 사용하고 기존 경로도 계속 제공되는지 확인한다.

완료 조건은 웹→프록시→API의 실제 왕복, 이동/뒤로 가기·로딩/빈 상태/오류·이미지 상태의 브라우저 확인과 필요한 내부 테스트, 오류 응답에 SQL·내부 예외 비노출, 응답과 로그에 비밀값 비노출 및 서버 로그의 진단 정보 확인, API 문서 접근 및 후속 사용 계약/설정 안내다. 제품별 검색/상세/루트·실제 DB 테이블·자료 등록은 제외한다. 검색 복귀/스크롤 완성은 Issue #44가 검증한다.

<a id="plan"></a>
## 계획과 예정 검증

1. Task 001·002 결과를 확인하고 아래 Router/Query 버전을 설치·잠금해 타입/빌드 호환성을 검증한다.
2. 동작 구현 전에 기술 연결 확인용 최소 화면을 마련해 입력/출력·상태를 검토한다. Issue #15의 [화면 설계 인계](<../issue-15/task-002.md#design-handoff>)를 참조하되 제품 공통 시각 디자인은 Issue #44의 담당으로 둔다. 검증 전용 응답/실패 사례를 실제 제품 API로 노출하지 않는다.
3. 공통 연결의 동작을 Red→최소 구현→Green으로 개발하고 HTTP·컴포넌트 자동 검사와 아래 브라우저 조작을 함께 수행한다.

### 구현 전 공유할 사용자 확인 목록

| 준비·조작 | 기대 결과·내부 확인 |
|---|---|
| 로컬 웹의 확인 화면에서 화면 이동·뒤로 이동 | 이동과 Router 복원 골격 작동. 제품 목록 복귀의 완성으로 판정하지 않음 |
| 통제된 정상/지연/빈 응답 조회 | 상대 API 호출·로딩·완료·빈 상태가 구분됨. DTO·Query 상태 대조 |
| 잘못된 입력·없는 대상·통제한 서버 실패 | 400/404/500 ProblemDetail과 안전한 안내. 서버 로그와 응답 대조 |
| 예제 상대 이미지·누락 이미지 표시, 로컬 API 문서 접속 | 경로 조합·대체 표시·교체 전후 경로 동시 제공·문서 확인. 실제 게임 자료 사용 없음 |

실제 진입 주소·화면과 요청 계약은 구현 전에 공유한다. AI 자동/직접 조작·사용자 결과를 분리해 기록하며 현재는 모두 미수행이다. 커밋 전 [자체·별도 검수](<../../../../.agents/skills/review-work/SKILL.md#before-commit>)를 수행한다.

<a id="implementation-decisions"></a>
## 확정한 구현 세부 사항 — 2026-11-12

이 구역은 #42의 실행 준비에서 정한 설계다. 제품 범위·시각 디자인을 추가하지 않았고, 결정 당시 설치·구현·커밋은 수행하지 않았다.

### 웹·확인 화면

- `react-router-dom` **7.18.5**, `@tanstack/react-query` **5.107.1**을 정확히 고정한다. Node 기준은 **24.22.3**이다. Task 001의 React·Vite·TypeScript는 유지하며 실제 설치/typecheck/build는 구현 때 검증한다.
- `createBrowserRouter`의 공통 레이아웃 아래 `ScrollRestoration`·오류 경계를 두고 QueryClientProvider는 앱에 한 번 연결한다. HTTP 호출/오류 변환은 공통 fetch 모듈, 화면 상태는 Query, 임시 입력은 React 상태로 나눈다. loader에서 같은 조회를 반복하지 않는다.
- 로컬 진입점은 `http://localhost:5173/__dev/foundation`이다. `import.meta.env.DEV` 분기 안의 lazy import로 확인 화면과 경로를 제품 빌드에서 제외한다. 화면은 두 개의 이동 링크, 정상/지연/빈 응답/오류 선택, 조회 버튼, 결과 영역, 예제/누락 이미지로 구성한다. 상태·입력·출력을 먼저 검토한 뒤 API를 연결한다.
- 공통 fetch는 상대 `/api/v1`만 호출하며 JSON 성공과 ProblemDetail 오류를 구분한다. AbortSignal·10초 제한을 지원하고 취소·통신 실패·시간 초과는 HTTP 업무 오류와 구별한다. Vite `/api` 프록시는 `http://127.0.0.1:8080`으로 접두사를 유지해 전달한다.
- 초기 Query 기본값은 retry 0, staleTime 0, gcTime 5분, focus/reconnect 자동 재조회 false다. queryKey에 조회 입력을 포함하고 Query의 signal을 fetch로 전달한다. 검색/상세별 캐시 정책은 해당 기능에서 명시하며 계산은 기존 버튼 실행 기준을 유지한다.

### API·오류·로그

| 항목 | 확정 계약 |
|---|---|
| 확인 API | local/test 프로필 전용 `GET /api/v1/_dev/foundation?scenario=...`. `ok`, `slow`(1초 지연), `empty`, `bad-input`, `missing`, `failure` 지원. 미지정은 ok, 알 수 없는 값은 400 |
| 성공 DTO | `{ "items": [{ "id": "sample-a", "label": "연결 확인" }] }`, 빈 상태는 items 빈 배열. 제품 DB 조회·도메인 엔티티·실제 게임 자료를 사용하지 않음 |
| 오류 상태 | bad-input 400, missing 404, failure 500. ProblemDetail 기본 필드와 `code`, `requestId`, 입력 오류 때 `fieldErrors: [{ field, code, message }]` 확장. rejectedValue·SQL·내부 예외를 응답에 넣지 않음 |
| 공통 코드 | `API_INPUT_INVALID`, `API_RESOURCE_NOT_FOUND`, `API_INTERNAL_ERROR`. DTO 검증·요청 파싱 실패도 안전한 400으로 변환. 기능별 업무 코드는 후속 API 담당이 추가 |
| 요청 식별 | 서버가 UUID를 만들고 `X-Request-ID` 응답 헤더·오류 본문·MDC 로그에 동일하게 사용. 사용자 제공 헤더는 그대로 신뢰/로그하지 않음. finally에서 MDC 정리 |
| 로그 | 정상 요청마다 INFO 로그를 추가하지 않음. 예상 4xx는 안전한 요약, 예상 못한 500은 requestId와 진단 stack trace를 ERROR에 기록. 요청 본문/비밀값·SQL 값·불필요한 개발 DEBUG 출력 제외 |
| API 문서 | 공통 설정에서 비활성, local/test에서 SpringDoc·Swagger UI 활성. 로컬 `http://127.0.0.1:8080/swagger-ui/index.html` 확인. 실제 배포의 문서 공개 범위는 후속 운영 담당 |

### 이미지·검증·후속 경계

- 기본 이미지 루트는 Vite `BASE_URL` 아래 `images/`다. 파일 상대 경로를 받는 공통 함수를 두고 `..`·절대 URL·잘못된 경로를 거부한다. 아직 외부 이미지 서버·사용자 입력 URL은 지원하지 않는다.
- 합성 `foundation-sample-a.svg`, 교체본 `foundation-sample-b.svg`, 고정 대체 이미지 `placeholder.svg`를 사용한다. null/빈 경로·로딩 실패는 대체 이미지로 표시하며 대체 이미지 실패의 무한 onError 반복을 막는다. a/b 경로 동시 제공과 alt 텍스트를 확인한다.
- 자동 검사는 fetch 정상/ProblemDetail/비JSON 실패/취소·시간 초과, Query 상태 격리·입력 변경, Router 이동, 이미지 대체, MVC 200/400/404/500·내부정보 비노출·문서 프로필을 다룬다. 브라우저 확인은 위 사용자 목록과 실제 프록시 왕복을 사용한다. Chrome 자동 조작은 사용하지 않으며 AI가 직접 확인하지 못하면 그 범위를 밝히고 사용자 확인과 구별한다.
- 운영 API 문서 노출·SPA fallback·권한/로그 보관·백업·S3 전환은 Issue #48이 필요한 적용/운영 담당에 연결한다. 제품 공통 디자인·검색 복귀 완성은 Issue #44다. 이들 후속 결정을 이번 Task의 미정으로 남기거나 로컬 골격으로 운영 완료를 주장하지 않는다.

선택 사항은 위와 같이 정했으며 설치·HTTP/브라우저·테스트 결과는 아직 없다. 근거: [React Router Data Mode](https://reactrouter.com/start/data/installation) · [TanStack Query 기본값](https://tanstack.com/query/latest/docs/framework/react/guides/important-defaults) · [공통 API 기준](<../../../../docs/details/development/기술 구성.md#api-common>). 패치 버전/peer 조건은 2026-11-12 npm registry에서 확인했다.
