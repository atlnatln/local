import React from 'react';
import styled, { keyframes } from 'styled-components';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  color?: string;
  text?: string;
}

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const SpinnerContainer = styled.div<{ size: 'small' | 'medium' | 'large' }>`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  
  ${({ size }) => {
    switch (size) {
      case 'small':
        return `padding: 8px;`;
      case 'medium':
        return `padding: 16px;`;
      case 'large':
        return `padding: 24px;`;
      default:
        return `padding: 16px;`;
    }
  }}
`;

const Spinner = styled.div<{ size: 'small' | 'medium' | 'large'; color: string }>`
  border: 3px solid #f3f3f3;
  border-top: 3px solid ${({ color }) => color};
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
  
  ${({ size }) => {
    switch (size) {
      case 'small':
        return `
          width: 20px;
          height: 20px;
          border-width: 2px;
        `;
      case 'medium':
        return `
          width: 32px;
          height: 32px;
          border-width: 3px;
        `;
      case 'large':
        return `
          width: 48px;
          height: 48px;
          border-width: 4px;
        `;
      default:
        return `
          width: 32px;
          height: 32px;
          border-width: 3px;
        `;
    }
  }}
`;

const LoadingText = styled.span<{ size: 'small' | 'medium' | 'large' }>`
  color: #6b7280;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  
  ${({ size }) => {
    switch (size) {
      case 'small':
        return `font-size: 12px;`;
      case 'medium':
        return `font-size: 14px;`;
      case 'large':
        return `font-size: 16px;`;
      default:
        return `font-size: 14px;`;
    }
  }}
`;

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'medium', 
  color = '#2563eb', 
  text = 'Yükleniyor...' 
}) => {
  return (
    <SpinnerContainer size={size}>
      <Spinner size={size} color={color} />
      {text && <LoadingText size={size}>{text}</LoadingText>}
    </SpinnerContainer>
  );
};

export default LoadingSpinner;
