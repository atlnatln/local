import Document, { DocumentContext, Html, Head, Main, NextScript } from 'next/document';
import { ServerStyleSheet } from 'styled-components';

export default class MyDocument extends Document {
  static async getInitialProps(ctx: DocumentContext) {
    const sheet = new ServerStyleSheet();
    const originalRenderPage = ctx.renderPage;

    try {
      ctx.renderPage = () =>
        originalRenderPage({
          enhanceApp: (App) => (props) =>
            sheet.collectStyles(<App {...props} />),
        });

      const initialProps = await Document.getInitialProps(ctx);
      return {
        ...initialProps,
        styles: [initialProps.styles, sheet.getStyleElement()],
      };
    } finally {
      sheet.seal();
    }
  }

  render() {
    const structuredData = {
      "@context": "https://schema.org",
      "@type": "WebApplication",
      "name": "Tarım İmar - Tarımsal Arazilerde Yapılaşma Hesaplama Sistemi",
      "description": "Tarımsal arazilerde yapılaşma süreçlerinde güncel mevzuata ve bilimsel esaslara uygun, güvenilir ve hızlı hesaplama çözümleri.",
      "url": "https://tarimimar.com.tr",
      "applicationCategory": "BusinessApplication",
      "operatingSystem": "Web Browser",
      "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "TRY"
      },
      "creator": {
        "@type": "Organization",
        "name": "Tarım İmar",
        "url": "https://tarimimar.com.tr"
      },
      "potentialAction": {
        "@type": "UseAction",
        "target": "https://tarimimar.com.tr/hesaplama/",
        "description": "Tarımsal yapılaşma hesaplaması yapın"
      }
    };

    return (
      <Html lang="tr">
        <Head>
          <meta charSet="utf-8" />
          <meta name="google-site-verification" content="5NVBTnWmN3y7tnxHkX3HSiuAwfMao5XziUKiel6PgNw" />
          <link rel="icon" href="/favicon.ico" sizes="32x32" />
          <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
          <link rel="icon" href="/favicon-16x16.svg" sizes="16x16" type="image/svg+xml" />
          <link rel="icon" href="/favicon-32x32.svg" sizes="32x32" type="image/svg+xml" />
          {/* Canonical tag removed from global _document.tsx - must be set per page via Seo component */}
          <link rel="manifest" href="/manifest.json" />
          <link rel="apple-touch-icon" href="/apple-touch-icon.svg" />

          {/* Fonts: next/font (pages/_app.tsx) handles loading & preloading */}
          <meta name="theme-color" content="#D2691E" />
          <meta name="msapplication-TileColor" content="#8B4513" />

          {/* Google Analytics 4 - Performance Optimized */}
          {process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID && (
            <>
              <script
                dangerouslySetInnerHTML={{
                  __html: `
                    window.dataLayer = window.dataLayer || [];
                    function gtag(){dataLayer.push(arguments);}
                    gtag('js', new Date());
                    
                    // Lazy load GTM script after page interaction
                    function loadGTMScript() {
                      if (window.gtmLoaded) return;
                      window.gtmLoaded = true;
                      
                      const script = document.createElement('script');
                      script.async = true;
                      script.src = 'https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID}';
                      document.head.appendChild(script);
                      
                      script.onload = function() {
                        gtag('config', '${process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID}', {
                          page_title: document.title,
                          page_location: window.location.href,
                          send_page_view: true,
                          cookie_domain: 'tarimimar.com.tr',
                          cookie_flags: 'SameSite=None;Secure'
                        });
                      };
                    }
                    
                    // Load GTM on first user interaction
                    ['mousedown', 'touchstart', 'scroll'].forEach(event => {
                      document.addEventListener(event, loadGTMScript, { once: true, passive: true });
                    });
                    
                    // Fallback: load after 3 seconds if no interaction
                    setTimeout(loadGTMScript, 3000);
                  `,
                }}
              />
            </>
          )}

          {/* Open Graph / Facebook */}
          <meta property="og:type" content="website" />
          <meta property="og:site_name" content="Tarım İmar" />
          <meta property="og:title" content="Tarım İmar - Tarımsal Arazilerde Yapılaşma Hesaplama Sistemi" />
          <meta property="og:description" content="Tarımsal arazilerde yapılaşma süreçlerinde güncel mevzuata ve bilimsel esaslara uygun, güvenilir ve hızlı hesaplama çözümleri." />
          <meta property="og:url" content="https://tarimimar.com.tr" />
          <meta property="og:image" content="https://tarimimar.com.tr/og-image.svg" />
          <meta property="og:image:width" content="1200" />
          <meta property="og:image:height" content="630" />
          <meta property="og:locale" content="tr_TR" />

          {/* Twitter */}
          <meta name="twitter:card" content="summary_large_image" />
          <meta name="twitter:title" content="Tarım İmar - Tarımsal Arazilerde Yapılaşma Hesaplama Sistemi" />
          <meta name="twitter:description" content="Tarımsal arazilerde yapılaşma süreçlerinde güncel mevzuata ve bilimsel esaslara uygun, güvenilir ve hızlı hesaplama çözümleri." />
          <meta name="twitter:image" content="https://tarimimar.com.tr/og-image.svg" />

          {/* Additional SEO Meta Tags */}
          <meta name="robots" content="index, follow" />
          <meta name="googlebot" content="index, follow" />
          <meta name="author" content="Tarım İmar" />
          <meta name="publisher" content="Tarım İmar" />
          <meta name="keywords" content="tarım, yapılaşma, hesaplama, mevzuat, bağ evi, sera, hayvan barınağı, depo, lisanslı depo, soğuk hava deposu, gübre çukuru, toprak koruma, arazi kullanımı" />
          <meta name="theme-color" content="#d2691e" />
          <meta name="msapplication-TileColor" content="#d2691e" />

          {/* Structured Data */}
          <script
            type="application/ld+json"
            dangerouslySetInnerHTML={{
              __html: JSON.stringify(structuredData)
            }}
          />

          {/* Preconnect for performance */}
          <link rel="preconnect" href="https://www.google-analytics.com" />
          <link rel="preconnect" href="https://www.googletagmanager.com" />
          
          {/* Leaflet CSS - Local (Performance Optimized) */}
          <link rel="preload" href="/leaflet.css" as="style" />
          <link rel="stylesheet" href="/leaflet.css" />
        </Head>
        <body>
          <Main />
          <NextScript />
        </body>
      </Html>
    );
  }
}
