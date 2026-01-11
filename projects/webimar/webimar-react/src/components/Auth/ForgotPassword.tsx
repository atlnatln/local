import React, { useState } from 'react';
import styled from 'styled-components';

interface ForgotPasswordProps {
  onClose?: () => void;
}

const ResetContainer = styled.div`
  padding: 30px;
  background: white;
  border-radius: 8px;
  position: relative;
`;

const Title = styled.h2`
  text-align: center;
  color: #333;
  margin-bottom: 30px;
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 5px;
  color: #555;
  font-weight: 500;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const Button = styled.button`
  width: 100%;
  padding: 12px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  
  &:hover {
    background: #0056b3;
  }
  
  &:disabled {
    background: #6c757d;
    cursor: not-allowed;
  }
`;

const Message = styled.div`
  margin-top: 20px;
  padding: 15px;
  border-radius: 4px;
  text-align: center;
  
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

const LinkButton = styled.button`
  background: none;
  border: none;
  color: #007bff;
  text-decoration: underline;
  cursor: pointer;
  font-size: 14px;
  margin-top: 20px;
  
  &:hover {
    color: #0056b3;
  }
`;

interface ForgotPasswordProps {
  onBackToLogin?: () => void;
}

const ForgotPassword: React.FC<ForgotPasswordProps> = ({ onClose }) => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [emailSent, setEmailSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email) {
      setMessage({
        type: 'error',
        text: 'Email adresi gerekli'
      });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      // Admin onaylı şifre sıfırlama endpoint'i kullan
      const response = await fetch('/api/accounts/password-reset-request/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setEmailSent(true);
        setMessage({
          type: 'success',
          text: data.detail || 'Şifre sıfırlama talebi alınmıştır. Admin onayından sonra yeni şifreniz e-posta ile gönderilecektir.'
        });
      } else {
        setMessage({
          type: 'error',
          text: data.detail || 'Bir hata oluştu.'
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
    <ResetContainer>
      <Title>🔑 Şifremi Unuttum</Title>
      
      <div style={{ 
        background: '#f8f9fa', 
        border: '1px solid #dee2e6', 
        borderRadius: '6px', 
        padding: '15px', 
        marginBottom: '20px',
        fontSize: '14px',
        color: '#6c757d'
      }}>
        <strong>📝 Admin Onaylı Şifre Sıfırlama</strong><br/>
        Şifre sıfırlama talebiniz admin onayına gönderilecektir. 
        Onay sonrasında yeni şifreniz e-posta ile gönderilecektir.
      </div>
      
      <div style={{ 
        background: '#fff3cd', 
        border: '1px solid #ffeaa7', 
        borderRadius: '6px', 
        padding: '12px', 
        marginBottom: '15px',
        fontSize: '13px',
        color: '#856404'
      }}>
        <strong>⚠️ Günlük Limit:</strong> Güvenlik amacıyla günde en fazla <strong>3 kez</strong> şifre sıfırlama talebi gönderebilirsiniz.
      </div>
      
      {!emailSent ? (
        <form onSubmit={handleSubmit}>
          <FormGroup>
            <Label htmlFor="email">Email Adresi</Label>
            <Input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="example@email.com"
              required
            />
          </FormGroup>
          
          <Button type="submit" disabled={loading}>
            {loading ? 'Gönderiliyor...' : 'Şifre Sıfırlama Talebi Gönder'}
          </Button>
        </form>
      ) : (
        <div style={{ textAlign: 'center' }}>
          <p>✅ Şifre sıfırlama talebi gönderildi!</p>
          <p>Admin onayından sonra yeni şifreniz e-posta ile gönderilecektir.</p>
          
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? 'Gönderiliyor...' : 'Tekrar Gönder'}
          </Button>
        </div>
      )}
      
      {message && (
        <Message className={message.type}>
          {message.text}
        </Message>
      )}
      
      {onClose && (
        <div style={{ textAlign: 'center' }}>
          <LinkButton onClick={onClose}>
            ← Geri dön
          </LinkButton>
        </div>
      )}
    </ResetContainer>
  );
};

export default ForgotPassword;
