import React, { useState } from 'react';
import styled from 'styled-components';
import GoogleLoginButton from './GoogleLoginButton';

const FormContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  padding: 32px 24px;
  max-width: 350px;
  margin: 0 auto;
  
  @media (max-width: 768px) {
    padding: 24px 20px;
    gap: 14px;
    max-width: 100%;
    border-radius: 8px;
    box-shadow: none;
  }
`;

const Title = styled.h2`
  text-align: center;
  margin: 0 0 16px 0;
  color: #374151;
`;

const InfoText = styled.div`
  font-size: 14px;
  color: #6b7280;
  text-align: center;
  padding: 12px;
  background: #f9fafb;
  border-radius: 6px;
  margin-bottom: 8px;
  
  @media (max-width: 768px) {
    font-size: 15px;
    padding: 14px;
  }
`;

const CheckboxContainer = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 8px;
  font-size: 13px;
  color: #4b5563;
  line-height: 1.4;
`;

const Checkbox = styled.input`
  margin-top: 3px;
  cursor: pointer;
  width: 16px;
  height: 16px;
`;

const Link = styled.a`
  color: #2563eb;
  text-decoration: none;
  &:hover {
    text-decoration: underline;
  }
`;

const RegisterForm: React.FC<{ onSuccess?: () => void }> = ({ onSuccess }) => {
  const [isAgreed, setIsAgreed] = useState(false);

  return (
    <FormContainer>
      <Title>Yeni Hesap Oluştur</Title>
      
      <InfoText>
        <strong>🔐 Güvenli Kayıt</strong><br/>
        Google hesabınızla hızlı ve güvenli bir şekilde kayıt olun.
      </InfoText>

      <CheckboxContainer>
        <Checkbox 
          type="checkbox" 
          id="legal-consent" 
          checked={isAgreed} 
          onChange={(e) => setIsAgreed(e.target.checked)}
        />
        <label htmlFor="legal-consent">
          <Link href="/kullanim-kosullari" target="_blank" rel="noopener noreferrer">Kullanım Koşulları</Link>,{' '}
          <Link href="/gizlilik-politikasi" target="_blank" rel="noopener noreferrer">Gizlilik Politikası</Link> ve{' '}
          <Link href="/kvkk-aydinlatma" target="_blank" rel="noopener noreferrer">KVKK Aydınlatma Metni</Link>'ni okudum ve kabul ediyorum.
        </label>
      </CheckboxContainer>

      <GoogleLoginButton text="Google ile Kayıt Ol" disabled={!isAgreed} />
    </FormContainer>
  );
};

export default RegisterForm;
