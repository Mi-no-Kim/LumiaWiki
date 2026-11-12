"""Check one staged Task state; never infer acceptance or change records.

Run from the repository root (or pass --repo):
  python .agents/skills/review-work/scripts/check_task_status.py \
    --task work/records/phase-001/issue-15/task-001.md --expect-state 완료

Exit codes: 0 matches, 1 mismatch, 2 unconfirmed input/source.
"""

import argparse
from pathlib import Path
import re
import subprocess
import sys


STATES = ("예정", "진행 중", "검증 중", "대기", "보류", "완료", "취소")
TASK_PATH = re.compile(
    r"work/records/(?:phase-[0-9]+/issue-[0-9]+|issues/issue-[0-9]+|"
    r"harness/issue-[0-9]+)/task-[0-9]+\.md"
)


def staged_state(repo, task):
    # Validate before any repository lookup; traversal and preservation paths
    # cannot be passed to Git, including through Windows path separators.
    if not TASK_PATH.fullmatch(task):
        raise ValueError("현재 기록 체계의 저장소 상대 Task 경로가 필요합니다")
    try:
        root = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--show-toplevel"],
            check=True, capture_output=True,
        ).stdout.decode("utf-8").strip()
        text = subprocess.run(
            ["git", "-C", root, "show", ":" + task],
            check=True, capture_output=True,
        ).stdout.decode("utf-8")
    except (OSError, subprocess.CalledProcessError, UnicodeError) as error:
        raise ValueError("Git 인덱스의 Task를 읽을 수 없습니다; 경로·스테이징·충돌을 확인하세요") from error
    summaries = re.findall(
        r"^## 현재 요약\s*\n(.*?)(?=^#{1,2} |\Z)", text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if len(summaries) != 1:
        raise ValueError("현재 요약 구역이 없거나 중복되어 상태를 확정할 수 없습니다")
    states = re.findall(r"^- 상태:\s*(.*?)\s*$", summaries[0], flags=re.MULTILINE)
    if len(states) != 1 or states[0] not in STATES:
        raise ValueError("현재 요약의 상태가 없거나 중복·미지원 값입니다")
    return states[0]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--task", required=True, help="저장소 상대 Task 경로")
    parser.add_argument("--expect-state", required=True, choices=STATES,
                        help="기존 수용 판단에서 정한 상태; 이 검사는 수용을 판단하지 않음")
    args = parser.parse_args(argv)
    try:
        actual = staged_state(args.repo, args.task)
    except ValueError as error:
        print(f"미확인: {error}", file=sys.stderr)
        return 2
    if actual != args.expect_state:
        print(f"불일치: {args.task} - 인덱스 상태 '{actual}', 기대 '{args.expect_state}'. "
              "수용 판단과 담당 기록을 대조한 뒤 필요한 상태를 반영·스테이징하세요.")
        return 1
    print(f"일치: {args.task} - 인덱스 상태 '{actual}'. "
          "Task 상태만 확인; 검수·GitHub·PR·종료 처리는 별도 확인.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
