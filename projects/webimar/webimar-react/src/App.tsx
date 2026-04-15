import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import AppLayout from './components/AppLayout';
import AnalyticsTracker from './components/AnalyticsTracker';
import HomePage from './pages/HomePage';
import CalculationPage from './pages/CalculationPage';
import AccountPage from './pages/AccountPage';
import GoogleCallback from './auth/GoogleCallback';
import LoginPage from './auth/LoginPage';
import LogoutPage from './auth/LogoutPage';
import RegisterPage from './auth/RegisterPage';
import { StructureType } from './types';
import { StructureTypesProvider, useStructureTypes } from './contexts/StructureTypesContext';
import { AuthProvider } from './auth';
import './App.css';

// Console log filtresi aktif et
import './utils/consoleLogFilter';

// Yapı türü descriptions mapping - Backend constants.py ile uyumlu 27 yapı türü
const getStructureDescription = (structureType: StructureType, structureTypeLabels: Record<StructureType, string>): string => {
  const descriptions: Record<StructureType, string> = {
    // Özel Üretim Tesisleri (ID: 1-4)
    'solucan-tesisi': 'Solucan ve solucan gübresi üretim tesisleri için yapı hesaplamalarını yapın.',
    'mantar-tesisi': 'Mantar üretim tesisleri için yapı hesaplamalarını yapın.',
    'sera': 'Seracılık tesisleri için yapı hesaplamalarını yapın.',
    'aricilik': 'Arı yetiştiriciliği ve bal üretimi tesisleri için hesaplamalar.',
    
    // Depolama ve İşleme Tesisleri (ID: 5-16)
    'hububat-silo': 'Hububat ve yem depolama siloları için yapı hesaplamalarını yapın.',
    'tarimsal-depo': 'Tarımsal amaçlı depolar için yapı hesaplamalarını yapın.',
    'lisansli-depo': 'Lisanslı depolar için yapı hesaplamalarını yapın.',
    'yikama-tesisi': 'Tarımsal ürün yıkama tesisleri için yapı hesaplamalarını yapın.',
    'kurutma-tesisi': 'Hububat, çeltik, ayçiçeği kurutma tesisleri için yapı hesaplamalarını yapın.',
    'meyve-sebze-kurutma': 'Açıkta meyve/sebze kurutma alanları için yapı hesaplamalarını yapın.',
    'zeytinyagi-fabrikasi': 'Zeytinyağı fabrikaları için yapı hesaplamalarını yapın.',
    'su-depolama': 'Su depolama tesisleri için yapı hesaplamalarını yapın.',
    'su-kuyulari': 'Su kuyuları için yapı hesaplamalarını yapın.',
    'bag-evi': 'Bağ evleri için yapı hesaplamalarını yapın.',
    'zeytinyagi-uretim-tesisi': 'Zeytinyağı üretim tesisleri için yapı hesaplamalarını yapın.',
    'soguk-hava-deposu': 'Soğuk hava depoları için yapı hesaplamalarını yapın.',
    
    // Hayvancılık Tesisleri (ID: 17-27)
    'sut-sigirciligi': 'Süt sığırı yetiştiriciliği tesisleri için yapı hesaplamalarını yapın.',
    'agil-kucukbas': 'Koyun, keçi ve benzeri küçükbaş hayvanlar için ağıl hesaplamalarını yapın.',
    'kumes-yumurtaci': 'Yumurtacı tavuk kümesleri için yapı hesaplamalarını yapın.',
    'kumes-etci': 'Etçi tavuk kümesleri için yapı hesaplamalarını yapın.',
    'kumes-gezen': 'Gezen tavuk kümesleri için yapı hesaplamalarını yapın.',
    'kumes-hindi': 'Hindi kümesleri için yapı hesaplamalarını yapın.',
    'kaz-ordek': 'Kaz ve ördek çiftlikleri için yapı hesaplamalarını yapın.',
    'hara': 'At yetiştiriciliği için hara tesisi hesaplamalarını yapın.',
    'ipek-bocekciligi': 'İpek böceği yetiştiriciliği tesisleri için hesaplamalar.',
    'evcil-hayvan': 'Evcil hayvan ve bilimsel araştırma hayvanı üretim tesisleri için hesaplamalar.',
    'besi-sigirciligi': 'Besi sığırı yetiştiriciliği tesisleri için yapı hesaplamalarını yapın.',
    
    // 2025 Yeni Yapılar (ID: 29-43)
    'fide-uretim': 'Fide üretim tesisleri için yapı hesaplamalarını yapın.',
    'fidan-uretim': 'Fidan üretim tesisleri için yapı hesaplamalarını yapın.',
    'sahipsiz-hayvan': 'Sahipsiz hayvan barınakları için yapı hesaplamalarını yapın.',
    'sundurma': 'Tarımsal amaçlı sundurma tesisleri için yapı hesaplamalarını yapın.',
    'ciftlik-atolyesi': 'Çiftlik atölyeleri için yapı hesaplamalarını yapın.',
    'su-urunleri': 'Su ürünleri üretim tesisleri için yapı hesaplamalarını yapın.',
    'deve-kusu': 'Deve kuşu üretim tesisleri için yapı hesaplamalarını yapın.',
    'gubre-deposu': 'Gübre depolama tesisleri için yapı hesaplamalarını yapın.',
    'mandira': 'Mandıra (süt sağım ve soğutma) tesisleri için yapı hesaplamalarını yapın.',
    'un-degirmeni': 'Un değirmeni tesisleri için yapı hesaplamalarını yapın.',
    'teleferik': 'Tarımsal amaçlı teleferik sistemleri için hesaplamalar.',
    'golet': 'Hayvan içme suyu göletleri için yapı hesaplamalarını yapın.',
    'islim': 'İslim ünitesi tesisleri için yapı hesaplamalarını yapın.',
    'muz-sarartma': 'Muz sarartma üniteleri için yapı hesaplamalarını yapın.',
    'tarimsal-arge': 'Tarımsal AR-GE tesisleri için yapı hesaplamalarını yapın.'
  };
  
  return descriptions[structureType] || `${structureTypeLabels[structureType]} için yapı hesaplamalarını yapın.`;
};

// App Routes component - dinamik yapı türleri ile
const AppRoutes: React.FC = () => {
  const { structureTypeLabels, loading } = useStructureTypes();

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <div>Yapı türleri yükleniyor...</div>
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/google/callback" element={<GoogleCallback />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/auth/register" element={<RegisterPage />} />
      <Route path="/logout" element={<LogoutPage />} />
      <Route path="/auth/logout" element={<LogoutPage />} />
      <Route path="/account" element={<AccountPage />} />
      {/* Calculation pages */}
      {Object.keys(structureTypeLabels).map((structureType) => {
        const type = structureType as StructureType;
        return (
          <Route
            key={type}
            path={`/${type}`}
            element={
              <CalculationPage
                calculationType={type}
                title={structureTypeLabels[type]}
                description={getStructureDescription(type, structureTypeLabels)}
              />
            }
          />
        );
      })}
    </Routes>
  );
};

const App: React.FC = () => {
  // Runtime environment variables kullan (window._webimar_env)
  // @ts-ignore
  const envVars = window._webimar_env || {};
  const configuredBasename = envVars.REACT_APP_ROUTER_BASENAME !== undefined 
    ? envVars.REACT_APP_ROUTER_BASENAME 
    : '/hesaplama';

  const basename = configuredBasename
    && typeof window !== 'undefined'
    && !window.location.pathname.startsWith(`${configuredBasename}/`)
    && window.location.pathname !== configuredBasename
      ? ''
      : configuredBasename;

  return (
    <HelmetProvider>
      <AuthProvider>
        <StructureTypesProvider>
          <Router
            basename={basename}
            future={{
              v7_startTransition: true,
              v7_relativeSplatPath: true
            }}
          >
            <AnalyticsTracker />
            <AppLayout>
              <AppRoutes />
            </AppLayout>
            <ToastContainer
              position="top-right"
              autoClose={5000}
              hideProgressBar={false}
              newestOnTop={false}
              closeOnClick
              rtl={false}
              pauseOnFocusLoss
              draggable
              pauseOnHover
              theme="light"
            />
          </Router>
        </StructureTypesProvider>
      </AuthProvider>
    </HelmetProvider>
  );
};

export default App;
