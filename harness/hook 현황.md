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
      "sourceDigest": "38db9a0467e81b67290a91f6dfb395a9f6f4554645a493aa67689a65318243ef",
      "title": "현황 검사 · Git pre-commit",
      "purpose": "스킬·hook 현황 누락·불일치 시 커밋 차단",
      "when": "Git 커밋 전; 기존 hook 성공 후",
      "verification": {"status": "verified", "sourceDigest": "38db9a0467e81b67290a91f6dfb395a9f6f4554645a493aa67689a65318243ef", "date": "2026-11-12", "environment": "Windows / Python 3.14.2", "scope": "로컬 후보·34개 회귀·실제 Git hook 정상/거부·설치/복원", "evidence": "work/records/harness/issue-55/issue.md#catalog-split"}
    }
  ]
}
```

</details>
