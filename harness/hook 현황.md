# hook 현황

<a id="current"></a>

<!-- inventory-table -->
| 항목·원천 | 적용 조건 | 동작 | 확인 상태 |
|---|---|---|---|
| [공통 기록 주석·상태 · Codex PostToolUse](<../.codex/hooks.json>) | 로컬 대화·실행에서 신뢰한 hook의 지원 도구 종료 후(동기) | 기존 명시 보호와 신규 Issue·Task·수행 기록 자동 검사·피드백; 자동 원복 없음 | 재확인 필요 |
| [자동 닫기 표현 검사 · Git commit-msg](<../scripts/hooks/commit-msg>) | Git 커밋 메시지 확정 시; 기존 사용자 hook 성공 후 | 최종 메시지의 닫기 키워드·Issue 참조 결합 거부 | 재확인 필요 |
| [현황·기록·공통 주석 검사 · Git pre-commit](<../scripts/hooks/pre-commit>) | Git 커밋 전; 기존 사용자 hook 성공 후 | 현황·기록 검사와 기존 보호·신규 주석/상태 검사; 고정 기존 기록은 새 형식 제외 | 재확인 필요 |
| [브랜치 이름과 백업 이력 검사 · Git pre-push](<../scripts/hooks/pre-push>) | Git 푸시 전; 설치한 복제본에서 기존 사용자 hook 성공 후 | 원격 브랜치 대상 이름과 로컬 전용 백업 이력을 검사 | 확인 |
| [로컬 브랜치 이름 검사 · Git reference-transaction](<../scripts/hooks/reference-transaction>) | 로컬 참조 트랜잭션 준비 시; 설치한 복제본에서 기존 사용자 hook 성공 후 | Git이 전달한 로컬 브랜치 생성과 보존 참조를 검사 | 확인 |
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
        "harness/templates/task-plan.md",
        "harness/templates/task-with-plan.md",
        "harness/templates/task.md",
        "scripts/check-issue-rule-comments.py",
        "scripts/check-rule-comments.py",
        "scripts/harness_inventory.py",
        "scripts/issue_rule_comments.py",
        "scripts/rule_comments.py"
      ],
      "sourceDigest": "de6f1be9e13c298501a0ddf1781556d11b765cd54391d5528be28ffab5bfd890",
      "title": "공통 기록 주석·상태 · Codex PostToolUse",
      "purpose": "기존 명시 보호와 신규 Issue·Task·수행 기록 자동 검사·피드백; 자동 원복 없음",
      "when": "로컬 대화·실행에서 신뢰한 hook의 지원 도구 종료 후(동기)",
      "verification": {
        "status": "stale",
        "sourceDigest": "e09d36e9ba8f39ae4f3f95e932b71dd22e0596efa32b21fdefd6effd319c24f3",
        "environment": "Windows / Python 3.14.2 / git version 2.52.0.windows.1",
        "scope": "정식 Task 양식의 중복 start 주석이 현재 로컬 도구 종료 후 수동 호출 전에 자동 거부됐고 피드백을 확인했다. 임시 중복 제거·원복 바이트/지문과 정상 통과를 확인했다. 등록 명령의 격리 호출과 실제 자동 관찰을 구분하며 다른 대화·환경·실패 경로의 완전 차단을 주장하지 않는다.",
        "evidence": "work/records/harness/issue-72/artifacts/formalization-verification.md#hooks"
      }
    },
    {
      "id": "git:commit-msg",
      "kind": "git",
      "definition": "scripts/hooks/commit-msg",
      "files": [
        "scripts/check-github-closing.py",
        "scripts/github_closing.py",
        "scripts/hooks/commit-msg",
        "scripts/install-harness-hooks.py"
      ],
      "sourceDigest": "7e19ef5138ac7e3fce29361b4e29ca58193d113ad21c5da491f5402b86e96314",
      "title": "자동 닫기 표현 검사 · Git commit-msg",
      "purpose": "최종 메시지의 닫기 키워드·Issue 참조 결합 거부",
      "when": "Git 커밋 메시지 확정 시; 기존 사용자 hook 성공 후",
      "verification": {
        "status": "stale",
        "sourceDigest": "456cf2482a51efd024df9d8291357238302378cfd6c19b191e0a4c1d50f2bbfb",
        "environment": "Windows / Python 3.14.2 / Git 2.52.0 / 격리 임시 저장소·현재 로컬 저장소",
        "scope": "신규 회귀 15개로 아홉 키워드·참조·CRLF, PR 제목/본문·전체 커밋 범위·얕은 이력 거부, 실제 commit-msg의 거부/정상 통과와 사용자 hook 수정/실패·복구·다른 hook 보존을 확인했다. 현재 저장소에도 commit-msg를 설치하고 git hook run으로 사고 표현 거부·Refs 통과와 HEAD/index 불변을 확인했다. 원격 CI와 GitHub 닫기 재시험은 이 근거에 포함하지 않는다.",
        "evidence": "work/records/harness/issue-72/issue.md#closing-reference-guard"
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
        "harness/templates/task-plan.md",
        "harness/templates/task-with-plan.md",
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
      "sourceDigest": "5e1b4905043b1475e9405653aa422c7be2dddb2cb52813fce287f8e4be6a921b",
      "title": "현황·기록·공통 주석 검사 · Git pre-commit",
      "purpose": "현황·기록 검사와 기존 보호·신규 주석/상태 검사; 고정 기존 기록은 새 형식 제외",
      "when": "Git 커밋 전; 기존 사용자 hook 성공 후",
      "verification": {
        "status": "stale",
        "sourceDigest": "6fcbef22e6583390405ce277e2f52e45afe7ec53f657cf480311f5ce35aba78e",
        "environment": "Windows / Python 3.14.2 / git version 2.52.0.windows.1",
        "scope": "실제 제출 index로 구성한 격리 전체 회귀 99개로 신규 Task 실제 pre-commit과 CRLF 의존 수집까지 확인했다. 정상 후보·스테이징 주석 삭제 거부·작업 파일만 복구한 위반·정상 index/미스테이징 위반을 구분했다. 기존 hook 연결·복구·부분 구성도 확인했고 실제 설치 wrapper/원래 hook 보존을 대조했다. 실제 index 검사와 별도 검수를 통과했다. 최종 커밋의 hook 실행은 Git 제출에서 확인하며 CI·원격은 수행하지 않았다.",
        "evidence": "work/records/harness/issue-72/artifacts/formalization-verification.md#hooks"
      }
    },
    {
      "id": "git:pre-push",
      "kind": "git",
      "definition": "scripts/hooks/pre-push",
      "files": [
        "scripts/check-branch-names.py",
        "scripts/hooks/pre-push",
        "scripts/install-harness-hooks.py"
      ],
      "sourceDigest": "c564804ff8b002e8ee4ee731b69876482ca576b0ed2aed9bac6e46ee8c9c2fce",
      "title": "브랜치 이름과 백업 이력 검사 · Git pre-push",
      "purpose": "원격 브랜치 대상 이름과 로컬 전용 백업 이력을 검사",
      "when": "Git 푸시 전; 설치한 복제본에서 기존 사용자 hook 성공 후",
      "verification": {
        "status": "verified",
        "sourceDigest": "c564804ff8b002e8ee4ee731b69876482ca576b0ed2aed9bac6e46ee8c9c2fce",
        "environment": "Windows / Python 3.14.2 / Git 2.52.0.windows.1 / 격리 저장소와 실제 로컬 공용 훅",
        "scope": "격리 전송·복구 검증 후 실제 공용 훅 설치와 정상 대상 허용, 금지 대상·백업 이력 차단을 로컬 입력으로 확인했다. 실제 원격 전송은 수행하지 않았다.",
        "evidence": "work/records/harness/issue-81/artifacts/task-002-execution.md#work-branch-hook-live-install"
      }
    },
    {
      "id": "git:reference-transaction",
      "kind": "git",
      "definition": "scripts/hooks/reference-transaction",
      "files": [
        "scripts/check-branch-names.py",
        "scripts/hooks/reference-transaction",
        "scripts/install-harness-hooks.py"
      ],
      "sourceDigest": "7a02796a835d48436610708659c3df604c81882cd976ac50e3c6a2e73030f1cd",
      "title": "로컬 브랜치 이름 검사 · Git reference-transaction",
      "purpose": "Git이 전달한 로컬 브랜치 생성과 보존 참조를 검사",
      "when": "로컬 참조 트랜잭션 준비 시; 설치한 복제본에서 기존 사용자 hook 성공 후",
      "verification": {
        "status": "verified",
        "sourceDigest": "7a02796a835d48436610708659c3df604c81882cd976ac50e3c6a2e73030f1cd",
        "environment": "Windows / Python 3.14.2 / Git 2.52.0.windows.1 / 격리 저장소와 실제 로컬 공용 훅",
        "scope": "격리 검증 후 실제 공용 훅 설치와 정상 참조 트랜잭션의 준비·중단, 금지 이름과 백업 삭제 거부를 확인했다. 기본 Git 이름 변경의 제한과 검사 명령 검증은 수행 기록에 연결했다.",
        "evidence": "work/records/harness/issue-81/artifacts/task-002-execution.md#work-branch-hook-live-install"
      }
    }
  ]
}
```

</details>
