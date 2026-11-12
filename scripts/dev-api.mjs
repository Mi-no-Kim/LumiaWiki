import { spawn } from 'node:child_process';
import { resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

export const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');

export function serverEnvironment(input) {
  const env = { ...input, SPRING_PROFILES_ACTIVE: 'local' };
  for (const key of [
    'DB_HOST',
    'DB_PORT',
    'DB_NAME',
    'DB_USERNAME',
    'DB_PASSWORD',
  ]) {
    if (!env[key]?.trim() || /^(CHANGE_ME|<.*>)$/i.test(env[key])) {
      throw new Error(`${key} must be set to a personal local value.`);
    }
  }
  if (!/^[a-zA-Z0-9.-]+$/.test(env.DB_HOST))
    throw new Error('DB_HOST is invalid.');
  for (const key of ['DB_NAME', 'DB_USERNAME']) {
    if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(env[key]))
      throw new Error(`${key} is invalid.`);
  }
  env.SERVER_PORT ??= '8080';
  for (const key of ['DB_PORT', 'SERVER_PORT']) {
    if (
      !/^\d+$/.test(env[key]) ||
      Number(env[key]) < 1 ||
      Number(env[key]) > 65535
    ) {
      throw new Error(`${key} must be an integer from 1 to 65535.`);
    }
  }
  return env;
}

export function gradleCommand(projectRoot, args) {
  const backend = resolve(projectRoot, 'backend');
  return process.platform === 'win32'
    ? {
        command: process.env.ComSpec ?? 'cmd.exe',
        args: [
          '/d',
          '/s',
          '/c',
          `""${resolve(backend, 'gradlew.bat')}" ${args.join(' ')}"`,
        ],
        cwd: backend,
        windowsVerbatimArguments: true,
      }
    : {
        command: 'sh',
        args: [resolve(backend, 'gradlew'), ...args],
        cwd: backend,
      };
}

function main() {
  let env;
  try {
    env = serverEnvironment(process.env);
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
    return;
  }
  const invocation = gradleCommand(root, [
    'bootRun',
    '--console=plain',
    '--no-daemon',
  ]);
  const child = spawn(invocation.command, invocation.args, {
    ...invocation,
    env,
    stdio: 'inherit',
    windowsHide: true,
  });
  let interrupted = false;
  const stop = (signal) => {
    interrupted = true;
    if (process.platform === 'win32') {
      // Only this child tree, including Gradle's Java child, is stopped.
      spawn('taskkill.exe', ['/pid', String(child.pid), '/t', '/f'], {
        stdio: 'ignore',
        windowsHide: true,
      });
    } else child.kill(signal);
  };
  process.once('SIGINT', () => stop('SIGINT'));
  process.once('SIGTERM', () => stop('SIGTERM'));
  child.once('error', () => {
    console.error(
      'Cannot start the Gradle Wrapper. Check JDK 21 and backend files.',
    );
    process.exitCode = 1;
  });
  child.once('exit', (code) => {
    process.exitCode = interrupted ? 130 : (code ?? 1);
  });
}

if (
  process.argv[1] &&
  pathToFileURL(resolve(process.argv[1])).href === import.meta.url
)
  main();
