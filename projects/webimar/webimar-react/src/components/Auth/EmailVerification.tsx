import React, { useState } from 'react';
import styled from 'styled-components';
import { emailService } from '../../services/emailService';

const EmailVerificationCard = styled.div`
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
  text-align: center;
`;

const Title = styled.h3`
  color: #495057;
  margin-bottom: 15px;
`;

const Description = styled.p`
  color: #6c757d;
  margin-bottom: 20px;
  line-height: 1.5;
`;

const Button = styled.button`
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  
  &:hover {
    background: #0056b3;
  }
  
  &:disabled {
    background: #6c757d;
    cursor: not-allowed;
  }
`;

const Message = styled.div`
  margin-top: 15px;
  padding: 10px;
  border-radius: 4px;
  
  &.success {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
  }
  
  &.error {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
  }
`;

const SkipButton = styled.button`
  background: transparent;
  color: #6c757d;
  border: 1px solid #dee2e6;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-left: 10px;
  
  &:hover {
    background: #f8f9fa;
  }
`;

const Input = styled.input`
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  margin-bottom: 15px;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

interface EmailVerificationProps {
  userEmail?: string;
  onSkip?: () => void;
  onVerified?: () => void;
}

const EmailVerification: React.FC<EmailVerificationProps> = ({ 
  userEmail = '', 
  onSkip, 
  onVerified 
}) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [emailSent, setEmailSent] = useState(false);
  const [email, setEmail] = useState(userEmail);

  const handleSendVerification = async () => {
    if (!email.trim()) {
      setMessage({ type: 'error', text: 'Lütfen geçerli bir email adresi girin' });
      return;
    }
    
    setLoading(true);
    setMessage(null);
    
    try {
      const response = await emailService.sendVerificationEmail(email);
      
      if (response.success) {
        setEmailSent(true);
        setMessage({
          type: 'success',
          text: 'Doğrulama maili gönderildi! Email adresinizi kontrol edin.'
        });
      } else {
        setMessage({
          type: 'error',
          text: response.message || 'Mail gönderilemedi'
        });
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: 'Bir hata oluştu. Lütfen tekrar deneyin.'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <EmailVerificationCard>
      <Title>📧 Email Doğrulama</Title>
      
      {!emailSent ? (
        <>
          <Description>
            Hesabınızı güvenli tutmak için email adresinizi doğrulamanızı öneririz.
          </Description>
          
          <Input 
            type="email" 
            value={email} 
            onChange={(e) => setEmail(e.target.value)} 
            placeholder="Email adresinizi girin"
          />
          
          <Button 
            onClick={handleSendVerification}
            disabled={loading || !email.trim()}
          >
            {loading ? 'Gönderiliyor...' : 'Doğrulama Maili Gönder'}
          </Button>
          
          {onSkip && (
            <SkipButton onClick={onSkip}>
              Daha Sonra
            </SkipButton>
          )}
        </>
      ) : (
        <>
          <Description>
            ✅ Doğrulama maili <strong>{email}</strong> adresine gönderildi!
            <br />
            Email'inizdeki linke tıklayarak hesabınızı aktifleştirin.
          </Description>
          
          <Button onClick={handleSendVerification} disabled={loading}>
            {loading ? 'Gönderiliyor...' : 'Tekrar Gönder'}
          </Button>
          
          {onSkip && (
            <SkipButton onClick={onSkip}>
              Daha Sonra Doğrula
            </SkipButton>
          )}
        </>
      )}
      
      {message && (
        <Message className={message.type}>
          {message.text}
        </Message>
      )}
    </EmailVerificationCard>
  );
};

export default EmailVerification;
