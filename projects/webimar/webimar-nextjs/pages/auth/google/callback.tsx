import { useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';

export default function GoogleCallbackPage() {
  const router = useRouter();

  useEffect(() => {
    if (!router.isReady) return;

    const queryString = window.location.search;
    const bridgeUrl = `${window.location.origin}/hesaplama/auth/google/callback${queryString}`;

    window.location.replace(bridgeUrl);
  }, [router.isReady]);

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
          Giriş akışı React callback hattına devrediliyor...
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
