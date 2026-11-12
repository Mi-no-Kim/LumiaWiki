import fs from 'node:fs/promises';
import path from 'node:path';
import { npm, gradle, run, repository, isMain } from './process.mjs';
import { collectFiles, safeFile } from './paths.mjs';
import { formatFiles } from './format.mjs';

export async function check(root, scope) {
  const python = process.platform === 'win32' ? 'python' : 'python3';
  const py = (args) =>
    run(python, ['-B', '-X', 'utf8', ...args], { cwd: root });
  if (scope === 'frontend') {
    await formatFiles(
      root,
      (await collectFiles(root)).filter((x) => x.startsWith('frontend/')),
    );
    await npm(root, ['--prefix', 'frontend', 'run', 'lint']);
    await npm(root, [
      '--prefix',
      'frontend',
      'run',
      'test',
      '--',
      '--reporter=default',
      '--reporter=junit',
      '--outputFile=test-results/vitest.xml',
    ]);
    await npm(root, ['--prefix', 'frontend', 'run', 'build']);
  } else if (scope === 'backend') {
    await gradle(root, ['spotlessCheck', 'test', 'integrationTest', 'bootJar']);
  } else if (scope === 'tools') {
    await formatFiles(
      root,
      (await collectFiles(root)).filter(
        (x) => !x.startsWith('frontend/') && !x.startsWith('backend/'),
      ),
    );
    const tests = (await fs.readdir(await safeFile(root, 'scripts')))
      .filter((x) => x.endsWith('.test.mjs'))
      .map((x) => 'scripts/' + x);
    await run(process.execPath, ['--test', ...tests], { cwd: root });
    await py(['-m', 'unittest', 'discover', '-s', 'scripts/tests', '-v']);
    await py([
      '-m',
      'unittest',
      'discover',
      '-s',
      '.agents/skills/review-work/scripts',
      '-p',
      'test_*.py',
      '-v',
    ]);
  } else if (scope === 'docs') {
    await formatFiles(root, await collectFiles(root, { docs: true }));
    const candidate = process.env.CI ? 'HEAD' : 'work';
    await py(['scripts/check-harness-inventory.py', '--candidate', candidate]);
    await py([
      'scripts/check-work-records.py',
      '--candidate',
      process.env.CI ? 'HEAD' : 'index',
    ]);
  } else if (scope === 'all') {
    await formatFiles(root, await collectFiles(root));
    for (const area of ['tools', 'frontend', 'backend', 'docs'])
      await check(root, area);
  } else throw Error('Choose tools, docs, frontend, backend or all.');
}
if (isMain(import.meta.url))
  check(repository(), process.argv[2]).catch((e) => {
    console.error(e.message);
    process.exitCode = 2;
  });
