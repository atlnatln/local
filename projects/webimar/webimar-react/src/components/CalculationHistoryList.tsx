import React, { useEffect, useState, memo, useMemo, useCallback } from 'react';
import styled from 'styled-components';
import { deleteCalculationHistory } from '../services/api';
import { getCachedCalculationHistory, clearCalculationHistoryCache, CalculationHistory } from '../services/cachedApi';
import CalculationDetailModal from './CalculationDetailModal';
import { toast } from 'react-toastify';
import { tokenStorage } from '../utils/tokenStorage';
import { useDebounceSearch } from '../hooks/useDebounceSearch';

interface CalculationHistoryListProps {
  isModal?: boolean;
  onClose?: () => void;
  refreshTrigger?: number; // Değişiklik yakalanması için sayı değeri
}

const ModalOverlay = styled.div`
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.18);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const ModalContent = styled.div`
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.13);
  padding: 24px;
  width: 96vw;
  max-width: 700px;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;

  @media (max-width: 600px) {
    border-radius: 8px;
    padding: 12px 6px;
    width: 98vw;
    max-width: 98vw;
    min-width: unset;
    font-size: 15px;
  }
`;

const CloseButton = styled.button`
  position: absolute;
  top: 10px;
  right: 16px;
  background: none;
  border: none;
  font-size: 22px;
  color: #888;
  cursor: pointer;
`;

const HistoryContainer = styled.div<{ $isModal?: boolean }>`
  width: 100%;
  margin-top: ${props => props.$isModal ? '0' : '32px'};
  background: #f8fafc;
  border-radius: 12px;
  padding: 24px 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
`;

const Title = styled.h3`
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 18px;
  color: #2563eb;
  display: flex;
  align-items: center;
  gap: 8px;
`;

// 🚀 OPTIMIZATION: Search Components
const SearchContainer = styled.div`
  position: relative;
  margin-bottom: 20px;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s ease;

  &:focus {
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  }

  &::placeholder {
    color: #9ca3af;
  }
`;

const SearchIndicator = styled.div`
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
  font-size: 14px;
`;

const GroupTitle = styled.div`
  font-size: 15px;
  font-weight: 600;
  color: #555;
  margin: 18px 0 12px 0;
  padding-bottom: 6px;
  border-bottom: 2px solid #e5e7eb;
`;

const CalculationCard = styled.div`
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  border: 1px solid #e5e7eb;
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    transform: translateY(-1px);
  }
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
`;

const CalculationType = styled.div`
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
`;

const CalculationTitle = styled.div<{ $isUntitled?: boolean }>`
  font-size: 14px;
  color: #6b7280;
  font-style: ${props => props.$isUntitled ? 'italic' : 'normal'};
`;

const DateTimeInfo = styled.div`
  text-align: right;
  font-size: 12px;
  color: #9ca3af;
  line-height: 1.4;
`;

const QuickInfo = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 8px 0;
`;

const InfoTag = styled.span`
  background: #f3f4f6;
  color: #374151;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f3f4f6;
`;

const ActionButton = styled.button<{ $variant?: 'primary' | 'secondary' }>`
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: #fff;
  color: #374151;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: #f9fafb;
    border-color: #9ca3af;
  }
  
  ${props => props.$variant === 'primary' && `
    background: #2563eb;
    border-color: #2563eb;
    color: #fff;
    
    &:hover {
      background: #1d4ed8;
    }
  `}
`;

const LocationInfo = styled.div`
  font-size: 12px;
  color: #0ea5e9;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
`;

const LoadingState = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
`;

// Helper functions
function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('tr-TR', { 
    day: '2-digit', 
    month: '2-digit', 
    year: 'numeric' 
  });
}

function formatTime(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleTimeString('tr-TR', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
}

function extractQuickInfo(parameters: any): { area?: string; facility?: string; location?: string } {
  const info: any = {};
  
  if (parameters.alan_m2) {
    info.area = `${parameters.alan_m2.toLocaleString('tr-TR')} m²`;
  }
  
  if (parameters.arazi_vasfi) {
    info.facility = parameters.arazi_vasfi;
  }
  
  return info;
}

// Gruplama fonksiyonu
function groupByDate(history: CalculationHistory[]): [string, CalculationHistory[]][] {
  const groups: Record<string, CalculationHistory[]> = {};
  
  history.forEach(item => {
    const date = new Date(item.created_at);
    const key = `${date.getFullYear()}-${(date.getMonth()+1).toString().padStart(2,'0')}-${date.getDate().toString().padStart(2,'0')}`;
    if (!groups[key]) groups[key] = [];
    groups[key].push(item);
  });
  
  return Object.entries(groups).sort((a,b) => b[0].localeCompare(a[0]));
}

// 🚀 OPTIMIZATION: React.memo ile component optimize et  
const CalculationHistoryList = memo<CalculationHistoryListProps>(({ 
  onClose, 
  isModal = false, 
  refreshTrigger 
}) => {
  const [history, setHistory] = useState<CalculationHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<CalculationHistory | null>(null);
  const [showDetail, setShowDetail] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // 🚀 OPTIMIZATION: Debounced search for performance
  const { filteredItems: filteredHistory, isSearching } = useDebounceSearch(
    history, 
    searchTerm,
    (items: CalculationHistory[], term: string) => items.filter(item => 
      item.calculation_type?.toLowerCase().includes(term.toLowerCase()) ||
      item.title?.toLowerCase().includes(term.toLowerCase()) ||
      item.description?.toLowerCase().includes(term.toLowerCase()) ||
      item.created_at?.toLowerCase().includes(term.toLowerCase())
    ),
    300 // 300ms debounce
  );

  // 🚀 OPTIMIZATION: useCallback ile handler memoization
  const handleDeleteCalculation = useCallback(async (item: CalculationHistory) => {
    if (!window.confirm('Bu hesaplamayı silmek istediğinize emin misiniz?')) return;
    try {
      const token = tokenStorage.getAccessToken();
      if (!token) {
        toast.error('Oturum bulunamadı.');
        return;
      }
      await deleteCalculationHistory(item.id);
      setHistory((prev) => prev.filter((h) => h.id !== item.id));
      clearCalculationHistoryCache(); // 🚀 OPTIMIZATION: Clear cache after delete
      toast.success('Hesaplama başarıyla silindi.');
    } catch (e: any) {
      toast.error('Hesaplama silinirken hata oluştu.');
    }
  }, []); // No dependencies - stable callback

  // 🚀 OPTIMIZATION: useMemo ile type labels caching
  const typeLabels = useMemo(() => ({
    'sera': 'Sera Hesaplaması',
    'bag-evi': 'Bağ Evi Hesaplaması',
    'aricilik': 'Arıcılık Tesisi Hesaplaması',
    'mantar-tesisi': 'Mantar Tesisi Hesaplaması',
    'solucan-tesisi': 'Solucan Tesisi Hesaplaması',
    'buyukbas': 'Büyükbaş Hayvancılık Hesaplaması',
    'kucukbas': 'Küçükbaş Hayvancılık Hesaplaması',
    'kanatli': 'Kanatlı Hayvancılık Hesaplaması',
    'hara': 'Hara Tesisi Hesaplaması',
    'tarimsal-depo': 'Tarımsal Depo Hesaplaması',
    'tarimsal-amacli-depo': 'Tarımsal Amaçlı Depo Hesaplaması',
    'lisansli-depo': 'Lisanslı Depo Hesaplaması',
    'hububat-silo': 'Hububat Silo Hesaplaması',
    'yikama-tesisi': 'Yıkama Tesisi Hesaplaması',
    'kurutma-tesisi': 'Kurutma Tesisi Hesaplaması',
    'soguk-hava-deposu': 'Soğuk Hava Deposu Hesaplaması',
    'zeytinyagi-fabrikasi': 'Zeytinyağı Fabrikası Hesaplaması',
    'zeytinyagi-uretim-tesisi': 'Zeytinyağı Üretim Tesisi Hesaplaması',
    'meyve-sebze-kurutma': 'Meyve-Sebze Kurutma Tesisi Hesaplaması',
    'su-depolama': 'Su Depolama Tesisi Hesaplaması',
    'su-kuyulari': 'Su Kuyuları Hesaplaması',
    'evcil-hayvan': 'Evcil Hayvan Bakımevi Hesaplaması',
    'sut-sigirciligi': 'Süt Sığırcılığı Hesaplaması',
    'besi-sigirciligi': 'Besi Sığırcılığı Hesaplaması',
    'agil-kucukbas': 'Ağıl (Küçükbaş) Hesaplaması',
    'kumes-yumurtaci': 'Kümes (Yumurtacı) Hesaplaması',
    'kumes-etci': 'Kümes (Etçi) Hesaplaması',
    'kumes-gezen': 'Kümes (Gezen) Hesaplaması',
    'kumes-hindi': 'Kümes (Hindi) Hesaplaması',
    'kaz-ordek': 'Kaz-Ördek Hesaplaması',
    'ipek-bocekciligi': 'İpek Böcekçiliği Hesaplaması'
  } as const), []); // useMemo closing

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const token = tokenStorage.getAccessToken();
        if (!token) {
          setError('Oturum bulunamadı.');
          setLoading(false);
          return;
        }
        const data = await getCachedCalculationHistory(); // 🚀 OPTIMIZATION: Use cached API
        setHistory(data);
      } catch (e) {
        setError('Geçmiş yüklenemedi.');
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  // Yeni hesaplama kaydedildiğinde history'yi otomatik refresh et
  const refreshHistory = async () => {
    try {
      const token = tokenStorage.getAccessToken();
      if (!token) return;
      
      const data = await getCachedCalculationHistory(); // 🚀 OPTIMIZATION: Use cached API
      setHistory(data);
    } catch (e) {
      console.error('History refresh failed:', e);
    }
  };

  // Window focus olduğunda veya parent component'ten refresh signali geldiğinde refresh yap
  useEffect(() => {
    const handleFocus = () => {
      refreshHistory();
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, []);

  // refreshTrigger prop değiştiğinde refresh yap
  useEffect(() => {
    if (refreshTrigger) {
      refreshHistory();
    }
  }, [refreshTrigger]);

  const handleOpenDetail = (item: CalculationHistory) => {
    setSelected(item);
    setShowDetail(true);
  };

  const handleCloseDetail = () => {
    setShowDetail(false);
    setSelected(null);
  };

  const handleCopyCalculation = (item: CalculationHistory) => {
    const copyData = {
      title: item.title || 'Başlıksız Hesaplama',
      type: item.calculation_type,
      date: formatDate(item.created_at),
      time: formatTime(item.created_at),
      parameters: item.parameters,
      result: item.result
    };

    const textToCopy = `
📊 ${copyData.title}
🗓️ ${copyData.date} ${copyData.time}
🏗️ ${item.calculation_type}

📋 Parametreler:
${Object.entries(copyData.parameters)
  .map(([key, value]) => `• ${key}: ${value}`)
  .join('\n')}

📈 Sonuçlar:
${Object.entries(copyData.result || {})
  .map(([key, value]) => `• ${key}: ${value}`)
  .join('\n')}
    `.trim();

    navigator.clipboard.writeText(textToCopy).then(() => {
      toast.success('Hesaplama kopyalandı!');
    }).catch(() => {
      toast.error('Kopyalama başarısız');
    });
  };

  // (Fazlalık fonksiyon silindi, yukarıdaki tek tanım kullanılacak)

  if (loading) {
    const loadingContent = <LoadingState>Geçmiş yükleniyor...</LoadingState>;
    return isModal ? (
      <ModalOverlay onClick={onClose}>
        <ModalContent onClick={e => e.stopPropagation()}>
          <CloseButton onClick={onClose}>&times;</CloseButton>
          <HistoryContainer $isModal={isModal}>{loadingContent}</HistoryContainer>
        </ModalContent>
      </ModalOverlay>
    ) : <HistoryContainer $isModal={isModal}>{loadingContent}</HistoryContainer>;
  }
  
  if (error) {
    const errorContent = <EmptyState style={{color:'#dc2626'}}>{error}</EmptyState>;
    return isModal ? (
      <ModalOverlay onClick={onClose}>
        <ModalContent onClick={e => e.stopPropagation()}>
          <CloseButton onClick={onClose}>&times;</CloseButton>
          <HistoryContainer $isModal={isModal}>{errorContent}</HistoryContainer>
        </ModalContent>
      </ModalOverlay>
    ) : <HistoryContainer $isModal={isModal}>{errorContent}</HistoryContainer>;
  }
  
  if (!history.length) {
    const emptyContent = <EmptyState>Henüz bir hesaplama yapılmamış.</EmptyState>;
    return isModal ? (
      <ModalOverlay onClick={onClose}>
        <ModalContent onClick={e => e.stopPropagation()}>
          <CloseButton onClick={onClose}>&times;</CloseButton>
          <HistoryContainer $isModal={isModal}>{emptyContent}</HistoryContainer>
        </ModalContent>
      </ModalOverlay>
    ) : <HistoryContainer $isModal={isModal}>{emptyContent}</HistoryContainer>;
  }

  // 🚀 OPTIMIZATION: Use filtered results for grouping 
  const grouped = groupByDate(filteredHistory);

  const content = (
    <HistoryContainer $isModal={isModal}>
      <Title><span role="img" aria-label="hesap">🧮</span> Hesaplama Geçmişi</Title>
      
      {/* 🚀 OPTIMIZATION: Search Input with Debouncing */}
      <SearchContainer>
        <SearchInput
          type="text"
          placeholder="Hesaplama ara... (tip, başlık, açıklama)"
          value={searchTerm}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
        />
        {isSearching && <SearchIndicator>🔍</SearchIndicator>}
      </SearchContainer>

      {/* Use filtered history instead of original history */}
      {grouped.map(([date, items]) => (
        <div key={date}>
          <GroupTitle>{formatDate(date + 'T00:00:00')}</GroupTitle>
          {items.map((item: CalculationHistory) => {
            const quickInfo = extractQuickInfo(item.parameters);
            const calculationLabel = (typeLabels as Record<string, string>)[item.calculation_type] || item.calculation_type;
            
            return (
              <CalculationCard key={item.id}>
                <CardHeader>
                  <div>
                    <CalculationType>{calculationLabel}</CalculationType>
                    <CalculationTitle $isUntitled={!item.title}>
                      {item.title || 'Başlıksız Hesaplama'}
                    </CalculationTitle>
                  </div>
                  <DateTimeInfo>
                    <div>{formatTime(item.created_at)}</div>
                    <div>{formatDate(item.created_at)}</div>
                  </DateTimeInfo>
                </CardHeader>

                {(quickInfo.area || quickInfo.facility) && (
                  <QuickInfo>
                    {quickInfo.area && <InfoTag>📏 {quickInfo.area}</InfoTag>}
                    {quickInfo.facility && <InfoTag>🏗️ {quickInfo.facility}</InfoTag>}
                  </QuickInfo>
                )}

                {item.description && (
                  <div style={{ fontSize: 13, color: '#6b7280', margin: '8px 0' }}>
                    {item.description}
                  </div>
                )}

                {item.map_coordinates && (
                  <LocationInfo>
                    📍 Harita koordinatları mevcut
                  </LocationInfo>
                )}

                <ActionButtons>
                  <ActionButton 
                    $variant="primary"
                    onClick={() => handleOpenDetail(item)}
                  >
                    Detayları Görüntüle
                  </ActionButton>
                  <ActionButton
                    onClick={() => handleCopyCalculation(item)}
                  >
                    Kopyala
                  </ActionButton>
                  <ActionButton
                    $variant="secondary"
                    onClick={() => handleDeleteCalculation(item)}
                  >
                    Sil
                  </ActionButton>
                </ActionButtons>
              </CalculationCard>
            );
          })}
        </div>
      ))}
      
      {showDetail && selected && (
        <CalculationDetailModal
          isOpen={showDetail}
          onClose={handleCloseDetail}
          calculation={selected}
        />
      )}
    </HistoryContainer>
  );

  if (isModal) {
    return (
      <ModalOverlay onClick={onClose}>
        <ModalContent onClick={e => e.stopPropagation()}>
          <CloseButton onClick={onClose}>&times;</CloseButton>
          {content}
        </ModalContent>
      </ModalOverlay>
    );
  }

  return content;
}); // memo closing

// 🚀 Display name for React DevTools
CalculationHistoryList.displayName = 'CalculationHistoryList';

export default CalculationHistoryList;
