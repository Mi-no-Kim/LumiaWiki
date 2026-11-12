import { spawn, execFileSync } from 'node:child_process';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import fs from 'node:fs/promises';
import { createHash, randomUUID } from 'node:crypto';
import { homedir } from 'node:os';
import { safeFile } from './paths.mjs';

export const isMain = (meta) =>
  process.argv[1] && pathToFileURL(path.resolve(process.argv[1])).href === meta;
export const repository = () =>
  execFileSync('git', ['rev-parse', '--show-toplevel'], {
    encoding: 'utf8',
    timeout: 5000,
    windowsHide: true,
  }).trim();

export function run(
  command,
  args,
  {
    cwd,
    timeout = 600_000,
    quiet = false,
    env = process.env,
    windowsVerbatimArguments = false,
    input,
  } = {},
) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd,
      env,
      windowsHide: true,
      windowsVerbatimArguments,
      detached: process.platform !== 'win32',
      stdio: quiet
        ? [input === undefined ? 'ignore' : 'pipe', 'pipe', 'pipe']
        : 'inherit',
    });
    if (input !== undefined) {
      child.stdin.on('error', () => {});
      child.stdin.end(input);
    }
    let output = '',
      timedOut = false;
    if (quiet)
      for (const stream of [child.stdout, child.stderr])
        stream.on('data', (data) => {
          output = (output + data).slice(-8000);
        });
    const timer = setTimeout(() => {
      timedOut = true;
      if (process.platform === 'win32') {
        try {
          execFileSync(
            'taskkill.exe',
            ['/pid', String(child.pid), '/t', '/f'],
            { windowsHide: true, stdio: 'ignore', timeout: 1500 },
          );
        } catch {
          child.kill('SIGKILL');
        }
      } else {
        try {
          process.kill(-child.pid, 'SIGKILL');
        } catch {
          child.kill('SIGKILL');
        }
      }
    }, timeout);
    child.once('error', () => {
      clearTimeout(timer);
      reject(
        Error(
          'Required tool cannot start; install it explicitly and retry the command.',
        ),
      );
    });
    child.once('close', (code) => {
      clearTimeout(timer);
      if (timedOut)
        reject(Error('Quality command timed out; verification required.'));
      else if (code !== 0) {
        const error = Error(
          `Quality command failed (${code}); run the explicit command for details.`,
        );
        error.output = output;
        reject(error);
      } else resolve(output);
    });
  });
}

export function gradle(root, args, options = {}) {
  const cwd = path.join(root, 'backend');
  const common = [...args, '--console=plain'];
  if (process.platform !== 'win32')
    return run('sh', [path.join(cwd, 'gradlew'), ...common], {
      ...options,
      cwd,
    });
  const parts = [path.join(cwd, 'gradlew.bat'), ...common];
  if (parts.some((x) => /[&|<>^%"\r\n]/.test(x)))
    throw Error('Unsafe Gradle argument; review file path.');
  const line = '"' + parts.map((x) => '"' + x + '"').join(' ') + '"';
  return run(process.env.ComSpec || 'cmd.exe', ['/d', '/s', '/c', line], {
    ...options,
    cwd,
    windowsVerbatimArguments: true,
  });
}

export function npm(root, args, options = {}) {
  if (process.platform !== 'win32')
    return run('npm', args, { ...options, cwd: root });
  const cli =
    process.env.npm_execpath ||
    path.join(
      path.dirname(process.execPath),
      'node_modules/npm/bin/npm-cli.js',
    );
  return run(process.execPath, [cli, ...args], { ...options, cwd: root });
}

async function wrapperDigest(root) {
  const hash = createHash('sha256');
  for (const name of [
    'backend/gradle/wrapper/gradle-wrapper.properties',
    'backend/gradle/wrapper/gradle-wrapper.jar',
  ]) {
    const bytes = await fs.readFile(await safeFile(root, name));
    hash.update(
      name.endsWith('.properties')
        ? bytes.toString('utf8').replaceAll('\r\n', '\n')
        : bytes,
    );
  }
  return hash.digest('hex');
}

export async function prepareJava(root) {
  const state = await safeFile(root, '.tmp/quality');
  await fs.mkdir(state, { recursive: true });
  const init = await safeFile(
    root,
    '.tmp/quality/prepare-' + randomUUID() + '.gradle',
  );
  await fs.writeFile(
    init,
    'gradle.settingsEvaluated { println("QUALITY_GRADLE_HOME=" + gradle.gradleHomeDir.absolutePath) }\n',
  );
  try {
    const output = await gradle(root, ['spotlessJava', '--init-script', init], {
      quiet: true,
    });
    const home = /^QUALITY_GRADLE_HOME=(.+)$/m.exec(output)?.[1]?.trim();
    if (!home) throw Error('Cannot identify prepared Gradle distribution.');
    const ready = {
      wrapperDigest: await wrapperDigest(root),
      home: path.resolve(home),
      cache: path.resolve(
        process.env.GRADLE_USER_HOME || path.join(homedir(), '.gradle'),
        'wrapper/dists',
      ),
    };
    if (!ready.home.startsWith(ready.cache + path.sep))
      throw Error('Prepared Gradle is outside the expected Wrapper cache.');
    await fs.writeFile(
      await safeFile(root, '.tmp/quality/java-ready.json'),
      JSON.stringify(ready),
    );
  } finally {
    await fs.unlink(init);
  }
}

export async function preparedGradle(root, args, options = {}) {
  // Calling the Wrapper with --offline can still download its distribution.
  // Execute only the exact distribution identified by explicit preparation.
  let ready;
  try {
    const parent = execFileSync(
      'git',
      ['-C', root, 'rev-parse', '--show-toplevel'],
      { encoding: 'utf8', timeout: 5000, windowsHide: true },
    ).trim();
    ready = JSON.parse(
      await fs.readFile(
        await safeFile(parent, '.tmp/quality/java-ready.json'),
        'utf8',
      ),
    );
    const cache = path.resolve(
      process.env.GRADLE_USER_HOME || path.join(homedir(), '.gradle'),
      'wrapper/dists',
    );
    if (
      ready.wrapperDigest !== (await wrapperDigest(root)) ||
      ready.cache !== cache ||
      !path.resolve(ready.home).startsWith(cache + path.sep) ||
      (await fs.realpath(ready.home)) !== path.resolve(ready.home)
    )
      throw Error('Prepared distribution differs.');
  } catch {
    throw Error(
      'Java formatter is not prepared for this Wrapper; run npm run format:prepare explicitly.',
    );
  }
  const executable = path.join(
    ready.home,
    'bin',
    process.platform === 'win32' ? 'gradle.bat' : 'gradle',
  );
  if (!(await fs.lstat(executable)).isFile())
    throw Error(
      'Prepared Gradle is missing; run npm run format:prepare explicitly.',
    );
  const common = [...args, '--offline', '--console=plain'];
  if (process.platform !== 'win32')
    return run(executable, common, {
      ...options,
      cwd: path.join(root, 'backend'),
    });
  const parts = [executable, ...common];
  if (parts.some((x) => /[&|<>^%"\r\n]/.test(x)))
    throw Error('Unsafe prepared Gradle argument.');
  return run(
    process.env.ComSpec || 'cmd.exe',
    ['/d', '/s', '/c', '"' + parts.map((x) => '"' + x + '"').join(' ') + '"'],
    {
      ...options,
      cwd: path.join(root, 'backend'),
      windowsVerbatimArguments: true,
    },
  );
}
