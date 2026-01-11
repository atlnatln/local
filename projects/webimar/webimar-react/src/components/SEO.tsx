import React from 'react';
import { Helmet } from 'react-helmet-async';

interface SEOProps {
  title: string;
  description: string;
  canonical?: string;
  keywords?: string;
  ogImage?: string;
}

const SEO: React.FC<SEOProps> = ({
  title,
  description,
  canonical,
  keywords,
  ogImage
}) => {
  const siteUrl = 'https://tarimimar.com.tr';
  
  // Canonical URL normalization: her zaman trailing slash ile
  const normalizeCanonical = (url: string): string => {
    if (url.startsWith('http')) {
      // Tam URL - trailing slash ekle
      return url.endsWith('/') ? url : `${url}/`;
    }
    // Relative path - trailing slash ile birleştir
    const path = url.startsWith('/') ? url : `/${url}`;
    return path.endsWith('/') ? path : `${path}/`;
  };
  
  const fullCanonical = canonical 
    ? (canonical.startsWith('http') 
        ? normalizeCanonical(canonical)
        : `${siteUrl}${normalizeCanonical(canonical)}`)
    : `${siteUrl}/`;

  return (
    <Helmet>
      <title>{title}</title>
      <meta name="description" content={description} />
      {keywords && <meta name="keywords" content={keywords} />}
      <link rel="canonical" href={fullCanonical} />
      
      {/* Open Graph Meta Tags */}
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={fullCanonical} />
      <meta property="og:type" content="website" />
      {ogImage && <meta property="og:image" content={ogImage} />}
      
      {/* Twitter Card Meta Tags */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      {ogImage && <meta name="twitter:image" content={ogImage} />}
    </Helmet>
  );
};

export default SEO;
