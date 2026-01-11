import React from 'react';
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
  margin-bottom: 8px;
  color: #374151;
`;

const InfoText = styled.p`
  text-align: center;
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 16px;
  
  @media (max-width: 768px) {
    font-size: 15px;
  }
`;

const LoginForm: React.FC<{ onLogin?: () => void }> = ({ onLogin }) => {
  return (
    <FormContainer>
      <Title>Giriş Yap</Title>
      <InfoText>
        Google hesabınızla güvenli bir şekilde giriş yapın.
      </InfoText>
      <GoogleLoginButton />
    </FormContainer>
  );
};

export default LoginForm;
