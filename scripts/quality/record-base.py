"""Prepare only changed parent record blobs for an explicit CI check."""

import os
from pathlib import PurePosixPath
import subprocess
def git(*args, **kwargs):
    return subprocess.check_output(['git', *args], **kwargs)
parents = git('rev-list', '--parents', '-n', '1', 'HEAD').decode().split()
if len(parents) > 1:
    base = parents[1]
    paths = git('diff', '--name-only', '-z', '--diff-filter=AM', '--no-renames', base, 'HEAD', '--',
                'AGENTS.md', 'README.md', 'STRUCTURE.md', 'docs', 'harness', 'work').decode().split('\0')
    paths = [path for path in paths if path and PurePosixPath(path).suffix in ('.md', '.json', '.yaml', '.yml', '.toml')
             and not ('/artifacts/' in path and not path.endswith('.md'))]
    if paths:
        rows = git('ls-tree', '-r', '-z', base, '--', *paths).split(b'\0')
        objects = sorted({row.split(b'\t', 1)[0].split()[2] for row in rows if row})
        if objects:
            checked = git('cat-file', '--batch-check', input=b'\n'.join(objects) + b'\n',
                          env={**os.environ, 'GIT_NO_LAZY_FETCH': '1'})
            missing = [line.split()[0].decode() for line in checked.splitlines() if line.endswith(b' missing')]
            if missing:
                subprocess.run(['git', 'fetch', '--no-tags', '--no-write-fetch-head',
                                '--filter=blob:none', 'origin', *missing], check=True)
