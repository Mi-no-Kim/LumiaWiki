# hook 현황

<a id="current"></a>

<!-- inventory-table -->

| 항목·원천                                                                         | 적용 조건                                                  | 동작                                                                                | 확인 상태   |
| --------------------------------------------------------------------------------- | ---------------------------------------------------------- | ----------------------------------------------------------------------------------- | ----------- |
| [변경 파일 포맷 · Codex PostToolUse](../.codex/hooks.json)                        | PostToolUse / ^apply_patch$; 도구 사전 설치·정의 신뢰 필요 | 허용 변경 파일만 포맷; 실패는 제출 미확인으로 보존                                  | 재확인 필요 |
| [공통 기록 주석·상태 · Codex PostToolUse](../.codex/hooks.json)                   | 로컬 대화·실행에서 신뢰한 hook의 지원 도구 종료 후(동기)   | 기존 명시 보호와 신규 Issue·Task·수행 기록 자동 검사·피드백; 자동 원복 없음         | 재확인 필요 |
| [편집 TDD 검사 · Codex PreToolUse](../.codex/hooks.json)                          | PreToolUse / ^apply_patch$; 프로젝트·hook 신뢰 필요        | 유효한 Red/예외 없는 apply_patch 편집 거부                                          | 재확인 필요 |
| [자동 닫기 표현 검사 · Git commit-msg](../scripts/hooks/commit-msg)               | Git 커밋 메시지 확정 시; 기존 사용자 hook 성공 후          | 최종 메시지의 닫기 키워드·Issue 참조 결합 거부                                      | 확인        |
| [제출 TDD·품질·현황·기록·주석 검사 · Git pre-commit](../scripts/hooks/pre-commit) | Git 커밋 전; 연결된 기존 사용자/TDD hook 성공 후           | 기존 hook을 먼저 실행하고 현황·기록·품질·공통 주석/상태를 확인; 고정 기존 기록 보존 | 재확인 필요 |

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
      "sourceDigest": "122347595d31017a9da6dadd7018da41ca903f0b40ea22bb3fb59fac0e282192",
      "title": "변경 파일 포맷 · Codex PostToolUse",
      "purpose": "허용 변경 파일만 포맷; 실패는 제출 미확인으로 보존",
      "when": "PostToolUse / ^apply_patch$; 도구 사전 설치·정의 신뢰 필요",
      "verification": {
        "status": "stale",
        "sourceDigest": "53386923de8863ae35e9ffdbeea95c39412407e85419759deac8fc8698daf9b6",
        "environment": "Windows / current Codex apply_patch / Node 24.22.3 / prepared Gradle 9.9.1 / JDK 21",
        "scope": "사용자 검토·신뢰 후 실제 apply_patch 네 호출로 JSON/Java 생성·수정·포맷된 입력 반복을 확인했다. 패치 밖 두 대조 파일 바이트 유지·새 event receipt 4개·실패 marker 불변·기존 TDD 실제 거부와 probe 제거를 확인했다.",
        "evidence": "work/records/phase-001/issue-42/artifacts/task-004-implementation.md#host-verification"
      }
    },
    {
      "id": "codex:.codex/hooks.json:PostToolUse:1:0",
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
      "sourceDigest": "2329143a8ea6fe5b64d3ac3fb92f687dc707aa186648d2befd0113d8b20e09b7",
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
      "id": "codex:.codex/hooks.json:PreToolUse:0:0",
      "kind": "codex",
      "definition": ".codex/hooks.json",
      "files": [
        ".codex/hooks.json",
        "scripts/tdd-check.py",
        "scripts/tdd_core.py"
      ],
      "sourceDigest": "7df18af01bbdc0c8c0868c8d716d89dbe6cfe3f16c956f694ddae4d89980c7ce",
      "title": "편집 TDD 검사 · Codex PreToolUse",
      "purpose": "유효한 Red/예외 없는 apply_patch 편집 거부",
      "when": "PreToolUse / ^apply_patch$; 프로젝트·hook 신뢰 필요",
      "verification": {
        "status": "stale",
        "sourceDigest": "83e810f55efc694b6cd24ee19ec99d4d00c5500785387c385a4293e3a52b466c",
        "environment": "Windows / Python 3.14.2 / actual apply_patch",
        "scope": "같은 PreToolUse handler와 TDD 의존을 보존했다. 현재 Task의 실제 apply_patch를 무효한 예외 spec으로 거부하고, 새 유효한 예외를 등록·활성화한 뒤 허용했다. 기존 Red/Green 거부 의미는 동일 handler의 Task 002 근거와 현재 전체 fixture로 확인한다.",
        "evidence": "work/records/phase-001/issue-42/artifacts/task-004-implementation.md#verification"
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
      "sourceDigest": "456cf2482a51efd024df9d8291357238302378cfd6c19b191e0a4c1d50f2bbfb",
      "title": "자동 닫기 표현 검사 · Git commit-msg",
      "purpose": "최종 메시지의 닫기 키워드·Issue 참조 결합 거부",
      "when": "Git 커밋 메시지 확정 시; 기존 사용자 hook 성공 후",
      "verification": {
        "status": "verified",
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
        ".prettierrc.json",
        "backend/build.gradle",
        "backend/gradle/wrapper/gradle-wrapper.jar",
        "backend/gradle/wrapper/gradle-wrapper.properties",
        "backend/gradlew",
        "backend/gradlew.bat",
        "backend/settings.gradle",
        "harness/examples/issue-body-example-42.md",
        "harness/examples/task-body-example-43-002.md",
        "harness/examples/task-body-example-db-method.md",
        "harness/examples/task-body-example-recording.md",
        "harness/examples/task-execution-example.md",
        "harness/rule-comments.json",
        "harness/templates/issue.md",
        "harness/templates/task-execution.md",
        "harness/templates/task.md",
        "package-lock.json",
        "package.json",
        "scripts/check-harness-inventory.py",
        "scripts/check-issue-rule-comments.py",
        "scripts/check-rule-comments.py",
        "scripts/check-work-records.py",
        "scripts/harness_inventory.py",
        "scripts/hooks/pre-commit",
        "scripts/install-harness-hooks.py",
        "scripts/install-hooks.py",
        "scripts/issue_rule_comments.py",
        "scripts/quality/format.mjs",
        "scripts/quality/paths.mjs",
        "scripts/quality/process.mjs",
        "scripts/rule_comments.py",
        "scripts/tdd-check.py",
        "scripts/tdd_core.py"
      ],
      "sourceDigest": "68bb37e4f0453d8c47854843cd550bb1c986cb3510e4c6fb0d1ad9fb1705a822",
      "title": "제출 TDD·품질·현황·기록·주석 검사 · Git pre-commit",
      "purpose": "기존 hook을 먼저 실행하고 현황·기록·품질·공통 주석/상태를 확인; 고정 기존 기록 보존",
      "when": "Git 커밋 전; 연결된 기존 사용자/TDD hook 성공 후",
      "verification": {
        "status": "stale",
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
