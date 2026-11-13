# Task 43-001 — 최초 구동 검증

<a id="current"></a>

담당: [Task 43-001](../task-001.md#summary). 실행기 접속값 경계와 새 격리 DB의 최초 준비·Spring/Flyway 접속을 검증한다. 실제 게임 자료와 기존 개발 DB·볼륨은 사용하지 않는다.

DB 문서의 갱신과 포맷/수집·CI 분류 검증은 [DB 문서 확인](#database-documents)을 따른다. 문서와 도구 변경을 최초 구동 DB 재검증으로 표시하지 않는다.

## 확인할 동작

- app/Flyway 필수값·고정 이름 검사, 관리자/과거 접속값의 Java 전달 차단, 일반 환경·비밀번호 값 보존.
- 빈 격리 DB의 두 역할/최소 권한 준비, migrator 설치/app 접속과 금지 권한 확인.
- 실패 시 역할/권한 준비 단위 롤백과 원문 SQL·비밀번호·오류 출력 차단.
- 로그 조건 불일치·필수값 누락 시 역할 쓰기 전 중단.

<a id="tdd-plan"></a>

## 실행 범위

## 커밋 전 확인

- 비교 기준은 HEAD 0239caae788f1724547579eae46f4caa6eb3df71과 실제 index다. 최초 구동 구현·확정 저장 계약의 체크포인트이며 공통 도메인 구현 완료가 아니다.
- 자체 확인에서 실행기/DB 문서 경로 테스트 9건 통과, JDK 21의 Spotless·단위 테스트·JAR 빌드 성공을 확인했다. Gradle은 일치하는 캐시 결과를 재사용했다. DB/Docker는 실행하지 않고 기존 격리 DB 통과 영수증과 index 입력의 일치를 확인했다.
- 런타임과 계약 문서를 별도 에이전트가 읽기 전용 검수했다. 현재 계약의 미정 재표시와 현황 부모 계층을 수정했고 같은 검토자가 해당 수정의 실제 index를 재확인했다. 추가 필수 지적은 없다.
- TDD 후보·현황 원천·기록·문서 참조/형식을 검사했다. 실제 자료·기존 DB/볼륨·개인 환경값과 제품 도메인 표 생성은 수행하지 않았다. 커밋 이후 허용된 구현 파일 작성은 별도 작업 내용으로 구별한다.

<!-- tdd-plan -->

```json
{
  "schema": 1,
  "cycles": [
    {
      "id": "local-environment",
      "kind": "behavior",
      "targets": [
        "scripts/dev-api.mjs",
        ".gitattributes"
      ],
      "tests": [
        "scripts/dev-api.test.mjs"
      ],
      "settings": [],
      "adapter": "junit",
      "command": [
        "node",
        "--test",
        "--test-reporter=junit",
        "--test-reporter-destination={report}",
        "scripts/dev-api.test.mjs"
      ],
      "expectedFailures": [
        "test.missing app or Flyway passwords cannot use legacy credentials",
        "test.only app and Flyway credentials reach Java while normal environment survives",
        "test.local database and role names must match the agreed identities"
      ]
    },
    {
      "id": "database-bootstrap",
      "kind": "behavior",
      "targets": [
        "db/bootstrap/10-prepare-roles.sh",
        "db/bootstrap/sql/prepare-roles.sql",
        "compose.yaml",
        ".env.example",
        "backend/src/main/resources/application-local.yaml",
        "scripts/verify-bootstrap.mjs"
      ],
      "tests": [
        "backend/src/test/java/io/github/minokim/lumiawiki/BootstrapInitializationTests.java",
        "backend/src/test/resources/db/bootstrap-migration/V1__bootstrap_test_probe.sql"
      ],
      "settings": [],
      "adapter": "junit",
      "command": [
        "backend/gradlew.bat",
        "-p",
        "backend",
        "integrationTest",
        "--tests",
        "io.github.minokim.lumiawiki.BootstrapInitializationTests",
        "--console=plain",
        "--no-daemon",
        "-PtddReportDir={report}",
        "--max-workers=2",
        "-Dorg.gradle.jvmargs=-Xms64m -Xmx256m -XX:MaxMetaspaceSize=256m"
      ],
      "expectedFailures": [
        "io.github.minokim.lumiawiki.BootstrapInitializationTests.initializationSeparatesRolesAndSpringConnections(CapturedOutput)",
        "io.github.minokim.lumiawiki.BootstrapInitializationTests.lateSqlFailureRollsBackRolesAndPrivilegesWithoutSecretOutput()",
        "io.github.minokim.lumiawiki.BootstrapInitializationTests.nonstandardLoggingStopsBeforePasswordSql()",
        "io.github.minokim.lumiawiki.BootstrapInitializationTests.missingInputFailsBeforeDatabaseWrites()"
      ]
    },
    {
      "id": "isolated-bootstrap-validation",
      "kind": "correction",
      "reason": "검증 환경에서 호스트 Spring/JVM 접속 설정을 제거하고 운영 이미지와 같은 SCRAM 호스트 인증을 명시한다. 제품 동작 변경 없이 테스트의 격리/인증 가정을 바로잡는다.",
      "targets": [
        "db/bootstrap/10-prepare-roles.sh",
        "db/bootstrap/sql/prepare-roles.sql",
        "compose.yaml",
        ".env.example",
        "backend/src/main/resources/application-local.yaml",
        "scripts/verify-bootstrap.mjs",
        "backend/src/test/java/io/github/minokim/lumiawiki/BootstrapInitializationTests.java"
      ],
      "tests": [
        "backend/src/test/java/io/github/minokim/lumiawiki/BootstrapInitializationTests.java",
        "backend/src/test/resources/db/bootstrap-migration/V1__bootstrap_test_probe.sql"
      ],
      "settings": [],
      "adapter": "junit",
      "command": [
        "backend/gradlew.bat",
        "-p",
        "backend",
        "integrationTest",
        "--tests",
        "io.github.minokim.lumiawiki.BootstrapInitializationTests",
        "--console=plain",
        "--no-daemon",
        "-PtddReportDir={report}",
        "--max-workers=2",
        "-Dorg.gradle.jvmargs=-Xms64m -Xmx256m -XX:MaxMetaspaceSize=256m"
      ]
    },
    {
      "id": "database-documentation-scope",
      "kind": "behavior",
      "targets": [
        "scripts/quality/paths.mjs"
      ],
      "tests": [
        "scripts/quality-db-docs.test.mjs"
      ],
      "settings": [],
      "adapter": "junit",
      "command": [
        "node",
        "--test",
        "--test-reporter=junit",
        "--test-reporter-destination={report}",
        "scripts/quality-db-docs.test.mjs"
      ],
      "expectedFailures": [
        "test.database Markdown has a format scope without enabling SQL formatting",
        "test.docs collection includes database Markdown and excludes raw evidence",
        "test.database documentation changes select only documentation checks"
      ]
    },
    {
      "id": "database-documentation",
      "kind": "correction",
      "reason": "db 경로는 편집 guard에서 동작 대상으로 분류되지만 이번 대상 네 파일은 현재 계약과 사용법을 설명하는 Markdown뿐이다. 런타임 변경 없이 문서와 링크를 작성하고 DB 문서의 포맷/수집 경계 검증을 재사용한다.",
      "targets": [
        "db/README.md",
        "db/bootstrap/README.md",
        "db/model/common-tables.md",
        "db/migration/README.md"
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
      "id": "database-model-decisions",
      "kind": "correction",
      "reason": "사용자가 확인한 D3 일대일 대응과 D4 게임 패치 단위 이력을 DB 모델 Markdown에 반영한다. 런타임 변경 없이 문서의 확정/미정 경계를 갱신한다.",
      "targets": [
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
    },
    {
      "id": "checkpoint-db-documentation",
      "kind": "correction",
      "reason": "커밋 후보의 DB Markdown을 한 번에 확인한다. 런타임은 일치하는 기존 통과 영수증을 재사용하고 이 단계에서는 문서 포맷/수집 검사만 실행하며 DB 작업은 하지 않는다.",
      "targets": [
        "db/README.md",
        "db/bootstrap/README.md",
        "db/migration/README.md",
        "db/model/common-tables.md",
        "db/model/consumer-references.md",
        "db/model/names-and-dates.md",
        "db/model/permissions-and-installation.md",
        "db/model/ranges-and-uniqueness.md",
        "db/model/region-layout.md",
        "db/model/table-layout.md",
        "db/model/writes-and-checks.md"
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

<a id="results"></a>

## 검증 결과

| 검증 | 결과·근거 |
| --- | --- |
| 실행기 환경 경계 | Node 6건 통과. `local-environment`의 Red 3건 실패·Green 6건 성공 receipt를 아래에 보존 |
| Compose 설정 | 합성 전용 env-file을 지정한 실제 `compose.yaml`의 `config --quiet` 성공. 개인 .env 미사용, 컨테이너 생성 없음 |
| 최초 준비·권한·실패 | 새 PostgreSQL 18.6/SCRAM 환경의 통합 4건 통과. 역할·소유·허용/금지 권한·특수 문자 값 보존·로그 조건/누락 거부·중간 실패 롤백·고정 출력 확인 |
| 백엔드 회귀·패키징 | `spotlessCheck test integrationTest bootJar` 성공. 단위 9건·통합 6건, 실패·오류·skip 0 |
| 실제 최초 구동 | `JAVA_HOME`에 기존 JDK 21을 지정한 `node scripts/verify-bootstrap.mjs` 성공. 실행 ID `lw-bootstrap-6214226fbceb`. JAR SQL 포함·Flyway 적용·앱/DB 재시작 보존·잘못된 비밀번호 거부·실제 env-file/bootRun 확인 |
| 격리·정리 | 원천 지문 보존, 제품 SQL/JAR에 합성 SQL 없음. 검증 프로젝트 소유를 확인한 임시 컨테이너/볼륨 정리 완료. 비밀값 없는 실행 결과는 `.tmp/issue-42/task-001/lw-bootstrap-6214226fbceb/result.json` |

개인 `.env`·기존 개발 DB/볼륨·실제 게임 자료는 사용하지 않았다. 기존 DB 이관·개인 환경 실행·공통 도메인 표와 P1 보호 장치 적용·제품 화면 검증은 수행하지 않았다. Task 43-001 전체 완료와 구별한다.

자체 검수에서 구현 원천·설정 연결·권한/소유·실패 종료·격리 범위와 검증 근거를 대조했다. 쉘/SQL은 UTF-8·BOM 없음·LF를 확인했다. 원문 오류를 출력하지 않는 최초 준비 진단과 기본 Flyway/JPA 기동의 한계는 계약대로 유지한다. 문서 26개·로컬 참조 521개·담당 미정 12개 묶음 검사에서 오류는 없었다. Task/Issue 100줄 초과는 안내 경고이며 필요한 현재 계획을 유지한다.

<a id="database-documents"></a>

## DB 문서와 검사 경계

[DB 안내](../../../../../db/README.md#current)·최초 구동·공통 표·마이그레이션의 네 문서를 목적별로 작성했다. DB 변경 때 담당 문서도 갱신하며 상세 계약의 중복 복사와 실행 경과 누적은 하지 않는다. D3는 일대일 대응, D4는 지속 지역 ID·별도 연결/이력의 게임 패치 단위 보존을 반영했다. 실제 열·표·키·제약 배치는 미정이다.

- DB Markdown 포맷·문서 수집·CI 분류 3건: 실제 Red 3건 실패 → Green 3건 통과. SQL/쉘/원자료·증거 첨부의 제외를 확인했다.
- 기존 품질 회귀 21건: Windows에서 20건 통과·파일 symlink 권한이 필요한 1건 skip. 디렉터리 junction 거부·실제 hook fixture·인덱스 형식·중복/재진입·보존 경계·복구 동작을 확인했다. 명령은 `python -B -X utf8 -m unittest discover -s scripts/tests -p test_quality.py -v`다.
- 실제 `apply_patch`의 DB 문서 생성과 포맷을 확인했다. 저장소의 실제 인덱스 변경·커밋 실행은 하지 않았다. 기존 Git/Codex hook 정의·Java 포맷 경로는 그대로이며 변경한 경로 분류·수집의 근거를 현재 hook 현황에 연결한다.
- 이번 확인은 문서·도구 범위다. 새 DB를 만들거나 기존 DB/개인 .env·게임 자료를 조회하지 않았다. 최초 구동 동작의 기존 실행 근거와 구별한다.
- 자체 검수에서 선택한 D3/D4 의미·미정 경계와 DB 문서/담당 원천의 일치를 대조했다. 문서 32개·참조 555개·담당 미정 12개 묶음 검사와 형식·hook 현황 검사를 통과했다. Task/Issue의 100줄 초과는 안내 경고이며 기존 계획을 보존했다.

<!-- tdd-evidence -->
```json
{
  "schema": 1,
  "receipts": [
    {
      "id": "local-environment",
      "kind": "behavior",
      "spec": "d062833893177b5e87d0b4d0b5ae65b8510ae993773cd8ca11f2ce70d1a9e558",
      "worktree": "f8f58622827de84fd0e6",
      "baseline": "0239caae788f1724547579eae46f4caa6eb3df71",
      "task": "work/records/phase-001/issue-43/artifacts/task-001-bootstrap-verification.md",
      "finished": true,
      "red": {
        "runId": "496d667c19e348628ff34b2fa7d67933",
        "started": 1794556254.955703,
        "finishedAt": 1794556255.3553538,
        "command": [
          "node",
          "--test",
          "--test-reporter=junit",
          "--test-reporter-destination={report}",
          "scripts/dev-api.test.mjs"
        ],
        "exitCode": 1,
        "result": {
          "tests": 6,
          "failures": 3,
          "errors": 0,
          "skipped": 0,
          "names": [
            "test.missing app or Flyway passwords cannot use legacy credentials",
            "test.invalid DB and server ports are rejected before starting Java",
            "test.DB host cannot inject JDBC options or disclose credentials",
            "test.only app and Flyway credentials reach Java while normal environment survives",
            "test.local database and role names must match the agreed identities",
            "test.password characters and whitespace are preserved without normalization"
          ],
          "failedNames": [
            "test.missing app or Flyway passwords cannot use legacy credentials",
            "test.only app and Flyway credentials reach Java while normal environment survives",
            "test.local database and role names must match the agreed identities"
          ]
        },
        "manifest": {
          ".codex/hooks.json": "816cb983d2faded1df2b58fc7da4b371c5990800df09768b324a8674448e31d4",
          ".gitattributes": null,
          "backend/build.gradle": "52b40fbbcdbb75b4ee5d5997811157a0ed61562cbd87c9eb6c3d859a88dd7960",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/resources/application.yaml": "d10d1ef05ddbec053c30bf2bc705e4c5f19a2b688baccd61a4f48af556bb40e0",
          "backend/src/test/resources/application-test.yaml": "e6aa7eb8da29c749b63e7330c634631d82f8710dc4fb6dee5ef883df1ce12e72",
          "frontend/package-lock.json": "e54e76e4ab1a402d4df0827152d1bf5c62142cd59e2798518b7ed2715931fc97",
          "frontend/package.json": "aae2e6358d704e1807f860f58272e3f8024cfdc092860bd0b0b4f7d58e76a228",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "2e55a2050f22641deaad0ac4b9b6723ad76aadab22ab037b9d38b1697a458367",
          "frontend/vitest.config.mjs": "f07e4974ad24bc562f5a975e8af587eb6fdfb402863825c718cfdf9a8b684eec",
          "package-lock.json": "539f24e43b65266883d2aa1a83428d75484cf059eeedcedf4043d09dc6d8a5e3",
          "package.json": "0e57b51524c8151aafb0155a93c5f61c30901819bde6cee895c0106f6dfcab85",
          "scripts/dev-api.mjs": "6dc4b11632e8f77222b8686fea3d994b696902a924ab483d7bf11874e5881008",
          "scripts/dev-api.test.mjs": "3adb60dd4f689197a344c4da1fd04ffdfaa094a86b569cfd6f76f739e567090a",
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": false
      },
      "final": {
        "runId": "b68bce36da4c40fc9eb2053b6c362413",
        "started": 1794556277.2256472,
        "finishedAt": 1794556277.6289847,
        "command": [
          "node",
          "--test",
          "--test-reporter=junit",
          "--test-reporter-destination={report}",
          "scripts/dev-api.test.mjs"
        ],
        "exitCode": 0,
        "result": {
          "tests": 6,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "names": [
            "test.missing app or Flyway passwords cannot use legacy credentials",
            "test.invalid DB and server ports are rejected before starting Java",
            "test.DB host cannot inject JDBC options or disclose credentials",
            "test.only app and Flyway credentials reach Java while normal environment survives",
            "test.local database and role names must match the agreed identities",
            "test.password characters and whitespace are preserved without normalization"
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
          "frontend/package-lock.json": "e54e76e4ab1a402d4df0827152d1bf5c62142cd59e2798518b7ed2715931fc97",
          "frontend/package.json": "aae2e6358d704e1807f860f58272e3f8024cfdc092860bd0b0b4f7d58e76a228",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "2e55a2050f22641deaad0ac4b9b6723ad76aadab22ab037b9d38b1697a458367",
          "frontend/vitest.config.mjs": "f07e4974ad24bc562f5a975e8af587eb6fdfb402863825c718cfdf9a8b684eec",
          "package-lock.json": "539f24e43b65266883d2aa1a83428d75484cf059eeedcedf4043d09dc6d8a5e3",
          "package.json": "0e57b51524c8151aafb0155a93c5f61c30901819bde6cee895c0106f6dfcab85",
          "scripts/dev-api.mjs": "4318ecb17725773d2a3435d37667ca24ad4351b72cf3cce9d46147bbbc42bd00",
          "scripts/dev-api.test.mjs": "3adb60dd4f689197a344c4da1fd04ffdfaa094a86b569cfd6f76f739e567090a",
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": true
      }
    },
    {
      "id": "database-bootstrap",
      "kind": "behavior",
      "spec": "dd79f4173eb48133736c7909a6df7ad52679fe33163e015cba33ddd1a5a531a4",
      "worktree": "f8f58622827de84fd0e6",
      "baseline": "0239caae788f1724547579eae46f4caa6eb3df71",
      "task": "work/records/phase-001/issue-43/artifacts/task-001-bootstrap-verification.md",
      "finished": true,
      "red": {
        "runId": "d46905c0061342eeab249fe7c1d0fe7d",
        "started": 1794556647.7676167,
        "finishedAt": 1794556676.3811083,
        "command": [
          "backend/gradlew.bat",
          "-p",
          "backend",
          "integrationTest",
          "--tests",
          "io.github.minokim.lumiawiki.BootstrapInitializationTests",
          "--console=plain",
          "--no-daemon",
          "-PtddReportDir={report}",
          "--max-workers=2",
          "-Dorg.gradle.jvmargs=-Xms64m -Xmx256m -XX:MaxMetaspaceSize=256m"
        ],
        "exitCode": 1,
        "result": {
          "tests": 4,
          "failures": 4,
          "errors": 0,
          "skipped": 0,
          "names": [
            "io.github.minokim.lumiawiki.BootstrapInitializationTests.nonstandardLoggingStopsBeforePasswordSql()",
            "io.github.minokim.lumiawiki.BootstrapInitializationTests.missingInputFailsBeforeDatabaseWrites()",
            "io.github.minokim.lumiawiki.BootstrapInitializationTests.initializationSeparatesRolesAndSpringConnections(CapturedOutput)",
            "io.github.minokim.lumiawiki.BootstrapInitializationTests.lateSqlFailureRollsBackRolesAndPrivilegesWithoutSecretOutput()"
          ],
          "failedNames": [
            "io.github.minokim.lumiawiki.BootstrapInitializationTests.nonstandardLoggingStopsBeforePasswordSql()",
            "io.github.minokim.lumiawiki.BootstrapInitializationTests.missingInputFailsBeforeDatabaseWrites()",
            "io.github.minokim.lumiawiki.BootstrapInitializationTests.initializationSeparatesRolesAndSpringConnections(CapturedOutput)",
            "io.github.minokim.lumiawiki.BootstrapInitializationTests.lateSqlFailureRollsBackRolesAndPrivilegesWithoutSecretOutput()"
          ]
        },
        "manifest": {
          ".codex/hooks.json": "816cb983d2faded1df2b58fc7da4b371c5990800df09768b324a8674448e31d4",
          ".env.example": "251762fa2a24a1d6937c1167ed27fd0dfa622859b084c21154df41366bb1aa5c",
          ".gitattributes": "4437511f6b3b866745490f0fcd2332d1e6194980fc028232ce0a84cec608d85b",
          "backend/build.gradle": "52b40fbbcdbb75b4ee5d5997811157a0ed61562cbd87c9eb6c3d859a88dd7960",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/resources/application-local.yaml": "3fe6ad5fdaa38b33adb58f86c546ee9f8f76b15bca91eaf0149aec9120c1af44",
          "backend/src/main/resources/application.yaml": "d10d1ef05ddbec053c30bf2bc705e4c5f19a2b688baccd61a4f48af556bb40e0",
          "backend/src/test/java/io/github/minokim/lumiawiki/BootstrapInitializationTests.java": "c81b36bcc87b65440efb5afda465dd65cb5364a0992fc1542b2004a37ec76838",
          "backend/src/test/resources/application-test.yaml": "e6aa7eb8da29c749b63e7330c634631d82f8710dc4fb6dee5ef883df1ce12e72",
          "backend/src/test/resources/db/bootstrap-migration/V1__bootstrap_test_probe.sql": "9dc33f07fd9884db7bea2b8990976681a9e11b8e4d0d8571f2530ebbe3935df0",
          "compose.yaml": "f850977af63aa8c754e5f81d0ba9099b2d167105a1e5a1a3c8bbdb97e2604ea8",
          "db/bootstrap/10-prepare-roles.sh": null,
          "db/bootstrap/sql/prepare-roles.sql": null,
          "frontend/package-lock.json": "e54e76e4ab1a402d4df0827152d1bf5c62142cd59e2798518b7ed2715931fc97",
          "frontend/package.json": "aae2e6358d704e1807f860f58272e3f8024cfdc092860bd0b0b4f7d58e76a228",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "2e55a2050f22641deaad0ac4b9b6723ad76aadab22ab037b9d38b1697a458367",
          "frontend/vitest.config.mjs": "f07e4974ad24bc562f5a975e8af587eb6fdfb402863825c718cfdf9a8b684eec",
          "package-lock.json": "539f24e43b65266883d2aa1a83428d75484cf059eeedcedf4043d09dc6d8a5e3",
          "package.json": "0e57b51524c8151aafb0155a93c5f61c30901819bde6cee895c0106f6dfcab85",
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c",
          "scripts/verify-bootstrap.mjs": "83a304c71c7a7d72a3254540cb9ca0c78f0b3a208315f76d711da1d195d6b92e"
        },
        "ok": false
      },
      "final": {
        "runId": "4e818e3754a44fdfa62260a51b8105ed",
        "started": 1794556869.97578,
        "finishedAt": 1794556899.9794614,
        "command": [
          "backend/gradlew.bat",
          "-p",
          "backend",
          "integrationTest",
          "--tests",
          "io.github.minokim.lumiawiki.BootstrapInitializationTests",
          "--console=plain",
          "--no-daemon",
          "-PtddReportDir={report}",
          "--max-workers=2",
          "-Dorg.gradle.jvmargs=-Xms64m -Xmx256m -XX:MaxMetaspaceSize=256m"
        ],
        "exitCode": 0,
        "result": {
          "tests": 4,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "names": [
            "io.github.minokim.lumiawiki.BootstrapInitializationTests.nonstandardLoggingStopsBeforePasswordSql()",
            "io.github.minokim.lumiawiki.BootstrapInitializationTests.missingInputFailsBeforeDatabaseWrites()",
            "io.github.minokim.lumiawiki.BootstrapInitializationTests.initializationSeparatesRolesAndSpringConnections(CapturedOutput)",
            "io.github.minokim.lumiawiki.BootstrapInitializationTests.lateSqlFailureRollsBackRolesAndPrivilegesWithoutSecretOutput()"
          ],
          "failedNames": []
        },
        "manifest": {
          ".codex/hooks.json": "816cb983d2faded1df2b58fc7da4b371c5990800df09768b324a8674448e31d4",
          ".env.example": "e61888b5706e93834e5fda74ae616afbeff3a56c4f8a4e1357d8ad818517cd5b",
          ".gitattributes": "4437511f6b3b866745490f0fcd2332d1e6194980fc028232ce0a84cec608d85b",
          "backend/build.gradle": "52b40fbbcdbb75b4ee5d5997811157a0ed61562cbd87c9eb6c3d859a88dd7960",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/resources/application-local.yaml": "e161d9789956b24211bc886419f0d2791c634be0238e82678a3575fbeeb46144",
          "backend/src/main/resources/application.yaml": "d10d1ef05ddbec053c30bf2bc705e4c5f19a2b688baccd61a4f48af556bb40e0",
          "backend/src/test/java/io/github/minokim/lumiawiki/BootstrapInitializationTests.java": "c81b36bcc87b65440efb5afda465dd65cb5364a0992fc1542b2004a37ec76838",
          "backend/src/test/resources/application-test.yaml": "e6aa7eb8da29c749b63e7330c634631d82f8710dc4fb6dee5ef883df1ce12e72",
          "backend/src/test/resources/db/bootstrap-migration/V1__bootstrap_test_probe.sql": "9dc33f07fd9884db7bea2b8990976681a9e11b8e4d0d8571f2530ebbe3935df0",
          "compose.yaml": "9e00c759b70fdb0fb2981de14a0e57d58428139baae9d22e8b2f8c0b165e8c34",
          "db/bootstrap/10-prepare-roles.sh": "832e9921588251e3a658fadc276ff7d3b46a46b110c45ae7a16cd4eb7819914a",
          "db/bootstrap/sql/prepare-roles.sql": "160a624d9577848f6e61404ad3e52791c6a395af56186fec08e852f3f88ff8d4",
          "frontend/package-lock.json": "e54e76e4ab1a402d4df0827152d1bf5c62142cd59e2798518b7ed2715931fc97",
          "frontend/package.json": "aae2e6358d704e1807f860f58272e3f8024cfdc092860bd0b0b4f7d58e76a228",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "2e55a2050f22641deaad0ac4b9b6723ad76aadab22ab037b9d38b1697a458367",
          "frontend/vitest.config.mjs": "f07e4974ad24bc562f5a975e8af587eb6fdfb402863825c718cfdf9a8b684eec",
          "package-lock.json": "539f24e43b65266883d2aa1a83428d75484cf059eeedcedf4043d09dc6d8a5e3",
          "package.json": "0e57b51524c8151aafb0155a93c5f61c30901819bde6cee895c0106f6dfcab85",
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c",
          "scripts/verify-bootstrap.mjs": "5745c67e3f1b56fe0383244a67d9db60c88fc2293aababab988351d2d5a7806c"
        },
        "ok": true
      }
    },
    {
      "id": "isolated-bootstrap-validation",
      "kind": "correction",
      "spec": "3136d90cd5894d1229046a26da76f68e00dc79404e1ae4f0e4bccb9e89b486b7",
      "worktree": "f8f58622827de84fd0e6",
      "finished": true,
      "baseline": "0239caae788f1724547579eae46f4caa6eb3df71",
      "task": "work/records/phase-001/issue-43/artifacts/task-001-bootstrap-verification.md",
      "final": {
        "runId": "aee6d1ad2a0f4d2699ede7611958bb31",
        "started": 1794557139.892559,
        "finishedAt": 1794557180.0619085,
        "command": [
          "backend/gradlew.bat",
          "-p",
          "backend",
          "integrationTest",
          "--tests",
          "io.github.minokim.lumiawiki.BootstrapInitializationTests",
          "--console=plain",
          "--no-daemon",
          "-PtddReportDir={report}",
          "--max-workers=2",
          "-Dorg.gradle.jvmargs=-Xms64m -Xmx256m -XX:MaxMetaspaceSize=256m"
        ],
        "exitCode": 0,
        "result": {
          "tests": 4,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "names": [
            "io.github.minokim.lumiawiki.BootstrapInitializationTests.nonstandardLoggingStopsBeforePasswordSql()",
            "io.github.minokim.lumiawiki.BootstrapInitializationTests.missingInputFailsBeforeDatabaseWrites()",
            "io.github.minokim.lumiawiki.BootstrapInitializationTests.initializationSeparatesRolesAndSpringConnections(CapturedOutput)",
            "io.github.minokim.lumiawiki.BootstrapInitializationTests.lateSqlFailureRollsBackRolesAndPrivilegesWithoutSecretOutput()"
          ],
          "failedNames": []
        },
        "manifest": {
          ".codex/hooks.json": "816cb983d2faded1df2b58fc7da4b371c5990800df09768b324a8674448e31d4",
          ".env.example": "e61888b5706e93834e5fda74ae616afbeff3a56c4f8a4e1357d8ad818517cd5b",
          ".gitattributes": "4437511f6b3b866745490f0fcd2332d1e6194980fc028232ce0a84cec608d85b",
          "backend/build.gradle": "52b40fbbcdbb75b4ee5d5997811157a0ed61562cbd87c9eb6c3d859a88dd7960",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/resources/application-local.yaml": "e161d9789956b24211bc886419f0d2791c634be0238e82678a3575fbeeb46144",
          "backend/src/main/resources/application.yaml": "d10d1ef05ddbec053c30bf2bc705e4c5f19a2b688baccd61a4f48af556bb40e0",
          "backend/src/test/java/io/github/minokim/lumiawiki/BootstrapInitializationTests.java": "2c121ddb8ab2ae18455b50153a23e0f23aa94ed5e0d3166d84f21f229417e359",
          "backend/src/test/resources/application-test.yaml": "e6aa7eb8da29c749b63e7330c634631d82f8710dc4fb6dee5ef883df1ce12e72",
          "backend/src/test/resources/db/bootstrap-migration/V1__bootstrap_test_probe.sql": "9dc33f07fd9884db7bea2b8990976681a9e11b8e4d0d8571f2530ebbe3935df0",
          "compose.yaml": "9e00c759b70fdb0fb2981de14a0e57d58428139baae9d22e8b2f8c0b165e8c34",
          "db/bootstrap/10-prepare-roles.sh": "832e9921588251e3a658fadc276ff7d3b46a46b110c45ae7a16cd4eb7819914a",
          "db/bootstrap/sql/prepare-roles.sql": "160a624d9577848f6e61404ad3e52791c6a395af56186fec08e852f3f88ff8d4",
          "frontend/package-lock.json": "e54e76e4ab1a402d4df0827152d1bf5c62142cd59e2798518b7ed2715931fc97",
          "frontend/package.json": "aae2e6358d704e1807f860f58272e3f8024cfdc092860bd0b0b4f7d58e76a228",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "2e55a2050f22641deaad0ac4b9b6723ad76aadab22ab037b9d38b1697a458367",
          "frontend/vitest.config.mjs": "f07e4974ad24bc562f5a975e8af587eb6fdfb402863825c718cfdf9a8b684eec",
          "package-lock.json": "539f24e43b65266883d2aa1a83428d75484cf059eeedcedf4043d09dc6d8a5e3",
          "package.json": "0e57b51524c8151aafb0155a93c5f61c30901819bde6cee895c0106f6dfcab85",
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c",
          "scripts/verify-bootstrap.mjs": "a401091925ed2d02f95540a38a2cbced924e2c1520eb66556bcc08a8972974be"
        },
        "ok": true
      }
    },
    {
      "id": "database-documentation-scope",
      "kind": "behavior",
      "spec": "941bb7f0f0554158e0b676c8f4bf8b63dd2a53af13c8557f7df1c697086d16ab",
      "worktree": "f8f58622827de84fd0e6",
      "baseline": "0239caae788f1724547579eae46f4caa6eb3df71",
      "task": "work/records/phase-001/issue-43/artifacts/task-001-bootstrap-verification.md",
      "finished": true,
      "red": {
        "runId": "7f917cd65e1f43bba36feb481ccd28fc",
        "started": 1794558173.7462204,
        "finishedAt": 1794558174.4003465,
        "command": [
          "node",
          "--test",
          "--test-reporter=junit",
          "--test-reporter-destination={report}",
          "scripts/quality-db-docs.test.mjs"
        ],
        "exitCode": 1,
        "result": {
          "tests": 3,
          "failures": 3,
          "errors": 0,
          "skipped": 0,
          "names": [
            "test.database Markdown has a format scope without enabling SQL formatting",
            "test.docs collection includes database Markdown and excludes raw evidence",
            "test.database documentation changes select only documentation checks"
          ],
          "failedNames": [
            "test.database Markdown has a format scope without enabling SQL formatting",
            "test.docs collection includes database Markdown and excludes raw evidence",
            "test.database documentation changes select only documentation checks"
          ]
        },
        "manifest": {
          ".codex/hooks.json": "816cb983d2faded1df2b58fc7da4b371c5990800df09768b324a8674448e31d4",
          ".gitattributes": "4437511f6b3b866745490f0fcd2332d1e6194980fc028232ce0a84cec608d85b",
          "backend/build.gradle": "52b40fbbcdbb75b4ee5d5997811157a0ed61562cbd87c9eb6c3d859a88dd7960",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/resources/application.yaml": "d10d1ef05ddbec053c30bf2bc705e4c5f19a2b688baccd61a4f48af556bb40e0",
          "backend/src/test/resources/application-test.yaml": "e6aa7eb8da29c749b63e7330c634631d82f8710dc4fb6dee5ef883df1ce12e72",
          "frontend/package-lock.json": "e54e76e4ab1a402d4df0827152d1bf5c62142cd59e2798518b7ed2715931fc97",
          "frontend/package.json": "aae2e6358d704e1807f860f58272e3f8024cfdc092860bd0b0b4f7d58e76a228",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "2e55a2050f22641deaad0ac4b9b6723ad76aadab22ab037b9d38b1697a458367",
          "frontend/vitest.config.mjs": "f07e4974ad24bc562f5a975e8af587eb6fdfb402863825c718cfdf9a8b684eec",
          "package-lock.json": "539f24e43b65266883d2aa1a83428d75484cf059eeedcedf4043d09dc6d8a5e3",
          "package.json": "0e57b51524c8151aafb0155a93c5f61c30901819bde6cee895c0106f6dfcab85",
          "scripts/quality-db-docs.test.mjs": "737f37ca0275acb010da0c7ce6521375dbb7f44b5c419a4dc611560c1cf43e59",
          "scripts/quality/paths.mjs": "1f38ff7aa54b3aaa1fdfcd2fa0ec8f75fb62134e80fe5d5ff54e8e31eaf0df53",
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": false
      },
      "final": {
        "runId": "97c2fadbc4ba469fa74fe261e4c8e0ec",
        "started": 1794558189.4130065,
        "finishedAt": 1794558189.9142768,
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
      "id": "database-documentation",
      "kind": "correction",
      "spec": "a1351d75f2d809e749a3e1e720ab2c70cc917bbd1ba28df45ab9f3cb53c4db50",
      "worktree": "f8f58622827de84fd0e6",
      "finished": true,
      "baseline": "0239caae788f1724547579eae46f4caa6eb3df71",
      "task": "work/records/phase-001/issue-43/artifacts/task-001-bootstrap-verification.md",
      "final": {
        "runId": "28638bf2267c419b9626ffa85d90d8ac",
        "started": 1794558450.0412772,
        "finishedAt": 1794558450.5796237,
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
          "db/README.md": "83400907a7c7cfb99ce180bbef8b627c41183d3c8d00a9cee69a0a99e52e51d3",
          "db/bootstrap/README.md": "4fca2394fd0b19cebedbdd09ec8b9e64b7cda0da429ea1cf0e83eb46bfbc77d5",
          "db/migration/README.md": "c8573306093b26a4280ce5b75018311c96a382d4186ddeca1a18740deeaa7543",
          "db/model/common-tables.md": "9dd0864d8479e014e0a3e756a34a3cdc67d944232bd5da4303d34324c902c523",
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
      "id": "database-model-decisions",
      "kind": "correction",
      "spec": "fe4f6390cdaf34c8695b520f052f75e1ad110a48f2a2d8598c404d1e88d7cc95",
      "worktree": "f8f58622827de84fd0e6",
      "finished": true,
      "baseline": "0239caae788f1724547579eae46f4caa6eb3df71",
      "task": "work/records/phase-001/issue-43/artifacts/task-001-bootstrap-verification.md",
      "final": {
        "runId": "c7fb8cf34d4b49d297f2434f70d38d29",
        "started": 1794558763.99371,
        "finishedAt": 1794558764.4804015,
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
          "db/model/common-tables.md": "bb70a5b875caccf03dfdccc85b58b5d50c636b5be8b91a57a58c24d671c6a159",
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
      "id": "checkpoint-db-documentation",
      "kind": "correction",
      "spec": "7320954481b1d87d082018ede1cc13f3dc3014268de4565cb7b3a9154de50499",
      "worktree": "f8f58622827de84fd0e6",
      "finished": true,
      "baseline": "0239caae788f1724547579eae46f4caa6eb3df71",
      "task": "work/records/phase-001/issue-43/artifacts/task-001-bootstrap-verification.md",
      "final": {
        "runId": "a65768165c844454b10a20f899c9fb9d",
        "started": 1794565556.938158,
        "finishedAt": 1794565557.6920722,
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
          "db/README.md": "0049f6c5aa6653fe219fa511fae42e36af86f959c9a108ce96199ff5eff24f63",
          "db/bootstrap/README.md": "4fca2394fd0b19cebedbdd09ec8b9e64b7cda0da429ea1cf0e83eb46bfbc77d5",
          "db/migration/README.md": "e8da0f8d9b35412336672cee479d127e63e9e3199463370d06761d7deb0115f0",
          "db/model/common-tables.md": "ac8d9230fa19363c4d4ac15141eb98afc0067f7417cb8ddb341b1025f2efe869",
          "db/model/consumer-references.md": "809f2cd8b9eebb470588c9cae3aa2da82659e58657e1738f50fd08d0a038ff40",
          "db/model/names-and-dates.md": "3e5f1237988113bf5e1e9616724c3a008db3b4b5d92b535f5d022a9c54d89328",
          "db/model/permissions-and-installation.md": "2ee6557fa657483a874c017824d5dda881f70d95aa8a3d07b61742a40ce9b5a0",
          "db/model/ranges-and-uniqueness.md": "15092b5bd995af2b49494de9b556ab8a434cdfd1bb643962d2a63a29de1f372c",
          "db/model/region-layout.md": "4a776ac7a79e013c64e50d455685ba425a648575203bc476bac7368af6542f6f",
          "db/model/table-layout.md": "97f4222b9673831896dff98cab19bca3d8c49e7c070d989f34ced0506c82c01f",
          "db/model/writes-and-checks.md": "e61edab6e4f03056fa662d852726ecd781a117afe7744fa93237a50042bcaa3a",
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
