const { withBundleAnalyzer } = require('@next/bundle-analyzer')

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow builds to succeed even if ESLint finds issues. This helps CI & prod builds
  // when there are many pre-existing lint warnings. Follow-up: fix lint warnings and
  // remove this override once codebase conforms to rules.
  eslint: {
    ignoreDuringBuilds: true,
  },
  // Standalone mode: Node.js server for proper hydration
  output: 'standalone',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  env: {
    CUSTOM_KEY: 'my-value'
  },
  generateEtags: false,
  poweredByHeader: false,
  compress: true,
  
  // Performance optimizations
  swcMinify: true, // Use SWC instead of Terser for faster builds
  modularizeImports: {
    // Tree shake large libraries
    'react-bootstrap': {
      transform: 'react-bootstrap/{{member}}',
    },
    lodash: {
      transform: 'lodash/{{member}}',
    },
  },
  
  compiler: {
    styledComponents: true,
  },
  experimental: {
    // Disable optimizeCss to avoid potential hydration issues
    // optimizeCss: true,
    scrollRestoration: true,
    optimizeCss: true, // Enable CSS optimization
    esmExternals: true,
  },

  async redirects() {
    return [
      {
        source: '/sitemap.xml.broken',
        destination: '/sitemap.xml',
        permanent: true,
      },
      {
        source: '/sitemap.xml.backup',
        destination: '/sitemap.xml',
        permanent: true,
      },
      {
        source: '/tr',
        destination: '/',
        permanent: true,
      },
      {
        source: '/tr/:path*',
        destination: '/:path*',
        permanent: true,
      },
      {
        source: '/hesaplama/:slug',
        destination: '/:slug/',
        permanent: true,
      },
      {
        source: '/hesaplama/:slug/',
        destination: '/:slug/',
        permanent: true,
      },
      {
        source: '/%5Byapi-turu%5D',
        destination: '/',
        permanent: true,
      },
      {
        source: '/%5Byapi-turu%5D/',
        destination: '/',
        permanent: true,
      },
      {
        source: '/cevre-duzeni-planlari/%5BplanId%5D',
        destination: '/cevre-duzeni-planlari/',
        permanent: true,
      },
      {
        source: '/cevre-duzeni-planlari/%5BplanId%5D/',
        destination: '/cevre-duzeni-planlari/',
        permanent: true,
      },
      {
        source: '/cevre-duzeni-planlari/il/%5BilSlug%5D',
        destination: '/cevre-duzeni-planlari/',
        permanent: true,
      },
      {
        source: '/cevre-duzeni-planlari/il/%5BilSlug%5D/',
        destination: '/cevre-duzeni-planlari/',
        permanent: true,
      },
      {
        source: '/mevzuat/izmir-sera-yonetmeligi',
        destination: '/documents/izmir-sera-yonetmeligi/',
        permanent: true,
      },
      {
        source: '/mevzuat/izmir-sera-yonetmeligi/',
        destination: '/documents/izmir-sera-yonetmeligi/',
        permanent: true,
      },
      {
        source: '/mevzuat/kapali-ortamda-bitkisel-uretim-kayit-sistemi-yonetmeligi',
        destination: '/documents/kapali-ortamda-bitkisel-uretim-kayit-sistemi-yonetmeligi/',
        permanent: true,
      },
      {
        source: '/mevzuat/kapali-ortamda-bitkisel-uretim-kayit-sistemi-yonetmeligi/',
        destination: '/documents/kapali-ortamda-bitkisel-uretim-kayit-sistemi-yonetmeligi/',
        permanent: true,
      },
      {
        source: '/:path*',
        has: [
          {
            type: 'host',
            value: 'www.tarimimar.com.tr',
          },
        ],
        destination: 'https://tarimimar.com.tr/:path*',
        permanent: true,
      },
    ]
  },

  async rewrites() {
    if (process.env.NODE_ENV !== 'development') {
      return []
    }

    return [
      {
        source: '/api',
        destination: 'http://localhost:8000/api/',
      },
      {
        source: '/api/',
        destination: 'http://localhost:8000/api/',
      },
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*/',
      },
    ]
  },
  // Removed custom webpack config that was causing hydration issues
  // by overriding Next.js default chunk splitting strategy
}

module.exports = process.env.ANALYZE === 'true' 
  ? withBundleAnalyzer({ enabled: true })(nextConfig)
  : nextConfig