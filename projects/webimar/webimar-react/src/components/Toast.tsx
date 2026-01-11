import React, { useEffect } from 'react';
import styled, { keyframes } from 'styled-components';

interface ToastProps {
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  onClose: () => void;
  duration?: number;
}

const slideIn = keyframes`
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
`;

const ToastContainer = styled.div<{ type: 'success' | 'error' | 'warning' | 'info' }>`
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 9999;
  min-width: 300px;
  max-width: 500px;
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: ${slideIn} 0.3s ease-out;
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 14px;
  font-weight: 500;
  
  ${({ type }) => {
    switch (type) {
      case 'success':
        return `
          background: #d1fae5;
          color: #065f46;
          border: 1px solid #a7f3d0;
        `;
      case 'error':
        return `
          background: #fee2e2;
          color: #991b1b;
          border: 1px solid #fecaca;
        `;
      case 'warning':
        return `
          background: #fef3c7;
          color: #92400e;
          border: 1px solid #fde68a;
        `;
      case 'info':
        return `
          background: #dbeafe;
          color: #1e40af;
          border: 1px solid #93c5fd;
        `;
      default:
        return '';
    }
  }}
  
  @media (max-width: 768px) {
    right: 16px;
    left: 16px;
    min-width: auto;
    max-width: none;
  }
`;

const ToastIcon = styled.span<{ type: 'success' | 'error' | 'warning' | 'info' }>`
  font-size: 18px;
  flex-shrink: 0;
  
  ${({ type }) => {
    switch (type) {
      case 'success':
        return `content: '✅';`;
      case 'error':
        return `content: '❌';`;
      case 'warning':
        return `content: '⚠️';`;
      case 'info':
        return `content: 'ℹ️';`;
      default:
        return '';
    }
  }}
  
  &::before {
    ${({ type }) => {
      switch (type) {
        case 'success':
          return `content: '✅';`;
        case 'error':
          return `content: '❌';`;
        case 'warning':
          return `content: '⚠️';`;
        case 'info':
          return `content: 'ℹ️';`;
        default:
          return '';
      }
    }}
  }
`;

const ToastMessage = styled.span`
  flex: 1;
  line-height: 1.4;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  margin-left: auto;
  opacity: 0.7;
  flex-shrink: 0;
  
  &:hover {
    opacity: 1;
  }
`;

const Toast: React.FC<ToastProps> = ({ message, type, onClose, duration = 5000 }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [onClose, duration]);

  return (
    <ToastContainer type={type}>
      <ToastIcon type={type} />
      <ToastMessage>{message}</ToastMessage>
      <CloseButton onClick={onClose}>×</CloseButton>
    </ToastContainer>
  );
};

export default Toast;
