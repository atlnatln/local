import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Seo from '../components/Seo';
import Layout from '../components/Layout';
import styles from '../styles/AccountPage.module.css';
import { AuthUser, clearAuthSession, logoutFromBackend, resolveAuthenticatedSession } from '../lib/authSync';

const AccountPage: React.FC = () => {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const session = await resolveAuthenticatedSession();

        if (!session.isAuthenticated || !session.user) {
          await router.push('/login');
          return;
        }

        setUser(session.user);
      } catch (error) {
        console.error('Auth check error:', error);
        await router.push('/login');
      } finally {
        setIsLoading(false);
      }
    };

    void checkAuth();
  }, [router]);

  const handleLogout = async () => {
    try {
      await logoutFromBackend();
    } finally {
      clearAuthSession({ reason: 'manual-logout' });
      await router.replace('/');
    }
  };

  if (isLoading) {
    return (
      <Layout>
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
          <div>Yükleniyor...</div>
        </div>
      </Layout>
    );
  }

  return (
    <>
      <Seo
        title="Hesabım - Tarım İmar"
        description="Tarım İmar hesabınız, hesap bilgileriniz ve ayarlarınız"
        canonical="https://tarimimar.com.tr/account/"
        url="https://tarimimar.com.tr/account/"
        ogImage="https://tarimimar.com.tr/og-image.svg"
        type="website"
        keywords="hesap, profil, tarım imar, hesap ayarları"
      />

      <Layout>
        <div className={styles.accountContainer}>
          <div className={styles.accountHeader}>
            <h1>Hesabım</h1>
            <p>Hesap bilgileriniz ve ayarlarınız</p>
          </div>

          <div className={styles.accountContent}>
            <div className={styles.accountCard}>
              <h2>Kullanıcı Bilgileri</h2>
              <div className={styles.userInfo}>
                <div className={styles.infoItem}>
                  <label>E-posta:</label>
                  <span>{user?.email || 'Bilgi bulunamadı'}</span>
                </div>
                <div className={styles.infoItem}>
                  <label>Kullanıcı Adı:</label>
                  <span>{user?.username || 'Bilgi bulunamadı'}</span>
                </div>
                <div className={styles.infoItem}>
                  <label>Üyelik Durumu:</label>
                  <span className={styles.statusActive}>Aktif</span>
                </div>
              </div>
            </div>

            <div className={styles.accountCard}>
              <h2>Hesap İşlemleri</h2>
              <div className={styles.actions}>
                <button
                  className={styles.actionButton}
                  onClick={() => router.push('/')}
                >
                  Ana Sayfa
                </button>
                <button
                  className={`${styles.actionButton} ${styles.logoutButton}`}
                  onClick={handleLogout}
                >
                  Çıkış Yap
                </button>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    </>
  );
};

export default AccountPage;
