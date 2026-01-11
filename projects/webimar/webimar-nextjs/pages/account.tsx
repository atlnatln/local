import React, { useEffect, useState } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import Seo from '../components/Seo';
import Layout from '../components/Layout';
import styles from '../styles/AccountPage.module.css';

const AccountPage: React.FC = () => {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Kullanıcı bilgilerini localStorage'dan al
    const checkAuth = () => {
      try {
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        const userData = localStorage.getItem('user');

        if (!token) {
          // Giriş yapılmamışsa login sayfasına yönlendir
          router.push('/login');
          return;
        }

        if (userData) {
          const parsedUser = JSON.parse(userData);
          setUser(parsedUser);
        } else {
          // User data yoksa varsayılan oluştur
          setUser({ email: 'authenticated', username: 'authenticated' });
        }
      } catch (error) {
        console.error('Auth check error:', error);
        router.push('/login');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  const handleLogout = () => {
    // Tüm auth bilgilerini temizle
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('webimar_auth_state');

    // Ana sayfaya yönlendir
    router.push('/');
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
        canonical="https://tarimimar.com.tr/account"
        url="https://tarimimar.com.tr/account"
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
