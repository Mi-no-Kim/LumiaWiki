import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <main>
      <p className="eyebrow">LUMIA ISLAND WIKI</p>
      <h1>루미아 아일랜드 위키</h1>
      <p>웹 실행 환경이 준비되었습니다.</p>
    </main>
  </StrictMode>,
);
