
import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { setAuthCookie } from '../utils/authCookie';
import { navigateToNextJs, getApiBaseUrl } from '../utils/environment';
import { persistAuthSession } from '../utils/authSync';

const GoogleCallback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const handleCallback = async () => {
      try {
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
          userEmail,
        });

        if (error) {
          setStatus('error');
          setMessage(errorMessage || 'Google girişi sırasında hata oluştu');
          return;
        }

        if (requiresApproval === 'true') {
          setStatus('error');
          setMessage(`${userEmail} için admin onayı bekleniyor. Kısa süre içinde e-posta alacaksınız.`);
          return;
        }

        if (!accessToken || !refreshToken) {
          setStatus('error');
          setMessage('Eksik yetkilendirme bilgileri. Lütfen tekrar giriş yapın.');
          return;
        }

        // /accounts/me/ ile kullanıcı bilgilerini al – token'ları henüz storage'a yazmıyoruz
        // böylece eski {isAuthenticated:false} shared state → finalizeLocalLogout race'i önlenir
        console.log('🔑 /accounts/me/ doğrulaması...');
        const meResponse = await fetch(`${getApiBaseUrl()}/accounts/me/`, {
          headers: { Authorization: `Bearer ${accessToken}` },
        });

        if (!meResponse.ok) {
          console.error('❌ /accounts/me/ başarısız:', meResponse.status);
          setStatus('error');
          setMessage('Kullanıcı doğrulaması başarısız. Lütfen tekrar giriş yapın.');
          return;
        }

        const userData = await meResponse.json();
        console.log('✅ Kullanıcı doğrulandı:', userData.email);

        // Tüm token + user + shared state'i tek atomik yazıyla kaydet.
        // persistAuthSession, webimar_auth_state'i {isAuthenticated:true} olarak yazar
        // ÖNCE, sonra event dispatch eder → syncAuthSignal artık yanlışlıkla logout yapmaz.
        persistAuthSession({
          accessToken,
          refreshToken,
          user: userData,
          source: 'react',
          reason: 'google-callback',
        });

        // Cookie (UI göstergesi amaçlı)
        try {
          if (userData?.email) setAuthCookie(userData.email);
        } catch (cookieError) {
          console.warn('Cookie ayarlama hatası:', cookieError);
        }

        setStatus('success');
        setMessage('Google ile giriş başarılı! Yönlendiriliyorsunuz...');

        setTimeout(() => {
          const returnUrl =
            localStorage.getItem('returnUrl') ||
            sessionStorage.getItem('returnUrl') ||
            '/';
          localStorage.removeItem('returnUrl');
          sessionStorage.removeItem('returnUrl');
          console.log('🔄 Google OAuth başarılı → yönlendiriliyor:', returnUrl);
          navigateToNextJs(returnUrl);
        }, 150);

      } catch (err: any) {
        console.error('Google callback hatası:', err);
        setStatus('error');
        setMessage('Giriş işlemi sırasında beklenmeyen hata oluştu.');
      }
    };

    handleCallback();
  }, [searchParams, navigate]);

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
