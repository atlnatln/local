import React, { useEffect } from 'react';
import styled from 'styled-components';
import { useAuth } from './AuthContext';
import { useNavigate } from 'react-router-dom';
import LoginForm from './LoginForm';
import { navigateToNextJs } from '../utils/environment';

const LoginPageContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
  background: #f7f3f0 url('/backgrounds/girisyap-arka-fon.webp') center center/cover no-repeat;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
  /* SEO için alt metin <img> ile eklenmez, sadece dosya adı ve yol optimize edildi */
`;

const LoginCard = styled.div`
  background: rgba(255,255,255,0.2);
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  border: 2px solid #d2691e;
  backdrop-filter: blur(6px) saturate(120%);
`;

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const Title = styled.h1`
  text-align: center;
  color: #654321;
  font-family: 'Playfair Display', 'Georgia', serif;
  margin-bottom: 30px;
  font-size: 2rem;
`;

const LoginPage: React.FC = () => {
  const { state } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (state.isAuthenticated) {
      navigateToNextJs('/');
    }
  }, [state.isAuthenticated, navigate]);

  const handleRegisterClick = () => {
    navigate('/register');
  };

  return (
    <LoginPageContainer>
      <LoginCard>
        <LoginForm />
        <div style={{ textAlign: 'center', marginTop: 20 }}>
          <span>Hesabınız yok mu? </span>
          {/* eslint-disable-next-line jsx-a11y/anchor-is-valid */}
          <a onClick={handleRegisterClick} style={{ color: '#d2691e', fontWeight: 600, textDecoration: 'underline', cursor: 'pointer' }}>Kayıt Ol</a>
        </div>
      </LoginCard>
    </LoginPageContainer>
  );
};

export default LoginPage;
