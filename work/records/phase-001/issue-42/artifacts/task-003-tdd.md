# Task 42-003 TDD 실행 입력과 정식 근거

[담당 Task](../task-003.md#summary)

<!-- tdd-plan -->
```json
{
  "schema": 1,
  "cycles": [
    {
      "id": "parent-record-gate-integration",
      "kind": "correction",
      "reason": "기검수 main PR #61의 기록 검사·CI를 main→phase→issue 순서로 반영한다. 기존 TDD→현황 wrapper와 새 기록 검사를 함께 보존하고 의존 선언·테스트 fixture만 결합한다. 새 동작의 Red를 꾸미지 않으며 기존 Task 002·PR #61 근거와 결합 후보의 실제 검사 결과를 사용한다.",
      "targets": [
        ".github/workflows/harness-inventory.yml",
        "scripts/check-work-records.py",
        "scripts/hooks/pre-commit"
      ],
      "tests": [
        "scripts/tests/test_harness_inventory.py",
        "scripts/tests/test_work_records.py"
      ],
      "settings": [],
      "adapter": "unittest",
      "command": [
        "python",
        "-B",
        "-X",
        "utf8",
        "scripts/test-python.py",
        "--report",
        "{report}",
        "--run-id",
        "{run_id}",
        "--",
        "discover",
        "-s",
        "scripts/tests",
        "-p",
        "test_harness_inventory.py",
        "-k",
        "test_record_gate",
        "-k",
        "test_existing_hook_rejection",
        "-k",
        "test_consistent_work_and_index",
        "-k",
        "test_branches_predating_record_check",
        "-v"
      ]
    },
    {
      "id": "router-query-dependencies",
      "kind": "environment",
      "reason": "Task에서 확정한 Router/Query 두 라이브러리만 정확히 고정하고 설치·타입·제품 빌드 호환성을 확인한다. 기능 로직의 선행 구현은 하지 않는다.",
      "targets": [
        "frontend/package.json",
        "frontend/package-lock.json"
      ],
      "tests": [],
      "settings": [],
      "adapter": "command",
      "command": [
        "npm.cmd",
        "--prefix",
        "frontend",
        "run",
        "build"
      ]
    },
    {
      "id": "screen-design-preview",
      "kind": "correction",
      "reason": "동작 구현 전 정적 확인 화면을 먼저 검토하는 디자인 예외다. 조회·화면 이동은 아직 비활성이며 API 미연결을 표시한다. 기존 DOM 환경 검사와 타입/빌드·화면 직접 관찰로 확인하며 실제 API 동작의 Green으로 사용하지 않는다.",
      "targets": [
        "frontend/src/main.tsx",
        "frontend/src/dev/FoundationPage.tsx"
      ],
      "tests": [
        "frontend/src/test/environment.test.tsx"
      ],
      "settings": [],
      "adapter": "vitest",
      "command": [
        "node",
        "frontend/node_modules/vitest/vitest.mjs",
        "run",
        "--root",
        "frontend",
        "src/test/environment.test.tsx",
        "--reporter=json",
        "--outputFile={report}"
      ]
    },
    {
      "id": "web-contract-signatures",
      "kind": "correction",
      "reason": "테스트가 실제 실행될 수 있게 무동작 타입·함수 시그니처와 명시적인 미구현 반환만 준비한다. 요청·경로 검증·취소·이미지 대체 로직은 실제 Red 뒤 작성한다.",
      "targets": [
        "frontend/src/shared/api.ts",
        "frontend/src/shared/images.tsx"
      ],
      "tests": [
        "frontend/src/test/environment.test.tsx"
      ],
      "settings": [],
      "adapter": "vitest",
      "command": [
        "node",
        "frontend/node_modules/vitest/vitest.mjs",
        "run",
        "--root",
        "frontend",
        "src/test/environment.test.tsx",
        "--reporter=json",
        "--outputFile={report}"
      ]
    },
    {
      "id": "http-and-image-boundaries",
      "kind": "behavior",
      "targets": [
        "frontend/src/shared/api.ts",
        "frontend/src/shared/images.tsx"
      ],
      "tests": [
        "frontend/src/shared/boundaries.test.tsx"
      ],
      "settings": [],
      "adapter": "vitest",
      "command": [
        "node",
        "frontend/node_modules/vitest/vitest.mjs",
        "run",
        "--root",
        "frontend",
        "src/shared/boundaries.test.tsx",
        "--reporter=json",
        "--outputFile={report}"
      ],
      "expectedFailures": [
        "fetches relative JSON without forwarding request bodies",
        "turns ProblemDetail into a safe HTTP error",
        "does not expose non JSON failure bodies",
        "separates cancellation network failure and timeout",
        "keeps timeout active while reading response body",
        "rejects paths outside the API boundary",
        "resolves images under the app base and rejects unsafe paths",
        "falls back once and recovers when the image path changes"
      ]
    },
    {
      "id": "foundation-interaction",
      "kind": "behavior",
      "targets": [
        "frontend/src/main.tsx",
        "frontend/src/app/App.tsx",
        "frontend/src/app/queryClient.ts",
        "frontend/src/dev/routes.ts",
        "frontend/src/dev/FoundationPage.tsx",
        "frontend/src/dev/NavigationPage.tsx",
        "frontend/vite.config.mjs"
      ],
      "tests": [
        "frontend/src/dev/foundation.test.tsx"
      ],
      "settings": [
        "frontend/src/shared/api.ts",
        "frontend/src/shared/images.tsx"
      ],
      "adapter": "vitest",
      "command": [
        "node",
        "frontend/node_modules/vitest/vitest.mjs",
        "run",
        "--root",
        "frontend",
        "src/dev/foundation.test.tsx",
        "--reporter=json",
        "--outputFile={report}"
      ],
      "expectedFailures": [
        "runs queries only on submit and shows loading then response",
        "changing scenario cancels stale work and shows independent empty and error states",
        "provides two navigable screens and restores back navigation"
      ]
    },
    {
      "id": "server-contract-signatures",
      "kind": "correction",
      "reason": "MockMvc 테스트를 실행할 수 있게 매핑 없는 컨트롤러·서비스와 통과만 하는 필터·빈 advice 타입을 준비한다. 요청 처리 로직은 실제 Red 뒤 구현한다. 기존 DB 비의존 테스트로 실행 환경을 확인한다.",
      "targets": [
        "backend/src/main/java/io/github/minokim/lumiawiki/common/api/ApiExceptionAdvice.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/common/api/RequestIdFilter.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/dev/FoundationController.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/dev/FoundationService.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/dev/FoundationResponse.java",
        "backend/src/main/resources/application.yaml",
        "backend/src/main/resources/application-local.yaml",
        "backend/src/test/resources/application-test.yaml"
      ],
      "tests": [
        "backend/src/test/java/io/github/minokim/lumiawiki/TestEnvironmentTests.java"
      ],
      "settings": [],
      "adapter": "junit",
      "command": [
        "backend/gradlew.bat",
        "-p",
        "backend",
        "--no-daemon",
        "--max-workers=2",
        "-Dorg.gradle.jvmargs=-Xms64m -Xmx256m -XX:MaxMetaspaceSize=256m",
        "test",
        "--tests",
        "io.github.minokim.lumiawiki.TestEnvironmentTests",
        "-PtddReportDir={report}"
      ]
    },
    {
      "id": "foundation-api-contract",
      "kind": "behavior",
      "targets": [
        "backend/src/main/java/io/github/minokim/lumiawiki/common/api/ApiExceptionAdvice.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/common/api/RequestIdFilter.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/dev/FoundationController.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/dev/FoundationService.java",
        "backend/src/main/java/io/github/minokim/lumiawiki/dev/FoundationResponse.java",
        "backend/src/main/resources/application.yaml",
        "backend/src/main/resources/application-local.yaml",
        "backend/src/test/resources/application-test.yaml",
        "backend/src/main/java/io/github/minokim/lumiawiki/common/api/ApiFailure.java"
      ],
      "tests": [
        "backend/src/test/java/io/github/minokim/lumiawiki/FoundationApiTests.java"
      ],
      "settings": [],
      "adapter": "junit",
      "command": [
        "backend/gradlew.bat",
        "-p",
        "backend",
        "--no-daemon",
        "--max-workers=2",
        "-Dorg.gradle.jvmargs=-Xms64m -Xmx256m -XX:MaxMetaspaceSize=256m",
        "test",
        "--tests",
        "io.github.minokim.lumiawiki.FoundationApiTests",
        "-PtddReportDir={report}"
      ],
      "expectedFailures": [
        "io.github.minokim.lumiawiki.FoundationApiTests.normalAndEmptyResponsesHaveServerOwnedRequestIds()",
        "io.github.minokim.lumiawiki.FoundationApiTests.badInputAndMissingUseProblemDetail()",
        "io.github.minokim.lumiawiki.FoundationApiTests.internalFailureRedactsResponsesAndLogs()",
        "io.github.minokim.lumiawiki.FoundationApiTests.mvcValidationAndParsingRemain400()",
        "io.github.minokim.lumiawiki.FoundationApiTests.unsupportedMethodKeeps405()",
        "io.github.minokim.lumiawiki.FoundationApiTests.profileGatesDevEndpoint()",
        "io.github.minokim.lumiawiki.FoundationApiTests.slowResponseUsesOneSecondDelay()"
      ]
    },
    {
      "id": "web-final-candidate",
      "kind": "correction",
      "reason": "HTTP·이미지와 화면 동작의 실제 Red/Green을 보존하고 최신 Vite 프록시·서버 프로필 설정을 포함한 공통 검사 맥락으로 제출 후보를 확인한다. 테스트의 unknown 값 비교를 타입에 맞는 동일 의미 matcher로 정정했으며 assertion을 삭제하거나 기대 동작을 낮추지 않았다. 새 기능 구현 예외가 아니다.",
      "targets": [
        "frontend/package.json",
        "frontend/package-lock.json",
        "frontend/src/main.tsx",
        "frontend/src/app/App.tsx",
        "frontend/src/app/queryClient.ts",
        "frontend/src/dev/routes.ts",
        "frontend/src/dev/FoundationPage.tsx",
        "frontend/src/dev/NavigationPage.tsx",
        "frontend/src/shared/api.ts",
        "frontend/src/shared/images.tsx",
        "frontend/vite.config.mjs"
      ],
      "tests": [
        "frontend/src/shared/boundaries.test.tsx",
        "frontend/src/dev/foundation.test.tsx",
        "frontend/src/test/environment.test.tsx"
      ],
      "settings": [],
      "adapter": "vitest",
      "command": [
        "node",
        "frontend/node_modules/vitest/vitest.mjs",
        "run",
        "--root",
        "frontend",
        "--reporter=json",
        "--outputFile={report}"
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
      "id": "parent-record-gate-integration",
      "kind": "correction",
      "spec": "ad37dde44c4521856ab62ac937bd080337e0ddd82d138d41a74c94e85d0d8e9b",
      "worktree": "f8f58622827de84fd0e6",
      "finished": true,
      "baseline": "2ca4efd473622282d138ecd970603682c884673d",
      "task": "work/records/phase-001/issue-42/artifacts/task-003-tdd.md",
      "final": {
        "runId": "a38914dcf6c24bb8a45c49d29f9bd8c2",
        "started": 1794479897.439044,
        "finishedAt": 1794479904.5766912,
        "command": [
          "python",
          "-B",
          "-X",
          "utf8",
          "scripts/test-python.py",
          "--report",
          "{report}",
          "--run-id",
          "{run_id}",
          "--",
          "discover",
          "-s",
          "scripts/tests",
          "-p",
          "test_harness_inventory.py",
          "-k",
          "test_record_gate",
          "-k",
          "test_existing_hook_rejection",
          "-k",
          "test_consistent_work_and_index",
          "-k",
          "test_branches_predating_record_check",
          "-v"
        ],
        "exitCode": 0,
        "result": {
          "tests": 4,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "names": [
            "test_harness_inventory.CandidateTests.test_consistent_work_and_index_are_read_only",
            "test_harness_inventory.HookTests.test_branches_predating_record_check_skip_but_unstaged_deletion_denies",
            "test_harness_inventory.HookTests.test_existing_hook_rejection_is_preserved",
            "test_harness_inventory.HookTests.test_record_gate_blocks_dates_but_only_warns_for_long_records"
          ],
          "failedNames": []
        },
        "manifest": {
          ".codex/hooks.json": "c9919a89f613c6c4ed0602d5ce108634c6442eaff1b8b3929162dd88c161a0f8",
          ".gitattributes": null,
          ".github/workflows/harness-inventory.yml": "f588d39e3e2f52de912d15d62967fd997e64d9d702e381f6128af210301c8fd8",
          "backend/build.gradle": "b1faa0d24d9a3440b6c9ceb0c9a7673167ff401145d5b250c3293e7810d745b9",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/resources/application.yaml": "4761c46d3f79db0632579511eac32ade8f1856703687973ddcb9d324cba5cc6e",
          "backend/src/test/resources/application-test.yaml": "bfeb67bd9ba26be9c9b36ee76324032a25e5bbfe205e0302b308c89cce14a344",
          "frontend/package-lock.json": "ca3f1f88c8eef376a2fafc3adac7d9bcfae337be30b36283c2cd6ad10f08ddd0",
          "frontend/package.json": "a817304bc81fc0d04b1694f8da5a68cbea3a0fb59686210f972fe7e7a9c1e32f",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "6023cc089e22ac6a494f9f27f6b243b06c9cfbef0eb8f5bd49af507813a55bc3",
          "frontend/vitest.config.mjs": "2df5221cb23b6db0a9b6377e300187806b4ec405cab5bc076c9777f3fb3d5aa0",
          "package-lock.json": null,
          "package.json": null,
          "scripts/check-work-records.py": "94590db6bb08d51e5dc0add9c8225f63ece2fb600dcca38c5becef5a0bc4690e",
          "scripts/hooks/pre-commit": "864ff1d52060645819a6f5a20a10ed5957f64116f9e59c5066fbf4953c22368c",
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c",
          "scripts/tests/test_harness_inventory.py": "f570b49c502f781fad6695864845e2fbcc72494b8c085517cb3ca484a791dd7f",
          "scripts/tests/test_work_records.py": "f0847497f2623b76ef727ca2c8d6ba34b830fd8de2b719e083703b3df2818c0f"
        },
        "ok": true
      }
    },
    {
      "id": "router-query-dependencies",
      "kind": "environment",
      "spec": "361ccc3ecf23605a25ae25445000395dff6c9fc5dc4a0307f60eb07141d3a9a9",
      "worktree": "f8f58622827de84fd0e6",
      "finished": true,
      "baseline": "21dd44fedf36f4416d0b74e8df383e0afb624294",
      "task": "work/records/phase-001/issue-42/artifacts/task-003-tdd.md",
      "final": {
        "runId": "5f59e1601573431d96300e97a3866edf",
        "started": 1794480141.638147,
        "finishedAt": 1794480157.7256682,
        "command": [
          "npm.cmd",
          "--prefix",
          "frontend",
          "run",
          "build"
        ],
        "exitCode": 0,
        "result": {
          "tests": 0,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "names": [],
          "failedNames": []
        },
        "manifest": {
          ".codex/hooks.json": "c9919a89f613c6c4ed0602d5ce108634c6442eaff1b8b3929162dd88c161a0f8",
          ".gitattributes": null,
          "backend/build.gradle": "b1faa0d24d9a3440b6c9ceb0c9a7673167ff401145d5b250c3293e7810d745b9",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/resources/application.yaml": "4761c46d3f79db0632579511eac32ade8f1856703687973ddcb9d324cba5cc6e",
          "backend/src/test/resources/application-test.yaml": "bfeb67bd9ba26be9c9b36ee76324032a25e5bbfe205e0302b308c89cce14a344",
          "frontend/package-lock.json": "f6d02d40aeb012b0164f0b505385de31fa5a35764a3d667133ccd50392cf8e89",
          "frontend/package.json": "203230a9a507a41820c1e2273a8f8e5f9e7156cb3cea11d39aef903b36a7f6f8",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "6023cc089e22ac6a494f9f27f6b243b06c9cfbef0eb8f5bd49af507813a55bc3",
          "frontend/vitest.config.mjs": "2df5221cb23b6db0a9b6377e300187806b4ec405cab5bc076c9777f3fb3d5aa0",
          "package-lock.json": null,
          "package.json": null,
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": true
      }
    },
    {
      "id": "screen-design-preview",
      "kind": "correction",
      "spec": "d91d8006a80b0a2adeec29ebd7bed067553ff1ebb6235a840cc00c370009d28c",
      "worktree": "f8f58622827de84fd0e6",
      "finished": true,
      "baseline": "21dd44fedf36f4416d0b74e8df383e0afb624294",
      "task": "work/records/phase-001/issue-42/artifacts/task-003-tdd.md",
      "final": {
        "runId": "aaba2bf1421440bbac1adc1df391e11b",
        "started": 1794480158.1986868,
        "finishedAt": 1794480169.9619431,
        "command": [
          "node",
          "frontend/node_modules/vitest/vitest.mjs",
          "run",
          "--root",
          "frontend",
          "src/test/environment.test.tsx",
          "--reporter=json",
          "--outputFile={report}"
        ],
        "exitCode": 0,
        "result": {
          "tests": 2,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "names": [
            "DOM test environment runs a React interaction using user-event and jest-dom assertions",
            "DOM test environment cleans the previous DOM and starts with independent component state"
          ],
          "failedNames": []
        },
        "manifest": {
          ".codex/hooks.json": "c9919a89f613c6c4ed0602d5ce108634c6442eaff1b8b3929162dd88c161a0f8",
          ".gitattributes": null,
          "backend/build.gradle": "b1faa0d24d9a3440b6c9ceb0c9a7673167ff401145d5b250c3293e7810d745b9",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/resources/application.yaml": "4761c46d3f79db0632579511eac32ade8f1856703687973ddcb9d324cba5cc6e",
          "backend/src/test/resources/application-test.yaml": "bfeb67bd9ba26be9c9b36ee76324032a25e5bbfe205e0302b308c89cce14a344",
          "frontend/package-lock.json": "f6d02d40aeb012b0164f0b505385de31fa5a35764a3d667133ccd50392cf8e89",
          "frontend/package.json": "203230a9a507a41820c1e2273a8f8e5f9e7156cb3cea11d39aef903b36a7f6f8",
          "frontend/src/dev/FoundationPage.tsx": "11a7df7aeb67a03e47ee7ca7aab64be2e24d431da9c18875076ecef39ffae7f4",
          "frontend/src/main.tsx": "77b3dcc4dcd689669395b92ee4d5af0c59b3f4a8fc66805a18412360111e7279",
          "frontend/src/test/environment.test.tsx": "1f529250a834f10781925a0e7e042a88a40c60f758dc60cefde671b12e21776c",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "6023cc089e22ac6a494f9f27f6b243b06c9cfbef0eb8f5bd49af507813a55bc3",
          "frontend/vitest.config.mjs": "2df5221cb23b6db0a9b6377e300187806b4ec405cab5bc076c9777f3fb3d5aa0",
          "package-lock.json": null,
          "package.json": null,
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": true
      }
    },
    {
      "id": "web-contract-signatures",
      "kind": "correction",
      "spec": "66b258d91d36a818e2f96709ff050bd403b3eccd02bad77ea765fb0b3229cc6d",
      "worktree": "f8f58622827de84fd0e6",
      "finished": true,
      "baseline": "21dd44fedf36f4416d0b74e8df383e0afb624294",
      "task": "work/records/phase-001/issue-42/artifacts/task-003-tdd.md",
      "final": {
        "runId": "d785f5fc647d44238162fe66fd282eaf",
        "started": 1794480307.1717184,
        "finishedAt": 1794480316.2332907,
        "command": [
          "node",
          "frontend/node_modules/vitest/vitest.mjs",
          "run",
          "--root",
          "frontend",
          "src/test/environment.test.tsx",
          "--reporter=json",
          "--outputFile={report}"
        ],
        "exitCode": 0,
        "result": {
          "tests": 2,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "names": [
            "DOM test environment runs a React interaction using user-event and jest-dom assertions",
            "DOM test environment cleans the previous DOM and starts with independent component state"
          ],
          "failedNames": []
        },
        "manifest": {
          ".codex/hooks.json": "c9919a89f613c6c4ed0602d5ce108634c6442eaff1b8b3929162dd88c161a0f8",
          ".gitattributes": null,
          "backend/build.gradle": "b1faa0d24d9a3440b6c9ceb0c9a7673167ff401145d5b250c3293e7810d745b9",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/resources/application.yaml": "4761c46d3f79db0632579511eac32ade8f1856703687973ddcb9d324cba5cc6e",
          "backend/src/test/resources/application-test.yaml": "bfeb67bd9ba26be9c9b36ee76324032a25e5bbfe205e0302b308c89cce14a344",
          "frontend/package-lock.json": "f6d02d40aeb012b0164f0b505385de31fa5a35764a3d667133ccd50392cf8e89",
          "frontend/package.json": "203230a9a507a41820c1e2273a8f8e5f9e7156cb3cea11d39aef903b36a7f6f8",
          "frontend/src/shared/api.ts": "4c3cd817d87e4696eab18228ad3a61522fe1226f65b73d6e0d186bbd1d56ed88",
          "frontend/src/shared/images.tsx": "b0a1c8233bc401d226b35e4b679fe3f7243cd9df1604bb2679f1f190f930cd8a",
          "frontend/src/test/environment.test.tsx": "1f529250a834f10781925a0e7e042a88a40c60f758dc60cefde671b12e21776c",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "6023cc089e22ac6a494f9f27f6b243b06c9cfbef0eb8f5bd49af507813a55bc3",
          "frontend/vitest.config.mjs": "2df5221cb23b6db0a9b6377e300187806b4ec405cab5bc076c9777f3fb3d5aa0",
          "package-lock.json": null,
          "package.json": null,
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": true
      }
    },
    {
      "id": "http-and-image-boundaries",
      "kind": "behavior",
      "spec": "8b2014a3421f13cd1b0254b7158861f7bfa0ac84177ee3c05a85d916573b093f",
      "worktree": "f8f58622827de84fd0e6",
      "baseline": "21dd44fedf36f4416d0b74e8df383e0afb624294",
      "task": "work/records/phase-001/issue-42/artifacts/task-003-tdd.md",
      "finished": true,
      "red": {
        "runId": "f73d874f91394aaead27eb8894244306",
        "started": 1794480337.2372284,
        "finishedAt": 1794480339.8842833,
        "command": [
          "node",
          "frontend/node_modules/vitest/vitest.mjs",
          "run",
          "--root",
          "frontend",
          "src/shared/boundaries.test.tsx",
          "--reporter=json",
          "--outputFile={report}"
        ],
        "exitCode": 1,
        "result": {
          "tests": 8,
          "failures": 8,
          "errors": 0,
          "skipped": 0,
          "names": [
            "fetches relative JSON without forwarding request bodies",
            "turns ProblemDetail into a safe HTTP error",
            "does not expose non JSON failure bodies",
            "separates cancellation network failure and timeout",
            "keeps timeout active while reading response body",
            "rejects paths outside the API boundary",
            "resolves images under the app base and rejects unsafe paths",
            "falls back once and recovers when the image path changes"
          ],
          "failedNames": [
            "fetches relative JSON without forwarding request bodies",
            "turns ProblemDetail into a safe HTTP error",
            "does not expose non JSON failure bodies",
            "separates cancellation network failure and timeout",
            "keeps timeout active while reading response body",
            "rejects paths outside the API boundary",
            "resolves images under the app base and rejects unsafe paths",
            "falls back once and recovers when the image path changes"
          ]
        },
        "manifest": {
          ".codex/hooks.json": "c9919a89f613c6c4ed0602d5ce108634c6442eaff1b8b3929162dd88c161a0f8",
          ".gitattributes": null,
          "backend/build.gradle": "b1faa0d24d9a3440b6c9ceb0c9a7673167ff401145d5b250c3293e7810d745b9",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/resources/application.yaml": "4761c46d3f79db0632579511eac32ade8f1856703687973ddcb9d324cba5cc6e",
          "backend/src/test/resources/application-test.yaml": "bfeb67bd9ba26be9c9b36ee76324032a25e5bbfe205e0302b308c89cce14a344",
          "frontend/package-lock.json": "f6d02d40aeb012b0164f0b505385de31fa5a35764a3d667133ccd50392cf8e89",
          "frontend/package.json": "203230a9a507a41820c1e2273a8f8e5f9e7156cb3cea11d39aef903b36a7f6f8",
          "frontend/src/shared/api.ts": "4c3cd817d87e4696eab18228ad3a61522fe1226f65b73d6e0d186bbd1d56ed88",
          "frontend/src/shared/boundaries.test.tsx": "c75f5097fbd01034d190b45df9d0ffc7d5212b1893b18f2e9ebcd441fca5163a",
          "frontend/src/shared/images.tsx": "b0a1c8233bc401d226b35e4b679fe3f7243cd9df1604bb2679f1f190f930cd8a",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "6023cc089e22ac6a494f9f27f6b243b06c9cfbef0eb8f5bd49af507813a55bc3",
          "frontend/vitest.config.mjs": "2df5221cb23b6db0a9b6377e300187806b4ec405cab5bc076c9777f3fb3d5aa0",
          "package-lock.json": null,
          "package.json": null,
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": false
      },
      "final": {
        "runId": "cb1762a7c6684934a800c55f384777ad",
        "started": 1794480374.7990518,
        "finishedAt": 1794480377.4807372,
        "command": [
          "node",
          "frontend/node_modules/vitest/vitest.mjs",
          "run",
          "--root",
          "frontend",
          "src/shared/boundaries.test.tsx",
          "--reporter=json",
          "--outputFile={report}"
        ],
        "exitCode": 0,
        "result": {
          "tests": 8,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "names": [
            "fetches relative JSON without forwarding request bodies",
            "turns ProblemDetail into a safe HTTP error",
            "does not expose non JSON failure bodies",
            "separates cancellation network failure and timeout",
            "keeps timeout active while reading response body",
            "rejects paths outside the API boundary",
            "resolves images under the app base and rejects unsafe paths",
            "falls back once and recovers when the image path changes"
          ],
          "failedNames": []
        },
        "manifest": {
          ".codex/hooks.json": "c9919a89f613c6c4ed0602d5ce108634c6442eaff1b8b3929162dd88c161a0f8",
          ".gitattributes": null,
          "backend/build.gradle": "b1faa0d24d9a3440b6c9ceb0c9a7673167ff401145d5b250c3293e7810d745b9",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/resources/application.yaml": "4761c46d3f79db0632579511eac32ade8f1856703687973ddcb9d324cba5cc6e",
          "backend/src/test/resources/application-test.yaml": "bfeb67bd9ba26be9c9b36ee76324032a25e5bbfe205e0302b308c89cce14a344",
          "frontend/package-lock.json": "f6d02d40aeb012b0164f0b505385de31fa5a35764a3d667133ccd50392cf8e89",
          "frontend/package.json": "203230a9a507a41820c1e2273a8f8e5f9e7156cb3cea11d39aef903b36a7f6f8",
          "frontend/src/shared/api.ts": "2fb6e8408fd6139e1aab5fc9bf38988da09b35326a775bbca031563cd57ca3ab",
          "frontend/src/shared/boundaries.test.tsx": "c75f5097fbd01034d190b45df9d0ffc7d5212b1893b18f2e9ebcd441fca5163a",
          "frontend/src/shared/images.tsx": "331ada9ff78e72b4015cde518f6b019c87e8896c7f5e21c58190c9c21c4fafbf",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "6023cc089e22ac6a494f9f27f6b243b06c9cfbef0eb8f5bd49af507813a55bc3",
          "frontend/vitest.config.mjs": "2df5221cb23b6db0a9b6377e300187806b4ec405cab5bc076c9777f3fb3d5aa0",
          "package-lock.json": null,
          "package.json": null,
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": true
      }
    },
    {
      "id": "foundation-interaction",
      "kind": "behavior",
      "spec": "cbe40f2f2cb8f726b62b9cefac6a9928f9999193440c7a927b9fcc3ac70dfaf4",
      "worktree": "f8f58622827de84fd0e6",
      "baseline": "21dd44fedf36f4416d0b74e8df383e0afb624294",
      "task": "work/records/phase-001/issue-42/artifacts/task-003-tdd.md",
      "finished": true,
      "red": {
        "runId": "eeb52132f9c342cc9321eed2efa52305",
        "started": 1794480423.809504,
        "finishedAt": 1794480432.3288605,
        "command": [
          "node",
          "frontend/node_modules/vitest/vitest.mjs",
          "run",
          "--root",
          "frontend",
          "src/dev/foundation.test.tsx",
          "--reporter=json",
          "--outputFile={report}"
        ],
        "exitCode": 1,
        "result": {
          "tests": 3,
          "failures": 3,
          "errors": 0,
          "skipped": 0,
          "names": [
            "runs queries only on submit and shows loading then response",
            "changing scenario cancels stale work and shows independent empty and error states",
            "provides two navigable screens and restores back navigation"
          ],
          "failedNames": [
            "runs queries only on submit and shows loading then response",
            "changing scenario cancels stale work and shows independent empty and error states",
            "provides two navigable screens and restores back navigation"
          ]
        },
        "manifest": {
          ".codex/hooks.json": "c9919a89f613c6c4ed0602d5ce108634c6442eaff1b8b3929162dd88c161a0f8",
          ".gitattributes": null,
          "backend/build.gradle": "b1faa0d24d9a3440b6c9ceb0c9a7673167ff401145d5b250c3293e7810d745b9",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/resources/application.yaml": "4761c46d3f79db0632579511eac32ade8f1856703687973ddcb9d324cba5cc6e",
          "backend/src/test/resources/application-test.yaml": "bfeb67bd9ba26be9c9b36ee76324032a25e5bbfe205e0302b308c89cce14a344",
          "frontend/package-lock.json": "f6d02d40aeb012b0164f0b505385de31fa5a35764a3d667133ccd50392cf8e89",
          "frontend/package.json": "203230a9a507a41820c1e2273a8f8e5f9e7156cb3cea11d39aef903b36a7f6f8",
          "frontend/src/app/App.tsx": null,
          "frontend/src/app/queryClient.ts": null,
          "frontend/src/dev/FoundationPage.tsx": "11a7df7aeb67a03e47ee7ca7aab64be2e24d431da9c18875076ecef39ffae7f4",
          "frontend/src/dev/NavigationPage.tsx": null,
          "frontend/src/dev/foundation.test.tsx": "6e835b620e42861939d916ee0335553389388e247f1dd4d09d6a548a28d452aa",
          "frontend/src/dev/routes.ts": null,
          "frontend/src/main.tsx": "77b3dcc4dcd689669395b92ee4d5af0c59b3f4a8fc66805a18412360111e7279",
          "frontend/src/shared/api.ts": "2fb6e8408fd6139e1aab5fc9bf38988da09b35326a775bbca031563cd57ca3ab",
          "frontend/src/shared/images.tsx": "331ada9ff78e72b4015cde518f6b019c87e8896c7f5e21c58190c9c21c4fafbf",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "6023cc089e22ac6a494f9f27f6b243b06c9cfbef0eb8f5bd49af507813a55bc3",
          "frontend/vitest.config.mjs": "2df5221cb23b6db0a9b6377e300187806b4ec405cab5bc076c9777f3fb3d5aa0",
          "package-lock.json": null,
          "package.json": null,
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": false
      },
      "final": {
        "runId": "3f6396af85fc4b27b7afbaa4e84db58e",
        "started": 1794480585.935256,
        "finishedAt": 1794480589.5281646,
        "command": [
          "node",
          "frontend/node_modules/vitest/vitest.mjs",
          "run",
          "--root",
          "frontend",
          "src/dev/foundation.test.tsx",
          "--reporter=json",
          "--outputFile={report}"
        ],
        "exitCode": 0,
        "result": {
          "tests": 3,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "names": [
            "runs queries only on submit and shows loading then response",
            "changing scenario cancels stale work and shows independent empty and error states",
            "provides two navigable screens and restores back navigation"
          ],
          "failedNames": []
        },
        "manifest": {
          ".codex/hooks.json": "c9919a89f613c6c4ed0602d5ce108634c6442eaff1b8b3929162dd88c161a0f8",
          ".gitattributes": null,
          "backend/build.gradle": "b1faa0d24d9a3440b6c9ceb0c9a7673167ff401145d5b250c3293e7810d745b9",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/resources/application.yaml": "4761c46d3f79db0632579511eac32ade8f1856703687973ddcb9d324cba5cc6e",
          "backend/src/test/resources/application-test.yaml": "bfeb67bd9ba26be9c9b36ee76324032a25e5bbfe205e0302b308c89cce14a344",
          "frontend/package-lock.json": "f6d02d40aeb012b0164f0b505385de31fa5a35764a3d667133ccd50392cf8e89",
          "frontend/package.json": "203230a9a507a41820c1e2273a8f8e5f9e7156cb3cea11d39aef903b36a7f6f8",
          "frontend/src/app/App.tsx": "c0dafb2f9d00d9b18335e238c4521e9a13d238d55a8a24b771d24ef755b0d17a",
          "frontend/src/app/queryClient.ts": "aac7cb60992f7f1a0dbccb5145a1e5559b35e5355f2214ce2291ac3e9a683524",
          "frontend/src/dev/FoundationPage.tsx": "716bc2db0383b252e45ae5a3fff670e2c0732510665d9e68a968dcab75337a03",
          "frontend/src/dev/NavigationPage.tsx": "448852e59a2bbd9b1b5ba73fa6696f3fbda1836aac8b8fd9bbfba1eb70b27a01",
          "frontend/src/dev/foundation.test.tsx": "6e835b620e42861939d916ee0335553389388e247f1dd4d09d6a548a28d452aa",
          "frontend/src/dev/routes.ts": "03bc24e876702a1a1a1a77f908d921654d3a8c409d48dcaa3ce8bd1d312c1eca",
          "frontend/src/main.tsx": "55e23958b3629135cea5953191761548b9d7f5e607f6e7ca9b204f6a9b1f9159",
          "frontend/src/shared/api.ts": "2fb6e8408fd6139e1aab5fc9bf38988da09b35326a775bbca031563cd57ca3ab",
          "frontend/src/shared/images.tsx": "331ada9ff78e72b4015cde518f6b019c87e8896c7f5e21c58190c9c21c4fafbf",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "85133eb3283ec0c8336044e60bea2150cc6203e6f8cc33f17c81882aaafe41ae",
          "frontend/vitest.config.mjs": "2df5221cb23b6db0a9b6377e300187806b4ec405cab5bc076c9777f3fb3d5aa0",
          "package-lock.json": null,
          "package.json": null,
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": true
      }
    },
    {
      "id": "server-contract-signatures",
      "kind": "correction",
      "spec": "6885a4f43bf807bd2fb4b572e97d91b5c87d4a86748c53bdeb74876c34897073",
      "worktree": "f8f58622827de84fd0e6",
      "finished": true,
      "baseline": "21dd44fedf36f4416d0b74e8df383e0afb624294",
      "task": "work/records/phase-001/issue-42/artifacts/task-003-tdd.md",
      "final": {
        "runId": "a17f7b43ae054444be525d7e309e4825",
        "started": 1794480702.6757078,
        "finishedAt": 1794480762.6324944,
        "command": [
          "backend/gradlew.bat",
          "-p",
          "backend",
          "--no-daemon",
          "--max-workers=2",
          "-Dorg.gradle.jvmargs=-Xms64m -Xmx256m -XX:MaxMetaspaceSize=256m",
          "test",
          "--tests",
          "io.github.minokim.lumiawiki.TestEnvironmentTests",
          "-PtddReportDir={report}"
        ],
        "exitCode": 0,
        "result": {
          "tests": 2,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "names": [
            "io.github.minokim.lumiawiki.TestEnvironmentTests.junitMockitoAndMockMvcRunWithoutDocker()",
            "io.github.minokim.lumiawiki.TestEnvironmentTests.beanValidationRejectsInputBeforeCallingTheCollaborator()"
          ],
          "failedNames": []
        },
        "manifest": {
          ".codex/hooks.json": "c9919a89f613c6c4ed0602d5ce108634c6442eaff1b8b3929162dd88c161a0f8",
          ".gitattributes": null,
          "backend/build.gradle": "b1faa0d24d9a3440b6c9ceb0c9a7673167ff401145d5b250c3293e7810d745b9",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/java/io/github/minokim/lumiawiki/common/api/ApiExceptionAdvice.java": "fccda07ff5b229c3412bb634195cbdccc26bc0c32392ff591069d184077fcc73",
          "backend/src/main/java/io/github/minokim/lumiawiki/common/api/RequestIdFilter.java": "a81bb2c80080236e6773a593b37bfd63c40ced73db77e3726b7b253c6a79e2d1",
          "backend/src/main/java/io/github/minokim/lumiawiki/dev/FoundationController.java": "b6b8affcdab97448733bab7d8ab0e4af5d026bc19e8cd6d1b3e500b3a4715f7b",
          "backend/src/main/java/io/github/minokim/lumiawiki/dev/FoundationResponse.java": null,
          "backend/src/main/java/io/github/minokim/lumiawiki/dev/FoundationService.java": "96d53909efe95a9ecec0e5644378955df58485a52103664879f7fbe0a4e55309",
          "backend/src/main/resources/application-local.yaml": "a9f83af5c15034c2a3e15219c0e39e80d15db4deae77e864f3999216452243e5",
          "backend/src/main/resources/application.yaml": "4761c46d3f79db0632579511eac32ade8f1856703687973ddcb9d324cba5cc6e",
          "backend/src/test/java/io/github/minokim/lumiawiki/TestEnvironmentTests.java": "8343b2e23274a1b28e67e6bafbcd49a240df72e7c589da046e5e781ca7ecaff0",
          "backend/src/test/resources/application-test.yaml": "bfeb67bd9ba26be9c9b36ee76324032a25e5bbfe205e0302b308c89cce14a344",
          "frontend/package-lock.json": "f6d02d40aeb012b0164f0b505385de31fa5a35764a3d667133ccd50392cf8e89",
          "frontend/package.json": "203230a9a507a41820c1e2273a8f8e5f9e7156cb3cea11d39aef903b36a7f6f8",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "85133eb3283ec0c8336044e60bea2150cc6203e6f8cc33f17c81882aaafe41ae",
          "frontend/vitest.config.mjs": "2df5221cb23b6db0a9b6377e300187806b4ec405cab5bc076c9777f3fb3d5aa0",
          "package-lock.json": null,
          "package.json": null,
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": true
      }
    },
    {
      "id": "foundation-api-contract",
      "kind": "behavior",
      "spec": "763efd6af00c48525ef36537982c799d5f28bcfea0f853b3da5acc3d336cb060",
      "worktree": "f8f58622827de84fd0e6",
      "baseline": "21dd44fedf36f4416d0b74e8df383e0afb624294",
      "task": "work/records/phase-001/issue-42/artifacts/task-003-tdd.md",
      "finished": true,
      "red": {
        "runId": "7829fe32f7af433caca454648b2926df",
        "started": 1794480815.016401,
        "finishedAt": 1794480829.0764987,
        "command": [
          "backend/gradlew.bat",
          "-p",
          "backend",
          "--no-daemon",
          "--max-workers=2",
          "-Dorg.gradle.jvmargs=-Xms64m -Xmx256m -XX:MaxMetaspaceSize=256m",
          "test",
          "--tests",
          "io.github.minokim.lumiawiki.FoundationApiTests",
          "-PtddReportDir={report}"
        ],
        "exitCode": 1,
        "result": {
          "tests": 7,
          "failures": 7,
          "errors": 0,
          "skipped": 0,
          "names": [
            "io.github.minokim.lumiawiki.FoundationApiTests.internalFailureRedactsResponsesAndLogs()",
            "io.github.minokim.lumiawiki.FoundationApiTests.unsupportedMethodKeeps405()",
            "io.github.minokim.lumiawiki.FoundationApiTests.normalAndEmptyResponsesHaveServerOwnedRequestIds()",
            "io.github.minokim.lumiawiki.FoundationApiTests.slowResponseUsesOneSecondDelay()",
            "io.github.minokim.lumiawiki.FoundationApiTests.badInputAndMissingUseProblemDetail()",
            "io.github.minokim.lumiawiki.FoundationApiTests.mvcValidationAndParsingRemain400()",
            "io.github.minokim.lumiawiki.FoundationApiTests.profileGatesDevEndpoint()"
          ],
          "failedNames": [
            "io.github.minokim.lumiawiki.FoundationApiTests.internalFailureRedactsResponsesAndLogs()",
            "io.github.minokim.lumiawiki.FoundationApiTests.unsupportedMethodKeeps405()",
            "io.github.minokim.lumiawiki.FoundationApiTests.normalAndEmptyResponsesHaveServerOwnedRequestIds()",
            "io.github.minokim.lumiawiki.FoundationApiTests.slowResponseUsesOneSecondDelay()",
            "io.github.minokim.lumiawiki.FoundationApiTests.badInputAndMissingUseProblemDetail()",
            "io.github.minokim.lumiawiki.FoundationApiTests.mvcValidationAndParsingRemain400()",
            "io.github.minokim.lumiawiki.FoundationApiTests.profileGatesDevEndpoint()"
          ]
        },
        "manifest": {
          ".codex/hooks.json": "c9919a89f613c6c4ed0602d5ce108634c6442eaff1b8b3929162dd88c161a0f8",
          ".gitattributes": null,
          "backend/build.gradle": "b1faa0d24d9a3440b6c9ceb0c9a7673167ff401145d5b250c3293e7810d745b9",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/java/io/github/minokim/lumiawiki/common/api/ApiExceptionAdvice.java": "fccda07ff5b229c3412bb634195cbdccc26bc0c32392ff591069d184077fcc73",
          "backend/src/main/java/io/github/minokim/lumiawiki/common/api/ApiFailure.java": null,
          "backend/src/main/java/io/github/minokim/lumiawiki/common/api/RequestIdFilter.java": "a81bb2c80080236e6773a593b37bfd63c40ced73db77e3726b7b253c6a79e2d1",
          "backend/src/main/java/io/github/minokim/lumiawiki/dev/FoundationController.java": "b6b8affcdab97448733bab7d8ab0e4af5d026bc19e8cd6d1b3e500b3a4715f7b",
          "backend/src/main/java/io/github/minokim/lumiawiki/dev/FoundationResponse.java": null,
          "backend/src/main/java/io/github/minokim/lumiawiki/dev/FoundationService.java": "96d53909efe95a9ecec0e5644378955df58485a52103664879f7fbe0a4e55309",
          "backend/src/main/resources/application-local.yaml": "a9f83af5c15034c2a3e15219c0e39e80d15db4deae77e864f3999216452243e5",
          "backend/src/main/resources/application.yaml": "4761c46d3f79db0632579511eac32ade8f1856703687973ddcb9d324cba5cc6e",
          "backend/src/test/java/io/github/minokim/lumiawiki/FoundationApiTests.java": "9f3268247d29ca45eee0803fc21dc8a8b3126bc8981ff04a943518571944a52e",
          "backend/src/test/resources/application-test.yaml": "bfeb67bd9ba26be9c9b36ee76324032a25e5bbfe205e0302b308c89cce14a344",
          "frontend/package-lock.json": "f6d02d40aeb012b0164f0b505385de31fa5a35764a3d667133ccd50392cf8e89",
          "frontend/package.json": "203230a9a507a41820c1e2273a8f8e5f9e7156cb3cea11d39aef903b36a7f6f8",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "85133eb3283ec0c8336044e60bea2150cc6203e6f8cc33f17c81882aaafe41ae",
          "frontend/vitest.config.mjs": "2df5221cb23b6db0a9b6377e300187806b4ec405cab5bc076c9777f3fb3d5aa0",
          "package-lock.json": null,
          "package.json": null,
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": false
      },
      "final": {
        "runId": "3638df142d5e44498205186ac1138471",
        "started": 1794480881.283038,
        "finishedAt": 1794480928.14274,
        "command": [
          "backend/gradlew.bat",
          "-p",
          "backend",
          "--no-daemon",
          "--max-workers=2",
          "-Dorg.gradle.jvmargs=-Xms64m -Xmx256m -XX:MaxMetaspaceSize=256m",
          "test",
          "--tests",
          "io.github.minokim.lumiawiki.FoundationApiTests",
          "-PtddReportDir={report}"
        ],
        "exitCode": 0,
        "result": {
          "tests": 7,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "names": [
            "io.github.minokim.lumiawiki.FoundationApiTests.internalFailureRedactsResponsesAndLogs()",
            "io.github.minokim.lumiawiki.FoundationApiTests.unsupportedMethodKeeps405()",
            "io.github.minokim.lumiawiki.FoundationApiTests.normalAndEmptyResponsesHaveServerOwnedRequestIds()",
            "io.github.minokim.lumiawiki.FoundationApiTests.slowResponseUsesOneSecondDelay()",
            "io.github.minokim.lumiawiki.FoundationApiTests.badInputAndMissingUseProblemDetail()",
            "io.github.minokim.lumiawiki.FoundationApiTests.mvcValidationAndParsingRemain400()",
            "io.github.minokim.lumiawiki.FoundationApiTests.profileGatesDevEndpoint()"
          ],
          "failedNames": []
        },
        "manifest": {
          ".codex/hooks.json": "c9919a89f613c6c4ed0602d5ce108634c6442eaff1b8b3929162dd88c161a0f8",
          ".gitattributes": null,
          "backend/build.gradle": "b1faa0d24d9a3440b6c9ceb0c9a7673167ff401145d5b250c3293e7810d745b9",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/java/io/github/minokim/lumiawiki/common/api/ApiExceptionAdvice.java": "7c6c4e6269254479d4ce6b992b8f8804e576467acffa3a4928f44102ee1585ea",
          "backend/src/main/java/io/github/minokim/lumiawiki/common/api/ApiFailure.java": "7732d755d4fe225b46ffb0ba71678a91ffa744bf764154f73bb6106fd88a59e8",
          "backend/src/main/java/io/github/minokim/lumiawiki/common/api/RequestIdFilter.java": "5ffd968c48ae1f28da4745433aad8118acb3b189aa1fff5684d42f442f2f5c30",
          "backend/src/main/java/io/github/minokim/lumiawiki/dev/FoundationController.java": "24893bb3b9c11ead2c2fb488934b652f087c9a2eedbe76e033f11da886e3bd7d",
          "backend/src/main/java/io/github/minokim/lumiawiki/dev/FoundationResponse.java": "da5d930609bc7dbe634ff92bdc5f0d66dd9016a43d8649bc08a24c93c43bd390",
          "backend/src/main/java/io/github/minokim/lumiawiki/dev/FoundationService.java": "68ce1698d17b6ca681dc1883c8ee5091ddc827e6d350e2e00e33183adabda32b",
          "backend/src/main/resources/application-local.yaml": "3fe6ad5fdaa38b33adb58f86c546ee9f8f76b15bca91eaf0149aec9120c1af44",
          "backend/src/main/resources/application.yaml": "d10d1ef05ddbec053c30bf2bc705e4c5f19a2b688baccd61a4f48af556bb40e0",
          "backend/src/test/java/io/github/minokim/lumiawiki/FoundationApiTests.java": "9f3268247d29ca45eee0803fc21dc8a8b3126bc8981ff04a943518571944a52e",
          "backend/src/test/resources/application-test.yaml": "e6aa7eb8da29c749b63e7330c634631d82f8710dc4fb6dee5ef883df1ce12e72",
          "frontend/package-lock.json": "f6d02d40aeb012b0164f0b505385de31fa5a35764a3d667133ccd50392cf8e89",
          "frontend/package.json": "203230a9a507a41820c1e2273a8f8e5f9e7156cb3cea11d39aef903b36a7f6f8",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "85133eb3283ec0c8336044e60bea2150cc6203e6f8cc33f17c81882aaafe41ae",
          "frontend/vitest.config.mjs": "2df5221cb23b6db0a9b6377e300187806b4ec405cab5bc076c9777f3fb3d5aa0",
          "package-lock.json": null,
          "package.json": null,
          "scripts/tdd-check.py": "6e2be41bfa97471f7d213de8c927fc7189fb27bb5864708d3e8d51444f49934d",
          "scripts/tdd-run.py": "d866be6895e8d146d28d7a0280dca62f403173365d0962cdf586c83258ec8010",
          "scripts/tdd_core.py": "af70059b700e486d37f0a2c7329b36d92c9ea90d9a312be2a020a60fa490dc87",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c"
        },
        "ok": true
      }
    },
    {
      "id": "web-final-candidate",
      "kind": "correction",
      "spec": "b3305da656c1d547ac6c4fc49ce92f32ed02cf40c8408beeebce143f3e8e82cf",
      "worktree": "f8f58622827de84fd0e6",
      "finished": true,
      "baseline": "21dd44fedf36f4416d0b74e8df383e0afb624294",
      "task": "work/records/phase-001/issue-42/artifacts/task-003-tdd.md",
      "final": {
        "runId": "8de1b74db902466a87646a2ca791f904",
        "started": 1794481005.6028433,
        "finishedAt": 1794481018.949757,
        "command": [
          "node",
          "frontend/node_modules/vitest/vitest.mjs",
          "run",
          "--root",
          "frontend",
          "--reporter=json",
          "--outputFile={report}"
        ],
        "exitCode": 0,
        "result": {
          "tests": 13,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "names": [
            "runs queries only on submit and shows loading then response",
            "changing scenario cancels stale work and shows independent empty and error states",
            "provides two navigable screens and restores back navigation",
            "fetches relative JSON without forwarding request bodies",
            "turns ProblemDetail into a safe HTTP error",
            "does not expose non JSON failure bodies",
            "separates cancellation network failure and timeout",
            "keeps timeout active while reading response body",
            "rejects paths outside the API boundary",
            "resolves images under the app base and rejects unsafe paths",
            "falls back once and recovers when the image path changes",
            "DOM test environment runs a React interaction using user-event and jest-dom assertions",
            "DOM test environment cleans the previous DOM and starts with independent component state"
          ],
          "failedNames": []
        },
        "manifest": {
          ".codex/hooks.json": "c9919a89f613c6c4ed0602d5ce108634c6442eaff1b8b3929162dd88c161a0f8",
          ".gitattributes": null,
          "backend/build.gradle": "b1faa0d24d9a3440b6c9ceb0c9a7673167ff401145d5b250c3293e7810d745b9",
          "backend/gradle/wrapper/gradle-wrapper.properties": "ce6651f61cd5c8827ffa10f4ebc400d9363745b0de5616cc4fc8140627c6a943",
          "backend/settings.gradle": "46d05a549b9d8eb3fd16af7d914377c9bf1bce8d234f941b210838b54eaa1bb9",
          "backend/src/main/resources/application.yaml": "d10d1ef05ddbec053c30bf2bc705e4c5f19a2b688baccd61a4f48af556bb40e0",
          "backend/src/test/resources/application-test.yaml": "e6aa7eb8da29c749b63e7330c634631d82f8710dc4fb6dee5ef883df1ce12e72",
          "frontend/package-lock.json": "f6d02d40aeb012b0164f0b505385de31fa5a35764a3d667133ccd50392cf8e89",
          "frontend/package.json": "203230a9a507a41820c1e2273a8f8e5f9e7156cb3cea11d39aef903b36a7f6f8",
          "frontend/src/app/App.tsx": "c0dafb2f9d00d9b18335e238c4521e9a13d238d55a8a24b771d24ef755b0d17a",
          "frontend/src/app/queryClient.ts": "aac7cb60992f7f1a0dbccb5145a1e5559b35e5355f2214ce2291ac3e9a683524",
          "frontend/src/dev/FoundationPage.tsx": "716bc2db0383b252e45ae5a3fff670e2c0732510665d9e68a968dcab75337a03",
          "frontend/src/dev/NavigationPage.tsx": "448852e59a2bbd9b1b5ba73fa6696f3fbda1836aac8b8fd9bbfba1eb70b27a01",
          "frontend/src/dev/foundation.test.tsx": "6e835b620e42861939d916ee0335553389388e247f1dd4d09d6a548a28d452aa",
          "frontend/src/dev/routes.ts": "03bc24e876702a1a1a1a77f908d921654d3a8c409d48dcaa3ce8bd1d312c1eca",
          "frontend/src/main.tsx": "55e23958b3629135cea5953191761548b9d7f5e607f6e7ca9b204f6a9b1f9159",
          "frontend/src/shared/api.ts": "2fb6e8408fd6139e1aab5fc9bf38988da09b35326a775bbca031563cd57ca3ab",
          "frontend/src/shared/boundaries.test.tsx": "b571dd5d4c48c2307c44b1fa7e2298b4e91f2455105d2beb2f35dfcb8d243491",
          "frontend/src/shared/images.tsx": "331ada9ff78e72b4015cde518f6b019c87e8896c7f5e21c58190c9c21c4fafbf",
          "frontend/src/test/environment.test.tsx": "1f529250a834f10781925a0e7e042a88a40c60f758dc60cefde671b12e21776c",
          "frontend/src/test/setup.ts": "268e7200d092daa3225eb06790ed72842e5d3234a53980c90ff463d7b81528d3",
          "frontend/tsconfig.json": "a95c02606228195fa68a509c2f5c0102c92a084db2b9261dfd73e5631e07fb21",
          "frontend/vite.config.mjs": "85133eb3283ec0c8336044e60bea2150cc6203e6f8cc33f17c81882aaafe41ae",
          "frontend/vitest.config.mjs": "2df5221cb23b6db0a9b6377e300187806b4ec405cab5bc076c9777f3fb3d5aa0",
          "package-lock.json": null,
          "package.json": null,
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
