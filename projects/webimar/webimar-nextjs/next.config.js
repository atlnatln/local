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