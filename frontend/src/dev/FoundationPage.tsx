import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { apiGet, ApiError } from '../shared/api';
import { CommonImage } from '../shared/images';
import styles from './FoundationPage.module.css';

type FoundationResponse = { items: { id: string; label: string }[] };

async function foundationResponse(
  scenario: string,
  signal: AbortSignal,
): Promise<FoundationResponse> {
  const value = await apiGet<FoundationResponse>(
    `/api/v1/_dev/foundation?scenario=${encodeURIComponent(scenario)}`,
    { signal },
  );
  if (
    !value ||
    !Array.isArray(value.items) ||
    value.items.some(
      (item) =>
        !item || typeof item.id !== 'string' || typeof item.label !== 'string',
    )
  )
    throw new ApiError('invalid-response');
  return value;
}

export default function FoundationPage() {
  const [scenario, setScenario] = useState('ok');
  const [attempt, setAttempt] = useState(0);
  const query = useQuery<FoundationResponse, ApiError>({
    queryKey: ['foundation', scenario, attempt],
    queryFn: ({ signal }) => foundationResponse(scenario, signal),
    enabled: attempt > 0,
  });
  const status = query.isFetching
    ? '조회 중'
    : query.isError
      ? `${query.error.problem?.status ?? '연결'} 오류`
      : query.isSuccess
        ? '200 · 응답 완료'
        : '조회 전';
  return (
    <div className={styles.shell}>
      <main className={styles.main}>
        <div className={styles.intro}>
          <div>
            <p className={styles.eyebrow}>FOUNDATION / 003</p>
            <h1>공통 연결 확인</h1>
            <p className={styles.muted}>
              화면, 응답, 이미지의 기본 흐름을 한곳에서 점검합니다.
            </p>
          </div>
          <span className={styles.preview}>실제 API 조회</span>
        </div>
        <div className={styles.layout}>
          <section className={styles.panel} aria-labelledby="response-heading">
            <div className={styles.sectionHeader}>
              <div>
                <span className={styles.number}>01</span>
                <h2 id="response-heading">API 응답</h2>
              </div>
              <span className={styles.muted}>{status}</span>
            </div>
            <p className={styles.description}>
              확인할 응답을 선택하고 조회 결과와 안내 상태를 확인하세요.
            </p>
            <form
              className={styles.form}
              onSubmit={(event) => {
                event.preventDefault();
                setAttempt((value) => value + 1);
              }}
            >
              <label htmlFor="scenario">
                응답 상황
                <select
                  id="scenario"
                  value={scenario}
                  onChange={(event) => {
                    setScenario(event.target.value);
                    setAttempt(0);
                  }}
                >
                  <option value="ok">정상 응답</option>
                  <option value="slow">지연 응답 · 1초</option>
                  <option value="empty">빈 응답</option>
                  <option value="bad-input">잘못된 입력 · 400</option>
                  <option value="missing">없는 대상 · 404</option>
                  <option value="failure">서버 오류 · 500</option>
                </select>
              </label>
              <button
                className={styles.primary}
                type="submit"
                disabled={query.isFetching}
              >
                조회하기 <span aria-hidden="true">↗</span>
              </button>
            </form>
            <div
              className={styles.result}
              aria-live="polite"
              aria-busy={query.isFetching}
              role={query.isError ? 'alert' : 'status'}
            >
              <span className={styles.signal} aria-hidden="true">
                {query.isError ? '!' : query.isSuccess ? '✓' : '↗'}
              </span>
              {query.isFetching ? (
                <>
                  <h3>응답을 기다리고 있습니다</h3>
                  <p>조회 중에도 다른 응답 상황을 선택할 수 있습니다.</p>
                </>
              ) : query.isError ? (
                <>
                  <h3>{query.error.message}</h3>
                  <p>응답 상황을 확인하고 다시 조회해 주세요.</p>
                  {query.error.problem?.requestId && (
                    <p className={styles.requestId}>
                      요청 ID: {query.error.problem.requestId}
                    </p>
                  )}
                </>
              ) : query.isSuccess ? (
                query.data.items.length ? (
                  <>
                    <h3>응답을 받았습니다</h3>
                    <ul className={styles.items}>
                      {query.data.items.map((item) => (
                        <li key={item.id}>{item.label}</li>
                      ))}
                    </ul>
                  </>
                ) : (
                  <>
                    <h3>조회 결과가 없습니다</h3>
                    <p>요청은 정상 처리되었으며 표시할 항목이 없습니다.</p>
                  </>
                )
              ) : (
                <>
                  <h3>조회할 준비가 되었습니다</h3>
                  <p>응답 상황을 선택하고 조회하기를 눌러 주세요.</p>
                </>
              )}
            </div>
            <div className={styles.stateExamples} aria-label="응답 상태 예시">
              <div>
                <span className={styles.dot} />
                조회 중<p>로딩 안내</p>
              </div>
              <div>
                <span className={`${styles.dot} ${styles.emptyDot}`} />빈 응답
                <p>결과 없음 안내</p>
              </div>
              <div>
                <span className={`${styles.dot} ${styles.errorDot}`} />
                오류 응답<p>안전한 안내와 요청 ID</p>
              </div>
            </div>
            <p className={styles.footnote}>
              상황 선택은 요청을 보내지 않습니다. 조회하기를 누르면 선택한
              상황으로 새로 요청합니다.
            </p>
          </section>
          <aside className={styles.panel} aria-labelledby="navigation-heading">
            <div className={styles.sectionHeader}>
              <div>
                <span className={styles.number}>02</span>
                <h2 id="navigation-heading">화면 이동</h2>
              </div>
            </div>
            <p className={styles.description}>
              두 화면을 오가며 이동과 브라우저 뒤로 가기를 확인합니다.
            </p>
            <nav className={styles.navigation} aria-label="연결 확인 화면">
              <NavLink to="/__dev/foundation" end>
                <strong>연결 확인</strong>
                <small>지금 보고 있는 화면</small>
                <b aria-hidden="true">↗</b>
              </NavLink>
              <NavLink to="/__dev/foundation/navigation">
                <strong>이동 확인</strong>
                <small>이동과 뒤로 가기 점검</small>
                <b aria-hidden="true">→</b>
              </NavLink>
            </nav>
            <div className={styles.note}>
              <span>확인 순서</span>
              <p>
                이동 확인 화면으로 이동한 뒤<br />
                브라우저의 뒤로 가기를 사용하세요.
              </p>
            </div>
          </aside>
        </div>
        <section
          className={`${styles.panel} ${styles.images}`}
          aria-labelledby="image-heading"
        >
          <div className={styles.sectionHeader}>
            <div>
              <span className={styles.number}>03</span>
              <h2 id="image-heading">이미지 제공</h2>
            </div>
            <span className={styles.muted}>합성 예제</span>
          </div>
          <p className={styles.description}>
            기존 이미지와 교체 이미지는 각 경로를 유지하고, 미등록·실패 상태는
            대체 이미지로 안내합니다.
          </p>
          <div className={styles.imageGrid}>
            {[
              ['foundation-sample-a.svg', '기존 이미지', '독립 경로 유지'],
              ['foundation-sample-b.svg', '교체 이미지', '새 경로로 제공'],
              [null, '미등록 이미지', '대체 이미지 표시'],
              ['missing-foundation.svg', '실패 이미지', '대체 이미지 표시'],
            ].map(([file, title, detail]) => (
              <figure key={title}>
                <div className={styles.imageFrame}>
                  <CommonImage path={file} alt={`${title} 합성 예제`} />
                </div>
                <figcaption>
                  <strong>{title}</strong>
                  <span>{detail}</span>
                </figcaption>
              </figure>
            ))}
          </div>
        </section>
        <footer className={styles.footer}>
          <span>실제 게임 자료를 사용하지 않는 개발 확인 화면입니다.</span>
          <span>LUMIA ISLAND WIKI</span>
        </footer>
      </main>
    </div>
  );
}
