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
      "targets": [".github/workflows/harness-inventory.yml", "scripts/check-work-records.py", "scripts/hooks/pre-commit"],
      "tests": ["scripts/tests/test_harness_inventory.py", "scripts/tests/test_work_records.py"],
      "settings": [],
      "adapter": "unittest",
      "command": ["python", "-B", "-X", "utf8", "scripts/test-python.py", "--report", "{report}", "--run-id", "{run_id}", "--", "discover", "-s", "scripts/tests", "-p", "test_harness_inventory.py", "-k", "test_record_gate", "-k", "test_existing_hook_rejection", "-k", "test_consistent_work_and_index", "-k", "test_branches_predating_record_check", "-v"]
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
    }
  ]
}
```
