// Simple auth cookie utilities to sync auth state between React SPA (3001) and Next.js (3000)
// NOT: Localhost'ta farklı portlar arasında cookie paylaşımı mümkün değil

const getCookieDomain = (): string | undefined => {
  try {
    const host = window.location.hostname;
    // Production domain
    if (host.endsWith('tarimimar.com.tr')) return '.tarimimar.com.tr';
    // For localhost, omit domain attribute (her port kendi cookie'sine sahip)
    return undefined;
  } catch {
    return undefined;
  }
};

export const setAuthCookie = (email?: string, days = 7) => {
  try {
    const maxAge = days * 24 * 60 * 60; // seconds
    
    // Localhost için özel handling - port'lar arası cookie paylaşımı sağla
    const host = window.location.hostname;
    const attrs = [`path=/`, `SameSite=Lax`, `Max-Age=${maxAge}`];
    
    // Production'da domain ayarla
    const domain = getCookieDomain();
    if (domain) attrs.push(`Domain=${domain}`);

    console.log('🍪 Setting auth cookies:', { host, domain, email });

    // Minimal flag to indicate authenticated
    document.cookie = [`webimar_auth=1`, ...attrs].join('; ');

    // Optional user email for header display in Next.js
    if (email) {
      const safe = encodeURIComponent(email);
      document.cookie = [`webimar_user=${safe}`, ...attrs].join('; ');
    }
    
    console.log('✅ Cookies set, current cookies:', document.cookie);
  } catch (e) {
    console.warn('setAuthCookie error', e);
  }
};

export const clearAuthCookie = () => {
  try {
    const past = 'Thu, 01 Jan 1970 00:00:00 GMT';
    const attrs = [`path=/`, `expires=${past}`];
    const domain = getCookieDomain();
    if (domain) attrs.push(`Domain=${domain}`);

    document.cookie = [`webimar_auth=`, ...attrs].join('; ');
    document.cookie = [`webimar_user=`, ...attrs].join('; ');
  } catch (e) {
    console.warn('clearAuthCookie error', e);
  }
};

export const getCookie = (name: string): string | null => {
  try {
    const value = document.cookie
      .split('; ')
      .find((row) => row.startsWith(`${name}=`))
      ?.split('=')[1];
    return value ? decodeURIComponent(value) : null;
  } catch {
    return null;
  }
};
