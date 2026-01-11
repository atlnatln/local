import styled from 'styled-components';

// Panel Styles
export const KontrolPanel = styled.div<{ $isOpen: boolean }>`
  position: fixed;
  top: 0;
  right: ${props => props.$isOpen ? '0' : '-100vw'};
  width: 100vw;
  height: 100vh;
  background: white;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  transition: right 0.3s ease;
  overflow-y: auto;
  padding: 0;

  @media (min-width: 768px) {
    width: 500px;
    right: ${props => props.$isOpen ? '0' : '-500px'};
  }
`;

export const KontrolHeader = styled.div`
  background: linear-gradient(135deg, #27ae60, #2ecc71);
  color: white;
  padding: 20px 20px 20px 20px;
  position: sticky;
  top: 0;
  z-index: 1001;
  text-align: center;
  @media (max-width: 600px) {
    padding-right: 48px; /* Çarpı butonu için boşluk bırak */
  }
`;

export const KontrolTitle = styled.h3`
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
`;

export const KontrolSubtitle = styled.p`
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
  text-align: center;
`;

export const CloseButton = styled.button`
  position: absolute;
  top: 15px;
  right: 15px;
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
`;

export const KontrolContent = styled.div`
  padding: 16px;
  
  @media (min-width: 768px) {
    padding: 20px;
  }
`;

// Tab Styles
export const TabContainer = styled.div`
  display: flex;
  border-bottom: 2px solid #ecf0f1;
  margin-bottom: 20px;
`;

export const TabButton = styled.button<{ $active: boolean }>`
  flex: 1;
  padding: 10px 12px;
  border: none;
  background: ${props => props.$active ? '#27ae60' : 'transparent'};
  color: ${props => props.$active ? 'white' : '#2c3e50'};
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  border-radius: 8px 8px 0 0;
  margin-bottom: -2px;
  
  @media (min-width: 768px) {
    padding: 12px 16px;
    font-size: 14px;
  }
  
  &:hover {
    background: ${props => props.$active ? '#27ae60' : '#ecf0f1'};
  }
`;

// Form Styles
export const FormSection = styled.div`
  margin-bottom: 24px;
`;

export const SectionTitle = styled.h4`
  color: #27ae60;
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
`;

export const FormGroup = styled.div`
  margin-bottom: 16px;
`;

export const Label = styled.label`
  display: block;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 6px;
  font-size: 14px;
`;

export const Input = styled.input`
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #e0e6ed;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: #27ae60;
  }
`;

export const Select = styled.select`
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #e0e6ed;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s ease;
  background: white;
  
  &:focus {
    outline: none;
    border-color: #27ae60;
  }
`;

// Button Styles
export const Button = styled.button<{ $variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' }>`
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  
  ${props => {
    switch (props.$variant) {
      case 'success':
        return `
          background: #27ae60;
          color: white;
          &:hover { background: #229954; }
        `;
      case 'warning':
        return `
          background: #f39c12;
          color: white;
          &:hover { background: #e67e22; }
        `;
      case 'danger':
        return `
          background: #e74c3c;
          color: white;
          &:hover { background: #c0392b; }
        `;
      case 'secondary':
        return `
          background: #95a5a6;
          color: white;
          &:hover { background: #7f8c8d; }
        `;
      default:
        return `
          background: #3498db;
          color: white;
          &:hover { background: #2980b9; }
        `;
    }
  }}

  &.desktop-only {
    @media (max-width: 600px) {
      display: none !important;
    }
  }
`;

// Tree Management Styles
export const AgacListesi = styled.div`
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 12px;
  min-height: 100px;
  max-height: 200px;
  overflow-y: auto;
`;

export const AgacItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #e9ecef;
  
  &:last-child {
    border-bottom: none;
  }
`;

// Result Panel Styles
export const SonucPanel = styled.div<{ $type: 'success' | 'warning' | 'error' }>`
  padding: 16px;
  border-radius: 8px;
  margin-top: 16px;
  
  ${props => {
    switch (props.$type) {
      case 'success':
        return `
          background: #d4edda;
          border: 1px solid #c3e6cb;
          color: #155724;
        `;
      case 'warning':
        return `
          background: #fff3cd;
          border: 1px solid #ffeaa7;
          color: #856404;
        `;
      default:
        return `
          background: #f8d7da;
          border: 1px solid #f5c6cb;
          color: #721c24;
        `;
    }
  }}
`;

// Info Box Styles
export const InfoBox = styled.div`
  background: #e3f2fd;
  border: 1px solid #bbdefb;
  color: #1565c0;
  padding: 12px;
  border-radius: 6px;
  font-size: 13px;
  margin-bottom: 16px;
`;

// Map Styles
export const MapWrapper = styled.div`
  height: 300px;
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 16px;
  border: 2px solid #e0e6ed;
  
  .leaflet-container {
    height: 100%;
    width: 100%;
  }
`;

// Area Display Styles
export const AreaDisplayContainer = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
`;

export const AreaDisplayBox = styled.div<{ $color: string }>`
  padding: 12px;
  border: 2px solid ${props => props.$color};
  border-radius: 6px;
  background: ${props => props.$color}10;
`;

export const AreaLabel = styled.div`
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
`;

export const AreaValue = styled.div`
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
`;

export const AreaSubtext = styled.div`
  font-size: 12px;
  color: #666;
  margin-top: 2px;
`;

// Common inline styles as styled components
export const FlexContainer = styled.div<{ $gap?: string; $direction?: 'row' | 'column' }>`
  display: flex;
  gap: ${props => props.$gap || '8px'};
  flex-direction: ${props => props.$direction || 'row'};
`;

export const InfoText = styled.div<{ size?: string; color?: string; weight?: string }>`
  font-size: ${props => props.size || '14px'};
  color: ${props => props.color || '#666'};
  font-weight: ${props => props.weight || 'normal'};
  margin-top: 4px;
`;

export const HighlightBox = styled.div<{ $variant?: 'success' | 'warning' | 'info' }>`
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 16px;
  font-size: 14px;
  
  ${props => {
    switch (props.$variant) {
      case 'success':
        return `
          background: #e8f5e8;
          border: 1px solid #c3e6cb;
          color: #155724;
        `;
      case 'warning':
        return `
          background: #fff3cd;
          border: 1px solid #ffeaa7;
          color: #856404;
        `;
      default:
        return `
          background: #f8f9fa;
          border: 1px solid #e9ecef;
          color: #2c3e50;
        `;
    }
  }}
`;
