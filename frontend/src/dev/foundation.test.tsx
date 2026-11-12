import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, test, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createMemoryRouter, RouterProvider } from 'react-router-dom';
import FoundationPage from './FoundationPage';

const clients: QueryClient[] = [];
afterEach(() => { clients.forEach(client => client.clear()); clients.length = 0; vi.unstubAllGlobals(); });
function mount() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: Infinity } } });
  clients.push(client);
  const router = createMemoryRouter([
    { path: '/__dev/foundation', element: <FoundationPage /> },
    { path: '/__dev/foundation/navigation', element: <p>이동 화면에 도착했습니다.</p> },
  ], { initialEntries: ['/__dev/foundation'] });
  render(<QueryClientProvider client={client}><RouterProvider router={router} /></QueryClientProvider>);
  return router;
}
const json = (items: { id: string; label: string }[]) => new Response(JSON.stringify({ items }), { headers: { 'content-type': 'application/json' } });

test('runs queries only on submit and shows loading then response', async () => {
  let resolve!: (response: Response) => void;
  const fetcher = vi.fn(() => new Promise<Response>(done => { resolve = done; }));
  vi.stubGlobal('fetch', fetcher); mount(); const user = userEvent.setup();
  expect(screen.getByRole('button', { name: '조회하기' })).toBeEnabled();
  expect(fetcher).not.toHaveBeenCalled();
  await user.click(screen.getByRole('button', { name: '조회하기' }));
  expect(await screen.findByText('응답을 기다리고 있습니다')).toBeVisible();
  resolve(json([{ id: 'sample-a', label: '연결 확인' }]));
  expect(await screen.findByText('연결 확인', { selector: 'li' })).toBeVisible();
  expect(fetcher).toHaveBeenCalledTimes(1);
});

test('changing scenario cancels stale work and shows independent empty and error states', async () => {
  let oldSignal!: AbortSignal; let oldResolve!: (response: Response) => void;
  const fetcher = vi.fn((url: string, { signal }: { signal: AbortSignal }) => {
    if (url.endsWith('scenario=ok')) { oldSignal = signal; return new Promise<Response>(done => { oldResolve = done; }); }
    if (url.endsWith('scenario=empty')) return Promise.resolve(json([]));
    return Promise.resolve(new Response(JSON.stringify({ status: 400, detail: 'SQL private', code: 'API_INPUT_INVALID', requestId: '12345678-1234-4234-8234-123456789abc' }), { status: 400, headers: { 'content-type': 'application/problem+json' } }));
  });
  vi.stubGlobal('fetch', fetcher); mount(); const user = userEvent.setup();
  expect(screen.getByRole('button', { name: '조회하기' })).toBeEnabled();
  await user.click(screen.getByRole('button', { name: '조회하기' }));
  await user.selectOptions(screen.getByLabelText('응답 상황'), 'empty');
  expect(oldSignal.aborted).toBe(true);
  expect(fetcher).toHaveBeenCalledTimes(1);
  await user.click(screen.getByRole('button', { name: '조회하기' }));
  expect(await screen.findByText('조회 결과가 없습니다')).toBeVisible();
  await act(async () => oldResolve(json([{ id: 'old', label: '이전 응답' }])));
  expect(screen.queryByText('이전 응답')).not.toBeInTheDocument();
  await user.selectOptions(screen.getByLabelText('응답 상황'), 'bad-input');
  await user.click(screen.getByRole('button', { name: '조회하기' }));
  const error = await screen.findByRole('alert');
  expect(error).toHaveTextContent('입력 내용을 확인해 주세요.');
  expect(error).toHaveTextContent('12345678-1234-4234-8234-123456789abc');
  expect(error).not.toHaveTextContent('SQL private');
});

test('provides two navigable screens and restores back navigation', async () => {
  const router = mount(); const user = userEvent.setup();
  expect(screen.queryByRole('link', { name: /이동 확인/ })).not.toBeNull();
  await user.click(screen.getByRole('link', { name: /이동 확인/ }));
  expect(await screen.findByText('이동 화면에 도착했습니다.')).toBeVisible();
  await act(async () => { await router.navigate(-1); });
  expect(await screen.findByRole('heading', { name: '공통 연결 확인' })).toBeVisible();
});
