# 스킬과 hook 현황

<a id="current"></a>
## 현재 구성과 확인 범위

이 문서는 프로젝트가 관리하는 skill·Codex/Git hook의 요약·원천 연결·확인 범위를 관리한다. 상세 규칙은 각 원천에 있고 [갱신 의무](<../docs/문서 관리 기준.md#skill-hook-inventory>)를 따른다. 아래 표는 이 문서의 관리 데이터에서 만든다.

<!-- inventory-table -->
| 종류 | 항목·원천 | 역할·적용 조건 | 확인 상태 |
|---|---|---|---|
| git | [현황 후보 검사](<../scripts/hooks/pre-commit>) | 실제 스테이징 원천과 현황의 누락·불일치를 검사<br>조건: Git 커밋 전; 기존 hook 뒤에 실행 | 확인 |
| skill | [작업 결과 검수](<../.agents/skills/review-work/SKILL.md>) | 작업 결과와 실제 제출 후보의 자체·별도 검수를 연결<br>조건: 검수·리뷰 또는 커밋 준비 | 미확인 |
| skill | [Rundown 응답](<../.agents/skills/rundown/SKILL.md>) | 핵심 결과·상태·다음 행동을 간결하게 전달<br>조건: 프로젝트 지침이 요구하는 사용자 응답 | 미확인 |
| skill | [추가 요청 판단](<../.agents/skills/triage-additional-request/SKILL.md>) | 추가·변경 요청의 작업 소속과 기존 변경 보존을 판단<br>조건: 기존 작업의 추가·변경 요청 착수 전 | 미확인 |
<!-- /inventory-table -->

현재 main 기준에는 프로젝트 Codex hook 정의가 없다. Task 42-002의 정의·검증은 해당 Task 브랜치에 보존돼 있으며 이 브랜치에서 적용된 것으로 표시하지 않는다. 개인·전역·외부 플러그인의 구성은 이 목록의 수집 대상이 아니다.

Git hook의 정의·실행 확인과 각 작업 환경의 설치 여부는 별개다. 실제 로컬 설치 상태는 아래 `--status`로 확인한다. GitHub Actions의 Windows·Ubuntu에서 정상 통과·의도한 원천 불일치 거부·정상 복구 후 통과를 확인했다. Ubuntu에서는 Windows junction 전용 사례가 제외됐다. 병합 필수 상태 검사로 지정하지는 않았다. 실제 실행 근거와 한계는 [Issue #55](<../work/records/harness/issue-55/issue.md#remote-ci>)에서 확인한다.

<a id="maintenance"></a>
## 변경과 제출 전 확인

1. 원천·적용 조건·정의/등록 위치와 의존 파일의 변경을 확인한다. 등록은 `.agents/skills/*/SKILL.md`, `.codex/hooks.json`·`.codex/config.toml`의 handler, `scripts/hooks/`의 표준 Git hook 이름을 기준으로 한다. `scripts/hooks/` 바로 아래는 hook 정의 전용이며 알 수 없는 파일은 조용히 무시하지 않고 분류를 요구한다. 보조 파일은 하위 폴더나 별도 경로에 두고 의존 목록으로 연결한다. skill 폴더의 소스 파일은 함께 수집하고 캐시/생성 환경은 제외한다.
2. 이 문서의 관리 데이터에서 해당 항목의 역할·조건·원천·파일 목록을 갱신한다. Git hook의 의존 파일은 정의 안의 `inventory-dependencies` JSON 목록, Codex hook의 실행기/보조 파일은 해당 항목의 `files`에 명시한다. 프로젝트 `.codex/config.toml`이 존재하면 handler 유무와 관계없이 각 Codex 항목의 필수 원천에 포함해 `features.hooks` 같은 적용 조건 변경을 확인한다. 새로운 등록 위치나 동적 의존이 있으면 판독 규칙과 의미 검수까지 갱신한다. 임의 경로의 의미를 자동 추론하는 검사는 아니다.
3. `--describe`가 반환한 실제 항목·파일·현재 지문을 대조해 `sourceDigest`를 갱신한다. 마지막 확인의 `verification.sourceDigest`는 실제 확인 또는 유효 근거의 재사용 판단에 대응해야 한다. 새 내용에 대한 근거가 없으면 `unverified`, 과거 확인을 보존하면 `stale`로 둔다. `verified`에는 대응 지문·날짜·환경·범위·근거가 모두 필요하다.
4. `--render` 출력으로 같은 문서의 표를 맞추고 work 후보를 확인한다. 필요한 원천과 이 문서를 함께 스테이징한 뒤 index 후보를 확인한다. 파일을 저장한 것과 제출 후보 반영은 구별한다.
5. 검수에서 설명·적용 조건·지정 의존의 충분성과 실제 실행 근거의 유효성을 확인한다. 지문/목록 검사는 이 의미 판단이나 동작 확인을 대체하지 않는다.

```text
python -B -X utf8 scripts/check-harness-inventory.py --candidate work --describe
python -B -X utf8 scripts/check-harness-inventory.py --candidate work --render
python -B -X utf8 scripts/check-harness-inventory.py --candidate work
python -B -X utf8 scripts/check-harness-inventory.py --candidate index
python -B -X utf8 scripts/check-harness-inventory.py --candidate HEAD
```

검사/출력 명령은 파일·index를 수정하지 않는다. 기본 검사는 index이며 정상은 무출력·종료 0, 불일치·시간 초과·판독 불능은 이유/다음 행동·종료 2다. 명시 대상을 읽고 약 3초의 내부 예산을 두며 Git의 지연 fetch와 Python bytecode 생성을 끈다. 텍스트 지문은 CRLF를 LF로 정규화하고 다른 바이트는 보존한다.

보존·비밀·작업 임시 경로는 접근 전에 거부하며 work의 symlink/junction, index/commit의 링크·미병합 항목은 자동 통과하지 않는다. 전체 저장소/개인 설정·대화 수집, 자동 수정·스테이징·테스트·설치·AI/네트워크 호출은 하지 않는다.

<a id="git-hook"></a>
## Git 연결과 해제

```text
python -B -X utf8 scripts/install-harness-hooks.py --status
python -B -X utf8 scripts/install-harness-hooks.py
python -B -X utf8 scripts/install-harness-hooks.py --remove
```

설치기는 core.hooksPath를 변경하지 않고 유효 위치를 확인한다. 저장소 밖 사용자 위치·reparse point는 자동 수정하지 않는다. 기존 pre-commit의 바이트/모드를 보존해 먼저 실행하고 원천/현황 검사를 뒤에 연결한다. 중복 설치는 무변경이고 자기 wrapper·백업이 그대로일 때만 복원한다. 원래 hook이나 자기 wrapper가 바뀌면 보존·검토 후 처리한다.

버전 관리되는 wrapper 정의가 바뀌면 기존 연결을 `--remove`로 복원한 뒤 설치 명령을 다시 실행해 새 정의를 적용하고 실제 연결을 확인한다. 중첩된 설치기가 있으면 먼저 바깥 wrapper의 해제 순서를 확인한다.

여러 설치기가 중첩되면 바깥 wrapper부터 해제한다. Task 42-002의 TDD wrapper가 기존 hook이면 그 원형과 metadata를 보존한다. 안쪽 TDD 설치기로 바깥 wrapper를 덮어쓰거나 해제하지 않는다. 현황 검사기와 현황 문서가 작업 폴더와 실제 index에 모두 없는 과거 브랜치는 기존 hook을 실행한 뒤 이 검사 단계만 생략한다. index에 구성이 남아 있거나 일부만 누락되면 거부한다. 임의 셸/IDE 편집의 사전 차단이나 로컬 hook의 우회 방지를 보장하지 않는다.

CI도 명시 commit을 같은 검사기로 대조한다. 실제 원격 정상·실패·복구를 확인했으며, 현재 CI와 로컬 hook 설치는 GitHub의 병합 필수 설정이 아니다. 필수 지정은 별도의 권한·설정 확인 대상이다.

<details>
<summary>관리 데이터 — 표·원천 지문과 마지막 확인</summary>

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
        "scripts/install-harness-hooks.py"
      ],
      "sourceDigest": "c3f93d83a554fd8bb5e471f4d278b5c0aca6840555369640a4e1f8e53526a9ef",
      "title": "현황 후보 검사",
      "purpose": "실제 스테이징 원천과 현황의 누락·불일치를 검사",
      "when": "Git 커밋 전; 기존 hook 뒤에 실행",
      "verification": {
        "status": "verified",
        "sourceDigest": "c3f93d83a554fd8bb5e471f4d278b5c0aca6840555369640a4e1f8e53526a9ef",
        "date": "2026-11-12",
        "environment": "Windows 로컬 Python 3.14.2 / GitHub Actions Windows·Ubuntu Python 3.14.10",
        "scope": "로컬 후보·설치/복원·실제 hook·50개 skill 규모 검사; 원격 정상/불일치 거부/정상 복구·도구 31개와 기존 5개 회귀(Ubuntu의 Windows junction 1개 제외); 각 사용자 환경의 설치·병합 필수 지정은 별도",
        "evidence": "work/records/harness/issue-55/issue.md#remote-ci"
      }
    },
    {
      "id": "skill:review-work",
      "kind": "skill",
      "definition": ".agents/skills/review-work/SKILL.md",
      "files": [
        ".agents/skills/review-work/SKILL.md",
        ".agents/skills/review-work/scripts/check_task_status.py",
        ".agents/skills/review-work/scripts/test_check_task_status.py"
      ],
      "sourceDigest": "369319517d2eac78556a28b574eb1d3e34825e4c8236ba8ca4836a7deebb5453",
      "title": "작업 결과 검수",
      "purpose": "작업 결과와 실제 제출 후보의 자체·별도 검수를 연결",
      "when": "검수·리뷰 또는 커밋 준비",
      "verification": {
        "status": "unverified",
        "sourceDigest": null,
        "date": null,
        "environment": null,
        "scope": null,
        "evidence": null
      }
    },
    {
      "id": "skill:rundown",
      "kind": "skill",
      "definition": ".agents/skills/rundown/SKILL.md",
      "files": [
        ".agents/skills/rundown/SKILL.md",
        ".agents/skills/rundown/agents/openai.yaml"
      ],
      "sourceDigest": "09b4ffedf8fe4949bed4e2b8c1e4c7313b591736357b0a75c3b5f22c0747877f",
      "title": "Rundown 응답",
      "purpose": "핵심 결과·상태·다음 행동을 간결하게 전달",
      "when": "프로젝트 지침이 요구하는 사용자 응답",
      "verification": {
        "status": "unverified",
        "sourceDigest": null,
        "date": null,
        "environment": null,
        "scope": null,
        "evidence": null
      }
    },
    {
      "id": "skill:triage-additional-request",
      "kind": "skill",
      "definition": ".agents/skills/triage-additional-request/SKILL.md",
      "files": [
        ".agents/skills/triage-additional-request/SKILL.md"
      ],
      "sourceDigest": "8a9441e96fc77c30bd03d23cfcb7a755b5ec52133a19d0ca2df66250cc02bede",
      "title": "추가 요청 판단",
      "purpose": "추가·변경 요청의 작업 소속과 기존 변경 보존을 판단",
      "when": "기존 작업의 추가·변경 요청 착수 전",
      "verification": {
        "status": "unverified",
        "sourceDigest": null,
        "date": null,
        "environment": null,
        "scope": null,
        "evidence": null
      }
    }
  ]
}
```

</details>
