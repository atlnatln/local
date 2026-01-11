import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { getNextJsUrl } from '../utils/environment';

const Container = styled.div`
  max-width: 400px;
  margin: 60px auto;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  padding: 32px 24px;
  text-align: center;
`;

const Title = styled.h2`
  color: #059669;
  margin-bottom: 18px;
`;

const Message = styled.div`
  font-size: 16px;
  margin-bottom: 18px;
  color: #374151;
`;

const Button = styled.button`
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 10px 24px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 18px;
`;

const VerifyEmail: React.FC = () => {
  const { uid, token } = useParams<{ uid?: string; token?: string }>();
  const navigate = useNavigate();
  const [status, setStatus] = useState('loading');
  const [message, setMessage] = useState('E-posta doğrulanıyor...');
  const [showResendButton, setShowResendButton] = useState(false);

  useEffect(() => {
    if (!uid || !token) {
      setStatus('error');
      setMessage('Doğrulama için gerekli bilgiler eksik.');
      return;
    }
    fetch(`${process.env.REACT_APP_API_BASE_URL || '/api'}/accounts/verify-email/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ uid, token })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setStatus('success');
          setMessage('E-posta adresiniz başarıyla doğrulandı! Artık giriş yapabilirsiniz.');
        } else {
          setStatus('error');
          const errorMessage = data.detail || data.message || 'Doğrulama başarısız.';
          
          // Expire olmuş token için özel mesaj ve yönlendirme
          if (errorMessage.toLowerCase().includes('süresi dolmuş') || 
              errorMessage.toLowerCase().includes('geçersiz') ||
              errorMessage.toLowerCase().includes('expired')) {
            setMessage('Doğrulama linkinizin süresi dolmuş. Yeni bir doğrulama linki talep edin.');
            setShowResendButton(true);
          } else {
            setMessage(errorMessage);
          }
        }
      })
      .catch(() => {
        setStatus('error');
        setMessage('Sunucuya ulaşılamadı. Lütfen daha sonra tekrar deneyin.');
      });
  }, [uid, token]);

  return (
    <Container>
      <Title>E-posta Doğrulama</Title>
      <Message>{message}</Message>
      {status === 'success' && (
        <Button onClick={() => navigate('/login')}>Giriş Yap</Button>
      )}
      {status === 'error' && !showResendButton && (
        <Button onClick={() => window.location.href = getNextJsUrl()}>Ana Sayfa</Button>
      )}
      {showResendButton && (
        <>
          <Button onClick={() => navigate('/login')}>Giriş Yap</Button>
          <Button onClick={() => navigate('/register')} style={{ marginLeft: '10px', background: '#6b7280' }}>
            Yeni Hesap
          </Button>
        </>
      )}
    </Container>
  );
};

export default VerifyEmail;
