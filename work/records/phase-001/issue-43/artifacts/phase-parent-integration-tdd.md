# #43 상위 Phase 반영 검증

Phase `abd92bd`와 #43 `1dc6fa1` 결합의 검사 입력과 실행 근거다. [#43 현황](../../../../현황.md#current)과 연결한다.

<!-- tdd-plan -->
```json
{"schema":1,"cycles":[{"id":"phase-abd92bd-issue43-integration","kind":"correction","reason":"검수한 Phase abd92bd를 #43 1dc6fa1에 결합한다. Phase에서 적용한 공통 검사와 #43 상태·DB 문서 분류를 함께 유지하고 기존 제품·SQL은 보존한다.","targets":[".agents/skills/create-issue/SKILL.md",".agents/skills/create-task/SKILL.md",".agents/skills/issue-plan/SKILL.md",".agents/skills/issue-resume/SKILL.md",".agents/skills/issue-run/SKILL.md",".agents/skills/review-work/SKILL.md",".agents/skills/review-work/scripts/check_task_status.py",".agents/skills/review-work/scripts/test_check_task_status.py",".agents/skills/task-plan/SKILL.md",".agents/skills/task-resume/SKILL.md",".agents/skills/task-run/SKILL.md",".codex/hooks.json",".github/workflows/harness-inventory.yml",".github/workflows/java-contract.yml",".github/workflows/quality.yml","scripts/check-issue-rule-comments.py","scripts/check-java-submission.py","scripts/check-java.py","scripts/check-work-records.py","scripts/hooks/pre-commit","scripts/java-contract/backend-input.gradle","scripts/java-contract/build.gradle","scripts/java-contract/settings.gradle","scripts/java-contract/src/main/java/lumia/contract/ContractRunner.java","scripts/java-contract/src/main/java/lumia/contract/HttpMappings.java","scripts/java-contract/src/main/java/lumia/contract/ModuleCheck.java","scripts/java-contract/src/main/java/lumia/contract/SourceReferences.java","scripts/java-contract/src/main/resources/META-INF/services/com.sun.source.util.Plugin","scripts/java-contract/src/test/java/lumia/contract/HttpMappingsTest.java","scripts/java-contract/src/test/java/lumia/contract/ModuleCheckTest.java","scripts/java-contract/src/test/java/lumia/contract/dev/LeakedController.java","scripts/java_guard.py","scripts/quality/paths.mjs","scripts/quality/record-base.py","scripts/rule_comments.py","scripts/tdd-check.py","scripts/tdd-run.py","scripts/tdd_core.py","scripts/tests/test_harness_inventory.py","scripts/tests/test_java_hooks.py","scripts/tests/test_java_submission.py","scripts/tests/test_quality.py","scripts/tests/test_rule_comments.py","scripts/tests/test_tdd_flow.py","scripts/tests/test_work_records.py"],"tests":[],"settings":[],"adapter":"unittest","command":["python","-B","-X","utf8","scripts/test-python.py","--report","{report}","--run-id","{run_id}","--","scripts.tests.test_quality.QualityTests.test_allowlist_and_preservation_before_collection","scripts.tests.test_harness_inventory.HookTests.test_quality_and_comment_checks_both_reject_in_combined_hook","scripts.tests.test_rule_comments.CurrentRecordTests.test_only_new_tasks_require_separate_plan_format"]}]}
```

<!-- tdd-evidence -->
```json
{
  "schema": 1,
  "receipts": [
    {
      "id": "phase-abd92bd-issue43-integration",
      "kind": "correction",
      "spec": "ea8f0c2641c2b4ffedf7536ab6ee3a6a35f84075df28677d52c96179fb079770",
      "worktree": "7c4775212fe7a41dfa7f",
      "finished": true,
      "baseline": "1dc6fa18a22c795f0cb984bee4f4fb4b3a294b48",
      "task": "work/records/phase-001/issue-43/artifacts/phase-parent-integration-tdd.md",
      "final": {
        "runId": "04f5662b24ae4ccdb798bbe030b3c366",
        "started": 1795611382.3615742,
        "finishedAt": 1795611390.4601076,
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
          "scripts.tests.test_quality.QualityTests.test_allowlist_and_preservation_before_collection",
          "scripts.tests.test_harness_inventory.HookTests.test_quality_and_comment_checks_both_reject_in_combined_hook",
          "scripts.tests.test_rule_comments.CurrentRecordTests.test_only_new_tasks_require_separate_plan_format"
        ],
        "exitCode": 0,
        "result": {
          "tests": 3,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "names": [
            "scripts.tests.test_quality.QualityTests.test_allowlist_and_preservation_before_collection",
            "scripts.tests.test_harness_inventory.HookTests.test_quality_and_comment_checks_both_reject_in_combined_hook",
            "scripts.tests.test_rule_comments.CurrentRecordTests.test_only_new_tasks_require_separate_plan_format"
          ],
          "failedNames": []
        },
        "manifest": {
          ".agents/skills/create-issue/SKILL.md": "f0bf15357ae3b6d90195fdbd0cda01e72fc3954a0b323ebe618dcd38905f5a78",
          ".agents/skills/create-task/SKILL.md": "958bbe30d93150f5f62eb8b6e65f12a2cc41caafaf652d7aea96e4e92e061ccb",
          ".agents/skills/issue-plan/SKILL.md": "219dbe09b980545032558b76602e24e98ca789df433fbf06e6d0eabc79ec916c",
          ".agents/skills/issue-resume/SKILL.md": "2f7c0067319b5c915aeaf33d641cd39ecae9067dfc9fa380a9ea6fb916659eb8",
          ".agents/skills/issue-run/SKILL.md": "95473917af88270c016152ffcccc9eb749f970342b5c3c1bfa34644876070bce",
          ".agents/skills/review-work/SKILL.md": "9cec5bf9313b39bb50d8dd643e19e41e04fd01d7e6becbf3ed7d29a81f94197f",
          ".agents/skills/review-work/scripts/check_task_status.py": "56d6bbb083ace18359b5715118a7191c94bea8bb394e6980a172038828888983",
          ".agents/skills/review-work/scripts/test_check_task_status.py": "4328b2e81f05442a2f5d44f96c47e7dc989f9f2acf420ba6b6f0d32e415ef4ad",
          ".agents/skills/task-plan/SKILL.md": "308f0dc01742241c382c8ec1f90a674676d88f06bcd830d7348502ed4cd9bd32",
          ".agents/skills/task-resume/SKILL.md": "6546996d8449197a2a4c3528b71c2ace461f887781691fca3148a7b280b45093",
          ".agents/skills/task-run/SKILL.md": "6aefabc21e31f8919bda1028c58eb28d6aed947f39eb6c91ea4f29ec162043d3",
          ".codex/hooks.json": "36c5f3bbf5d72d14d7dab782abec30032c29487d16f094a1d927dfd863f3750c",
          ".gitattributes": "4437511f6b3b866745490f0fcd2332d1e6194980fc028232ce0a84cec608d85b",
          ".github/workflows/harness-inventory.yml": "98310cd2950ca7032c97546190e46173887ec31d95b7392d5be2f1448370097e",
          ".github/workflows/java-contract.yml": "a6fbb670efd5e809fbe670f7741a8a1df477a71e5dec54453d88ca9dd8caeda8",
          ".github/workflows/quality.yml": "59e7f85ef32d190b300e6f4a5c5dcd1688f8c45d0f7dcda7f353a2c75b60b361",
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
          "scripts/check-issue-rule-comments.py": "a51d7bab93e1dd7b50f7c90f105bfee628fbad9a666f5ffa8e1b153a30abbd05",
          "scripts/check-java-submission.py": "4936443bdee9f10e755e4e7d0ff2cf7ad9b5f90eccd6a6612f07686487325848",
          "scripts/check-java.py": "893d7c5171ebc42c1422c49fccf490d5606d1379075c7829d2642cb78c1cbfed",
          "scripts/check-work-records.py": "b0a14327d73949596fa1faf5d088f126f06ece913dabd8cf7f7ea7beaae4257b",
          "scripts/hooks/pre-commit": "4cb2140beac0bd75350d1b5f176e3c5681944e7c2eaa299fb856bdc6bfd50274",
          "scripts/java-contract/backend-input.gradle": "d8837910a89980d2a9bec20799158476905ef92bb4d078674872d5096808a3fc",
          "scripts/java-contract/build.gradle": "372792ddf4f7cf0a82858245b035f34a2180f06e2862606006acd21926ab46c1",
          "scripts/java-contract/settings.gradle": "bd89da776ce2574546066fdb903df135a8e995bd6e2be4db8b387c337ebd7a39",
          "scripts/java-contract/src/main/java/lumia/contract/ContractRunner.java": "e0ce3d2db5f958ef911fa3d1140887bc5f72e06b9aeb02f3a1583cc59b89edc4",
          "scripts/java-contract/src/main/java/lumia/contract/HttpMappings.java": "c8da285f4a8ed2f810fc6130eaaccc841c1013397dd76c5817b5bb13fd67b793",
          "scripts/java-contract/src/main/java/lumia/contract/ModuleCheck.java": "d8038e4bc8040648b3610c1f99a9f80ad0228bab191e98df9a2b7a3c8a6dc4da",
          "scripts/java-contract/src/main/java/lumia/contract/SourceReferences.java": "cbc1f7dd20c2a52f60aea61c193db9cad7e19864e41460df67d1074b2ae712ee",
          "scripts/java-contract/src/main/resources/META-INF/services/com.sun.source.util.Plugin": "cd84bed6bef36d9e28990b3b0c8a57e1fe560aa2eee284e652ffb9335095b94b",
          "scripts/java-contract/src/test/java/lumia/contract/HttpMappingsTest.java": "6407b48217dd4d57f018ee7384ce6d95c520f35719ba7b68e18b1dff29957a0d",
          "scripts/java-contract/src/test/java/lumia/contract/ModuleCheckTest.java": "575df9b5c1e00010540bcd595856f1939154cd92f46fac466dd1576d2617c375",
          "scripts/java-contract/src/test/java/lumia/contract/dev/LeakedController.java": "e027641c8b207c3cd7d6e00a356b3a97f035c78d08313524e2b8c510b7ea5d2e",
          "scripts/java_guard.py": "adafed912e932f4e892ca0fce30c67eee9e55ec213b31b9043a9ef9f36a70fd7",
          "scripts/quality/paths.mjs": "ac79273db8aee27e019c6d0c7c8fe31edc0cb5dcd2324217d562349d0d00df28",
          "scripts/quality/record-base.py": "630bc1641df14668d5070e838465da63221927eee9bd2db1d18213ab7aa6f32c",
          "scripts/rule_comments.py": "3f62ebb8d861c52ec55080ca3d98d1480ce11c537f7a6df51575b7d647109111",
          "scripts/tdd-check.py": "857781c52c190f94ec186edfa07ba996ed5b80afbc37ab8c68246252e7cfe014",
          "scripts/tdd-run.py": "a65da4989ccf12b5e02b062bb23897c7237a1f3705356786f619392cedc37316",
          "scripts/tdd_core.py": "d1427d46bf0e80087e6943656dfa5391227255a2f21ce488ca52e532807fe068",
          "scripts/test-python.py": "52dc15ac99df8a9d4b861e80aa6fc41dffab7ac064238d5d03c5c51f4febc69c",
          "scripts/tests/test_harness_inventory.py": "5e6493beedfa3d3b9c9e7e88413eca077235021101a92420d7ef17ec9a960b3e",
          "scripts/tests/test_java_hooks.py": "988fdd66547735b8e2e9414d31a3931c87fb142b7d2e8884c82870558bf5280c",
          "scripts/tests/test_java_submission.py": "6fdcc6ba518b35a4f06edd98d705ff199bbc9480cf711c7b0d885a491055ae42",
          "scripts/tests/test_quality.py": "98cc11a4566c594dd6e7067ab3424d75c9a89697866d535f255fccd4f5adf8f9",
          "scripts/tests/test_rule_comments.py": "34ffd5231361188938988d6783f8cc2d8127f01b49be81de5aa0ddd91eb070b1",
          "scripts/tests/test_tdd_flow.py": "66ab9a1373bf80d8b8c3c8dee2007e24785975ad997bd757ae2209721955817b",
          "scripts/tests/test_work_records.py": "458c2713f5aa2b18b1e4664e818c2a4f484753a2097fa9fc9cc5411d0f50ca3b"
        },
        "ok": true
      }
    }
  ]
}
```
