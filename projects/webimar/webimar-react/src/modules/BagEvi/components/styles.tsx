/**
 * Bağ Evi Styles
 *
 * Bu dosya bağ evi bileşenleri için stil bileşenlerini içerir
 */

import styled from 'styled-components';

// Form Grid Layout
export const FormGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

// Form Section
export const FormSection = styled.div`
  background: #f9fafb;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border: 1px solid #e5e7eb;
`;

export const SectionTitle = styled.h3`
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 0.5rem;

  &::before {
    content: '';
    width: 4px;
    height: 1.125rem;
    background: #3b82f6;
    border-radius: 2px;
  }
`;

// Button Styles
export const PrimaryButton = styled.button`
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s ease-in-out;
  display: flex;
  align-items: center;
  gap: 0.5rem;

  &:hover {
    background: #2563eb;
  }

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
`;

export const SecondaryButton = styled.button`
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
  display: flex;
  align-items: center;
  gap: 0.5rem;

  &:hover {
    background: #f9fafb;
    border-color: #9ca3af;
  }

  &:disabled {
    background: #f9fafb;
    color: #9ca3af;
    cursor: not-allowed;
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
`;

export const DangerButton = styled.button`
  background: #ef4444;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s ease-in-out;
  display: flex;
  align-items: center;
  gap: 0.5rem;

  &:hover {
    background: #dc2626;
  }

  &:disabled {
    background: #fca5a5;
    cursor: not-allowed;
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
  }
`;

// Card Styles
export const Card = styled.div`
  background: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
`;

export const CardHeader = styled.div`
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
`;

export const CardTitle = styled.h4`
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
`;

export const CardContent = styled.div`
  color: #6b7280;
`;

// Alert Styles
export const Alert = styled.div<{ type: 'success' | 'error' | 'warning' | 'info' }>`
  padding: 1rem;
  border-radius: 0.375rem;
  margin-bottom: 1rem;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;

  ${props => {
    switch (props.type) {
      case 'success':
        return `
          background: #d1fae5;
          border: 1px solid #a7f3d0;
          color: #065f46;
        `;
      case 'error':
        return `
          background: #fee2e2;
          border: 1px solid #fecaca;
          color: #991b1b;
        `;
      case 'warning':
        return `
          background: #fef3c7;
          border: 1px solid #fde68a;
          color: #92400e;
        `;
      case 'info':
      default:
        return `
          background: #dbeafe;
          border: 1px solid #bfdbfe;
          color: #1e40af;
        `;
    }
  }}
`;

export const AlertIcon = styled.div`
  flex-shrink: 0;
  margin-top: 0.125rem;
`;

export const AlertContent = styled.div`
  flex: 1;
`;

// Table Styles
export const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
`;

export const TableHeader = styled.th`
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
`;

export const TableCell = styled.td`
  padding: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
  color: #6b7280;
`;

export const TableRow = styled.tr`
  &:hover {
    background: #f9fafb;
  }
`;

// Loading Styles
export const LoadingSpinner = styled.div`
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 50%;
  border-top-color: #3b82f6;
  animation: spin 1s ease-in-out infinite;

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
`;

export const LoadingContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 0.75rem;
  color: #6b7280;
`;

// Utility Styles
export const FlexContainer = styled.div`
  display: flex;
  gap: 1rem;
  align-items: center;
`;

export const FlexColumn = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

export const Spacer = styled.div<{ size?: string }>`
  height: ${props => props.size || '1rem'};
  width: ${props => props.size || '1rem'};
`;

// Responsive helpers
export const HiddenOnMobile = styled.div`
  @media (max-width: 768px) {
    display: none;
  }
`;

export const VisibleOnMobile = styled.div`
  display: none;

  @media (max-width: 768px) {
    display: block;
  }
`;
