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
  experimental: {
    // Disable optimizeCss to avoid potential hydration issues
    // optimizeCss: true,
    scrollRestoration: true
  }
  // Removed custom webpack config that was causing hydration issues
  // by overriding Next.js default chunk splitting strategy
}

module.exports = process.env.ANALYZE === 'true' 
  ? withBundleAnalyzer({ enabled: true })(nextConfig)
  : nextConfig