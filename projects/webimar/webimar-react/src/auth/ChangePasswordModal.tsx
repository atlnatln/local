import React, { useState } from 'react';
import styled from 'styled-components';
import { useToast } from '../hooks/useToast';
import LoadingSpinner from '../components/LoadingSpinner';
import { validatePassword, validatePasswordConfirm } from './authValidation';
import { tokenStorage } from '../utils/tokenStorage';

interface ChangePasswordModalProps {
  onClose: () => void;
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
  box-sizing: border-box;
  
  @media (max-width: 768px) {
    align-items: flex-start;
    padding: 8px;
    padding-top: 60px;
  }
`;

const ModalContent = styled.div`
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.13);
  padding: 32px 24px 24px 24px;
  min-width: 400px;
  max-width: 95vw;
  position: relative;
  width: 100%;
  max-width: 500px;
  
  @media (max-width: 768px) {
    min-width: unset;
    max-width: 100%;
    border-radius: 8px;
    padding: 24px 16px 16px 16px;
    margin: 0 auto;
  }
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
  z-index: 1;
  
  @media (max-width: 768px) {
    top: 8px;
    right: 12px;
    font-size: 24px;
    padding: 4px;
    &:hover {
      background: rgba(0,0,0,0.1);
      border-radius: 50%;
    }
  }
`;

const FormGroup = styled.div`
  margin-bottom: 16px;
  
  @media (max-width: 768px) {
    margin-bottom: 14px;
  }
`;

const Label = styled.label`
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #333;
  
  @media (max-width: 768px) {
    font-size: 14px;
    margin-bottom: 4px;
  }
`;

const Input = styled.input<{ $hasError?: boolean }>`
  padding: 10px 12px;
  border: 1px solid ${props => props.$hasError ? '#dc2626' : '#e5e7eb'};
  border-radius: 6px;
  font-size: 15px;
  width: 100%;
  background-color: ${props => props.$hasError ? '#fef2f2' : '#ffffff'};
  box-sizing: border-box;
  &:focus {
    outline: none;
    border-color: ${props => props.$hasError ? '#dc2626' : '#2563eb'};
    box-shadow: 0 0 0 3px ${props => props.$hasError ? 'rgba(220, 38, 38, 0.1)' : 'rgba(37, 99, 235, 0.1)'};
  }
  
  @media (max-width: 768px) {
    padding: 12px 14px;
    font-size: 16px;
    border-radius: 8px;
  }
`;

const Button = styled.button`
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 12px 0;
  font-size: 16px;
  font-weight: 500;
  width: 100%;
  cursor: pointer;
  &:hover {
    background: #1d4ed8;
  }
  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
  
  @media (max-width: 768px) {
    padding: 14px 0;
    font-size: 17px;
    border-radius: 8px;
  }
`;

const ErrorMsg = styled.div`
  color: #dc2626;
  font-size: 14px;
  text-align: center;
  margin-bottom: 8px;
  padding: 8px 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  
  @media (max-width: 768px) {
    font-size: 15px;
    padding: 10px 14px;
    border-radius: 8px;
  }
`;

const SuccessMsg = styled.div`
  color: #059669;
  font-size: 14px;
  text-align: center;
  margin-bottom: 8px;
  padding: 8px 12px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 6px;
`;

const FieldError = styled.div`
  color: #dc2626;
  font-size: 12px;
  margin-top: 4px;
`;

const LoadingOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
`;

const ChangePasswordModal: React.FC<ChangePasswordModalProps> = ({ onClose }) => {
  const { showSuccess, showError } = useToast();
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [fieldErrors, setFieldErrors] = useState<{[key: string]: string}>({});

  // Real-time validation
  const validateFieldInRealTime = (field: string, value: string) => {
    let validation: { isValid: boolean; error?: string } = { isValid: true };
    
    switch (field) {
      case 'oldPassword':
        validation = validatePassword(value);
        break;
      case 'newPassword':
        validation = validatePassword(value);
        break;
      case 'confirmPassword':
        validation = validatePasswordConfirm(newPassword, value);
        break;
      default:
        validation = { isValid: true };
    }
    
    setFieldErrors(prev => ({
      ...prev,
      [field]: validation.isValid ? '' : (validation.error || '')
    }));
    
    return validation.isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Form validasyonu
    const oldPasswordValid = validateFieldInRealTime('oldPassword', oldPassword);
    const newPasswordValid = validateFieldInRealTime('newPassword', newPassword);
    const confirmPasswordValid = validateFieldInRealTime('confirmPassword', confirmPassword);

    if (!oldPasswordValid || !newPasswordValid || !confirmPasswordValid) {
      showError('Lütfen form hatalarını düzeltin.');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = tokenStorage.getAccessToken();
      if (!token) {
        showError('Oturum süreniz dolmuş. Lütfen tekrar giriş yapın.');
        return;
      }

      const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
      const response = await fetch(`${API_BASE_URL}/accounts/change-password/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          old_password: oldPassword,
          new_password: newPassword,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess('Şifreniz başarıyla değiştirildi!');
        showSuccess('Şifreniz başarıyla değiştirildi!');
        
        // Formu temizle
        setOldPassword('');
        setNewPassword('');
        setConfirmPassword('');
        setFieldErrors({});
        
        setTimeout(() => {
          onClose();
        }, 1500);
      } else {
        // Backend'den dönen hata mesajı şifre kuralı ile ilgiliyse kullanıcıya açıkça göster
        let errorMessage = data.detail || 'Şifre değiştirme başarısız.';
        if (errorMessage.toLowerCase().includes('password')) {
          errorMessage = 'Şifre en az 4 karakter olmalıdır. Güvenli bir şifre seçin.';
        }
        setError(errorMessage);
        showError(errorMessage);
      }
    } catch (error) {
      const errorMsg = 'Sunucuya bağlanılamadı. İnternet bağlantınızı kontrol edin.';
      setError(errorMsg);
      showError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ModalOverlay onClick={onClose}>
      <ModalContent onClick={e => e.stopPropagation()}>
        {loading && (
          <LoadingOverlay>
            <LoadingSpinner text="Şifre değiştiriliyor..." />
          </LoadingOverlay>
        )}
        
        <CloseButton onClick={onClose} title="Kapat">×</CloseButton>
        
        <h2 style={{textAlign:'center', marginBottom: 24}}>Şifre Değiştir</h2>
        
        <form onSubmit={handleSubmit}>
          <FormGroup>
            <Label>Mevcut Şifre</Label>
            <Input
              type="password"
              value={oldPassword}
              onChange={e => {
                setOldPassword(e.target.value);
                validateFieldInRealTime('oldPassword', e.target.value);
              }}
              $hasError={!!fieldErrors.oldPassword}
              placeholder="Mevcut şifrenizi girin"
              required
            />
            {fieldErrors.oldPassword && <FieldError>{fieldErrors.oldPassword}</FieldError>}
          </FormGroup>

          <FormGroup>
            <Label>Yeni Şifre</Label>
            <Input
              type="password"
              value={newPassword}
              onChange={e => {
                setNewPassword(e.target.value);
                validateFieldInRealTime('newPassword', e.target.value);
                // Confirm password'u da kontrol et
                if (confirmPassword) {
                  validateFieldInRealTime('confirmPassword', confirmPassword);
                }
              }}
              $hasError={!!fieldErrors.newPassword}
              placeholder="Yeni şifrenizi girin"
              required
            />
            {fieldErrors.newPassword && <FieldError>{fieldErrors.newPassword}</FieldError>}
            <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
              Şifre en az 4 karakter olmalıdır.
            </div>
          </FormGroup>

          <FormGroup>
            <Label>Yeni Şifre Tekrar</Label>
            <Input
              type="password"
              value={confirmPassword}
              onChange={e => {
                setConfirmPassword(e.target.value);
                validateFieldInRealTime('confirmPassword', e.target.value);
              }}
              $hasError={!!fieldErrors.confirmPassword}
              placeholder="Yeni şifrenizi tekrar girin"
              required
            />
            {fieldErrors.confirmPassword && <FieldError>{fieldErrors.confirmPassword}</FieldError>}
          </FormGroup>

          {error && <ErrorMsg>{error}</ErrorMsg>}
          {success && <SuccessMsg>{success}</SuccessMsg>}
          
          <Button type="submit" disabled={loading}>
            {loading ? 'Değiştiriliyor...' : 'Şifre Değiştir'}
          </Button>
        </form>
      </ModalContent>
    </ModalOverlay>
  );
};

export default ChangePasswordModal;
