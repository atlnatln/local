import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import SEO from '../components/SEO';
import CalculationForm from '../components/CalculationForm';
import ResultDisplay from '../components/ResultDisplay';
import AdPlacementAccordion from '../components/AdPlacementAccordion';
import MapComponent, { MapRef } from '../components/Map/MapComponent';
import LocationAutocomplete from '../components/LocationAutocomplete';
import WaterPermitWarning from '../components/WaterPermitWarning';
import CalculationFeedbackAccordion from '../components/CalculationFeedbackAccordion';
import { LocationValidationProvider, useLocationValidation } from '../contexts/LocationValidationContext';
import { CalculationResult, StructureType } from '../types';
import { KMLParser } from '../utils/kmlParser';
import { toast } from 'react-toastify';
import L from 'leaflet';

interface CalculationPageProps {
  calculationType: StructureType;
  title: string;
  description: string;
}

const PageContainer = styled.div`
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  
  @media (max-width: 768px) {
    padding: 12px;
    max-width: 100%;
  }
`;

const PageHeader = styled.div`
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 2px solid #f3f4f6;
  text-align: center;
  
  @media (max-width: 768px) {
    margin-bottom: 24px;
    padding-bottom: 16px;
    text-align: left;
    padding: 0 4px 16px 4px;
  }
`;

const PageTitle = styled.h1`
  color: #111827;
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
  
  @media (max-width: 768px) {
    font-size: 24px;
  }
`;

const PageDescription = styled.p`
  color: #6b7280;
  font-size: 18px;
  line-height: 1.6;
  margin: 0;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  
  @media (max-width: 768px) {
    font-size: 16px;
    margin-left: 0;
    margin-right: 0;
  }
`;

const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
  
  @media (max-width: 768px) {
    gap: 16px;
    padding: 0 4px;
    margin: 0 -4px; /* Negatif margin ile container'ı genişlet */
  }
`;

const FormSection = styled.div`
  order: 0;
  
  @media (max-width: 768px) {
    margin: 0 -4px; /* Form bileşenlerini kahverengi çerçeve içinde genişlet */
  }
`;

const ResultSection = styled.div`
  order: 1;
  
  @media (max-width: 768px) {
    margin: 0 -4px; /* Result bileşenlerini kahverengi çerçeve içinde genişlet */
  }
`;

const AdSection = styled.div`
  order: 1;

  @media (max-width: 768px) {
    margin: 0 -4px;
  }
`;

const MapSection = styled.div<{ $isOpen: boolean }>`
  margin-bottom: 32px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  overflow: hidden;
  position: relative;
  transition: all 0.3s ease;
  height: ${props => props.$isOpen ? 'auto' : '60px'};
  
  @media (max-width: 768px) {
    margin: 0 -4px 24px -4px;  /* -8px yerine -4px kullanarak kahverengi çerçeveyi koruyoruz */
    border-radius: 8px;
  }
`;

const MapHeader = styled.div<{ $isOpen: boolean }>`
  padding: 16px 24px;
  border-bottom: ${props => props.$isOpen ? '1px solid #e5e7eb' : 'none'};
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 60px;
  position: relative;
  
  @media (max-width: 600px) {
    padding: 8px 10px;
    min-height: 44px;
    border-radius: 0;
    background: #f8fafc;
    gap: 6px;
  }
`;

const MapTitle = styled.h3`
  color: #111827;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  
  @media (max-width: 600px) {
    font-size: 15px;
    gap: 4px;
  }
`;

const MapToggleButton = styled.button<{ $isOpen: boolean }>`
  background: ${props => props.$isOpen ? '#e74c3c' : '#3498db'};
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  
  &:hover {
    background: ${props => props.$isOpen ? '#c0392b' : '#2980b9'};
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
  @media (max-width: 600px) {
    padding: 6px 10px;
    font-size: 13px;
    border-radius: 5px;
    gap: 3px;
  }
`;

const MapContainer = styled.div<{ $isOpen: boolean }>`
  overflow: ${props => props.$isOpen ? 'visible' : 'hidden'};
  transition: all 0.3s ease;
  max-height: ${props => props.$isOpen ? 'none' : '0'};
  opacity: ${props => props.$isOpen ? 1 : 0};
`;

const MapInfoSection = styled.div`
  margin: 16px;
  padding: 16px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9f5e9 100%);
  border-radius: 10px;
  border: 1px solid #c3e6cb;
  
  @media (max-width: 768px) {
    margin: 8px;
    padding: 10px;
    border-radius: 6px;
  }
  
  @media (max-width: 480px) {
    margin: 6px;
    padding: 8px;
  }
`;

const MapInfoTitle = styled.h4`
  margin: 0 0 10px 0;
  color: #155724;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  
  @media (max-width: 768px) {
    font-size: 13px;
    margin-bottom: 8px;
    gap: 4px;
  }
  
  @media (max-width: 480px) {
    font-size: 12px;
    margin-bottom: 6px;
  }
`;

const MapInfoList = styled.ul`
  margin: 0;
  padding: 0 0 0 16px;
  color: #2d5a3d;
  font-size: 12px;
  line-height: 1.5;
  
  li {
    margin-bottom: 4px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  @media (max-width: 768px) {
    font-size: 11px;
    padding-left: 14px;
    line-height: 1.4;
    
    li {
      margin-bottom: 3px;
    }
  }
  
  @media (max-width: 480px) {
    font-size: 10px;
    padding-left: 12px;
    
    li {
      margin-bottom: 2px;
    }
  }
`;

const MapInfoNote = styled.p`
  margin: 8px 0 0 0;
  padding: 8px;
  background: rgba(255, 193, 7, 0.15);
  border-radius: 4px;
  border-left: 2px solid #ffc107;
  color: #856404;
  font-size: 11px;
  line-height: 1.4;
  
  @media (max-width: 768px) {
    font-size: 10px;
    padding: 6px;
    margin-top: 6px;
  }
  
  @media (max-width: 480px) {
    font-size: 9px;
    padding: 5px;
    margin-top: 5px;
  }
`;

// Helper: extract first polygon ring from GeoJSON
const extractFirstPolygonCoords = (geoJson: any): number[][] | null => {
  const features = geoJson?.features || [];
  for (const feature of features) {
    const geometry = feature?.geometry;
    if (!geometry) continue;
    if (geometry.type === 'Polygon' && geometry.coordinates?.length) {
      return geometry.coordinates[0];
    }
    if (geometry.type === 'MultiPolygon' && geometry.coordinates?.length) {
      return geometry.coordinates[0][0];
    }
  }
  return null;
};

// Helper: compute centroid (lon/lat) from polygon coordinates
const computePolygonCentroid = (geoJson: any): { lat: number; lng: number } | null => {
  const coords = extractFirstPolygonCoords(geoJson);
  if (!coords || coords.length === 0) return null;

  const sum = coords.reduce(
    (acc, [lng, lat]) => ({ lat: acc.lat + lat, lng: acc.lng + lng }),
    { lat: 0, lng: 0 }
  );

  return {
    lat: sum.lat / coords.length,
    lng: sum.lng / coords.length
  };
};

// Helper: derive Leaflet bounds from GeoJSON
const getBoundsFromGeoJson = (geoJson: any): L.LatLngBounds | null => {
  try {
    const layer = L.geoJSON(geoJson);
    const bounds = layer.getBounds();
    return bounds.isValid() ? bounds : null;
  } catch (error) {
    console.error('Bounds hesaplanamadı', error);
    return null;
  }
};

// Ana sayfa bileşeni - location validation ile wrap edilmiş
const CalculationPageContent: React.FC<CalculationPageProps> = ({ 
  calculationType, 
  title, 
  description 
}) => {
  const [result, setResult] = useState<CalculationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isManualSelection, setIsManualSelection] = useState(false);
  const [isMapVisible, setIsMapVisible] = useState(true);
  const [araziVasfi, setAraziVasfi] = useState<string>('');
  const [emsalTuru, setEmsalTuru] = useState<string>('marjinal');
  const [formData, setFormData] = useState<any>(null);
  const [mapCoordinates, setMapCoordinates] = useState<any>(null);
  const [uploadedGeoJson, setUploadedGeoJson] = useState<any | null>(null);
  const [uploadedKmlName, setUploadedKmlName] = useState<string | null>(null);
  const [uploadedKmlError, setUploadedKmlError] = useState<string | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [_refreshHistoryTrigger, setRefreshHistoryTrigger] = useState<number>(0);
  const mapRef = useRef<MapRef>(null);
  
  // Location validation context
  const { 
    state: locationState, 
    setSelectedPoint, 
    canUserProceedWithCalculation 
  } = useLocationValidation();

  // Su tahsis belgesi uyarısı için kontrol
  const shouldShowWaterPermitWarning = () => {
    const { kmlCheckResult, suTahsisBelgesi } = locationState;
    const waterDependentFacilities = [
      'sut-sigirciligi', 'besi-sigirciligi', 'agil-kucukbas',
      'kumes-yumurtaci', 'kumes-etci', 'kumes-hindi', 'kaz-ordek',
      'kumes-gezen', 'hara', 'evcil-hayvan', 'yikama-tesisi'
    ];

    return calculationType &&
           waterDependentFacilities.includes(calculationType) &&
           (kmlCheckResult?.insideYasPolygons?.length || 0) > 0 &&
           suTahsisBelgesi === false;
  };

  const getBlockReason = () => {
    const { kmlCheckResult } = locationState;

    if (!kmlCheckResult) {
      return "⚠️ Haritadan bir konum seçmeniz gerekiyor";
    }

    return "⚠️ Haritadan geçerli bir konum seçmeniz gerekiyor";
  };
  
  console.log('🔍 CalculationPage - Form block check:', {
    calculationType,
    // isFormBlocked,
    blockReason: getBlockReason(),
    canProceed: canUserProceedWithCalculation(calculationType)
  });

  // Render Debug - Component her render edildiğinde çalışır
  // console.log('🔄 CalculationPage - Component Render:', {
  //   result: result,
  //   isLoading: isLoading,
  //   calculationType: calculationType,
  //   resultExists: !!result,
  //   shouldShowResult: !!(result || isLoading)
  // });

  // History refresh handler
  const handleRefreshHistory = () => {
    setRefreshHistoryTrigger(prev => prev + 1);
  };

  const handleCalculationResult = (newResult: CalculationResult) => {
    console.log('🎯 CalculationPage - handleCalculationResult called with:', newResult);
    console.log('🔍 CalculationPage - Before state update:', { currentResult: result, currentIsLoading: isLoading });
    
    setResult(newResult);
    setIsLoading(false);
    
    console.log('📊 CalculationPage - State updated: result set, isLoading set to false');
    
    // Debug: State güncellendikten sonra render koşulunu kontrol et
    setTimeout(() => {
      console.log('🔍 CalculationPage - Render Condition Debug:', {
        result: newResult,
        isLoading: false,
        shouldRenderResult: (newResult || false),
        newResult_truthy: !!newResult,
        newResult_success: newResult?.success
      });
    }, 100);
    
    // Force re-render debug
    setTimeout(() => {
      console.log('🔍 CalculationPage - Force check after 500ms...');
    }, 500);
  };

  const handleFormDataChange = (data: any) => {
    setFormData(data);
  };

  const handleMapCoordinatesChange = (coordinates: any) => {
    setMapCoordinates(coordinates);
  };

  const handleCalculationStart = () => {
    console.log('🚀 CalculationPage - handleCalculationStart called, setting isLoading to true');
    setIsLoading(true);
    setResult(null);
    console.log('📊 CalculationPage - State updated: isLoading set to true, result cleared');
  };

  const handleAraziVasfiChange = (newAraziVasfi: string) => {
    console.log(`🧹 CalculationPage - Arazi vasfı değişti: "${araziVasfi}" → "${newAraziVasfi}"`);
    
    // Arazi vasfı değiştiğinde önceki hesaplama sonuçlarını temizle
    if (araziVasfi && newAraziVasfi !== araziVasfi) {
      console.log('🧹 CalculationPage - Önceki hesaplama sonuçları temizleniyor');
      setResult(null);
      setIsLoading(false);
    }
    
    setAraziVasfi(newAraziVasfi);
    console.log('✅ CalculationPage - Arazi vasfı güncellendi');
  };

  // Emsal türü değişikliği için handler
  const handleEmsalTuruChange = (newEmsalTuru: string) => {
    console.log(`🔄 CalculationPage - Emsal türü değişti: "${emsalTuru}" → "${newEmsalTuru}"`);
    setEmsalTuru(newEmsalTuru);
    
    // Eğer sonuç zaten varsa, yeni hesaplama başlat
    if (result) {
      console.log('🔄 CalculationPage - Emsal türü değiştiği için yeniden hesaplama yapılacak');
      setIsLoading(true);
      
      // Form submit işlemini tetikle
      setTimeout(() => {
        const form = document.querySelector('form');
        if (form) {
          console.log('🚀 CalculationPage - Form submit tetikleniyor (emsal türü değişikliği)');
          form.dispatchEvent(new Event('submit', { bubbles: true }));
        } else {
          console.error('❌ CalculationPage - Form bulunamadı, loading durumu sıfırlanıyor');
          setIsLoading(false);
        }
      }, 100); // Form'un güncellenmesi için kısa bir bekleme
    }
    
    console.log('✅ CalculationPage - Emsal türü güncellendi');
  };

  // CalculationType değişiminde form ve sonuçları sıfırla
  useEffect(() => {
    console.log(`🔄 CalculationPage - calculationType değişti: "${calculationType}"`);
    console.log('🧹 CalculationPage - calculationType değişiminde önceki hesaplama verileri temizleniyor');
    
    // Form ve sonuçları sıfırla
    setResult(null);
    setIsLoading(false);
    setAraziVasfi(''); // Arazi vasfını da sıfırla
    setSelectedPoint(null); // Seçili koordinatları da temizle
    setIsManualSelection(false); // Manuel seçim flag'ini sıfırla
    
    console.log('✅ CalculationPage - calculationType değişiminde sıfırlama tamamlandı');
  }, [calculationType, setSelectedPoint]);

  const handleMapClick = (coordinate: {lat: number, lng: number}) => {
    setSelectedPoint(coordinate);
    setIsManualSelection(true); // Manuel seçim olarak işaretle
    console.log('🗺️ Manuel seçilen koordinat:', coordinate);
    console.log('📍 Calculation type:', calculationType);
  };

  const handleKmlUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploadedKmlError(null);

    // Dosya tipi kontrolü
    if (!file.name.toLowerCase().endsWith('.kml')) {
      toast.error('Sadece .kml uzantılı dosyalar kabul edilmektedir.', {
        position: 'top-center',
        autoClose: 5000
      });
      event.target.value = '';
      return;
    }

    // Boyut kontrolü: 50KB = 50 * 1024 = 51200 byte
    const maxSizeBytes = 50 * 1024;
    if (file.size > maxSizeBytes) {
      const sizeKB = (file.size / 1024).toFixed(1);
      toast.error(`KML dosyası çok büyük (${sizeKB} KB). Maksimum 50 KB izin verilmektedir.`, {
        position: 'top-center',
        autoClose: 5000
      });
      event.target.value = ''; // Input'u temizle
      return;
    }

    try {
      const fileText = await file.text();
      const geoJson = KMLParser.parseKMLToGeoJSON(fileText);

      if (!geoJson?.features?.length) {
        throw new Error('Geçerli poligon bulunamadı');
      }

      setUploadedGeoJson({ data: geoJson });
      setUploadedKmlName(file.name);

      const mapInstance = mapRef.current?.getMapInstance();
      const bounds = getBoundsFromGeoJson(geoJson);
      if (mapInstance && bounds) {
        mapInstance.fitBounds(bounds.pad(0.02));
      }

      const centroid = computePolygonCentroid(geoJson);
      if (centroid) {
        setSelectedPoint(centroid);
        setIsManualSelection(true);
      }

      console.log('✅ KML yüklendi ve haritaya eklendi:', file.name);
    } catch (error) {
      console.error('❌ KML yükleme hatası:', error);
      setUploadedGeoJson(null);
      setUploadedKmlName(null);
      setUploadedKmlError('KML dosyası okunamadı veya poligon bulunamadı. Lütfen geçerli bir KML yükleyin.');
    } finally {
      event.target.value = '';
    }
  };

  const toggleMapVisibility = () => {
    setIsMapVisible(!isMapVisible);
  };

  // Konum seçildiğinde haritada zoom yap
  const handleLocationSelect = (location: any) => {
    // Her zaman mahalle seviyesinde zoom (çünkü hepsi mahalle)
    const zoomLevel = 15;
    
    // Haritada konuma zoom yap - yeni format koordinatlarını kullan
    const lat = location.lat || location.latitude;
    const lon = location.lon || location.longitude;
    
    if (mapRef.current && lat && lon) {
      mapRef.current.zoomToLocation(lat, lon, zoomLevel);
    }
    
    // Mahalle seçimi için koordinat gösterimi ve marker'ı kaldır
    setSelectedPoint(null);
    setIsManualSelection(false);
    
    console.log(`📍 ${location.mahalle}, ${location.ilce}, ${location.il} seçildi (zoom: ${zoomLevel}) - Marker gösterilmiyor`);
  };

  // Sayfa başlığını dinamik olarak ayarla
  useEffect(() => {
    document.title = `${title} - Tarım İmar`;
  }, [title]);

  // Giriş formunu üstte göster
  return (
    <>
      <SEO
        title={`${title} Hesaplama | Tarım İmar`}
        description={description}
        canonical={`/${calculationType}`}
        keywords={`${title}, tarımsal yapılaşma, hesaplama, tarım imar, ${calculationType}`}
      />
      <PageContainer>
        {/* Giriş butonu kaldırıldı, kullanıcılar header'dan giriş yapıyor */}
        <PageHeader>
          <PageTitle>{title}</PageTitle>
          <PageDescription>{description}</PageDescription>
        </PageHeader>

      {/* Su Tahsis Belgesi Uyarısı */}
      {shouldShowWaterPermitWarning() && <WaterPermitWarning />}

      <MapSection $isOpen={isMapVisible}>
        <MapHeader $isOpen={isMapVisible}>
          <MapTitle>
            📍 Arazi Konumu Seçimi
          </MapTitle>
          <MapToggleButton $isOpen={isMapVisible} onClick={toggleMapVisibility}>
            {isMapVisible ? (
              <>
                <span>📍</span>
                Haritayı Gizle
              </>
            ) : (
              <>
                <span>🗺️</span>
                Haritayı Göster
              </>
            )}
          </MapToggleButton>
        </MapHeader>
        <MapContainer $isOpen={isMapVisible}>
          {/* Konum Arama Bölümü */}
          <div style={{ 
            marginBottom: window.innerWidth <= 600 ? '12px' : '16px', 
            padding: window.innerWidth <= 600 ? '12px' : '16px', 
            background: '#f8f9fa', 
            borderRadius: window.innerWidth <= 600 ? '6px' : '8px',
            border: '1px solid #e9ecef'
          }}>
            <div style={{ 
              marginBottom: window.innerWidth <= 600 ? '6px' : '8px', 
              fontSize: window.innerWidth <= 600 ? '12px' : '14px', 
              fontWeight: '600', 
              color: '#2c3e50' 
            }}>
              🔍 İlçe/Mahalle Arama
            </div>
            <LocationAutocomplete 
              onLocationSelect={handleLocationSelect}
              placeholder="İl, ilçe veya mahalle adı yazın... (örn: İzmir, Karşıyaka)"
            />
            <div style={{ 
              marginTop: window.innerWidth <= 600 ? '6px' : '8px', 
              fontSize: window.innerWidth <= 600 ? '10px' : '12px', 
              color: '#6c757d' 
            }}>
              💡 İlçe veya mahalle seçtiğinizde harita otomatik olarak o konuma odaklanacak
            </div>
          </div>

          <div style={{
            marginBottom: window.innerWidth <= 600 ? '12px' : '16px',
            padding: window.innerWidth <= 600 ? '12px' : '16px',
            background: '#f8f9fa',
            borderRadius: window.innerWidth <= 600 ? '6px' : '8px',
            border: '1px solid #e9ecef'
          }}>
            <div style={{
              marginBottom: window.innerWidth <= 600 ? '6px' : '8px',
              fontSize: window.innerWidth <= 600 ? '12px' : '14px',
              fontWeight: '600',
              color: '#2c3e50'
            }}>
              📂 KML Poligon Yükle (Arazi Sınırı)
            </div>
            <input
              type="file"
              accept=".kml"
              onChange={handleKmlUpload}
              style={{ fontSize: window.innerWidth <= 600 ? '12px' : '13px' }}
            />
            {uploadedKmlName && (
              <div style={{
                marginTop: 6,
                fontSize: window.innerWidth <= 600 ? '11px' : '12px',
                color: '#0f5132',
                background: '#d1e7dd',
                border: '1px solid #badbcc',
                borderRadius: 6,
                padding: '6px 8px'
              }}>
                ✅ Yüklendi: {uploadedKmlName}
              </div>
            )}
            {uploadedKmlError && (
              <div style={{
                marginTop: 6,
                fontSize: window.innerWidth <= 600 ? '11px' : '12px',
                color: '#842029',
                background: '#f8d7da',
                border: '1px solid #f5c2c7',
                borderRadius: 6,
                padding: '6px 8px'
              }}>
                {uploadedKmlError}
              </div>
            )}
          </div>

          <MapComponent
            ref={mapRef}
            center={[39.0, 35.0]}
            zoom={window.innerWidth < 768 ? 5 : 6}
            onMapClick={handleMapClick}
            selectedCoordinate={locationState.selectedPoint}
            showMarker={isManualSelection}
            height="400px"
            kmlLayers={[]}
            customGeoJsonLayers={uploadedGeoJson ? [{ data: uploadedGeoJson.data, name: uploadedKmlName || 'Yüklenen KML' }] : []}
          />

          {/* Harita Bilgilendirme Bölümü */}
          <MapInfoSection>
            <MapInfoTitle>
              <span>ℹ️</span>
              Harita Özellikleri ve Konum Seçimi
            </MapInfoTitle>
            <MapInfoList>
              <li><strong>Konum Seçimi:</strong> Hesaplama yapmak istediğiniz arazinin üzerine veya yakınına tıklayarak konum seçin.</li>
              <li><strong>Büyükova Kontrolü:</strong> Haritada işaretleyeceğiniz nokta Türkiye geneli "Büyükova Tarım Alanları" kontrolü yapar. Bu alanlarda tarımsal yapılaşma kısıtlamaları uygulanır.</li>
              <li><strong>DSİ Kapalı Havza:</strong> İşaretlediğiniz noktanın DSİ tarafından belirlenen YAS kapalı havza bölgelerinde olması durumunda su bağımlı tesisler (hayvancılık, yıkama tesisi vb.) için ek belgeler istenmektedir.</li>
              <li><strong>İl/İlçe Bilgisi:</strong> Seçilen noktanın il ve ilçe bilgisi harita doğrulamasında gösterilir.</li>
            </MapInfoList>
            <MapInfoNote>
              <strong>💡 İpucu:</strong> Seçtiğiniz konumun büyükova veya kapalı havza içinde olup olmadığı hesaplama sonucunda detaylı olarak gösterilecektir. Doğru sonuç için arazi konumunuzu mümkün olduğunca hassas seçin.
            </MapInfoNote>
          </MapInfoSection>

        </MapContainer>
      </MapSection>
      
      <ContentGrid>
        <FormSection>
          <CalculationForm
            calculationType={calculationType}
            onResult={handleCalculationResult}
            onCalculationStart={handleCalculationStart}
            selectedCoordinate={locationState.selectedPoint}
            onAraziVasfiChange={handleAraziVasfiChange}
            emsalTuru={emsalTuru}
            onEmsalTuruChange={handleEmsalTuruChange}
            onFormDataChange={handleFormDataChange}
            onMapCoordinatesChange={handleMapCoordinatesChange}
          />
        </FormSection>

        {result?.success && !isLoading && locationState.kmlCheckResult?.province && (
          <AdSection>
            <AdPlacementAccordion
              selectedProvince={locationState.kmlCheckResult?.province || null}
              calculationType={calculationType}
            />
          </AdSection>
        )}
        
        {(() => {
          // console.log('🔍 CalculationPage - Render Check:', { result, isLoading, shouldRender: (result || isLoading) });
          return null;
        })()}
        
        {(result || isLoading) && (
          <ResultSection>
            {(() => {
              console.log('🖼️ CalculationPage - Rendering ResultDisplay with:', { result, isLoading, calculationType, araziVasfi, emsalTuru });
              return null;
            })()}
            <ResultDisplay
              result={result}
              isLoading={isLoading}
              calculationType={calculationType}
              araziVasfi={araziVasfi}
              selectedEmsalType={emsalTuru}
              onEmsalTypeChange={handleEmsalTuruChange}
              formData={formData}
              mapCoordinates={mapCoordinates}
              onRefreshHistory={handleRefreshHistory}
            />
          </ResultSection>
        )}
      </ContentGrid>

      {/* Geri Bildirim — hesaplama sonucu geldikten sonra, footer'ın hemen üstünde */}
      {result && !isLoading && (
        <CalculationFeedbackAccordion calculationType={calculationType} />
      )}
    </PageContainer>
    </>
  );
};

// Ana bileşen - LocationValidationProvider ile wrap edilmiş
const CalculationPage: React.FC<CalculationPageProps> = (props) => {
  return (
    <LocationValidationProvider>
      <CalculationPageContent {...props} />
    </LocationValidationProvider>
  );
};

export default CalculationPage;
