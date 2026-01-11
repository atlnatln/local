import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { getNextJsUrl } from '../../utils/environment';

interface CookiePreferences {
  necessary: boolean;
  analytics: boolean;
  functional: boolean;
}

const Overlay = styled.div`
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  animation: slideUp 0.3s ease-out;

  @keyframes slideUp {
    from {
      transform: translateY(100%);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }

  @media (max-width: 480px) {
    background: rgba(0, 0, 0, 0.6);
  }
`;

const Banner = styled.div`
  background: #ffffff;
  border-top: 4px solid #3282b8;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.15);
  max-height: 90vh;
  overflow-y: auto;
  padding-bottom: env(safe-area-inset-bottom, 0px);

  @media (max-width: 768px) {
    max-height: 85vh;
  }

  @media (max-width: 480px) {
    max-height: 80vh;
    border-top-width: 3px;
  }
`;

const Content = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;

  @media (max-width: 768px) {
    padding: 20px 16px;
  }

  @media (max-width: 480px) {
    padding: 16px 12px;
  }
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;

  @media (max-width: 768px) {
    gap: 10px;
  }

  @media (max-width: 480px) {
    margin-bottom: 10px;
  }
`;

const Icon = styled.span`
  font-size: 1.8rem;

  @media (max-width: 768px) {
    font-size: 1.5rem;
  }

  @media (max-width: 480px) {
    font-size: 1.3rem;
  }
`;

const Title = styled.h2`
  font-size: 1.3rem;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0;

  @media (max-width: 768px) {
    font-size: 1.1rem;
  }

  @media (max-width: 480px) {
    font-size: 1rem;
  }
`;

const Description = styled.p`
  font-size: 0.95rem;
  line-height: 1.6;
  color: #4b5563;
  margin: 0 0 20px 0;

  @media (max-width: 768px) {
    font-size: 0.9rem;
    line-height: 1.5;
    margin-bottom: 16px;
  }

  @media (max-width: 480px) {
    font-size: 0.85rem;
    margin-bottom: 14px;
  }
`;

const Details = styled.div`
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;

  @media (max-width: 768px) {
    padding: 16px;
    margin-bottom: 16px;
  }

  @media (max-width: 480px) {
    padding: 14px 12px;
  }
`;

const CookieOption = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px 0;
  border-bottom: 1px solid #e5e7eb;

  &:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }

  &:first-child {
    padding-top: 0;
  }

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 8px;
    padding: 14px 0;
  }
`;

const OptionInfo = styled.div`
  flex: 1;
`;

const OptionLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  font-size: 1rem;
  margin-bottom: 6px;
  min-height: 44px;

  strong {
    color: #1f2937;

    @media (max-width: 480px) {
      font-size: 0.95rem;
    }
  }

  @media (max-width: 768px) {
    gap: 10px;
  }
`;

const OptionDescription = styled.p`
  font-size: 0.85rem;
  color: #6b7280;
  margin: 0;
  padding-left: 32px;

  @media (max-width: 768px) {
    padding-left: 30px;
    font-size: 0.8rem;
  }
`;

const Checkbox = styled.input`
  width: 20px;
  height: 20px;
  cursor: pointer;
  accent-color: #3282b8;
  flex-shrink: 0;

  @media (max-width: 768px) {
    width: 22px;
    height: 22px;
  }

  &:disabled {
    cursor: not-allowed;
  }
`;

const Badge = styled.span`
  font-size: 0.75rem;
  background: #e5e7eb;
  color: #6b7280;
  padding: 4px 10px;
  border-radius: 12px;
  white-space: nowrap;

  @media (max-width: 768px) {
    align-self: flex-start;
    margin-left: 30px;
  }
`;

const Actions = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 10px;
  }
`;

const PrimaryActions = styled.div`
  display: flex;
  gap: 12px;

  @media (max-width: 768px) {
    width: 100%;
    gap: 10px;
  }

  @media (max-width: 480px) {
    flex-direction: column;
  }
`;

const SecondaryActions = styled.div`
  display: flex;
  gap: 12px;

  @media (max-width: 768px) {
    width: 100%;
  }
`;

const buttonStyles = `
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 48px;

  @media (max-width: 768px) {
    flex: 1;
    padding: 14px 16px;
    font-size: 0.9rem;
  }

  @media (max-width: 480px) {
    width: 100%;
    padding: 16px;
    font-size: 0.95rem;
    min-height: 52px;
    border-radius: 10px;
  }
`;

const AcceptButton = styled.button`
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: #ffffff;
  border: none;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
  ${buttonStyles}

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);

    @media (hover: none) and (pointer: coarse) {
      transform: none;
    }
  }
`;

const RejectButton = styled.button`
  background: #ffffff;
  color: #374151;
  border: 2px solid #d1d5db;
  ${buttonStyles}

  &:hover {
    background: #f3f4f6;
    border-color: #9ca3af;
  }
`;

const DetailsButton = styled.button`
  background: transparent;
  color: #3282b8;
  border: 2px solid #3282b8;
  ${buttonStyles}

  &:hover {
    background: #3282b8;
    color: #ffffff;
  }
`;

const Links = styled.div`
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 0.85rem;

  @media (max-width: 480px) {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
    margin-top: 4px;
  }

  a {
    color: #3282b8;
    text-decoration: none;
    transition: color 0.2s ease;
    min-height: 44px;
    display: flex;
    align-items: center;

    @media (max-width: 480px) {
      font-size: 0.8rem;
      padding: 4px 0;
    }

    &:hover {
      color: #0f4c75;
      text-decoration: underline;
    }
  }
`;

const Separator = styled.span`
  color: #d1d5db;

  @media (max-width: 480px) {
    display: none;
  }
`;

const CookieBanner: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [preferences, setPreferences] = useState<CookiePreferences>({
    necessary: true,
    analytics: false,
    functional: false,
  });

  const baseUrl = getNextJsUrl();

  useEffect(() => {
    const savedConsent = localStorage.getItem('cookie_consent');
    if (!savedConsent) {
      setIsVisible(true);
    } else {
      try {
        const parsedConsent = JSON.parse(savedConsent);
        setPreferences(parsedConsent);
        if (parsedConsent.analytics) {
          enableAnalytics();
        }
      } catch (e) {
        setIsVisible(true);
      }
    }
  }, []);

  const enableAnalytics = () => {
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('consent', 'update', {
        analytics_storage: 'granted',
      });
    }
  };

  const disableAnalytics = () => {
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('consent', 'update', {
        analytics_storage: 'denied',
      });
    }
  };

  const savePreferences = (newPreferences: CookiePreferences) => {
    localStorage.setItem('cookie_consent', JSON.stringify(newPreferences));
    localStorage.setItem('cookie_consent_date', new Date().toISOString());
    
    if (newPreferences.analytics) {
      enableAnalytics();
    } else {
      disableAnalytics();
    }
    
    setIsVisible(false);
  };

  const handleAcceptAll = () => {
    const allAccepted: CookiePreferences = {
      necessary: true,
      analytics: true,
      functional: true,
    };
    setPreferences(allAccepted);
    savePreferences(allAccepted);
  };

  const handleRejectAll = () => {
    const onlyNecessary: CookiePreferences = {
      necessary: true,
      analytics: false,
      functional: false,
    };
    setPreferences(onlyNecessary);
    savePreferences(onlyNecessary);
  };

  const handleSavePreferences = () => {
    savePreferences(preferences);
  };

  const handlePreferenceChange = (key: keyof CookiePreferences) => {
    if (key === 'necessary') return;
    setPreferences(prev => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  if (!isVisible) return null;

  return (
    <Overlay>
      <Banner>
        <Content>
          <Header>
            <Icon>🍪</Icon>
            <Title>Çerez Kullanımı</Title>
          </Header>
          
          <Description>
            Web sitemizde deneyiminizi iyileştirmek için çerezler kullanıyoruz. 
            Zorunlu çerezler sitenin çalışması için gereklidir. Diğer çerezleri 
            tercihlerinize göre yönetebilirsiniz.
          </Description>

          {showDetails && (
            <Details>
              <CookieOption>
                <OptionInfo>
                  <OptionLabel>
                    <Checkbox
                      type="checkbox"
                      checked={preferences.necessary}
                      disabled
                    />
                    <strong>Zorunlu Çerezler</strong>
                  </OptionLabel>
                  <OptionDescription>
                    Sitenin temel işlevleri için gereklidir. Bu çerezler olmadan 
                    site düzgün çalışmaz.
                  </OptionDescription>
                </OptionInfo>
                <Badge>Her zaman aktif</Badge>
              </CookieOption>

              <CookieOption>
                <OptionInfo>
                  <OptionLabel>
                    <Checkbox
                      type="checkbox"
                      checked={preferences.analytics}
                      onChange={() => handlePreferenceChange('analytics')}
                    />
                    <strong>Analitik Çerezler</strong>
                  </OptionLabel>
                  <OptionDescription>
                    Site kullanımını analiz etmemize yardımcı olur. 
                    Google Analytics kullanılmaktadır.
                  </OptionDescription>
                </OptionInfo>
              </CookieOption>

              <CookieOption>
                <OptionInfo>
                  <OptionLabel>
                    <Checkbox
                      type="checkbox"
                      checked={preferences.functional}
                      onChange={() => handlePreferenceChange('functional')}
                    />
                    <strong>İşlevsellik Çerezleri</strong>
                  </OptionLabel>
                  <OptionDescription>
                    Tercihlerinizi hatırlar ve kişiselleştirilmiş deneyim sunar.
                  </OptionDescription>
                </OptionInfo>
              </CookieOption>
            </Details>
          )}

          <Actions>
            <PrimaryActions>
              <AcceptButton onClick={handleAcceptAll}>
                Tümünü Kabul Et
              </AcceptButton>
              <RejectButton onClick={handleRejectAll}>
                Sadece Zorunlu
              </RejectButton>
            </PrimaryActions>
            
            <SecondaryActions>
              {showDetails ? (
                <DetailsButton onClick={handleSavePreferences}>
                  Tercihleri Kaydet
                </DetailsButton>
              ) : (
                <DetailsButton onClick={() => setShowDetails(true)}>
                  Tercihleri Yönet
                </DetailsButton>
              )}
            </SecondaryActions>
          </Actions>

          <Links>
            <a href={`${baseUrl}/cerez-politikasi`}>Çerez Politikası</a>
            <Separator>|</Separator>
            <a href={`${baseUrl}/gizlilik-politikasi`}>Gizlilik Politikası</a>
          </Links>
        </Content>
      </Banner>
    </Overlay>
  );
};

export default CookieBanner;
