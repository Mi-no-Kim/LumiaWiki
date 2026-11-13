# 구조 마이그레이션

<a id="current"></a>

제품 DB 구조 SQL의 원천은 이 폴더 한 곳이다. N5에 따라 새 빈 격리 환경의 최초 파일은 V1__create_common_model.sql로 두며 제약 이름을 명시한다. 현재 제품 마이그레이션 SQL은 0개이고 실제 자료·DB 작업과 구현 파일 생성은 보류한다.

<a id="precreation-confirmation"></a>

## 생성 직전 전체 구조 확인

#43의 신규 테이블을 실제 생성하기 직전에 사용자에게 그때 생성할 전체 구조를 다시 제시하고 확인받는다. 실제 의도와 달라진 부분이 없는지 확인하기 위한 사용자 지정 조건이다. 설계 방향의 선택·이전 문서 검토를 이 최종 확인으로 대체하지 않는다.

- 확인 대상: 전체 표/필드·자료형·NULL/기본값·PK/FK/개수·UNIQUE/CHECK/인덱스·trigger·업무 권한·생성/실패 범위. 현재 후보는 [공통 표](../model/table-layout.md#current)·[지역 구조](../model/region-layout.md#current)·[갱신](../model/writes-and-checks.md#current)·[권한/설치](../model/permissions-and-installation.md#current)로 나눠 읽는다.
- 적용 경계: 새 DDL 실행·Flyway가 새 표를 적용할 서버 시작·해당 표의 격리 DB 통합 검증 전에 확인한다. 실제 스키마 생성과 기존 DB/자료 작업의 보류도 유지한다.
- 승인 대상의 문서/DDL 내용 지문과 실행 환경을 담당 기록에 연결한다. 사용자가 본 뒤 구조가 바뀌면 영향을 받은 표/관계를 다시 확인받는다. 지금은 생성 승인을 받은 상태가 아니다.

## 적용 경로

- Gradle이 이 폴더의 SQL을 JAR의 `db/migration/`에 포함한다. backend 리소스에 수동 사본을 만들지 않는다.
- Spring 시작 시 Flyway가 `classpath:db/migration`을 읽고 `lumia_migrator`로 적용한다. 서비스/JPA는 `lumia_app`으로 접속하고 JPA는 구조를 검증한다.
- 역할·최초 DB/스키마 권한은 [bootstrap](../bootstrap/README.md#current)의 담당이다. 구조·보호 장치와 해당 업무의 표/열 권한은 마이그레이션에서 관리한다. bootstrap 역할 생성 SQL을 복사하지 않는다.

## 작성 전에 정할 것

공통 8개 표의 필드·관계·제약·권한과 N1~N5는 확정 계약이다. 실제 제약별 이름과 정확한 실행 환경을 초안에서 제시한다. 새 빈 환경의 V1 이름을 기존 DB의 순번으로 자동 적용하지 않는다. 공통 PK 보호 함수는 첫 trigger보다 먼저 생성하고 최초 함수/회수와 각 표/자기 trigger는 합의한 원자 설치 단위를 유지한다. 충돌을 자동 교체·삭제·무시하지 않는다.

합성 SQL은 격리 테스트 리소스나 검증 복제본에만 둔다. 제품 원천에 테스트 표·게임 자료를 넣지 않는다. 검증은 [기존 격리 실행 근거](../../work/records/phase-001/issue-43/artifacts/task-001-bootstrap-verification.md#results)를 활용하고, 실제 변경에 맞는 저장/조회·참조·실패 동작을 추가 확인한다.

필드/관계의 현재 상태는 [공통 표](../model/common-tables.md#current), 구현·검증 계획과 미정은 [Task 43-001](../../work/records/phase-001/issue-43/task-001.md#summary)을 따른다. 기존 개발 DB의 조회·이관·적용과 실제 자료 등록은 계속 보류한다.
