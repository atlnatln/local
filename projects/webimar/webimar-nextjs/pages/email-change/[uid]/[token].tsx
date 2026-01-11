import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Seo from '../../../components/Seo';
import styled from 'styled-components';

const Container = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
`;

const Card = styled.div`
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  width: 100%;
  text-align: center;
`;

const Title = styled.h1`
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 16px;
`;

const Message = styled.p`
  font-size: 16px;
  color: #6b7280;
  margin-bottom: 24px;
  line-height: 1.6;
`;

const Button = styled.button`
  background: #059669;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin: 0 6px;

  &:hover {
    background: #047857;
    transform: translateY(-1px);
  }

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
    transform: none;
  }

  &.secondary {
    background: #6b7280;
    &:hover {
      background: #4b5563;
    }
  }
`;

const LoadingSpinner = styled.div`
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #059669;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ErrorIcon = styled.div`
  font-size: 48px;
  margin-bottom: 20px;
`;

const SuccessIcon = styled.div`
  font-size: 48px;
  margin-bottom: 20px;
`;

// Email service utility function
const confirmEmailChange = async (uid: string, token: string, newEmail: string) => {
  try {
    const API_BASE_URL = process.env.NODE_ENV === 'production' 
      ? 'https://tarimimar.com.tr/api'
      : 'http://localhost:8000/api';
      
    const response = await fetch(`${API_BASE_URL}/accounts/confirm-email-change/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        uid: uid,
        token: token,
        new_email: newEmail
      }),
    });

    const data = await response.json();
    
    if (response.status === 429) {
      return {
        success: false,
        message: 'Çok fazla istek gönderildi. Lütfen daha sonra tekrar deneyin.'
      };
    }

    return data;
  } catch (error) {
    console.error('Email change confirmation error:', error);
    return {
      success: false,
      message: 'Ağ hatası oluştu'
    };
  }
};

const EmailChangeConfirm: React.FC = () => {
  const router = useRouter();
  const { uid, token, new_email } = router.query;
  
  const [loading, setLoading] = useState(true);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleConfirmEmailChange = async () => {
      // Router henüz hazır değilse bekle
      if (!router.isReady) return;

      if (!uid || !token || !new_email) {
        setError('Geçersiz doğrulama linki.');
        setLoading(false);
        return;
      }

      try {
        const response = await confirmEmailChange(
          uid as string, 
          token as string, 
          new_email as string
        );
        
        if (response.success) {
          setSuccess(true);
        } else {
          setError(response.message || 'E-posta değişikliği onaylanamadı.');
        }
      } catch (err: any) {
        setError('Bağlantı hatası oluştu. Lütfen tekrar deneyin.');
      } finally {
        setLoading(false);
      }
    };

    handleConfirmEmailChange();
  }, [router.isReady, uid, token, new_email]);

  const handleGoToLogin = () => {
    const loginUrl = `${process.env.NEXT_PUBLIC_REACT_SPA_URL || '/hesaplama'}/login`;
    window.location.href = loginUrl;
  };

  const handleGoHome = () => {
    router.push('/');
  };

  if (loading) {
    return (
      <>
        <Seo
          title="E-posta Değişikliği Onaylanıyor - Tarım İmar"
          description="E-posta değişikliği onaylanıyor"
          canonical="https://tarimimar.com.tr/email-change"
          url="https://tarimimar.com.tr/email-change"
          ogImage="https://tarimimar.com.tr/og-image.svg"
          type="website"
          keywords="e-posta değişikliği, onay, tarım imar"
        />
        <Container>
          <Card>
            <LoadingSpinner />
            <Title>E-posta Değişikliği Onaylanıyor...</Title>
            <Message>Lütfen bekleyiniz, işleminiz gerçekleştiriliyor.</Message>
          </Card>
        </Container>
      </>
    );
  }

  if (success) {
    return (
      <>
        <Seo
          title="E-posta Değişikliği Başarılı - Tarım İmar"
          description="E-posta adresiniz başarıyla değiştirildi"
          canonical="https://tarimimar.com.tr/email-change"
          url="https://tarimimar.com.tr/email-change"
          ogImage="https://tarimimar.com.tr/og-image.svg"
          type="website"
          keywords="e-posta değişikliği, başarılı, tarım imar"
        />
        <Container>
          <Card>
            <SuccessIcon>✅</SuccessIcon>
            <Title>E-posta Değişikliği Başarılı!</Title>
            <Message>
              E-posta adresiniz başarıyla <strong>{new_email}</strong> olarak değiştirildi.
              <br />
              Artık yeni e-posta adresinizle giriş yapabilirsiniz.
            </Message>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
              <Button onClick={handleGoToLogin}>Giriş Yap</Button>
              <Button onClick={handleGoHome} className="secondary">Ana Sayfa</Button>
            </div>
          </Card>
        </Container>
      </>
    );
  }

  return (
    <>
      <Seo
        title="E-posta Değişikliği Başarısız - Tarım İmar"
        description="E-posta değişikliği onaylanamadı"
        canonical="https://tarimimar.com.tr/email-change"
        url="https://tarimimar.com.tr/email-change"
        ogImage="https://tarimimar.com.tr/og-image.svg"
        type="website"
        keywords="e-posta değişikliği, başarısız, tarım imar"
      />
      <Container>
        <Card>
          <ErrorIcon>❌</ErrorIcon>
          <Title>E-posta Değişikliği Başarısız</Title>
          <Message>
            {error || 'E-posta değişikliği onaylanamadı. Link geçersiz veya süresi dolmuş olabilir.'}
          </Message>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button onClick={handleGoToLogin}>Giriş Yap</Button>
            <Button onClick={handleGoHome} className="secondary">Ana Sayfa</Button>
          </div>
        </Card>
      </Container>
    </>
  );
};

export default EmailChangeConfirm;
