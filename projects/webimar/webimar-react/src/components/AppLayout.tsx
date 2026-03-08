import React, { useState, useEffect, useRef, lazy, Suspense } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import SidebarNavigation from './SidebarNavigation';
import { useIsMobile } from '../hooks/useMediaQuery';
import { LoginModalWrapper, useAuth } from '../auth';
import { saveReturnUrl } from '../utils/redirectUtils'; // EKLENDİ
import { ToastProvider } from '../hooks/useToast';
import Footer from './shared/Footer';

// Lazy load CookieBanner
const CookieBanner = lazy(() => import('./shared/CookieBanner'));

interface AppLayoutProps {
  children: React.ReactNode;
}

const LayoutContainer = styled.div`
  display: flex;
  min-height: 100vh;
  background-color: #f8fafc;
  width: 100%;
  max-width: 100vw;
  overflow-x: hidden;
  box-sizing: border-box;
  position: relative;
`;

const Sidebar = styled.aside<{ $isOpen: boolean }>`
  width: ${props => props.$isOpen ? '280px' : '60px'};
  background: #ffffff;
  border-right: 1px solid #e5e7eb;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
  position: fixed;
  height: 100vh;
  overflow-y: auto;
  z-index: 1201;
  transition: all 0.3s ease;

  @media (max-width: 768px) {
    width: 280px;
    transform: ${props => props.$isOpen ? 'translateX(0)' : 'translateX(-100%)'};
    border-right: ${props => props.$isOpen ? '1px solid #e5e7eb' : 'none'};
    left: 0;
    top: 0;
  }
`;

const MainContent = styled.main<{ $sidebarOpen: boolean }>`
  flex: 1;
  margin-left: ${props => props.$sidebarOpen ? '280px' : '60px'};
  padding: 24px;
  min-height: 100vh;
  transition: margin-left 0.3s ease;
  width: 100%;
  max-width: 100vw;
  overflow-x: hidden;
  box-sizing: border-box;

  @media (max-width: 768px) {
    margin-left: 0;
    padding: 16px;
    width: 100vw;
    max-width: 100vw;
  }
`;

const Header = styled.header`
  background: linear-gradient(
    135deg, 
    #1a1a2e 0%, 
    #16213e 20%, 
    #0f4c75 40%, 
    #3282b8 70%, 
    #bbe1fa 100%
  );
  border-bottom: 4px solid #bbe1fa;
  padding: 20px 32px;
  margin: -24px -24px 32px -24px;
  box-shadow: 
    inset 0 4px 16px rgba(0, 60, 120, 0.15),
    0 8px 32px rgba(0, 60, 120, 0.2),
    0 2px 8px rgba(255, 255, 255, 0.1) inset;
  position: relative;
  overflow: hidden;
  min-height: 80px;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
      radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%),
      radial-gradient(circle at 80% 50%, rgba(255,255,255,0.05) 0%, transparent 50%),
      repeating-linear-gradient(
        45deg,
        transparent 0px,
        rgba(255, 255, 255, 0.03) 1px,
        rgba(255, 255, 255, 0.03) 2px,
        transparent 3px,
        transparent 60px
      );
    pointer-events: none;
    animation: headerShimmer 8s ease-in-out infinite;
  }

  @keyframes headerShimmer {
    0%, 100% { opacity: 0.8; }
    50% { opacity: 1; }
  }

  @media (max-width: 768px) {
    padding: 16px 20px;
    margin: -16px -16px 16px -16px;
    min-height: 70px;
  }
`;

const WaveBackground = styled.div`
  position: absolute;
  left: -20px;
  right: -20px;
  top: -10px;
  bottom: -10px;
  z-index: 0;
  pointer-events: none;
  background: linear-gradient(
    120deg, 
    rgba(255,255,255,0.15) 0%, 
    rgba(187,225,250,0.25) 30%, 
    rgba(50,130,184,0.2) 70%, 
    rgba(255,255,255,0.1) 100%
  );
  border-radius: 20px;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.2);
  box-shadow: 
    0 8px 32px rgba(0,0,0,0.1),
    inset 0 2px 8px rgba(255,255,255,0.2);
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    bottom: 0;
    background: 
      repeating-linear-gradient(
        -45deg,
        transparent 0px,
        rgba(255, 255, 255, 0.1) 1px,
        rgba(255, 255, 255, 0.1) 2px,
        transparent 3px,
        transparent 30px
      );
    animation: modernWave 12s linear infinite;
    opacity: 0.6;
  }

  &::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(
      45deg,
      transparent 30%,
      rgba(255, 255, 255, 0.4) 50%,
      transparent 70%
    );
    animation: sparkle 8s ease-in-out infinite;
    opacity: 0.3;
  }

  @keyframes modernWave {
    0% { background-position: 0 0; }
    100% { background-position: 60px 60px; }
  }

  @keyframes sparkle {
    0%, 100% { 
      transform: translateX(-100%) translateY(-100%) rotate(45deg); 
      opacity: 0;
    }
    50% { 
      transform: translateX(100%) translateY(100%) rotate(45deg); 
      opacity: 0.4;
    }
  }

  @media (max-width: 768px) {
    left: -10px;
    right: -10px;
    top: -5px;
    bottom: -5px;
    border-radius: 15px;
  }
`;

const ModernHeaderTitle = styled.h1`
  position: relative;
  z-index: 1;
  font-size: 3.2rem;
  font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
  font-weight: 900;
  letter-spacing: 2px;
  text-align: center;
  margin: 0;
  background: linear-gradient(
    135deg, 
    #ffffff 0%, 
    #bbe1fa 25%, 
    #ffffff 50%, 
    #e8f4f8 75%, 
    #ffffff 100%
  );
  background-size: 300% auto;
  color: transparent;
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: modernGradient 6s ease-in-out infinite;
  filter: drop-shadow(0 4px 12px rgba(0, 60, 120, 0.3));
  user-select: none;
  display: inline-block;
  text-shadow: 
    0 2px 4px rgba(0, 60, 120, 0.2),
    0 0 20px rgba(255, 255, 255, 0.5);
  width: 100%;

  &::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 50%;
    transform: translateX(-50%);
    width: 80%;
    height: 3px;
    background: linear-gradient(
      90deg, 
      transparent 0%, 
      #bbe1fa 20%, 
      #ffffff 50%, 
      #bbe1fa 80%, 
      transparent 100%
    );
    border-radius: 2px;
    opacity: 0.8;
    animation: titleUnderline 4s ease-in-out infinite alternate;
  }

  @keyframes modernGradient {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
  }

  @keyframes titleUnderline {
    0% { width: 60%; opacity: 0.6; }
    100% { width: 90%; opacity: 1; }
  }

  @media (max-width: 768px) {
    font-size: 2.4rem;
    letter-spacing: 2px;
    padding: 0;
    
    &::after {
      bottom: -6px;
      height: 2px;
    }
  }

  @media (max-width: 480px) {
    font-size: 1.8rem;
    letter-spacing: 1.5px;
  }
`;

const ContentArea = styled.div`
  background: 
    linear-gradient(135deg, #faf8f5 0%, #f5f1ec 100%);
  border-radius: 0;
  box-shadow: 
    inset 0 0 0 2px rgba(139, 69, 19, 0.1),
    0 4px 12px rgba(139, 69, 19, 0.1);
  border: 2px solid #d2691e;
  min-height: calc(100vh - 140px);
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
      repeating-linear-gradient(
        45deg,
        transparent 0px,
        rgba(139, 69, 19, 0.01) 1px,
        rgba(139, 69, 19, 0.01) 2px,
        transparent 3px,
        transparent 60px
      );
    pointer-events: none;
  }
`;

const UserButton = styled.button`
  background: linear-gradient(
    135deg, 
    rgba(255,255,255,0.15) 0%, 
    rgba(255,255,255,0.25) 50%, 
    rgba(255,255,255,0.15) 100%
  );
  color: #ffffff;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: 12px;
  padding: 12px 20px;
  font-size: 14px;
  font-weight: 600;
  font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow:
    0 4px 16px rgba(0, 60, 120, 0.2),
    0 2px 8px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
  overflow: hidden;
  min-width: 120px;
  height: 44px;
  min-height: 44px;
  white-space: nowrap;
  text-align: center;
  z-index: 3;
  backdrop-filter: blur(10px);
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);

  &::before {
    content: '';
    position: absolute;
    inset: 0;
    pointer-events: none;
    background:
      radial-gradient(circle at 30% 30%, rgba(255,255,255,0.2) 0%, transparent 50%),
      linear-gradient(135deg, transparent 0%, rgba(255,255,255,0.05) 50%, transparent 100%);
    z-index: 1;
    transition: opacity 0.3s ease;
  }

  &::after {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    background: linear-gradient(
      45deg,
      rgba(255,255,255,0.1),
      rgba(255,255,255,0.3),
      rgba(255,255,255,0.1)
    );
    border-radius: 14px;
    z-index: -1;
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  &:hover {
    background: linear-gradient(
      135deg, 
      rgba(255,255,255,0.25) 0%, 
      rgba(255,255,255,0.35) 50%, 
      rgba(255,255,255,0.25) 100%
    );
    border-color: rgba(255,255,255,0.5);
    box-shadow: 
      0 8px 24px rgba(0, 60, 120, 0.3), 
      0 4px 12px rgba(0, 0, 0, 0.15),
      inset 0 1px 0 rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
  }

  &:hover::after {
    opacity: 1;
  }

  &:active {
    background: linear-gradient(
      135deg, 
      rgba(255,255,255,0.1) 0%, 
      rgba(255,255,255,0.2) 100%
    );
    border-color: rgba(255,255,255,0.4);
    box-shadow: 
      0 2px 8px rgba(0, 60, 120, 0.2),
      inset 0 2px 4px rgba(0, 0, 0, 0.1);
    transform: translateY(0px) scale(0.98);
  }

  &.login {
    background: linear-gradient(
      135deg, 
      rgba(59, 130, 246, 0.9) 0%, 
      rgba(37, 99, 235, 0.95) 100%
    ) !important;
    color: #fff !important;
    border-color: rgba(255,255,255,0.4) !important;
    box-shadow: 
      0 4px 16px rgba(59, 130, 246, 0.3), 
      0 2px 8px rgba(0, 0, 0, 0.1),
      inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
  }

  &.login:hover {
    background: linear-gradient(
      135deg, 
      rgba(37, 99, 235, 0.95) 0%, 
      rgba(59, 130, 246, 1) 100%
    ) !important;
    border-color: rgba(255,255,255,0.6) !important;
    box-shadow: 
      0 8px 24px rgba(59, 130, 246, 0.4), 
      0 4px 12px rgba(0, 0, 0, 0.15),
      inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
  }

  &.profile {
    background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
    color: #fff !important;
    border-color: rgba(255,255,255,0.4) !important;
  }

  &.logout {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
    color: #fff !important;
    border-color: rgba(255,255,255,0.4) !important;
  }

  @media (max-width: 768px) {
    padding: 10px 18px;
    font-size: 13px;
    min-width: 100px;
    height: 40px;
    min-height: 40px;
    border-radius: 10px;
  }

  @media (max-width: 480px) {
    padding: 8px 14px;
    font-size: 12px;
    min-width: 80px;
    height: 36px;
  }
`;

const HeaderContent = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  z-index: 2;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  backdrop-filter: blur(2px);

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 16px;
  }
`;

const HeaderCenter = styled.div`
  flex: 1;
  display: flex;
  justify-content: center;
  padding: 0 20px;

  @media (max-width: 768px) {
    order: 1;
    padding: 0;
  }
`;

const HeaderRight = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 0 0 auto;

  @media (max-width: 768px) {
    order: 2;
  }
`;

const UserInfo = styled.div`
  margin-top: 4px;
  background: rgba(255,255,255,0.05);
  /* border: 1px solid #d1d5db; */
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 10px;
  color: #000;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  white-space: nowrap;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 5;
  pointer-events: none;
  text-align: right;
  @media (max-width: 768px) {
    text-align: center;
    align-self: center;
    margin-top: 2px;
    border-radius: 0;
    font-size: 11px;
    padding: 6px 10px;
  }
`;

const MobileToggleButton = styled.button<{ $sidebarOpen: boolean }>`
  display: none;
  position: fixed;
  top: 23px;
  left: ${props => props.$sidebarOpen ? '300px' : '20px'};
  z-index: 1001;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  font-size: 20px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
  transition: all 0.3s ease;
  &:hover { background: #2980b9; transform: scale(1.05); }
  &:active { transform: scale(0.95); }
  @media (max-width: 768px) {
    display: flex;
    align-items: center;
    justify-content: center;
  }
`;

const MobileOverlay = styled.div<{ $isVisible: boolean }>`
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  opacity: ${props => props.$isVisible ? 1 : 0};
  visibility: ${props => props.$isVisible ? 'visible' : 'hidden'};
  transition: all 0.3s ease;
  @media (max-width: 768px) {
    display: block;
  }
`;

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const isMobile = useIsMobile();
  const navigate = useNavigate();
  const location = useLocation();

  // AuthContext'ten auth state ve actions'ları al
  const { state: { user, isAuthenticated }, logout } = useAuth();

  // Auth sayfalarında giriş butonunu gizle
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register' || location.pathname === '/auth/login' || location.pathname === '/auth/register';

  // Touch swipe state for sidebar
  const touchStartX = useRef<number | null>(null);
  const touchEndX = useRef<number | null>(null);

  // Mobilde ilk açılışta sidebar kapalı olsun
  useEffect(() => {
    if (isMobile) {
      setSidebarOpen(false);
    }
  }, [isMobile]);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleNavigation = () => {
    if (isMobile) {
      setSidebarOpen(false);
    }
  };

  const handleLogin = () => {
    // Mevcut sayfayı geri dönüş URL'i olarak kaydet
    saveReturnUrl();
    setShowLoginModal(true);
  };

  const handleLoginSuccess = () => {
    setShowLoginModal(false);
    // AuthContext otomatik olarak user state'ini güncelleyecek
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  // Sektör standartı: Hesabım butonu artık /account sayfasına yönlendiriyor
  const handleProfile = () => {
    navigate('/account');
  };

  // Sidebar swipe handlers:
  const handleTouchStart = (e: React.TouchEvent) => {
    if (!sidebarOpen) return;
    touchStartX.current = e.touches[0].clientX;
  };
  const handleTouchMove = (e: React.TouchEvent) => {
    if (!sidebarOpen) return;
    touchEndX.current = e.touches[0].clientX;
  };
  const handleTouchEnd = () => {
    if (!sidebarOpen || touchStartX.current === null || touchEndX.current === null) {
      touchStartX.current = null;
      touchEndX.current = null;
      return;
    }
    // Sağdan sola swipe: en az 70px kayma
    if (touchStartX.current - touchEndX.current > 70) {
      setSidebarOpen(false);
    }
    touchStartX.current = null;
    touchEndX.current = null;
  };

  return (
    <ToastProvider>
      <LayoutContainer>
        <Sidebar
          $isOpen={sidebarOpen}
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
        >
          <SidebarNavigation
            isOpen={sidebarOpen}
            onToggle={toggleSidebar}
            onNavigate={handleNavigation}
          />
        </Sidebar>

        <MobileToggleButton $sidebarOpen={sidebarOpen} onClick={toggleSidebar}>
          {sidebarOpen ? '✕' : '☰'}
        </MobileToggleButton>
        <MobileOverlay $isVisible={sidebarOpen} onClick={toggleSidebar} />

        <MainContent $sidebarOpen={sidebarOpen}>
          <Header>
            <WaveBackground />
            <HeaderContent>
              <div></div>
              <HeaderCenter>
                <ModernHeaderTitle>
                  <span style={{ letterSpacing: '2px' }}>🌾</span>
                  <span style={{ display: 'inline-block', width: '0.2em' }}></span>
                  <span style={{ letterSpacing: '2px' }}>tarım</span>
                  <span style={{ display: 'inline-block', width: '0.35em' }}></span>
                  <span style={{ letterSpacing: '2px' }}>imar</span>
                  <span style={{ display: 'inline-block', width: '0.2em' }}></span>
                  <span style={{ letterSpacing: '2px' }}>🏗️</span>
                </ModernHeaderTitle>
              </HeaderCenter>
              <HeaderRight>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px' }}>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    {!isAuthenticated && !isAuthPage ? (
                      <UserButton className="login" onClick={handleLogin}>
                        <span className="desktop-text">Giriş Yap</span>
                      </UserButton>
                    ) : isAuthenticated ? (
                      <>
                        <UserButton className="profile" onClick={handleProfile}>
                          {isMobile ? 'Hesabım' : (<><span className="mobile-icon">👤</span><span className="desktop-text">Hesabım</span></>)}
                        </UserButton>
                        <UserButton className="logout" onClick={handleLogout}>
                          {isMobile ? 'Çıkış' : (<><span className="mobile-icon">🚪</span><span className="desktop-text">Çıkış</span></>)}
                        </UserButton>
                      </>
                    ) : null}
                  </div>
                  {isAuthenticated && user && (
                    <UserInfo>
                      {user.email || user.username || 'Kullanıcı'}
                    </UserInfo>
                  )}
                </div>
              </HeaderRight>
            </HeaderContent>
          </Header>
          <ContentArea>
            {children}
          </ContentArea>
          <Footer />
          {showLoginModal && (
            <LoginModalWrapper
              onClose={() => setShowLoginModal(false)}
              onLoginSuccess={handleLoginSuccess}
            />
          )}
          {/* Profil modalı artık ana sayfa üzerinden açılacak, Hesabım butonu /account sayfasına yönlendiriyor */}
          <Suspense fallback={null}>
            <CookieBanner />
          </Suspense>
        </MainContent>
      </LayoutContainer>
    </ToastProvider>
  );
};

export default AppLayout;
