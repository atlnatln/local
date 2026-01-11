import { useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';

export default function GoogleCallbackPage() {
  const router = useRouter();

  useEffect(() => {
    if (!router.isReady) return;

    // URL parametrelerinden token'ları al
    const { access, refresh, requires_approval, user_email, error, message } = router.query;

    if (error) {
      console.error('Google OAuth Hata:', error, message);
      // Hata durumunda ana sayfaya yönlendir
      router.push('/?auth_error=' + encodeURIComponent(error as string));
      return;
    }

    if (requires_approval === 'true') {
      // Admin onay bekleyen kullanıcı
      console.log('Kullanıcı admin onay bekliyor:', user_email);
      router.push('/?requires_approval=true&email=' + encodeURIComponent(user_email as string || ''));
      return;
    }

    if (access && refresh) {
      // Token'ları localStorage'a kaydet
      try {
        localStorage.setItem('access_token', access as string);
        localStorage.setItem('refresh_token', refresh as string);
        
        // Kullanıcı bilgilerini çek ve state'i güncelle
        const fetchUserAndRedirect = async () => {
          try {
            const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://tarimimar.com.tr/api';
            const response = await fetch(`${API_BASE_URL}/accounts/me/`, {
              headers: {
                'Authorization': `Bearer ${access}`
              }
            });

            if (response.ok) {
              const userData = await response.json();
              localStorage.setItem('user', JSON.stringify(userData));
              
              // Layout.tsx için shared state güncelle
              const authState = {
                isAuthenticated: true,
                user: userData,
                timestamp: new Date().getTime()
              };
              localStorage.setItem('webimar_auth_state', JSON.stringify(authState));
              console.log('✅ User data fetched and state updated:', userData);
            } else {
              console.error('⚠️ Failed to fetch user data:', response.status);
            }
          } catch (err) {
            console.error('💥 Error fetching user data:', err);
          } finally {
            // Başarılı giriş sonrası ana sayfaya yönlendir
            const returnUrl = localStorage.getItem('returnUrl') || sessionStorage.getItem('returnUrl') || '/';
            
            // Return URL'yi temizle
            localStorage.removeItem('returnUrl');
            sessionStorage.removeItem('returnUrl');
            
            console.log('Google OAuth başarılı - Yönlendiriliyor:', returnUrl);
            router.push(returnUrl);
          }
        };

        fetchUserAndRedirect();
        
      } catch (error) {
        console.error('Token kaydetme hatası:', error);
        router.push('/?auth_error=token_storage');
      }
    } else {
      console.error('Google OAuth: Token bulunamadı');
      router.push('/?auth_error=no_tokens');
    }
  }, [router.isReady, router.query]);

  return (
    <>
      <Head>
        <title>Google Girişi İşleniyor... | Tarımımar</title>
        <meta name="robots" content="noindex,nofollow" />
      </Head>
      
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        flexDirection: 'column',
        fontFamily: 'Inter, sans-serif'
      }}>
        <div style={{
          width: '32px',
          height: '32px',
          border: '3px solid #f3f3f3',
          borderTop: '3px solid #22c55e',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          marginBottom: '16px'
        }} />
        
        <p style={{ color: '#6b7280', fontSize: '16px', margin: '0' }}>
          Google giriş bilgileriniz işleniyor...
        </p>
        
        <style jsx>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </>
  );
}
