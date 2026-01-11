import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useAuth } from './AuthContext';
import AppLayout from '../components/AppLayout';
import { useToast } from '../hooks/useToast';
import { tokenStorage } from '../utils/tokenStorage';
import { navigateToNextJs } from '../utils/environment';
import EmailChangeForm from '../components/Email/EmailChangeForm';
import CalculationHistoryList from '../components/CalculationHistoryList';

const Container = styled.div`
  max-width: 600px;
  margin: 0 auto;
  padding: 24px;
`;

const Card = styled.div`
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 32px;
  margin-bottom: 24px;
`;

const Title = styled.h1`
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 24px;
`;

const Section = styled.div`
  margin-bottom: 24px;
`;

const SectionTitle = styled.h2`
  font-size: 18px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 16px;
`;

const FormGroup = styled.div`
  margin-bottom: 16px;
`;

const Label = styled.label`
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 4px;
`;

const Input = styled.input`
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  &:focus {
    outline: none;
    border-color: #059669;
    box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.1);
  }
`;

const Button = styled.button<{ $variant?: 'primary' | 'secondary' }>`
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  ${props => props.$variant === 'secondary' ? `
    background: #f3f4f6;
    color: #374151;
    border: 1px solid #d1d5db;
    &:hover {
      background: #e5e7eb;
    }
  ` : `
    background: #059669;
    color: white;
    border: none;
    &:hover {
      background: #047857;
    }
    &:disabled {
      background: #9ca3af;
      cursor: not-allowed;
    }
  `}
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  
  @media (max-width: 640px) {
    grid-template-columns: 1fr;
  }
`;

const InfoItem = styled.div`
  padding: 12px;
  background: #f9fafb;
  border-radius: 6px;
`;

const InfoLabel = styled.div`
  font-size: 12px;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
`;

const InfoValue = styled.div`
  font-size: 14px;
  color: #1f2937;
  font-weight: 500;
`;

const StatusBadge = styled.span<{ $verified?: boolean }>`
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  ${props => props.$verified ? `
    background: #dcfce7;
    color: #166534;
  ` : `
    background: #fee2e2;
    color: #991b1b;
  `}
`;

const ProfilePage: React.FC = () => {
  const { state: { user, isLoading, isAuthenticated }, checkAuthStatus } = useAuth();
  const { showSuccess, showError } = useToast();
  const [isEditing, setIsEditing] = useState(false);
  const [showCalculationHistory, setShowCalculationHistory] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
  const [editForm, setEditForm] = useState({
    username: user?.username || '',
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
  });

  const handleEdit = () => {
    setEditForm({
      username: user?.username || '',
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
    });
    setIsEditing(true);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditForm({
      username: user?.username || '',
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
    });
  };

  const handleSave = async () => {
    try {
      const token = tokenStorage.getAccessToken();
      if (!token) {
        showError('Oturum bilginiz bulunamadı');
        return;
      }

      const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
      const response = await fetch(`${API_BASE_URL}/accounts/me/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(editForm),
      });

      if (response.ok) {
        showSuccess('Profil bilgileriniz güncellendi');
        setIsEditing(false);
        // Cache'i yenile
        checkAuthStatus(true);
      } else {
        const errorData = await response.json();
        showError(errorData.detail || 'Güncelleme sırasında hata oluştu');
      }
    } catch (error) {
      showError('Sunucuya bağlanılamadı');
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Bilinmiyor';
    return new Date(dateString).toLocaleDateString('tr-TR');
  };

  if (isLoading) {
    return (
      <Container>
        <Card>
          <div style={{ textAlign: 'center', padding: '40px' }}>
            Yükleniyor...
          </div>
        </Card>
      </Container>
    );
  }

  if (!user) {
    return (
      <Container>
        <Card>
          <div style={{ textAlign: 'center', padding: '40px' }}>
            Kullanıcı bilgileri bulunamadı
          </div>
        </Card>
      </Container>
    );
  }

  // Admin onaylı sistemde hesap durumu
  const isAccountActive = !!user.is_active;

  return (
    <Container>
      <Card>
        <Title>Profilim</Title>

        <Section>
          <SectionTitle>Temel Bilgiler</SectionTitle>
          
          {isEditing ? (
            <>
              <FormGroup>
                <Label>Kullanıcı Adı</Label>
                <Input
                  value={editForm.username}
                  onChange={(e) => setEditForm({ ...editForm, username: e.target.value })}
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Ad</Label>
                <Input
                  value={editForm.first_name}
                  onChange={(e) => setEditForm({ ...editForm, first_name: e.target.value })}
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Soyad</Label>
                <Input
                  value={editForm.last_name}
                  onChange={(e) => setEditForm({ ...editForm, last_name: e.target.value })}
                />
              </FormGroup>
              
              <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
                <Button onClick={handleSave}>Kaydet</Button>
                <Button $variant="secondary" onClick={handleCancel}>İptal</Button>
              </div>
            </>
          ) : (
            <>
              <InfoGrid>
                <InfoItem>
                  <InfoLabel>Kullanıcı Adı</InfoLabel>
                  <InfoValue>{user.username}</InfoValue>
                </InfoItem>
                
                <InfoItem>
                  <InfoLabel>E-posta</InfoLabel>
                  <InfoValue>{user.email}</InfoValue>
                </InfoItem>
                
                <InfoItem>
                  <InfoLabel>Ad</InfoLabel>
                  <InfoValue>{user.first_name || 'Belirtilmemiş'}</InfoValue>
                </InfoItem>
                
                <InfoItem>
                  <InfoLabel>Soyad</InfoLabel>
                  <InfoValue>{user.last_name || 'Belirtilmemiş'}</InfoValue>
                </InfoItem>
              </InfoGrid>
              
              <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
                <Button onClick={handleEdit}>Düzenle</Button>
                <Button $variant="secondary" onClick={() => setShowCalculationHistory(true)}>
                  Geçmiş Hesaplamalar
                </Button>
                {/* Silme butonu artık sayfa altında, burada kaldırıldı */}
              </div>
            </>
          )}
        </Section>

        {/* Admin onaylı sisteme uyum: E-posta doğrulama kaldırıldı */}
        <Section>
          <SectionTitle>
            Hesap Durumu
            <span style={{ marginLeft: 8 }}>
              <StatusBadge $verified={isAccountActive}>
                {isAccountActive ? 'Aktif' : 'Pasif (Admin onayı bekliyor)'}
              </StatusBadge>
            </span>
          </SectionTitle>
          <p style={{ margin: 0, color: isAccountActive ? '#166534' : '#991b1b' }}>
            {isAccountActive
              ? 'Hesabınız admin tarafından onaylanmış ve aktiftir.'
              : 'Hesabınız admin onayı beklemektedir. Onaylanana kadar giriş yapılamaz.'}
          </p>
        </Section>

        <Section>
          <SectionTitle>E-posta Ayarları</SectionTitle>
          <p style={{ 
            marginTop: -8, 
            marginBottom: 12, 
            color: '#d97706', 
            fontSize: 14, 
            backgroundColor: '#fef3c7', 
            padding: '12px', 
            borderRadius: '6px',
            border: '1px solid #fbbf24'
          }}>
            <strong>⚠️ Önemli:</strong> E-posta değişikliği admin onayı gerektirir. 
            <br />• Yeni e-posta adresinize doğrulama linki gönderilir
            <br />• Admin tarafından onaylandıktan sonra değişiklik tamamlanır
            <br />• İşlem süresi 1-2 iş günü sürebilir
          </p>
          <EmailChangeForm currentEmail={user.email} />
        </Section>

        <Section>
          <SectionTitle>Hesap Bilgileri</SectionTitle>
          <InfoGrid>
            <InfoItem>
              <InfoLabel>Kayıt Tarihi</InfoLabel>
              <InfoValue>{formatDate(user.profile?.created_at)}</InfoValue>
            </InfoItem>
          </InfoGrid>
        </Section>

        {/* Tekrarlı EmailVerificationSection kaldırıldı */}
      </Card>
      
      {showCalculationHistory && (
        <CalculationHistoryList
          onClose={() => setShowCalculationHistory(false)}
          isModal={true}
        />
      )}

      {/* Sayfanın altına Hesabı Sil butonu ve onay kutusu - Sadece giriş yapmış kullanıcılar için */}
      {isAuthenticated && user && tokenStorage.getAccessToken() && (
        <div style={{ margin: '40px 0 0 0', textAlign: 'center' }}>
          {!showDeleteConfirm ? (
            <Button $variant="secondary" style={{ background: '#dc2626', color: 'white', minWidth: 160 }} onClick={() => setShowDeleteConfirm(true)}>
              Hesabı Sil
            </Button>
          ) : (
          <div style={{ marginTop: 16 }}>
            <div style={{ color: '#dc2626', marginBottom: 12, fontWeight: 500 }}>
              Emin misiniz? Bu işlem geri alınamaz ve hesabınız kalıcı olarak silinecek!
            </div>
            
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', marginBottom: 6, fontWeight: 500 }}>
                Mevcut Şifreniz
              </label>
              <Input
                type="password"
                value={deletePassword}
                onChange={(e) => setDeletePassword(e.target.value)}
                placeholder="Hesap silme işlemi için şifrenizi girin"
                style={{ marginBottom: 12 }}
              />
            </div>
            
            <Button $variant="secondary" style={{ background: '#dc2626', color: 'white', minWidth: 160 }} onClick={async () => {
              if (!deletePassword.trim()) {
                showError('Hesap silme işlemi için şifrenizi girmeniz gereklidir.');
                return;
              }
              
              // Token kontrolü
              const token = tokenStorage.getAccessToken();
              if (!token) {
                showError('Oturum süresi dolmuş. Lütfen tekrar giriş yapın.');
                return;
              }
              
              console.log('🔑 Delete account token:', token ? 'Mevcut' : 'Yok');
              
              // Silme işlemi
              try {
                const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
                const response = await fetch(`${API_BASE_URL}/accounts/me/delete-account/`, {
                  method: 'DELETE',
                  headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                  },
                  body: JSON.stringify({
                    password: deletePassword
                  }),
                });
                if (response.ok) {
                  showSuccess('Hesabınız başarıyla silindi.');
                  tokenStorage.clearAll();
                  navigateToNextJs('/');
                } else {
                  const data = await response.json();
                  showError(data.detail || 'Hesap silinirken bir hata oluştu.');
                }
              } catch (error) {
                showError('Bağlantı hatası. Lütfen tekrar deneyin.');
              }
            }}>
              Evet, Hesabı Sil
            </Button>
            <Button $variant="secondary" style={{ marginLeft: 12, minWidth: 120 }} onClick={() => setShowDeleteConfirm(false)}>
              İptal
            </Button>
          </div>
        )}
        </div>
      )}
    </Container>
  );
};

export default ProfilePage;
