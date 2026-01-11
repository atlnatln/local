import React, { useEffect } from 'react';
import styled from 'styled-components';
import { useStructureTypes } from '../contexts/StructureTypesContext';
import { Link } from 'react-router-dom';
import SEO from '../components/SEO';

// Yapı türü ikonları eşlemesi
const structureTypeIcons: Record<string, string> = {
  'hububat-silo': '🌾',
  'tarimsal-depo': '🏪',
  'lisansli-depo': '📦',
  'yikama-tesisi': '🚿',
  'kurutma-tesisi': '🌞',
  'meyve-sebze-kurutma': '🍑',
  'zeytinyagi-fabrikasi': '🫒',
  'su-depolama': '💧',
  'su-kuyulari': '⛲',
  'bag-evi': '🏡',
  'soguk-hava-deposu': '❄️',
  'solucan-tesisi': '🪱',
  'mantar-tesisi': '🍄',
  'sera': '🌱',
  'aricilik': '🐝',
  'sut-sigirciligi': '🐄',
  'agil-kucukbas': '🐑',
  'kumes-yumurtaci': '🥚',
  'kumes-etci': '🍗',
  'kumes-gezen': '🐔',
  'kumes-hindi': '🦃',
  'kaz-ordek': '🦆',
  'hara': '🐎',
  'ipek-bocekciligi': '🦋',
  'evcil-hayvan': '🐕',
  'besi-sigirciligi': '🐃',
  // Diğerleri için default:
};

// Belediye logoları kaldırıldı

const HomeContainer = styled.div`
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
  background: #f7f3f0;
  position: relative;
  overflow-x: hidden;
  width: 100%;
  box-sizing: border-box;
  
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
        rgba(139, 69, 19, 0.02) 0px,
        rgba(139, 69, 19, 0.02) 2px,
        transparent 2px,
        transparent 20px
      );
    pointer-events: none;
  }
  
  @media (max-width: 768px) {
    padding: 0;
    margin: 0;
    width: 100%;
    max-width: 100%;
    overflow-x: hidden;
    box-sizing: border-box;
  }
`;

const HeroSection = styled.div`
  text-align: center;
  margin-bottom: 60px;
  padding: 60px 40px;
  background: 
    linear-gradient(135deg, rgba(139, 69, 19, 0.9) 0%, rgba(101, 67, 33, 0.9) 100%),
    url('data:image/svg+xml;utf8,<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><defs><pattern id="wood" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse"><rect width="20" height="20" fill="%23D2691E"/><path d="M0 0L20 20M20 0L0 20" stroke="%23A0522D" stroke-width="0.5" opacity="0.3"/></pattern></defs><rect width="100%" height="100%" fill="url(%23wood)"/></svg>');
  background-size: 100px 100px, cover;
  border-radius: 0;
  color: #f5f5dc;
  margin: -24px -24px 60px -24px;
  position: relative;
  box-shadow: 
    inset 0 0 0 3px rgba(139, 69, 19, 0.3),
    0 8px 32px rgba(139, 69, 19, 0.2);
  overflow-x: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
      repeating-linear-gradient(
        0deg,
        rgba(139, 69, 19, 0.1) 0px,
        transparent 1px,
        transparent 8px,
        rgba(139, 69, 19, 0.1) 9px
      );
    pointer-events: none;
  }
  
  @media (max-width: 600px) {
    padding: 28px 16px;
    margin: 0 0 32px 0;
    width: 100%;
    max-width: 100%;
    overflow-x: hidden;
    box-sizing: border-box;
  }
`;

const HeroTitle = styled.h1`
  font-size: 48px;
  font-weight: 800;
  margin: 0 0 16px 0;
  font-family: 'Playfair Display', 'Georgia', serif;
  text-shadow: 
    2px 2px 4px rgba(0, 0, 0, 0.5),
    0 0 20px rgba(245, 245, 220, 0.3);
  color: #f5f5dc;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 50%;
    transform: translateX(-50%);
    width: 120px;
    height: 3px;
    background: linear-gradient(90deg, transparent, #d2691e, transparent);
    border-radius: 2px;
  }
  
  @media (max-width: 600px) {
    font-size: 28px;
  }
`;

const HeroDescription = styled.p`
  font-size: 20px;
  opacity: 1;
  max-width: 900px;
  margin: 0 auto;
  line-height: 2.1;
  font-family: 'Crimson Text', 'Georgia', serif;
  color: #fffbe9;
  font-weight: 500;
  letter-spacing: 0.2px;
  text-shadow: 0 1px 2px rgba(139,69,19,0.12);
  background: rgba(139,69,19,0.04);
  border-radius: 8px;
  padding: 12px 18px;
  box-sizing: border-box;
  @media (max-width: 600px) {
    font-size: 15px;
    max-width: 98vw;
    padding: 8px 6px;
    border-radius: 4px;
  }
`;

const StructureTypesSection = styled.div`
  margin-bottom: 60px;
  background: 
    linear-gradient(135deg, #faf8f5 0%, #f5f1ec 100%);
  padding: 40px;
  border: 2px solid #d2691e;
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
        0deg,
        transparent 0px,
        rgba(139, 69, 19, 0.02) 1px,
        rgba(139, 69, 19, 0.02) 2px,
        transparent 3px,
        transparent 30px
      );
    pointer-events: none;
  }
  
  @media (max-width: 600px) {
    margin: 0 16px 40px 16px;
    padding: 16px;
    border-width: 1px;
    width: calc(100% - 32px);
    max-width: calc(100% - 32px);
    overflow-x: hidden;
    box-sizing: border-box;
  }
`;

const SectionTitle = styled.h2`
  color: #654321;
  font-size: 36px;
  font-weight: 800;
  text-align: center;
  margin: 0 0 50px 0;
  font-family: 'Playfair Display', 'Georgia', serif;
  text-shadow: 
    2px 2px 4px rgba(139, 69, 19, 0.2),
    0 0 20px rgba(139, 69, 19, 0.1);
  position: relative;
  
  &::before {
    content: '🌾';
    position: absolute;
    top: 50%;
    left: 20px;
    transform: translateY(-50%);
    font-size: 24px;
    opacity: 0.3;
  }
  
  &::after {
    content: '🌾';
    position: absolute;
    top: 50%;
    right: 20px;
    transform: translateY(-50%);
    font-size: 24px;
    opacity: 0.3;
  }
  
  @media (max-width: 600px) {
    font-size: 22px;
    margin-bottom: 30px;
    
    &::before,
    &::after {
      display: none;
    }
  }
`;

const StructureTypesGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  gap: 50px;
  
  @media (max-width: 600px) {
    gap: 30px;
  }
`;

const CategorySection = styled.div`
  background: 
    linear-gradient(135deg, #ffffff 0%, #faf8f5 100%);
  border-radius: 0;
  padding: 40px;
  box-shadow: 
    inset 0 0 0 2px rgba(139, 69, 19, 0.1),
    0 8px 24px rgba(139, 69, 19, 0.1);
  border: 2px solid #d2691e;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 15px;
    left: 15px;
    right: 15px;
    bottom: 15px;
    border: 1px solid rgba(139, 69, 19, 0.1);
    pointer-events: none;
  }
  
  @media (max-width: 600px) {
    padding: 24px;
    border-width: 1px;
  }
`;

const CategoryHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30px;
  
  @media (max-width: 600px) {
    margin-bottom: 20px;
  }
`;

const CategoryIcon = styled.span`
  font-size: 40px;
  margin-right: 16px;
  text-shadow: 0 2px 4px rgba(139, 69, 19, 0.2);
  
  @media (max-width: 600px) {
    font-size: 28px;
    margin-right: 10px;
  }
`;

const CategoryTitle = styled.h3`
  color: #654321;
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  font-family: 'Playfair Display', 'Georgia', serif;
  text-shadow: 0 1px 2px rgba(139, 69, 19, 0.1);
  
  @media (max-width: 600px) {
    font-size: 18px;
  }
`;

const CategoryGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  
  @media (max-width: 600px) {
    grid-template-columns: 1fr;
    gap: 15px;
  }
`;

const StructureTypeButton = styled(Link)`
  display: flex;
  align-items: center;
  gap: 12px;
  background: 
    linear-gradient(135deg, #f5f1ec 0%, #ede4d8 100%);
  border: 2px solid #d2691e;
  border-radius: 0;
  padding: 16px 20px;
  text-decoration: none;
  color: #654321;
  font-size: 15px;
  font-weight: 600;
  font-family: 'Crimson Text', 'Georgia', serif;
  transition: all 0.3s ease;
  cursor: pointer;
  box-shadow: 
    inset 0 1px 4px rgba(255, 255, 255, 0.3),
    0 2px 8px rgba(139, 69, 19, 0.1);
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 4px;
    left: 4px;
    right: 4px;
    bottom: 4px;
    border: 1px solid rgba(139, 69, 19, 0.1);
    pointer-events: none;
  }
  
  &:hover {
    border-color: #b8860b;
    background: 
      linear-gradient(135deg, #ede4d8 0%, #e6d4c4 100%);
    color: #8b4513;
    text-decoration: none;
    box-shadow: 
      inset 0 1px 4px rgba(255, 255, 255, 0.4),
      0 4px 12px rgba(139, 69, 19, 0.2);
    transform: translateY(-2px);
  }
  
  @media (max-width: 600px) {
    padding: 12px 16px;
    font-size: 13px;
  }
`;

const StructureTypeIcon = styled.div`
  font-size: 22px;
  margin-right: 8px;
  display: flex;
  align-items: center;
  text-shadow: 0 1px 2px rgba(139, 69, 19, 0.2);
  
  @media (max-width: 600px) {
    font-size: 18px;
    margin-right: 6px;
  }
`;

const GetStartedSection = styled.div`
  background: 
    linear-gradient(135deg, rgba(139, 69, 19, 0.95) 0%, rgba(160, 82, 45, 0.95) 100%),
    url('data:image/svg+xml;utf8,<svg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"><defs><pattern id="rustic" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="1.5" fill="%23A0522D" opacity="0.3"/></pattern></defs><rect width="100%" height="100%" fill="url(%23rustic)"/></svg>');
  border-radius: 0;
  padding: 50px 40px;
  text-align: center;
  color: #f5f5dc;
  position: relative;
  border: 3px solid #d2691e;
  box-shadow: 
    inset 0 0 0 2px rgba(139, 69, 19, 0.2),
    0 8px 24px rgba(139, 69, 19, 0.2);
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
      repeating-linear-gradient(
        -45deg,
        transparent 0px,
        rgba(139, 69, 19, 0.1) 1px,
        rgba(139, 69, 19, 0.1) 2px,
        transparent 3px,
        transparent 20px
      );
    pointer-events: none;
  }
  
  &::after {
    content: '🏡';
    position: absolute;
    top: 20px;
    left: 20px;
    font-size: 24px;
    opacity: 0.4;
  }
  
  @media (max-width: 600px) {
    padding: 24px 16px;
    margin: 0 16px;
    border-width: 2px;
    max-width: calc(100vw - 32px);
    overflow-x: hidden;
  }
`;

const GetStartedTitle = styled.h2`
  font-size: 32px;
  font-weight: 800;
  margin: 0 0 20px 0;
  font-family: 'Playfair Display', 'Georgia', serif;
  text-shadow: 
    2px 2px 4px rgba(0, 0, 0, 0.5),
    0 0 20px rgba(245, 245, 220, 0.3);
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 50%;
    transform: translateX(-50%);
    width: 100px;
    height: 2px;
    background: linear-gradient(90deg, transparent, #d2691e, transparent);
    border-radius: 2px;
  }
  
  @media (max-width: 600px) {
    font-size: 20px;
    margin-bottom: 12px;
  }
`;

const GetStartedDescription = styled.p`
  font-size: 18px;
  opacity: 0.95;
  margin: 0 0 30px 0;
  font-family: 'Crimson Text', 'Georgia', serif;
  line-height: 1.6;
  font-style: italic;
  
  @media (max-width: 600px) {
    font-size: 14px;
    margin-bottom: 20px;
  }
`;

const HomePage: React.FC = () => {
  const { structureTypeLabels, structureCategories } = useStructureTypes();

  // Sayfa başlığını ayarla
  useEffect(() => {
    document.title = 'Tarım İmar - Tarımsal Yapılaşma Hesaplama Sistemi';
  }, []);

  // "Depolama ve İşleme Tesisleri" kategorisini en üste taşı
  let categories = Object.values(structureCategories);
  const depoIndex = categories.findIndex((cat: any) => cat.name === "Depolama ve İşleme Tesisleri");
  if (depoIndex > 0) {
    const [depo] = categories.splice(depoIndex, 1);
    categories = [depo, ...categories];
  }

  return (
    <>
      <SEO
        title="Tarımsal Yapılaşma Hesaplama Sistemi | Tarım İmar"
        description="Tarımsal arazilerde yapılaşma hesaplamaları için güncel mevzuata uygun, güvenilir ve hızlı hesaplama sistemi. 27 farklı yapı türü için detaylı analiz ve hesaplama desteği."
        canonical="/"
        keywords="tarımsal yapılaşma, tarım imar, hesaplama sistemi, tarımsal tesisler, arazi hesaplama"
      />
      <HomeContainer>
      <HeroSection>
        <HeroTitle>Arazilerde Yapılaşma Mevzuatı ve Hesaplama Sistemi</HeroTitle>
        <HeroDescription>
          Tarımsal arazilerde yapılaşma süreçlerinde güncel mevzuata ve bilimsel esaslara uygun, güvenilir ve hızlı hesaplama çözümleri. 
          Yasal sınırlar, teknik gereklilikler ve modern teknolojinin birleştiği noktada, doğru ve şeffaf analiz ile karar desteği sunuyoruz.
        </HeroDescription>
      </HeroSection>

      <GetStartedSection>
        <GetStartedTitle>Hesaplamaya Başlayın</GetStartedTitle>
        <GetStartedDescription>
          Yapı hesaplamalarınızı güvenilir ve hızlı bir şekilde yapın.
        </GetStartedDescription>
      </GetStartedSection>

      <StructureTypesSection>
        <SectionTitle>Desteklenen Yapı Türleri</SectionTitle>
        <StructureTypesGrid>
          {categories.map((category: any, index) => (
            <CategorySection key={index}>
              <CategoryHeader>
                <CategoryIcon>{category.icon}</CategoryIcon>
                <CategoryTitle>{category.name}</CategoryTitle>
              </CategoryHeader>
              <CategoryGrid>
                {category.types.map((type: string, idx: number) => (
                  <StructureTypeButton key={type + '-' + idx} to={`/${type}`}>
                    <StructureTypeIcon>
                      {structureTypeIcons[type] || category.icon}
                    </StructureTypeIcon>
                    <span>{structureTypeLabels[type as keyof typeof structureTypeLabels] || type}</span>
                  </StructureTypeButton>
                ))}
              </CategoryGrid>
            </CategorySection>
          ))}
        </StructureTypesGrid>
      </StructureTypesSection>
    </HomeContainer>
    </>
  );
};

export default HomePage;
