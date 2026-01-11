import React, { useState } from 'react';
import styled from 'styled-components';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';

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
  padding: 0 0 16px 0;
  min-width: 340px;
  max-width: 95vw;
  position: relative;
  width: 100%;
  max-width: 480px;
  
  @media (max-width: 768px) {
    min-width: unset;
    max-width: 100%;
    border-radius: 8px;
    padding: 0 0 12px 0;
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

interface LoginModalWrapperProps {
  onClose: () => void;
  onLoginSuccess: () => void;
}

const LoginModalWrapper: React.FC<LoginModalWrapperProps> = ({ onClose, onLoginSuccess }) => {
  const [showRegister, setShowRegister] = useState(false);

  const handleLoginSuccess = () => {
    onLoginSuccess();
    onClose();
  };

  return (
    <ModalOverlay onClick={onClose}>
      <ModalContent onClick={e => e.stopPropagation()}>
        <CloseButton onClick={onClose} title="Kapat">×</CloseButton>
        {showRegister ? (
          <>
            <RegisterForm onSuccess={() => { setShowRegister(false); }} />
            <div style={{textAlign:'center',marginTop:12,padding:'0 8px'}}>
              <span style={{fontSize:14}}>Zaten hesabınız var mı?{' '}
                <button 
                  type="button" 
                  onClick={() => setShowRegister(false)} 
                  style={{
                    color:'#2563eb',
                    background:'none',
                    border:'none',
                    padding:'4px 8px',
                    textDecoration:'underline',
                    cursor:'pointer',
                    fontSize:'14px'
                  }}
                >
                  Giriş Yap
                </button>
              </span>
            </div>
          </>
        ) : (
          <>
            <LoginForm onLogin={handleLoginSuccess} />
            <div style={{textAlign:'center',marginTop:12,padding:'0 8px'}}>
              <span style={{fontSize:14}}>Hesabınız yok mu?{' '}
                <button 
                  type="button" 
                  onClick={() => setShowRegister(true)} 
                  style={{
                    color:'#2563eb',
                    background:'none',
                    border:'none',
                    padding:'4px 8px',
                    textDecoration:'underline',
                    cursor:'pointer',
                    fontSize:'14px'
                  }}
                >
                  Kayıt Ol
                </button>
              </span>
            </div>
          </>
        )}
      </ModalContent>
    </ModalOverlay>
  );
};

export default LoginModalWrapper;
