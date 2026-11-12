import fs from 'node:fs/promises';
import path from 'node:path';
import { fingerprint, stateDir, clearFailures } from './format.mjs';
import { normalize, formatKind, safeFile, pathKey } from './paths.mjs';
import { run, repository, isMain } from './process.mjs';

export function patchPaths(patch) {
  if (typeof patch !== 'string')
    throw Error(
      'Cannot read patch paths; recover edits and run npm run format.',
    );
  patch = patch.replaceAll('\r\n', '\n');
  if (
    !patch.startsWith('*** Begin Patch\n') ||
    !patch.trimEnd().endsWith('*** End Patch')
  )
    throw Error(
      'Cannot read patch paths; recover edits and run npm run format.',
    );
  const names = [
    ...patch.matchAll(
      /^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)$/gm,
    ),
  ].map((x) => x[1]);
  if (!names.length)
    throw Error('Cannot read patch paths; run npm run format.');
  return [...new Set(names)];
}

export async function postEdit(root, event, { formatter } = {}) {
  if (event.tool_name !== 'apply_patch') return;
  await stateDir(root);
  const held = [];
  let names = ['unknown'];
  async function directory(name) {
    const target = await safeFile(root, '.tmp/quality/' + name);
    await fs.mkdir(target, { recursive: true });
    return target;
  }
  async function stateFile(area, name) {
    await directory(area);
    return safeFile(root, '.tmp/quality/' + area + '/' + name);
  }
  try {
    const base = event.cwd ? path.resolve(event.cwd) : path.resolve(root);
    names = patchPaths(event.tool_input?.command).map((input) => {
      if (input.replaceAll('\\', '/').split('/').includes('..'))
        throw Error('Patch path traversal requires review.');
      if (!path.isAbsolute(input)) normalize(input);
      return normalize(
        path.relative(root, path.resolve(base, input)).replaceAll('\\', '/'),
      );
    });
    const selected = new Map();
    for (const name of names) {
      const kind = formatKind(name);
      if (kind === 'unknown')
        throw Error('Unclassified edited file; review formatting scope.');
      if (kind === 'skip') continue;
      const file = await safeFile(root, name);
      if (
        await fs.stat(file).catch((e) => {
          if (e.code === 'ENOENT') return null;
          throw e;
        })
      )
        selected.set(pathKey(name), name);
    }
    names = [...selected.values()].sort();
    if (!names.length) return;
    for (const name of names) {
      const lock = await stateFile('locks', fingerprint(pathKey(name)));
      try {
        const handle = await fs.open(lock, 'wx');
        held.push({ lock, handle });
      } catch (e) {
        if (e.code === 'EEXIST')
          throw Error(
            'Format already running for a changed file; run npm run format after it finishes.',
          );
        throw e;
      }
    }
    const manifest = async () =>
      Object.fromEntries(
        await Promise.all(
          names.map(async (name) => [
            pathKey(name),
            fingerprint(await fs.readFile(await safeFile(root, name))),
          ]),
        ),
      );
    const receipt = await stateFile(
      'events',
      fingerprint(
        String(event.tool_use_id || '') + '\0' + names.map(pathKey).join('\0'),
      ) + '.json',
    );
    const previous = await fs.readFile(receipt, 'utf8').catch((e) => {
      if (e.code === 'ENOENT') return '';
      throw e;
    });
    if (event.tool_use_id && previous === JSON.stringify(await manifest()))
      return;
    const started = performance.now();
    if (formatter)
      await formatter(root, names, { write: true, offline: true, quiet: true });
    else {
      for (const [kind, timeout] of [
        ['prettier', 15_000],
        ['java', 60_000],
      ]) {
        const group = names.filter((x) => formatKind(x) === kind);
        if (!group.length) continue;
        await run(
          process.execPath,
          [
            path.join(root, 'scripts/quality/format.mjs'),
            '--write',
            '--offline',
            '--quiet',
            '--files-json',
          ],
          {
            cwd: root,
            timeout: Math.min(timeout, 80_000 - (performance.now() - started)),
            quiet: true,
            input: JSON.stringify(group),
          },
        );
      }
    }
    if (performance.now() - started > 80_000)
      throw Error(
        'Combined formatting time limit exceeded; run npm run format.',
      );
    await fs.writeFile(
      await stateFile('events', path.basename(receipt)),
      JSON.stringify(await manifest()),
    );
    await clearFailures(root, names);
  } catch (e) {
    for (const name of names.length ? names : ['unknown']) {
      const file = await stateFile(
        'failures',
        fingerprint(pathKey(name)) + '.json',
      );
      await fs.writeFile(
        file,
        JSON.stringify({ file: name, reason: 'format unverified' }),
      );
    }
    throw e;
  } finally {
    for (const { lock, handle } of held.reverse()) {
      await handle.close();
      await fs.unlink(lock);
    }
  }
}

if (isMain(import.meta.url)) {
  (async () => {
    const chunks = [];
    for await (const chunk of process.stdin) chunks.push(chunk);
    let event;
    try {
      event = JSON.parse(Buffer.concat(chunks).toString('utf8'));
    } catch {
      event = { tool_name: 'apply_patch' };
    }
    await postEdit(repository(), event);
  })().catch((e) => {
    console.error(
      'Format unverified: ' +
        String(e.message).split('\n')[0] +
        '\nNext: recover the edited file and classify failed paths before submission.',
    );
    process.exitCode = 2;
  });
}
