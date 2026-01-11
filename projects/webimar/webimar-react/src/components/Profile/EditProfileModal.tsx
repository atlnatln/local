import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import ChangePasswordModal from '../../auth/ChangePasswordModal';
import UserSessionsModal from '../../auth/UserSessionsModal';
import CalculationHistoryList from '../CalculationHistoryList';
import EmailChangeModal from '../Email/EmailChangeModal';
import LoadingSpinner from '../LoadingSpinner';
import { useToast } from '../../hooks/useToast';
import { useUniqueValidation } from '../../hooks/useUniqueValidation';
import { validateUsername } from '../../utils/validation';
import { tokenStorage } from '../../utils/tokenStorage';
import { navigateToNextJs } from '../../utils/environment';

interface UserProfile {
  username: string;
  email: string;
  profile?: {
    created_at?: string;
    updated_at?: string;
  };
}

interface EditProfileModalProps {
  user: UserProfile;
  onClose: () => void;
  onProfileUpdate: (user: UserProfile) => void;
}

const ModalOverlay = styled.div`
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.18);
  z-index: 1000;
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
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  width: 100%;
  max-width: 600px;
  
  @media (max-width: 768px) {
    min-width: unset;
    max-width: 100%;
    border-radius: 8px;
    padding: 24px 16px 16px 16px;
    margin: 0 auto;
    max-height: 85vh;
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

const Title = styled.h2`
  margin: 0 0 20px 0;
  color: #333;
  font-size: 20px;
  
  @media (max-width: 768px) {
    font-size: 18px;
    margin: 0 0 16px 0;
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

const Button = styled.button<{ $variant?: 'primary' | 'secondary' | 'danger' }>`
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  margin-right: 8px;
  margin-bottom: 8px;
  transition: all 0.2s ease;
  
  @media (max-width: 768px) {
    padding: 12px 16px;
    font-size: 15px;
    margin-right: 6px;
    margin-bottom: 6px;
    border-radius: 8px;
    width: auto;
    min-width: 100px;
  }
  
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
  
  ${props => props.$variant === 'danger' && `
    background: #dc2626;
    color: white;
    &:hover { background: #b91c1c; }
  `}
`;

const FieldError = styled.div`
  color: #dc2626;
  font-size: 12px;
  margin-top: 4px;
  margin-bottom: 8px;
`;

const SuccessMessage = styled.div`
  color: #059669;
  font-size: 14px;
  padding: 8px 12px;
  background: #d1fae5;
  border: 1px solid #bbf7d0;
  border-radius: 6px;
  margin-bottom: 16px;
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

const DeleteSection = styled.div`
  border-top: 1px solid #e5e7eb;
  padding-top: 20px;
  margin-top: 20px;
`;

const DeleteWarning = styled.div`
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 16px;
  color: #dc2626;
  font-size: 14px;
`;

const EditProfileModal: React.FC<EditProfileModalProps> = ({ user, onClose, onProfileUpdate }) => {
  const { showSuccess, showError } = useToast();
  
  // State'leri tamamen boş başlat, user prop'una bağımlı olma
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [showChangePasswordModal, setShowChangePasswordModal] = useState(false);
  const [showSessionsModal, setShowSessionsModal] = useState(false);
  const [showCalculationHistoryModal, setShowCalculationHistoryModal] = useState(false);
  const [showEmailChangeModal, setShowEmailChangeModal] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
  const [fieldErrors, setFieldErrors] = useState<{[key: string]: string}>({});

  // Benzersizlik kontrolü hook'ları - tamamen boş referans
  const usernameValidation = useUniqueValidation(username, '/accounts/check-username/', 500, '');

  // Real-time validation functions
  const validateFieldInRealTime = (field: string, value: string) => {
    let validation: { isValid: boolean; error?: string } = { isValid: true };
    
    switch (field) {
      case 'username':
        validation = validateUsername(value);
        // Benzersizlik kontrolü
        if (validation.isValid) {
          if (usernameValidation.isChecking) {
            validation = { isValid: false, error: 'Kontrol ediliyor...' };
          } else if (usernameValidation.isUnique === false) {
            validation = { isValid: false, error: usernameValidation.error };
          }
        }
        break;
      default:
        break;
    }
    
    setFieldErrors(prev => ({
      ...prev,
      [field]: validation.error || ''
    }));
    
    return validation.isValid;
  };

  const handleUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setUsername(value);
    validateFieldInRealTime('username', value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validasyonları kontrol et
    const isUsernameValid = validateFieldInRealTime('username', username);
    
    if (!isUsernameValid) {
      showError('Lütfen kullanıcı adını doğru şekilde doldurun.');
      return;
    }

    // Benzersizlik kontrolü
    if (usernameValidation.isChecking) {
      showError('Lütfen kontroller tamamlanana kadar bekleyin.');
      return;
    }

    if (usernameValidation.isUnique === false) {
      showError('Bu kullanıcı adı zaten kullanılıyor.');
      return;
    }

    setLoading(true);
    setSuccess('');

    try {
      const token = tokenStorage.getAccessToken();
      const formData = new FormData();
      
      formData.append('username', username);

      const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
      const response = await fetch(`${API_BASE_URL}/accounts/me/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess('Profil başarıyla güncellendi!');
        showSuccess('Profil başarıyla güncellendi!');
        onProfileUpdate(data);
        setTimeout(() => {
          onClose();
        }, 1500);
      } else {
        if (data.username) {
          setFieldErrors(prev => ({ ...prev, username: data.username[0] }));
        }
        showError(data.detail || 'Profil güncellenirken bir hata oluştu.');
      }
    } catch (error) {
      showError('Bağlantı hatası. Lütfen tekrar deneyin.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!deletePassword) {
      showError('Hesap silmek için mevcut şifrenizi girin.');
      return;
    }

    // Token kontrolü
    const token = tokenStorage.getAccessToken();
    if (!token) {
      showError('Oturum süresi dolmuş. Lütfen tekrar giriş yapın.');
      return;
    }
    
    console.log('🔑 Delete account token:', token ? 'Mevcut' : 'Yok');

    setLoading(true);
    try {
      const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
      const response = await fetch(`${API_BASE_URL}/accounts/me/delete-account/`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ password: deletePassword }),
      });

      const data = await response.json();

      if (response.ok) {
        showSuccess('Hesabınız başarıyla silindi.');
        tokenStorage.clearAll();
        navigateToNextJs('/');
      } else {
        showError(data.detail || 'Hesap silinirken bir hata oluştu.');
      }
    } catch (error) {
      showError('Bağlantı hatası. Lütfen tekrar deneyin.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <ModalOverlay onClick={onClose}>
        <ModalContent onClick={e => e.stopPropagation()}>
          {loading && (
            <LoadingOverlay>
              <LoadingSpinner />
            </LoadingOverlay>
          )}
          
          <CloseButton onClick={onClose}>&times;</CloseButton>
          <Title>Profil Düzenle</Title>

          {success && <SuccessMessage>{success}</SuccessMessage>}

          <form onSubmit={handleSubmit}>
            <FormGroup>
              <Label htmlFor="username">Kullanıcı Adı *</Label>
              <Input
                id="username"
                type="text"
                value={username}
                onChange={handleUsernameChange}
                $hasError={!!fieldErrors.username}
                disabled={loading}
                required
              />
              {fieldErrors.username && <FieldError>{fieldErrors.username}</FieldError>}
            </FormGroup>

            <FormGroup>
              <Label>E-posta Adresi</Label>
              <Input
                type="email"
                value={user.email}
                disabled
                style={{ background: '#f9fafb', color: '#6b7280' }}
              />
              <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
                E-posta adresinizi değiştirmek için aşağıdaki butonu kullanın.
              </div>
            </FormGroup>

            <Button 
              type="submit" 
              $variant="primary" 
              disabled={loading || usernameValidation.isChecking}
            >
              {loading ? 'Güncelleniyor...' : 'Kullanıcı Adını Güncelle'}
            </Button>
          </form>

          <div style={{ marginTop: '20px', borderTop: '1px solid #e5e7eb', paddingTop: '20px' }}>
            <Button 
              $variant="secondary" 
              onClick={() => setShowEmailChangeModal(true)}
              disabled={loading}
            >
              E-posta Adresi Değiştir
            </Button>
            <Button 
              $variant="secondary" 
              onClick={() => setShowChangePasswordModal(true)}
              disabled={loading}
            >
              Şifre Değiştir
            </Button>
            
            <Button 
              $variant="secondary" 
              onClick={() => setShowSessionsModal(true)}
              disabled={loading}
            >
              Oturum Geçmişi
            </Button>
            
            <Button 
              $variant="secondary" 
              onClick={() => setShowCalculationHistoryModal(true)}
              disabled={loading}
            >
              Geçmiş Hesaplamalar
            </Button>
          </div>

          {/* Hesap Silme - Sadece token varsa göster */}
          {tokenStorage.getAccessToken() && (
            <DeleteSection>
              {/* <h3 style={{ color: '#dc2626', marginBottom: '12px' }}>Tehlikeli Alan</h3> */}
              
              {!showDeleteConfirm ? (
                <Button 
                  $variant="danger" 
                  onClick={() => setShowDeleteConfirm(true)}
                  disabled={loading}
                >
                  Hesabı Sil
                </Button>
              ) : (
              <>
                <DeleteWarning>
                  ⚠️ Bu işlem geri alınamaz! Hesabınız ve tüm verileriniz kalıcı olarak silinecektir.
                </DeleteWarning>
                
                <FormGroup>
                  <Label htmlFor="deletePassword">Şifrenizi onaylayın:</Label>
                  <Input
                    id="deletePassword"
                    type="password"
                    value={deletePassword}
                    onChange={(e) => setDeletePassword(e.target.value)}
                    placeholder="Hesap silme işlemi için şifrenizi girin"
                    disabled={loading}
                  />
                </FormGroup>
                
                <Button 
                  $variant="danger" 
                  onClick={handleDeleteAccount}
                  disabled={loading || !deletePassword}
                >
                  {loading ? 'Siliniyor...' : 'Hesabı Kalıcı Olarak Sil'}
                </Button>
                
                <Button 
                  $variant="secondary" 
                  onClick={() => {
                    setShowDeleteConfirm(false);
                    setDeletePassword('');
                  }}
                  disabled={loading}
                >
                  İptal
                </Button>
              </>
            )}
            </DeleteSection>
          )}
        </ModalContent>
      </ModalOverlay>

      {showEmailChangeModal && (
        <EmailChangeModal
          onClose={() => setShowEmailChangeModal(false)}
          currentEmail={user.email}
        />
      )}

      {showChangePasswordModal && (
        <ChangePasswordModal
          onClose={() => setShowChangePasswordModal(false)}
        />
      )}

      {showSessionsModal && (
        <UserSessionsModal
          onClose={() => setShowSessionsModal(false)}
        />
      )}

      {showCalculationHistoryModal && (
        <CalculationHistoryList
          onClose={() => setShowCalculationHistoryModal(false)}
          isModal={true}
        />
      )}
    </>
  );
};

export default EditProfileModal;
