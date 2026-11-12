import { Link } from 'react-router-dom';
import styles from './FoundationPage.module.css';

export default function NavigationPage() {
  return <main className={styles.main}>
    <div className={styles.intro}><div><p className={styles.eyebrow}>FOUNDATION / NAVIGATION</p><h1>이동 화면에 도착했습니다</h1><p className={styles.muted}>브라우저의 뒤로 가기로 이전 화면에 돌아갈 수 있습니다.</p></div></div>
    <section className={styles.panel}><h2>화면 이동 확인</h2><p className={styles.description}>화면 간 링크와 브라우저 이력 이동을 확인합니다. 제품 목록의 검색 조건·스크롤 복원은 해당 기능에서 검증합니다.</p><nav className={styles.navigation} aria-label="연결 확인 화면"><Link to="/__dev/foundation"><strong>연결 확인으로</strong><small>확인 화면 다시 열기</small><b aria-hidden="true">←</b></Link><Link to="/"><strong>처음으로</strong><small>기본 화면</small><b aria-hidden="true">↗</b></Link></nav></section>
  </main>;
}
