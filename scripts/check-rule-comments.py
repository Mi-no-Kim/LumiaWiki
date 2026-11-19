"""Shared command for current Issue/Task/execution and legacy Issue protection."""

import runpy
from pathlib import Path

if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).with_name('check-issue-rule-comments.py')), run_name='__main__')
