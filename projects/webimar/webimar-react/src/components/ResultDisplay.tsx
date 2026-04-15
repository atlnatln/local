import React, { useState, useRef, useLayoutEffect } from 'react';
import styled from 'styled-components';
import { CalculationResult, StructureType } from '../types';
import { useStructureTypes } from '../contexts/StructureTypesContext';
import { EmsalTuruContainer, EmsalTuruButton } from './CalculationForm/styles';
import SaveCalculationModal from './SaveCalculationModal';
import BuyukOvaModal from './Modals/BuyukOvaModal';
import { useAuth } from '../auth/AuthContext';

interface ResultDisplayProps {
  result: CalculationResult | null;
  isLoading: boolean;
  calculationType: StructureType;
  araziVasfi?: string; // Arazi vasfı bilgisi manuel kontrol butonu için
  onEmsalTypeChange?: (emsalType: string) => void; // Emsal türü değiştiğinde çağrılacak fonksiyon
  selectedEmsalType?: string; // Seçili emsal türü
  formData?: any; // Hesaplama parametreleri kaydetmek için
  mapCoordinates?: any; // Harita koordinatları kaydetmek için
  onRefreshHistory?: () => void; // History'yi refresh etmek için callback
}

const ResultContainer = styled.div`
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 4px;  /* Çerçevenin 3-4 piksel içinde olması için padding azaltıldı */
  margin-top: 24px;
  border: 1px solid #e5e7eb;
  
  @media (max-width: 768px) {
    margin: 24px -4px 0 -4px;  /* -8px yerine -4px kullanarak kahverengi çerçeveyi koruyoruz */
    border-radius: 8px;
    padding: 3px;  /* Mobilde padding'i biraz azaltıyoruz */
  }
`;

const ResultHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 16px;  /* Margin azaltıldı */
  padding: 20px 20px 16px 20px;  /* Üst, sağ, alt, sol padding eklendi */
  border-bottom: 2px solid #f3f4f6;
  gap: 8px;  /* İkon ve metin arasında sabit boşluk */
  
  @media (max-width: 768px) {
    padding: 12px 12px 8px 12px;  /* Yan padding'i artırdık */
    margin-bottom: 8px;
    gap: 6px;
  }
`;

const ResultIcon = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #10b981, #059669);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;  /* İkonun küçülmesini önler */
  
  @media (max-width: 768px) {
    width: 40px;
    height: 40px;
  }
  
  &::after {
    content: '✓';
    color: white;
    font-size: 24px;
    font-weight: bold;
    
    @media (max-width: 768px) {
      font-size: 20px;
    }
  }
`;

const ResultTitle = styled.h2`
  color: #111827;
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  flex: 1;  /* Kalan alanı kaplar */
  
  @media (max-width: 768px) {
    font-size: 20px;
  }
`;

const ResultSubtitle = styled.p`
  color: #6b7280;
  font-size: 14px;
  margin: 4px 0 0 0;
  
  @media (max-width: 768px) {
    font-size: 13px;
    margin: 2px 0 0 0;
  }
`;

const LoadingContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #6b7280;
`;

const LoadingSpinner = styled.div`
  width: 32px;
  height: 32px;
  border: 3px solid #f3f4f6;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 12px;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ResultContent = styled.div`
  padding: 0 20px 20px 20px;  /* Sağ, sol, alt padding eklendi */
  
  @media (max-width: 768px) {
    padding: 0 8px 8px 8px;
  }
  
  /* Ham HTML mesaj kartlarını gizlemek için genel style */
  .hidden-detail-message {
    display: none !important;
  }
`;

const ResultGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 20px;
  
  @media (max-width: 768px) {
    margin: 20px -4px 0 -4px;  /* -8px yerine -4px kullanarak kahverengi çerçeveyi koruyoruz */
    gap: 16px;
    grid-template-columns: 1fr;
  }
`;

const ResultCard = styled.div`
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
    transform: translateY(-2px);
  }
`;

const ResultLabel = styled.h3`
  color: #374151;
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px 0;
`;

const ResultValue = styled.div`
  color: #111827;
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
`;

const ResultDescription = styled.p`
  color: #6b7280;
  font-size: 14px;
  margin: 8px 0 0 0;
  line-height: 1.5;
`;

const ErrorContainer = styled.div`
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 16px;
  margin-top: 20px;
`;

const ErrorTitle = styled.h3`
  color: #dc2626;
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px 0;
`;

const LocationInfoContainer = styled.div`
  background: #fef7cd;
  border: 1px solid #fed7aa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
`;

const LocationIcon = styled.div`
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #f59e0b;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
  
  &::after {
    content: '📍';
    font-size: 14px;
  }
`;

const LocationMessage = styled.p`
  color: #92400e;
  font-size: 14px;
  font-weight: 500;
  margin: 0;
  line-height: 1.5;
`;

const ErrorMessage = styled.p`
  color: #7f1d1d;
  font-size: 14px;
  margin: 0;
`;

const ManuelKontrolButton = styled.button`
  background: linear-gradient(135deg, #059669, #10b981);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  
  &:hover {
    background: linear-gradient(135deg, #047857, #059669);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const SaveButton = styled.button`
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  margin: 20px 0;
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  justify-content: center;
  
  &:hover {
    background: linear-gradient(135deg, #059669, #047857);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

// Backend constants.py ile senkronize yapı türü display isimleri - artık context'ten geliyor
const getCalculationTypeDisplayName = (type: StructureType, structureTypeLabels: Record<StructureType, string>): string => {
  return structureTypeLabels[type] || type;
};

// Dinamik alan konfigürasyonu
interface FieldConfig {
  key: string | string[]; // Tek alan veya alternatif alanlar
  label: string;
  unit: string;
  description: string;
  formatter?: (value: any, data?: any) => string;
  condition?: (data: any) => boolean;
}

const fieldConfigs: FieldConfig[] = [
  // Teknik detay alanlarını kaldırdık: kapasite, arazi_alani/alan_m2, maksimum_emsal, emsal_orani
  // Kullanıcı dostu görüntüleme için sadece anlamlı alanlar bırakıldı
  {
    key: 'yapi_alani',
    label: 'Yapı Alanı',
    unit: 'm²',
    description: 'İnşa edilebilecek maksimum yapı alanı'
  },
  {
    key: 'insaat_alani',
    label: 'İnşaat Alanı',
    unit: 'm²',
    description: 'Toplam inşaat alanı'
  },
  {
    key: 'sera_alani',
    label: 'Sera Alanı',
    unit: 'm²',
    description: 'Kurulabilecek sera alanı'
  },
  {
    key: ['depolama_kapasitesi', 'depo_alani'],
    label: 'Depo Alanı',
    unit: '',
    description: '',
    formatter: (value: any, data: any) => {
      if (data.depolama_kapasitesi) {
        return `${formatNumber(data.depolama_kapasitesi)} ton`;
      }
      if (data.depo_alani) {
        return `${formatNumber(data.depo_alani)} m²`;
      }
      return `${formatNumber(value)} m²`;
    },
    condition: (data: any) => data.depolama_kapasitesi || data.depo_alani
  },
  {
    key: 'silo_kapasitesi',
    label: 'Silo Kapasitesi',
    unit: 'ton',
    description: 'Silo depolama kapasitesi'
  },
  {
    key: 'soguk_depo_kapasitesi',
    label: 'Soğuk Depo Kapasitesi',
    unit: 'ton',
    description: 'Soğuk depo kapasitesi'
  },
  {
    key: 'uretim_kapasitesi',
    label: 'Üretim Kapasitesi',
    unit: 'kg/yıl',
    description: 'Yıllık üretim kapasitesi'
  },
  {
    key: 'kovan_sayisi',
    label: 'Maksimum Kovan Sayısı',
    unit: 'adet',
    description: 'Kurulabilecek maksimum kovan sayısı'
  },
  {
    key: 'havuz_alani',
    label: 'Havuz Alanı',
    unit: 'm²',
    description: 'Su ürünleri havuz alanı'
  },
  {
    key: 'maksimum_insaat_alani',
    label: 'Maksimum İnşaat Alanı',
    unit: 'm²',
    description: 'Bağ evi için maksimum inşaat alanı'
  },
  {
    key: 'taban_alani',
    label: 'Maksimum Taban Alanı',
    unit: 'm²',
    description: 'Bağ evi için maksimum taban alanı'
  },
  {
    key: 'uretim_alani',
    label: 'Üretim Alanı',
    unit: 'm²',
    description: 'Aktif üretim alanı'
  },
  {
    key: 'kalan_emsal',
    label: 'Kalan Emsal Hakkı',
    unit: 'm²',
    description: 'Müştemilatlar (araç yolu, idari bina, laboratuvar vb.) için kullanılabilir alan'
  }
];

const getFieldValue = (data: any, key: string | string[]): any => {
  if (Array.isArray(key)) {
    for (const k of key) {
      if (data[k] !== undefined && data[k] !== null) {
        return data[k];
      }
    }
    return null;
  }
  return data[key];
};

const renderFieldCards = (data: any) => {
  return fieldConfigs.map((config, index) => {
    const value = getFieldValue(data, config.key);
    
    // Alan yoksa veya koşul sağlanmıyorsa gösterme
    if (!value && value !== 0) return null;
    if (config.condition && !config.condition(data)) return null;
    
    // Özel formatter varsa kullan
    const formattedValue = config.formatter 
      ? config.formatter(value, data)
      : `${formatNumber(value)} ${config.unit}`;
    
    // Açıklama için özel mantık
    let description = config.description;
    if (Array.isArray(config.key) && config.key.includes('depolama_kapasitesi') && config.key.includes('depo_alani')) {
      description = data.depolama_kapasitesi ? 'Maksimum depolama kapasitesi' : 'Depo taban alanı';
    }
    
    return (
      <ResultCard key={`field-${index}`}>
        <ResultLabel>{config.label}</ResultLabel>
        <ResultValue>
          {formattedValue}
        </ResultValue>
        <ResultDescription>
          {description}
        </ResultDescription>
      </ResultCard>
    );
  }).filter(Boolean);
};

const formatNumber = (value: number | string): string => {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return value.toString();
  
  return new Intl.NumberFormat('tr-TR', {
    maximumFractionDigits: 2
  }).format(num);
};

const formatResultKey = (key: string): string => {
  const keyMap: Record<string, string> = {
    // Bağ evi sonuçları
    'maksimum_insaat_alani': 'Maksimum İnşaat Alanı',
    'maksimum_taban_alani': 'Maksimum Taban Alanı',
    'taban_alani': 'Maksimum Taban Alanı',
    'insaat_alani': 'Maksimum İnşaat Alanı',
    'emsal_orani': 'Emsal Oranı',
    'toplam_alan': 'Toplam Alan',
    'dikili_alan': 'Dikili Alan',
    'tarla_alan': 'Tarla Alanı',
    'zeytinlik_alan': 'Zeytinlik Alanı',
    'kalan_emsal': 'Kalan Emsal',
    'maksimum_emsal': 'Maksimum Emsal',
    
    // Genel sonuçlar
    'alan_m2': 'Toplam Alan',
    'arazi_alani': 'Arazi Alanı',
    'yapi_alani': 'Yapı Alanı',
    'kapasite': 'Kapasite',
    'depo_alani': 'Depo Alanı',
    'depolama_kapasitesi': 'Depolama Kapasitesi',
    'uretim_kapasitesi': 'Üretim Kapasitesi',
    'silo_kapasitesi': 'Silo Kapasitesi'
  };
  
  return keyMap[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const formatResultValue = (value: any, key: string): string => {
  if (typeof value === 'number') {
    // Özel formatlar
    if (key.includes('orani')) {
      return `%${formatNumber(value * 100)}`;
    }
    if (key.includes('kapasite') && key.includes('depolama')) {
      return `${formatNumber(value)} ton`;
    }
    if (key.includes('alan')) {
      return `${formatNumber(value)} m²`;
    }
    return formatNumber(value);
  }
  
  if (typeof value === 'boolean') {
    return value ? 'Evet' : 'Hayır';
  }
  
  // Object render hatası düzeltmesi
  if (typeof value === 'object' && value !== null) {
    if (Array.isArray(value)) {
      return value.join(', ');
    }
    // Object'i JSON string olarak göster
    return JSON.stringify(value, null, 2);
  }
  
  return String(value);
};

const getResultDescription = (key: string): string => {
  const descriptions: Record<string, string> = {
    'maksimum_insaat_alani': 'Mevzuata göre yapılabilecek maksimum inşaat alanı',
    'maksimum_taban_alani': 'Bağ evinin maksimum taban alanı (75 m²)',
    'taban_alani': 'Bağ evinin maksimum taban alanı',
    'insaat_alani': 'Toplam yapılaşma alanı',
    'emsal_orani': 'Uygulanan emsal oranı',
    'toplam_alan': 'Parselin toplam alanı',
    'kalan_emsal': 'Müştemilatlar için kullanılabilir alan',
    'maksimum_emsal': 'İzin verilen maksimum yapılaşma alanı'
  };
  
  return descriptions[key] || 'Hesaplama sonucu';
};

const ResultDisplay: React.FC<ResultDisplayProps> = ({ 
  result, 
  isLoading, 
  calculationType, 
  araziVasfi, 
  onEmsalTypeChange,
  selectedEmsalType,
  formData,
  mapCoordinates,
  onRefreshHistory
}) => {
  const { structureTypeLabels } = useStructureTypes();
  const { state: { isAuthenticated } } = useAuth();
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showBuyukOvaModal, setShowBuyukOvaModal] = useState(false);
  const resultContentRef = useRef<HTMLDivElement>(null);

    // Sadece HTML içeriğindeki "Büyük Ova Mesajı", "Mesaj Metin" ve "Detay Mesaji" bileşenlerini gizle (turuncu modal'e dokunma)
  useLayoutEffect(() => {
    if (resultContentRef.current && result?.data) {
      const hideBuyukOvaMessage = () => {
        // Tüm h3 elementlerini kontrol et
        const h3Elements = resultContentRef.current!.querySelectorAll('h3');
        h3Elements.forEach((h3) => {
          const h3Text = h3.textContent?.trim();
          if (h3Text === 'Buyuk Ova Mesaji' || h3Text === 'Mesaj Metin' || h3Text === 'Detay Mesaji') {
            // Bu h3'ün direct parent div'ini bul ve gizle
            let parentDiv = h3.parentElement;
            
            // İlk parent div'i gizle (sc-fJtJci labDuu gibi) - CSS class da ekle
            if (parentDiv && parentDiv.classList.length > 0) {
              (parentDiv as HTMLElement).style.display = 'none';
              parentDiv.classList.add('hidden-detail-message');
              
              // Eğer hala görünüyorsa, onun da parent'ını gizle (sc-jaRLub hdKFcG gibi)
              const grandParentDiv = parentDiv.parentElement;
              if (grandParentDiv && grandParentDiv.classList.length > 0) {
                const hasOtherContent = Array.from(grandParentDiv.children).some(child => 
                  child !== parentDiv && (child as HTMLElement).style.display !== 'none'
                );
                if (!hasOtherContent) {
                  (grandParentDiv as HTMLElement).style.display = 'none';
                  grandParentDiv.classList.add('hidden-detail-message');
                }
              }
            }
          }
        });
      };
      
      // DOM güncellendiğinde hemen çalıştır (layout'dan önce)
      hideBuyukOvaMessage();
      
      // Backup için minimal timeout da ekle
      const timer = setTimeout(hideBuyukOvaMessage, 50);
      return () => clearTimeout(timer);
    }
  }, [result?.data]);

  // Ek optimizasyon: result değiştiğinde hemen gizle
  useLayoutEffect(() => {
    if (resultContentRef.current) {
      // HTML inject edilmeden önce potansiyel elementleri gizle
      const preHideElements = () => {
        const allDivs = resultContentRef.current!.querySelectorAll('div');
        allDivs.forEach((div) => {
          const h3Child = div.querySelector('h3');
          if (h3Child) {
            const h3Text = h3Child.textContent?.trim();
            if (h3Text === 'Buyuk Ova Mesaji' || h3Text === 'Mesaj Metin' || h3Text === 'Detay Mesaji') {
              (div as HTMLElement).style.display = 'none';
              div.classList.add('hidden-detail-message');
            }
          }
        });
      };
      
      // Immediate ve micro-task'da çalıştır
      preHideElements();
      Promise.resolve().then(preHideElements);
    }
  }, [result]);
  
  const handleSaveCalculation = () => {
    setShowSaveModal(true);
  };
  
  const handleSaveSuccess = () => {
    setShowSaveModal(false);
    // Başarılı kayıt sonrası gerekirse refreshHistory gibi callback çağırılabilir
  };

  console.log('🖼️ ResultDisplay props:', { result, isLoading, calculationType });

  if (isLoading) {
    console.log('⏳ Showing loading state');
    return (
      <ResultContainer>
        <LoadingContainer>
          <LoadingSpinner />
          <span>Hesaplama yapılıyor...</span>
        </LoadingContainer>
      </ResultContainer>
    );
  }

  if (!result) {
    console.log('❌ No result to display');
    return (
      <ResultContainer>
        <div style={{ 
          padding: '40px', 
          textAlign: 'center', 
          color: '#6b7280',
          fontSize: '16px'
        }}>
          Hesaplama yapmak için formu doldurun ve "Hesapla" butonuna tıklayın.
        </div>
      </ResultContainer>
    );
  }

  if (!result.success) {
    // Backend'den gelen detaylı mesajı kullan
    const detailedMessage = result.data?.results?.mesaj || result.data?.results?.ana_mesaj || result.data?.results?.detay_mesaji || result.data?.mesaj || result.data?.ana_mesaj || result.data?.detay_mesaji || result.message;
    console.log('💥 Showing error result:', detailedMessage);
    return (
      <ResultContainer>
        <ErrorContainer>
          <ErrorMessage dangerouslySetInnerHTML={{ __html: detailedMessage || 'Hesaplama başarısız oldu.' }} />
        </ErrorContainer>
      </ResultContainer>
    );
  }

  // Double-check: Eğer backend'den success false gelmişse hiçbir şekilde success render etme
  if (!result.success) {
    const detailedMessage = result.data?.results?.mesaj || result.data?.results?.ana_mesaj || result.data?.results?.detay_mesaji || result.data?.mesaj || result.data?.ana_mesaj || result.data?.detay_mesaji || result.message;
    console.log('🚫 Double-check: Backend returned success: false, not rendering success result');
    return (
      <ResultContainer>
        <ErrorContainer>
          <ErrorMessage dangerouslySetInnerHTML={{ __html: detailedMessage || 'Hesaplama başarısız oldu.' }} />
        </ErrorContainer>
      </ResultContainer>
    );
  }

  const data = result.data;
  console.log('✨ Rendering successful result with data:', data);

  // Backend'den gelen nested results object'lerini data'ya merge et
  const mergedData = { 
    ...data, 
    ...(data.results || {}),
    ...(data.results?.results || {}), // EKLENDI: İç içe results objesini de merge et
    // Ana mesajı nested results'tan da alabilir
    ana_mesaj: data.results?.results?.ana_mesaj || data.results?.ana_mesaj || data.ana_mesaj,
    mesaj: data.results?.results?.mesaj || data.results?.mesaj || data.mesaj,
    html_mesaj: data.results?.results?.html_mesaj || data.results?.html_mesaj || data.html_mesaj,
    izin_durumu: data.results?.results?.izin_durumu || data.results?.izin_durumu || data.izin_durumu
  };

  // Debug için büyük ova mesajını kontrol et
  console.log('DEBUG: data:', data);
  console.log('DEBUG: data.results:', data.results);
  console.log('DEBUG: mergedData.buyuk_ova_mesaji:', mergedData.buyuk_ova_mesaji);

  // İzin durumu için backend detaylarındaki değeri kullan
  const izinDurumu = mergedData.detaylar?.izin_durumu || mergedData.izin_durumu;

  return (
    <ResultContainer>
      <ResultHeader>
        <ResultIcon />
        <div>
          <ResultTitle>{getCalculationTypeDisplayName(calculationType, structureTypeLabels)} Hesaplama Sonucu</ResultTitle>
          <ResultSubtitle>Hesaplama başarıyla tamamlandı</ResultSubtitle>
        </div>
      </ResultHeader>
      
      <ResultContent ref={resultContentRef}>
        {/* Büyük ova konumu uyarısı (turuncu modal) */}
        {mergedData.buyuk_ova_mesaji && (
          <LocationInfoContainer>
            <LocationIcon />
            <div>
              <LocationMessage>{mergedData.buyuk_ova_mesaji}</LocationMessage>
              <button
                onClick={() => setShowBuyukOvaModal(true)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#92400e',
                  textDecoration: 'underline',
                  cursor: 'pointer',
                  fontSize: '14px',
                  padding: '4px 0',
                  marginTop: '8px',
                  display: 'block'
                }}
              >
                ⓘ Detaylı bilgi için tıklayın
              </button>
            </div>
          </LocationInfoContainer>
        )}
        
        <ResultGrid>
          {/* Dinamik alan kartları */}
          {renderFieldCards(mergedData)}
          
          {/* Backend'den gelen results object'indeki bilgileri göster (büyük ova mesajıyla uyumlu) */}
          {mergedData.results && typeof mergedData.results === 'object' && (
            <>
              {Object.entries(mergedData.results).map(([key, value]) => {
                // Exclude common non-displayable fields ve location info'yu da dahil et
                if (['success', 'message', 'data', 'ana_mesaj', 'mesaj', 'html_mesaj', 'izin_durumu', 'hesaplama_tipi', 'location_info', '_debug', 'detaylar', 'debug_info'].includes(key)) return null;
                
                // Teknik detay alanlarını filtrele (kullanıcı talebi - "bu bileşeni tüm hesaplama sonuçlarından çıkaralım")
                if (['kapasite', 'maksimum_kapasite', 'arazi_buyuklugu_m2', 'emsal_m2', 'maksimum_emsal', 'emsal_orani', 'arazi_alani', 'alan_m2', 'sonuc', 'maksimum_sera_alani', 'toplam_yapi_alani_m2', 'kalan_emsal_m2', 'uygulanan_kural', 'hesaplama_kurali_aciklama', 'yapilanabilir', 'arazi_alani_m2', 'silo_taban_alani_m2', 'maksimum_emsal_alani_m2', 'html_content', 'mevcut_alan_m2', 'gerekli_minimum_alan_m2', 'sorun_detay', 'neden', 'maksimum_insaat_alani_m2', 'kalan_emsal_hakki_m2', 'maksimum_yikama_alani_m2', 'maksimum_kurutma_alani_m2', 'fabrika_uretim_alani_m2', 'emsal_kullanim_orani', 'su_depolama_pompaj_alani_m2', 'emsal_tipi', 'detay_mesaj', 'alan_dagilimi', 'soguk_depo_kapasitesi_ton', 'bakici_evi_hakki', 'planlamai_kurulu_uyari', 'hayvan_tipi', 'uretim_tipi', 'kumes_alani_m2', 'mustemilat_alani_m2', 'gezinti_alani_kapasitesi', 'emsal_kapasitesi', 'belirleyici_kisit', 'maksimum_yapilasma_alani_m2', 'min_arazi_sarti_saglandi_mi', 'dut_bahcesi_var_mi', 'uyari_mesaji_ozel_durum', 'sonraki_adim_bilgisi', 'bakici_evi_m2', 'idari_bina_m2', 'uretim_alani_m2', 'depo_alani_m2', 'cekim_odasi_alani_m2', 'kutu_sayisi', 'beslenebilecek_kutu_sayisi', 'toplam_yaprak_ihtiyaci_kg', 'toplam_yas_koza_kg', 'emsal_orani_yuzde', 'maksimum_depo_alani', 'min_alan_sarti', 'zeytin_kontrol', 'depolama_kapasitesi_ton', 'kapali_su_havzasi_icinde', 'aciklama', 'toplam_arazi_varligi', 'depo_hakki_m2', 'depo_hakki_dekar', 'yapilar', 'kapali_alan_m2', 'gezinti_alani_m2', 'kuluckahane_m2', 'civciv_buyutme_m2', 'yem_deposu_m2', 'idari_bina_hakki'].includes(key)) return null;
                
                if (value === null || value === undefined || value === '') return null;
                
                // Location info object'inin içeriğini de filtrele
                if (typeof value === 'object' && value !== null) {
                  // Eğer object içinde coordinates, buyuk_ova_icinde gibi location bilgileri varsa gösterme
                  const locationObject = value as any;
                  if (locationObject.coordinates || locationObject.buyuk_ova_icinde || locationObject.izmir_icinde || locationObject.location_valid) {
                    return null;
                  }
                }
                
                // Büyük ova çelişkisi düzeltmesi - buyuk_ova_icerisinde değerini mesajla uyumlu hale getir
                let displayValue = value;
                if (key === 'buyuk_ova_icerisinde' && mergedData.buyuk_ova_mesaji) {
                  // Eğer mesajda "içerisinde bulunmaktadır" yazıyorsa true olmalı
                  if (mergedData.buyuk_ova_mesaji.includes('içerisinde bulunmaktadır')) {
                    displayValue = true;
                  }
                }
                
                return (
                  <ResultCard key={`results-${key}`}>
                    <ResultLabel>{formatResultKey(key)}</ResultLabel>
                    <ResultValue>
                      {formatResultValue(displayValue, key)}
                    </ResultValue>
                    <ResultDescription>
                      {getResultDescription(key)}
                    </ResultDescription>
                  </ResultCard>
                );
              })}
            </>
          )}
        </ResultGrid>


      {/* Emsal Türü Seçimi - ipek böcekçiliği için asla gösterilmez */}
      {calculationType !== 'bag-evi' && calculationType !== 'sera' && calculationType !== 'zeytinyagi-fabrikasi' && calculationType !== 'su-kuyulari' && calculationType !== 'ipek-bocekciligi' && onEmsalTypeChange && (
        <ResultCard style={{ 
          marginTop: '16px',
          padding: '20px'
        }}>
          <ResultLabel style={{ marginBottom: '12px' }}>
            Emsal Türü Seçimi
          </ResultLabel>
          <EmsalTuruContainer>
            <EmsalTuruButton
              type="button"
              $isSelected={(selectedEmsalType || 'marjinal') === 'marjinal'}
              onClick={() => {
                if (onEmsalTypeChange) onEmsalTypeChange('marjinal');
              }}
            >
              <div className="emsal-title">🏜️ Marjinal Alan</div>
              <div className="emsal-percentage">%20</div>
              <div className="emsal-subtitle">Marjinal tarım arazileri için emsal</div>
            </EmsalTuruButton>
            
            <EmsalTuruButton
              type="button"
              $isSelected={(selectedEmsalType || 'marjinal') === 'mutlak_dikili'}
              onClick={() => {
                if (onEmsalTypeChange) onEmsalTypeChange('mutlak_dikili');
              }}
            >
              <div className="emsal-title">🌱 Mutlak & Dikili Alan</div>
              <div className="emsal-percentage">%5</div>
              <div className="emsal-subtitle">Mutlak tarım arazisi, dikili tarım arazisi ve özel ürün arazileri için emsal</div>
            </EmsalTuruButton>
          </EmsalTuruContainer>
          <ResultDescription style={{ marginTop: '12px', textAlign: 'center', fontStyle: 'italic' }}>
            Emsal türünü değiştirdiğinizde hesaplamalar otomatik olarak güncellenir
          </ResultDescription>
        </ResultCard>
      )}

      {/* Detaylı HTML Mesajı - Backend'den gelen ana_mesaj */}
      {(() => {
        const hasMessage = mergedData.ana_mesaj || mergedData.mesaj || mergedData.html_mesaj;
        console.log('🔍 ResultDisplay - Ana mesaj kontrol:', {
          hasMessage: !!hasMessage,
          ana_mesaj: !!mergedData.ana_mesaj,
          mesaj: !!mergedData.mesaj,
          html_mesaj: !!mergedData.html_mesaj,
          message_length: hasMessage ? hasMessage.length : 0,
          // Debug: Tüm results seviyelerini kontrol et
          'data.results?.results?.ana_mesaj': !!result?.data?.results?.results?.ana_mesaj,
          'data.results?.results?.mesaj': !!result?.data?.results?.results?.mesaj
        });
        return null;
      })()}
      {(mergedData.ana_mesaj || mergedData.mesaj || mergedData.html_mesaj) && (
        <ResultCard style={{ marginTop: '20px', padding: '0' }}>
          <div 
            style={{ padding: '20px' }}
            dangerouslySetInnerHTML={{ __html: mergedData.ana_mesaj || mergedData.mesaj || mergedData.html_mesaj || '' }}
          />
        </ResultCard>
      )}

      {/* Bağ evi varsayımsal sonuç için manuel kontrol butonu - "Zeytin ağaçlı + tarla" için gizle */}
      {/* Manuel kontrol zaten yapıldıysa da gizle */}
      {calculationType === 'bag-evi' && 
       izinDurumu === 'izin_verilebilir_varsayimsal' && 
       araziVasfi !== 'Zeytin ağaçlı + tarla' &&
       !(mergedData.ana_mesaj || mergedData.mesaj || mergedData.html_mesaj || '').includes('Bu hesaplama manuel alan kontrolünüz temel alınarak yapılmıştır') && (
        <ResultCard style={{ 
          marginTop: '16px', 
          background: 'linear-gradient(135deg, #eff6ff, #dbeafe)',
          border: '2px solid #3b82f6',
          textAlign: 'center'
        }}>
          <div style={{ marginBottom: '16px' }}>
            <div style={{ 
              fontSize: '16px', 
              fontWeight: '600', 
              color: '#1d4ed8',
              marginBottom: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}>
              <span>🎯</span>
              <span>Kesin Sonuç İçin Manuel Kontrol</span>
            </div>
            <div style={{ 
              fontSize: '14px', 
              color: '#1e40af',
              lineHeight: '1.5'
            }}>
              Kesin sonuç için <strong>manuel alan kontrolü</strong> yapmanız önerilir.
            </div>
          </div>
          
          <ManuelKontrolButton
            onClick={() => {
              // Dikili alan kontrolü modalını aç
              const event = new CustomEvent('openDikiliKontrol');
              window.dispatchEvent(event);
            }}
          >
            <span>🌳</span>
            <span>Manuel Alan Kontrolü Başlat</span>
            <span>→</span>
          </ManuelKontrolButton>
          
          <div style={{ 
            fontSize: '12px', 
            color: '#64748b', 
            marginTop: '12px',
            fontStyle: 'italic'
          }}>
            Manuel kontrol sonucuna göre hesaplama otomatik olarak güncellenecektir
          </div>
        </ResultCard>
      )}

      {/* Ek Bilgiler */}
      {mergedData.aciklama && (
        <ResultCard style={{ marginTop: '20px' }}>
          <ResultLabel>Açıklama</ResultLabel>
          <ResultDescription style={{ marginTop: '8px', fontSize: '16px' }}>
            {mergedData.aciklama}
          </ResultDescription>
        </ResultCard>
      )}
      </ResultContent>
      
      {/* Hesaplamayı Kaydet Butonu - Sadece giriş yapan kullanıcılar için */}
      {isAuthenticated && (
        <SaveButton onClick={handleSaveCalculation}>
          <span>💾</span>
          <span>Hesaplamayı Kaydet</span>
        </SaveButton>
      )}
      
      {/* Save Calculation Modal */}
      {showSaveModal && (
        <SaveCalculationModal
          isOpen={showSaveModal}
          onClose={() => setShowSaveModal(false)}
          onSaved={handleSaveSuccess}
          onRefreshHistory={onRefreshHistory}
          calculationData={{
            structure_type: calculationType,
            calculation_data: formData || {},
            result: result,
            map_coordinates: mapCoordinates
          }}
        />
      )}

      {/* Büyük Ova Modal */}
      {showBuyukOvaModal && (
        <BuyukOvaModal
          isOpen={showBuyukOvaModal}
          onClose={() => setShowBuyukOvaModal(false)}
          calculationType={calculationType}
          selectedPoint={mapCoordinates && mapCoordinates.lat && mapCoordinates.lng ? 
            { lat: mapCoordinates.lat, lng: mapCoordinates.lng } : 
            null
          }
        />
      )}
    </ResultContainer>
  );
};

export default ResultDisplay;
