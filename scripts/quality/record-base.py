"""Prepare changed parent record blobs without broadening the sparse checkout."""

import os
from pathlib import PurePosixPath
import subprocess
from urllib.request import Request, urlopen
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
        entries = [row.split(b'\t', 1)[0].split() for row in rows if row]
        objects = sorted({entry[2] for entry in entries if entry[1] == b'blob'})
        if objects:
            checked = git('cat-file', '--batch-check', input=b'\n'.join(objects) + b'\n',
                          env={**os.environ, 'GIT_NO_LAZY_FETCH': '1'})
            missing = [line.split()[0].decode() for line in checked.splitlines() if line.endswith(b' missing')]
            for oid in missing:
                url = f"{os.environ['GITHUB_API_URL']}/repos/{os.environ['GITHUB_REPOSITORY']}/git/blobs/{oid}"
                request = Request(url, headers={'Accept': 'application/vnd.github.raw+json'})
                request.add_unredirected_header('Authorization', f"Bearer {os.environ['PARENT_BLOB_TOKEN']}")
                with urlopen(request, timeout=30) as response:
                    blob = response.read(20_000_001)
                if len(blob) > 20_000_000 or git('hash-object', '--stdin', input=blob).decode().strip() != oid:
                    raise ValueError(f'Invalid parent document blob: {oid}')
                git('hash-object', '-w', '--stdin', input=blob)
