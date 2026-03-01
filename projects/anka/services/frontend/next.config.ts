/** @type {import('next').NextConfig} */

// Backend URL for server-side rewrites (NOT the browser URL).
// Docker: "http://backend:8000"   (Docker DNS)
// Native: "http://localhost:8000"  (default)
const INTERNAL_BACKEND_URL =
  process.env.NEXT_INTERNAL_BACKEND_URL || 'http://localhost:8000';

const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  
  // API proxy configuration
  rewrites: async () => {
    return {
      beforeFiles: [
        // Proxy API requests to backend
        {
          source: '/api/:path*',
          destination: `${INTERNAL_BACKEND_URL}/api/:path*`,
        },
      ],
    };
  },

  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_ENVIRONMENT: process.env.NEXT_PUBLIC_ENVIRONMENT || 'development',
    NEXT_PUBLIC_GOOGLE_CLIENT_ID:
      process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID ||
      '201804658613-d8163rl6enjgc4anq38f9g5r1vsahnee.apps.googleusercontent.com',
    NEXT_PUBLIC_GOOGLE_MAPS_API_KEY:
      process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || '',
  },

  // Headers for security
  async headers() {
    return [
      {
        source: '/login',
        headers: [
          {
            key: 'Cross-Origin-Opener-Policy',
            value: 'same-origin-allow-popups',
          },
          {
            key: 'Cache-Control',
            value: 'no-store, no-cache, must-revalidate, max-age=0',
          },
          {
            key: 'Pragma',
            value: 'no-cache',
          },
          {
            key: 'Expires',
            value: '0',
          },
        ],
      },
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
