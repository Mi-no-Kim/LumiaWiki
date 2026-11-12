# hook 현황

<a id="current"></a>

<!-- inventory-table -->
| 항목·원천 | 적용 조건 | 동작 | 확인 상태 |
|---|---|---|---|
| [현황·기록 검사 · Git pre-commit](<../scripts/hooks/pre-commit>) | Git 커밋 전; 기존 hook 성공 후 | 현황 불일치·신규 기록 위반 차단; Task·Issue 100줄 초과는 경고 | 확인 |
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
        "scripts/install-harness-hooks.py"
      ],
      "sourceDigest": "60b6322d8ea11d970d81445b0f064b043524ce3a6741a0ce8050047ed234ea33",
      "title": "현황·기록 검사 · Git pre-commit",
      "purpose": "현황 불일치·신규 기록 위반 차단; Task·Issue 100줄 초과는 경고",
      "when": "Git 커밋 전; 기존 hook 성공 후",
      "verification": {
        "status": "verified",
        "sourceDigest": "60b6322d8ea11d970d81445b0f064b043524ce3a6741a0ce8050047ed234ea33",
        "environment": "Windows / Python 3.14.2",
        "scope": "새 기록 검사 10개·기존 hook 결합 6개; 실제 별도 index 정상/101줄 경고 성공/날짜 거부·기존 wrapper 보존. 로컬 확인 범위이며 원격 CI는 Issue #60의 연결 PR을 참조. 구버전 브랜치 호환·작업 파일만 삭제한 후보 거부.",
        "evidence": "work/records/harness/issue-60/artifacts/verification.md#verification"
      }
    }
  ]
}
```

</details>
