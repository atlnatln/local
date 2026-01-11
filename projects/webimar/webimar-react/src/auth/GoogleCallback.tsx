
import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from './AuthContext';
import { tokenStorage } from '../utils/tokenStorage';
import { setAuthCookie } from '../utils/authCookie';
import { navigateToNextJs } from '../utils/environment';

const GoogleCallback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { checkAuthStatus } = useAuth();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // URL parametrelerini al
        const accessToken = searchParams.get('access');
        const refreshToken = searchParams.get('refresh');
        const error = searchParams.get('error');
        const errorMessage = searchParams.get('message');
        const requiresApproval = searchParams.get('requires_approval');
        const userEmail = searchParams.get('user_email');

        console.log('🔍 Google OAuth Callback Params:', {
          hasAccess: !!accessToken,
          hasRefresh: !!refreshToken,
          error,
          requiresApproval,
          userEmail
        });

        if (error) {
          // Hata durumu
          setStatus('error');
          setMessage(errorMessage || 'Google girişi sırasında hata oluştu');
          return;
        }

        if (requiresApproval === 'true') {
          // Admin onayı bekleniyor
          setStatus('error');
          setMessage(`${userEmail} için admin onayı bekleniyor. Kısa süre içinde e-posta alacaksınız.`);
          return;
        }

        if (!accessToken || !refreshToken) {
          // Token'lar eksik
          setStatus('error');
          setMessage('Eksik yetkilendirme bilgileri. Lütfen tekrar giriş yapın.');
          return;
        }

        // Token'ları tokenStorage'a kaydet
        console.log('💾 Token\'ları kaydediyor...');
        tokenStorage.setAccessToken(accessToken);
        tokenStorage.setRefreshToken(refreshToken);

        // --- CRITICAL: Next ile uyumlu localStorage anahtarları set et ---
        try {
          localStorage.setItem('access_token', accessToken);
          localStorage.setItem('refresh_token', refreshToken);
          localStorage.setItem('token', accessToken);
        } catch (e) {
          console.warn('localStorage write failed in GoogleCallback:', e);
        }
        // -------------------------------------------------------------

        // Auth durumunu kontrol et ve user bilgilerini al
        await checkAuthStatus(true); // force refresh

        // User bilgilerini al ve kaydet
        const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
        const userResponse = await fetch(`${API_BASE_URL}/accounts/me/`, {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
        });

        if (userResponse.ok) {
          const userData = await userResponse.json();
          tokenStorage.setUser(userData);
          try {
            localStorage.setItem('user', JSON.stringify(userData));
            const authState = {
              isAuthenticated: true,
              user: userData,
              timestamp: Date.now()
            };
            localStorage.setItem('webimar_auth_state', JSON.stringify(authState));
          } catch (e) {
            console.warn('localStorage user/webimar_auth_state write failed:', e);
          }
          console.log('✅ User bilgileri kaydedildi:', userData);
        } else {
          console.warn('⚠️ User bilgileri alınamadı, devam ediliyor...');
        }

        // Cookie ayarla
        try {
          const user = tokenStorage.getUser();
          if (user?.email) {
            setAuthCookie(user.email);
          }
        } catch (cookieError) {
          console.warn('Cookie ayarlama hatası:', cookieError);
        }

        setStatus('success');
        setMessage('Google ile giriş başarılı! Yönlendiriliyorsunuz...');

        // Yönlendirmeyi token ve storage setlendikten sonra yap
        setTimeout(() => {
          const returnUrl = localStorage.getItem('returnUrl') || sessionStorage.getItem('returnUrl') || '/';
          localStorage.removeItem('returnUrl');
          sessionStorage.removeItem('returnUrl');
          
          console.log('🔄 Google OAuth başarılı - Next.js\'e yönlendiriliyor:', returnUrl);
          
          // Next.js ana sayfasına yönlendir
          navigateToNextJs(returnUrl);
        }, 150);

      } catch (err: any) {
        console.error('Google callback hatası:', err);
        setStatus('error');
        setMessage('Giriş işlemi sırasında beklenmeyen hata oluştu.');
      }
    };

    handleCallback();
  }, [searchParams, navigate, checkAuthStatus]);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '50vh',
      padding: '20px',
      textAlign: 'center'
    }}>
      {status === 'loading' && (
        <>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>⏳</div>
          <h2>Google Girişi İşleniyor...</h2>
          <p>Lütfen bekleyin, yönlendirme yapılıyor.</p>
        </>
      )}

      {status === 'success' && (
        <>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>✅</div>
          <h2>Giriş Başarılı!</h2>
          <p>{message}</p>
        </>
      )}

      {status === 'error' && (
        <>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>❌</div>
          <h2>Giriş Başarısız</h2>
          <p style={{ color: '#dc3545', marginBottom: '20px' }}>{message}</p>
          <button
            onClick={() => navigate('/login')}
            style={{
              padding: '10px 20px',
              background: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer'
            }}
          >
            Tekrar Dene
          </button>
        </>
      )}
    </div>
  );
};

export default GoogleCallback;
