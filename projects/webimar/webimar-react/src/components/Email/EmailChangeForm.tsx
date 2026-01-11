import React, { useState } from 'react';
import styled from 'styled-components';
import { useToast } from '../../hooks/useToast';
import { tokenStorage } from '../../utils/tokenStorage';
import { API_BASE_URL } from '../../services/api';

const FormContainer = styled.form`
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  padding: 24px 20px;
  max-width: 350px;
  margin: 0 auto;
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
  font-size: 15px;
  background-color: ${props => props.$hasError ? '#fef2f2' : '#ffffff'};
  box-sizing: border-box;
  &:focus {
    outline: none;
    border-color: ${props => props.$hasError ? '#dc2626' : '#059669'};
    box-shadow: 0 0 0 3px ${props => props.$hasError ? 'rgba(220, 38, 38, 0.1)' : 'rgba(5, 150, 105, 0.1)'};
  }
`;

const Button = styled.button`
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 10px 0;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  &:hover { background: #1d4ed8; }
`;

const SuccessMsg = styled.div`
  color: #059669;
  background: #d1fae5;
  border: 1px solid #bbf7d0;
  border-radius: 6px;
  padding: 14px;
  margin-bottom: 12px;
  text-align: left;
  white-space: pre-line;
  line-height: 1.5;
  font-size: 14px;
`;

const ErrorMsg = styled.div`
  color: #dc2626;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  padding: 10px;
  margin-bottom: 12px;
  text-align: center;
`;

const EmailChangeForm: React.FC<{ currentEmail: string }> = ({ currentEmail }) => {
  const { showSuccess, showError } = useToast();
  const [newEmail, setNewEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!newEmail || !password) {
      setError('Yeni e-posta ve mevcut şifre gereklidir.');
      return;
    }
    setLoading(true);
    try {
      const token = tokenStorage.getAccessToken();
      // API_BASE_URL imported from services/api
      const response = await fetch(`${API_BASE_URL}/accounts/request-email-change/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ new_email: newEmail, password }),
      });
      const data = await response.json();
      if (response.ok) {
        setSuccess('✅ E-posta değişiklik talebi başarıyla gönderildi!\n\n📧 Yeni e-posta adresinize doğrulama linki gönderildi.\n⏳ Admin onayı sonrasında değişiklik tamamlanacaktır.\n📋 İşlem durumunu e-posta ile takip edebilirsiniz.');
        showSuccess('E-posta değişiklik talebi gönderildi! Admin onayı bekleniyor.');
        setNewEmail('');
        setPassword('');
      } else {
        setError(data.detail || 'E-posta değişikliği sırasında hata oluştu.');
        showError(data.detail || 'E-posta değişikliği sırasında hata oluştu.');
      }
    } catch (err) {
      setError('Bağlantı hatası. Lütfen tekrar deneyin.');
      showError('Bağlantı hatası. Lütfen tekrar deneyin.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <FormContainer onSubmit={handleSubmit}>
      <Label>Mevcut E-posta: <b>{currentEmail}</b></Label>
      <Label htmlFor="newEmail">Yeni E-posta Adresi</Label>
      <Input
        id="newEmail"
        type="email"
        value={newEmail}
        onChange={e => setNewEmail(e.target.value)}
        placeholder="yeni@email.com"
        required
      />
      <Label htmlFor="password">Mevcut Şifre</Label>
      <Input
        id="password"
        type="password"
        value={password}
        onChange={e => setPassword(e.target.value)}
        placeholder="Şifreniz"
        required
      />
      {error && <ErrorMsg>{error}</ErrorMsg>}
      {success && <SuccessMsg>{success}</SuccessMsg>}
      <Button type="submit" disabled={loading}>{loading ? 'Gönderiliyor...' : 'E-posta Değiştir'}</Button>
    </FormContainer>
  );
};

export default EmailChangeForm;
