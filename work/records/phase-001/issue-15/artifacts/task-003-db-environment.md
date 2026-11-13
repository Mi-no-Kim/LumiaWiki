# Task 003 — DB·실행 환경·SQL 배치

담당 기록: [Task 003](../task-003.md#summary). 이 문서는 해당 주제의 상세 기록이며 Task 상태·남은 결정·전체 인계는 담당 기록에서 관리한다.

<a id="current"></a>

## PostgreSQL 이미지·Docker Compose 사용 확정

신규 환경의 초기 기준으로 PostgreSQL 18.6을 제안했고 사용자가 공식 이미지 `postgres:18.6` 사용을 확정했다. 2026-11-11 공식 배포 목록과 릴리스 노트에서 18.6을 확인했고, Flyway PostgreSQL 문서는 검증 버전에 18을 명시한다. 후자는 PostgreSQL 18 계열에 대한 도구 문서 확인이며 이 저장소의 정확한 Boot 관리 드라이버·Flyway 조합을 설치·실행해 검증한 결과는 아니다. 실제 접속·마이그레이션 호환성은 후속 기반 구축에서 확인한다.

사용자는 PostgreSQL을 새로 구성하고 `postgres:18.6` 이미지와 Docker Compose를 사용하기로 했다. DB 설치·실제 접속은 하지 않았다. 저장·접속값·로컬/테스트 환경은 아래 실행 구성과 공통 설정 논의에서 정한다.

- [PostgreSQL 공식 릴리스 목록](https://www.postgresql.org/) · [PostgreSQL 18.6 릴리스 노트](https://www.postgresql.org/docs/release/18.6/) · [Flyway PostgreSQL 지원](https://documentation.red-gate.com/flyway/reference/database-driver-reference/postgresql-database)

## 배치·SQL·환경변수 합의

사용자는 backend·frontend·db 배치, 공용 SQL을 서버 빌드 리소스에 포함해 Spring Boot Flyway로 실행하는 방식과 DB 보존·접속·환경변수 기준을 확정했다. 현재 규칙 전문은 [DB 환경 기준](<../../../../../docs/details/development/DB 환경.md#layout>)으로 옮겼다. SQL의 단일 원천과 Python 등 자료 처리 가능성을 유지하며 실제 설정은 첫 기반 구축에서 수행한다.

<a id="db-config"></a>

### DB 보존·접속·환경변수 기준

[실제 DB 기준](<../../../../../docs/details/development/DB 환경.md#db-config>)을 따른다. 이미지·볼륨·계정·환경변수의 설정이나 실제 DB 실행은 아직 하지 않았다.

<a id="server-runtime-proposal"></a>

## 서버 공통 실행 설정 확정

사용자는 최소 로그·`open-in-view=false`·환경별 설정 분리·오류 처리 연결을 확정했다. 설정 파일·실행 환경은 아직 만들지 않았다. 앱 이름 `lumiawiki-api`와 로컬 서버 `127.0.0.1:8080`, DB 환경변수·Flyway·`ddl-auto=validate`·SQL 자동 초기화 `never`는 앞선 합의를 유지한다.

| 항목           | 상태 | 기준                                                                                                                                              |
| -------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| JPA 조회 범위  | 확정 | [개발 기준의 JPA 조회·응답 범위](<../../../../../docs/개발 기준.md#jpa-query-boundary>)에 따라 `spring.jpa.open-in-view=false` 사용               |
| 환경별 설정    | 확정 | [개발 기준의 서버 환경별 설정](<../../../../../docs/개발 기준.md#server-profiles>)에 따라 공통·로컬·테스트를 분리하고 프로필을 명시               |
| 오류 처리 연결 | 확정 | [개발 기준의 API 오류 처리](<../../../../../docs/개발 기준.md#error-handling>)에 따라 기본 MVC 오류와 공통 예외 처리를 연결                       |
| 로그           | 확정 | [애플리케이션 개발 기준의 최소 로그](<../../../../../docs/개발 기준.md#logging>)를 원천으로 사용. 별도 수집·보관 시스템은 배포·운영 설계에서 결정 |

확정한 서버 기준의 실제 기본 로그·프로필·트랜잭션/DTO·오류 응답 설정과 동작은 첫 기반 구축 및 해당 서버 기능 과제에서 검증한다. 기준 채택을 실제 구현·실행 검증 완료로 확대하지 않는다. 오류 처리의 기준·설정 표·요약·인계를 대조하고 관련 6개 문서의 로컬 참조 83개·공백을 자체 확인했다. 실제 오류 응답 실행 검증은 아직 수행하지 않았다.

근거: [Spring Boot 프로필](https://docs.spring.io/spring-boot/reference/features/profiles.html) · [공통 설정 속성](https://docs.spring.io/spring-boot/appendix/application-properties/index.html) · [Spring ProblemDetail](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-ann-rest-exceptions.html).

<a id="environment-proposal"></a>

### 환경별 설정 분리 확정

사용자가 추천안대로 확정했으며 원천은 [실제 개발 기준](<../../../../../docs/개발 기준.md#server-profiles>)이다. 이 기록에서 설정 규칙 전문을 중복 관리하지 않는다. 실제 YAML·프로필 활성화·환경변수·테스트 연결 설정과 실행 검증은 아직 수행하지 않았으며 첫 기반 구축 과제에 배정한다.

<a id="common-identity-proposal"></a>

## 공통 내부 식별값 확정

사용자가 내부 ID의 DB `BIGINT`·IDENTITY 발급, Java `Long`, API·프런트 문자열 표현을 추천안대로 확정했다. 원천은 [실제 개발 기준](<../../../../../docs/details/development/공통 DB 모델.md#internal-identifiers>)이며 기존 [제품 식별 요구](<../../../../../docs/details/product/게임 데이터 변경 관리.md#identity-information>)도 이 기준으로 연결했다. 구체 테이블·키·참조 일치 검사는 기존 인계대로 DB 설계에서 정한다. 실제 스키마·데이터 등록·ID 발급·API 실행은 아직 수행하지 않았다. 채택안과 개발·제품 원천·인계를 자체 대조하고 관련 6개 문서의 로컬 참조 99개·공백을 확인했다.

<a id="datetime-proposal"></a>

## 날짜·시각·미확인 값 확정

사용자는 서비스 데이터 시각의 정밀도를 밀리초 대신 초로 정하고 나머지 추천안을 확인했다. 원천은 [실제 개발 기준](<../../../../../docs/개발 기준.md#datetime>)이다. PostgreSQL `timestamptz(0)`·Java `Instant`·초 단위 UTC 저장/비교/API, 날짜 전용 값의 `DATE`/`LocalDate`, 기본 한국 시간 표시와 미확인 값 처리를 따른다. 실제 자료 확인·변환·등록·날짜/시각 코드 실행은 아직 하지 않았다. 채택안·제품/개발 원천·인계를 자체 대조하고 관련 6개 문서의 참조 104개·공백과 밀리초 추천값이 남지 않았음을 확인했다.

<a id="skill-json-proposal"></a>

## 스킬 연결별 JSON 저장·최소 검증 확정

사용자는 추천안대로 확정했다. 원천은 [실제 개발 기준](<../../../../../docs/개발 기준.md#skill-json>)이며 [제품의 스킬 연결·버전 역할](<../../../../../docs/details/product/게임 데이터 변경 관리.md#item-skills>)도 이 기준에 연결했다. 실제 JSON 입력·스키마·JPA/API 매핑이나 저장/읽기 검증은 아직 수행하지 않았다. 수식에 관한 구체 논의·구현은 기존대로 딜량 계산기 작업까지 보류한다. 채택안·개발/제품 원천·인계를 자체 대조하고 관련 문서 참조 108개·공백을 확인했다.

<a id="stat-numeric-proposal"></a>

## 능력치 값 NUMERIC·BigDecimal 확정

사용자는 능력치 값에 NUMERIC과 BigDecimal을 사용하는 것으로 확정했다. 원천은 [실제 개발 기준](<../../../../../docs/개발 기준.md#stat-numeric>)이며 [제품 능력치 요구](<../../../../../docs/details/product/아이템 탐색과 상세.md#stat-information>)도 이 기준에 연결했다. 실제 값·허용 범위·소수 자릿수와 API/화면의 구체 표현은 자료 확인 뒤 담당 데이터/DB/API 설계에서 스키마·검증 구현 전에 정한다. 수식·딜량 계산의 세부 규칙은 기존대로 후속 범위다. 실제 능력치 저장·매핑·합산·전달 실행은 아직 수행하지 않았다. 채택안·개발/제품 원천·인계를 자체 대조하고 관련 6개 문서의 참조 113개·공백을 확인했다.

<a id="image-storage-proposal"></a>

## 이미지 보관 공통 방식 확정·S3 후속 검토

사용자는 우선 DB의 상대 경로와 프런트 public 정적 파일 방식으로 진행하기로 했다. 원천은 [실제 개발 기준](<../../../../../docs/개발 기준.md#images>)이고 [제품의 이미지 정보](<../../../../../docs/details/product/아이템 탐색과 상세.md#item-information>)도 연결했다. 파일 변경 시 재빌드·배포와 과거 참조 파일 보존을 전제로 한다.

사용자가 질문한 S3는 [후속 저장소 검토 후보](<../../../../../docs/개발 기준.md#image-storage-followup>)로 남긴다. 전환·CloudFront·시점은 아직 확정하지 않았다. Task 005가 배정할 이미지 제공/배포 설계에서 파일 규모·이미지 업데이트/재배포 부담 또는 공개 배포 환경 결정 시 비용·접근·캐시·이관을 검토한다. 이 검토를 현재 P1의 필수 S3 구현으로 확대하지 않는다.

실제 이미지 확보·다운로드·변환·등록, 프런트 정적 파일 배치, AWS 리소스 생성은 수행하지 않았다. 자료 처리 보류도 유지한다. 현재 정적 방식 채택과 S3 검토 후보의 구분·원천/인계·자료 보존을 자체 대조하고 관련 6개 문서의 로컬 참조 118개·공백을 확인했다. 파일 제공·이관·AWS 동작 검증은 아직 수행하지 않았다.
