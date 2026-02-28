import { useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Seo from '../components/Seo';

const ProfilePage = () => {
  const router = useRouter();

  useEffect(() => {
    // Client-side'da mevcut origin'i kullan
    const reactUrl = `${window.location.origin}/hesaplama/account`;
    console.log('🔄 Redirecting to React SPA profile:', reactUrl);
    window.location.href = reactUrl;
  }, []);

  return (
    <>
      <Seo
        title="Profil - Tarım İmar"
        description="Tarım İmar profil sayfası"
        canonical="https://tarimimar.com.tr/profile/"
        url="https://tarimimar.com.tr/profile/"
        ogImage="https://tarimimar.com.tr/og-image.svg"
        type="website"
        keywords="profil, hesap, tarım imar"
      />
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Profil sayfasına yönlendiriliyor...</p>
          <p className="mt-2 text-sm text-gray-500">
            {process.env.NODE_ENV === 'production' 
              ? 'Hesaplama sistemine yönlendiriliyorsunuz...' 
              : 'Geliştirme ortamına yönlendiriliyorsunuz...'}
          </p>
        </div>
      </div>
    </>
  );
};

export default ProfilePage;
