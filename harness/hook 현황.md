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
      "sourceDigest": "405d577c68409b8f5532eb418e03d17120e706f7e00f469f126a7ffdf01f5d36",
      "title": "제출 TDD·현황·기록·형식 검사 · Git pre-commit",
      "purpose": "기존 hook·TDD·현황·기록 검사 후 인덱스 실행기·내용·설정의 형식 확인",
      "when": "Git 커밋 전; TDD hook이 연결된 현재 구성",
      "verification": {
        "status": "verified",
        "sourceDigest": "405d577c68409b8f5532eb418e03d17120e706f7e00f469f126a7ffdf01f5d36",
        "environment": "Windows / Node 24.22.3 / Python 3.14.2 / JDK 21 / actual installed Git hook",
        "scope": "기존 TDD wrapper 보존 후 정상 actual index 종료 0, 별도 index README 형식 위반 종료 2와 실제 index 불변을 확인했다. staged 실행기·내용·설정을 사용하고 부분 스테이징·원천 현황·이전 hook 공존은 현재 fixture로 확인했다.",
        "evidence": "work/records/phase-001/issue-42/artifacts/task-004-implementation.md#verification"
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
      "sourceDigest": "53386923de8863ae35e9ffdbeea95c39412407e85419759deac8fc8698daf9b6",
      "title": "변경 파일 포맷 · Codex PostToolUse",
      "purpose": "허용 변경 파일만 포맷; 실패는 제출 미확인으로 보존",
      "when": "PostToolUse / ^apply_patch$; 도구 사전 설치·정의 신뢰 필요",
      "verification": {
        "status": "verified",
        "sourceDigest": "53386923de8863ae35e9ffdbeea95c39412407e85419759deac8fc8698daf9b6",
        "environment": "Windows / current Codex apply_patch / Node 24.22.3 / prepared Gradle 9.9.1 / JDK 21",
        "scope": "사용자 검토·신뢰 후 실제 apply_patch 네 호출로 JSON/Java 생성·수정·포맷된 입력 반복을 확인했다. 패치 밖 두 대조 파일 바이트 유지·새 event receipt 4개·실패 marker 불변·기존 TDD 실제 거부와 probe 제거를 확인했다.",
        "evidence": "work/records/phase-001/issue-42/artifacts/task-004-implementation.md#host-verification"
      }
    }
  ]
}
```

</details>
