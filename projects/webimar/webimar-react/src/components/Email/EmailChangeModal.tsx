import React, { useState } from 'react';
import styled from 'styled-components';
import { useToast } from '../../hooks/useToast';
import { tokenStorage } from '../../utils/tokenStorage';
import { API_BASE_URL } from '../../services/api';

interface EmailChangeModalProps {
  onClose: () => void;
  currentEmail: string;
}

const ModalOverlay = styled.div`
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.18);
  z-index: 1001;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
`;

const ModalContent = styled.div`
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.13);
  padding: 32px 24px;
  max-width: 500px;
  width: 100%;
  position: relative;
`;

const CloseButton = styled.button`
  position: absolute;
  top: 10px;
  right: 16px;
  background: none;
  border: none;
  font-size: 22px;
  color: #888;
  cursor: pointer;
`;

const Title = styled.h2`
  margin: 0 0 20px 0;
  color: #333;
  font-size: 20px;
`;

const FormGroup = styled.div`
  margin-bottom: 16px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #333;
`;

const Input = styled.input`
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 15px;
  width: 100%;
  box-sizing: border-box;
  &:focus {
    outline: none;
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  }
`;

const Button = styled.button<{ $variant?: 'primary' | 'secondary' }>`
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  margin-right: 8px;
  transition: all 0.2s ease;
  
  ${props => props.$variant === 'primary' && `
    background: #2563eb;
    color: white;
    &:hover { background: #1d4ed8; }
    &:disabled { background: #94a3b8; cursor: not-allowed; }
  `}
  
  ${props => props.$variant === 'secondary' && `
    background: #f3f4f6;
    color: #374151;
    &:hover { background: #e5e7eb; }
  `}
`;

const InfoBox = styled.div`
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 16px;
  color: #92400e;
  font-size: 14px;
`;

const SuccessMessage = styled.div`
  color: #059669;
  background: #d1fae5;
  border: 1px solid #bbf7d0;
  border-radius: 6px;
  padding: 14px;
  margin-bottom: 16px;
  white-space: pre-line;
  line-height: 1.5;
  text-align: left;
  font-size: 14px;
`;

const ErrorMessage = styled.div`
  color: #dc2626;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 16px;
`;

const EmailChangeModal: React.FC<EmailChangeModalProps> = ({ onClose, currentEmail }) => {
  const { showSuccess, showError } = useToast();
  const [newEmail, setNewEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newEmail || !password) {
      setError('Lütfen tüm alanları doldurun.');
      return;
    }

    if (newEmail === currentEmail) {
      setError('Yeni e-posta adresi mevcut adresinizle aynı.');
      return;
    }

    // E-posta formatı kontrolü
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(newEmail)) {
      setError('Geçerli bir e-posta adresi girin.');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = tokenStorage.getAccessToken();
      // API_BASE_URL imported from services/api
      
      const response = await fetch(`${API_BASE_URL}/accounts/request-email-change/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          new_email: newEmail,
          password: password
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess('✅ E-posta değişiklik talebi başarıyla gönderildi!\n\n📧 Yeni e-posta adresinize doğrulama linki gönderildi.\n⏳ Admin onayı sonrasında değişiklik tamamlanacaktır.\n📋 İşlem durumunu e-posta ile takip edebilirsiniz.');
        showSuccess('E-posta değişiklik talebi gönderildi! Admin onayı bekleniyor.');
        
        // 3 saniye sonra modal'ı kapat
        setTimeout(() => {
          onClose();
        }, 3000);
      } else {
        setError(data.detail || 'E-posta değişikliği talebi gönderilemedi.');
        showError(data.detail || 'E-posta değişikliği talebi gönderilemedi.');
      }
    } catch (error) {
      setError('Bağlantı hatası. Lütfen tekrar deneyin.');
      showError('Bağlantı hatası. Lütfen tekrar deneyin.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ModalOverlay onClick={onClose}>
      <ModalContent onClick={e => e.stopPropagation()}>
        <CloseButton onClick={onClose}>&times;</CloseButton>
        <Title>E-posta Adresi Değiştir</Title>
        
        <InfoBox>
          🔒 Güvenlik nedeniyle e-posta değişikliği için şifre doğrulaması gereklidir. 
          Yeni e-posta adresinize doğrulama linki gönderilecektir.
        </InfoBox>

        {success && <SuccessMessage>{success}</SuccessMessage>}
        {error && <ErrorMessage>{error}</ErrorMessage>}

        <form onSubmit={handleSubmit}>
          <FormGroup>
            <Label>Mevcut E-posta:</Label>
            <Input
              type="email"
              value={currentEmail}
              disabled
              style={{ background: '#f9fafb', color: '#6b7280' }}
            />
          </FormGroup>

          <FormGroup>
            <Label htmlFor="newEmail">Yeni E-posta Adresi:</Label>
            <Input
              id="newEmail"
              type="email"
              value={newEmail}
              onChange={(e) => setNewEmail(e.target.value)}
              placeholder="yeni@email.com"
              disabled={loading}
              required
            />
          </FormGroup>

          <FormGroup>
            <Label htmlFor="password">Mevcut Şifreniz:</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Şifrenizi girin"
              disabled={loading}
              required
            />
          </FormGroup>

          <Button 
            type="submit" 
            $variant="primary" 
            disabled={loading}
          >
            {loading ? 'Gönderiliyor...' : 'E-posta Değişikliği Talep Et'}
          </Button>
          
          <Button 
            type="button" 
            $variant="secondary" 
            onClick={onClose}
            disabled={loading}
          >
            İptal
          </Button>
        </form>
      </ModalContent>
    </ModalOverlay>
  );
};

export default EmailChangeModal;
