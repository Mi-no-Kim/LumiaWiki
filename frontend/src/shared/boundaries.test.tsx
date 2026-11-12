import { afterEach, expect, test, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { apiGet } from './api';
import { CommonImage, imageUrl } from './images';

afterEach(() => {
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

test('fetches relative JSON without forwarding request bodies', async () => {
  const fetcher = vi.fn().mockResolvedValue(
    new Response('{"items":[]}', {
      headers: { 'content-type': 'application/json' },
    }),
  );
  vi.stubGlobal('fetch', fetcher);
  const result = await apiGet('/api/v1/_dev/foundation?scenario=empty').catch(
    (error) => error,
  );
  expect(result).toEqual({ items: [] });
  expect(fetcher).toHaveBeenCalledWith(
    '/api/v1/_dev/foundation?scenario=empty',
    expect.objectContaining({ signal: expect.any(AbortSignal) }),
  );
  expect(fetcher.mock.calls[0][1]).not.toHaveProperty('body');
});

test('turns ProblemDetail into a safe HTTP error', async () => {
  const requestId = '12345678-1234-4234-8234-123456789abc';
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          status: 400,
          detail: 'unsafe SQL password=example',
          code: 'API_INPUT_INVALID',
          requestId,
          fieldErrors: [
            { field: 'scenario', code: 'Invalid', message: '확인 필요' },
          ],
        }),
        {
          status: 400,
          headers: { 'content-type': 'application/problem+json' },
        },
      ),
    ),
  );
  const error = await apiGet('/api/v1/_dev/foundation').catch((error) => error);
  expect(error).toMatchObject({
    kind: 'http',
    problem: {
      status: 400,
      requestId,
      code: 'API_INPUT_INVALID',
      fieldErrors: [{ field: 'scenario' }],
    },
  });
  expect(error).toHaveProperty(
    'message',
    expect.not.stringMatching(/SQL|password|example/),
  );
});

test('does not expose non JSON failure bodies', async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue(
      new Response('<html>password=private</html>', {
        status: 502,
        headers: { 'content-type': 'text/html' },
      }),
    ),
  );
  const error = await apiGet('/api/v1/example').catch((error) => error);
  expect(error).toMatchObject({ kind: 'http', problem: { status: 502 } });
  expect(error).toHaveProperty(
    'message',
    expect.not.stringContaining('private'),
  );
});

test('separates cancellation network failure and timeout', async () => {
  const abort = new AbortController();
  abort.abort();
  await expect(
    apiGet('/api/v1/example', { signal: abort.signal }),
  ).rejects.toMatchObject({ kind: 'cancelled' });
  vi.stubGlobal(
    'fetch',
    vi.fn().mockRejectedValue(new TypeError('private endpoint')),
  );
  await expect(apiGet('/api/v1/example')).rejects.toMatchObject({
    kind: 'network',
  });
  vi.useFakeTimers();
  vi.stubGlobal(
    'fetch',
    vi.fn(
      (_url, { signal }) =>
        new Promise((_resolve, reject) =>
          signal.addEventListener(
            'abort',
            () => reject(new DOMException('aborted', 'AbortError')),
            { once: true },
          ),
        ),
    ),
  );
  const pending = apiGet('/api/v1/example').catch((error) => error);
  await vi.advanceTimersByTimeAsync(10_000);
  expect(await pending).toMatchObject({ kind: 'timeout' });
});

test('keeps timeout active while reading response body', async () => {
  vi.useFakeTimers();
  vi.stubGlobal(
    'fetch',
    vi.fn((_url, { signal }) =>
      Promise.resolve({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () =>
          new Promise((_resolve, reject) =>
            signal.addEventListener(
              'abort',
              () => reject(new DOMException('aborted', 'AbortError')),
              { once: true },
            ),
          ),
      }),
    ),
  );
  const pending = apiGet('/api/v1/example').catch((error) => error);
  await vi.advanceTimersByTimeAsync(10_000);
  expect(await pending).toMatchObject({ kind: 'timeout' });
});

test('rejects paths outside the API boundary', async () => {
  const fetcher = vi.fn();
  vi.stubGlobal('fetch', fetcher);
  await expect(apiGet('https://example.invalid/api/v1')).rejects.toMatchObject({
    kind: 'boundary',
  });
  await expect(apiGet('/api/v1/../../private')).rejects.toMatchObject({
    kind: 'boundary',
  });
  expect(fetcher).not.toHaveBeenCalled();
});

test('resolves images under the app base and rejects unsafe paths', () => {
  expect(imageUrl('sample-a.svg', '/wiki/')).toBe('/wiki/images/sample-a.svg');
  for (const path of [
    null,
    '',
    '../private.svg',
    '%2e%2e/private.svg',
    'https://example.invalid/a.svg',
    '/absolute.svg',
    'a\\b.svg',
  ])
    expect(imageUrl(path)).toBeNull();
});

test('falls back once and recovers when the image path changes', () => {
  const view = render(
    <CommonImage path="foundation-sample-a.svg" alt="예제" />,
  );
  const image = screen.getByRole('img', { name: '예제' });
  expect(image).toHaveAttribute('src', '/images/foundation-sample-a.svg');
  fireEvent.error(image);
  expect(image).toHaveAttribute('src', '/images/placeholder.svg');
  fireEvent.error(image);
  expect(image).toHaveAttribute('src', '/images/placeholder.svg');
  view.rerender(<CommonImage path="foundation-sample-b.svg" alt="예제" />);
  expect(screen.getByRole('img', { name: '예제' })).toHaveAttribute(
    'src',
    '/images/foundation-sample-b.svg',
  );
});
