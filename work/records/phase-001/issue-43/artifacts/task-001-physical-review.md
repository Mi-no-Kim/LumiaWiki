# Task 43-001 — 물리 구조·갱신·권한 검토

<a id="current"></a>

담당: [Task 43-001](../task-001.md#summary). 공통 표와 지역 이력의 물리 관계·제약·갱신·업무 권한을 한 검토 묶음으로 준비한다. 새 Task를 만들지 않는다.

## 범위와 확인 조건

기존 M1~M3·D1~D4와 8개 표·U-A/A-A·C-A/L-A/M-A, region 작업용 이름의 필수·유일성·업무 UPDATE를 유지한다. N1~N5와 메이저/마이너 각각 0~99 CHECK·패치 정렬 UNIQUE를 확정했다. 번호 범위는 사용자 확인을 근거로 하며 실제 자료를 조사한 것은 아니다. 실제 제약별 이름·정확한 실행 환경은 초안/생성 직전 확인에서 제시한다. 실제 자료·개인 .env·기존 DB/볼륨을 조회하지 않고 SQL/매핑 파일·테이블·스키마를 생성하지 않는다.

**새 테이블 생성 직전에 전체 구조를 다시 제시해 사용자 확인을 받는다.** 초기 설계 방향의 선택을 생성 승인으로 사용하지 않는다. 해당 구조의 격리 DB 생성/마이그레이션 검증도 이 확인 뒤에 수행한다. [최종 구조 확인 절차](../../../../../db/migration/README.md#precreation-confirmation)를 따른다.

## 검토 문서

| 내용 | 문서 |
| --- | --- |
| 공통 6개 표의 필드·NULL·관계·제약 후보 | [공통 표 배치](../../../../../db/model/table-layout.md#current) |
| 지역의 지속 ID·패치 이력·신규 표 후보/대안 | [지역 구조](../../../../../db/model/region-layout.md#current) |
| 업무 단위·참조 검사·국소 동시성·실패 | [갱신과 검사](../../../../../db/model/writes-and-checks.md#current) |
| 업무 권한·설치 배치·보호 대상·생성 전 확인 | [권한과 설치](../../../../../db/model/permissions-and-installation.md#current) |

## 확정 계약과 남은 준비

- R-A 확정: 지역 전체 지도 구성 버전+소속 행 두 표를 추가해 총 8개 표로 구성한다. 구성 변화가 없는 패치는 앞선 구성을 사용한다. 조회 우선·완전한 구성/미확인 구별·구성 안 유일성 검사를 위한 선택이다.
- U-A 확정: 일반 UNIQUE는 즉시 검사하고 단건 수정을 기본으로 한다. 등급/패치 번호 여러 행 자리교환은 초기 범위에서 제외한다. L-A는 패치/지도 기준 표와 종류 계층의 필요한 잠금으로 관련 수정의 순서를 맞춘다. 과거 화면 입력의 자동 검출과는 구별한다.
- A-A 확정: 교정용 소속 행 DELETE만 허용하며 공통 대상·지도 버전의 일반 삭제는 허용하지 않는다. C-A의 region.id FK, M-A의 새 두 표를 포함한 PK 보호/한 파일 설치를 적용하며 실제 GRANT/DDL 실행은 보류한다.
- 저장 구조 확정: weapon_type.category_id NOT NULL FK + UNIQUE, 종류의 UNIQUE NULLS NOT DISTINCT (parent_id, name), 일반 FK의 ON UPDATE NO ACTION과 지도 2개 표의 열/키·유일성·적용 범위를 유지한다. region.display_name TEXT NOT NULL·UNIQUE와 빈값 거부·작업용 UPDATE를 적용하며 공개 이름과 구별한다.
- N1~N5 확정: 시즌/패치 이름의 추가 UNIQUE 없음·중복 검사 이름의 C 비교·서비스/저장소와 격리 통합 테스트/재현 절차·기존 400/404/500 및 업무 롤백/기존 설정의 대기·명시적 제약 이름/새 빈 환경 V1 한 파일/최초 격리 DB 검증을 채택했다. 새 HTTP API·관리 화면과 추가 시간 제한/자동 재시도는 초기 범위에 넣지 않는다.
- 번호 계약: 사용자 확인으로 메이저·마이너 각각 0~99와 패치 정렬 UNIQUE를 저장 제약에 반영한다. 0~99 밖 입력은 자동 변환하지 않고 거부/확인한다. 실제 자료·DB 작업·구현 파일 생성은 보류하며 생성 직전 전체 구조/대상 확인을 유지한다.

<a id="verification"></a>

## 확인 결과

- 문서 41개·참조 630개·담당 미정 12개 묶음 검사 오류 없음. Task/Issue 100줄 초과는 기존 계획을 유지하는 안내 경고다.
- 합성 자료로 R-A의 시작/다음 경계, 이전 구성 재사용, 첫 구성 전 미확인/명시된 빈 구성, 지역 미등장·구성별 중복 범위와 교정 영향 범위를 확인했다. 실제 조회 SQL·트랜잭션·잠금·권한은 실행하지 않았다.
- C-A의 FK 존재와 Q의 등장 검사가 다른 점을 대조했다. 비조정 경합의 반례와 두 순차 처리 순서에서 뒤의 작업이 최신 상태로 거부/수용되는 합성 사례를 확인했다. 이는 개념 검토이며 실제 DB 잠금/격리 실행 증거가 아니다. L-A의 서로 다른 행 쓰기 대기 가능성·과거 화면 입력 자동 검출과의 구별도 문서에 반영했다.
- 자체 검수에서 필드/NULL·개수/FK·유일성·기본값·업무 경계·설치 순서와 기존 합의를 대조했다. 삭제/재작성 교정과 소속 행 직접 FK의 충돌은 C-A 지속 지역 FK 계약으로 피하고, 동일 Q의 소속은 서비스/L-A로 검사한다. 새로운 직접 FK 요구는 구조/교정 계약 변경 대상으로 구별했다.
- 실제 생성 직전 전체 구조 재확인 조건을 DB/마이그레이션 안내·Task·부모 Issue·현황에 연결했다. R-A/U-A/A-A·C-A/L-A/M-A를 설계 선택으로 반영했으며 생성 승인은 미확인이다.
- 실행기/초기 준비/접속 설정 7개 입력의 지문이 기존 실행 근거와 같고 제품 마이그레이션 SQL은 0개임을 확인했다. DB 접속·자료/개인 .env 조회·SQL/매핑 파일 생성·테이블/스키마 생성은 하지 않았다.
- region 작업용 이름의 필수·빈값/중복 금지·업무 UPDATE와 공개 API/화면 제외 조건을 사용자 응답과 DB/기준/Task/부모 기록에 대조했다. 이름 수정이 지도 이력·획득 참조를 바꾸지 않는 계약을 확인했으며 실제 DB/응답 검증은 수행하지 않았다.
- N1~N5와 사용자 확인의 번호 0~99를 저장/갱신/설치·기준·Task/부모 기록에 대조했다. 확정 정책과 실제 제약/자료 검증을 구별하고 미정 목록에서 재선택 대상은 제외했다. 공개 API 추가·기존 DB 적용·보류 해제는 포함하지 않았다.
- DB 문서의 포맷/수집·분류 3건은 아래 문서 예외의 확인으로 연결한다. 실제 테이블 설치/DB 검증은 최종 구조 확인 뒤에만 수행한다.

<!-- tdd-plan -->

```json
{
  "schema": 1,
  "cycles": [
    {
      "id": "physical-review-documents",
      "kind": "correction",
      "reason": "db 경로 Markdown의 문서 예외다. 승인된 정책과 새 물리/갱신/권한 후보 및 테이블 생성 전 재확인 조건만 작성하며 런타임·SQL·DB를 변경하지 않는다.",
      "targets": [
        "db/model/table-layout.md",
        "db/model/region-layout.md",
        "db/model/writes-and-checks.md",
        "db/model/permissions-and-installation.md",
        "db/model/common-tables.md",
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
      "id": "reference-lock-installation-review",
      "kind": "correction",
      "reason": "후속 지역 참조·국소 잠금·새 PK 보호·설치 후보를 DB Markdown에서 구체화한다. 사용자 미확인 선택은 후보로 두며 실제 SQL/매핑·테이블/스키마·DB 상태는 변경하지 않는다.",
      "targets": [
        "db/model/consumer-references.md",
        "db/model/writes-and-checks.md",
        "db/model/permissions-and-installation.md",
        "db/model/region-layout.md",
        "db/model/table-layout.md",
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
      "id": "region-work-label-public-output",
      "kind": "correction",
      "reason": "DB Markdown 문서 예외다. 승인된 작업용 표시 이름의 공개 API/화면 출력 제외 조건을 명시하며 실제 코드·SQL·DB는 변경하지 않는다.",
      "targets": [
        "db/model/table-layout.md"
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
      "id": "region-work-label-contract",
      "kind": "correction",
      "reason": "DB Markdown 문서 예외다. 8개 표 구조의 사용자 승인과 region 작업용 표시 이름을 문서에 반영하며 실제 자료·SQL/매핑·테이블/스키마·DB는 변경하지 않는다.",
      "targets": [
        "db/model/table-layout.md",
        "db/model/region-layout.md",
        "db/model/permissions-and-installation.md",
        "db/model/common-tables.md",
        "db/model/consumer-references.md"
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
      "id": "implementation-contract-decisions",
      "kind": "correction",
      "reason": "DB Markdown 문서 예외다. 승인된 N1~N5와 사용자 확인의 패치 번호 0~99를 저장·갱신·검증/설치 계약에 반영한다. 실제 자료·SQL/Java 파일·DB 상태는 변경하지 않는다.",
      "targets": [
        "db/model/common-tables.md",
        "db/model/ranges-and-uniqueness.md",
        "db/model/table-layout.md",
        "db/model/region-layout.md",
        "db/model/writes-and-checks.md",
        "db/model/permissions-and-installation.md",
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
      "id": "physical-review-documents",
      "kind": "correction",
      "spec": "d4befa204f7780fa16ef7fb9a0692f311809e1911d3c8861a2054829733b6ef5",
      "worktree": "f8f58622827de84fd0e6",
      "finished": true,
      "baseline": "0239caae788f1724547579eae46f4caa6eb3df71",
      "task": "work/records/phase-001/issue-43/artifacts/task-001-physical-review.md",
      "final": {
        "runId": "c2233d5e596d436fb3f4162f1e2db3a0",
        "started": 1794560759.9096994,
        "finishedAt": 1794560760.5268571,
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
          "db/migration/README.md": "77c309072496bf535392e33047141b768e48968620ed177a626d149062f9baec",
          "db/model/common-tables.md": "25cab96223aa996085e0e09702ec08b075d936d091cb4ec89f162cbd426ae88f",
          "db/model/permissions-and-installation.md": "9446e3d921ea385cd69c704902d319dd0a7aa580148158bcc2ed5790542f9e62",
          "db/model/region-layout.md": "3b4cfe9227fc9e9d042e0fb6e3197761e50666d0fcb83ece6eea426473cb98c6",
          "db/model/table-layout.md": "b3db1414378c9b72d5b0d9c515d5bd2c1fbd4eb8b9895b9766c3928785972232",
          "db/model/writes-and-checks.md": "eaa61f9e1cc0446153fca80794f228530e15544c2701f25631be525d594d80a1",
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
      "id": "reference-lock-installation-review",
      "kind": "correction",
      "spec": "fabc22057d438e3f61114abbb6be1a4538a237e1002a84445800a299b515a4b0",
      "worktree": "f8f58622827de84fd0e6",
      "finished": true,
      "baseline": "0239caae788f1724547579eae46f4caa6eb3df71",
      "task": "work/records/phase-001/issue-43/artifacts/task-001-physical-review.md",
      "final": {
        "runId": "87314d19cc554077820c79312ac79b15",
        "started": 1794562021.0077837,
        "finishedAt": 1794562021.5496554,
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
          "db/model/common-tables.md": "978d028b864865ddc8d9999343adb9216f5584b94d9f505864d28069dc340d5b",
          "db/model/consumer-references.md": "110bb2de0c206d300d5b24470c5301a52135d8edf5b32bfa1052dbf75885eee1",
          "db/model/permissions-and-installation.md": "79e0c48f65331242a84b307d3ec050e1d65ad0652160a5d9033f58000ea05164",
          "db/model/region-layout.md": "aff0001a934316805df7009af1d7afb3df58e11eebab8d45af1e44d37b4b5412",
          "db/model/table-layout.md": "d0b97c373ff25841e0df64e69ce868571c923db1b9b00247b57a92760137b5f1",
          "db/model/writes-and-checks.md": "3a306d2b7fe642913ea533a468b2a755f0bd1d40752524274a5f9422c219d558",
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
      "id": "region-work-label-contract",
      "kind": "correction",
      "spec": "fc14cd508cdf6e3cba252aafdf2db0d37878a5723a56c806ae30358378af07bd",
      "worktree": "f8f58622827de84fd0e6",
      "finished": true,
      "baseline": "0239caae788f1724547579eae46f4caa6eb3df71",
      "task": "work/records/phase-001/issue-43/artifacts/task-001-physical-review.md",
      "final": {
        "runId": "2c2bdbf2b2544903b3fa86432bb02160",
        "started": 1794563366.782373,
        "finishedAt": 1794563367.4099133,
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
          "db/model/common-tables.md": "f709b3ed9329494f410fc34207b5ef7558404343dc6503ad769aea000a40274e",
          "db/model/consumer-references.md": "809f2cd8b9eebb470588c9cae3aa2da82659e58657e1738f50fd08d0a038ff40",
          "db/model/permissions-and-installation.md": "4cadc7dd91984e3366f8934aafa5c36d5418071a7bc4c2a1812b9cbd63bcdd37",
          "db/model/region-layout.md": "f89f9c14b0922d08b4d43b18c56b8c83790ea29d0f6d46884acb6a352d5a9407",
          "db/model/table-layout.md": "d649ebea7f353236ad7aa58bc74826587952dc9bf7f285b26c959842f8854bd2",
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
      "id": "region-work-label-public-output",
      "kind": "correction",
      "spec": "7a525824a069818327f303cb945b1cbaf2ff14c4e80eca032875cad9acd8ccdd",
      "worktree": "f8f58622827de84fd0e6",
      "finished": true,
      "baseline": "0239caae788f1724547579eae46f4caa6eb3df71",
      "task": "work/records/phase-001/issue-43/artifacts/task-001-physical-review.md",
      "final": {
        "runId": "e07a9b9e4ef34127811be0a7c409d37b",
        "started": 1794563448.1527805,
        "finishedAt": 1794563448.7446737,
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
          "db/model/table-layout.md": "527e1f64cd9b78b38de63cf1a6ead52061dd139659b9d917263169886d715d13",
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
      "id": "implementation-contract-decisions",
      "kind": "correction",
      "spec": "b8c34e70301dceaf9da326e15f35973aaa523c1efb0bc18a1db49b325d0edf8d",
      "worktree": "f8f58622827de84fd0e6",
      "finished": true,
      "baseline": "0239caae788f1724547579eae46f4caa6eb3df71",
      "task": "work/records/phase-001/issue-43/artifacts/task-001-physical-review.md",
      "final": {
        "runId": "5e306921970f4d85b66b0c8ae020caf8",
        "started": 1794564690.903392,
        "finishedAt": 1794564691.5084226,
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
          "db/migration/README.md": "e8da0f8d9b35412336672cee479d127e63e9e3199463370d06761d7deb0115f0",
          "db/model/common-tables.md": "ac8d9230fa19363c4d4ac15141eb98afc0067f7417cb8ddb341b1025f2efe869",
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
