import React from 'react';
import styled from 'styled-components';

interface LocationAlertProps {
  type: 'error' | 'warning' | 'info';
  message: string;
  onClose?: () => void;
  autoClose?: boolean;
}

const AlertContainer = styled.div<{ $type: 'error' | 'warning' | 'info' }>`
  position: fixed;
  top: 20px;
  right: 20px;
  max-width: 400px;
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 10000;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  
  ${props => {
    switch (props.$type) {
      case 'error':
        return `
          background: linear-gradient(135deg, #fee2e2, #fecaca);
          border-left: 4px solid #dc2626;
          color: #7f1d1d;
        `;
      case 'warning':
        return `
          background: linear-gradient(135deg, #fef3c7, #fde68a);
          border-left: 4px solid #f59e0b;
          color: #92400e;
        `;
      case 'info':
        return `
          background: linear-gradient(135deg, #dbeafe, #bfdbfe);
          border-left: 4px solid #3b82f6;
          color: #1e40af;
        `;
    }
  }}
  
  animation: slideIn 0.3s ease-out;
  
  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
`;

const AlertIcon = styled.div`
  font-size: 20px;
  flex-shrink: 0;
  margin-top: 2px;
`;

const AlertContent = styled.div`
  flex: 1;
`;

const AlertMessage = styled.p`
  margin: 0;
  font-size: 14px;
  line-height: 1.4;
  font-weight: 500;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  color: inherit;
  opacity: 0.7;
  transition: opacity 0.2s;
  
  &:hover {
    opacity: 1;
  }
`;

const LocationAlert: React.FC<LocationAlertProps> = ({ 
  type, 
  message, 
  onClose, 
  autoClose = true 
}) => {
  React.useEffect(() => {
    if (autoClose) {
      const timer = setTimeout(() => {
        onClose?.();
      }, 5000); // 5 saniye sonra otomatik kapanır
      
      return () => clearTimeout(timer);
    }
  }, [autoClose, onClose]);

  const getIcon = () => {
    switch (type) {
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'info':
        return 'ℹ️';
    }
  };

  return (
    <AlertContainer $type={type}>
      <AlertIcon>{getIcon()}</AlertIcon>
      <AlertContent>
        <AlertMessage>{message}</AlertMessage>
      </AlertContent>
      {onClose && (
        <CloseButton onClick={onClose}>×</CloseButton>
      )}
    </AlertContainer>
  );
};

export default LocationAlert;
