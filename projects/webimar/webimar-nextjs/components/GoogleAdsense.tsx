import Script from 'next/script';

export default function GoogleAdsense() {
  // Replace with actual Client ID when available, for now using a placeholder or environment variable
  const clientId = process.env.NEXT_PUBLIC_ADSENSE_CLIENT_ID || 'ca-pub-XXXXXXXXXXXXXXXX'; 

  return (
    <Script
      strategy="afterInteractive"
      src={`https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${clientId}`}
      crossOrigin="anonymous"
    />
  );
}
