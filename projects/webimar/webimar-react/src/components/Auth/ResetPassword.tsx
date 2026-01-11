import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, useParams } from 'react-router-dom';
import styled from 'styled-components';
import { emailService } from '../../services/emailService';

const Container = styled.div`
  max-width: 400px;
  margin: 100px auto;
  padding: 30px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
`;

const Title = styled.h2`
  color: #333;
  margin-bottom: 30px;
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
  text-align: left;
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
  
  &.loading {
    background: #fff3cd;
    color: #856404;
    border: 1px solid #ffeaa7;
  }
`;

const ResetPassword: React.FC = () => {
  const [searchParams] = useSearchParams();
  const params = useParams<{ uid?: string; token?: string }>();
  const navigate = useNavigate();
  
  // URL parametrelerinden veya query string'den uid ve token'ı al
  const uid = params.uid || searchParams.get('uid');
  const token = params.token || searchParams.get('token');
  
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(true);
  const [isValidLink, setIsValidLink] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'loading', text: string } | null>(null);

  useEffect(() => {
    // Link geçerliliğini kontrol et
    const verifyLink = async () => {
      if (!uid || !token) {
        setMessage({
          type: 'error',
          text: 'Geçersiz şifre sıfırlama linki'
        });
        setVerifying(false);
        return;
      }

      // Burada token geçerliliğini kontrol edebiliriz
      // Şimdilik sadece parametrelerin var olduğunu kontrol ediyoruz
      setIsValidLink(true);
      setVerifying(false);
    };

    verifyLink();
  }, [uid, token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newPassword || !confirmPassword) {
      setMessage({
        type: 'error',
        text: 'Tüm alanları doldurun'
      });
      return;
    }

    if (newPassword !== confirmPassword) {
      setMessage({
        type: 'error',
        text: 'Şifreler eşleşmiyor'
      });
      return;
    }

    // Yeni şifre kuralları: En az 4 karakter (tüm karakterler kabul edilir)
    if (newPassword.length < 4) {
      setMessage({
        type: 'error',
        text: 'Şifre en az 4 karakter olmalıdır'
      });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const response = await emailService.resetPassword(uid!, token!, newPassword);
      
      if (response.success) {
        setMessage({
          type: 'success',
          text: 'Şifreniz başarıyla değiştirildi! Giriş sayfasına yönlendiriliyorsunuz...'
        });
        
        // 3 saniye sonra login sayfasına yönlendir
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      } else {
        setMessage({
          type: 'error',
          text: response.message
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

  if (verifying) {
    return (
      <Container>
        <Title>🔄 Doğrulanıyor...</Title>
        <Message className="loading">
          Şifre sıfırlama linki kontrol ediliyor...
        </Message>
      </Container>
    );
  }

  if (!isValidLink) {
    return (
      <Container>
        <Title>❌ Geçersiz Link</Title>
        <Message className="error">
          Bu şifre sıfırlama linki geçersiz veya süresi dolmuş.
          <br />
          Lütfen yeni bir şifre sıfırlama talebinde bulunun.
        </Message>
        <Button onClick={() => navigate('/forgot-password')} style={{ marginTop: '20px' }}>
          Yeni Şifre Sıfırlama Talebi
        </Button>
      </Container>
    );
  }

  return (
    <Container>
      <Title>🔑 Yeni Şifre Belirle</Title>
      
      <form onSubmit={handleSubmit}>
        <FormGroup>
          <Label htmlFor="newPassword">Yeni Şifre</Label>
          <Input
            type="password"
            id="newPassword"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="En az 4 karakter"
            required
          />
        </FormGroup>
        
        <FormGroup>
          <Label htmlFor="confirmPassword">Şifre Tekrar</Label>
          <Input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Şifrenizi tekrar girin"
            required
          />
        </FormGroup>
        
        <Button type="submit" disabled={loading}>
          {loading ? 'Değiştiriliyor...' : 'Şifreyi Değiştir'}
        </Button>
      </form>
      
      {message && (
        <Message className={message.type}>
          {message.text}
        </Message>
      )}
    </Container>
  );
};

export default ResetPassword;
