import React, { Suspense, lazy } from 'react';
import styled from 'styled-components';

// 🚀 OPTIMIZATION: Lazy load modal components for better bundle splitting
const LocationSelectionModalLazy = lazy(() => import('./Modals/LocationSelectionModal'));
const BuyukOvaModalLazy = lazy(() => import('./Modals/BuyukOvaModal'));
const SuTahsisModalLazy = lazy(() => import('./Modals/SuTahsisModal'));

// Loading spinner for lazy modals
const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  font-size: 14px;
  color: #666;
`;

// Wrapper component for lazy-loaded modals
interface LazyModalWrapperProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

const LazyModalWrapper: React.FC<LazyModalWrapperProps> = ({ 
  children, 
  fallback = <LoadingSpinner>Modal yükleniyor...</LoadingSpinner> 
}) => (
  <Suspense fallback={fallback}>
    {children}
  </Suspense>
);

// Pre-configured lazy modal components
export const LocationSelectionModalLazyWrapper: React.FC<React.ComponentProps<typeof LocationSelectionModalLazy>> = (props) => (
  <LazyModalWrapper>
    <LocationSelectionModalLazy {...props} />
  </LazyModalWrapper>
);

export const BuyukOvaModalLazyWrapper: React.FC<React.ComponentProps<typeof BuyukOvaModalLazy>> = (props) => (
  <LazyModalWrapper>
    <BuyukOvaModalLazy {...props} />
  </LazyModalWrapper>
);

export const SuTahsisModalLazyWrapper: React.FC<React.ComponentProps<typeof SuTahsisModalLazy>> = (props) => (
  <LazyModalWrapper>
    <SuTahsisModalLazy {...props} />
  </LazyModalWrapper>
);

export default LazyModalWrapper;
