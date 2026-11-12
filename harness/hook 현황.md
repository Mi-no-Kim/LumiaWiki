# hook 현황

<a id="current"></a>

<!-- inventory-table -->
| 항목·원천 | 적용 조건 | 동작 | 확인 상태 |
|---|---|---|---|
| [편집 TDD 검사 · Codex PreToolUse](<../.codex/hooks.json>) | PreToolUse / ^apply_patch$; 프로젝트·hook 신뢰 필요 | 유효한 Red/예외 없는 apply_patch 편집 거부 | 확인 |
| [제출 TDD·현황·기록 검사 · Git pre-commit](<../scripts/hooks/pre-commit>) | Git 커밋 전; TDD hook이 연결된 현재 구성 | 기존 TDD 검사 후 현황 불일치·신규 기록 위반 차단; Task·Issue 100줄 초과는 경고 | 확인 |
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
        "scripts/check-work-records.py",
        "scripts/harness_inventory.py",
        "scripts/hooks/pre-commit",
        "scripts/install-harness-hooks.py",
        "scripts/install-hooks.py",
        "scripts/tdd-check.py",
        "scripts/tdd_core.py"
      ],
      "sourceDigest": "0bf0a560143cf0bfd4359194691fb83ae6e073257b5beb93489444f1cd3207aa",
      "title": "제출 TDD·현황·기록 검사 · Git pre-commit",
      "purpose": "기존 TDD 검사 후 현황 불일치·신규 기록 위반 차단; Task·Issue 100줄 초과는 경고",
      "when": "Git 커밋 전; TDD hook이 연결된 현재 구성",
      "verification": {
        "status": "verified",
        "sourceDigest": "0bf0a560143cf0bfd4359194691fb83ae6e073257b5beb93489444f1cd3207aa",
        "environment": "Windows / Python 3.14.2 / 격리 Git fixture",
        "scope": "결합 후보의 현황 work/index 읽기 전용, 이전 hook 거부 유지, 기록 검사 이전 브랜치 호환/미스테이징 삭제 거부, 날짜 차단/101줄 경고 성공의 4개 실제 사례. TDD wrapper 자체는 Task 002의 동일 입력 근거 재사용.",
        "evidence": "work/records/phase-001/issue-42/artifacts/task-003-tdd.md"
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
        "evidence": "work/records/phase-001/issue-42/artifacts/task-002-verification.md#parent-integration"
      }
    }
  ]
}
```

</details>
