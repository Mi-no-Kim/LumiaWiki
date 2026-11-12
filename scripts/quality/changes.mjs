import fs from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { areas, classifyChanges, pathspecs } from './paths.mjs';
import { repository, isMain } from './process.mjs';

export async function changes(root, env = process.env) {
  const all = () => Object.fromEntries(areas.map((x) => [x, true]));
  if (
    env.QUALITY_EVENT === 'workflow_dispatch' ||
    !/^[a-f0-9]{40}$/.test(env.QUALITY_BASE || '') ||
    /^0+$/.test(env.QUALITY_BASE) ||
    !/^[a-f0-9]{40}$/.test(env.QUALITY_HEAD || '')
  )
    return all();
  try {
    const output = execFileSync(
      'git',
      [
        '-C',
        root,
        'diff',
        '--name-only',
        '--no-renames',
        '-z',
        env.QUALITY_BASE,
        env.QUALITY_HEAD,
        '--',
        ...pathspecs,
      ],
      { timeout: 10_000, windowsHide: true },
    );
    return classifyChanges(output.toString('utf8').split('\0').filter(Boolean));
  } catch {
    return all();
  }
}

export function aggregate(needs) {
  if (needs?.changes?.result !== 'success') return false;
  return areas.every((area) => {
    const flag = needs.changes.outputs?.[area],
      result = needs[area]?.result;
    return (
      (flag === 'true' && result === 'success') ||
      (flag === 'false' && result === 'skipped')
    );
  });
}

if (isMain(import.meta.url))
  (async () => {
    if (process.argv.includes('--aggregate')) {
      if (!aggregate(JSON.parse(process.env.QUALITY_NEEDS || '{}')))
        throw Error(
          'Required quality job failed, cancelled, or was unexpectedly skipped.',
        );
      console.log('Required quality jobs passed.');
    } else {
      const result = await changes(repository());
      const output = areas.map((x) => `${x}=${result[x]}\n`).join('');
      if (process.env.GITHUB_OUTPUT)
        await fs.appendFile(process.env.GITHUB_OUTPUT, output);
      else process.stdout.write(output);
    }
  })().catch((e) => {
    console.error(e.message);
    process.exitCode = 2;
  });
