import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';

// CSV'den gelen konum verisi için interface
interface LocationData {
  il: string;
  ilce: string;
  mahalle: string;
  lat: number;
  lon: number;
  // Geriye uyumluluk için eski format alanları
  tur?: 'İLÇE' | 'MAHALLE';
  ad?: string;
  dosya?: string;
  longitude?: number;
  latitude?: number;
}

type IndexedLocationData = LocationData & {
  ilN: string;
  ilceN: string;
  mahalleN: string;
};

// Türkçe karakterleri normalize etme fonksiyonu
const normalizeText = (text: string): string => {
  return text
    .toLowerCase()
    .normalize('NFD') // Unicode normalize
    .replace(/[\u0300-\u036f]/g, '') // Aksanları kaldır
    .replace(/ç/g, 'c')
    .replace(/ğ/g, 'g')
    .replace(/ı/g, 'i')
    .replace(/ö/g, 'o')
    .replace(/ş/g, 's')
    .replace(/ü/g, 'u')
    .trim();
};

// Komponent props
interface LocationAutocompleteProps {
  onLocationSelect: (location: LocationData) => void;
  placeholder?: string;
}

// Styled components
const AutocompleteContainer = styled.div`
  position: relative;
  width: 100%;
`;

const SearchInputContainer = styled.div`
  position: relative;
  width: 100%;
`;

const SearchInput = styled.input`
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
  padding: 12px 16px 12px 40px;
  border: 2px solid #e0e6ed;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  
  @media (max-width: 600px) {
    padding: 10px 8px 10px 34px;
    font-size: 14px;
    border-radius: 6px;
    min-width: 0;
    width: 100%;
    max-width: 100vw;
  }
  
  &:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.2);
    transform: translateY(-1px);
  }
  &::placeholder {
    color: #999;
    transition: color 0.2s ease;
  }
  &:focus::placeholder {
    color: #bbb;
  }
  &:disabled {
    background-color: #f5f7fa;
    cursor: not-allowed;
  }
`;

const SearchIcon = styled.div`
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #7f8c8d;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  @media (max-width: 600px) {
    left: 8px;
    font-size: 15px;
  }
`;

const LoadingSpinner = styled.div`
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  border: 2px solid #e0e6ed;
  border-top-color: #3498db;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  
  @keyframes spin {
    to { transform: translateY(-50%) rotate(360deg); }
  }
`;

const SuggestionsList = styled.ul`
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e0e6ed;
  border-top: none;
  border-radius: 0 0 8px 8px;
  max-height: 300px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  margin: 0;
  padding: 0;
  list-style: none;
  @media (max-width: 600px) {
    border-radius: 0 0 6px 6px;
    max-height: 180px;
    font-size: 13px;
  }
`;

const SuggestionItem = styled.li<{ $isHighlighted: boolean }>`
  padding: 12px 16px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s ease;
  background-color: ${props => props.$isHighlighted ? '#f8f9fa' : 'white'};
  @media (max-width: 600px) {
    padding: 9px 12px;
    font-size: 13px;
  }
  &:hover {
    background-color: #f8f9fa;
  }
  &:last-child {
    border-bottom: none;
  }
`;

const LocationLabel = styled.div`
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 2px;
`;

const LocationSubtext = styled.div`
  font-size: 12px;
  color: #666;
`;

const LocationBadge = styled.span<{ $type: 'İLÇE' | 'MAHALLE' }>`
  display: inline-block;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  margin-right: 8px;
  background-color: ${props => props.$type === 'İLÇE' ? '#3498db' : '#27ae60'};
  color: white;
`;

// CSV parser fonksiyonu
const parseCSV = (csvText: string): LocationData[] => {
  const lines = csvText.trim().split('\n');
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const headers = lines[0].split(',');
  
  return lines.slice(1).map(line => {
    const values = line.split(',');
    return {
      il: values[0],
      ilce: values[1],
      mahalle: values[2],
      lat: parseFloat(values[3]),
      lon: parseFloat(values[4]),
      // Geriye uyumluluk için eski format alanları
      tur: 'MAHALLE' as const,
      ad: values[2], // mahalle adını ad alanına da kopyala
      longitude: parseFloat(values[4]),
      latitude: parseFloat(values[3])
    };
  }).filter(item => item.lat && item.lon && !isNaN(item.lat) && !isNaN(item.lon)); // Geçersiz koordinatları filtrele
};

const LocationAutocomplete: React.FC<LocationAutocompleteProps> = ({
  onLocationSelect,
  placeholder = "İl, ilçe veya mahalle adı yazın... (örn: İzmir, Karşıyaka, Çiğli)"
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [suggestions, setSuggestions] = useState<LocationData[]>([]);
  const [allLocations, setAllLocations] = useState<IndexedLocationData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [hasSelectedLocation, setHasSelectedLocation] = useState(false); // Konum seçimi durumu
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  // Hız için basit indeksler (tek sefer oluşturulur)
  const provinceNormSetRef = useRef<Set<string>>(new Set());
  const districtNormSetRef = useRef<Set<string>>(new Set());
  const provinceIndexRef = useRef<Map<string, IndexedLocationData[]>>(new Map());
  const districtIndexRef = useRef<Map<string, IndexedLocationData[]>>(new Map());

  // CSV dosyasını yükle
  useEffect(() => {
    const loadLocationData = async () => {
      try {
        // Hem local (3001) hem prod için root-relative path kullan.
        // Prod: Nginx isteği Next.js'e iletir (dosya orada olmalı).
        // Dev: React server kendi public klasöründen sunar (CORS derdi yok).
        const response = await fetch('/kml_places_final.csv');
        const csvText = await response.text();
        const locations = parseCSV(csvText) as LocationData[];

        // 1) Normalize alanları bir kez hesapla
        const indexed: IndexedLocationData[] = locations.map(location => ({
          ...location,
          ilN: normalizeText(location.il),
          ilceN: normalizeText(location.ilce),
          mahalleN: normalizeText(location.mahalle)
        }));

        // 2) Bir kez sıralayıp (il/ilçe/mahalle) arama sırasında sort maliyetini kaldır
        indexed.sort((a, b) => {
          if (a.il !== b.il) return a.il.localeCompare(b.il);
          if (a.ilce !== b.ilce) return a.ilce.localeCompare(b.ilce);
          return a.mahalle.localeCompare(b.mahalle);
        });

        // 3) İndeksleri oluştur (O(1) exact match ve daraltma)
        const provinceNormSet = new Set<string>();
        const districtNormSet = new Set<string>();
        const provinceIndex = new Map<string, IndexedLocationData[]>();
        const districtIndex = new Map<string, IndexedLocationData[]>();

        for (const location of indexed) {
          provinceNormSet.add(location.ilN);
          districtNormSet.add(location.ilceN);

          const provinceBucket = provinceIndex.get(location.ilN);
          if (provinceBucket) provinceBucket.push(location);
          else provinceIndex.set(location.ilN, [location]);

          const districtBucket = districtIndex.get(location.ilceN);
          if (districtBucket) districtBucket.push(location);
          else districtIndex.set(location.ilceN, [location]);
        }

        provinceNormSetRef.current = provinceNormSet;
        districtNormSetRef.current = districtNormSet;
        provinceIndexRef.current = provinceIndex;
        districtIndexRef.current = districtIndex;

        setAllLocations(indexed);
        console.log(`📍 ${indexed.length} konum yüklendi`);
      } catch (error) {
        console.error('Konum verileri yüklenemedi:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadLocationData();
  }, []);

  // Debounce: her tuş vuruşunda ağır filtre çalışmasın (daha hızlı tepki için 120ms)
  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 120);
    return () => window.clearTimeout(timeoutId);
  }, [searchTerm]);

  // Arama terimi değiştiğinde suggestions'ı güncelle
  useEffect(() => {
    if (debouncedSearchTerm.length < 1) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    // Kullanıcı kelimeleri farklı sırada girebilir: mahalle→il→ilçe vb.
    // Bu yüzden aramayı token bazlı ve sıra bağımsız yapıyoruz.
    const tokens = debouncedSearchTerm
      .split(/\s+/)
      .map(part => normalizeText(part))
      .filter(part => part.length > 0);

    const normalizedSearchTerm = normalizeText(debouncedSearchTerm);

    // Tek kelime aramalarında, arama terimi bir ile tam eşleşiyorsa
    // sonuçları o ile daralt (aksi halde 12-limit içinde kaybolabiliyor).
    const isSingleWordSearch = tokens.length === 1;
    const provinceNormSet = provinceNormSetRef.current;
    const districtNormSet = districtNormSetRef.current;
    const provinceIndex = provinceIndexRef.current;
    const districtIndex = districtIndexRef.current;

    const hasExactProvinceMatch = isSingleWordSearch && provinceNormSet.has(tokens[0]);

    // Çok kelimeli aramalarda (örn: "uşak ba"), eğer token'lar arasında
    // tam il eşleşmesi varsa sonuçları o il(ler)e daralt.
    const exactProvinceTokens = new Set<string>();
    if (tokens.length >= 2) {
      for (const token of tokens) {
        if (provinceNormSet.has(token)) exactProvinceTokens.add(token);
      }
    }

    const exactDistrictTokens = new Set<string>();
    if (tokens.length >= 2 && exactProvinceTokens.size === 0) {
      for (const token of tokens) {
        if (districtNormSet.has(token)) exactDistrictTokens.add(token);
      }
    }

    let candidates: IndexedLocationData[] = allLocations;

    if (tokens.length >= 2) {
      // İl tam eşleşmesi varsa o ile daralt
      if (exactProvinceTokens.size === 1) {
        const onlyProvince = Array.from(exactProvinceTokens)[0];
        candidates = provinceIndex.get(onlyProvince) ?? [];
      } else if (exactProvinceTokens.size > 1) {
        candidates = Array.from(exactProvinceTokens)
          .flatMap(token => provinceIndex.get(token) ?? []);
      } else if (exactDistrictTokens.size === 1) {
        // İl yok ama ilçe tam eşleştiyse o ilçeye daralt
        const onlyDistrict = Array.from(exactDistrictTokens)[0];
        candidates = districtIndex.get(onlyDistrict) ?? [];
      } else if (exactDistrictTokens.size > 1) {
        candidates = Array.from(exactDistrictTokens)
          .flatMap(token => districtIndex.get(token) ?? []);
      }
    } else if (hasExactProvinceMatch) {
      candidates = provinceIndex.get(tokens[0]) ?? [];
    }

    // Relevance scoring için her lokasyona skor hesapla
    const scoredCandidates = candidates.map(location => {
      let score = 0;
      let matchCount = 0;

      if (tokens.length === 1 && !hasExactProvinceMatch) {
        // Tek kelime arama - tam eşleşme öncelikli
        const term = normalizedSearchTerm;
        
        // Tam eşleşme (en yüksek skor)
        if (location.ilN === term) score += 1000;
        else if (location.ilceN === term) score += 900;
        else if (location.mahalleN === term) score += 800;
        
        // Başlangıç eşleşmesi (yüksek skor)
        else if (location.ilN.startsWith(term)) score += 700;
        else if (location.ilceN.startsWith(term)) score += 600;
        else if (location.mahalleN.startsWith(term)) score += 500;
        
        // İçinde geçme (orta skor)
        else if (location.ilN.includes(term)) score += 400;
        else if (location.ilceN.includes(term)) score += 300;
        else if (location.mahalleN.includes(term)) score += 200;
        
        // Eşleşme yoksa negatif skor
        else score = -1;
      } else {
        // Çok kelimeli arama - tüm tokenlar eşleşmeli
        for (const token of tokens) {
          let tokenMatched = false;
          
          // Tam eşleşme kontrolü
          if (location.ilN === token) {
            score += 100;
            tokenMatched = true;
          } else if (location.ilceN === token) {
            score += 90;
            tokenMatched = true;
          } else if (location.mahalleN === token) {
            score += 80;
            tokenMatched = true;
          }
          // Başlangıç eşleşmesi
          else if (location.ilN.startsWith(token)) {
            score += 70;
            tokenMatched = true;
          } else if (location.ilceN.startsWith(token)) {
            score += 60;
            tokenMatched = true;
          } else if (location.mahalleN.startsWith(token)) {
            score += 50;
            tokenMatched = true;
          }
          // İçinde geçme
          else if (location.ilN.includes(token)) {
            score += 40;
            tokenMatched = true;
          } else if (location.ilceN.includes(token)) {
            score += 30;
            tokenMatched = true;
          } else if (location.mahalleN.includes(token)) {
            score += 20;
            tokenMatched = true;
          }
          
          if (tokenMatched) matchCount++;
        }
        
        // Tüm tokenlar eşleşmediyse negatif skor
        if (matchCount < tokens.length) score = -1;
      }

      return { location, score };
    }).filter(item => item.score > 0); // Sadece eşleşenleri al

    // Score'a göre sırala (en yüksek skordan en düşüğe)
    scoredCandidates.sort((a, b) => b.score - a.score);

    // İlk 30 sonucu al
    const filtered = scoredCandidates.slice(0, 30).map(item => item.location);

    setSuggestions(filtered);
    setShowSuggestions(filtered.length > 0);
    setHighlightedIndex(-1);
  }, [debouncedSearchTerm, allLocations]);

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex(prev => prev > 0 ? prev - 1 : prev);
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0) {
          handleLocationSelect(suggestions[highlightedIndex]);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        setHighlightedIndex(-1);
        break;
    }
  };

  // Konum seçildiğinde
  const handleLocationSelect = (location: LocationData) => {
    // Mahalle / İlçe / İl şeklinde göster
    const displayText = `${location.mahalle} / ${location.ilce} / ${location.il}`;
    
    setSearchTerm(displayText);
    setShowSuggestions(false);
    setHighlightedIndex(-1);
    setHasSelectedLocation(true); // Konum seçildi işaretini koy
    onLocationSelect(location);
  };

  // Input değiştiğinde
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    // Kullanıcı manuel yazmaya başladıysa, seçim flag'ini kaldır
    if (hasSelectedLocation) {
      setHasSelectedLocation(false);
    }
  };

  // Input focus'ta
  const handleInputFocus = () => {
    // Eğer daha önce bir konum seçilmişse, input'u temizle ve yeni arama için hazırla
    if (hasSelectedLocation) {
      setSearchTerm('');
      setHasSelectedLocation(false);
      setSuggestions([]);
      setShowSuggestions(false);
      setHighlightedIndex(-1);
    } else if (suggestions.length > 0) {
      setShowSuggestions(true);
    }
  };

  // Input blur'da (küçük gecikme ile)
  const handleInputBlur = () => {
    setTimeout(() => {
      setShowSuggestions(false);
    }, 200);
  };

  return (
    <AutocompleteContainer>
      <SearchInputContainer>
        <SearchIcon>
          🔍
        </SearchIcon>
        <SearchInput
          ref={inputRef}
          type="text"
          value={searchTerm}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={handleInputFocus}
          onBlur={handleInputBlur}
          placeholder={isLoading ? "Konum verileri yükleniyor..." : placeholder}
          disabled={isLoading}
        />
        {isLoading && <LoadingSpinner />}
      </SearchInputContainer>
      
      {showSuggestions && suggestions.length > 0 && (
        <SuggestionsList>
          {suggestions.map((location, index) => (
            <SuggestionItem
              key={`${location.il}-${location.ilce}-${location.mahalle}-${index}`}
              $isHighlighted={index === highlightedIndex}
              onClick={() => handleLocationSelect(location)}
            >
              <LocationLabel>
                <LocationBadge $type="MAHALLE">
                  MAHALLE
                </LocationBadge>
                <strong>{location.mahalle}</strong>
                <span style={{ color: '#666', fontSize: '0.9em' }}> / {location.ilce} / {location.il}</span>
              </LocationLabel>
              <LocationSubtext>
                {location.il} ili, {location.ilce} ilçesi, {location.mahalle} mahallesi • {location.lat.toFixed(4)}, {location.lon.toFixed(4)}
              </LocationSubtext>
            </SuggestionItem>
          ))}
        </SuggestionsList>
      )}
    </AutocompleteContainer>
  );
};

export default LocationAutocomplete;
