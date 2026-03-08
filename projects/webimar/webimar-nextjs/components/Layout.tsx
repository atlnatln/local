import React, { useCallback, useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Footer from './Footer';
import styles from '../styles/Layout.module.css';
import {
  AUTH_CHANGE_EVENT,
  AuthUser,
  clearAuthSession,
  logoutFromBackend,
  readSharedAuthState,
  readStoredTokens,
  readStoredUser,
  resolveAuthenticatedSession,
} from '../lib/authSync';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const router = useRouter();
  const [isClient, setIsClient] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<AuthUser | null>(null);
  const syncRequestRef = useRef(0);

  const syncAuthState = useCallback(async () => {
    const requestId = ++syncRequestRef.current;
    setIsClient(true);

    const sharedState = readSharedAuthState<AuthUser>();
    const storedUser = readStoredUser<AuthUser>() || sharedState?.user || null;
    const { accessToken, refreshToken } = readStoredTokens();

    if (!accessToken && !refreshToken) {
      if (requestId !== syncRequestRef.current) return;
      setIsAuthenticated(false);
      setUser(null);
      return;
    }

    if (accessToken && storedUser) {
      setIsAuthenticated(true);
      setUser(storedUser);
    }

    const resolved = await resolveAuthenticatedSession();
    if (requestId !== syncRequestRef.current) return;

    setIsAuthenticated(resolved.isAuthenticated);
    setUser(resolved.user);
  }, []);

  useEffect(() => {
    void syncAuthState();

    const handleStorageChange = () => {
      void syncAuthState();
    };
    const handleAuthChange = () => {
      void syncAuthState();
    };
    const handleFocus = () => {
      void syncAuthState();
    };
    const handleVisibility = () => {
      void syncAuthState();
    };

    window.addEventListener('storage', handleStorageChange);
    window.addEventListener(AUTH_CHANGE_EVENT, handleAuthChange as EventListener);
    window.addEventListener('focus', handleFocus);
    document.addEventListener('visibilitychange', handleVisibility);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener(AUTH_CHANGE_EVENT, handleAuthChange as EventListener);
      window.removeEventListener('focus', handleFocus);
      document.removeEventListener('visibilitychange', handleVisibility);
    };
  }, [syncAuthState]);

  const handleLogin = () => {
    const baseUrl = process.env.NEXT_PUBLIC_REACT_SPA_URL || '/hesaplama';

    if (isAuthenticated) {
      window.location.href = `${baseUrl}/account`;
    } else {
      const returnUrl = router.asPath || '/';
      if (typeof window !== 'undefined') {
        window.localStorage.setItem('returnUrl', returnUrl);
        window.sessionStorage.setItem('returnUrl', returnUrl);
      }
      window.location.href = `${baseUrl}/login`;
    }
  };

  const handleLogout = async () => {
    try {
      await logoutFromBackend();
    } finally {
      clearAuthSession({ reason: 'manual-logout' });
      setIsAuthenticated(false);
      setUser(null);
      window.location.replace('/');
    }
  };

  if (!isClient) {
    return (
      <div className={styles.layoutContainer}>
        <main className={styles.mainContent}>
          <header className={styles.header}>
            <div className={styles.waveBackground}></div>
            <div className={styles.headerContent}>
              <div className={styles.headerCenter}>
                <div className={styles.animatedHeaderWrapper}>
                  <Link href="/" style={{ textDecoration: 'none', color: 'inherit' }}>
                    <span className={styles.modernHeaderTitle}>
                      <span style={{ letterSpacing: '2px' }}>🌾</span>
                      <span style={{ display: 'inline-block', width: '0.2em' }}></span>
                      <span style={{ letterSpacing: '2px' }}>tarım</span>
                      <span style={{ display: 'inline-block', width: '0.35em' }}></span>
                      <span style={{ letterSpacing: '2px' }}>imar</span>
                      <span style={{ display: 'inline-block', width: '0.2em' }}></span>
                      <span style={{ letterSpacing: '2px' }}>🏗️</span>
                    </span>
                  </Link>
                </div>
              </div>
              <div className={styles.headerRight}>
                <div className={styles.userActions}>
                  <button className={`${styles.userButton} ${styles.login}`}>
                    <span className={styles.desktopText}>Giriş Yap</span>
                  </button>
                </div>
              </div>
            </div>
          </header>
          <div className={styles.contentArea}>
            {children}
          </div>
        </main>
      </div>
    );
  }

  return (
    <>
      <Head>
        {/* Performance optimizations */}
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
      </Head>
      <div className={styles.layoutContainer}>
        <main className={styles.mainContent}>
          <header className={styles.header}>
            <div className={styles.waveBackground}></div>
            <div className={styles.headerContent}>
              <div className={styles.headerCenter}>
                <div className={styles.animatedHeaderWrapper}>
                  <Link href="/" style={{ textDecoration: 'none', color: 'inherit' }}>
                    <span className={styles.modernHeaderTitle}>
                      <span style={{ letterSpacing: '2px' }}>🌾</span>
                      <span style={{ display: 'inline-block', width: '0.2em' }}></span>
                      <span style={{ letterSpacing: '2px' }}>tarım</span>
                      <span style={{ display: 'inline-block', width: '0.35em' }}></span>
                      <span style={{ letterSpacing: '2px' }}>imar</span>
                      <span style={{ display: 'inline-block', width: '0.2em' }}></span>
                      <span style={{ letterSpacing: '2px' }}>🏗️</span>
                    </span>
                  </Link>
                </div>
              </div>

            <div className={styles.headerRight}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px' }}>
                <div style={{ display: 'flex', gap: '8px' }}>
                  {!isAuthenticated ? (
                    <button className={`${styles.userButton} ${styles.login}`} onClick={handleLogin}>
                      <span className={styles.desktopText}>Giriş Yap</span>
                    </button>
                  ) : (
                    <>
                      <button className={`${styles.userButton} ${styles.profile}`} onClick={handleLogin}>
                        <span className={styles.mobileIcon}>👤</span><span className={styles.desktopText}>Hesabım</span>
                      </button>
                      <button className={`${styles.userButton} ${styles.logout}`} onClick={handleLogout}>
                        <span className={styles.mobileIcon}>🚪</span><span className={styles.desktopText}>Çıkış</span>
                      </button>
                    </>
                  )}
                </div>
                {isAuthenticated && user && (
                  <div className={styles.userInfo}>
                    {user.email || user.username || 'Kullanıcı'}
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>
        <div className={styles.contentArea}>
          {children}
        </div>
        <Footer />
      </main>
    </div>
    </>
  );
};

export default Layout;
