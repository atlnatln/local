import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import Head from 'next/head';
import styles from '../styles/Layout.module.css';

// Basit cookie okuma yardımcı fonksiyonu
function getCookie(name: string): string | null {
  if (typeof document === 'undefined') return null;
  const value = document.cookie
    .split('; ')
    .find((row) => row.startsWith(`${name}=`))
    ?.split('=')[1];
  return value ? decodeURIComponent(value) : null;
}

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const router = useRouter();
  const [isClient, setIsClient] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<any>(null);

  // Canonical URL oluştur
  const canonicalUrl = `https://tarimimar.com.tr${router.asPath === '/' ? '' : router.asPath}`;

  // Backend'den user bilgilerini çek
  const fetchUserFromBackend = async (token: string): Promise<any | null> => {
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 
                          (process.env.NEXT_PUBLIC_BACKEND_URL ? `${process.env.NEXT_PUBLIC_BACKEND_URL.replace(/\/$/, '')}/api` : 'https://tarimimar.com.tr/api');
      
      const response = await fetch(`${API_BASE_URL}/accounts/me/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
      });

      if (response.ok) {
        const userData = await response.json();
        console.log('✅ User data fetched from backend:', userData);
        return userData;
      } else {
        console.warn('⚠️ Failed to fetch user data:', response.status);
        return null;
      }
    } catch (error) {
      console.error('💥 Error fetching user data:', error);
      return null;
    }
  };

  useEffect(() => {
    setIsClient(true);

    // URL'den auth parametrelerini kontrol et (React SPA'dan gelen)
    const checkUrlAuthParams = () => {
      if (typeof window !== 'undefined') {
        const urlParams = new URLSearchParams(window.location.search);
        const authStatus = urlParams.get('auth');
        const userEmail = urlParams.get('user');
        
        if (authStatus === 'success' && userEmail) {
          console.log('🔗 Auth success from React SPA, syncing to Next.js localStorage');
          
          // Next.js localStorage'ına auth bilgilerini kopyala
          localStorage.setItem('token', 'synced_from_react');
          localStorage.setItem('access_token', 'synced_from_react');
          localStorage.setItem('user', JSON.stringify({ email: userEmail }));
          
          // URL'i temizle
          window.history.replaceState({}, document.title, window.location.pathname);
          
          return { authenticated: true, user: { email: userEmail } };
        }
      }
      return null;
    };

    const readAuthFromStorageOrCookies = () => {
      try {
        // Auth debug - sadece development'da göster
        if (process.env.NODE_ENV === 'development') {
          console.log('🔍 Next.js Auth Debug:');
        }
        
        // RADIKAL ÇÖZÜM: Önce shared auth state'i kontrol et
        const sharedState = typeof localStorage !== 'undefined' 
          ? localStorage.getItem('webimar_auth_state') 
          : null;
          
        if (sharedState) {
          try {
            const authData = JSON.parse(sharedState);
            const { isAuthenticated: sharedAuth, user: sharedUser } = authData;
            
            if (process.env.NODE_ENV === 'development') {
              console.log('🔄 [Next.js] Shared auth state:', authData);
            }
            
            if (sharedAuth && sharedUser) {
              setIsAuthenticated(true);
              setUser(sharedUser);
              return;
            } else {
              setIsAuthenticated(false);
              setUser(null);
              return;
            }
          } catch (e) {
            if (process.env.NODE_ENV === 'development') {
              console.log('Shared state parse error:', e);
            }
          }
        }
        
        // Önce URL'den gelen auth parametrelerini kontrol et
        const urlAuth = checkUrlAuthParams();
        if (urlAuth) {
          if (process.env.NODE_ENV === 'development') {
            console.log('✅ Auth via URL params:', urlAuth.user);
          }
          setIsAuthenticated(true);
          setUser(urlAuth.user);
          return;
        }
        
        // 1) localStorage (aynı origin ise)
        const token = typeof localStorage !== 'undefined'
          ? (localStorage.getItem('token') || localStorage.getItem('access_token'))
          : null;
        const userData = typeof localStorage !== 'undefined'
          ? localStorage.getItem('user')
          : null;

        if (process.env.NODE_ENV === 'development') {
          console.log('📦 localStorage:', {
            token: token ? 'EXISTS' : 'MISSING',
            user: userData ? 'EXISTS' : 'MISSING',
            userParsed: userData ? JSON.parse(userData) : null
          });
        }

        if (token && userData) {
          try {
            const parsedUser = JSON.parse(userData);
            if (process.env.NODE_ENV === 'development') {
              console.log('✅ Auth via localStorage:', parsedUser);
            }
            setIsAuthenticated(true);
            setUser(parsedUser);
            return;
          } catch (e) {
            if (process.env.NODE_ENV === 'development') {
              console.log('❌ localStorage parse error:', e);
            }
            // Parse hatası durumunda token varsa varsayılan user oluştur
            if (token) {
              if (process.env.NODE_ENV === 'development') {
                console.log('🔄 Creating default user from token');
              }
              setIsAuthenticated(true);
              setUser({ email: 'authenticated', username: 'authenticated' });
              return;
            }
          }
        }

        // Eğer token var ama user data yoksa, backend'den user bilgilerini çek
        if (token && !userData) {
          if (process.env.NODE_ENV === 'development') {
            console.log('🔄 Token found but no user data, fetching from backend');
          }
          setIsAuthenticated(true);
          
          // Backend'den user bilgilerini çek
          fetchUserFromBackend(token).then(fetchedUser => {
            if (fetchedUser) {
              setUser(fetchedUser);
              // User data'yı localStorage'a kaydet
              localStorage.setItem('user', JSON.stringify(fetchedUser));
            } else {
              // Fetch başarısız olursa varsayılan oluştur
              setUser({ email: 'authenticated', username: 'authenticated' });
            }
          }).catch(() => {
            setUser({ email: 'authenticated', username: 'authenticated' });
          });
          return;
        }

        // 2) Cookie fallback (farklı origin/port senaryosunda)
        const authCookie = getCookie('webimar_auth');
        const emailCookie = getCookie('webimar_user');
        if (process.env.NODE_ENV === 'development') {
          console.log('🍪 Cookies:', {
            webimar_auth: authCookie,
            webimar_user: emailCookie,
            allCookies: document.cookie
          });
        }
        
        if (authCookie === '1') {
          if (process.env.NODE_ENV === 'development') {
            console.log('✅ Auth via cookies');
          }
          setIsAuthenticated(true);
          if (emailCookie && (!user || !user.email)) {
            setUser({ email: emailCookie });
          }
          return;
        }

        // 3) Hiçbiri yoksa logout state
        if (process.env.NODE_ENV === 'development') {
          console.log('❌ No auth found');
        }
        setIsAuthenticated(false);
        setUser(null);
      } catch (err) {
        console.log('🚨 Auth check error:', err);
        setIsAuthenticated(false);
        setUser(null);
      }
    };

    // İlk yüklemede kontrol et
    readAuthFromStorageOrCookies();

    // Storage değişikliklerini dinle (aynı origin)
    const handleStorageChange = () => readAuthFromStorageOrCookies();
    window.addEventListener('storage', handleStorageChange);

    // RADIKAL ÇÖZÜM: Sürekli auth state kontrolü (daha az sıklıkta)
    const authStateInterval = setInterval(() => {
      readAuthFromStorageOrCookies();
    }, 5000); // Her 5 saniyede bir kontrol et

    // Sekmeye odaklanınca/canlılık değişince cookie'leri tekrar kontrol et
    const handleFocus = () => readAuthFromStorageOrCookies();
    const handleVisibility = () => readAuthFromStorageOrCookies();
    window.addEventListener('focus', handleFocus);
    document.addEventListener('visibilitychange', handleVisibility);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('focus', handleFocus);
      document.removeEventListener('visibilitychange', handleVisibility);
      clearInterval(authStateInterval);
    };
  }, []);

  const handleLogin = () => {
    const baseUrl = process.env.NEXT_PUBLIC_REACT_SPA_URL || '/hesaplama';
    
    if (isAuthenticated) {
      // Kullanıcı giriş yapmışsa React SPA'daki account sayfasına yönlendir
      window.location.href = `${baseUrl}/account`;
    } else {
      // Giriş yapmamışsa React SPA'daki login sayfasına yönlendir
      window.location.href = `${baseUrl}/login`;
    }
  };

  const handleLogout = () => {
    if (process.env.NODE_ENV === 'development') {
      console.log('🔄 [Next.js] Logout initiated');
    }
    
    // RADIKAL ÇÖZÜM: Shared auth state
    const authState = {
      isAuthenticated: false,
      user: null,
      timestamp: Date.now()
    };
    
    // Tüm token türlerini temizle
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem('token');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      localStorage.removeItem('accessToken');
      localStorage.setItem('webimar_auth_state', JSON.stringify(authState));
    }
    
    // Cookie'leri temizle
    if (typeof document !== 'undefined') {
      document.cookie = 'webimar_auth=; Max-Age=0; path=/';
      document.cookie = 'webimar_user=; Max-Age=0; path=/';
    }

    setIsAuthenticated(false);
    setUser(null);

    if (process.env.NODE_ENV === 'development') {
      console.log('✅ [Next.js] Auth state cleared - redirecting');
    }
    
    // Direkt yönlendirme
    window.location.href = '/';
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
                    <h1 className={styles.modernHeaderTitle}>
                      <span style={{ letterSpacing: '2px' }}>🌾</span>
                      <span style={{ display: 'inline-block', width: '0.2em' }}></span>
                      <span style={{ letterSpacing: '2px' }}>tarım</span>
                      <span style={{ display: 'inline-block', width: '0.35em' }}></span>
                      <span style={{ letterSpacing: '2px' }}>imar</span>
                      <span style={{ display: 'inline-block', width: '0.2em' }}></span>
                      <span style={{ letterSpacing: '2px' }}>🏗️</span>
                    </h1>
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
                    <h1 className={styles.modernHeaderTitle}>
                      <span style={{ letterSpacing: '2px' }}>🌾</span>
                      <span style={{ display: 'inline-block', width: '0.2em' }}></span>
                      <span style={{ letterSpacing: '2px' }}>tarım</span>
                      <span style={{ display: 'inline-block', width: '0.35em' }}></span>
                      <span style={{ letterSpacing: '2px' }}>imar</span>
                      <span style={{ display: 'inline-block', width: '0.2em' }}></span>
                      <span style={{ letterSpacing: '2px' }}>🏗️</span>
                    </h1>
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
      </main>
    </div>
    </>
  );
};

export default Layout;
