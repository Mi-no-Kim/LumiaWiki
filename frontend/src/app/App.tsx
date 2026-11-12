import { Link, Outlet, ScrollRestoration } from 'react-router-dom';
import type { RouteObject } from 'react-router-dom';
import styles from './App.module.css';

function AppLayout() {
  return <>
    <header className={styles.topbar}>
      <Link className={styles.brand} to="/">L<span> / </span>루미아 아일랜드 위키</Link>
      {import.meta.env.DEV && <span className={styles.local}>로컬 개발 전용</span>}
    </header>
    <Outlet /><ScrollRestoration />
  </>;
}

function Home() {
  return <main className="landing"><p className="eyebrow">LUMIA ISLAND WIKI</p><h1>루미아 아일랜드 위키</h1><p>웹 실행 환경이 준비되었습니다.</p></main>;
}

function RouteError() {
  return <main className="landing" role="alert"><h1>화면을 열지 못했습니다</h1><p>잠시 후 다시 시도해 주세요.</p><Link to="/">처음으로</Link></main>;
}

function NotFound() {
  return <main className="landing"><h1>페이지를 찾을 수 없습니다</h1><Link to="/">처음으로</Link></main>;
}

export function appRoutes(extraRoutes: RouteObject[] = []): RouteObject[] {
  return [{ element: <AppLayout />, errorElement: <RouteError />, children: [
    { index: true, element: <Home /> }, ...extraRoutes, { path: '*', element: <NotFound /> },
  ] }];
}
