import React from 'react';
import styled from 'styled-components';
import { getNextJsUrl } from '../../utils/environment';

const FooterContainer = styled.footer`
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f4c75 100%);
  color: #ffffff;
  padding: 48px 24px 24px;
  margin-top: auto;

  @media (max-width: 768px) {
    padding: 32px 16px 20px;
  }

  @media (max-width: 480px) {
    padding: 28px 14px 16px;
    padding-bottom: calc(16px + env(safe-area-inset-bottom, 0px));
  }
`;

const FooterContent = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 32px;
  max-width: 1200px;
  margin: 0 auto;

  @media (max-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
    gap: 24px 16px;
  }

  @media (max-width: 480px) {
    grid-template-columns: 1fr;
    gap: 20px;
  }
`;

const FooterSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;

  @media (max-width: 768px) {
    text-align: left;

    &:first-child {
      grid-column: 1 / -1;
      text-align: center;
    }
  }

  @media (max-width: 480px) {
    text-align: center;
  }
`;

const FooterTitle = styled.h3`
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  color: #bbe1fa;

  @media (max-width: 768px) {
    font-size: 1.3rem;
  }

  @media (max-width: 480px) {
    font-size: 1.2rem;
  }
`;

const FooterDescription = styled.p`
  font-size: 0.9rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;

  @media (max-width: 480px) {
    font-size: 0.85rem;
    line-height: 1.5;
  }
`;

const SectionTitle = styled.h4`
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  color: #bbe1fa;
  border-bottom: 2px solid rgba(187, 225, 250, 0.3);
  padding-bottom: 8px;

  @media (max-width: 768px) {
    font-size: 1rem;
  }

  @media (max-width: 480px) {
    font-size: 0.95rem;
    padding-bottom: 6px;
  }
`;

const FooterNav = styled.nav`
  display: flex;
  flex-direction: column;
  gap: 8px;

  @media (max-width: 768px) {
    align-items: flex-start;
  }

  @media (max-width: 480px) {
    align-items: center;
    gap: 6px;
  }

  a {
    color: rgba(255, 255, 255, 0.8);
    text-decoration: none;
    font-size: 0.9rem;
    transition: color 0.2s ease, padding-left 0.2s ease;

    @media (max-width: 768px) {
      font-size: 0.85rem;
      padding: 4px 0;
    }

    @media (max-width: 480px) {
      font-size: 0.88rem;
      padding: 6px 0;
      min-height: 36px;
      display: flex;
      align-items: center;
    }

    &:hover {
      color: #bbe1fa;
      padding-left: 4px;

      @media (hover: none) and (pointer: coarse) {
        padding-left: 0;
      }
    }
  }
`;

const ContactInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;

  a {
    color: rgba(255, 255, 255, 0.8);
    text-decoration: none;
    font-size: 0.9rem;
    transition: color 0.2s ease;

    @media (max-width: 480px) {
      font-size: 0.88rem;
      padding: 6px 0;
    }

    &:hover {
      color: #bbe1fa;
    }
  }
`;

const FooterBottom = styled.div`
  max-width: 1200px;
  margin: 32px auto 0;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;

  @media (max-width: 768px) {
    margin-top: 24px;
    padding-top: 20px;
  }

  @media (max-width: 480px) {
    margin-top: 20px;
    padding-top: 16px;
  }

  p {
    margin: 0;
    font-size: 0.85rem;
    color: rgba(255, 255, 255, 0.7);

    @media (max-width: 480px) {
      font-size: 0.8rem;
    }
  }
`;

const LegalNotice = styled.p`
  margin-top: 8px !important;
  font-size: 0.8rem !important;
  color: rgba(255, 255, 255, 0.5) !important;

  @media (max-width: 480px) {
    font-size: 0.75rem !important;
    line-height: 1.4 !important;
  }
`;

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();
  const baseUrl = getNextJsUrl();

  return (
    <FooterContainer>
      <FooterContent>
        <FooterSection>
          <FooterTitle>🌾 Tarım İmar</FooterTitle>
          <FooterDescription>
            Tarımsal arazilerde yapılaşma süreçlerinde güncel mevzuata uygun, 
            güvenilir hesaplama çözümleri sunuyoruz.
          </FooterDescription>
        </FooterSection>

        <FooterSection>
          <SectionTitle>Hızlı Erişim</SectionTitle>
          <FooterNav>
            <a href={baseUrl}>Ana Sayfa</a>
            <a href="/hesaplama/bag-evi">Bağ Evi</a>
            <a href="/hesaplama/sera">Sera</a>
            <a href={`${baseUrl}/aricilik-planlama`}>Arıcılık Planlama</a>
          </FooterNav>
        </FooterSection>

        <FooterSection>
          <SectionTitle>Hukuki Metinler</SectionTitle>
          <FooterNav>
            <a href={`${baseUrl}/gizlilik-politikasi`}>Gizlilik Politikası</a>
            <a href={`${baseUrl}/kvkk-aydinlatma`}>KVKK Aydınlatma Metni</a>
            <a href={`${baseUrl}/cerez-politikasi`}>Çerez Politikası</a>
            <a href={`${baseUrl}/kullanim-kosullari`}>Kullanım Koşulları</a>
          </FooterNav>
        </FooterSection>

        <FooterSection>
          <SectionTitle>İletişim</SectionTitle>
          <ContactInfo>
            <a href="mailto:info@tarimimar.com.tr">📧 info@tarimimar.com.tr</a>
          </ContactInfo>
        </FooterSection>
      </FooterContent>

      <FooterBottom>
        <p>© {currentYear} Tarım İmar. Tüm hakları saklıdır.</p>
        <LegalNotice>
          Bu site 6698 sayılı KVKK ve GDPR kapsamında kişisel verilerin korunması ilkelerine uygun olarak işletilmektedir.
        </LegalNotice>
      </FooterBottom>
    </FooterContainer>
  );
};

export default Footer;
