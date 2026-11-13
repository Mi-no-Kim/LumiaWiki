# 구조 마이그레이션

<a id="current"></a>

제품 DB 구조 SQL의 원천은 이 폴더 한 곳이다. [V1__create_common_model.sql](V1__create_common_model.sql)은 새 격리 DB 검증을 거쳐 승인한 로컬 lumiawiki/public에 적용했다. 실제 환경·DDL 지문·검증 한계는 [적용 결과](application-status.md#current)를 따른다. 실제 게임 자료 작업은 계속 보류한다.

<a id="precreation-confirmation"></a>

## 생성 직전 전체 구조 확인

#43의 신규 테이블을 실제 생성하기 직전에 전체 표/필드·자료형·NULL/기본값·PK/FK/개수·UNIQUE/CHECK/인덱스·trigger·업무 권한·실행 대상/실패 범위를 사용자에게 확인받는다. 설계 방향의 선택만으로 생성하지 않는다.

현재 [8개 표·DDL 지문·실행 순서와 대상](creation-review.md#current)은 사용자 확인을 받았다. 허용 범위는 새 격리 검증 후 해당 로컬 DB의 신규 8개 표 적용이며 실제 자료 작업은 포함하지 않는다. 기존 객체/역할/소유 변경은 별도 승인 범위만 수행한다. 사용자가 본 뒤 구조나 대상이 달라지면 영향을 받은 범위를 다시 제시한다.

## 적용 경로와 실패 범위

- Gradle이 이 폴더의 SQL을 JAR의 db/migration/에 포함한다. backend 리소스에 수동 사본을 만들지 않는다.
- Spring 시작 시 Flyway가 classpath:db/migration을 lumia_migrator로 적용한다. 서비스/JPA는 lumia_app으로 접속하며 Hibernate ddl-auto=validate를 유지한다.
- 함수·8개 표·제약·trigger·업무 GRANT는 V1 한 트랜잭션에 설치한다. plain CREATE의 충돌을 교체·삭제·건너뛰지 않는다. 실패 시 이 설치 단위를 롤백하며 선행 bootstrap·DB/볼륨·Flyway 관리 표는 자동 삭제하지 않는다.
- 적용한 migration 파일은 수정하지 않는다. 후속 구조 변경은 새 migration과 필요한 사용자 구조 확인으로 진행한다.
- 역할·DB/스키마 최초 권한은 [bootstrap](../bootstrap/README.md#current), 제품 객체의 권한은 migration이 소유한다. 기존 환경은 자동 최초 초기화의 대상으로 취급하지 않는다.

## 문서와 검증

필드·관계·업무 의미는 [공통 표](../model/common-tables.md#current), Java 사용법과 DB 없는/격리 검사 명령은 [구현 안내](../model/implementation.md#current), 승인·결과·잔여는 [Task 43-001](../../work/records/phase-001/issue-43/task-001.md#summary)이 소유한다. 합성 검증 입력은 격리 DB/테스트 리소스에만 두며 로컬 제품 표에는 등록하지 않는다.
