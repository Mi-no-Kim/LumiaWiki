# Task 003 — 기술 선택·버전·생성 옵션

담당 기록: [Task 003](<../task-003.md#summary>). 이 문서는 선택 이유·당시 확인·대안을 보존한다. 현재 규칙의 원천은 [기술 구성 기준](<../../../../../docs/details/development/기술 구성.md#current>)이며 Task 상태·인계는 담당 기록에서 관리한다.

<a id="current"></a>

<a id="inherited-requirements"></a>
## 합의·인계에서 확인한 기술 선택 입력

| 입력 | 이번 선택에 반영할 조건 |
|---|---|
| 검색·상세·루트와 공통 디자인 | 검색 자동 갱신·접는 필터·미리보기, 전체 재귀 트리, 화면 안 장비 선택·명시적 루트 계산을 지원한다. 공통 UI를 재사용하고 구현 전에 기능 화면 디자인을 검토한다. |
| 상태·탐색 | 검색어·필터·스크롤 복귀, 상세 간 탐색, 루트 입력 변경 후 이전 조건 결과 표시와 계산 상태를 다룬다. 현재 저장·요청 처리 방식은 실제 개발 기준을 따르고 기능별 세부 정책은 담당 설계에서 정한다. |
| 데이터·버전 | 아이템 단위 이력·유효 버전 선택, 원본 능력치와 표시 캐시, 스킬 대상/특정 버전 참조·연결별 JSON·텍스트를 지원한다. SQL 전체 채택을 전제로 삼지 않고 DB 선택은 후속 논의에서 확정했다. |
| P1 경계 | 상세는 v1.0.0만 표시하고 버전 선택기는 후속이다. 루트는 직접 지정·지역 집합/배달 범위다. 수식은 딜량 계산기 작업 전까지 논의하지 않는다. |
| 실제 작업·운영 | 이 Task는 선택·공통 기준의 결정이며 설치·연결·스키마 생성은 후속이다. 자료 조사·확보·처리는 사용자 보류를 유지한다. 기술 선호는 아래와 같이 확인했으며 구체 호스팅·운영 규모는 미정이다. |

논의는 언어와 앱/서버 구성 → DB → 실행 버전·패키지/빌드/테스트·코드 검사 → 환경변수·DB 접속/변경 관리 → 공통 식별·버전 보존·의존 관계 순으로 진행한다. 선택할 때 공식 문서의 지원·호환성을 확인하며, 기능별 DB/API/알고리즘 상세는 Task 005의 담당 기능 설계로 넘긴다.

## 기술 선호와 합의한 기본 구성

사용자는 익숙한 기술을 우선하고 Java·Spring, React, PostgreSQL을 제시했다. 이후 React 화면과 Java/Spring Boot API 서버의 역할을 나누고 PostgreSQL을 사용하는 아래 기본 구성에 동의했다. 앞서 제안한 Next.js 중심 구성은 채택하지 않는다. 버전·도구는 아래 확정 내용을 따르고 구체 배포 방식은 별도 결정한다.

현재 기준은 [실제 개발 기준의 기본 기술 구성](<../../../../../docs/details/development/기술 구성.md#stack>)에서 관리한다. 이 기록은 선택 이유·당시 확인 근거를 보존한다.

공식 문서에서 Spring Boot의 Spring MVC 자동 구성·JSON 응답 처리, React의 빌드·라우팅 도구 선택 경계, PostgreSQL의 JSON 저장 지원을 확인했다. 익숙함과 기존 요구를 고려한 구성 선택이며 실제 설치·실행 확인은 아니다.

- [Spring Boot 웹 구성](https://docs.spring.io/spring-boot/reference/web/servlet.html) · [React 앱 구성](https://react.dev/learn/build-a-react-app-from-scratch) · [PostgreSQL JSON](https://www.postgresql.org/docs/current/datatype-json.html)

## 프런트 언어 선택

사용자는 React를 TypeScript로 작성하고 버전은 7.0.2를 사용하기로 확정했다. 아이템·검색 조건·계산 결과와 UI 상태의 코드상 구조를 명시하고 잘못된 필드 사용을 개발 중 확인하기 위한 선택이다. 타입 작성·유지 비용은 있으며 실제 API 응답의 실행 시 검증을 대신하지 않는다. 검사 설정은 후속 논의에서 정한다.

- [React의 TypeScript 사용](https://react.dev/learn/typescript)

## 프런트 개발·빌드 도구 선택

사용자는 Vite를 개발·빌드 도구로 채택하고 버전은 8.3.7로 확정했다. React + TypeScript 기본 템플릿, 개발 서버와 배포용 빌드 기능을 공식 문서에서 확인했다. 화면 개발·빌드는 Vite, API·조회·계산은 합의한 Spring Boot 서버가 담당한다. Node.js·npm 기준은 아래에서 확정했다. 실제 설치는 후속 기반 구축 때 수행한다. 렌더링·라우팅·배포 방식은 Vite 채택만으로 확정하지 않는다.

- [Vite 시작 안내](https://vite.dev/guide/)

## 프런트 패키지 관리·설치 기준

사용자는 npm 사용과 `package-lock.json` 커밋을 확정했다. 의존성을 의도적으로 추가·변경할 때는 `npm install`로 잠금 파일을 함께 갱신·검토하고, 깨끗한 환경·CI에서 기존 구성을 설치할 때는 `npm ci`를 사용한다. npm 공식 문서에서 잠금 파일 요구·불일치 시 실패·설치 중 잠금 파일을 수정하지 않는 동작을 확인했다. npm 자체는 잠금 파일과 호환되는 버전을 사용하고 정확한 버전을 강제하지 않는다. 현재 로컬 11.19.1로 시작하며 실제 설치·빌드는 후속 기반 구축에서 확인한다. 잠금 파일만으로 OS·런타임 차이까지 모두 재현된다고 판정하지 않는다.

- [npm ci 공식 문서](https://docs.npmjs.com/cli/v11/commands/npm-ci/)

## 서버 빌드·의존성 관리 선택

사용자는 Gradle과 Gradle Wrapper를 채택하고 이후 버전을 9.9.1로 확정했다. Spring Boot Gradle 플러그인의 실행·패키징·의존성 관리 지원과 Wrapper의 지정 Gradle 버전 실행 기능을 공식 문서에서 확인했다. Wrapper 파일을 저장소에 포함해 개발·CI의 Gradle 실행 버전을 맞춘다. Java·라이브러리 버전까지 Wrapper가 자동 고정하는 것으로 처리하지 않는다. 설정 문법은 아래에서 확정했다. 실제 Wrapper 생성·빌드 실행은 수행하지 않았다.

- [Spring Boot Gradle 플러그인](https://docs.spring.io/spring-boot/gradle-plugin/index.html) · [Gradle Wrapper](https://docs.gradle.org/current/userguide/gradle_wrapper.html)

## Gradle 설정 문법 선택

사용자는 익숙한 Groovy DSL의 `build.gradle`을 선택했다. 서버 구현 언어는 Java로 유지하며 빌드 설정 파일은 Groovy 문법으로 작성한다. 실제 빌드 파일 작성은 후속 기반 구축 때 수행한다.

- [Gradle 설정 문법·파일 확장자 안내](https://docs.gradle.org/current/userguide/kotlin_dsl.html#script_file_names)

## 서버 버전·생성 옵션 확정과 초기 설정 추천

사용자는 Java 21·Spring Boot 4.1.2·Gradle Wrapper 9.9.1과 JPA·Flyway·아래 기본 의존성 8개를 확정했다. 이후 아래 생성 옵션·앱 초기 버전도 확정했다. 앞선 Java 25 제안은 채택하지 않는다. 초기 실행 설정 표는 후속 합의를 반영하며 실제 개발 기준을 함께 따른다.

2026-11-11 확인한 공식 시스템 요구에 따라 Spring Boot 4.1.2를 제안했고 사용자가 채택했다. Java 21이 지원 범위에 포함되고 현재 안정 버전이며, 지정된 구버전 라이브러리 유지 제약이 없는 신규 프로젝트라는 점을 고려했다. Gradle Wrapper는 Boot가 지원하는 9.x 중 9.9.1을 선택했다. JDK는 사용자가 이미 사용하는 21을 유지하며 실제 배포판·패치 정보와 빌드 호환성은 후속 기반 구축에서 확인·기록한다.

현재 기준은 [실제 개발 기준의 서버 생성·실행 설정](<../../../../../docs/details/development/기술 구성.md#initializr>)에서 관리한다. 이 기록은 선택 이유·당시 확인 근거를 보존한다.

- [Spring Boot 시스템 요구](https://docs.spring.io/spring-boot/system-requirements.html) · [Initializr 생성 옵션](https://docs.spring.io/initializr/docs/current/reference/html/) · [DB 접속·JPA 설정](https://docs.spring.io/spring-boot/reference/data/sql.html) · [DB 초기화·Flyway](https://docs.spring.io/spring-boot/how-to/data-initialization.html)

## 기본 의존성 구성 확정

사용자가 아래 기본·테스트 의존성 8개 구성을 확정했다. 좌표·범위는 채택한 Spring Boot 4.1.2를 기준으로 하며 아직 설치하지 않았다. `org.springframework.boot` 그룹의 starter 버전과 Boot가 관리하는 외부 라이브러리 버전은 Boot의 의존성 관리에 맞추고 개별 버전을 중복 지정하지 않는 방식을 추천한다.

현재 기준은 [실제 개발 기준의 기본 의존성](<../../../../../docs/details/development/기술 구성.md#dependencies>)에서 관리한다. 이 기록은 선택 이유·당시 확인 근거를 보존한다.

- [Boot starter 목록·버전 관리](https://docs.spring.io/spring-boot/reference/using/build-systems.html) · [테스트 구성](https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html) · [Flyway PostgreSQL 모듈](https://docs.spring.io/spring-boot/how-to/data-initialization.html)

## Lombok·API 문서화 확정과 Initializr 사전 안내

사용자는 기본 의존성 확정 뒤 Lombok·API 문서화 도구 추천과 Initializr에서 지정할 수 있는 항목의 사전 안내를 요청했다. 앞으로 생성 화면에서 고를 항목과 생성 후 확인·추가할 항목을 함께 제시한다. 2026-11-11 공식 Initializr 메타데이터와 Boot 4.1.2 의존성 매핑을 읽어 아래 선택 이름을 확인했다. 프로젝트·설정 파일은 생성하지 않았다.

현재 기준은 [실제 개발 기준의 Initializr 의존성·개발 편의 도구](<../../../../../docs/details/development/기술 구성.md#dependencies>)에서 관리한다. 이 기록은 선택 이유·당시 확인 근거를 보존한다.

사용자는 Lombok을 앞서 제안한 방식으로 채택했다. 반복되는 생성자·getter·로그 필드 작성을 줄이기 위한 선택이다. Gradle은 `compileOnly`와 `annotationProcessor`를 함께 사용하고 버전은 Boot 관리값에 맞춘다. 테스트 코드에서 어노테이션을 쓰면 테스트용 설정도 확인한다. `@RequiredArgsConstructor`·`@Getter`·`@Slf4j` 등 필요한 기능만 사용하고, 광범위한 메서드를 생성하는 `@Data`를 JPA 엔티티에 일괄 적용하지 않는다.

사용자는 API 문서화를 springdoc-openapi 3.2.0 + Swagger UI로 확정했다. 컨트롤러 기반으로 API 설명을 만들고 브라우저에서 요청·응답을 확인할 수 있어 초기 프런트/API 연결 부담을 줄일 수 있다는 판단이다. 공식 호환표의 Boot 4.1.x 지원 범위인 springdoc 3.1.x~3.2.x 중 3.2.0을 선택했으며 이 라이브러리 버전은 명시한다. 테스트 기반 문서화인 Spring REST Docs도 Initializr 선택지지만 이번에는 문서 유지 비용을 고려해 대안으로만 둔다. 문서의 공개 범위·환경별 노출은 웹·환경 설정 기준에서 별도 결정한다. 이 선택만으로 Boot 버전·나머지 설정까지 일괄 확정한 것으로 보지 않는다.

Project·Language·Boot·Group·Artifact·Name·Description·Package name·Packaging·Java·Configuration의 값은 앞의 생성 옵션 표를 함께 안내한다. 앱 버전 `0.0.1-SNAPSHOT`은 생성물의 기본값으로 확인하며 UI에 별도 입력란이 있다고 단정하지 않는다. 포트·DB 환경변수·JPA 설정·Flyway 경로 등 실행 설정은 생성 후 설정 파일에서 다룬다. Flyway PostgreSQL 모듈과 테스트 의존성은 별도 검색 항목이라고 안내하지 않고 생성된 빌드의 포함 여부·범위를 확인해 빠졌으면 추가한다.

- [Initializr 공식 메타데이터](https://start.spring.io/metadata/client) · [Boot 4.1.2 의존성 매핑](https://start.spring.io/dependencies?bootVersion=4.1.2) · [Lombok Gradle 설정](https://projectlombok.org/setup/gradle) · [Lombok Data 생성 범위](https://projectlombok.org/features/Data) · [springdoc 설정·호환표](https://springdoc.org/)

## 서버 실행·빌드 버전 확정

사용자가 이미 사용하는 JDK 21이 있다고 확인했으므로 이를 유지한다. 별도 JDK 배포판 선정·교체는 현재 결정 항목에서 제외하고 앞선 Temurin 제안은 채택하지 않는다. 사용자는 Spring Boot 4.1.2와 Gradle Wrapper 9.9.1도 확정했다. 2026-11-11 공식 Gradle 호환성 표에서 Java 21 실행·빌드 지원을, Boot 시스템 요구에서 Java 21 및 Gradle 9.x 지원을 확인했다. 실제 빌드는 후속 기반 구축에서 검증한다.

개발·CI의 Gradle 실행은 합의한 Wrapper로 통일하고 Java 빌드 대상은 21로 맞춘다. Initializr의 Java 선택은 21로 두며 Gradle 정확한 버전은 생성 후 Wrapper에서 맞춘다. 이후 사용자의 로컬 버전 조회 요청으로 아래 JDK 정보를 확인했다. JDK 설치·교체는 하지 않았다.

- [Gradle Java 호환성](https://docs.gradle.org/current/userguide/compatibility.html#java_runtime) · [Spring Boot 요구](https://docs.spring.io/spring-boot/system-requirements.html)

<a id="version-policy"></a>
## 로컬 도구의 호환 조건·프로젝트 버전 관리 확정

사용자는 로컬 도구의 정확한 버전을 강제하지 않고 호환 조건으로 관리하는 안을 채택했다. 앞서 확정했던 Node.js 26.13.0 LTS·동봉 npm 11.20.0은 권장 참고값으로 바꾸고 기존 로컬 Node.js 24.13.0·npm 11.19.1로 개발을 시작한다. 현재 Node는 Vite 8.3.7의 Node 요구 범위에 포함되며 실제 패키지 설치·타입 검사·빌드는 후속 기반 구축에서 검증한다. 버전 설치·업데이트는 하지 않았다.

현재 기준은 [실제 개발 기준의 버전 관리 기준](<../../../../../docs/details/development/기술 구성.md#version-policy>)에서 관리한다. 이 기록은 선택 이유·당시 확인 근거를 보존한다.

- [Node.js LTS 다운로드](https://nodejs.org/en/download) · [Node.js 26.13.0 릴리스](https://nodejs.org/en/blog/release/v26.13.0) · [동봉 npm 버전](https://github.com/nodejs/node/blob/v26.13.0/deps/npm/package.json) · [Vite 요구 사항](https://vite.dev/guide/)

## React·Vite·TypeScript 버전 확정

사용자는 React·react-dom 19.3.1, Vite 8.3.7, TypeScript 7.0.2를 초기 버전으로 확정했다. 2026-11-11 공식 npm 배포 메타데이터의 안정 버전 태그를 확인했다. react-dom 19.3.1의 React 요구는 `^19.3.1`이며 Vite 8.3.7의 Node 요구는 `^20.19.0 || >=22.12.0`, TypeScript 7.0.2의 Node 요구는 `>=16.20.0`이다. 현재 로컬 Node 24.13.0과 권장 참고값 26.13.0 모두 범위에 포함된다.

공식 create-vite의 react-ts 템플릿도 React 19.3.1·Vite 8.3 계열·TypeScript 7.0.2를 사용함을 확인했다. 이 템플릿은 비교 근거이며 부속 검사 도구·React Compiler·상태/라우팅 도구까지 채택한 것은 아니다. 실제 의존성 설치·타입 검사·빌드·화면 동작 확인은 후속 기반 구축에서 수행한다. 저장소의 패키지 선언·잠금 파일에 채택한 버전과 실제 설치 버전을 맞춘다.

- [React 버전 안내](https://react.dev/versions) · [React 배포 메타데이터](https://registry.npmjs.org/react/latest) · [react-dom 배포 메타데이터](https://registry.npmjs.org/react-dom/latest) · [Vite 배포 메타데이터](https://registry.npmjs.org/vite/latest) · [TypeScript 배포 메타데이터](https://registry.npmjs.org/typescript/latest) · [공식 React TS 템플릿](https://github.com/vitejs/vite/blob/main/packages/create-vite/template-react-ts/package.json)

<a id="code-quality-proposal"></a>
## 코드 검사·포맷팅 기준

[채택한 도구·실행 시점·TypeScript 병행·문서 및 자동 포맷 기준](<task-003-code-quality.md#current>)에서 관리한다. 실제 설치·명령·hook 연결과 검증은 첫 기반 구축에서 수행한다.

<a id="api-common-proposal"></a>
## API 공통 형식·로컬 연결 확정

사용자는 아래 API 공통 규칙과 로컬 연결 방식을 추천안대로 확정했다. API·프록시·오류 처리 설정은 아직 구현하지 않았다.

현재 기준은 [실제 개발 기준의 API 공통 기준](<../../../../../docs/details/development/기술 구성.md#api-common>)에서 관리한다. 이 기록은 선택 이유·당시 확인 근거를 보존한다.

근거: [Spring 오류 응답·ProblemDetail](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-ann-rest-exceptions.html) · [Vite 개발 서버 프록시](https://vite.dev/config/server-options.html#server-proxy) · [Spring CORS](https://docs.spring.io/spring-framework/reference/web/webmvc-cors.html)

<a id="frontend-common-proposal"></a>
## 프런트 공통 구성 확정

사용자는 아래 프런트 공통 구성을 추천안대로 확정했다. 라이브러리 설치·프로젝트 생성·화면 구현은 아직 하지 않았다.

현재 기준은 [실제 개발 기준의 프런트 공통 기준](<../../../../../docs/details/development/기술 구성.md#frontend-common>)에서 관리한다. 이 기록은 선택 이유·당시 확인 근거를 보존한다.

근거: [React Router 모드·스크롤 지원](https://reactrouter.com/start/modes) · [React 상태 관리](https://react.dev/learn/managing-state) · [TanStack Query 역할](https://tanstack.com/query/latest/docs/framework/react/overview) · [타입 지원·버전 관리](https://tanstack.com/query/latest/docs/framework/react/typescript) · [기본 재조회 정책](https://tanstack.com/query/latest/docs/framework/react/guides/important-defaults) · [Vite CSS Modules](https://vite.dev/guide/features.html#css-modules)
