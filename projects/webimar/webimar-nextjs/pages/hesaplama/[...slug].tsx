import { useEffect } from 'react';
import { useRouter } from 'next/router';

// Hesaplama sayfaları için React SPA'ya redirect
export default function HesaplamaRedirect() {
  const router = useRouter();

  useEffect(() => {
    const { asPath } = router;
    
    // React SPA URL'ini env'den al, yoksa fallback
    const reactSpaUrl = process.env.NEXT_PUBLIC_REACT_SPA_URL || 'http://localhost:3001';
    
    // /hesaplama/* rotalarını React SPA'ya yönlendir
    if (asPath.startsWith('/hesaplama/')) {
      const reactPath = asPath.replace('/hesaplama/', '/');
      const fullUrl = `${reactSpaUrl}${reactPath}`;
      
      console.log(`🔄 Redirecting ${asPath} → ${fullUrl}`);
      window.location.href = fullUrl;
    }
  }, [router]);

  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h2>🔄 Hesaplama sayfasına yönlendiriliyorsunuz...</h2>
      <p>Lütfen bekleyin...</p>
    </div>
  );
}

export async function getServerSideProps(context: any) {
  const { params } = context;
  
  // Server-side redirect de yapabiliriz
  const reactSpaUrl = process.env.NEXT_PUBLIC_REACT_SPA_URL || 'http://localhost:3001';
  const reactPath = `/${params.slug.join('/')}`;
  
  return {
    redirect: {
      destination: `${reactSpaUrl}${reactPath}`,
      permanent: false,
    },
  };
}