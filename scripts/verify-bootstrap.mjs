import { spawn } from 'node:child_process';
import { createHash, randomBytes } from 'node:crypto';
import { createServer } from 'node:net';
import {
  readdir,
  mkdir,
  copyFile,
  readFile,
  writeFile,
  stat,
  access,
} from 'node:fs/promises';
import { resolve, join, relative, dirname, sep } from 'node:path';
import { root, gradleCommand, serverEnvironment } from './dev-api.mjs';

const id = `lw-bootstrap-${randomBytes(6).toString('hex')}`;
const area = resolve(root, '.tmp/issue-42/task-001', id);
const project = join(area, 'project');
const composeFile = join(area, 'compose.json');
const password = randomBytes(24).toString('hex');
const sql =
  "CREATE TABLE bootstrap_probe (id integer PRIMARY KEY, value text NOT NULL);\nINSERT INTO bootstrap_probe VALUES (1, 'preserved');\n";
const digest = (data) => createHash('sha256').update(data).digest('hex');
const safe = (text) => text.replaceAll(password, '[redacted]');
let sequence = 0;
let app;
let databaseCreated = false;

function start(command, args, options = {}) {
  const child = spawn(command, args, {
    windowsHide: true,
    ...options,
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  let output = '';
  child.stdout.on('data', (data) => {
    output += data;
  });
  child.stderr.on('data', (data) => {
    output += data;
  });
  const done = new Promise((resolveDone) => {
    child.once('error', (error) =>
      resolveDone({ code: 1, output: output + error.message }),
    );
    child.once('close', (code) => resolveDone({ code: code ?? 1, output }));
  });
  return { child, done, output: () => output };
}

async function stop(processHandle) {
  if (
    !processHandle ||
    processHandle.child.exitCode !== null ||
    !processHandle.child.pid
  )
    return;
  if (process.platform === 'win32') {
    const killer = start('taskkill.exe', [
      '/pid',
      String(processHandle.child.pid),
      '/t',
      '/f',
    ]);
    await killer.done;
  } else processHandle.child.kill('SIGTERM');
  await Promise.race([
    processHandle.done,
    new Promise((r) => setTimeout(r, 5000)),
  ]);
}

async function run(command, args, options = {}) {
  const { timeout = 600000, ...spawnOptions } = options;
  const handle = start(command, args, spawnOptions);
  let timer;
  const result = await Promise.race([
    handle.done,
    new Promise((r) => {
      timer = setTimeout(
        () => r({ code: 1, output: 'Command timed out.' }),
        timeout,
      );
    }),
  ]);
  clearTimeout(timer);
  if (result.code !== 0) {
    await stop(handle);
    const log = join(area, `failure-${++sequence}.log`);
    await writeFile(log, safe(result.output));
    throw new Error(`Command failed (${command}); see ${relative(root, log)}.`);
  }
  return result.output;
}

function composeArgs(args) {
  return ['compose', '-p', id, '-f', composeFile, ...args];
}
const docker = (args) => run('docker', composeArgs(args), { timeout: 120000 });

async function copyTree(source, destination, inputs) {
  await mkdir(destination, { recursive: true });
  for (const entry of await readdir(source, { withFileTypes: true })) {
    if (entry.isSymbolicLink())
      throw new Error('Symlinks are not allowed in verification inputs.');
    const from = join(source, entry.name);
    const to = join(destination, entry.name);
    if (entry.isDirectory()) await copyTree(from, to, inputs);
    else {
      const bytes = await readFile(from);
      await copyFile(from, to);
      if (digest(bytes) !== digest(await readFile(to)))
        throw new Error('Input copy mismatch.');
      inputs[relative(root, from).split(sep).join('/')] = digest(bytes);
    }
  }
}

async function freePort() {
  const server = createServer();
  await new Promise((yes, no) => {
    server.once('error', no);
    server.listen(0, '127.0.0.1', yes);
  });
  const port = server.address().port;
  await new Promise((yes) => server.close(yes));
  return String(port);
}

async function ready(handle) {
  const deadline = Date.now() + 90000;
  while (Date.now() < deadline) {
    if (/Started \S+ in /.test(handle.output())) return;
    if (handle.child.exitCode !== null) break;
    await new Promise((r) => setTimeout(r, 300));
  }
  await writeFile(join(area, 'app-start-failure.log'), safe(handle.output()));
  throw new Error(
    'API did not start within 90 seconds; inspect the saved startup log.',
  );
}

async function query(sqlText) {
  return (
    await docker([
      'exec',
      '-T',
      'db',
      'psql',
      '-U',
      'bootstrap',
      '-d',
      'bootstrap',
      '-At',
      '-c',
      sqlText,
    ])
  ).trim();
}

async function main() {
  // No Docker resources are created until the supplied backend is complete.
  for (const name of [
    'build.gradle',
    'settings.gradle',
    'gradlew',
    'gradlew.bat',
    'gradle/wrapper/gradle-wrapper.jar',
    'gradle/wrapper/gradle-wrapper.properties',
    'src/main/resources/application-local.yaml',
  ]) {
    try {
      await access(join(root, 'backend', name));
    } catch {
      throw new Error(
        `Backend input missing: backend/${name}. Add the supplied server files and settings first.`,
      );
    }
  }
  await mkdir(project, { recursive: true });
  await run('docker', ['info', '--format', '{{.OSType}}'], { timeout: 15000 });
  const inputs = {};
  for (const name of [
    'build.gradle',
    'settings.gradle',
    'gradlew',
    'gradlew.bat',
  ]) {
    const from = join(root, 'backend', name);
    const to = join(project, 'backend', name);
    await mkdir(dirname(to), { recursive: true });
    await copyFile(from, to);
    inputs[`backend/${name}`] = digest(await readFile(from));
    if (inputs[`backend/${name}`] !== digest(await readFile(to)))
      throw new Error('Input copy mismatch.');
  }
  try {
    const from = join(root, 'backend/gradle.properties');
    await access(from);
    await copyFile(from, join(project, 'backend/gradle.properties'));
    inputs['backend/gradle.properties'] = digest(await readFile(from));
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
  }
  await copyTree(
    join(root, 'backend/gradle/wrapper'),
    join(project, 'backend/gradle/wrapper'),
    inputs,
  );
  await copyTree(
    join(root, 'backend/src/main'),
    join(project, 'backend/src/main'),
    inputs,
  );
  const migration = join(project, 'db/migration/V1__bootstrap_probe.sql');
  await mkdir(dirname(migration), { recursive: true });
  await writeFile(migration, sql);
  await writeFile(
    join(area, 'input-hashes.json'),
    JSON.stringify(inputs, null, 2),
  );
  const build = gradleCommand(project, [
    'bootJar',
    '--console=plain',
    '--no-daemon',
  ]);
  await run(build.command, build.args, { ...build, env: process.env });
  const jar = join(
    project,
    'backend/build/libs/lumiawiki-api-0.0.1-SNAPSHOT.jar',
  );
  await stat(jar);
  const jarTool = process.env.JAVA_HOME
    ? join(
        process.env.JAVA_HOME,
        'bin',
        process.platform === 'win32' ? 'jar.exe' : 'jar',
      )
    : 'jar';
  const unpack = join(area, 'jar-entry');
  await mkdir(unpack, { recursive: true });
  const entry = 'BOOT-INF/classes/db/migration/V1__bootstrap_probe.sql';
  await run(jarTool, ['-xf', jar, entry], { cwd: unpack });
  if ((await readFile(join(unpack, entry), 'utf8')) !== sql)
    throw new Error('Packaged SQL does not match its input.');
  console.log('PASS: source hashes and packaged shared SQL');

  const config = {
    services: {
      db: {
        image: 'postgres:18.6',
        environment: {
          POSTGRES_DB: 'bootstrap',
          POSTGRES_USER: 'bootstrap',
          POSTGRES_PASSWORD: password,
        },
        ports: ['127.0.0.1::5432'],
        volumes: ['probe_data:/var/lib/postgresql'],
        healthcheck: {
          test: ['CMD-SHELL', 'pg_isready -U bootstrap -d bootstrap'],
          interval: '5s',
          timeout: '5s',
          retries: 12,
          start_period: '10s',
        },
      },
    },
    volumes: { probe_data: {} },
  };
  await writeFile(composeFile, JSON.stringify(config), { mode: 0o600 });
  databaseCreated = true;
  await docker(['up', '-d', '--wait', '--wait-timeout', '90', 'db']);
  const portText = (await docker(['port', 'db', '5432'])).trim();
  const dbPort = portText.match(/:(\d+)$/)?.[1];
  if (!dbPort) throw new Error('Cannot identify isolated database port.');
  const env = serverEnvironment({
    ...process.env,
    DB_HOST: '127.0.0.1',
    DB_PORT: dbPort,
    DB_NAME: 'bootstrap',
    DB_USERNAME: 'bootstrap',
    DB_PASSWORD: password,
    SERVER_PORT: await freePort(),
  });
  const java = process.env.JAVA_HOME
    ? join(
        process.env.JAVA_HOME,
        'bin',
        process.platform === 'win32' ? 'java.exe' : 'java',
      )
    : 'java';
  const snapshot = async () => ({
    row: await query('SELECT id, value FROM bootstrap_probe;'),
    history: await query(
      'SELECT version, success, checksum FROM flyway_schema_history ORDER BY installed_rank;',
    ),
  });
  app = start(java, ['-jar', jar], { cwd: project, env });
  await ready(app);
  const first = await snapshot();
  if (first.row !== '1|preserved' || !/^1\|t\|-?\d+$/.test(first.history))
    throw new Error('Unexpected migration result.');
  await stop(app);
  app = undefined;
  app = start(java, ['-jar', jar], { cwd: project, env });
  await ready(app);
  if (JSON.stringify(await snapshot()) !== JSON.stringify(first))
    throw new Error('Application restart changed migration data/history.');
  await stop(app);
  app = undefined;
  console.log('PASS: migration, JDBC connection, application restart');
  await docker(['down']);
  await docker(['up', '-d', '--wait', '--wait-timeout', '90', 'db']);
  if (JSON.stringify(await snapshot()) !== JSON.stringify(first))
    throw new Error('Database restart lost data/history.');
  console.log('PASS: named volume preserved after compose down/up');

  // Docker may allocate a different host port when the container is recreated.
  env.DB_PORT = (await docker(['port', 'db', '5432']))
    .trim()
    .match(/:(\d+)$/)?.[1];
  if (!env.DB_PORT)
    throw new Error('Cannot identify the restarted database port.');
  env.SERVER_PORT = await freePort();

  const wrong = start(java, ['-jar', jar], {
    cwd: project,
    env: { ...env, DB_PASSWORD: 'intentionally-wrong-bootstrap-password' },
  });
  let wrongTimer;
  const failed = await Promise.race([
    wrong.done,
    new Promise((r) => {
      wrongTimer = setTimeout(() => r(null), 90000);
    }),
  ]);
  clearTimeout(wrongTimer);
  await stop(wrong);
  if (
    !failed ||
    failed.code === 0 ||
    !/authentication failed|password authentication|28P01/i.test(
      failed.output,
    ) ||
    failed.output.includes(password) ||
    failed.output.includes('intentionally-wrong-bootstrap-password')
  ) {
    await writeFile(
      join(area, 'wrong-password-failure.log'),
      safe(failed?.output ?? 'Startup timed out.').replaceAll(
        'intentionally-wrong-bootstrap-password',
        '[redacted-wrong]',
      ),
    );
    throw new Error('Wrong-password failure was not safely verified.');
  }
  console.log('PASS: incorrect password fails without exposing credentials');

  const localEnvFile = join(area, 'connection.env');
  env.SERVER_PORT = await freePort();
  await writeFile(
    localEnvFile,
    [
      'DB_HOST',
      'DB_PORT',
      'DB_NAME',
      'DB_USERNAME',
      'DB_PASSWORD',
      'SERVER_PORT',
    ]
      .map((key) => `${key}=${env[key]}`)
      .join('\n'),
    { mode: 0o600 },
  );
  const runnerEnv = { ...process.env };
  for (const key of [
    'DB_HOST',
    'DB_PORT',
    'DB_NAME',
    'DB_USERNAME',
    'DB_PASSWORD',
    'SERVER_PORT',
    'SPRING_PROFILES_ACTIVE',
  ])
    delete runnerEnv[key];
  app = start(
    process.execPath,
    [`--env-file=${localEnvFile}`, join(root, 'scripts/dev-api.mjs')],
    { cwd: root, env: runnerEnv },
  );
  await ready(app);
  if (JSON.stringify(await snapshot()) !== JSON.stringify(first))
    throw new Error('Local launcher changed data/history.');
  await stop(app);
  app = undefined;
  await writeFile(
    localEnvFile,
    '# Temporary connection removed after successful verification.\n',
  );
  console.log('PASS: native env-file and real local bootRun launcher');
  for (const [name, hash] of Object.entries(inputs)) {
    if (digest(await readFile(join(root, name))) !== hash)
      throw new Error(
        'Original source changed during verification; rerun against the new input.',
      );
  }
  const production = gradleCommand(root, ['bootJar', '--console=plain']);
  await run(production.command, production.args, {
    ...production,
    env: process.env,
  });
  const actualJar = join(
    root,
    'backend/build/libs/lumiawiki-api-0.0.1-SNAPSHOT.jar',
  );
  const entries = await run(jarTool, ['-tf', actualJar]);
  if (entries.includes('V1__bootstrap_probe.sql'))
    throw new Error('Synthetic SQL leaked into the product JAR.');
  const originalSql = await readdir(join(root, 'db/migration'));
  if (originalSql.includes('V1__bootstrap_probe.sql'))
    throw new Error('Synthetic SQL leaked into shared sources.');

  // Verify ownership before removing this run's exclusively created volume.
  const volume = `${id}_probe_data`;
  const label = (
    await run('docker', [
      'volume',
      'inspect',
      volume,
      '--format',
      '{{ index .Labels "com.docker.compose.project" }}',
    ])
  ).trim();
  if (label !== id)
    throw new Error(
      'Cannot verify temporary volume ownership; cleanup stopped.',
    );
  await docker(['down', '--volumes']);
  databaseCreated = false;
  await writeFile(
    join(area, 'result.json'),
    JSON.stringify(
      {
        id,
        inputs,
        migration: first,
        syntheticSqlAbsentFromProduct: true,
        temporaryResourcesRemoved: true,
      },
      null,
      2,
    ),
  );
  // The local report contains no credentials. Remove its temporary secret file.
  await writeFile(
    composeFile,
    JSON.stringify({ run: id, temporaryResourcesRemoved: true }),
  );
  console.log(
    `PASS: original sources unchanged; temporary resources removed; report ${relative(root, join(area, 'result.json'))}`,
  );
}

try {
  await main();
} catch (error) {
  console.error(safe(error.message));
  if (databaseCreated)
    console.error(
      `Verification resources retained for ${id}. Use only its recorded compose.json for recovery.`,
    );
  process.exitCode = 1;
} finally {
  await stop(app);
}
