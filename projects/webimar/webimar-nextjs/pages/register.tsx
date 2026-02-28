import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Seo from '../components/Seo';

const RegisterPage: React.FC = () => {
  const router = useRouter();

  useEffect(() => {
    // React uygulamasına yönlendir - client-side origin kullan
    const redirectTo = router.query.redirect || '/';
    const registerPath = '/hesaplama/auth/register';
    window.location.href = `${window.location.origin}${registerPath}?redirect=${encodeURIComponent(redirectTo as string)}`;
  }, [router.query.redirect]);

  return (
    <>
      <Seo
        title="Kayıt Ol - Tarım İmar"
        description="Tarım İmar hesabınızı oluşturun ve hesaplama araçlarına erişin"
        canonical="https://tarimimar.com.tr/register/"
        url="https://tarimimar.com.tr/register/"
        ogImage="https://tarimimar.com.tr/og-image.svg"
        type="website"
        keywords="kayıt, hesap oluşturma, tarım imar, üye ol"
      />
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: '#f8f9fa',
        fontFamily: 'Inter, sans-serif'
      }}>
        <div style={{
          background: 'white',
          borderRadius: '8px',
          padding: '32px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
          textAlign: 'center',
          maxWidth: '400px',
          width: '100%'
        }}>
          <h2 style={{ color: '#333', marginBottom: '16px' }}>
            Kayıt Olunuyor...
          </h2>
          <p style={{ color: '#666', marginBottom: '24px' }}>
            Tarım İmar hesap oluşturma sayfasına yönlendiriliyorsunuz.
          </p>
          <div style={{
            border: '3px solid #f3f3f3',
            borderTop: '3px solid #28a745',
            borderRadius: '50%',
            width: '32px',
            height: '32px',
            animation: 'spin 1s linear infinite',
            margin: '0 auto'
          }} />
          <style jsx>{`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}</style>
        </div>
      </div>
    </>
  );
};

export default RegisterPage;
