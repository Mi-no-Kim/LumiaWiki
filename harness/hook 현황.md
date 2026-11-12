# hook 현황

<a id="current"></a>

<!-- inventory-table -->
| 항목·원천 | 적용 조건 | 동작 | 확인 상태 |
|---|---|---|---|
| [현황 검사 · Git pre-commit](<../scripts/hooks/pre-commit>) | Git 커밋 전; 기존 hook 성공 후 | 스킬·hook 현황 누락·불일치 시 커밋 차단 | 확인 |
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
      "files": ["scripts/check-harness-inventory.py", "scripts/harness_inventory.py", "scripts/hooks/pre-commit", "scripts/install-harness-hooks.py"],
      "sourceDigest": "1ef9e02865cd813e5fbd2bca337ddf1011246e490e1ea0a5cfe9c910183c276b",
      "title": "현황 검사 · Git pre-commit",
      "purpose": "스킬·hook 현황 누락·불일치 시 커밋 차단",
      "when": "Git 커밋 전; 기존 hook 성공 후",
      "verification": {"status": "verified", "sourceDigest": "1ef9e02865cd813e5fbd2bca337ddf1011246e490e1ea0a5cfe9c910183c276b", "environment": "Windows / Python 3.14.2", "scope": "날짜 없는 후보·원천 불일치·날짜 필드 거부; 설치/복원 회귀", "evidence": "work/records/harness/issue-55/verification.md#document-structure"}
    }
  ]
}
```

</details>
