import React, { useEffect } from 'react';
import styled from 'styled-components';
import { useAuth } from './AuthContext';
import { useNavigate } from 'react-router-dom';
import { navigateToNextJs } from '../utils/environment';

const LogoutPageContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  padding: 20px;
`;

const LogoutCard = styled.div`
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  border: 2px solid #d2691e;
  text-align: center;
`;

const Title = styled.h1`
  color: #654321;
  font-family: 'Playfair Display', 'Georgia', serif;
  margin-bottom: 20px;
  font-size: 2rem;
`;

const Message = styled.p`
  color: #666;
  margin-bottom: 30px;
  font-size: 1.1rem;
`;

const Button = styled.button`
  background: #d2691e;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s ease;

  &:hover {
    background: #b8860b;
  }
`;

const LogoutPage: React.FC = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // Sayfa yüklendiğinde otomatik logout yap
    logout();
  }, [logout]);

  const handleGoHome = () => {
    navigateToNextJs('/');
  };

  return (
    <LogoutPageContainer>
      <LogoutCard>
        <Title>Çıkış Yapıldı</Title>
        <Message>
          Başarıyla çıkış yaptınız.
        </Message>
        <Button onClick={handleGoHome}>
          Ana Sayfaya Dön
        </Button>
      </LogoutCard>
    </LogoutPageContainer>
  );
};

export default LogoutPage;
