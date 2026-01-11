// Environment configuration utilities
// Automatically detects production/development and provides correct URLs

export const getEnvironment = () => {
  if (typeof window === 'undefined') return 'development'; // Server-side
  
  const hostname = window.location.hostname;
  
  // Production domain check
  if (hostname === 'tarimimar.com.tr' || hostname === 'www.tarimimar.com.tr') {
    return 'production';
  }
  
  // Development/local
  return 'development';
};

export const getNextJsUrl = () => {
  // Runtime detection - always use current origin for local development
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    
    // Production domain
    if (hostname === 'tarimimar.com.tr' || hostname === 'www.tarimimar.com.tr') {
      return 'https://tarimimar.com.tr';
    }
    
    // Local development - use current origin (works for both dev-local.sh and dev-docker.sh)
    // If REACT_APP_NEXTJS_URL is http://localhost:3000, use it (dev-local.sh)
    // Otherwise use window.location.origin (dev-docker.sh: http://localhost)
    const envUrl = process.env.REACT_APP_NEXTJS_URL;
    if (envUrl && envUrl.includes('3000')) {
      return envUrl; // dev-local.sh mode
    }
    return window.location.origin; // dev-docker.sh mode
  }
  
  // Fallback for SSR (not used in CRA but kept for safety)
  return process.env.REACT_APP_NEXTJS_URL || 'http://localhost:3000';
};

export const getApiBaseUrl = () => {
  // Runtime detection based on hostname
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    
    // Production domain
    if (hostname === 'tarimimar.com.tr' || hostname === 'www.tarimimar.com.tr') {
      return 'https://tarimimar.com.tr/api';
    }
    
    // Development/localhost - use current origin
    return `${window.location.origin}/api`;
  }
  
  // Fallback for SSR (not used in CRA but kept for safety)
  return process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
};

export const navigateToNextJs = (path: string = '/') => {
  const nextJsUrl = getNextJsUrl();
  const fullUrl = `${nextJsUrl}${path.startsWith('/') ? path : '/' + path}`;
  
  console.log(`🔄 Navigating to Next.js: ${fullUrl}`);
  window.location.href = fullUrl;
};

export const replaceToNextJs = (path: string = '/') => {
  const nextJsUrl = getNextJsUrl();
  const fullUrl = `${nextJsUrl}${path.startsWith('/') ? path : '/' + path}`;
  
  console.log(`🔄 Replacing to Next.js: ${fullUrl}`);
  window.location.replace(fullUrl);
};

// Debug info for development
export const getEnvironmentInfo = () => {
  return {
    environment: getEnvironment(),
    nextJsUrl: getNextJsUrl(),
    apiBaseUrl: getApiBaseUrl(),
    hostname: typeof window !== 'undefined' ? window.location.hostname : 'N/A'
  };
};
