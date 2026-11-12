# hook 현황

<a id="current"></a>

<!-- inventory-table -->
| 항목·원천 | 적용 조건 | 동작 | 확인 상태 |
|---|---|---|---|
| [편집 TDD 검사 · Codex PreToolUse](<../.codex/hooks.json>) | PreToolUse / ^apply_patch$; 프로젝트·hook 신뢰 필요 | 유효한 Red/예외 없는 apply_patch 편집 거부 | 확인 |
| [제출 TDD·현황 검사 · Git pre-commit](<../scripts/hooks/pre-commit>) | Git 커밋 전; TDD hook이 연결된 현재 구성 | 기존 TDD 검사 후 현황 누락·불일치 시 커밋 차단 | 확인 |
<!-- /inventory-table -->

<details>
<summary>검사용 데이터</summary>

<!-- harness-inventory -->
```json
{
  "schema": 1,
  "entries": [
    {
      "id": "git:pre-commit",
      "kind": "git",
      "definition": "scripts/hooks/pre-commit",
      "files": [
        "scripts/check-harness-inventory.py",
        "scripts/harness_inventory.py",
        "scripts/hooks/pre-commit",
        "scripts/install-harness-hooks.py",
        "scripts/install-hooks.py",
        "scripts/tdd-check.py",
        "scripts/tdd_core.py"
      ],
      "sourceDigest": "cdf8fe8e8a9b7e3056bd7bc104ab836097c9c831a80e67e0de6f806a2368d883",
      "title": "제출 TDD·현황 검사 · Git pre-commit",
      "purpose": "기존 TDD 검사 후 현황 누락·불일치 시 커밋 차단",
      "when": "Git 커밋 전; TDD hook이 연결된 현재 구성",
      "verification": {
        "status": "verified",
        "sourceDigest": "cdf8fe8e8a9b7e3056bd7bc104ab836097c9c831a80e67e0de6f806a2368d883",
        "environment": "Windows / Python 3.14.2 / 실제 설치 hook",
        "scope": "설치된 TDD→현황 연결: 정상 허용·TDD 불일치/현황 불일치 거부; 기존 wrapper·metadata 보존",
        "evidence": "work/records/phase-001/issue-42/task-002.md#parent-integration"
      }
    },
    {
      "id": "codex:.codex/hooks.json:PreToolUse:0:0",
      "kind": "codex",
      "definition": ".codex/hooks.json",
      "files": [
        ".codex/hooks.json",
        "scripts/tdd-check.py",
        "scripts/tdd_core.py"
      ],
      "sourceDigest": "47635e3b58ceef8809750c2d2218aa1cae07aeb2d06c87e1586837a8ca0a6a96",
      "title": "편집 TDD 검사 · Codex PreToolUse",
      "purpose": "유효한 Red/예외 없는 apply_patch 편집 거부",
      "when": "PreToolUse / ^apply_patch$; 프로젝트·hook 신뢰 필요",
      "verification": {
        "status": "verified",
        "sourceDigest": "47635e3b58ceef8809750c2d2218aa1cae07aeb2d06c87e1586837a8ca0a6a96",
        "environment": "Windows / Python 3.14.2 / 실제 설치 hook",
        "scope": "실제 apply_patch 무근거 거부·파일 부재; 동일 정의/실행기의 기존 Red 허용·Green 후 거부 근거 재사용",
        "evidence": "work/records/phase-001/issue-42/task-002.md#parent-integration"
      }
    }
  ]
}
```

</details>
