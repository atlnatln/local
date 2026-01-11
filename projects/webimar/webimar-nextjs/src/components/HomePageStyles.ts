import styled from 'styled-components';

// Modern CSS Grid Layout with responsive design
export const PageContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #faf8f5 0%, #f5f1ec 100%);
  
  @media (max-width: 768px) {
    min-height: 100vh;
  }
`;

export const HeroSection = styled.section`
  background: linear-gradient(
    135deg, 
    rgba(139, 69, 19, 0.95) 0%, 
    rgba(101, 67, 33, 0.95) 100%
  );
  padding: 80px 2rem 60px;
  text-align: center;
  color: #f5f5dc;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml;utf8,<svg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"><circle cx="30" cy="30" r="1.5" fill="%23A0522D" opacity="0.3"/></svg>');
    pointer-events: none;
  }
  
  @media (max-width: 768px) {
    padding: 60px 1rem 40px;
  }
`;

export const HeroTitle = styled.h1`
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 800;
  margin: 0 0 1.5rem 0;
  font-family: 'Georgia', serif;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  line-height: 1.2;
  position: relative;
  z-index: 1;
  
  @media (max-width: 768px) {
    margin-bottom: 1rem;
  }
`;

export const HeroDescription = styled.p`
  font-size: clamp(1rem, 2.5vw, 1.25rem);
  opacity: 0.95;
  max-width: 800px;
  margin: 0 auto;
  line-height: 1.8;
  font-family: 'Georgia', serif;
  position: relative;
  z-index: 1;
  
  @media (max-width: 768px) {
    line-height: 1.6;
  }
`;

export const MainContent = styled.main`
  max-width: 1200px;
  margin: 0 auto;
  padding: 4rem 2rem;
  
  @media (max-width: 768px) {
    padding: 2rem 1rem;
  }
`;

export const SectionTitle = styled.h2`
  color: #654321;
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  font-weight: 700;
  text-align: center;
  margin: 0 0 3rem 0;
  font-family: 'Georgia', serif;
  text-shadow: 0 1px 2px rgba(139, 69, 19, 0.1);
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 50%;
    transform: translateX(-50%);
    width: 80px;
    height: 3px;
    background: linear-gradient(90deg, transparent, #d2691e, transparent);
    border-radius: 2px;
  }
  
  @media (max-width: 768px) {
    margin-bottom: 2rem;
  }
`;

export const CategoriesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  margin-bottom: 4rem;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    margin-bottom: 2rem;
  }
`;

export const CategoryCard = styled.article`
  background: linear-gradient(135deg, #ffffff 0%, #faf8f5 100%);
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 
    0 4px 20px rgba(139, 69, 19, 0.08),
    0 1px 3px rgba(139, 69, 19, 0.1);
  border: 1px solid rgba(139, 69, 19, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 
      0 8px 30px rgba(139, 69, 19, 0.12),
      0 2px 6px rgba(139, 69, 19, 0.15);
  }
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: linear-gradient(90deg, #d2691e, #8b4513);
  }
  
  @media (max-width: 768px) {
    padding: 1.5rem;
  }
`;

export const CategoryHeader = styled.header`
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 1rem;
`;

export const CategoryIcon = styled.span`
  font-size: 2.5rem;
  filter: drop-shadow(0 2px 4px rgba(139, 69, 19, 0.2));
  
  @media (max-width: 768px) {
    font-size: 2rem;
  }
`;

export const CategoryTitle = styled.h3`
  color: #654321;
  font-size: clamp(1.25rem, 3vw, 1.5rem);
  font-weight: 700;
  margin: 0;
  font-family: 'Georgia', serif;
  line-height: 1.3;
`;

export const CategoryDescription = styled.p`
  color: #8b4513;
  font-size: 0.95rem;
  margin: 0 0 1.5rem 0;
  line-height: 1.6;
  font-style: italic;
`;

export const StructuresGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
`;

export const StructureLink = styled.a`
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: linear-gradient(135deg, #f5f1ec 0%, #ede4d8 100%);
  border: 1px solid #d2691e;
  border-radius: 8px;
  padding: 1rem;
  text-decoration: none;
  color: #654321;
  font-size: 0.9rem;
  font-weight: 600;
  font-family: 'Georgia', serif;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  
  &:hover {
    border-color: #b8860b;
    background: linear-gradient(135deg, #ede4d8 0%, #e6d4c4 100%);
    color: #8b4513;
    text-decoration: none;
    transform: translateX(4px);
  }
  
  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    background: #d2691e;
    transform: scaleY(0);
    transition: transform 0.3s ease;
  }
  
  &:hover::before {
    transform: scaleY(1);
  }
  
  @media (max-width: 768px) {
    padding: 0.875rem;
    font-size: 0.85rem;
  }
`;

export const StructureIcon = styled.span`
  font-size: 1.25rem;
  flex-shrink: 0;
  
  @media (max-width: 768px) {
    font-size: 1.1rem;
  }
`;

export const CTASection = styled.section`
  background: linear-gradient(135deg, rgba(139, 69, 19, 0.95) 0%, rgba(160, 82, 45, 0.95) 100%);
  border-radius: 16px;
  padding: 3rem 2rem;
  text-align: center;
  color: #f5f5dc;
  position: relative;
  overflow: hidden;
  margin-top: 4rem;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml;utf8,<svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="1" fill="%23A0522D" opacity="0.2"/></svg>');
    pointer-events: none;
  }
  
  @media (max-width: 768px) {
    padding: 2rem 1.5rem;
    margin-top: 2rem;
  }
`;

export const CTATitle = styled.h2`
  font-size: clamp(1.5rem, 4vw, 2rem);
  font-weight: 800;
  margin: 0 0 1rem 0;
  font-family: 'Georgia', serif;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  position: relative;
  z-index: 1;
`;

export const CTADescription = styled.p`
  font-size: clamp(1rem, 2.5vw, 1.125rem);
  opacity: 0.95;
  margin: 0;
  font-family: 'Georgia', serif;
  line-height: 1.6;
  position: relative;
  z-index: 1;
`;

export const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  font-size: 1.125rem;
  color: #654321;
`;

export const ErrorMessage = styled.div`
  background: #ffeaea;
  border: 1px solid #ffb3b3;
  border-radius: 8px;
  padding: 1.5rem;
  margin: 2rem 0;
  color: #d63031;
  text-align: center;
  font-weight: 500;
`;
