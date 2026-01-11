import React, { useState } from 'react';
import styled from 'styled-components';
import { emailService } from '../../services/emailService';
import { useToast } from '../../hooks/useToast';

const Container = styled.div`
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
  margin-top: 16px;
`;

const Title = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 16px;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
`;

const Label = styled.label`
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 4px;
`;

const Input = styled.input<{ $hasError?: boolean }>`
  padding: 10px 12px;
  border: 1px solid ${props => props.$hasError ? '#dc2626' : '#e5e7eb'};
  border-radius: 6px;
  font-size: 14px;
  background-color: ${props => props.$hasError ? '#fef2f2' : '#ffffff'};
  
  &:focus {
    outline: none;
    border-color: ${props => props.$hasError ? '#dc2626' : '#059669'};
    box-shadow: 0 0 0 3px ${props => props.$hasError ? 'rgba(220, 38, 38, 0.1)' : 'rgba(5, 150, 105, 0.1)'};
  }
`;

const Button = styled.button`
  background: #059669;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  
  &:hover {
    background: #047857;
  }
  
  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.div`
  color: #dc2626;
  font-size: 12px;
  margin-top: 4px;
`;

const SuccessMessage = styled.div`
  color: #059669;
  font-size: 14px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 6px;
  padding: 12px;
  margin-top: 16px;
`;

const InfoText = styled.div`
  font-size: 13px;
  color: #6b7280;
  background: #f9fafb;
  border-radius: 4px;
  padding: 12px;
  margin-bottom: 16px;
`;

interface EmailChangeProps {
  currentEmail: string;
}

const EmailChange: React.FC<EmailChangeProps> = ({ currentEmail }) => {
  const [newEmail, setNewEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [errors, setErrors] = useState<{[key: string]: string}>({});
  const { showSuccess, showError } = useToast();

  const validateForm = () => {
    const newErrors: {[key: string]: string} = {};
    
    if (!newEmail) {
      newErrors.newEmail = 'Yeni e-posta adresi gereklidir';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newEmail)) {
      newErrors.newEmail = 'Geçerli bir e-posta adresi girin';
    } else if (newEmail === currentEmail) {
      newErrors.newEmail = 'Yeni e-posta adresi mevcut adresinizle aynı olamaz';
    }
    
    if (!password) {
      newErrors.password = 'Mevcut şifreniz gereklidir';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    setSuccess('');
    setErrors({});
    
    try {
      const response = await emailService.requestEmailChange(newEmail.trim(), password);
      
      if (response.success) {
        setSuccess(response.message || 'E-posta değişikliği talebi gönderildi. Yeni e-posta adresinizi kontrol edin.');
        setNewEmail('');
        setPassword('');
        showSuccess('E-posta değişikliği talebi gönderildi!');
      } else {
        showError(response.message || 'E-posta değişikliği sırasında hata oluştu');
      }
    } catch (error: any) {
      showError('Ağ hatası oluştu. Lütfen tekrar deneyin.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <Title>E-posta Adresi Değiştir</Title>
      
      <InfoText>
        🔒 Güvenliğiniz için e-posta değişikliği doğrulama gerektirir. Yeni e-posta adresinize 
        doğrulama linki gönderilecek ve mevcut e-posta adresinize bilgilendirme yapılacaktır.
      </InfoText>
      
      <Form onSubmit={handleSubmit}>
        <FormGroup>
          <Label htmlFor="currentEmail">Mevcut E-posta</Label>
          <Input
            id="currentEmail"
            type="email"
            value={currentEmail}
            disabled
            style={{ background: '#f3f4f6', color: '#6b7280' }}
          />
        </FormGroup>
        
        <FormGroup>
          <Label htmlFor="newEmail">Yeni E-posta Adresi</Label>
          <Input
            id="newEmail"
            type="email"
            value={newEmail}
            onChange={(e) => setNewEmail(e.target.value)}
            $hasError={!!errors.newEmail}
            placeholder="yeni@email.com"
            disabled={loading}
          />
          {errors.newEmail && <ErrorMessage>{errors.newEmail}</ErrorMessage>}
        </FormGroup>
        
        <FormGroup>
          <Label htmlFor="password">Mevcut Şifreniz</Label>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            $hasError={!!errors.password}
            placeholder="Mevcut şifrenizi girin"
            disabled={loading}
          />
          {errors.password && <ErrorMessage>{errors.password}</ErrorMessage>}
        </FormGroup>
        
        <Button type="submit" disabled={loading}>
          {loading ? 'Gönderiliyor...' : 'E-posta Değişikliği Talep Et'}
        </Button>
      </Form>
      
      {success && (
        <SuccessMessage>
          {success}
        </SuccessMessage>
      )}
    </Container>
  );
};

export default EmailChange;
