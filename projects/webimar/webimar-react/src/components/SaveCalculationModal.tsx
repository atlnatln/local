import React, { useState, useEffect } from 'react';
import { tokenStorage } from '../utils/tokenStorage';
import styled from 'styled-components';
import { saveCalculationHistory } from '../services/api';
import { toast } from 'react-toastify';
import { UI_MESSAGES } from '../constants/messages';

interface SaveCalculationData {
  title: string;
  description?: string;
  structure_type: string;
  calculation_data: any;
  result: any;
}

const Overlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const Modal = styled.div`
  background: white;
  border-radius: 12px;
  padding: 32px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  max-height: 90vh;
  overflow-y: auto;
`;

const Title = styled.h2`
  color: #2563eb;
  margin-bottom: 24px;
  font-size: 24px;
  font-weight: 700;
  text-align: center;
`;

const Question = styled.p`
  color: #4b5563;
  margin-bottom: 24px;
  font-size: 16px;
  text-align: center;
  line-height: 1.5;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
`;

const Label = styled.label`
  color: #374151;
  font-weight: 600;
  margin-bottom: 8px;
  font-size: 14px;
`;

const Input = styled.input<{ $hasError?: boolean }>`
  padding: 12px 16px;
  border: 2px solid ${props => props.$hasError ? '#dc2626' : '#d1d5db'};
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.2s;
  
  &:focus {
    outline: none;
    border-color: ${props => props.$hasError ? '#dc2626' : '#2563eb'};
  }
`;

const TextArea = styled.textarea<{ $hasError?: boolean }>`
  padding: 12px 16px;
  border: 2px solid ${props => props.$hasError ? '#dc2626' : '#d1d5db'};
  border-radius: 8px;
  font-size: 16px;
  min-height: 80px;
  resize: vertical;
  transition: border-color 0.2s;
  font-family: inherit;
  
  &:focus {
    outline: none;
    border-color: ${props => props.$hasError ? '#dc2626' : '#2563eb'};
  }
`;

const ErrorText = styled.span`
  color: #dc2626;
  font-size: 14px;
  margin-top: 4px;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 24px;
`;

const Button = styled.button<{ $variant?: 'primary' | 'secondary' }>`
  flex: 1;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  
  ${props => props.$variant === 'primary' ? `
    background: #2563eb;
    color: white;
    
    &:hover:not(:disabled) {
      background: #1d4ed8;
    }
  ` : `
    background: #f3f4f6;
    color: #4b5563;
    
    &:hover:not(:disabled) {
      background: #e5e7eb;
    }
  `}
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

interface SaveCalculationModalProps {
  isOpen: boolean;
  onClose: () => void;
  calculationData: {
    structure_type: string;
    calculation_data: any;
    result: any;
    map_coordinates?: { lat: number; lng: number };
    [key: string]: any;
  };
  onSaved?: (savedCalculation: any) => void;
  onRefreshHistory?: () => void; // History'yi refresh etmek için callback
}

const SaveCalculationModal: React.FC<SaveCalculationModalProps> = ({
  isOpen,
  onClose,
  calculationData,
  onSaved,
  onRefreshHistory
}) => {
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ title?: string }>({});
  const [title, setTitle] = useState('');

  // Otomatik başlık oluşturma fonksiyonu
  const generateAutoTitle = (): string => {
    const now = new Date();
    const dateStr = now.toLocaleDateString('tr-TR', { 
      day: '2-digit', 
      month: 'long', 
      year: 'numeric'
    });
    const timeStr = now.toLocaleTimeString('tr-TR', { 
      hour: '2-digit', 
      minute: '2-digit'
    });
    
    // Hesaplama türünü Türkçe'ye çevir
    const typeLabels: Record<string, string> = {
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
    };
    
    const typeLabel = typeLabels[calculationData.calculation_type] || 'Hesaplama';
    
    // Koordinat bilgisi varsa kısaca ekle
    let locationStr = '';
    if (calculationData.map_coordinates) {
      const coords = calculationData.map_coordinates;
      if (coords.lat && coords.lng) {
        locationStr = ` (${coords.lat.toFixed(4)}, ${coords.lng.toFixed(4)})`;
      }
    }
    
    return `${typeLabel} - ${dateStr} ${timeStr}${locationStr}`;
  };

  // Modal her açıldığında otomatik başlığı yeniden oluştur
  useEffect(() => {
    if (isOpen) {
      setTitle(generateAutoTitle());
      setDescription('');
      setErrors({});
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, calculationData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Frontend validation - backend ile uyumlu
    if (!title.trim()) {
      setErrors({ title: 'Hesaplama başlığı gereklidir' });
      return;
    }
    
    if (title.trim().length < 2) {
      setErrors({ title: 'Başlık en az 2 karakter olmalıdır.' });
      return;
    }
    
    setLoading(true);
    setErrors({});
    try {
      const token = tokenStorage.getAccessToken();
      if (!token) {
        toast.error(UI_MESSAGES.AUTH.SESSION_EXPIRED);
        return;
      }
      const dataToSave: SaveCalculationData = {
        ...calculationData,
        title: title.trim(),
        description: description.trim() || undefined,
        // Backend HTML extraction sistemi kullanılacak - frontend temizleme kaldırıldı
        result: calculationData.result
      };
      const savedCalculation = await saveCalculationHistory(dataToSave);
      toast.success(UI_MESSAGES.CALCULATION.SAVE_SUCCESS);
      
      // Hesaplama kaydedildikten sonra history'yi refresh et
      onRefreshHistory?.();
      
      onSaved?.(savedCalculation);
      onClose();
      setTitle(generateAutoTitle());
      setDescription('');
    } catch (error: any) {
      console.error('💾 Save calculation error:', error);
      
      if (error.response?.data?.errors) {
        // Backend validasyon hataları (field bazlı)
        setErrors(error.response.data.errors);
      } else if (error.response?.data?.message) {
        // Genel backend mesajları
        const errorMsg = error.response.data.message;
        if (errorMsg.includes('zaten kaydedilmiş') || errorMsg.includes('duplicate')) {
          setErrors({ title: 'Bu başlık ile zaten bir hesaplamanız mevcut. Farklı bir başlık deneyiniz.' });
        } else {
          toast.error(errorMsg);
        }
      } else if (error.response?.data?.detail) {
        // REST Framework standart hata formatı
        toast.error(error.response.data.detail);
      } else {
        // Genel hata mesajı
        toast.error(error.message || UI_MESSAGES.CALCULATION.SAVE_FAILED);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setTitle('');
    setDescription('');
    setErrors({});
    onClose();
  };

  if (!isOpen) return null;

  return (
    <Overlay onClick={(e) => e.target === e.currentTarget && handleCancel()}>
      <Modal>
        <Title>Hesaplamayı Kaydet</Title>
        <Question>
          Bu hesaplamayı kaydetmek ister misiniz? Daha sonra geçmiş hesaplamalarınızdan erişebilirsiniz.
        </Question>

        <Form onSubmit={handleSubmit}>
          <FormGroup>
            <Label htmlFor="title">Hesaplama Başlığı *</Label>
            <Input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Örn: Sera Hesaplaması - Mart 2025"
              $hasError={!!errors.title}
              maxLength={200}
            />
            {errors.title && <ErrorText>{errors.title}</ErrorText>}
          </FormGroup>

          <FormGroup>
            <Label htmlFor="description">Açıklama (İsteğe bağlı)</Label>
            <TextArea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Bu hesaplama hakkında notlarınız..."
              maxLength={500}
            />
          </FormGroup>

          <ButtonGroup>
            <Button type="button" $variant="secondary" onClick={handleCancel} disabled={loading}>
              İptal
            </Button>
            <Button type="submit" $variant="primary" disabled={loading}>
              {loading ? 'Kaydediliyor...' : 'Kaydet'}
            </Button>
          </ButtonGroup>
        </Form>
      </Modal>
    </Overlay>
  );
};

export default SaveCalculationModal;
