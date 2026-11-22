# Task 43-003 수행 기록

- Task: [43-003 제작·획득·배달 관계 저장/조회](../task-003.md#summary)
- 기록 기준: [Task 공통 절차](<../../../../../harness/Task 공통 절차.md#recording-proposal>)

<!-- execution-rule:recording
Task당 한 파일을 쓰고 이 주석은 머리말에 한 번만 둔다. 착수한 할 일은 구역 구조만 주석 없이 추가해 본문과 왕복 연결하고 실제 내용으로 채운다.
할 일의 태그·배정 조건에 따라 실제 조치·선택과 이유·근거를 남긴다. 파일 수정 없는 논의도 기록하고 제안·미결·합의·철회를 구별한다.
논의·사용자 결정은 실제 응답으로, AI 결정은 명시 위임·실제 선택으로 확인한다. 필수 논의를 생략하지 않는다.
확인은 계획·전달본을 참조하고 실제 대상·방법·관찰·판정·근거·한계를 남긴다. 변경본은 검증한 버전·범위를 식별하고 달라진 영향만 다시 확인한다.
진행·검수·수용에 필요한 결정은 Task에 결론·이유·조건·상세 링크를 남긴다. 공통 상세는 한 구역만 참조하며 잔여는 해당 할 일의 미해결·재개 조건이다.
보완·재시도는 같은 구역을 갱신한다. 식별자는 순서와 구별하고 삭제·분할·병합에도 수행·판단/실패 근거·당시 기준·본문 연결을 보존한다.
코드·diff·테스트 원문·명령별 로그를 복사·누적하지 않는다. 미발생 승인·결과나 단순 확인용 증명 파일을 만들지 않는다.
세부 작성 조건은 위 기록 기준을 따르고 생성 양식으로 돌아가지 않는다.
-->

<a id="work-equipment-slot"></a>

## 분류 기반 장착 부위 정정

- 할 일: [Task 수행계획](../task-003.md#work-equipment-slot)

- 조치·판단: [개정 전달본](task-003-assignment.md#equipment-slot-revision)에 따라 [V4](../../../../../db/migration/V4__derive_item_equipment_slot.sql)에서 `item_version.equipment_slot`을 제거했다. 장비 그룹과 부위를 `item_category.equipment_role`에 분류 ID의 역할로 두었다. V3의 표준 이름·계층에서 역할을 한 번 초기화하고, 새 분류는 등록 또는 장비 그룹으로 처음 이동할 때 역할을 정한다. 초기화된 역할은 이름 변경에도 유지한다. Spring 조회는 현재 계층을 한 SQL 문에서 읽고, 이미 방문한 ID에서 순회를 중단한다.
- 확인: 기존 코드의 이름 변경 회귀는 `v4-category-identity-red`에서 실패했다. 개정 후보 `v4-category-identity-verified`은 단위 43건, 격리 PostgreSQL 18.6 통합 21건, 포맷·JAR 검사를 통과했다. 빈 DB 설치·V3 갱신, 같은 ID의 장비 그룹·부위 이름 변경과 과거 버전 조회, 이미 읽은 상위 관계가 남은 트랜잭션에서의 동시 재배치를 확인했다. V4 SQL SHA-256은 `e8cf0bc352cc98d41ea1f534d41a35c4d05a4cafbd004c30089f596e5ce6e7dc`이며 JAR 내 바이트와 일치한다. 입력 SHA-256은 `3a6cf9be664838cb868617e9e73cbd0e5b99955bba6fd52dcccee04352d60396`다. V4 인덱스 17개 파일을 대조했고, 두 회귀의 실행 근거와 제출 범위를 별도 검수해 필수 결함이 없음을 확인했다.
- 잔여: 개발 DB 적용과 실제 자료 작업은 보류한다. 기존 분류명이 이미 표준 이름과 다르면 V4에서 역할을 자동으로 초기화할 수 없다.

## V4 커밋 훅 검증

이전 V4의 이름 기반 조회를 격리 사본에 재현해 이름 변경 회귀를 먼저 실행한다. 현재 코드로 복원해 같은 입력으로 다시 확인한다.

<!-- tdd-plan -->
```json
{
  "schema": 1,
  "cycles": [
    {
      "id": "v4-equipment-category-identity",
      "kind": "behavior",
      "expectation": "같은 분류 ID에서 부위 이름 변경 전후에 조회 결과가 유지된다.",
      "targets": [
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogErrors.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CommonCatalogStore.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/EquipmentCategoryRole.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/EquipmentSlot.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemCatalogService.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemCategory.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersion.java",
        "db/migration/V4__derive_item_equipment_slot.sql"
      ],
      "tests": [
        "backend/src/test/java/io/github/minokim/lumiawiki/catalog/CommonCatalogIntegrationTests.java",
        "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemCatalogServiceTests.java",
        "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemStorageMigrationTests.java"
      ],
      "command": [
        "backend/gradlew.bat",
        "-p",
        "backend",
        "-PtddReportDir={report}",
        "integrationTest",
        "--tests",
        "io.github.minokim.lumiawiki.catalog.CommonCatalogIntegrationTests.itemStoragePreservesEquipmentSlotsWhenCategoryNamesChange",
        "--offline"
      ],
      "adapter": "junit",
      "expectedFailures": [
        "io.github.minokim.lumiawiki.catalog.CommonCatalogIntegrationTests.itemStoragePreservesEquipmentSlotsWhenCategoryNamesChange()"
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
      "id": "v4-equipment-category-identity",
      "kind": "behavior",
      "spec": "90d843ccec25de03c5db9551dc4162b52776216e027d198eba6bcf9e35155aa2",
      "worktree": "7eaeb7d12ad4d31ab1d0",
      "baseline": "169c79c4757983d216201c8c9deebb8fdd86c150",
      "task": "work/records/phase-001/issue-43/artifacts/task-003-execution.md",
      "finished": true,
      "red": {
        "runId": "c438a30f495a457e9a5cf6704885c466",
        "started": 1795377505.7900796,
        "finishedAt": 1795377534.1968887,
        "command": [
          "backend/gradlew.bat",
          "-p",
          "backend",
          "-PtddReportDir={report}",
          "integrationTest",
          "--tests",
          "io.github.minokim.lumiawiki.catalog.CommonCatalogIntegrationTests.itemStoragePreservesEquipmentSlotsWhenCategoryNamesChange",
          "--offline"
        ],
        "exitCode": 1,
        "result": {
          "tests": 1,
          "failures": 1,
          "errors": 0,
          "skipped": 0,
          "names": [
            "io.github.minokim.lumiawiki.catalog.CommonCatalogIntegrationTests.itemStoragePreservesEquipmentSlotsWhenCategoryNamesChange()"
          ],
          "failedNames": [
            "io.github.minokim.lumiawiki.catalog.CommonCatalogIntegrationTests.itemStoragePreservesEquipmentSlotsWhenCategoryNamesChange()"
          ]
        },
        "manifest": {
          ".codex/hooks.json": "afb95b34e8d441cbd42a7535736128ce520e2ab9c016211d1739a0b40ff4e900",
          ".gitattributes": "4437511f6b3b866745490f0fcd2332d1e6194980fc028232ce0a84cec608d85b",
          "backend/build.gradle": "52b40fbbcdbb75b4ee5d5997811157a0ed61562cbd87c9eb6c3d859a88dd7960",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogErrors.java": "27ef8be77c9334432673e442572792fc933004117fd2586bcd2421ae4230e1df",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CommonCatalogStore.java": "c0e1f3e6559994399fac2f29ae4799f9475fddc03a98e7d3ab21ba323c419ce9",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/EquipmentCategoryRole.java": "817fda99200f9cb55558fa044d4413e98b25bfc613691131a599d2bded12fb9e",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/EquipmentSlot.java": "ed3a6c1f04f460135a25ac46f36be153149b0f9da697907ecfa32b4afa70b7fa",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemCatalogService.java": "a0eb7d382e7af77f17b1d1c2ff23a9f54792b6958a37e5aa8e2ad5ec76fa9efa",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemCategory.java": "63ca657e922f0d70ffc434a777029a205ba272054e930442fe0bd4ee90b0b52f",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersion.java": "7d2209969a3cf705c18964ecdc6b1da36d5411ea60fe6ff13810cd33222a29e3",
          "backend/src/main/resources/application.yaml": "d10d1ef05ddbec053c30bf2bc705e4c5f19a2b688baccd61a4f48af556bb40e0",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/CommonCatalogIntegrationTests.java": "b5e95149ae9a68a516ddf764549f159fcf87993e05651aff727df64bcf4e9a4b",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemCatalogServiceTests.java": "e493ec35c2774edd62a738d3faff52419592f25f82add3402a38e38a26991883",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemStorageMigrationTests.java": "3a33392ce26af90924f691d4d8aa1e4396099e17365e01da8500cb7db15256a9",
          "backend/src/test/resources/application-test.yaml": "e6aa7eb8da29c749b63e7330c634631d82f8710dc4fb6dee5ef883df1ce12e72",
          "db/migration/V4__derive_item_equipment_slot.sql": "e8cf0bc352cc98d41ea1f534d41a35c4d05a4cafbd004c30089f596e5ce6e7dc",
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
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": false
      },
      "final": {
        "runId": "d04634975f3e4887a3195462777a24e7",
        "started": 1795377534.747676,
        "finishedAt": 1795377558.1578562,
        "command": [
          "backend/gradlew.bat",
          "-p",
          "backend",
          "-PtddReportDir={report}",
          "integrationTest",
          "--tests",
          "io.github.minokim.lumiawiki.catalog.CommonCatalogIntegrationTests.itemStoragePreservesEquipmentSlotsWhenCategoryNamesChange",
          "--offline"
        ],
        "exitCode": 0,
        "result": {
          "tests": 1,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "names": [
            "io.github.minokim.lumiawiki.catalog.CommonCatalogIntegrationTests.itemStoragePreservesEquipmentSlotsWhenCategoryNamesChange()"
          ],
          "failedNames": []
        },
        "manifest": {
          ".codex/hooks.json": "afb95b34e8d441cbd42a7535736128ce520e2ab9c016211d1739a0b40ff4e900",
          ".gitattributes": "4437511f6b3b866745490f0fcd2332d1e6194980fc028232ce0a84cec608d85b",
          "backend/build.gradle": "52b40fbbcdbb75b4ee5d5997811157a0ed61562cbd87c9eb6c3d859a88dd7960",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogErrors.java": "27ef8be77c9334432673e442572792fc933004117fd2586bcd2421ae4230e1df",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/CommonCatalogStore.java": "c0e1f3e6559994399fac2f29ae4799f9475fddc03a98e7d3ab21ba323c419ce9",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/EquipmentCategoryRole.java": "817fda99200f9cb55558fa044d4413e98b25bfc613691131a599d2bded12fb9e",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/EquipmentSlot.java": "3692de42555019909fa7a34a296c47da5aa7ce14dcf2614b4846e0d34a76cc2e",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemCatalogService.java": "e3d1f0275dc52d2d90b9fe0a6c045c0301bea5d5cd749698c0289f256d8e0f76",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemCategory.java": "63ca657e922f0d70ffc434a777029a205ba272054e930442fe0bd4ee90b0b52f",
          "backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersion.java": "7d2209969a3cf705c18964ecdc6b1da36d5411ea60fe6ff13810cd33222a29e3",
          "backend/src/main/resources/application.yaml": "d10d1ef05ddbec053c30bf2bc705e4c5f19a2b688baccd61a4f48af556bb40e0",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/CommonCatalogIntegrationTests.java": "b5e95149ae9a68a516ddf764549f159fcf87993e05651aff727df64bcf4e9a4b",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemCatalogServiceTests.java": "e493ec35c2774edd62a738d3faff52419592f25f82add3402a38e38a26991883",
          "backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemStorageMigrationTests.java": "3a33392ce26af90924f691d4d8aa1e4396099e17365e01da8500cb7db15256a9",
          "backend/src/test/resources/application-test.yaml": "e6aa7eb8da29c749b63e7330c634631d82f8710dc4fb6dee5ef883df1ce12e72",
          "db/migration/V4__derive_item_equipment_slot.sql": "e8cf0bc352cc98d41ea1f534d41a35c4d05a4cafbd004c30089f596e5ce6e7dc",
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
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": true
      }
    }
  ]
}
```
