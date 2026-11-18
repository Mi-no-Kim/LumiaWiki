# hook 현황

<a id="current"></a>

<!-- inventory-table -->
| 항목·원천 | 적용 조건 | 동작 | 확인 상태 |
|---|---|---|---|
| [공통 기록 주석·상태 · Codex PostToolUse](<../.codex/hooks.json>) | 로컬 대화·실행에서 신뢰한 hook의 지원 도구 종료 후(동기) | 기존 명시 보호와 신규 Issue·Task·수행 기록 자동 검사·피드백; 자동 원복 없음 | 확인 |
| [현황·기록·공통 주석 검사 · Git pre-commit](<../scripts/hooks/pre-commit>) | Git 커밋 전; 기존 사용자 hook 성공 후 | 현황·기록 검사와 기존 보호·신규 주석/상태 검사; 고정 기존 기록은 새 형식 제외 | 확인 |
<!-- /inventory-table -->

<details>
<summary>검사용 데이터</summary>

<!-- harness-inventory -->
```json
{
  "schema": 1,
  "entries": [
    {
      "id": "codex:.codex/hooks.json:PostToolUse:0:0",
      "kind": "codex",
      "definition": ".codex/hooks.json",
      "files": [
        ".codex/hooks.json",
        "harness/examples/issue-body-example-42.md",
        "harness/examples/task-body-example-43-002.md",
        "harness/examples/task-body-example-db-method.md",
        "harness/examples/task-body-example-recording.md",
        "harness/examples/task-execution-example.md",
        "harness/rule-comments.json",
        "harness/templates/issue.md",
        "harness/templates/task-execution.md",
        "harness/templates/task.md",
        "scripts/check-issue-rule-comments.py",
        "scripts/check-rule-comments.py",
        "scripts/harness_inventory.py",
        "scripts/issue_rule_comments.py",
        "scripts/rule_comments.py"
      ],
      "sourceDigest": "e09d36e9ba8f39ae4f3f95e932b71dd22e0596efa32b21fdefd6effd319c24f3",
      "title": "공통 기록 주석·상태 · Codex PostToolUse",
      "purpose": "기존 명시 보호와 신규 Issue·Task·수행 기록 자동 검사·피드백; 자동 원복 없음",
      "when": "로컬 대화·실행에서 신뢰한 hook의 지원 도구 종료 후(동기)",
      "verification": {
        "status": "verified",
        "sourceDigest": "e09d36e9ba8f39ae4f3f95e932b71dd22e0596efa32b21fdefd6effd319c24f3",
        "environment": "Windows / Python 3.14.2 / git version 2.52.0.windows.1",
        "scope": "정식 Task 양식의 중복 start 주석이 현재 로컬 도구 종료 후 수동 호출 전에 자동 거부됐고 피드백을 확인했다. 임시 중복 제거·원복 바이트/지문과 정상 통과를 확인했다. 등록 명령의 격리 호출과 실제 자동 관찰을 구분하며 다른 대화·환경·실패 경로의 완전 차단을 주장하지 않는다.",
        "evidence": "work/records/harness/issue-72/artifacts/formalization-verification.md#hooks"
      }
    },
    {
      "id": "git:pre-commit",
      "kind": "git",
      "definition": "scripts/hooks/pre-commit",
      "files": [
        "harness/examples/issue-body-example-42.md",
        "harness/examples/task-body-example-43-002.md",
        "harness/examples/task-body-example-db-method.md",
        "harness/examples/task-body-example-recording.md",
        "harness/examples/task-execution-example.md",
        "harness/rule-comments.json",
        "harness/templates/issue.md",
        "harness/templates/task-execution.md",
        "harness/templates/task.md",
        "scripts/check-harness-inventory.py",
        "scripts/check-issue-rule-comments.py",
        "scripts/check-rule-comments.py",
        "scripts/check-work-records.py",
        "scripts/harness_inventory.py",
        "scripts/hooks/pre-commit",
        "scripts/install-harness-hooks.py",
        "scripts/issue_rule_comments.py",
        "scripts/rule_comments.py"
      ],
      "sourceDigest": "6fcbef22e6583390405ce277e2f52e45afe7ec53f657cf480311f5ce35aba78e",
      "title": "현황·기록·공통 주석 검사 · Git pre-commit",
      "purpose": "현황·기록 검사와 기존 보호·신규 주석/상태 검사; 고정 기존 기록은 새 형식 제외",
      "when": "Git 커밋 전; 기존 사용자 hook 성공 후",
      "verification": {
        "status": "verified",
        "sourceDigest": "6fcbef22e6583390405ce277e2f52e45afe7ec53f657cf480311f5ce35aba78e",
        "environment": "Windows / Python 3.14.2 / git version 2.52.0.windows.1",
        "scope": "실제 제출 index로 구성한 격리 전체 회귀 99개로 신규 Task 실제 pre-commit과 CRLF 의존 수집까지 확인했다. 정상 후보·스테이징 주석 삭제 거부·작업 파일만 복구한 위반·정상 index/미스테이징 위반을 구분했다. 기존 hook 연결·복구·부분 구성도 확인했고 실제 설치 wrapper/원래 hook 보존을 대조했다. 실제 index 검사와 별도 검수를 통과했다. 최종 커밋의 hook 실행은 Git 제출에서 확인하며 CI·원격은 수행하지 않았다.",
        "evidence": "work/records/harness/issue-72/artifacts/formalization-verification.md#hooks"
      }
    }
  ]
}
```

</details>
