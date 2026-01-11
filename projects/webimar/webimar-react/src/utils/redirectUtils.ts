/**
 * Login işlemleri için redirect utilities
 */

export const saveReturnUrl = (url?: string): void => {
  const currentUrl = url || window.location.pathname + window.location.search;
  
  // Login/register sayfalarında returnUrl saklamayalım
  if (currentUrl === '/login' || currentUrl === '/register' || currentUrl === '/auth/login' || currentUrl === '/auth/register') {
    return;
  }
  
  // Ana sayfa için de returnUrl saklamayalım
  if (currentUrl === '/' || currentUrl === '') {
    return;
  }
  
  // URL'i hem localStorage hem sessionStorage'a kaydet (çift güvenlik)
  localStorage.setItem('returnUrl', currentUrl);
  sessionStorage.setItem('returnUrl', currentUrl);
  
  console.log('🔗 Return URL saved:', currentUrl);
};

export const getReturnUrl = (): string | null => {
  return localStorage.getItem('returnUrl') || sessionStorage.getItem('returnUrl');
};

export const clearReturnUrl = (): void => {
  localStorage.removeItem('returnUrl');
  sessionStorage.removeItem('returnUrl');
  console.log('🗑️ Return URL cleared');
};

export const redirectToLoginWithReturn = (currentUrl?: string): void => {
  saveReturnUrl(currentUrl);
  window.location.href = '/login';
};

export const redirectToLogin = (): void => {
  window.location.href = '/login';
};
