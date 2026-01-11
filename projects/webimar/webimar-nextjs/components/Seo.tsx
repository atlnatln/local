import Head from 'next/head';
import React from 'react';

interface SeoProps {
  title: string;
  description: string;
  canonical?: string;
  url?: string;
  ogImage?: string;
  type?: string;
  jsonLd?: object | null;
  structuredData?: Record<string, unknown> | null;
  keywords?: string;
}

export default function Seo({
  title,
  description,
  canonical,
  url,
  ogImage = '/og-image.svg',
  type = 'website',
  jsonLd = null,
  structuredData = null,
  keywords = ''
}: SeoProps) {
  // Canonical URL normalization: her zaman trailing slash ile
  const normalizeUrl = (urlStr: string | undefined): string => {
    if (!urlStr) return '';
    // Trailing slash ekle (eğer yoksa)
    return urlStr.endsWith('/') ? urlStr : `${urlStr}/`;
  };
  
  const normalizedCanonical = normalizeUrl(canonical);
  const pageUrl = normalizedCanonical || normalizeUrl(url) || (typeof window !== 'undefined' ? normalizeUrl(window.location.href) : '');

  return (
    <Head>
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      {keywords && <meta name="keywords" content={keywords} />}

      {/* Canonical URL */}
      {normalizedCanonical && <link rel="canonical" href={normalizedCanonical} />}

      {/* Open Graph - Enhanced */}
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={pageUrl || ''} />
      <meta property="og:type" content={type} />
      <meta property="og:image" content={ogImage} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
      <meta property="og:site_name" content="Tarım İmar" />
      <meta property="og:locale" content="tr_TR" />

      {/* Twitter Card - Enhanced */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={ogImage} />
      <meta name="twitter:site" content="@tarimimar" />
      <meta name="twitter:creator" content="@tarimimar" />

      {/* Additional SEO Meta Tags */}
      <meta name="author" content="Tarım İmar" />
      <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />
      <meta name="googlebot" content="index, follow" />
      <meta name="theme-color" content="#2d5a27" />

      {/* Language and Region */}
      <meta httpEquiv="content-language" content="tr" />
      <meta name="geo.region" content="TR" />
      <meta name="geo.country" content="Türkiye" />

      {/* JSON-LD structured data */}
      {(structuredData || jsonLd) && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData || jsonLd) }}
        />
      )}
    </Head>
  );
}
