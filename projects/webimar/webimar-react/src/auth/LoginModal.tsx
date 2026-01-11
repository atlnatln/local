import React, { useState } from 'react';
import { useIsMobile } from './useIsMobile';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';
import { tokenStorage } from '../utils/tokenStorage';

const ModalOverlay = styled.div`
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.18);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const ModalContent = styled.div`
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.13);
  padding: 0 0 16px 0;
  min-width: 340px;
  max-width: 95vw;
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

const LoginButton = styled.button`
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 8px 18px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
  &:hover { background: #1d4ed8; }
`;

const LoginModal: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(() => !!tokenStorage.getAccessToken());
  const navigate = useNavigate();

  const handleLogout = () => {
    tokenStorage.clearAll();
    setIsLoggedIn(false);
  };

  const handleLogin = () => {
    setOpen(false);
    setIsLoggedIn(true);
  };

  const handleAccount = () => {
    navigate('/account');
  };

  const isMobile = useIsMobile();
  return (
    <>
      {!isLoggedIn ? (
        <LoginButton onClick={() => { setOpen(true); setShowRegister(false); }}>Giriş Yap</LoginButton>
      ) : (
        <div style={{ display: 'flex', gap: 8 }}>
          <LoginButton as="button" style={{background:'#059669'}} onClick={handleAccount}>
            {isMobile ? 'Hesabım' : 'Hesabım'}
          </LoginButton>
          <LoginButton as="button" style={{background:'#dc2626'}} onClick={handleLogout}>
            {isMobile ? 'Çıkış' : 'Çıkış'}
          </LoginButton>
        </div>
      )}
      {open && (
        <ModalOverlay onClick={() => setOpen(false)}>
          <ModalContent onClick={e => e.stopPropagation()}>
            <CloseButton onClick={() => setOpen(false)} title="Kapat">×</CloseButton>
            {showRegister ? (
              <>
                <RegisterForm onSuccess={() => { setShowRegister(false); }} />
                <div style={{textAlign:'center',marginTop:12}}>
                  <span style={{fontSize:14}}>Zaten hesabınız var mı?{' '}
                    <button type="button" onClick={() => setShowRegister(false)} style={{color:'#2563eb',background:'none',border:'none',padding:0,textDecoration:'underline',cursor:'pointer'}}>Giriş Yap</button>
                  </span>
                </div>
              </>
            ) : (
              <>
                <LoginForm onLogin={handleLogin} />
                <div style={{textAlign:'center',marginTop:12}}>
                  <span style={{fontSize:14}}>Hesabınız yok mu?{' '}
                    <button type="button" onClick={() => setShowRegister(true)} style={{color:'#059669',background:'none',border:'none',padding:0,textDecoration:'underline',cursor:'pointer'}}>Kayıt Ol</button>
                  </span>
                </div>
              </>
            )}
          </ModalContent>
        </ModalOverlay>
      )}
    </>
  );
};

export default LoginModal;
