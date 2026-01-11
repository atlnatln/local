import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { AuthProvider } from './AuthContext';

import { ToastProvider } from '../hooks/useToast';
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <ToastProvider>
      <AuthProvider>{children}</AuthProvider>
    </ToastProvider>
  );
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
) => render(ui, { wrapper: AllTheProviders, ...options });

export * from '@testing-library/react';
export { customRender as render };
