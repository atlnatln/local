import styled, { keyframes } from 'styled-components';

// Cursor yanıp sönme animasyonu
export const blink = keyframes`
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
`;

// Ana form container
export const FormContainer = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
  overflow: hidden;
`;

// Form başlığı
export const FormTitle = styled.h2`
  color: #2c3e50;
  margin: 0;
  padding: 24px 24px 16px;
  font-size: 24px;
  font-weight: 600;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
  
  @media (max-width: 768px) {
    font-size: 20px;
    padding: 20px 16px 12px;
  }
`;

// Form içeriği
export const FormContent = styled.div`
  padding: 24px;
  
  @media (max-width: 768px) {
    padding: 8px;
  }
`;

// Form bölümü
export const FormSection = styled.div`
  margin-bottom: 32px;
  
  &:last-child {
    margin-bottom: 0;
  }
  
  @media (max-width: 768px) {
    margin-bottom: 24px;
  }
`;

// Bölüm başlığı
export const SectionTitle = styled.h3`
  color: #374151;
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #f3f4f6;
  display: flex;
  align-items: center;
  gap: 8px;
  
  @media (max-width: 768px) {
    font-size: 15px;
    margin-bottom: 12px;
  }
`;

// Form grid düzeni
export const FormGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 12px;
    margin: 0 -4px; /* Mobilde daha geniş yapıyoruz */
  }
`;

// Form grubu
export const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
`;

// Label
export const Label = styled.label`
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 14px;
`;

// Input alanı
export const Input = styled.input`
  padding: 12px;
  border: 2px solid #e0e6ed;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.2s ease;

  &:focus {
    outline: none;
    border-color: #3498db;
  }

  &:invalid {
    border-color: #e74c3c;
  }
`;

// Submit butonu
export const SubmitButton = styled.button<{ $isLoading: boolean }>`
  background: ${props => props.$isLoading ? '#95a5a6' : '#3498db'};
  color: white;
  border: none;
  padding: 16px 32px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: ${props => props.$isLoading ? 'not-allowed' : 'pointer'};
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  margin-top: 8px;

  &:hover {
    background: ${props => props.$isLoading ? '#95a5a6' : '#2980b9'};
    transform: ${props => props.$isLoading ? 'none' : 'translateY(-1px)'};
  }

  &:disabled {
    background: #95a5a6;
    cursor: not-allowed;
    transform: none;
  }
  
  @media (max-width: 768px) {
    padding: 14px 24px;
    font-size: 15px;
  }
`;

// Hata mesajı
export const ErrorMessage = styled.div`
  background: #fef5f5;
  border: 1px solid #feb2b2;
  color: #c53030;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;
`;

// Smart Auto-Detection UI Feedback Bileşenleri
export const SmartDetectionFeedback = styled.div<{ $variant: 'manual' | 'map' | 'reset' }>`
  margin-top: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  animation: slideIn 0.3s ease-out;
  
  ${props => props.$variant === 'manual' && `
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    color: #856404;
  `}
  
  ${props => props.$variant === 'map' && `
    background: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
  `}
  
  ${props => props.$variant === 'reset' && `
    background: #cce7ff;
    border: 1px solid #99d6ff;
    color: #0056b3;
  `}
  
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

// Haritaya dön butonu
export const ResetToMapButton = styled.button`
  background: none;
  border: none;
  color: #0056b3;
  font-size: 11px;
  text-decoration: underline;
  cursor: pointer;
  padding: 0;
  margin-left: auto;
  
  &:hover {
    color: #003d82;
  }
`;

// Zorunlu alan göstergesi
export const RequiredIndicator = styled.span`
  color: #e74c3c;
  margin-left: 4px;
`;

// Emsal türü seçim butonları container
export const EmsalTuruContainer = styled.div`
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: 8px;
  }
`;

// Emsal türü seçim butonu
export const EmsalTuruButton = styled.button<{ $isSelected: boolean }>`
  flex: 1;
  min-width: 140px;
  padding: 14px 20px;
  border: 2px solid ${props => props.$isSelected ? '#3498db' : '#e0e6ed'};
  border-radius: 8px;
  background: ${props => props.$isSelected ? '#3498db' : '#ffffff'};
  color: ${props => props.$isSelected ? '#ffffff' : '#2c3e50'};
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  
  &:hover {
    border-color: #3498db;
    background: ${props => props.$isSelected ? '#2980b9' : '#f8f9fa'};
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  .emsal-title {
    font-size: 15px;
    font-weight: 700;
  }
  
  .emsal-subtitle {
    font-size: 12px;
    opacity: 0.8;
    font-weight: 400;
  }
  
  .emsal-percentage {
    font-size: 20px;
    font-weight: 800;
    margin: 4px 0;
  }
  
  @media (max-width: 768px) {
    padding: 12px 16px;
    
    .emsal-title {
      font-size: 14px;
    }
    
    .emsal-percentage {
      font-size: 18px;
    }
    
    .emsal-subtitle {
      font-size: 11px;
    }
  }
`;

// Dikili kontrol butonu
export const DikiliKontrolButton = styled.button`
  background: linear-gradient(135deg, #27ae60, #2ecc71);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  margin-top: 4px;

  &:hover {
    background: linear-gradient(135deg, #229954, #27ae60);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
  }

  &:active {
    transform: translateY(0);
  }
  
  @media (max-width: 768px) {
    padding: 12px 16px;
    font-size: 13px;
  }
`;

// Animasyonlu Select Container
export const AnimatedSelectContainer = styled.div`
  position: relative;
`;

// Animasyonlu Select
export const AnimatedSelect = styled.select<{ $hasValue?: boolean }>`
  padding: 12px;
  border: 2px solid #e0e6ed;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.2s ease;
  width: 100%;
  background: white;
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 12px center;
  background-repeat: no-repeat;
  background-size: 16px;
  padding-right: 40px;

  &:focus {
    outline: none;
    border-color: #3498db;
  }

  &:invalid {
    border-color: #e74c3c;
  }

  option:first-child {
    color: #999;
  }
`;

// Typewriter placeholder
export const TypewriterPlaceholder = styled.div<{ $show?: boolean }>`
  position: absolute;
  top: 50%;
  left: 12px;
  transform: translateY(-50%);
  color: #999;
  font-size: 16px;
  pointer-events: none;
  opacity: ${props => props.$show ? 1 : 0};
  transition: opacity 0.2s ease;
  font-family: inherit;
  
  .cursor {
    animation: ${blink} 1s infinite;
  }
`;
