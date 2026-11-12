import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash, randomUUID } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import {
  collectFiles,
  formatKind,
  safeFile,
  normalize,
  pathspecs,
  pathKey,
} from './paths.mjs';
import {
  gradle,
  preparedGradle,
  prepareJava,
  run,
  isMain,
  repository,
} from './process.mjs';

export const fingerprint = (value) =>
  createHash('sha256').update(value).digest('hex');
export const stateDir = async (root) => {
  const dir = await safeFile(root, '.tmp/quality');
  await fs.mkdir(dir, { recursive: true });
  return dir;
};
export async function clearFailures(root, names, all = false) {
  await stateDir(root);
  const dir = await safeFile(root, '.tmp/quality/failures');
  if (all) {
    const unresolved = [];
    for (const entry of await fs.readdir(dir).catch((e) => {
      if (e.code === 'ENOENT') return [];
      throw e;
    })) {
      if (!/^[a-f0-9]{64}\.json$/.test(entry))
        throw Error('Unknown failure state; review it before submission.');
      const file = await safeFile(root, '.tmp/quality/failures/' + entry);
      const record = JSON.parse(await fs.readFile(file, 'utf8'));
      let kind = 'unknown';
      try {
        kind = formatKind(record.file);
      } catch {}
      if (kind === 'unknown' || record.file === 'unknown')
        unresolved.push(record.file);
      else await fs.unlink(file);
    }
    if (unresolved.length)
      throw Error(
        'Unclassified edit remains unverified; classify or recover it before submission.',
      );
  } else
    for (const name of names) {
      const file = await safeFile(
        root,
        '.tmp/quality/failures/' + fingerprint(pathKey(name)) + '.json',
      );
      await fs.unlink(file).catch((e) => {
        if (e.code !== 'ENOENT') throw e;
      });
    }
}

async function prettierOptions(root) {
  const config = JSON.parse(
    await fs.readFile(await safeFile(root, '.prettierrc.json'), 'utf8'),
  );
  if (config.plugins || config.overrides)
    throw Error('Formatter plugins/overrides require explicit review.');
  const manifest = JSON.parse(
    await fs.readFile(await safeFile(root, 'package.json'), 'utf8'),
  );
  const lock = JSON.parse(
    await fs.readFile(await safeFile(root, 'package-lock.json'), 'utf8'),
  );
  const prettier = await import('prettier');
  if (
    manifest.devDependencies?.prettier !== prettier.version ||
    lock.packages?.['node_modules/prettier']?.version !== prettier.version
  )
    throw Error(
      'Candidate formatter version differs; run npm ci for the declared lock.',
    );
  return { prettier, config };
}

export async function formatFiles(
  root,
  names,
  { write = false, offline = false, quiet = false, runGradle } = {},
) {
  const selected = [...new Set(names.map(normalize))];
  const groups = { prettier: [], java: [] };
  for (const name of selected) {
    const kind = formatKind(name);
    if (kind === 'unknown')
      throw Error('Unclassified format path: ' + name + '; review its scope.');
    if (kind === 'skip') continue;
    const file = await safeFile(root, name);
    const stat = await fs.stat(file).catch((e) => {
      if (e.code === 'ENOENT') return null;
      throw e;
    });
    if (stat?.isFile()) groups[kind].push(name);
  }
  if (groups.prettier.length) {
    const { prettier, config } = await prettierOptions(root);
    const bad = [];
    for (const name of groups.prettier) {
      const file = await safeFile(root, name),
        original = await fs.readFile(file, 'utf8');
      const formatted = await prettier.format(original, {
        ...config,
        filepath: file,
      });
      if (formatted !== original) {
        if (write) await fs.writeFile(file, formatted);
        else bad.push(name);
      }
    }
    if (bad.length)
      throw Error(
        'Format differs: ' +
          bad.slice(0, 3).join(', ') +
          '; run npm run format.',
      );
  }
  if (groups.java.length) {
    const targets = groups.java.map((name) => {
      if (name.includes(','))
        throw Error('Comma in Java path requires review.');
      return path.resolve(root, name);
    });
    await (runGradle || (offline ? preparedGradle : gradle))(
      root,
      [
        write ? 'spotlessApply' : 'spotlessCheck',
        ...(offline ? ['--offline'] : []),
        ...(write ? ['-PspotlessIdeHook=' + targets.join(',')] : []),
      ],
      { quiet, timeout: offline ? 60_000 : 600_000 },
    );
  }
  if (write) await clearFailures(root, selected);
  return { checked: groups.prettier.length + groups.java.length };
}

export async function checkIndex(root) {
  const state = await stateDir(root),
    failures = await safeFile(root, '.tmp/quality/failures');
  if (
    (
      await fs.readdir(failures).catch((e) => {
        if (e.code === 'ENOENT') return [];
        throw e;
      })
    ).length
  )
    throw Error(
      'Automatic format is unverified; recover edits and classify failed paths before submission.',
    );
  const git = (...args) =>
    execFileSync('git', ['-C', root, ...args], {
      timeout: 10_000,
      windowsHide: true,
      maxBuffer: 30_000_000,
    });
  // Collect index metadata only; preservation roots and evidence are excluded before collection.
  const rows = git(
    'ls-files',
    '--stage',
    '-z',
    '--',
    ...pathspecs,
    ':(glob,icase,exclude)**/artifacts/**',
    ':(glob,exclude)**/.env*',
  )
    .toString('utf8')
    .split('\0')
    .filter(Boolean);
  const entries = new Map(
    rows.map((row) => {
      const tab = row.indexOf('\t'),
        [mode, oid, stage] = row.slice(0, tab).split(' ');
      return [
        row.slice(tab + 1),
        { name: row.slice(tab + 1), mode, oid, stage },
      ];
    }),
  );
  const support = [
    'package.json',
    'package-lock.json',
    '.prettierrc.json',
    'backend/build.gradle',
    'backend/settings.gradle',
    'backend/gradlew',
    'backend/gradlew.bat',
    'backend/gradle/wrapper/gradle-wrapper.jar',
    'backend/gradle/wrapper/gradle-wrapper.properties',
    ...[...entries.keys()].filter((x) =>
      /^scripts\/quality\/[^/]+\.mjs$/.test(x),
    ),
  ];
  for (const required of [
    'scripts/quality/format.mjs',
    'scripts/quality/paths.mjs',
    'scripts/quality/process.mjs',
  ]) {
    if (!entries.has(required))
      throw Error(
        'Staged formatter source is incomplete; restore the candidate configuration.',
      );
  }
  const destination = path.join(state, 'index-' + randomUUID());
  await safeFile(root, path.relative(root, destination).replaceAll('\\', '/'));
  await fs.mkdir(destination);
  const copied = new Set(),
    identities = new Map();
  async function copy(names) {
    const items = [...new Set(names)]
      .filter((name) => !copied.has(name))
      .map((name) => {
        normalize(name);
        const item = entries.get(name);
        if (!item || item.mode === '120000' || item.stage !== '0')
          throw Error(
            'Missing, symlink or unmerged index source requires review.',
          );
        const key = pathKey(name);
        if (identities.has(key) && identities.get(key) !== name)
          throw Error('Index paths alias the same local file.');
        identities.set(key, name);
        return item;
      });
    if (!items.length) return;
    const payload = execFileSync('git', ['-C', root, 'cat-file', '--batch'], {
      input: items.map((x) => x.oid).join('\n') + '\n',
      windowsHide: true,
      maxBuffer: 30_000_000,
      timeout: 10_000,
    });
    let offset = 0;
    for (const item of items) {
      const newline = payload.indexOf(10, offset),
        header = payload.subarray(offset, newline).toString().split(' ');
      if (header[1] !== 'blob' || !/^\d+$/.test(header[2]))
        throw Error('Cannot read index blob.');
      const size = Number(header[2]),
        target = await safeFile(destination, item.name);
      offset = newline + 1;
      await fs.mkdir(path.dirname(target), { recursive: true });
      await fs.writeFile(target, payload.subarray(offset, offset + size));
      offset += size + 1;
      copied.add(item.name);
    }
  }
  try {
    await copy(support.filter((x) => entries.has(x)));
    const added = git(
      'diff',
      '--cached',
      '--name-only',
      '--diff-filter=A',
      '--no-renames',
      '-z',
      '--',
      ...pathspecs,
    )
      .toString('utf8')
      .split('\0')
      .filter(Boolean);
    const policy = String.raw`import fs from 'node:fs'; import {pathToFileURL} from 'node:url';
const p=await import(pathToFileURL(process.argv[1]).href);
const {names,added}=JSON.parse(fs.readFileSync(0,'utf8'));
process.stdout.write(JSON.stringify({selected:names.filter(x=>['prettier','java'].includes(p.formatKind(x))),unknown:names.filter(x=>added.includes(x)&&p.formatKind(x)==='unknown')}));`;
    const decision = JSON.parse(
      execFileSync(
        process.execPath,
        [
          '--input-type=module',
          '-e',
          policy,
          path.join(destination, 'scripts/quality/paths.mjs'),
        ],
        {
          input: JSON.stringify({ names: [...entries.keys()], added }),
          encoding: 'utf8',
          cwd: destination,
          timeout: 10_000,
          windowsHide: true,
        },
      ),
    );
    if (decision.unknown.length)
      throw Error(
        'Unclassified new index path: ' +
          decision.unknown.slice(0, 3).join(', ') +
          '; classify it before submission.',
      );
    const selected = decision.selected;
    await copy(selected);
    try {
      await run(
        process.execPath,
        [
          path.join(destination, 'scripts/quality/format.mjs'),
          '--check',
          '--offline',
          '--quiet',
          '--snapshot',
        ],
        { cwd: destination, timeout: 80_000, quiet: true },
      );
    } catch (e) {
      throw Error(
        'Index format: ' + (e.output?.trim().split('\n')[0] || e.message),
      );
    }
    return { checked: selected.length };
  } finally {
    if (!destination.startsWith(path.resolve(root, '.tmp/quality') + path.sep))
      throw Error('Unsafe temporary cleanup target.');
    await fs.rm(destination, { recursive: true, force: true });
  }
}

async function main() {
  const args = process.argv.slice(2),
    parent = repository();
  let root = parent;
  if (args.includes('--snapshot')) {
    root = path.resolve(process.cwd());
    if (
      path.dirname(root) !== path.resolve(parent, '.tmp/quality') ||
      !/^index-[a-f0-9-]+$/.test(path.basename(root))
    )
      throw Error('Invalid index snapshot root.');
  }
  if (args.includes('--index')) return checkIndex(root);
  if (args.includes('--prepare')) return prepareJava(root);
  const known = new Set([
    '--write',
    '--check',
    '--docs',
    '--files-json',
    '--offline',
    '--quiet',
    '--snapshot',
  ]);
  for (const arg of args)
    if (!known.has(arg)) throw Error('Unknown format argument.');
  let names;
  if (args.includes('--files-json')) {
    const chunks = [];
    for await (const chunk of process.stdin) chunks.push(chunk);
    names = JSON.parse(Buffer.concat(chunks).toString('utf8'));
  } else names = await collectFiles(root, { docs: args.includes('--docs') });
  const result = await formatFiles(root, names, {
    write: args.includes('--write'),
    offline: args.includes('--offline'),
    quiet: args.includes('--quiet'),
  });
  if (
    args.includes('--write') &&
    !args.includes('--docs') &&
    !args.includes('--files-json')
  )
    await clearFailures(root, [], true);
  return result;
}
if (isMain(import.meta.url))
  main().catch((e) => {
    console.error(String(e.message).split('\n')[0]);
    process.exitCode = 2;
  });
