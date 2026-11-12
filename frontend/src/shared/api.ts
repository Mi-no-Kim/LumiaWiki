export type ApiErrorKind =
  | 'http'
  | 'network'
  | 'timeout'
  | 'cancelled'
  | 'invalid-response'
  | 'boundary';
export interface ProblemDetail {
  status: number;
  code?: string;
  requestId?: string;
  fieldErrors?: { field: string; code: string; message: string }[];
}
export class ApiError extends Error {
  constructor(
    public kind: ApiErrorKind,
    public problem?: ProblemDetail,
  ) {
    const messages = {
      http:
        problem?.status === 400
          ? '입력 내용을 확인해 주세요.'
          : problem?.status === 404
            ? '요청한 대상을 찾을 수 없습니다.'
            : '요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요.',
      network: '서버에 연결하지 못했습니다. 연결 상태를 확인해 주세요.',
      timeout: '응답 시간이 초과되었습니다. 다시 시도해 주세요.',
      cancelled: '요청을 취소했습니다.',
      'invalid-response': '서버 응답을 확인할 수 없습니다.',
      boundary: '지원하지 않는 요청 경로입니다.',
    };
    super(messages[kind]);
    this.name = 'ApiError';
  }
}

function problemFrom(status: number, value: unknown): ProblemDetail {
  const problem: ProblemDetail = { status };
  if (!value || typeof value !== 'object') return problem;
  const input = value as Record<string, unknown>;
  if (
    typeof input.code === 'string' &&
    /^[A-Z][A-Z0-9_]{0,79}$/.test(input.code)
  )
    problem.code = input.code;
  if (
    typeof input.requestId === 'string' &&
    /^[a-f0-9-]{36}$/i.test(input.requestId)
  )
    problem.requestId = input.requestId;
  if (Array.isArray(input.fieldErrors))
    problem.fieldErrors = input.fieldErrors
      .filter(
        (field): field is NonNullable<ProblemDetail['fieldErrors']>[number] =>
          Boolean(field) &&
          typeof field.field === 'string' &&
          typeof field.code === 'string' &&
          typeof field.message === 'string',
      )
      .map(({ field, code, message }) => ({ field, code, message }));
  return problem;
}

export async function apiGet<T>(
  path: string,
  {
    signal,
    timeoutMs = 10_000,
  }: { signal?: AbortSignal; timeoutMs?: number } = {},
): Promise<T> {
  // eslint-disable-next-line no-control-regex -- Reject control characters at the API boundary.
  if (!path.startsWith('/api/v1') || /[\\#\u0000-\u001f]/.test(path))
    throw new ApiError('boundary');
  const url = new URL(path, 'http://api.invalid');
  if (
    url.origin !== 'http://api.invalid' ||
    !(url.pathname === '/api/v1' || url.pathname.startsWith('/api/v1/'))
  )
    throw new ApiError('boundary');
  if (signal?.aborted) throw new ApiError('cancelled');
  const controller = new AbortController();
  const cancel = () => controller.abort();
  signal?.addEventListener('abort', cancel, { once: true });
  let timedOut = false;
  const timer = setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, timeoutMs);
  try {
    const response = await fetch(`${url.pathname}${url.search}`, {
      signal: controller.signal,
      headers: { Accept: 'application/json, application/problem+json' },
    });
    let value: unknown;
    if (response.headers.get('content-type')?.includes('json')) {
      try {
        value = await response.json();
      } catch (error) {
        if (controller.signal.aborted) throw error;
        if (response.ok) throw new ApiError('invalid-response');
      }
    } else if (response.ok) throw new ApiError('invalid-response');
    if (!response.ok)
      throw new ApiError('http', problemFrom(response.status, value));
    return value as T;
  } catch (error) {
    if (signal?.aborted) throw new ApiError('cancelled');
    if (timedOut) throw new ApiError('timeout');
    if (error instanceof ApiError) throw error;
    throw new ApiError('network');
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener('abort', cancel);
  }
}
