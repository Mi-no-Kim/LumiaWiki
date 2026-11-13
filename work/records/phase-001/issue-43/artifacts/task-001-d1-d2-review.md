# Task 43-001 — D1·D2 검토

<a id="current"></a>

담당: [Task 43-001](../task-001.md#summary). 기존 작업의 저장 계약 보완이며 새 Task를 만들지 않는다. [D1 이름·날짜](../../../../../db/model/names-and-dates.md#current)와 [D2 범위·중복](../../../../../db/model/ranges-and-uniqueness.md#current)을 하나의 검토 묶음으로 사용한다.

## 범위와 상태

기존 M1~M3·D3 일대일 대응·D4 지속 지역 ID/게임 패치 이력과 D1의 5개 메타정보 NULL 등록·D2-N의 지정 목록/조회 패치 중복 금지를 유지한다. 메이저·마이너 각각 0~99는 사용자 확인을 받았고 CHECK·패치 정렬 UNIQUE를 적용한다. N1의 추가 시즌/패치 이름 UNIQUE 없음과 N2의 C 비교를 채택했다. 실제 목록·누락/중복 사례 조사나 SQL/매핑 파일·테이블/스키마 생성은 수행하지 않는다.

## 확인할 결과

- D1: 미확인 값과 진행 중/해당 없음의 구별, 필수값 유지, 명시 조회와 현재/예정 판정의 경계.
- D2: 기존 업무 키와 새 제약 후보 구별, 정렬식의 가상 충돌/순서 사례, 이름·순서 유일성의 비교 범위.
- 공통: 확정한 정책·검토 기준·실제 입력/물리 상세의 구별과 담당/결정 시점, 목적별 문서·참조 일치.

<a id="verification"></a>

## 확인 결과

- 문서 35개·참조 572개·담당 미정 12개 묶음 검사 오류 없음. 기존 Task/Issue의 100줄 초과는 안내 경고다. 변경 문서 형식도 확인했다.
- 가상 산술 3사례의 충돌/역전과 두 시즌의 0~99 조합 20,000개에서 정렬값 유일성·시즌 사이 순서를 확인했다. 실제 게임 번호 범위의 검증과 구별한다.
- 기존 실행 근거와 대조해 실행기·초기 준비·접속 설정 7개 입력의 내용 지문이 일치함을 확인했다. 제품 마이그레이션 SQL은 0개다. 실제 DB 접속·테이블/스키마 생성·자료 조회·SQL/매핑 파일 생성은 하지 않았다.
- 자체 검수에서 기존 합의와 새 제안을 구별하고 미확인 값의 의미·번호/정렬의 충돌·지역 이력의 비교 범위·담당/입력/시점을 대조했다. D1 NULL 등록·D2-P 검토 기준·D2-N의 중복 금지 범위를 사용자 응답대로 반영했다. 실제 입력 확인·제약 생성과 구별한다.
- DB Markdown의 포맷/수집·분류 3건은 아래 문서 예외의 확인으로 연결한다. 문서와 가상 산술 검사를 DB 동작 검증으로 보고하지 않는다.

<!-- tdd-plan -->

```json
{
  "schema": 1,
  "cycles": [
    {
      "id": "d1-d2-documentation",
      "kind": "correction",
      "reason": "db 경로의 Markdown을 편집 guard가 동작 대상으로 분류하므로 문서 작성 예외를 명시한다. D1/D2의 미확정 검토안과 안내 링크만 작성하며 런타임·SQL·DB 상태는 변경하지 않는다.",
      "targets": [
        "db/model/names-and-dates.md",
        "db/model/ranges-and-uniqueness.md",
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
      "id": "d1-d2-decisions",
      "kind": "correction",
      "reason": "사용자가 확인한 5개 메타정보 NULL 등록, 0~99/패치 정렬 UNIQUE 검토 기준, 지정한 목록/패치 안의 중복 금지를 Markdown에 반영한다. 실제 자료·SQL·런타임·DB 상태는 변경하지 않는다.",
      "targets": [
        "db/model/names-and-dates.md",
        "db/model/ranges-and-uniqueness.md",
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
      "id": "d1-d2-documentation",
      "kind": "correction",
      "spec": "756b4f5277b5a43e6da9151c2c8886516462191704ca9fbde77bf739f2599857",
      "worktree": "f8f58622827de84fd0e6",
      "finished": true,
      "baseline": "0239caae788f1724547579eae46f4caa6eb3df71",
      "task": "work/records/phase-001/issue-43/artifacts/task-001-d1-d2-review.md",
      "final": {
        "runId": "290fb37d380046828fb6a3f3eccd5101",
        "started": 1794559298.5848603,
        "finishedAt": 1794559299.2051322,
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
          "db/model/common-tables.md": "ae91ce1a36160fda448e129b71a236110ff4defd8e0979719fa247dfc63ea183",
          "db/model/names-and-dates.md": "36cd3e58d729a6956d05153ca81ec9241279248af6ce87ff9cf48262ead24ada",
          "db/model/ranges-and-uniqueness.md": "ee443170f4356295b21f5b0b48bb011aa942337826d9678fde3a1e12545eb9a2",
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
      "id": "d1-d2-decisions",
      "kind": "correction",
      "spec": "52e40c4cdf83777ce3cfbca0d11894d4853b3b8e0a4dd53f4be24f0052d1f4da",
      "worktree": "f8f58622827de84fd0e6",
      "finished": true,
      "baseline": "0239caae788f1724547579eae46f4caa6eb3df71",
      "task": "work/records/phase-001/issue-43/artifacts/task-001-d1-d2-review.md",
      "final": {
        "runId": "60500e5e61c04ec5a9ee173d89e18978",
        "started": 1794559637.0767303,
        "finishedAt": 1794559637.580533,
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
          "db/model/common-tables.md": "7a15baf4a511438cd0489392f9c7bf0536bdec2a055827bd984e6a2b77f76612",
          "db/model/names-and-dates.md": "3e5f1237988113bf5e1e9616724c3a008db3b4b5d92b535f5d022a9c54d89328",
          "db/model/ranges-and-uniqueness.md": "e085ce955501e9a0dee33ed65ad8da8fd3e12dbc075b8abd88705bfc4477021d",
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
