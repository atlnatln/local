import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { useAuth } from './AuthContext';
import { useNavigate } from 'react-router-dom';
import RegisterForm from './RegisterForm';
import { navigateToNextJs } from '../utils/environment';

const RegisterPageContainer = styled.div<{ $backgroundUrl: string }>`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
  background: #f7f3f0 url(${props => props.$backgroundUrl}) center center/cover no-repeat;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
  /* SEO için alt metin <img> ile eklenmez, sadece dosya adı ve yol optimize edildi */
`;

const RegisterCard = styled.div`
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

// Success Modal Styles
const SuccessModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
`;

const SuccessModalContent = styled.div`
  background: white;
  border-radius: 12px;
  padding: 30px;
  max-width: 500px;
  width: 100%;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  border: 2px solid #28a745;
`;

const SuccessIcon = styled.div`
  font-size: 4rem;
  color: #28a745;
  margin-bottom: 20px;
`;

const SuccessTitle = styled.h2`
  color: #28a745;
  margin-bottom: 15px;
  font-size: 1.5rem;
`;

const SuccessMessage = styled.p`
  color: #6b7280;
  margin-bottom: 25px;
  line-height: 1.6;
  font-size: 1rem;
`;

const SuccessButton = styled.button`
  background: #28a745;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  
  &:hover {
    background: #218838;
  }
`;

const RegisterPage: React.FC = () => {
  const { state } = useAuth();
  const navigate = useNavigate();
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const backgroundUrl = typeof window !== 'undefined'
    && window.location.pathname.startsWith('/hesaplama')
      ? '/hesaplama/backgrounds/girisyap-arka-fon.webp'
      : '/backgrounds/girisyap-arka-fon.webp';

  useEffect(() => {
    if (state.isAuthenticated) {
      navigateToNextJs('/');
    }
  }, [state.isAuthenticated, navigate]);

  const handleRegisterSuccess = () => {
    // Login sayfasına yönlendirmek yerine success modal göster
    setShowSuccessModal(true);
  };

  const handleCloseSuccessModal = () => {
    setShowSuccessModal(false);
    navigateToNextJs('/');  // Next.js ana sayfaya yönlendir
  };

  const handleLoginClick = () => {
    navigate('/login');
  };

  return (
    <>
      <RegisterPageContainer $backgroundUrl={backgroundUrl}>
        <RegisterCard>
          <RegisterForm onSuccess={handleRegisterSuccess} />
          <div style={{ textAlign: 'center', marginTop: 20 }}>
            <span>Zaten hesabınız var mı? </span>
            {/* eslint-disable-next-line jsx-a11y/anchor-is-valid */}
            <a onClick={handleLoginClick} style={{ color: '#d2691e', fontWeight: 600, textDecoration: 'underline', cursor: 'pointer' }}>Giriş Yap</a>
          </div>
        </RegisterCard>
      </RegisterPageContainer>

      {/* Success Modal */}
      {showSuccessModal && (
        <SuccessModalOverlay onClick={(e) => e.target === e.currentTarget && handleCloseSuccessModal()}>
          <SuccessModalContent>
            <SuccessIcon>✅</SuccessIcon>
            <SuccessTitle>Kayıt Talebiniz Alındı!</SuccessTitle>
            <SuccessMessage>
              Kayıt talebiniz admin onayına gönderildi. Admin onayından sonra hesabınız aktif edilecek 
              ve giriş bilgileriniz e-posta adresinize gönderilecektir.
              <br/><br/>
              <strong>Admin onayı sonrası giriş yapabileceksiniz.</strong>
            </SuccessMessage>
            <SuccessButton onClick={handleCloseSuccessModal}>
              Anladım
            </SuccessButton>
          </SuccessModalContent>
        </SuccessModalOverlay>
      )}
    </>
  );
};

export default RegisterPage;
