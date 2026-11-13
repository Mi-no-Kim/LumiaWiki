# Task 43-001 — 테이블 생성과 적용 결과

<a id="current"></a>

담당은 [Task 43-001](../task-001.md#summary)이다. 사용자에게 [전체 구조·대상·순서](../../../../../db/migration/creation-review.md#current)를 확인받고, 새 격리 DB 검증 뒤 기존 로컬 lumiawiki/public에 8개 표를 추가했다. 실제 게임 자료 작업은 계속 보류한다.

## 승인 범위와 실제 반영

- 승인: 새 격리 PostgreSQL 18.6의 최초 검증, 기존 로컬 DB 메타정보 조회와 충돌 없는 신규 8개 표 생성, 결과 문서 갱신.
- 별도 승인: lumia_app·lumia_migrator LOGIN 역할과 최소 권한/PUBLIC 권한 회수, 빈 flyway_schema_history의 lumia_migrator 소유 이관, 개인 .env의 app/Flyway 값 비공개 사용과 누락/예제 키 보완. 기존 개인 값과 DB/public 소유자는 유지한다.
- 로컬 대상: Docker desktop-linux / lumiawiki-db-1(e85f1d98b2a7), 127.0.0.1:5432 / lumiawiki/public / PostgreSQL 18.6.
- 적용: 실행 JAR의 SQL과 원천 SHA-256 일치를 확인하고 migrator Flyway V1 성공·app Hibernate validate를 확인했다. Flyway checksum은 -995352012이며 DDL SHA-256은 1495d8a5085188f535865f9b46f51aa1c9a18480c1b49efd68df61c43f5b8ddd다.
- 메타정보 대조: 제품 표 8개·명시한 제약 60개·FK 6개·trigger 8개·공용 함수 1개·시퀀스 8개의 구조/소유/권한이 일치한다. DB 소유자 lumiawiki, public 소유자 pg_database_owner는 유지했고 8개 제품 표는 모두 0행이다.
- 실제 자료 조사·변환·등록, 볼륨 삭제/초기화, 승인 범위 밖의 객체/역할/소유 변경은 수행하지 않았다. 기반 체크포인트 49c39d4 대비 구현·테스트·문서와 관련 상태를 같은 제출 단위에 포함한다.

<a id="verification"></a>

## 실행 검증과 근거

- 단위 30건·격리 통합 11건(공통 모델 5·최초 준비 4·기존 앱 2), 실패/오류/누락 0. SpotlessCheck와 실행 JAR 패키징 통과.
- 공통 모델: 실제 DDL/Flyway 설치와 재검증·재적용 없음, JPA 왕복/시각 절삭, 지도 미확인/빈 구성/재사용과 작업용 이름 분리, 순환 거부/업무 오류 매핑, 지도 교정 실패 롤백, app의 정상 DML과 권한/PK/FK 거부, 기준 잠금 충돌/해제와 SELECT 허용을 확인했다.
- 설치 실패: 제품 SQL 뒤 강제 오류를 넣은 별도 격리 DB에서 제품 표·함수·권한 전체 롤백과 빈 Flyway 관리 표 보존을 확인했다. 검증용 SQL/자료는 로컬 제품 표에 넣지 않았다.
- PK guard: ALWAYS의 id=id는 DB가 428C9로 먼저 거부한다. id=DEFAULT의 실제 값 변경은 LW001로 거부되며 같은 ID의 일반 속성 수정은 성공한다. 다른 제약이 먼저 거부하면 그 오류를 유지하는 기존 계약과 일치한다.
- 문서 46개·로컬 참조 698개 검사 오류 없음, DB 문서 경로/접속 환경 도구 검사 9건과 변경 문서 포맷/공백 검사 통과. 기존 Task/Issue의 100줄 초과는 안내 경고이며 필요한 계획/미정은 유지했다.
- [JUnit 결과 요약/코드 지문](task-001-database-verification.json)과 [로컬 메타정보 대조](task-001-local-metadata.json)는 실제 실행 근거다. 사용자용 결과와 제약은 [DB 적용 결과](../../../../../db/migration/application-status.md#current), 재현 명령은 [구현 안내](../../../../../db/model/implementation.md#current)가 소유한다.

<a id="acceptance"></a>

## 완료 조건과 수용

Task 001은 완료다. 부모 Issue #43·Phase 001의 완료로 전파하지 않는다.

| 완료 조건 | 충족 근거 |
| --- | --- |
| 승인한 공통 식별·시즌/패치·지역/분류 저장 구조와 Java 매핑 | V1의 8개 표·키/FK/NULL/UNIQUE/CHECK·guard/권한과 JPA validate, 승인본 DDL 지문 일치 |
| 서비스 저장/조회·기본 수정과 오류/롤백 | 단위 30·격리 통합 11건, 지도 선택/교정·작업용 이름 분리·순환 검사·업무/설치 롤백 |
| 격리 검증 후 정확한 로컬 대상 적용 | 승인한 역할/최소 권한·빈 관리 표 소유 준비, Flyway V1 성공·app JPA 검증, 메타정보 대조/제품 0행 |
| 후속 식별/참조·검사 계약과 현재 문서 | DB 목적별 안내·서비스 사용법, 소비 참조/잠금·CatalogReferenceCheck 인계, Task·부모/현황 대응 |

## 자체·별도 검수

비교 기준은 49c39d4, 대상은 실제 제출 후보의 DDL/Java·테스트/프로브 동반 변경·DB 문서와 담당/상위 기록이다. 자체 검수에서 요구/원천·범위·입력/결과·후속 영향과 현재 지문을 대조했다. 별도 에이전트 task001_runtime_final은 코드/DDL·실행 근거를, task001_acceptance_final은 수용/문서·부모 상태를 읽기 전용 검수했다.

필수 코드/DDL 결함은 없었다. 문서에 남은 구현/DB 보류·해결한 미정·과거 허용 범위의 불일치를 현재 계약/생성 결과에 맞췄다. 동일한 Java/DDL·38개 소스와 원본 JUnit 지문에 대한 41건 검증 근거를 재사용하며, 문서 수정에 맞는 형식/참조·기록/상태와 실제 인덱스 대조를 수행한다. 실제 인덱스의 TDD 근거·기록 검사, Task 완료 상태 일치와 공백 검사를 통과했다. 기존 Git 개행 정규화를 반영한 인덱스 내용과 38개 검증 입력을 대조했다. 이번 별도 검수에서는 DB를 다시 실행하지 않았다.

## 잔여와 후속 인계

| 남은 항목 | 담당·필요 입력 | 처리 시점 |
| --- | --- | --- |
| 아이템/스킬 버전·능력치 원본/캐시 | 002, 확정 R1/R2/R3·현재 분류와 필수 종류 참조, 개별 수량/JSON 의미 | 해당 저장 계약 구현 전 새 선택을 먼저 확인 |
| 제작/획득/배달 본행·결합 조회/소비 검사 | 003/004, 지속 region.id·패치별 지도 소속·유효 구간과 버전 참조 | 소비 표 저장 전 CatalogReferenceCheck와 동일 잠금 계약 연결, 실제 서비스 업무 경합/실패 검증 |
| 실제 이름·목록·날짜/출처·등록·교정 | #45, 제공 자료·기준 패치/시간대·해석과 확인용 화면 | 현재 보류. 사용자 재개와 필요한 저장/조회·검증 수단 준비 뒤 |
| 제품 API/화면·제작/루트 소비 기능 | #44 및 #46/#47, 해당 기능의 입력/응답·사용 흐름 | 해당 기능의 설계/화면/구현 단계에서 확인 |
| 추가 표/다른 대상·복원/키 재배치/정비 | 변경 담당과 001 참조 계약, 정확한 이유·대상·보존/실패/복구 범위 | 실제 필요 때 별도 확인. 신규 생성 직전 전체 구조/정확한 실행 대상 사용자 확인 |

현재 동시성 근거는 JDBC 기준 잠금 충돌/해제와 일반 SELECT 허용까지다. 후속 소비 업무 간 경합 전체·화면·실제 자료의 적합성을 확인했다고 판단하지 않는다. 추가 사용자 결정 없이 공통 기반 완료를 수용할 수 있으며 실제 자료 작업 보류는 유지한다.

<a id="workflow-recovery"></a>

## 변경 소유 분리와 보존

[Issue/Task 소유 대조](issue-43-change-ownership.md#current)에 따라 Issue 준비/등록 문서는 issue/43-item-persistence의 d6adc6f에 두고, 그 커밋에서 task/43-001-common-storage를 분기해 공통 모델·최초 구동·저장/조회·검증 결과를 배치했다. Task 본문의 상세 실행 기록은 같은 브랜치의 로컬 근거와 연결한다. Issue/부모 수용을 완료로 바꾸지 않는다.

원본 49c39d4·45ec5d7·9b8773e와 기존 task/43-001-common-model·로컬 codex/preserved-43-before-split은 그대로 보존한다. 새 Task 배치의 코드/DDL과 직접 지원 파일은 9b8773e의 Git 원본과 대조하며 실제 등록 #67~#70·부모 #43·milestone/자기 상태를 유지한다. 정상화의 상세 문서/메타정보 외 동작을 변경하지 않는다.

이번 요청은 PR·병합·DB 작업을 포함하지 않는다. 기존 커밋을 사후 분리하며 과거에 정식 절차를 수행한 것으로 기록하지 않는다. 이전 41건 검증과 승인 DDL 지문은 보존된 원본을 근거로 재사용한다.

<!-- tdd-plan -->

```json
{
  "schema": 1,
  "cycles": [
    {
      "id": "creation-confirmation-documents",
      "kind": "correction",
      "reason": "DB Markdown 문서 예외다. 실제 생성 전 사용자 확인용 전체 구조·대상·현재 거부/미확인 경계를 문서화한다. SQL·Java·실제 DB 상태를 변경하지 않는다.",
      "targets": [
        "db/migration/creation-review.md",
        "db/migration/README.md",
        "db/README.md"
      ],
      "tests": [
        "scripts/quality-db-docs.test.mjs"
      ],
      "settings": [
        "scripts/quality/paths.mjs"
      ],
      "adapter": "junit",
      "command": [
        "node",
        "--test",
        "--test-reporter=junit",
        "--test-reporter-destination={report}",
        "scripts/quality-db-docs.test.mjs"
      ]
    },
    {
      "id": "creation-scope-and-results",
      "kind": "correction",
      "reason": "DB Markdown 문서 예외다. 사용자가 승인한 기존 로컬 메타정보/8개 표 적용 범위와 실제 격리 검증·로컬 준비 승인 대기·적용 결과를 목적별 문서에 반영한다. DDL 구조와 게임 자료는 변경하지 않는다.",
      "targets": [
        "db/README.md",
        "db/migration/README.md",
        "db/migration/creation-review.md",
        "db/migration/application-status.md",
        "db/model/implementation.md",
        "db/model/table-layout.md",
        "db/model/region-layout.md",
        "db/model/permissions-and-installation.md",
        "db/model/common-tables.md",
        "db/model/ranges-and-uniqueness.md",
        "db/model/writes-and-checks.md",
        "db/model/names-and-dates.md"
      ],
      "tests": [
        "scripts/quality-db-docs.test.mjs"
      ],
      "settings": [
        "scripts/quality/paths.mjs"
      ],
      "adapter": "junit",
      "command": [
        "node",
        "--test",
        "--test-reporter=junit",
        "--test-reporter-destination={report}",
        "scripts/quality-db-docs.test.mjs"
      ]
    },
    {
      "id": "final-current-document-consistency",
      "kind": "correction",
      "reason": "DB Markdown 문서 예외다. 최종 검수에서 찾은 현재 상태/완료 원천의 오래된 후보·미정 안내를 확정한 V1과 적용 결과에 연결한다. 구조·정책·DB를 변경하지 않는다.",
      "targets": [
        "db/README.md",
        "db/model/common-tables.md"
      ],
      "tests": [
        "scripts/quality-db-docs.test.mjs"
      ],
      "settings": [
        "scripts/quality/paths.mjs"
      ],
      "adapter": "junit",
      "command": [
        "node",
        "--test",
        "--test-reporter=junit",
        "--test-reporter-destination={report}",
        "scripts/quality-db-docs.test.mjs"
      ]
    }
  ]
}
```

<!-- tdd-evidence -->
```json
{
  "schema": 1,
  "receipts": [
    {
      "id": "creation-confirmation-documents",
      "kind": "correction",
      "spec": "f86e0350beab7421ea8531cb2b1fa9ffe34154e2b6b92d6c4071255c71cfe7a4",
      "worktree": "f8f58622827de84fd0e6",
      "finished": true,
      "baseline": "49c39d43e35dcff40cfcbcac7328fcd4b070b085",
      "task": "work/records/phase-001/issue-43/artifacts/task-001-creation.md",
      "final": {
        "runId": "626e31112d0f4057becc303b0261d720",
        "started": 1794568111.0782108,
        "finishedAt": 1794568111.6137028,
        "command": [
          "node",
          "--test",
          "--test-reporter=junit",
          "--test-reporter-destination={report}",
          "scripts/quality-db-docs.test.mjs"
        ],
        "exitCode": 0,
        "result": {
          "tests": 3,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "names": [
            "test.database Markdown has a format scope without enabling SQL formatting",
            "test.docs collection includes database Markdown and excludes raw evidence",
            "test.database documentation changes select only documentation checks"
          ],
          "failedNames": []
        },
        "manifest": {
          ".codex/hooks.json": "816cb983d2faded1df2b58fc7da4b371c5990800df09768b324a8674448e31d4",
          ".gitattributes": "4437511f6b3b866745490f0fcd2332d1e6194980fc028232ce0a84cec608d85b",
          "backend/build.gradle": "52b40fbbcdbb75b4ee5d5997811157a0ed61562cbd87c9eb6c3d859a88dd7960",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/resources/application.yaml": "d10d1ef05ddbec053c30bf2bc705e4c5f19a2b688baccd61a4f48af556bb40e0",
          "backend/src/test/resources/application-test.yaml": "e6aa7eb8da29c749b63e7330c634631d82f8710dc4fb6dee5ef883df1ce12e72",
          "db/README.md": "65a4157999a852f3a27ec424c0d64c55be4b542027de1c3f5c131299b10fa4b8",
          "db/migration/README.md": "a19bee3e2e8c05f419e6cf657ad0711aacff5e85b0aef8d70dfa1e49e0edf1d6",
          "db/migration/creation-review.md": "56a789606b19274be9f56599a2b760b0de86ff1d017a1d80ff84c823e165c6ee",
          "frontend/package-lock.json": "e54e76e4ab1a402d4df0827152d1bf5c62142cd59e2798518b7ed2715931fc97",
          "frontend/package.json": "aae2e6358d704e1807f860f58272e3f8024cfdc092860bd0b0b4f7d58e76a228",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "2e55a2050f22641deaad0ac4b9b6723ad76aadab22ab037b9d38b1697a458367",
          "frontend/vitest.config.mjs": "f07e4974ad24bc562f5a975e8af587eb6fdfb402863825c718cfdf9a8b684eec",
          "package-lock.json": "539f24e43b65266883d2aa1a83428d75484cf059eeedcedf4043d09dc6d8a5e3",
          "package.json": "0e57b51524c8151aafb0155a93c5f61c30901819bde6cee895c0106f6dfcab85",
          "scripts/quality-db-docs.test.mjs": "737f37ca0275acb010da0c7ce6521375dbb7f44b5c419a4dc611560c1cf43e59",
          "scripts/quality/paths.mjs": "3024a32e429115cf47b45b500515fb64e62b24fe7276d257d18c7df5f8526855",
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": true
      }
    },
    {
      "id": "creation-scope-and-results",
      "kind": "correction",
      "spec": "ac462b55ae73c3f3253d9f1fadf161b662b1c1e3ddb4b21cbf58bfa47b288bdf",
      "worktree": "f8f58622827de84fd0e6",
      "finished": true,
      "baseline": "49c39d43e35dcff40cfcbcac7328fcd4b070b085",
      "task": "work/records/phase-001/issue-43/artifacts/task-001-creation.md",
      "final": {
        "runId": "371b9d46a58a496fbb407025fe709cf8",
        "started": 1794569430.7469697,
        "finishedAt": 1794569431.3731658,
        "command": [
          "node",
          "--test",
          "--test-reporter=junit",
          "--test-reporter-destination={report}",
          "scripts/quality-db-docs.test.mjs"
        ],
        "exitCode": 0,
        "result": {
          "tests": 3,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "names": [
            "test.database Markdown has a format scope without enabling SQL formatting",
            "test.docs collection includes database Markdown and excludes raw evidence",
            "test.database documentation changes select only documentation checks"
          ],
          "failedNames": []
        },
        "manifest": {
          ".codex/hooks.json": "816cb983d2faded1df2b58fc7da4b371c5990800df09768b324a8674448e31d4",
          ".gitattributes": "4437511f6b3b866745490f0fcd2332d1e6194980fc028232ce0a84cec608d85b",
          "backend/build.gradle": "52b40fbbcdbb75b4ee5d5997811157a0ed61562cbd87c9eb6c3d859a88dd7960",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/resources/application.yaml": "d10d1ef05ddbec053c30bf2bc705e4c5f19a2b688baccd61a4f48af556bb40e0",
          "backend/src/test/resources/application-test.yaml": "e6aa7eb8da29c749b63e7330c634631d82f8710dc4fb6dee5ef883df1ce12e72",
          "db/README.md": "ecb8ed33bcc29506e1631be279d124379bf677ba12fdadad399fc4ae7cecf125",
          "db/migration/README.md": "1a331f246299ab6f09f652cd2ae514dbe9cd3f7cba1230e611a3e18bce5189cc",
          "db/migration/application-status.md": "3bcf228f9d567cff7c30d5c3c76a62e9b84f3b1e5befa453d0ce7ca8f3a32f95",
          "db/migration/creation-review.md": "5908c47649b81726e81313ae53da859483d4187b7795bcd39f081c4ca2eaff88",
          "db/model/common-tables.md": "e47d9ed2fa39ac2aabe0d78d71b083aacacbc9bfd701f8e1d811028ba86a28a9",
          "db/model/implementation.md": "7b90810c4a7babc63c5559272c74d817aa3fa28fb30c9d644eccf951933dd924",
          "db/model/names-and-dates.md": "8e2b8758df399699f852a51c0b4ca75e5706434d25864355d2b2ac5b8d3b21bc",
          "db/model/permissions-and-installation.md": "6f963f9544faedc92bfd05b6eef90db9e44d2075b76cebedbe0408dc9f300de7",
          "db/model/ranges-and-uniqueness.md": "54581609fac723c7f728b7e74c511e5fe57d8beb6a03f29c16738f76a71fabd3",
          "db/model/region-layout.md": "fd09a77c70c52a0c7e7c24c12744324cfee9d566080276da57675feb76131ad3",
          "db/model/table-layout.md": "cf3c45a737cafb204417b7f0acf9d540a10cd98deee17f7501214679d80fd007",
          "db/model/writes-and-checks.md": "1fcbf3a6f04eab869c20f87ef48e7306e7e16afb35f299a806dab2173f002d36",
          "frontend/package-lock.json": "e54e76e4ab1a402d4df0827152d1bf5c62142cd59e2798518b7ed2715931fc97",
          "frontend/package.json": "aae2e6358d704e1807f860f58272e3f8024cfdc092860bd0b0b4f7d58e76a228",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "2e55a2050f22641deaad0ac4b9b6723ad76aadab22ab037b9d38b1697a458367",
          "frontend/vitest.config.mjs": "f07e4974ad24bc562f5a975e8af587eb6fdfb402863825c718cfdf9a8b684eec",
          "package-lock.json": "539f24e43b65266883d2aa1a83428d75484cf059eeedcedf4043d09dc6d8a5e3",
          "package.json": "0e57b51524c8151aafb0155a93c5f61c30901819bde6cee895c0106f6dfcab85",
          "scripts/quality-db-docs.test.mjs": "737f37ca0275acb010da0c7ce6521375dbb7f44b5c419a4dc611560c1cf43e59",
          "scripts/quality/paths.mjs": "3024a32e429115cf47b45b500515fb64e62b24fe7276d257d18c7df5f8526855",
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": true
      }
    },
    {
      "id": "final-current-document-consistency",
      "kind": "correction",
      "spec": "069a998f4ab3e4816654501bfb1e86cbd5d6ca2bfee2125f6e225b24838b66c2",
      "worktree": "f8f58622827de84fd0e6",
      "finished": true,
      "baseline": "49c39d43e35dcff40cfcbcac7328fcd4b070b085",
      "task": "work/records/phase-001/issue-43/artifacts/task-001-creation.md",
      "final": {
        "runId": "7a2ac6c3561744c2a226a935d22bd508",
        "started": 1794569948.0563753,
        "finishedAt": 1794569948.5600348,
        "command": [
          "node",
          "--test",
          "--test-reporter=junit",
          "--test-reporter-destination={report}",
          "scripts/quality-db-docs.test.mjs"
        ],
        "exitCode": 0,
        "result": {
          "tests": 3,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "names": [
            "test.database Markdown has a format scope without enabling SQL formatting",
            "test.docs collection includes database Markdown and excludes raw evidence",
            "test.database documentation changes select only documentation checks"
          ],
          "failedNames": []
        },
        "manifest": {
          ".codex/hooks.json": "816cb983d2faded1df2b58fc7da4b371c5990800df09768b324a8674448e31d4",
          ".gitattributes": "4437511f6b3b866745490f0fcd2332d1e6194980fc028232ce0a84cec608d85b",
          "backend/build.gradle": "52b40fbbcdbb75b4ee5d5997811157a0ed61562cbd87c9eb6c3d859a88dd7960",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/resources/application.yaml": "d10d1ef05ddbec053c30bf2bc705e4c5f19a2b688baccd61a4f48af556bb40e0",
          "backend/src/test/resources/application-test.yaml": "e6aa7eb8da29c749b63e7330c634631d82f8710dc4fb6dee5ef883df1ce12e72",
          "db/README.md": "0b5c1c3a902bb4bac63201f2b4c0a2b5d21593e36c5623ed28b3394be38ac344",
          "db/model/common-tables.md": "2f3240f5afcfa2a0245eb1b80b78b9bb6b95310c9ed76407d0a692e8674b6e03",
          "frontend/package-lock.json": "e54e76e4ab1a402d4df0827152d1bf5c62142cd59e2798518b7ed2715931fc97",
          "frontend/package.json": "aae2e6358d704e1807f860f58272e3f8024cfdc092860bd0b0b4f7d58e76a228",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "2e55a2050f22641deaad0ac4b9b6723ad76aadab22ab037b9d38b1697a458367",
          "frontend/vitest.config.mjs": "f07e4974ad24bc562f5a975e8af587eb6fdfb402863825c718cfdf9a8b684eec",
          "package-lock.json": "539f24e43b65266883d2aa1a83428d75484cf059eeedcedf4043d09dc6d8a5e3",
          "package.json": "0e57b51524c8151aafb0155a93c5f61c30901819bde6cee895c0106f6dfcab85",
          "scripts/quality-db-docs.test.mjs": "737f37ca0275acb010da0c7ce6521375dbb7f44b5c419a4dc611560c1cf43e59",
          "scripts/quality/paths.mjs": "3024a32e429115cf47b45b500515fb64e62b24fe7276d257d18c7df5f8526855",
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": true
      }
    }
  ]
}
```
