import { expect, test } from 'vitest';

test('controlled CI assertion failure', () => {
  expect(1).toBe(2);
});
