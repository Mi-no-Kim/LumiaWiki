# hook 현황

<a id="current"></a>

<!-- inventory-table -->

| 항목·원천                                                                    | 적용 조건                                                  | 동작                                                                | 확인 상태 |
| ---------------------------------------------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------- | --------- |
| [변경 파일 포맷 · Codex PostToolUse](../.codex/hooks.json)                   | PostToolUse / ^apply_patch$; 도구 사전 설치·정의 신뢰 필요 | 허용 변경 파일만 포맷; 실패는 제출 미확인으로 보존                  | 확인      |
| [편집 TDD 검사 · Codex PreToolUse](../.codex/hooks.json)                     | PreToolUse / ^apply_patch$; 프로젝트·hook 신뢰 필요        | 유효한 Red/예외 없는 apply_patch 편집 거부                          | 확인      |
| [제출 TDD·현황·기록·형식 검사 · Git pre-commit](../scripts/hooks/pre-commit) | Git 커밋 전; TDD hook이 연결된 현재 구성                   | 기존 hook·TDD·현황·기록 검사 후 인덱스 실행기·내용·설정의 형식 확인 | 확인      |

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
        ".prettierrc.json",
        "backend/build.gradle",
        "backend/gradle/wrapper/gradle-wrapper.jar",
        "backend/gradle/wrapper/gradle-wrapper.properties",
        "backend/gradlew",
        "backend/gradlew.bat",
        "backend/settings.gradle",
        "package-lock.json",
        "package.json",
        "scripts/check-harness-inventory.py",
        "scripts/check-work-records.py",
        "scripts/harness_inventory.py",
        "scripts/hooks/pre-commit",
        "scripts/install-harness-hooks.py",
        "scripts/install-hooks.py",
        "scripts/quality/format.mjs",
        "scripts/quality/paths.mjs",
        "scripts/quality/process.mjs",
        "scripts/tdd-check.py",
        "scripts/tdd_core.py"
      ],
      "sourceDigest": "e48a90f4511bdc12f3adb48f10f35ae49027485af092804b30be259693318222",
      "title": "제출 TDD·현황·기록·형식 검사 · Git pre-commit",
      "purpose": "기존 hook·TDD·현황·기록 검사 후 인덱스 실행기·내용·설정의 형식 확인",
      "when": "Git 커밋 전; TDD hook이 연결된 현재 구성",
      "verification": {
        "status": "verified",
        "sourceDigest": "e48a90f4511bdc12f3adb48f10f35ae49027485af092804b30be259693318222",
        "environment": "Windows / Node 24.22.3 / Python 3.14.2 / current apply_patch and isolated hook/index fixtures",
        "scope": "DB Markdown 포맷/수집·CI 분류 3건과 기존 품질 fixture 20건 통과·파일 symlink 1건 skip. 실제 apply_patch DB 문서 포맷을 확인했다. 변경한 경로 분류/수집 외 hook 정의·인덱스 실행·Java 경로는 동일하며 Task 42-004의 기존 실제 hook 근거를 재사용한다. 저장소 실제 인덱스 변경·커밋 실행은 미수행이다.",
        "evidence": "work/records/phase-001/issue-43/artifacts/task-001-bootstrap-verification.md#database-documents"
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
      "sourceDigest": "83e810f55efc694b6cd24ee19ec99d4d00c5500785387c385a4293e3a52b466c",
      "title": "편집 TDD 검사 · Codex PreToolUse",
      "purpose": "유효한 Red/예외 없는 apply_patch 편집 거부",
      "when": "PreToolUse / ^apply_patch$; 프로젝트·hook 신뢰 필요",
      "verification": {
        "status": "verified",
        "sourceDigest": "83e810f55efc694b6cd24ee19ec99d4d00c5500785387c385a4293e3a52b466c",
        "environment": "Windows / Python 3.14.2 / actual apply_patch",
        "scope": "같은 PreToolUse handler와 TDD 의존을 보존했다. 현재 Task의 실제 apply_patch를 무효한 예외 spec으로 거부하고, 새 유효한 예외를 등록·활성화한 뒤 허용했다. 기존 Red/Green 거부 의미는 동일 handler의 Task 002 근거와 현재 전체 fixture로 확인한다.",
        "evidence": "work/records/phase-001/issue-42/artifacts/task-004-implementation.md#verification"
      }
    },
    {
      "id": "codex:.codex/hooks.json:PostToolUse:0:0",
      "kind": "codex",
      "definition": ".codex/hooks.json",
      "files": [
        ".codex/hooks.json",
        ".prettierrc.json",
        "backend/build.gradle",
        "backend/gradle/wrapper/gradle-wrapper.jar",
        "backend/gradle/wrapper/gradle-wrapper.properties",
        "backend/gradlew",
        "backend/gradlew.bat",
        "backend/settings.gradle",
        "package-lock.json",
        "package.json",
        "scripts/quality/format.mjs",
        "scripts/quality/paths.mjs",
        "scripts/quality/post-edit.mjs",
        "scripts/quality/process.mjs"
      ],
      "sourceDigest": "70e864c41ab8a00dd84c2f8b9f9d619a3e1ddb0f0a553209e622766e7eda0ebc",
      "title": "변경 파일 포맷 · Codex PostToolUse",
      "purpose": "허용 변경 파일만 포맷; 실패는 제출 미확인으로 보존",
      "when": "PostToolUse / ^apply_patch$; 도구 사전 설치·정의 신뢰 필요",
      "verification": {
        "status": "verified",
        "sourceDigest": "70e864c41ab8a00dd84c2f8b9f9d619a3e1ddb0f0a553209e622766e7eda0ebc",
        "environment": "Windows / Node 24.22.3 / Python 3.14.2 / current apply_patch and isolated hook/index fixtures",
        "scope": "DB Markdown 포맷/수집·CI 분류 3건과 기존 품질 fixture 20건 통과·파일 symlink 1건 skip. 실제 apply_patch DB 문서 포맷을 확인했다. 변경한 경로 분류/수집 외 hook 정의·인덱스 실행·Java 경로는 동일하며 Task 42-004의 기존 실제 hook 근거를 재사용한다. 저장소 실제 인덱스 변경·커밋 실행은 미수행이다.",
        "evidence": "work/records/phase-001/issue-43/artifacts/task-001-bootstrap-verification.md#database-documents"
      }
    }
  ]
}
```

</details>
