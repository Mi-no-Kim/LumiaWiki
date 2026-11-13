import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, rm } from 'node:fs/promises';
import { resolve, join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { formatKind, collectFiles, classifyChanges } from './quality/paths.mjs';

test('database Markdown has a format scope without enabling SQL formatting', () => {
  for (const name of [
    'db/README.md',
    'db/bootstrap/README.md',
    'db/model/common-tables.md',
    'db/migration/README.md',
  ])
    assert.equal(formatKind(name), 'prettier', name);
  for (const name of [
    'db/migration/V1.sql',
    'db/bootstrap/10-prepare-roles.sh',
    'db/raw/source.md',
    'db/artifacts/proof.md',
    'db/.env',
    'harness-design/source.md',
    '.harness-state/source.md',
  ])
    assert.equal(formatKind(name), 'skip', name);
});

test('docs collection includes database Markdown and excludes raw evidence', async () => {
  const parent = resolve(dirname(fileURLToPath(import.meta.url)), '../.tmp');
  await mkdir(parent, { recursive: true });
  const fixture = await mkdtemp(join(parent, 'db-docs-'));
  try {
    const inputs = {
      'db/README.md': '# Database\n',
      'db/model/common-tables.md': '# Common tables\n',
      'db/migration/README.md': '# Migration\n',
      'db/migration/V1.sql': '  SELECT 1;  ',
      'db/bootstrap/10-prepare-roles.sh': '  unchanged shell  ',
      'db/raw/source.md': '  unchanged source  ',
      'db/artifacts/proof.md': '  unchanged proof  ',
    };
    for (const [name, value] of Object.entries(inputs)) {
      await mkdir(dirname(join(fixture, name)), { recursive: true });
      await writeFile(join(fixture, name), value);
    }
    const expected = Object.keys(inputs)
      .filter(
        (name) =>
          name.endsWith('.md') &&
          !name.includes('/raw/') &&
          !name.includes('/artifacts/'),
      )
      .sort();
    assert.deepEqual(await collectFiles(fixture, { docs: true }), expected);
    for (const [name, value] of Object.entries(inputs))
      assert.equal(await readFile(join(fixture, name), 'utf8'), value);
  } finally {
    if (dirname(fixture) !== parent)
      throw new Error('Unsafe fixture cleanup target.');
    await rm(fixture, { recursive: true, force: true });
  }
});

test('database documentation changes select only documentation checks', () => {
  const none = { tools: false, docs: false, frontend: false, backend: false };
  assert.deepEqual(classifyChanges(['db/model/common-tables.md']), {
    ...none,
    docs: true,
  });
  assert.deepEqual(
    classifyChanges(['db/model/common-tables.md', 'db/migration/V1.sql']),
    { ...none, docs: true, backend: true },
  );
  assert.deepEqual(classifyChanges(['db/migration/V1.sql']), {
    ...none,
    backend: true,
  });
});
