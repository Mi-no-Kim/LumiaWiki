import test from 'node:test';
import assert from 'node:assert/strict';
import { serverEnvironment } from './dev-api.mjs';

const valid = {
  DB_HOST: '127.0.0.1',
  DB_PORT: '5432',
  DB_NAME: 'lumiawiki',
  DB_APP_USERNAME: 'lumia_app',
  DB_APP_PASSWORD: 'app-test-secret',
  DB_FLYWAY_USERNAME: 'lumia_migrator',
  DB_FLYWAY_PASSWORD: 'migration-test-secret',
  DB_USERNAME: 'lumiawiki',
  DB_PASSWORD: 'legacy-test-secret',
};

test('missing app or Flyway passwords cannot use legacy credentials', () => {
  for (const key of ['DB_APP_PASSWORD', 'DB_FLYWAY_PASSWORD']) {
    for (const password of [undefined, '', 'CHANGE_ME', '<개인 값>']) {
      assert.throws(
        () => serverEnvironment({ ...valid, [key]: password }),
        (error) => {
          assert.ok(error.message.includes(key));
          assert.ok(!error.message.includes(valid.DB_PASSWORD));
          return true;
        },
      );
    }
  }
});

test('invalid DB and server ports are rejected before starting Java', () => {
  for (const port of ['0', '65536', '5432junk', '1.5']) {
    assert.throws(
      () => serverEnvironment({ ...valid, DB_PORT: port }),
      /DB_PORT/,
    );
    assert.throws(
      () => serverEnvironment({ ...valid, SERVER_PORT: port }),
      /SERVER_PORT/,
    );
  }
});

test('DB host cannot inject JDBC options or disclose credentials', () => {
  assert.throws(
    () =>
      serverEnvironment({
        ...valid,
        DB_HOST: 'host/?password=app-test-secret',
      }),
    (error) => {
      assert.match(error.message, /DB_HOST/);
      assert.ok(!error.message.includes(valid.DB_APP_PASSWORD));
      return true;
    },
  );
});

test('only app and Flyway credentials reach Java while normal environment survives', () => {
  const input = {
    ...valid,
    DB_BOOTSTRAP_USERNAME: 'lumiawiki',
    DB_BOOTSTRAP_PASSWORD: 'bootstrap-test-secret',
    POSTGRES_USER: 'lumiawiki',
    POSTGRES_PASSWORD: 'postgres-test-secret',
    PGUSER: 'lumiawiki',
    PGPASSWORD: 'pg-test-secret',
    PATH: 'existing-path',
    JAVA_HOME: 'existing-java-home',
    HTTPS_PROXY: 'existing-proxy',
    SPRING_PROFILES_ACTIVE: 'production',
    SERVER_PORT: '8081',
  };
  const env = serverEnvironment(input);
  for (const key of [
    'DB_BOOTSTRAP_USERNAME',
    'DB_BOOTSTRAP_PASSWORD',
    'DB_USERNAME',
    'DB_PASSWORD',
    'POSTGRES_USER',
    'POSTGRES_PASSWORD',
    'PGUSER',
    'PGPASSWORD',
  ])
    assert.equal(env[key], undefined, key);
  assert.equal(env.DB_APP_PASSWORD, valid.DB_APP_PASSWORD);
  assert.equal(env.DB_FLYWAY_PASSWORD, valid.DB_FLYWAY_PASSWORD);
  assert.equal(env.PATH, input.PATH);
  assert.equal(env.JAVA_HOME, input.JAVA_HOME);
  assert.equal(env.HTTPS_PROXY, input.HTTPS_PROXY);
  assert.equal(env.SPRING_PROFILES_ACTIVE, 'local');
  assert.equal(env.SERVER_PORT, '8081');
  assert.equal(input.DB_BOOTSTRAP_PASSWORD, 'bootstrap-test-secret');
});

test('local database and role names must match the agreed identities', () => {
  for (const key of ['DB_NAME', 'DB_APP_USERNAME', 'DB_FLYWAY_USERNAME']) {
    assert.throws(
      () => serverEnvironment({ ...valid, [key]: 'another_name' }),
      new RegExp(key),
    );
  }
});

test('password characters and whitespace are preserved without normalization', () => {
  for (const password of ['  ', ' a\'"$\\한글\n끝 ']) {
    const env = serverEnvironment({
      ...valid,
      DB_APP_PASSWORD: password,
      DB_FLYWAY_PASSWORD: password,
    });
    assert.equal(env.DB_APP_PASSWORD, password);
    assert.equal(env.DB_FLYWAY_PASSWORD, password);
  }
});
