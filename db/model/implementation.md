# 공통 도메인 구현과 확인 경로

<a id="current"></a>

합의한 8개 표의 DDL·Java 매핑·저장/조회 코드를 구현했다. 단위 검사와 새 격리 DB의 DDL/JPA·권한·잠금·업무/설치 롤백 검증을 통과하고 승인한 로컬에 적용했다. 정확한 대상과 검증 한계는 [적용 결과](../migration/application-status.md#current)를 따른다. 실제 자료 작업은 계속 보류한다.

## 코드와 DDL의 담당

| 담당                                                           | 원천                                                                                                                                                                                                                  |
| -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 8개 표·PK/FK/UNIQUE/CHECK/NOT NULL 이름·함수/trigger·업무 권한 | [V1 DDL](../migration/V1__create_common_model.sql)                                                                                                                                                                    |
| 8개 JPA 엔티티와 공통 ID                                       | [catalog 패키지](../../backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogRow.java)                                                                                                                     |
| 등록/수정·입력 검사·트랜잭션·영향 검사 호출                    | [CommonCatalogService](../../backend/src/main/java/io/github/minokim/lumiawiki/catalog/CommonCatalogService.java)                                                                                                     |
| EntityManager 저장/조회·명시적 잠금·지도 조회 SQL              | [CommonCatalogStore](../../backend/src/main/java/io/github/minokim/lumiawiki/catalog/CommonCatalogStore.java)                                                                                                         |
| 공개 지도 조회 결과와 후속 검사 연결점                         | [CatalogViews](../../backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogViews.java)·[CatalogReferenceCheck](../../backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogReferenceCheck.java) |
| 알려진 업무 제약/SQLSTATE의 입력 오류 변환                     | [CatalogErrors](../../backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogErrors.java)                                                                                                                   |

DDL을 실제 표 상태로 해석하지 않는다. SQL 원천은 db/migration 한 곳이며 Java에서 스키마를 생성하지 않는다. 새 파일은 Flyway 대상에 포함되므로 **생성 승인 전에 서버·bootRun·integrationTest·DB 검증 도구를 실행하지 않는다.** bootJar/단위 테스트는 서버를 시작하지 않는다.

## 서비스 사용 범위

| 기능           | 메서드·의미                                                                                              |
| -------------- | -------------------------------------------------------------------------------------------------------- |
| 시즌·패치      | create/updateSeason, create/updatePatch. 정렬 저장/재계산·번호 0~99·날짜 검사·시각 절삭                  |
| 종류           | create/updateCategory. 부모 NULL은 확인된 루트 입력이며 잠금 후 최신 부모 경로 순환 검사                 |
| 작업용 지역    | createRegion/renameRegion. 표시 이름만 수정하며 지도 이력과 연결하지 않음                                |
| 등급·무기 종류 | create/updateGrade, create/updateWeaponType. 지정 관리자 판단·기본 검사와 필수 종류 연결                 |
| 지도 구성      | saveMap. mapId NULL이면 전체 새 구성, 지정 ID면 그 구성 교정. NULL 목록은 오류, 빈 목록은 확인된 빈 지도 |
| 조회           | get/list는 내부 공통 자료 조회. readMap은 지정 패치의 유효 구성과 소속 행을 한 SQL에서 선택              |

readMap은 없는 조회 패치를 404에 연결하고, 패치는 있지만 앞선 지도가 없으면 known=false, 소속 0개인 구성이 있으면 known=true/빈 목록을 반환한다. 공개 지도 이름은 소속 행만 읽고 Region.displayName은 결과에 포함하지 않는다. 새 HTTP API·관리 화면은 만들지 않았다. 내부 엔티티를 그대로 공개 응답에 직렬화하지 않는다.

쓰기 서비스는 READ COMMITTED를 요청하고 업무 실패를 전파한다. 외부 트랜잭션에서 호출할 때도 같은 격리·최초 DML 전 필요한 잠금/고정 순서를 따라야 한다. 기본 시간 제한/격리를 일괄 강화하거나 자동 재시도를 추가하지 않는다.

## 후속 참조와 현재 한계

현재 모델은 공통 8개 표뿐이며 획득 본행·아이템 버전/캐시를 저장하지 않는다. 003/004는 후속 자료를 저장하기 전에 CatalogReferenceCheck 구현을 Spring bean으로 등록하고 소속/유효 구간의 영향 검사를 연결해야 한다. 검사는 관련 기준 잠금 아래 공통 변경 flush 뒤 같은 트랜잭션에서 실행되며 실패를 삼키지 않는다. 이 연결점만으로 후속 참조 검증을 완료했다고 판단하지 않는다.

기존 foundation/probe 통합 테스트는 별도의 fixture 설정·합성 migration·빈 entity 패키지를 사용한다. 최초 구동 검증 도구의 사본은 catalog 소스를 제외해 기존 접속/역할 검증과 도메인 생성을 구별한다. 기존 구동 검사와 공통 모델 검사는 각자의 migration/설정으로 구별한다.

## 확인 명령과 범위

JDK 21과 Docker를 준비한다. 기본 test는 integration 태그를 제외하므로 DB 없는 서비스/저장소 검사다. integrationTest는 매 실행 새 격리 PostgreSQL을 사용하고 개인 .env/로컬 DB 접속값을 읽지 않는다.

```powershell
$env:JAVA_HOME='C:\Program Files\Java\jdk-21.0.11'
.\backend\gradlew.bat -p backend test --offline
.\backend\gradlew.bat -p backend integrationTest --tests io.github.minokim.lumiawiki.catalog.CommonCatalogIntegrationTests --offline
```

공통 모델 통합 검사는 실제 제품 SQL/Flyway를 migrator로 설치하고 app 계정 JPA validate 뒤 저장/조회·권한·실패 동작을 검사한다. 강제 설치 실패는 별도 격리 DB와 임시 테스트 SQL에만 넣는다. 로컬에는 검증 자료를 저장하지 않는다.

단위 검사의 가짜 트랜잭션과 실제 DB 롤백의 근거를 구별한다. 로컬 적용 시에는 같은 SQL을 포함한 실행 JAR로 Flyway 적용/JPA validate를 확인하고 읽기 전용 메타정보로 구조·소유·권한·빈 상태를 대조했다. 계획·실행 근거와 수용은 [Task 43-001](../../work/records/phase-001/issue-43/task-001.md#summary)·[생성 기록](../../work/records/phase-001/issue-43/artifacts/task-001-creation.md#verification)이 관리한다.
