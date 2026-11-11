import test from 'node:test';
import assert from 'node:assert/strict';
import { serverEnvironment } from './dev-api.mjs';

const valid = {
  DB_HOST: '127.0.0.1', DB_PORT: '5432', DB_NAME: 'lumiawiki',
  DB_USERNAME: 'lumiawiki', DB_PASSWORD: 'local-test-secret',
};

test('missing or example password is rejected without disclosing values', () => {
  for (const password of [undefined, '', 'CHANGE_ME', '<개인 값>']) {
    assert.throws(() => serverEnvironment({ ...valid, DB_PASSWORD: password }), /DB_PASSWORD/);
  }
});
test('invalid DB and server ports are rejected before starting Java', () => {
  for (const port of ['0', '65536', '5432junk', '1.5']) {
    assert.throws(() => serverEnvironment({ ...valid, DB_PORT: port }), /DB_PORT/);
    assert.throws(() => serverEnvironment({ ...valid, SERVER_PORT: port }), /SERVER_PORT/);
  }
});
test('DB host cannot inject JDBC connection options; errors do not leak secrets', () => {
  assert.throws(() => serverEnvironment({ ...valid, DB_HOST: 'host/?password=local-test-secret' }), (error) => {
    assert.match(error.message, /DB_HOST/);
    assert.ok(!error.message.includes('local-test-secret'));
    return true;
  });
});
test('valid connection is preserved in environment and local profile is explicit', () => {
  const env = serverEnvironment({ ...valid, SPRING_PROFILES_ACTIVE: 'production', SERVER_PORT: '8081' });
  assert.equal(env.DB_PASSWORD, valid.DB_PASSWORD);
  assert.equal(env.SPRING_PROFILES_ACTIVE, 'local');
  assert.equal(env.SERVER_PORT, '8081');
  assert.equal(env.DB_PORT, '5432');
});
