import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useToast } from '../../hooks/useToast';
import { emailService } from '../../services/emailService';
import { getNextJsUrl } from '../../utils/environment';

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

  &:hover {
    background: #047857;
    transform: translateY(-1px);
  }

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
    transform: none;
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

const EmailChangeConfirm: React.FC = () => {
  const { uid, token } = useParams<{ uid: string; token: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { showSuccess, showError } = useToast();
  
  const [loading, setLoading] = useState(true);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const newEmail = searchParams.get('new_email');

  useEffect(() => {
    const confirmEmailChange = async () => {
      if (!uid || !token || !newEmail) {
        setError('Geçersiz doğrulama linki.');
        setLoading(false);
        return;
      }

      try {
        const response = await emailService.confirmEmailChange(uid, token, newEmail);
        
        if (response.success) {
          setSuccess(true);
          showSuccess('E-posta adresiniz başarıyla değiştirildi!');
        } else {
          setError(response.message || 'E-posta değişikliği onaylanamadı.');
          showError(response.message || 'E-posta değişikliği onaylanamadı.');
        }
      } catch (err: any) {
        setError('Bağlantı hatası oluştu. Lütfen tekrar deneyin.');
        showError('Bağlantı hatası oluştu.');
      } finally {
        setLoading(false);
      }
    };

    confirmEmailChange();
  }, [uid, token, newEmail, showSuccess, showError]);

  const handleGoToLogin = () => {
    navigate('/login');
  };

  const handleGoHome = () => {
    window.location.href = getNextJsUrl();
  };

  if (loading) {
    return (
      <Container>
        <Card>
          <LoadingSpinner />
          <Title>E-posta Değişikliği Onaylanıyor...</Title>
          <Message>Lütfen bekleyiniz, işleminiz gerçekleştiriliyor.</Message>
        </Card>
      </Container>
    );
  }

  if (success) {
    return (
      <Container>
        <Card>
          <SuccessIcon>✅</SuccessIcon>
          <Title>E-posta Değişikliği Başarılı!</Title>
          <Message>
            E-posta adresiniz başarıyla <strong>{newEmail}</strong> olarak değiştirildi.
            <br />
            Artık yeni e-posta adresinizle giriş yapabilirsiniz.
          </Message>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
            <Button onClick={handleGoToLogin}>Giriş Yap</Button>
            <Button onClick={handleGoHome} style={{ background: '#6b7280' }}>Ana Sayfa</Button>
          </div>
        </Card>
      </Container>
    );
  }

  return (
    <Container>
      <Card>
        <ErrorIcon>❌</ErrorIcon>
        <Title>E-posta Değişikliği Başarısız</Title>
        <Message>
          {error || 'E-posta değişikliği onaylanamadı. Link geçersiz veya süresi dolmuş olabilir.'}
        </Message>
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
          <Button onClick={handleGoToLogin}>Giriş Yap</Button>
          <Button onClick={handleGoHome} style={{ background: '#6b7280' }}>Ana Sayfa</Button>
        </div>
      </Card>
    </Container>
  );
};

export default EmailChangeConfirm;
