import React, { useEffect, useState, useRef, useMemo } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import styled from 'styled-components';

const MapContainer_Styled = styled.div`
  .leaflet-container {
    height: 400px;
    width: 100%;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
  }
`;

interface HavzaHaritasiProps {
  // onLocationSelect is no longer used for input, but kept for compatibility.
  onLocationSelect?: (il: string, ilce: string) => void; 
  selectedLocation: { il: string; ilce: string };
  selectedProducts?: string[];
  havzaData: Record<string, Record<string, string[]>>;
  showSupportedDistricts?: boolean;
}

const YEM_BITKILERI_BIRINCI = [
  'Fiğ',
  'Burçak',
  'Mürdümük',
  'Hayvan Pancarı',
  'Yem Şalgamı',
  'Yem Bezelyesi',
  'Yem Baklası',
  'Üçgül',
  'İtalyan Çimi',
  'Yulaf',
  'Yulaf (yem)',
  'Çavdar',
  'Çavdar (yem)',
  'Tritikale',
  'Tritikale (yem)'
];

const YEM_BITKILERI_IKINCI = [
  'Yonca',
  'Korunga',
  'Yapay Çayır Mera',
  'Silajlık Mısır',
  'Silajlık Soya',
  'Sorgum Otu',
  'Sudan Otu',
  'Sorgum-Sudan Otu Melezi'
];

const PRODUCT_COLORS = ['#F59E0B', '#EF4444', '#10B981', '#8B5CF6', '#F97316', '#06B6D4', '#84CC16'];

// Türkçe karakter normalizasyonu (eşleştirme anahtarı için)
function normalizeKey(name: string): string {
  if (!name) return '';
  return name
    .toLocaleUpperCase('tr-TR')
    .replace(/\s+/g, '')
    .replace(/İ/g, 'I')
    .replace(/Ö/g, 'O')
    .replace(/Ü/g, 'U')
    .replace(/Ç/g, 'C')
    .replace(/Ş/g, 'S')
    .replace(/Ğ/g, 'G')
    .replace(/Â/g, 'A')
    .replace(/Î/g, 'I')
    .replace(/Û/g, 'U')
    .replace(/[^A-Z0-9]/g, '')
    .trim();
}

// Türkçe karakter normalizasyonu
function normalizeName(name: string): string {
  return normalizeKey(name);
}

// İsim eşleştirmesi için fuzzy matching
function areNamesLooseMatch(name1: string, name2: string): boolean {
  if (!name1 || !name2) return false;
  const norm1 = normalizeName(name1);
  const norm2 = normalizeName(name2);
  return norm1 === norm2;
}

// İlçe ismindeki yaygın farklılıkları normalize et
function normalizeDistrictName(name: string): string {
  if (!name) return '';
  
  return normalizeKey(name)
    // Yaygın farklılıkları düzelt
    .replace(/MERKEZ$/g, '') // MERKEZ sonekini kaldır
    .replace(/^MERKEZ$/g, '') // Sadece MERKEZ olan ilçeleri boş string yap
    .replace(/IL$/g, '') // İL sonekini kaldır (normalize edilmiş)
    .replace(/BELEDIYESI$/g, '') // BELEDİYESİ sonekini kaldır (normalize edilmiş)
    .trim();
}

// Gelişmiş ilçe eşleştirme fonksiyonu
function findDistrictMatch(ilceGeo: string, ilcelerHavza: string[]): string | null {
  if (!ilceGeo || !ilcelerHavza) return null;
  
  const normalizedGeo = normalizeDistrictName(ilceGeo);
  
  // 1. Tam eşleşme
  for (const ilce of ilcelerHavza) {
    if (normalizeDistrictName(ilce) === normalizedGeo) {
      return ilce;
    }
  }
  
  // 2. GeoJSON'da il adı ile ilçe adı aynıysa, MERKEZ olarak ara
  if (normalizedGeo && normalizedGeo.length > 0) {
    for (const ilce of ilcelerHavza) {
      if (normalizeDistrictName(ilce) === 'MERKEZ' || ilce === 'MERKEZ') {
        return ilce;
      }
    }
  }
  
  // 3. Kısmi eşleşme (substring)
  for (const ilce of ilcelerHavza) {
    const normalizedHavza = normalizeDistrictName(ilce);
    if (normalizedGeo.includes(normalizedHavza) || normalizedHavza.includes(normalizedGeo)) {
      return ilce;
    }
  }
  
  return null;
}

// Ürün adlarını havza veri setiyle eşleştirmek için normalize et
function normalizeProductKey(name: string): string {
  if (!name) return '';
  return name
    .toLocaleLowerCase('tr-TR')
    .replace(/\s+/g, ' ')
    .replace(/\([^)]*\)/g, '')
    .trim();
}

function hasProductMatch(selected: string[], supported: string[]): boolean {
  if (!selected.length || !supported.length) return false;
  const supportedKeys = new Set(supported.map(normalizeProductKey));
  return selected.some((p) => supportedKeys.has(normalizeProductKey(p)));
}

function isYemBitkisiDetay(product: string): boolean {
  return YEM_BITKILERI_BIRINCI.includes(product) || YEM_BITKILERI_IKINCI.includes(product);
}

function expandSelectedProducts(selectedProducts?: string[]): string[] {
  if (!selectedProducts || selectedProducts.length === 0) return [];
  return selectedProducts.flatMap((product) => {
    if (isYemBitkisiDetay(product)) return [product, 'Yem Bitkileri'];
    if (product === 'Diğer Ürünler') return ['Diğer Ürünler'];
    return [product];
  });
}

function expandedVariantsForSingleProduct(product: string): string[] {
  if (isYemBitkisiDetay(product)) return [product, 'Yem Bitkileri'];
  if (product === 'Diğer Ürünler') return ['Diğer Ürünler'];
  return [product];
}

// Feature'dan ilçe ve il ismini çıkar
function getFeatureInfo(feature: any) {
  const props = feature.properties;
  
  // Turkey Districts geojson standartları değişken olabilir, 
  // genelde ADM1 (İl) ve ADM2 (İlçe) olur.
  
  let il = props.ADM1_TR || props.admin1Name || props.il || '';
  let ilce = props.ADM2_TR || props.admin2Name || props.ilce || props.name || '';
  
  if (!ilce && props.Name && props.description) {
      // KML'den dönüşmüş olabilir
      ilce = props.Name;
  }
  
  return { 
    il: normalizeName(il), 
    ilce: normalizeName(ilce)
  };
}

function MapUpdater({ selectedLocation, geoData }: { selectedLocation: { il: string, ilce: string }, geoData: any }) {
  const map = useMap();
  const prevLocationRef = useRef<{ il: string, ilce: string }>({ il: '', ilce: '' });

  useEffect(() => {
    if (!geoData || !selectedLocation.il) return;

    if (prevLocationRef.current.il === selectedLocation.il && 
        prevLocationRef.current.ilce === selectedLocation.ilce) {
      return;
    }
    prevLocationRef.current = selectedLocation;

    const targetIl = normalizeName(selectedLocation.il);
    const targetIlce = normalizeName(selectedLocation.ilce || '');

    let foundFeature: any = null;
    let foundLayer: L.Layer | null = null;
    
    // GeoJSON layer'ını bulmak için basit bir yol: veriyi tara
    // Ancak map.fitBounds için L.Layer instance'ına ihtiyacımız var.
    // Bu yüzden özellik aramak yerine map üzerindeki layerları taramak daha iyi olabilir ama
    // GeoJSON component statik data ile render olduğu için ref ile erişmek zor olabilir.
    // Alternatif: L.geoJSON(feature).getBounds() kullanmak.
    
    for (const feature of geoData.features) {
      const { il, ilce } = getFeatureInfo(feature);
      
      // İlçe eşleşmesi
      // Not: Bazı GeoJSON kayıtlarında merkez ilçe adı il adı ile aynıdır (örn: AĞRI - AĞRI)
      // Bu durumda kullanıcı "MERKEZ" seçtiyse ve kayıt il=ilçe şklindeyse eşleştirme yap.
      const isDirectMatch = targetIlce && ilce === targetIlce;
      const isMerkezMatch = targetIlce === 'MERKEZ' && areNamesLooseMatch(ilce, il);

      if (isDirectMatch || isMerkezMatch) {
        // İllerin de tutması lazım ama bazen veri setindeki il adı (özellikle merkez ilçelerde) farklı olabilir.
        // Genelde ilçeler uniqdir veya ile göre bakılır.
        if (!targetIl || il === targetIl) {
           foundFeature = feature;
           break;
        }
      }
    }
    
    // Eğer ilçe bulunamadıysa ama il seçiliyse, o ilin tüm ilçelerini kapsayan bir bounds bulabiliriz
    // Ama şimdilik sadece ilçe odaklı gidelim
    
    if (foundFeature) {
      const layer = L.geoJSON(foundFeature);
      const bounds = layer.getBounds();
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 10 });
      }
    } else if (targetIl) {
        // İlin koordinatlarına git (eğer ilçe yoksa)
        // Bunun için manuel bir mapping veya geojson featurelarının bounding box union'ı gerekir.
        // Şimdilik pas geçiyoruz.
    }

  }, [selectedLocation, geoData, map]);

  return null;
}

function InitialBoundsFitter({ geoData }: { geoData: any }) {
  const map = useMap();
  const didFitRef = useRef(false);

  useEffect(() => {
    if (!geoData || didFitRef.current) return;

    const bounds = L.geoJSON(geoData).getBounds();
    if (!bounds.isValid()) return;

    // İlk açılışta Türkiye sınırlarını tam kadraja sığdır.
    // maxZoom ile aşırı yakınlaşmayı engelliyoruz (mobilde de tutarlı).
    setTimeout(() => {
      map.invalidateSize();
      map.fitBounds(bounds, { padding: [10, 10], maxZoom: 6 });
      didFitRef.current = true;
    }, 0);
  }, [geoData, map]);

  return null;
}

function SupportedDistrictsBoundsFitter({
  geoData,
  selectedLocation,
  selectedProducts,
  normalizedHavzaData,
  showSupportedDistricts,
  plannedFillByKey
}: {
  geoData: any;
  selectedLocation: { il: string; ilce: string };
  selectedProducts?: string[];
  normalizedHavzaData: Record<string, Record<string, string[]>>;
  showSupportedDistricts: boolean;
  plannedFillByKey: Map<string, string>;
}) {
  const map = useMap();
  const prevShowRef = useRef(false);
  const lastProductsSigRef = useRef('');

  useEffect(() => {
    const productsSig = (selectedProducts || []).join('|');

    if (!showSupportedDistricts) {
      prevShowRef.current = false;
      lastProductsSigRef.current = productsSig;
      return;
    }

    if (!geoData || !selectedProducts || selectedProducts.length === 0) return;
    if (!normalizedHavzaData) return;

    const shouldFit = !prevShowRef.current || lastProductsSigRef.current !== productsSig;
    prevShowRef.current = true;
    lastProductsSigRef.current = productsSig;
    if (!shouldFit) return;

    const targetIl = normalizeName(selectedLocation.il);
    const targetIlce = normalizeName(selectedLocation.ilce || '');

    const bounds = L.latLngBounds([]);
    let anyIncluded = false;

    for (const feature of geoData.features || []) {
      const { il, ilce } = getFeatureInfo(feature);
      let include = false;

      // Seçili bölgeyi (yeşil) her zaman kadraja dahil et
      if (targetIlce) {
        const isDirectMatch = ilce === targetIlce;
        const isMerkezMatch = targetIlce === 'MERKEZ' && areNamesLooseMatch(ilce, il);
        
        if ((isDirectMatch || isMerkezMatch) && (!targetIl || il === targetIl)) {
            include = true;
        }
      } else if (targetIl) {
        if (il === targetIl) include = true;
      }

        // Desteklenen diğer ilçeler (turuncu/mor vb.)
        if (plannedFillByKey.has(`${il}|${ilce}`)) include = true;

      if (!include) continue;

      const layer = L.geoJSON(feature);
      const b = layer.getBounds();
      if (!b.isValid()) continue;

      bounds.extend(b);
      anyIncluded = true;
    }

    if (anyIncluded && bounds.isValid()) {
      // Diğer ilçeler görünürken kullanıcı fark etsin diye kadrajı genişlet.
      // maxZoom ile aşırı yaklaşmayı engelliyoruz.
      map.fitBounds(bounds, { padding: [20, 20], maxZoom: 7 });
    }
  }, [geoData, map, normalizedHavzaData, plannedFillByKey, selectedLocation, selectedProducts, showSupportedDistricts]);

  return null;
}

function HavzaHaritasi({ selectedLocation, selectedProducts, havzaData, showSupportedDistricts = false }: HavzaHaritasiProps) {
  const [geoData, setGeoData] = useState<any>(null);

  const expandedSelectedProducts = useMemo(() => expandSelectedProducts(selectedProducts), [selectedProducts]);

  // Veri normalizasyonu cache
  const normalizedHavzaData = useMemo(() => {
    if (!havzaData) return {};
    const lookup: Record<string, Record<string, string[]>> = {};
    
    Object.keys(havzaData).forEach(ilBase => {
        const ilNorm = normalizeName(ilBase);
        lookup[ilNorm] = {};
        
        const ilceList = havzaData[ilBase];
        if (ilceList) {
            Object.keys(ilceList).forEach(ilceBase => {
                const ilceNorm = normalizeName(ilceBase);
                lookup[ilNorm][ilceNorm] = ilceList[ilceBase];
            });
        }
    });
    return lookup;
  }, [havzaData]);

  useEffect(() => {
    fetch('/turkey-districts.geojson')
      .then(res => res.json())
      .then(data => setGeoData(data))
      .catch(err => console.error('GeoJSON yüklenemedi:', err));
  }, []);

  const plannedFillByKey = useMemo(() => {
    const map = new Map<string, string>();
    if (!showSupportedDistricts) return map;
    if (!geoData || !geoData.features) return map;
    if (!expandedSelectedProducts || expandedSelectedProducts.length === 0) return map;
    if (!normalizedHavzaData) return map;

    for (const feature of geoData.features || []) {
      const { il, ilce } = getFeatureInfo(feature);
      if (!il || !ilce) continue;

      const ilData = normalizedHavzaData[il];
      if (!ilData) continue;

      const ilcelerHavza = Object.keys(ilData);
      const matchedIlce = findDistrictMatch(ilce, ilcelerHavza);
      const supportedProducts = matchedIlce ? ilData[matchedIlce] : undefined;
      if (!supportedProducts) continue;

      if (!hasProductMatch(expandedSelectedProducts, supportedProducts)) continue;

      let plannedColor = '#F59E0B';

      if (selectedProducts && selectedProducts.length > 1) {
        let supportedCount = 0;
        let firstMatchIndex = -1;

        for (let i = 0; i < selectedProducts.length; i++) {
          const product = selectedProducts[i];
          const expanded = expandedVariantsForSingleProduct(product);
          if (hasProductMatch(expanded, supportedProducts)) {
            supportedCount++;
            if (firstMatchIndex === -1) firstMatchIndex = i;
          }
        }

        if (supportedCount > 1) {
          plannedColor = '#6D28D9';
        } else if (firstMatchIndex !== -1) {
          plannedColor = PRODUCT_COLORS[firstMatchIndex % PRODUCT_COLORS.length];
        }
      }

      map.set(`${il}|${ilce}`, plannedColor);
    }

    return map;
  }, [expandedSelectedProducts, geoData, normalizedHavzaData, selectedProducts, showSupportedDistricts]);

  const hasAnyPlannedMatch = useMemo(() => {
    return plannedFillByKey.size > 0;
  }, [plannedFillByKey]);

  const style = (feature: any) => {
    const { il, ilce } = getFeatureInfo(feature);
    
    const targetIl = normalizeName(selectedLocation.il);
    const targetIlce = normalizeName(selectedLocation.ilce || '');

    // Debug: sadece development'ta ilk polygon için
    if (process.env.NODE_ENV !== 'production' && feature === geoData?.features?.[0]) {
      console.log('🔍 Harita Debug:', {
        showSupportedDistricts,
        selectedProducts: selectedProducts?.length || 0,
        normalizedHavzaDataExists: !!normalizedHavzaData,
        sampleIlce: il + '-' + ilce
      });
    }

    // 1. Seçim Kontrolü
    let isSelected = false;
    if (targetIlce) {
        const isDirectMatch = ilce === targetIlce;
        const isMerkezMatch = targetIlce === 'MERKEZ' && areNamesLooseMatch(ilce, il);

        if ((isDirectMatch || isMerkezMatch) && (!targetIl || il === targetIl)) {
            isSelected = true;
        }
    } else if (targetIl) {
        if (il === targetIl) {
            isSelected = true;
        }
    }

    // 2. Ürün Filtresi Kontrolü (Planned Production)
    const plannedColor = (showSupportedDistricts && il && ilce) ? plannedFillByKey.get(`${il}|${ilce}`) : undefined;
    const isPlanned = !!plannedColor;

    // Stil Önceliği: Seçili > Planlı > Varsayılan
    if (isSelected) {
        return {
          fillColor: '#059669', // Koyu Yeşil
          weight: 2,
          opacity: 1,
          color: '#047857',
          fillOpacity: 0.7
        };
    }
    
    if (isPlanned) {
        return {
          fillColor: plannedColor,
          weight: 1.2,
          opacity: 1,
          color: plannedColor,
          fillOpacity: 0.25
        };
    }

    // Buton aktifken, desteklenmeyen ilçeleri gri ile "Diğer" olarak göster
    if (showSupportedDistricts && selectedProducts && selectedProducts.length > 0) {
      return {
        fillColor: '#9CA3AF',
        weight: 0.6,
        opacity: 1,
        color: '#e2e8f0',
        fillOpacity: 0.12
      };
    }

    return {
      fillColor: '#3B82F6', // Mavi
      weight: 0.5,
      opacity: 1,
      color: 'white',
      fillOpacity: 0.05 // Çok silik
    };
  };

  const onEachFeature = (feature: any, layer: L.Layer) => {
    const { il, ilce } = getFeatureInfo(feature);
    
    // Popup içeriğini zenginleştir
    let popupContent = `<strong>${il} - ${ilce}</strong>`;

    if (normalizedHavzaData) {
      const ilData = normalizedHavzaData[il];
      if (ilData) {
        // Gelişmiş ilçe eşleştirme kullan
        const ilcelerHavza = Object.keys(ilData);
        const matchedIlce = findDistrictMatch(ilce, ilcelerHavza);
        
        let supportedProducts: string[] | undefined;
        
        if (matchedIlce) {
          supportedProducts = ilData[matchedIlce];
        }

        if (supportedProducts && supportedProducts.length > 0) {
          const urunListesi = supportedProducts.map((u: string) => `<li style="margin-bottom:3px;">${u}</li>`).join('');
          popupContent += `<br/><div style="margin-top:6px; font-size:11px; color:#374151;"><strong>Ürün Deseni:</strong><ul style="margin:4px 0 0 0; padding-left:16px; list-style-type:disc; line-height:1.4;">${urunListesi}</ul></div>`;
        } else {
          popupContent += `<br/><div style="margin-top:6px; font-size:11px; color:#9ca3af;">Ürün deseni bulunamadı.</div>`;
        }
      }
    }
    
    // Eğer ürünler seçiliyse ve bu ilçede destekleniyorsa belirt
    if (selectedProducts && selectedProducts.length > 0 && normalizedHavzaData) {
      const ilData = normalizedHavzaData[il];
      if (ilData) {
        // Gelişmiş ilçe eşleştirme kullan
        const ilcelerHavza = Object.keys(ilData);
        const matchedIlce = findDistrictMatch(ilce, ilcelerHavza);
        
        let supportedProducts: string[] | undefined;
        
        if (matchedIlce) {
          supportedProducts = ilData[matchedIlce];
        }

        if (supportedProducts) {
          const matchingProducts = selectedProducts.filter(p => supportedProducts.includes(p));
                
          if (matchingProducts.length > 0) {
             popupContent += `<br/><br/><span style="color:#D97706">✅ Desteklenen: ${matchingProducts.join(', ')}</span>`;
          } else {
             popupContent += `<br/><br/><span style="color:#9ca3af">❌ Seçili ürünler bu havzada desteklenmiyor.</span>`;
          }
        }
      }
    }
    
    if (ilce || il) {
      layer.bindPopup(popupContent);
    }
  };

  return (
    <>
      <MapContainer_Styled>
        <MapContainer
        center={[39.0, 35.0]} // Türkiye merkezi
        zoom={6}
        scrollWheelZoom={true}
        style={{ height: '400px', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {geoData && (
          <GeoJSON 
            data={geoData} 
            style={style} 
            onEachFeature={onEachFeature}
          />
        )}

        <InitialBoundsFitter geoData={geoData} />
        <MapUpdater selectedLocation={selectedLocation} geoData={geoData} />
        <SupportedDistrictsBoundsFitter
          geoData={geoData}
          selectedLocation={selectedLocation}
          selectedProducts={selectedProducts}
          normalizedHavzaData={normalizedHavzaData}
          showSupportedDistricts={showSupportedDistricts}
          plannedFillByKey={plannedFillByKey}
        />
      </MapContainer>
    </MapContainer_Styled>
    
    {/* Harita Legend - Haritanın Altında */}
    <div style={{
      background: 'white',
      padding: '12px',
      borderRadius: '8px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
      marginTop: '12px',
      fontSize: '11px',
      maxWidth: '300px'
    }}>
      <h4 style={{ margin: '0 0 8px 0', fontSize: '12px', color: '#374151', fontWeight: '600' }}>Harita Gösterimi</h4>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
        <div style={{ width: '12px', height: '12px', backgroundColor: '#059669', marginRight: '8px', borderRadius: '2px', opacity: 0.7 }}></div>
        <span>Seçili Bölge</span>
      </div>
      {selectedProducts && selectedProducts.length === 1 ? (
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
          <div
            style={{
              width: '12px',
              height: '12px',
              backgroundColor: hasAnyPlannedMatch ? '#F59E0B' : '#9CA3AF',
              marginRight: '8px',
              borderRadius: '2px',
              opacity: hasAnyPlannedMatch ? 0.6 : 0.12
            }}
          ></div>
          <span style={{ color: hasAnyPlannedMatch ? undefined : '#9ca3af' }}>
            Planlı Üretim Alanı ({selectedProducts[0]})
          </span>
        </div>
      ) : selectedProducts && selectedProducts.length > 1 ? (
        <>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
            <div style={{ width: '12px', height: '12px', backgroundColor: '#6D28D9', marginRight: '8px', borderRadius: '2px', opacity: 1 }}></div>
            <span><b>Birden Çok Ürün Destekleyen</b></span>
          </div>
          {selectedProducts.map((product: string, index: number) => {
            const productColors = ['#F59E0B', '#EF4444', '#10B981', '#8B5CF6', '#F97316', '#06B6D4', '#84CC16'];
            const color = productColors[index % productColors.length];
            return (
              <div key={product} style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                <div style={{ width: '12px', height: '12px', backgroundColor: color, marginRight: '8px', borderRadius: '2px', opacity: 0.8 }}></div>
                <span>{product} (Tek)</span>
              </div>
            );
          })}
        </>
      ) : (
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: '#F59E0B', marginRight: '8px', borderRadius: '2px', opacity: 0.6 }}></div>
          <span>Planlı Üretim Alanı (Seçilen Ürün)</span>
        </div>
      )}
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <div
          style={{
            width: '12px',
            height: '12px',
            backgroundColor: showSupportedDistricts && selectedProducts && selectedProducts.length > 0 ? '#9CA3AF' : '#3B82F6',
            marginRight: '8px',
            borderRadius: '2px',
            opacity: showSupportedDistricts && selectedProducts && selectedProducts.length > 0 ? 0.12 : 0.05
          }}
        ></div>
        <span style={{ color: showSupportedDistricts && selectedProducts && selectedProducts.length > 0 ? '#9ca3af' : undefined }}>
          Diğer
        </span>
      </div>
    </div>
  </>
  );
}

export default HavzaHaritasi;
