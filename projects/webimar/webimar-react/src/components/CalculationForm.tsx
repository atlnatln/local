import React, { useState, useEffect } from 'react';
import { DetailedCalculationInput, CalculationResult, StructureType } from '../types';
import { calculateBagEvi, calculateSera, calculateHayvancilik, calculateDepoAmbar, calculateStructure } from '../services/api';
import { useStructureTypes } from '../contexts/StructureTypesContext';
import { useLocationValidation } from '../contexts/LocationValidationContext';
import { toast } from 'react-toastify';
import { checkIzmirBelediyesi5000M2 } from '../utils/izmirBelediyesiKontrol';
import AlanKontrol from './AlanKontrol';
import { BagEviCalculator } from '../modules/BagEvi';
import IzmirBelediyesiUyari from './IzmirBelediyesiUyari';
import SmartDetectionFeedback from './CalculationForm/SmartDetectionFeedback';
import FormField from './CalculationForm/FormField';
import AlanKontrolButtons from './CalculationForm/AlanKontrolButtons';
import FormSectionComponent from './CalculationForm/FormSectionComponent';
import { BagEviForm } from '../modules/BagEvi';
import TarimsalDepoFormFields from './CalculationForm/TarimsalDepoFormFields';
import { FormValidator } from './CalculationForm/FormValidator';
import { useTypewriter } from './CalculationForm/useTypewriter';
import {
  FormContainer,
  FormTitle,
  FormContent,
  FormGrid,
  FormGroup,
  Label,
  SubmitButton,
  ErrorMessage,
  RequiredIndicator,
  AnimatedSelectContainer,
  AnimatedSelect,
  TypewriterPlaceholder
} from './CalculationForm/styles';
import SuTahsisModal from './Modals/SuTahsisModal';
import LocationSelectionModal from './Modals/LocationSelectionModal';

console.log('🔧 CalculationForm LOADED - V2.1 (Mantar Tesisi Added)');

// Helper to create calculator function for a specific type
const createCalculator = (type: StructureType) => (data: any) => calculateStructure(type, data);

// Simple API service mapping
const apiService = {
  calculations: {
    // Specific implementations
    bag_evi: calculateBagEvi,
    sera: calculateSera,
    hayvancilik: calculateHayvancilik,
    depo_ambar: calculateDepoAmbar,
    
    // Generic implementations using calculateStructure
    solucan_tesisi: createCalculator('solucan-tesisi'),
    mantar_tesisi: createCalculator('mantar-tesisi'),
    aricilik: createCalculator('aricilik'),
    hububat_silo: createCalculator('hububat-silo'),
    tarimsal_depo: createCalculator('tarimsal-depo'),
    lisansli_depo: createCalculator('lisansli-depo'),
    yikama_tesisi: createCalculator('yikama-tesisi'),
    kurutma_tesisi: createCalculator('kurutma-tesisi'),
    meyve_sebze_kurutma: createCalculator('meyve-sebze-kurutma'),
    zeytinyagi_fabrikasi: createCalculator('zeytinyagi-fabrikasi'),
    su_depolama: createCalculator('su-depolama'),
    su_kuyulari: createCalculator('su-kuyulari'),
    zeytinyagi_uretim_tesisi: createCalculator('zeytinyagi-uretim-tesisi'),
    soguk_hava_deposu: createCalculator('soguk-hava-deposu'),
    sut_sigirciligi: createCalculator('sut-sigirciligi'),
    agil_kucukbas: createCalculator('agil-kucukbas'),
    kumes_yumurtaci: createCalculator('kumes-yumurtaci'),
    kumes_etci: createCalculator('kumes-etci'),
    kumes_gezen: createCalculator('kumes-gezen'),
    kumes_hindi: createCalculator('kumes-hindi'),
    kaz_ordek: createCalculator('kaz-ordek'),
    hara: createCalculator('hara'),
    ipek_bocekciligi: createCalculator('ipek-bocekciligi'),
    evcil_hayvan: createCalculator('evcil-hayvan'),
    besi_sigirciligi: createCalculator('besi-sigirciligi'),
    
    // Legacy/Fallback keys if needed
    gübreli_alan: calculateDepoAmbar, 
  }
};

console.log('🔧 CalculationForm LOADED - V2.1 (Mantar Tesisi Added)');

// Backend constants.py ile senkronize yapı türü labels - artık types dosyasından import ediliyor

// Arazi tipi interface'i API'den gelen data için
interface AraziTipi {
  id: number;
  ad: string;
}

interface CalculationFormComponentProps {
  calculationType: StructureType;
  onResult: (result: CalculationResult) => void;
  onCalculationStart: () => void;
  selectedCoordinate?: { lat: number; lng: number } | null;
  onAraziVasfiChange?: (araziVasfi: string) => void;
  emsalTuru?: string; // Seçili emsal türü
  onEmsalTuruChange?: (emsalTuru: string) => void; // Emsal türü değiştiğinde çağrılacak fonksiyon
  onFormDataChange?: (formData: any) => void; // Form verisi değiştiğinde çağrılacak
  onMapCoordinatesChange?: (coordinates: any) => void; // Harita koordinatları değiştiğinde çağrılacak
}

const CalculationForm: React.FC<CalculationFormComponentProps> = ({
  calculationType,
  onResult,
  onCalculationStart,
  selectedCoordinate,
  onAraziVasfiChange,
  emsalTuru,
  onEmsalTuruChange,
  onFormDataChange,
  onMapCoordinatesChange
}) => {
  const { structureTypeLabels, getFilteredYapiTurleri, getFilteredAraziTipleri } = useStructureTypes();
  
  // Create consolidated calculator instance for bağ evi calculations
  const bagEviCalculator = new BagEviCalculator();
  
  // Create form validator instance
  const formValidator = new FormValidator();
  
  const [formData, setFormData] = useState<DetailedCalculationInput & {
    dut_bahcesi_alani?: number;
    dut_agaci_sayisi?: number;
  }>({
    alan_m2: 0,
    arazi_vasfi: '', // Başlangıçta boş olacak ki placeholder görünsün
    emsal_turu: 'marjinal' // Default olarak marjinal (%20) seçili
  });
  // Dut Bahçesi Kontrolü için modal state
  const [dutBahcesiKontrolOpen, setDutBahcesiKontrolOpen] = useState(false);

  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [araziTipleri, setAraziTipleri] = useState<AraziTipi[]>([]);
  const [araziTipleriLoading, setAraziTipleriLoading] = useState(true);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [selectFocused, setSelectFocused] = useState(false);
  const [selectOpen, setSelectOpen] = useState(false);
  const [suTahsisBelgesi, setSuTahsisBelgesi] = useState<boolean>(false);
  const [showSuTahsisModal, setShowSuTahsisModal] = useState(false);
  const [showLocationModal, setShowLocationModal] = useState(false);
  
  // İzmir Belediyesi Uyarı Modali
  const [showIzmirUyari, setShowIzmirUyari] = useState(false);
  const [izmirUyariShown, setIzmirUyariShown] = useState(false); // İzmir uyarısı daha önce gösterildi mi
  const [izmirUyariData, setIzmirUyariData] = useState<{
    arazi_alani_m2: number;
    yapiTuru: string;
    koordinatlar?: { lat: number; lng: number };
    pendingResult?: CalculationResult;
    pendingFormData?: any; // Hesaplama için hazır form data'sı
  } | null>(null);
  
  // Location validation context
  const { state: locationState, isWaterRestrictedForLivestock } = useLocationValidation();
  
  // Dikili alan kontrolü için
  const [dikiliKontrolOpen, setDikiliKontrolOpen] = useState(false);
  const [dikiliKontrolSonucu, setDikiliKontrolSonucu] = useState<any>(null);


  // Typewriter efekti için
  const { displayedText } = useTypewriter('Arazi vasfınızı seçiniz', 80);

  // Form alanlarının aktif olup olmadığını kontrol eden fonksiyon
  // NOT: Koordinat seçilmese bile form aktif olsun, kontrol handleSubmit'te yapılsın
  const isFormDisabled = false; // !selectedCoordinate; -> Her zaman false yap
  
  // Koordinat seçilip seçilmediğini ayrı bir flag olarak tut
  const hasCoordinate = !!selectedCoordinate;
  
  // External emsal türü ile senkronizasyon
  useEffect(() => {
    if (emsalTuru && emsalTuru !== formData.emsal_turu) {
      setFormData(prev => ({ ...prev, emsal_turu: emsalTuru as 'marjinal' | 'mutlak_dikili' }));
    }
  }, [emsalTuru, formData.emsal_turu]);

  // Form data değiştiğinde parent'a haber ver
  useEffect(() => {
    if (onFormDataChange) {
      onFormDataChange(formData);
    }
  }, [formData, onFormDataChange]);

  // Selected coordinate değiştiğinde parent'a haber ver
  useEffect(() => {
    if (onMapCoordinatesChange && selectedCoordinate) {
      onMapCoordinatesChange(selectedCoordinate);
    }
  }, [selectedCoordinate, onMapCoordinatesChange]);

  // API'den arazi tiplerini çek - yapı türüne göre filtrele
  useEffect(() => {
    const fetchAraziTipleri = async () => {
      try {
        setAraziTipleriLoading(true);
        
        // Yapı türü labelını kullanarak filtreleme yap
        const yapiTuruLabel = structureTypeLabels && structureTypeLabels[calculationType];
        console.log(`🎯 CalculationForm - Yapı türü: ${calculationType} → Label: ${yapiTuruLabel}`);
        
        // Filtrelenen arazi tiplerini context üzerinden çek
        const filteredAraziTipleri = await getFilteredAraziTipleri(yapiTuruLabel);
        console.log(`🎯 CalculationForm - ${yapiTuruLabel || calculationType} için filtrelenmiş arazi tipleri:`, 
          filteredAraziTipleri.map(a => `${a.id}: ${a.ad}`).join(', '));
        
        setAraziTipleri(filteredAraziTipleri);
        
      } catch (error) {
        console.error('Arazi tipleri API hatası:', error);
      } finally {
        setAraziTipleriLoading(false);
      }
    };

    // structureTypeLabels yüklendikten sonra çalıştır
    if (structureTypeLabels && calculationType) {
      fetchAraziTipleri();
    }
  }, [calculationType, structureTypeLabels, getFilteredAraziTipleri]);

  // Custom event listener for opening dikili kontrol modal
  useEffect(() => {
    const handleOpenDikiliKontrol = () => {
      setDikiliKontrolOpen(true);
    };

    window.addEventListener('openDikiliKontrol', handleOpenDikiliKontrol);
    
    return () => {
      window.removeEventListener('openDikiliKontrol', handleOpenDikiliKontrol);
    };
  }, []);

  // 🎯 Smart Auto-Detection Helper Fonksiyonları
  const getSmartDetectionStatus = (fieldName: string) => {
    if (!dikiliKontrolSonucu) return null;
    
    if (dikiliKontrolSonucu.manualOverride && dikiliKontrolSonucu.overrideField === fieldName) {
      return 'manual';
    }
    
    if (dikiliKontrolSonucu.directTransfer) {
      return 'map';
    }
    
    return null;
  };

  const handleResetToMapValue = (fieldName: string) => {
    if (!dikiliKontrolSonucu?.originalMapValues) return;
    
    const originalValue = dikiliKontrolSonucu.originalMapValues[fieldName];
    if (originalValue !== undefined) {
      console.log(`🔄 ${fieldName} harita değerine geri döndürülüyor: ${originalValue}`);
      
      // Form değerini güncelle
      setFormData(prev => ({
        ...prev,
        [fieldName]: originalValue
      }));
      
      // Akıllı algılamayı sıfırla
      setDikiliKontrolSonucu((prev: any) => ({
        ...prev,
        directTransfer: true,
        manualOverride: false,
        overrideField: undefined
      }));
    }
  };

  const renderSmartDetectionFeedback = (fieldName: string) => {
    const status = getSmartDetectionStatus(fieldName);
    if (!status) return null;

    if (status === 'manual' && dikiliKontrolSonucu?.originalMapValues) {
      const originalValue = dikiliKontrolSonucu.originalMapValues[fieldName];
      
      return (
        <SmartDetectionFeedback 
          variant="manual"
          icon="✏️"
          text={`Manuel değer kullanılıyor (Harita: ${originalValue?.toLocaleString()} m²)`}
          onResetToMap={() => handleResetToMapValue(fieldName)}
        />
      );
    }

    if (status === 'map') {
      return (
        <SmartDetectionFeedback 
          variant="map"
          icon="🗺️"
          text="Harita verisi kullanılıyor"
        />
      );
    }

    return null;
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    // 🔒 GÜÇLÜ GÜVENLİK KONTROLÜ: Multi-level validation
    if (!e) {
      console.error('❌ handleInputChange: Event is null/undefined');
      return;
    }

    if (!e.target) {
      console.error('❌ handleInputChange: Event target is null/undefined', {
        event: e,
        eventType: typeof e,
        eventKeys: e ? Object.keys(e) : 'N/A'
      });
      return;
    }

    // Target properties validation
    const target = e.target;
    if (!('name' in target) || !('value' in target)) {
      console.error('❌ handleInputChange: Target missing name or value properties', {
        target,
        hasName: 'name' in target,
        hasValue: 'value' in target,
        targetType: (target as any).tagName || typeof target
      });
      return;
    }

    const { name } = target;
    // Value extraction - checkbox vs. regular input
    const rawValue = (target as HTMLInputElement).type === 'checkbox' 
      ? (target as HTMLInputElement).checked 
      : (target as HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement).value;
    
    // Type safe value - most form fields expect string values
    const value = typeof rawValue === 'boolean' ? String(rawValue) : rawValue;

    // Sayısal alanlar için sadece rakam kabul et (örn. 'e', '+', '-' gibi inputları da temizler)
    // Not: Bu alanlar m² / adet gibi tam sayı bekler.
    const digitsOnlyFields = [
      'alan_m2',
      'tarla_alani',
      'dikili_alani',
      'zeytinlik_alani',
      'sera_alani_m2',
      'silo_taban_alani_m2',
      'zeytin_agac_sayisi',
      'zeytin_agac_adedi',
      'tapu_zeytin_agac_adedi',
      'mevcut_zeytin_agac_adedi'
    ];

    const normalizedValue = (
      typeof value === 'string' && digitsOnlyFields.includes(name)
        ? value.replace(/[^\d]/g, '')
        : value
    );

    // Name validation - must be non-empty string
    if (!name || typeof name !== 'string') {
      console.error('❌ handleInputChange: Invalid name property', {
        name,
        nameType: typeof name,
        target
      });
      return;
    }

    console.log(`🔄 CalculationForm - handleInputChange: ${name} = "${normalizedValue}" (validated)`);
    
    // 🎯 AKILLI ALGILA (Çözüm 3): Harita verisi varken manuel değer girilirse otomatik olarak manuel moda geç
    const alanInputlari = ['alan_m2', 'dikili_alani', 'tarla_alani', 'zeytinlik_alani'];
    if (alanInputlari.includes(name) && dikiliKontrolSonucu?.directTransfer && normalizedValue !== '') {
      const numericValue = Number(normalizedValue);
      const currentMapValue = name === 'alan_m2' ? dikiliKontrolSonucu.dikiliAlan :  // alan_m2 de dikili alan değerini kullanır
                             name === 'dikili_alani' ? dikiliKontrolSonucu.dikiliAlan :
                             name === 'tarla_alani' ? dikiliKontrolSonucu.tarlaAlani :
                             name === 'zeytinlik_alani' ? dikiliKontrolSonucu.zeytinlikAlani : 0;
      
      // Sadece değer farklıysa akıllı algılamayı tetikle
      if (numericValue !== currentMapValue) {
        console.log(`📝 AKILLI ALGILA: ${name} manuel olarak değiştirildi (${currentMapValue} → ${numericValue})`);
        console.log(`🔄 Harita verisi pasif ediliyor, manuel değer öncelikli hale getiriliyor`);
        
        setDikiliKontrolSonucu((prev: any) => ({
          ...prev,
          directTransfer: false, // Harita verisini pasif et
          manualOverride: true,  // Manuel değer kullanıldığını işaretle
          overrideField: name,   // Hangi alan override edildiğini sakla
          originalMapValues: {   // Orijinal harita değerlerini sakla (geri dönüş için)
            ...prev.originalMapValues,
            alan_m2: prev.dikiliAlan || 0,      // alan_m2 için de dikili alan değerini sakla
            dikili_alani: prev.dikiliAlan || 0,
            tarla_alani: prev.tarlaAlani || 0,
            zeytinlik_alani: prev.zeytinlikAlani || 0
          }
        }));
      }
    }
    
    setFormData(prev => ({
      ...prev,
      [name]: (name === 'alan_m2' || name === 'silo_taban_alani_m2' || name === 'tarla_alani' || name === 'dikili_alani' || name === 'zeytinlik_alani' || name === 'zeytin_agac_sayisi' || name === 'zeytin_agac_adedi' || name === 'tapu_zeytin_agac_adedi' || name === 'mevcut_zeytin_agac_adedi') ? Number(normalizedValue) : normalizedValue
    }));

    console.log(`✅ CalculationForm - State updated for ${name}`);
    
    // Debug: Güncel formData state'ini log'la
    setTimeout(() => {
      console.log(`📊 CalculationForm - Current formData.arazi_vasfi: "${formData.arazi_vasfi}"`);
      console.log(`📊 CalculationForm - Should show Tarla+Zeytinlik inputs: ${formData.arazi_vasfi === 'Tarla + Zeytinlik'}`);
    }, 100);

    // Arazi vasfı seçildiğinde dropdown'ı kapat ve parent'a bildir
    if (name === 'arazi_vasfi' && normalizedValue) {
      console.log(`🎯 CalculationForm - Arazi vasfı seçildi: "${normalizedValue}"`);
      setSelectOpen(false);

      // --- YENİ: Arazi vasfı değiştiğinde tüm bağımlı alanları sıfırla ---
      console.log(`🧹 Arazi vasfı değişti - Form alanları temizleniyor`);
      setFormData(prev => ({
        ...prev,
        arazi_vasfi: normalizedValue,
        // Temel alanlar - alan_m2'yi sadece bağ evi için sıfırla, diğer hesaplamalarda koru
        alan_m2: calculationType === 'bag-evi' ? 0 : prev.alan_m2,
        tarla_alani: 0,
        dikili_alani: 0,
        zeytinlik_alani: 0,
        // Zeytin / ağaç sayısı alanları
        zeytin_agac_sayisi: 0,
        zeytin_agac_adedi: 0,
        tapu_zeytin_agac_adedi: 0,
        mevcut_zeytin_agac_adedi: 0,
        // Dut bahçesi alanları (ipek böcekçiliği için)
        dut_bahcesi_alani: 0,
        dut_agaci_sayisi: 0,
        // Depo/sera özel alanları
        depo_alani: 0,
        sera_alani_m2: 0,
        silo_taban_alani_m2: 0,
        // Manuel kontrol sonucu ve eklenen ağaç listesi temizlenir
        manuel_kontrol_sonucu: undefined,
        eklenenAgaclar: undefined
      }));

      // Dikili kontrol modal'dan gelen sonucu temizle
      setDikiliKontrolSonucu(null);

      // Validation hatalarını temizle
      setValidationErrors({});

      console.log(`✅ Form tüm alanları sıfırlandı - Arazi vasfı: "${normalizedValue}"`);
      
      // Parent component'a arazi vasfı değiştiğini bildir
      onAraziVasfiChange?.(normalizedValue);
      
      // Filtrelenmiş yapı türlerini al ve konsola yazdır
      getFilteredYapiTurleri(normalizedValue).then(filteredYapiTurleri => {
        console.log(`🎯 Arazi vasfı "${normalizedValue}" için filtrelenmiş yapı türleri:`, 
          filteredYapiTurleri.map(y => `${y.id}: ${y.ad}`).join(', '));
      }).catch(error => {
        console.error('Filtreleme hatası:', error);
      });
    }

    // Clear validation error when user starts typing
    if (validationErrors[name]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  // Dikili alan kontrolü handler'ları
  const handleDikiliKontrolOpen = () => {
    setDikiliKontrolOpen(true);
  };

  const handleDikiliKontrolClose = () => {
    setDikiliKontrolOpen(false);
  };

  const handleDikiliKontrolSuccess = (result: any) => {
    try {
      console.log('�💥💥 CALLBACK CAGIRILDI TAMAM!');
      console.log('🎯 RESULT:', result);
      console.log('🎯 result?.eklenenAgaclar:', result?.eklenenAgaclar);
      
      setDikiliKontrolSonucu(result);
      console.log('✅✅✅ STATE GUNCELLENDI!');
      console.log('� DIKILI KONTROL SONUCU SET EDILDI:', result);
    } catch (error) {
      console.error('🚨 ERROR in handleDikiliKontrolSuccess:', error);
    }
    console.log('🔍 DEBUG - mevcut formData.arazi_vasfi:', formData.arazi_vasfi);
    
    // 🔥 YENİ: Temizleme işlemi kontrolü
    if (result?.clearAll === true) {
      console.log('🧹 Temizleme işlemi algılandı - FormData sıfırlanıyor');
      setFormData(prev => ({
        ...prev,
        dikili_alani: 0,
        tarla_alani: 0,
        zeytinlik_alani: 0,
        alan_m2: formData.arazi_vasfi === 'Dikili vasıflı' ? 0 : prev.alan_m2
      }));
      
      // Validation hatalarını da temizle
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors.dikili_alani;
        delete newErrors.tarla_alani;
        delete newErrors.zeytinlik_alani;
        if (formData.arazi_vasfi === 'Dikili vasıflı') {
          delete newErrors.alan_m2;
        }
        return newErrors;
      });
      
      console.log('✅ Form tamamen temizlendi - Harita verileri sıfırlandı');
      setDikiliKontrolOpen(false);
      return; // Temizleme işleminde sonraki kodları çalıştırma
    }
    
    // Doğrudan aktarım (ağaç hesaplaması olmadan) veya kontrol sonucu (preliminary check dahil)
    const isDirectTransfer = result?.directTransfer === true;
    const isSuccessfulControl = result?.dikiliAlanKontrolSonucu?.type === 'success' && 
                               result?.dikiliAlanKontrolSonucu?.yeterlilik?.yeterli === true;
    const isPreliminaryCheck = result?.preliminaryCheck === true; // Yeni: preliminary check flag'i
    
    console.log('🔍 DEBUG - isDirectTransfer:', isDirectTransfer);
    console.log('🔍 DEBUG - isSuccessfulControl:', isSuccessfulControl);
    console.log('🔍 DEBUG - isPreliminaryCheck:', isPreliminaryCheck);
    
    // Değer aktarım koşulları: Doğrudan aktarım VEYA başarılı kontrol VEYA preliminary check
    // "Dikili vasıflı" için sadece dikiliAlan kontrolü, 
    // "Tarla + Zeytinlik" için tarlaAlani ve zeytinlikAlani kontrolü,
    // "… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf" için sadece dikiliAlan kontrolü,
    // diğerleri için hem dikiliAlan hem tarlaAlani kontrolü
    const hasRequiredAreas = formData.arazi_vasfi === 'Dikili vasıflı' 
      ? result?.dikiliAlan 
      : formData.arazi_vasfi === 'Tarla + Zeytinlik'
      ? (result?.tarlaAlani && result?.zeytinlikAlani)
      : formData.arazi_vasfi === '… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf'
      ? result?.dikiliAlan
      : formData.arazi_vasfi === '… Adetli Zeytin Ağacı bulunan tarla'
      ? result?.tarlaAlani
      : (result?.dikiliAlan && result?.tarlaAlani);
    
    console.log('🔍 DEBUG - hasRequiredAreas hesaplama:');
    console.log('  - arazi_vasfi:', formData.arazi_vasfi);
    console.log('  - result.dikiliAlan:', result?.dikiliAlan);
    console.log('  - hasRequiredAreas final:', hasRequiredAreas);
    
    const shouldEnterIfBlock = (isDirectTransfer || isSuccessfulControl || isPreliminaryCheck) && hasRequiredAreas;
    console.log('🔍 DEBUG - shouldEnterIfBlock:', shouldEnterIfBlock);
    
    if (shouldEnterIfBlock) {
      console.log('🔍 DEBUG - IF BLOCK ENTERED - Area transfer başlıyor');
      
      const dikiliAlan = result.dikiliAlan; // Dikili alan değeri
      const tarlaAlani = result.tarlaAlani; // Tarla alanı
      const zeytinlikAlani = result.zeytinlikAlani; // Zeytinlik alanı
      
      console.log('🔍 DEBUG - Alan değerleri:');
      console.log('  - dikiliAlan:', dikiliAlan);
      console.log('  - tarlaAlani:', tarlaAlani);
      console.log('  - zeytinlikAlani:', zeytinlikAlani);
      
      // "Dikili vasıflı" arazi tipi için özel alan_m2 güncellemesi
      if (formData.arazi_vasfi === 'Dikili vasıflı') {
        console.log('🔍 DEBUG - Dikili vasıflı branch');
        setFormData(prev => ({
          ...prev,
          alan_m2: dikiliAlan, // Dikili vasıflı için alan_m2 = dikili alan
          dikili_alani: dikiliAlan,
          tarla_alani: tarlaAlani
        }));
        
        // Validation hatalarını temizle (alan_m2 dahil)
        setValidationErrors(prev => {
          const newErrors = { ...prev };
          delete newErrors.alan_m2;
          delete newErrors.dikili_alani;
          delete newErrors.tarla_alani;
          return newErrors;
        });
        
        console.log(`🚀 Dikili vasıflı için özel aktarım:`);
        console.log(`  - alan_m2: ${dikiliAlan} m² (dikili alan)`);
        console.log(`  - dikili_alani: ${dikiliAlan} m²`);
        console.log(`  - tarla_alani: ${tarlaAlani} m²`);
      } else if (formData.arazi_vasfi === 'Tarla + Zeytinlik') {
        console.log('🔍 DEBUG - Tarla + Zeytinlik branch');
        // "Tarla + Zeytinlik" arazi tipi için özel aktarım
        setFormData(prev => ({
          ...prev,
          tarla_alani: tarlaAlani,
          zeytinlik_alani: zeytinlikAlani
        }));
        
        // Validation hatalarını temizle
        setValidationErrors(prev => {
          const newErrors = { ...prev };
          delete newErrors.tarla_alani;
          delete newErrors.zeytinlik_alani;
          return newErrors;
        });
        
        console.log(`🚀 Tarla + Zeytinlik için aktarım:`);
        console.log(`  - tarla_alani: ${tarlaAlani} m²`);
        console.log(`  - zeytinlik_alani: ${zeytinlikAlani} m²`);
      } else if (formData.arazi_vasfi === '… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf') {
        console.log('🔍 DEBUG - … Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf branch ENTERED');
        console.log('🔍 DEBUG - setFormData çağrılıyor, dikiliAlan:', dikiliAlan);
        console.log('🔍 DEBUG - mevcut formData.dikili_alani (değişmeden önce):', formData.dikili_alani);
        
        // "… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf" arazi tipi için özel aktarım
        setFormData(prev => {
          console.log('🔍 DEBUG - setFormData içinde prev:', prev);
          const newData = {
            ...prev,
            dikili_alani: dikiliAlan // Sadece dikili alanı güncelle
          };
          console.log('🔍 DEBUG - setFormData içinde newData:', newData);
          return newData;
        });
        
        // Validation hatalarını temizle
        setValidationErrors(prev => {
          const newErrors = { ...prev };
          delete newErrors.dikili_alani;
          console.log('🔍 DEBUG - Validation errors temizlendi, dikili_alani hatası silindi');
          return newErrors;
        });
        
        console.log(`🚀 … Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf için aktarım:`);
        console.log(`  - dikili_alani: ${dikiliAlan} m²`);
        
        // Extra debug - check after state update (with timeout to allow state to settle)
        setTimeout(() => {
          console.log('🔍 DEBUG - 100ms sonra formData kontrolü (state güncellendikten sonra)');
          console.log('🔍 DEBUG - setFormData sonrası beklenen dikili_alani:', dikiliAlan);
        }, 100);
        
      } else {
        console.log('🔍 DEBUG - Diğer arazi tipleri branch');
        // Diğer arazi tipleri için normal aktarım
        setFormData(prev => ({
          ...prev,
          dikili_alani: dikiliAlan,
          tarla_alani: tarlaAlani
        }));
        
        // Validation hatalarını temizle
        setValidationErrors(prev => {
          const newErrors = { ...prev };
          delete newErrors.dikili_alani;
          delete newErrors.tarla_alani;
          return newErrors;
        });
      }
      
      console.log('🔍 DEBUG - Area transfer tamamlandı');
      
      // Konsol mesajları
      if (isDirectTransfer) {
        if (formData.arazi_vasfi === 'Tarla + Zeytinlik') {
          console.log(`🚀 Doğrudan aktarım - Poligon verileri forma aktarıldı:`);
          console.log(`  - Tarla alanı: ${tarlaAlani} m²`);
          console.log(`  - Zeytinlik alanı: ${zeytinlikAlani} m²`);
          console.log(`📝 Not: Bu arazi tipinde ağaç hesaplaması gerekmez`);
        } else if (formData.arazi_vasfi === '… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf') {
          console.log(`🚀 Doğrudan aktarım - Poligon verileri forma aktarıldı:`);
          console.log(`  - Dikili alan: ${dikiliAlan} m²`);
          console.log(`📝 Not: Bu arazi tipinde sadece dikili alan bilgisi alınır`);
        } else {
          console.log(`🚀 Doğrudan aktarım - Poligon verileri forma aktarıldı:`);
          console.log(`  - Dikili alan: ${dikiliAlan} m²`);
          console.log(`  - Tarla alanı: ${tarlaAlani} m²`);
          console.log(`📝 Not: Ağaç hesaplaması yapılmadı, sadece alan bilgileri aktarıldı`);
        }
      } else {
        console.log(`✅ Dikili alan kontrolü başarılı - Değerler aktarıldı:`);
        console.log(`  - Dikili alan: ${dikiliAlan} m²`);
        console.log(`  - Tarla alanı: ${tarlaAlani} m²`);
        console.log(`📊 Ağaçların teorik kapladığı alan: ${result?.dikiliAlanKontrolSonucu?.alanBilgisi?.kaplanAlan} m² (yoğunluk kontrolü için)`);
        console.log(`🎯 Yeterlilik oranı: %${result?.dikiliAlanKontrolSonucu?.yeterlilik?.oran?.toFixed(1)} (min: %${result?.dikiliAlanKontrolSonucu?.yeterlilik?.minimumOran})`);
      }
    } else {
      console.log('🔍 DEBUG - IF BLOCK SKIPPED - Area transfer yapılmadı');
      console.log('🔍 DEBUG - Sebep analizi:');
      console.log('  - (isDirectTransfer || isSuccessfulControl):', (isDirectTransfer || isSuccessfulControl));
      console.log('  - hasRequiredAreas:', hasRequiredAreas);
      console.log('  - Combined condition:', (isDirectTransfer || isSuccessfulControl) && hasRequiredAreas);
      console.log('❌ Dikili alan kontrolü başarısız - Yeterlilik kriteri sağlanmadı, değer aktarımı yapılmadı');
    }
  };

  // İzmir Belediyesi uyarı kontrolü yapan helper fonksiyon
  const checkIzmirBelediyesiUyari = (result: CalculationResult) => {
    // Eğer zaten İzmir uyarısı gösterilmişse direkt sonucu gönder
    if (izmirUyariShown) {
      console.log('İzmir uyarısı daha önce gösterildi, direkt sonuç gönderiliyor');
      onResult(result);
      return;
    }
    
    // Arazi alanını alabilmek için formData'dan alan bilgisini al
    const araziAlani = formData.alan_m2 || 0;
    
    // İzmir Belediyesi uyarı kontrolü - hesaplamadan SONRA (API sonucunda)
    const izmirKontrolSonuc = checkIzmirBelediyesi5000M2(araziAlani, calculationType, selectedCoordinate || undefined);
    
    if (izmirKontrolSonuc.uyariGosterilsinMi) {
      // İzmir uyarı modalini göster
      setIzmirUyariData({
        arazi_alani_m2: araziAlani,
        yapiTuru: calculationType,
        koordinatlar: selectedCoordinate || undefined,
        pendingResult: result
      });
      setShowIzmirUyari(true);
      setIzmirUyariShown(true); // Uyarı gösterildi olarak işaretle
    } else {
      // Doğrudan sonucu gönder
      onResult(result);
    }
  };

  // İzmir uyarı modal handler fonksiyonları
  const handleIzmirUyariClose = () => {
    setShowIzmirUyari(false);
    setIzmirUyariData(null);
  };

  // Direct calculation - İzmir uyarısı sonrası hesaplama (ana handleSubmit mantığı ile aynı)
  const handleDirectCalculation = async (pendingFormData: any) => {
    setIsLoading(true);
    setError(null);
    console.log('📞 CalculationForm - Calling onCalculationStart after İzmir warning');
    onCalculationStart();
    console.log('✅ CalculationForm - onCalculationStart called');

    try {
      // calculationType'ı API service key formatına dönüştür (- yerine _)
      const calculationKey = calculationType.replace(/-/g, '_');
      console.log(`🔄 CalculationType: ${calculationType} → Key: ${calculationKey}`);
      
      const calculationFunction = apiService.calculations[calculationKey as keyof typeof apiService.calculations];
      
      if (!calculationFunction) {
        throw new Error(`Hesaplama türü desteklenmiyor: ${calculationType}`);
      }
      
      const apiResult = await calculationFunction(pendingFormData);
      console.log('🎯 API Result after İzmir warning:', apiResult);
      
      // Ana handleSubmit ile aynı response processing mantığı
      // UX-optimized format'ı kontrol et
      const isUXFormat = (apiResult as any).result && (apiResult as any).explanation && (apiResult as any).meta;
      
      if (isUXFormat) {
        // UX-optimized format'tan dönüştür
        const uxResult = (apiResult as any);
        
        const result: CalculationResult = {
          success: uxResult.result?.success || false,
          message: uxResult.result?.main_message || uxResult.explanation?.detailed_message || 'Hesaplama tamamlandı',
          data: {
            // UX format'tan veri aktar
            izin_durumu: uxResult.result?.status === 'tesis_yapilabilir' ? 'izin_verilebilir' : 'izin_verilemez',
            ana_mesaj: uxResult.result?.main_message || 'Hesaplama tamamlandı',
            mesaj: uxResult.explanation?.detailed_message || '',
            // Summary'den tüm hesaplama detaylarını aktar
            ...uxResult.summary,
            // Advanced details'tan orijinal mesajı al (HTML içeriği için)
            html_mesaj: uxResult.advanced_details?.data?.mesaj || uxResult.advanced_details?.data?.html_mesaj || '',
            // Form verilerini ekle
            alan_m2: pendingFormData.alan_m2,
            // Meta bilgileri
            calculation_type: uxResult.meta?.calculation_type,
            timestamp: uxResult.meta?.timestamp
          }
        };
        
        console.log('🔄 UX Format Transformed Result (Direct):', result);
        onResult(result);
        return;
      }
      
      // Legacy format için mapping düzeltmesi: results, detaylar ve data altındaki tüm alanları üst seviyeye merge et
      let baseResult: CalculationResult = {
        success: (apiResult as any).success || false,
        message: (apiResult as any).sonuc || (apiResult as any).message || 'Hesaplama tamamlandı',
        data: {
          ...(apiResult as any),
          ...(apiResult as any).results || {},
          ...(apiResult as any).detaylar || {},
          ...(apiResult as any).data || {},
          // results field'ını da doğrudan ekle
          results: (apiResult as any).results || {},
        }
      };
      
      console.log('🔄 Legacy Format Transformed Result (Direct):', baseResult);
      onResult(baseResult);
      
    } catch (err) {
      console.log('❌ CalculationForm - Error occurred in direct calculation:', err);
      const errorMessage = err instanceof Error ? err.message : 'Hesaplama sırasında bir hata oluştu';
      setError(errorMessage);
      
      const errorResult: CalculationResult = {
        success: false,
        message: errorMessage,
        data: {
          izin_durumu: 'izin_verilemez',
          ana_mesaj: errorMessage
        }
      };
      
      onResult(errorResult);
    } finally {
      setIsLoading(false);
    }
  };

  const handleIzmirUyariContinue = () => {
    if (izmirUyariData?.pendingResult) {
      // Pending result varsa direkt sonucu göster
      setShowIzmirUyari(false);
      setIzmirUyariData(null);
      onResult(izmirUyariData.pendingResult);
    } else if (izmirUyariData?.pendingFormData) {
      // Form data'sı varsa hesaplama yap
      setShowIzmirUyari(false);
      setIzmirUyariData(null);
      
      // Hesaplama işlemini tetikle
      handleDirectCalculation(izmirUyariData.pendingFormData);
      return;
    }
    handleIzmirUyariClose();
  };

  const validateForm = (): boolean => {
    // Debug logging ekle
    console.log('🔍 CalculationForm - validateForm called');
    console.log('📊 CalculationForm - Current formData:', formData);
    console.log('📊 CalculationForm - Current calculationType:', calculationType);
    
    // Use the separated FormValidator
    const validationResult = formValidator.validateForm(formData, calculationType);
    
    console.log('📊 CalculationForm - ValidationResult:', validationResult);
    
    // Su tahsis belgesi kontrolü
    const needsWaterPermit = WATER_DEPENDENT_FACILITIES.includes(calculationType) && 
                (locationState.kmlCheckResult?.insideYasPolygons?.length || 0) > 0;
    
    if (needsWaterPermit && !suTahsisBelgesi) {
      validationResult.errors.suTahsisBelgesi = 'Su tahsis belgesi durumunuzu belirtmeniz gerekiyor';
      validationResult.isValid = false;
    }
    
    console.log('📊 CalculationForm - Final validationResult:', validationResult);
    setValidationErrors(validationResult.errors);
    return validationResult.isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // En temel log'lar - filtre edilmesin diye
    window.console?.log?.('�🚀🚀 SUBMIT BUTTON CLICKED - FORM SUBMITTED');
    window.console?.log?.('📍 Coordinate check:', selectedCoordinate);
    
    // Koordinat kontrolü
    if (!selectedCoordinate) {
      window.console?.log?.('❌❌❌ NO COORDINATE - OPENING MODAL');
      setShowLocationModal(true);
      return;
    }
    
    // Validation
    if (!validateForm()) {
      window.console?.log?.('❌❌❌ VALIDATION FAILED');
      window.console?.log?.('🔍 VALIDATION ERRORS:', validationErrors);
      return;
    }

    // İzmir Belediyesi uyarı kontrolü - hesaplamadan ÖNCE
    const araziAlani = formData.alan_m2 || 0;
    const izmirKontrolSonuc = checkIzmirBelediyesi5000M2(araziAlani, calculationType, selectedCoordinate || undefined);
    
    if (izmirKontrolSonuc.uyariGosterilsinMi) {
      // İzmir uyarı modalini göster - hesaplama yapmadan
      setIzmirUyariData({
        arazi_alani_m2: araziAlani,
        yapiTuru: calculationType,
        koordinatlar: selectedCoordinate || undefined,
        pendingFormData: { ...formData, latitude: selectedCoordinate?.lat, longitude: selectedCoordinate?.lng } // Form data'sını sakla
      });
      setShowIzmirUyari(true);
      console.log('⚠️ İzmir Belediyesi uyarısı gösteriliyor - hesaplama beklemeye alındı');
      return; // Hesaplama yapmadan dur
    }

    window.console?.log?.('✅✅✅ STARTING CALCULATION');

    // 🍇 Bağ evi için özel ön kontrol
    if (calculationType === 'bag-evi' || calculationType === 'tarimsal-depo') {
      const yapiTuru = calculationType === 'tarimsal-depo' ? 'Tarımsal depo' : 'Bağ evi';
      
      // Dikili kontrol sonucu varsa ve preliminaryCheck flag'i varsa uygunluğu kontrol et
      if (dikiliKontrolSonucu?.preliminaryCheck && dikiliKontrolSonucu?.dikiliAlanKontrolSonucu) {
        const sonuc = dikiliKontrolSonucu.dikiliAlanKontrolSonucu;
        
        // Ağaç sayısı yeterli mi kontrol et
        if (sonuc.yeterlilik?.yeterli === true) {
          console.log(`✅ ${yapiTuru} için ağaç sayısı yeterli - hesaplama devam ediyor`);
        } else if (sonuc.yeterlilik?.kriter2 === true) {
          console.log(`⚠️ ${yapiTuru} için alan yeterli ama ağaç sayısı yetersiz - hesaplama devam ediyor`);
          // Kullanıcıya bildiri göster
          toast.warning(
            `Alan uygun ancak dekara dikili ağaç sayısı yetersiz. ${yapiTuru} yapılabilir ama ideal koşullar sağlanmamış.`,
            { position: 'top-center', autoClose: 5000 }
          );
        } else {
          // Her iki kriter de başarısız - ama hesaplama yine de devam etsin, sonuçta uyarı gösterilsin
          console.log(`⚠️ ${yapiTuru} için ağaç sayısı ve alan kriterleri yetersiz - hesaplama devam ediyor ama uyarı gösterilecek`);
          toast.warning(
            `Mevcut alanınız ve ağaç sayınız ${yapiTuru.toLowerCase()} için yetersiz görünüyor. Hesaplama yapılacak ama sonuçları değerlendirin.`,
            { position: 'top-center', autoClose: 6000 }
          );
        }
      } else {
        // Dikili kontrol yapılmamış - bu normal durum da olabilir
        console.log(`ℹ️ ${yapiTuru} için dikili kontrol yapılmamış - normal hesaplama devam ediyor`);
      }
    }

    setIsLoading(true);
    setError(null);
    console.log('📞 CalculationForm - Calling onCalculationStart');
    onCalculationStart();
    console.log('✅ CalculationForm - onCalculationStart called');

    try {
      // calculationType'ı API service key formatına dönüştür (- yerine _)
      const calculationKey = calculationType.replace(/-/g, '_');
      console.log(`🔄 CalculationType: ${calculationType} → Key: ${calculationKey}`);
      console.log('📋 Available calculations:', Object.keys(apiService.calculations));
      console.log('🔍 Looking for key:', calculationKey);
      console.log('✅ Key exists?', calculationKey in apiService.calculations);
      console.log('🎯 Full apiService.calculations object:', apiService.calculations);
      
      // İpek böcekçiliği için dut_bahcesi_var_mi alanını default true yap
      const finalFormData = { ...formData };
      
      if (calculationType === 'ipek-bocekciligi' && finalFormData.dut_bahcesi_var_mi === undefined) {
        finalFormData.dut_bahcesi_var_mi = true;
        console.log('🌳 İpek böcekçiliği için dut_bahcesi_var_mi default true olarak ayarlandı');
      }

      // Su kuyusu için kapalı su havzası bilgisini ekle
      if (calculationType === 'su-kuyulari') {
        finalFormData.kapaliSuHavzasiIcinde = (locationState.kmlCheckResult?.insideYasPolygons?.length || 0) > 0;
        console.log('💧 Su kuyusu için kapalı su havzası bilgisi eklendi:', finalFormData.kapaliSuHavzasiIcinde);
      }

      // Büyükbaş hayvancılık için büyük ova alanı bilgisini ekle
      if (calculationType === 'sut-sigirciligi' || calculationType === 'besi-sigirciligi') {
        finalFormData.buyuk_ova_icinde = (locationState.kmlCheckResult?.insideOvaPolygons?.length || 0) > 0;
        console.log('🏞️ Büyükbaş hayvancılık için büyük ova alanı bilgisi eklendi:', finalFormData.buyuk_ova_icinde);
      }

      // Bağ evi için konsolide hesaplama motoru ile form verisini hazırla
      if (calculationType === 'bag-evi') {
        const bagEviFormData = {
          calculationType,
          arazi_vasfi: formData.arazi_vasfi,
          alan_m2: formData.alan_m2,
          tarla_alani: formData.tarla_alani,
          dikili_alani: formData.dikili_alani,
          zeytinlik_alani: formData.zeytinlik_alani,
          zeytin_agac_sayisi: formData.zeytin_agac_sayisi,
          zeytin_agac_adedi: formData.zeytin_agac_adedi,
          tapu_zeytin_agac_adedi: formData.tapu_zeytin_agac_adedi,
          mevcut_zeytin_agac_adedi: formData.mevcut_zeytin_agac_adedi,
          manuel_kontrol_sonucu: dikiliKontrolSonucu || formData.manuel_kontrol_sonucu,
          latitude: formData.latitude,
          longitude: formData.longitude
        };

        // Konsolide hesaplama motoru ile backend için hazırla
        const preparedData = bagEviCalculator.prepareFormDataForBackend(bagEviFormData);
        
        // Hazırlanan verileri finalFormData'ya aktar
        Object.assign(finalFormData, preparedData);
        
        console.log('🍇 Bağ evi için konsolide hesaplama motoru kullanıldı');
        console.log('🔄 Arazi vasfı:', formData.arazi_vasfi);
        console.log('� dikiliKontrolSonucu state:', dikiliKontrolSonucu);
        console.log('�📊 Hazırlanan veriler:', preparedData);
        console.log('🎯 preparedData içinde manuel_kontrol_sonucu var mı?', preparedData.manuel_kontrol_sonucu ? 'VAR' : 'YOK');
      }

      // Tarımsal depo için bağ evi mantığı ile form verisini hazırla
      if (calculationType === 'tarimsal-depo') {
        const tarimsalDepoFormData = {
          calculationType,
          arazi_vasfi: formData.arazi_vasfi,
          depo_alani: formData.depo_alani, // Ana fark: depo alanı
          alan_m2: formData.alan_m2,
          tarla_alani: formData.tarla_alani,
          dikili_alani: formData.dikili_alani,
          zeytinlik_alani: formData.zeytinlik_alani,
          zeytin_agac_sayisi: formData.zeytin_agac_sayisi,
          zeytin_agac_adedi: formData.zeytin_agac_adedi,
          tapu_zeytin_agac_adedi: formData.tapu_zeytin_agac_adedi,
          mevcut_zeytin_agac_adedi: formData.mevcut_zeytin_agac_adedi,
          manuel_kontrol_sonucu: dikiliKontrolSonucu || formData.manuel_kontrol_sonucu,
          latitude: formData.latitude,
          longitude: formData.longitude
        };

        // Bağ evi calculator'ı kullanarak verileri hazırla (aynı mantık)
        const preparedData = bagEviCalculator.prepareFormDataForBackend(tarimsalDepoFormData);
        
        // Hazırlanan verileri finalFormData'ya aktar
        Object.assign(finalFormData, preparedData);
        
        console.log('🏪 Tarımsal depo için bağ evi mantığı kullanıldı');
        console.log('🔄 Arazi vasfı:', formData.arazi_vasfi);
        console.log('📦 Depo alanı:', formData.depo_alani);
        console.log('📊 Hazırlanan veriler:', preparedData);
      }

      // Seçilen koordinat bilgisini form dataya ekle
      if (selectedCoordinate) {
        finalFormData.latitude = selectedCoordinate.lat;
        finalFormData.longitude = selectedCoordinate.lng;
        console.log('📍 Koordinat bilgisi form dataya eklendi:', selectedCoordinate);
      }

      // Emsal türü bilgisini ekle (bağ evi hariç)
      if (calculationType !== 'bag-evi') {
        if (calculationType !== 'ipek-bocekciligi') {
          finalFormData.emsal_turu = formData.emsal_turu || 'marjinal';
          console.log(`📐 Emsal türü eklendi: ${finalFormData.emsal_turu} (${finalFormData.emsal_turu === 'marjinal' ? '%20' : '%5'})`);
        }
      }
      
      // Dinamik emsal gerektiren tipler için emsal_orani ekle
      const dynamicEmsalTypes = [
        'mantar-tesisi',
        'aricilik',
        'hububat-silo',
        'tarimsal-silo',
        'solucan-tesisi',
        'tarimsal-depo',
        'lisansli-depo',
        'kurutma-tesisi',
        'meyve-sebze-kurutma',
        'yikama-tesisi',
        'su-depolama',
        'soguk-hava-deposu',
        // Hayvancılık tesisleri - dinamik emsal
        'sut-sigirciligi',
        'agil-kucukbas',
        'kumes-yumurtaci',
        'kumes-etci',
        'kumes-gezen',
        'kumes-hindi',
        'kaz-ordek',
        'hara',
        /* 'ipek-bocekciligi', */
        'evcil-hayvan',
        'besi-sigirciligi'
      ];
      if (dynamicEmsalTypes.includes(calculationType)) {
        // emsal_turu 'marjinal' ise 0.20, 'mutlak_dikili' ise 0.05
        let emsalOrani = 0.20;
        if (finalFormData.emsal_turu === 'mutlak_dikili') {
          emsalOrani = 0.05;
        }
        finalFormData.emsal_orani = emsalOrani;
        console.log(`📐 Emsal oranı eklendi: ${emsalOrani} (${finalFormData.emsal_turu})`);
      }

      // API'ye gönderilecek payload'u debug için yazdır
      console.log('📦 API payload:', finalFormData);

      // Explicitly debug each step
      console.log('🔬 Debug Info:');
      console.log('- calculationType:', calculationType);
      console.log('- calculationKey:', calculationKey);
      console.log('- typeof calculationKey:', typeof calculationKey);
      console.log('- apiService:', apiService);
      console.log('- apiService.calculations:', apiService.calculations);
      console.log('- Object.keys(apiService.calculations):', Object.keys(apiService.calculations));
      console.log('- Has solucan_tesisi key?:', 'solucan_tesisi' in apiService.calculations);
      console.log('- apiService.calculations.solucan_tesisi:', apiService.calculations.solucan_tesisi);
      
      const calculationFunction = apiService.calculations[calculationKey as keyof typeof apiService.calculations];
      console.log('🎲 calculationFunction:', calculationFunction);
      
      if (!calculationFunction) {
        console.error(`❌ Function not found for key: ${calculationKey}`);
        console.error('❌ Available keys:', Object.keys(apiService.calculations));
        throw new Error(`Hesaplama türü desteklenmiyor: ${calculationType}`);
      }
      const apiResult = await calculationFunction(finalFormData);
      console.log('🎯 API Result:', apiResult);
      
      // Debug: Hara ve İpek Böcekçiliği response'larını log'la
      if (calculationType === 'hara' || calculationType === 'ipek-bocekciligi') {
        console.log(`${calculationType} API Response:`, JSON.stringify(apiResult, null, 2));
      }
      
      // İpek böcekçiliği için özel response mapping
      if (calculationType === 'ipek-bocekciligi' && (apiResult as any).sonuc && typeof (apiResult as any).sonuc === 'object') {
        const ipekResult = (apiResult as any).sonuc;
        const result: CalculationResult = {
          success: (apiResult as any).success || false,
          message: ipekResult.mesaj_metin || (apiResult as any).message || 'İpek böcekçiliği hesaplama tamamlandı',
          data: {
            // İpek böcekçiliği sonuclarını aktar
            ...ipekResult,
            // Ana mesajı ayarla
            ana_mesaj: ipekResult.mesaj_metin || ipekResult.mesaj || 'İpek böcekçiliği hesaplama tamamlandı',
            // HTML mesajını ayarla
            mesaj: ipekResult.mesaj || '',
            // Diğer alanları map et
            alan_m2: formData.alan_m2,
            maksimum_kapasite: ipekResult.maksimum_taban_alani,
            maksimum_taban_alani: ipekResult.maksimum_taban_alani,
            maksimum_yapilasma_alani_m2: ipekResult.maksimum_yapilasma_alani_m2
          }
        };
        
        console.log('🔄 İpek Böcekçiliği Transformed Result:', result);
        checkIzmirBelediyesiUyari(result);
        return;
      }
      
      // Backend response'unu frontend CalculationResult formatına dönüştür
      // UX-optimized format'ı kontrol et
      const isUXFormat = (apiResult as any).result && (apiResult as any).explanation && (apiResult as any).meta;
      
      if (isUXFormat) {
        // UX-optimized format'tan dönüştür
        const uxResult = (apiResult as any);
        
        // 🍇 Bağ evi/Tarımsal depo için özel işlem
        if (calculationType === 'bag-evi' || calculationType === 'tarimsal-depo') {
          const yapiTuru = calculationType === 'tarimsal-depo' ? 'Tarımsal depo' : 'Bağ evi';

          // Backend dikili validasyon sonucunu kontrol et
          let uyariMesaji = '';

          const backendDikiliValidasyon = (apiResult as any).results?.dikili_validasyon;
          const izinDurumu = (apiResult as any).results?.izin_durumu;
          const backendSuccess = (apiResult as any).success;

          if (backendSuccess && izinDurumu?.includes('izin_verilebilir')) {
            uyariMesaji = `<div style="color: #059669; font-weight: bold; margin-bottom: 8px;">✅ Ağaç sayısı yeterli - ${yapiTuru} yapılabilir</div>`;
          } else if (backendDikiliValidasyon?.gecerli === false) {
            uyariMesaji = `<div style="color: #dc2626; font-weight: bold; margin-bottom: 8px;">❌ Ağaç sayısı yetersiz - ${yapiTuru} yapılamaz</div>`;
          } else if (!backendSuccess) {
            uyariMesaji = `<div style="color: #dc2626; font-weight: bold; margin-bottom: 8px;">❌ Hesaplama başarısız - ${yapiTuru} yapılamaz</div>`;
          }

          // Ana mesajı uyarı ile birleştir - KULLANICI DOSTU MESAJLARI KORU
          const originalMessage = uxResult.result?.main_message || uxResult.explanation?.detailed_message || 'Hesaplama tamamlandı';

          // Backend'den gelen kullanıcı dostu mesaj varsa onu kullan, yoksa uyarı ile birleştir
          let combinedMessage;
          
          // Backend'den kullanıcı dostu HTML mesajı kontrol et
          const hasUserFriendlyMessage = originalMessage && 
            (originalMessage.includes('<b>') || originalMessage.includes('<div>') || originalMessage.length > 100);
            
          if (hasUserFriendlyMessage) {
            // Backend'den detaylı kullanıcı dostu HTML mesajı geldi - doğrudan kullan (wrapper ekleme)
            combinedMessage = originalMessage;
            console.log(`🍇 ${yapiTuru} için backend'den gelen kullanıcı dostu HTML mesajı kullanılıyor`);
          } else {
            // Basit mesaj - uyarı ile birleştir
            combinedMessage = uyariMesaji + originalMessage;
            console.log(`🍇 ${yapiTuru} için uyarı mesajı ile birleştirildi`);
          }

          console.log(`🍇 ${yapiTuru} için özel mesaj hazırlandı:`, combinedMessage);
          
          const result: CalculationResult = {
            success: (apiResult as any).success || false,
            message: combinedMessage,
            data: {
              // UX format'tan veri aktar
              izin_durumu: uxResult.result?.status === 'tesis_yapilabilir' ? 'izin_verilebilir' : 'izin_verilemez',
              ana_mesaj: combinedMessage,
              mesaj: combinedMessage,
              // Dikili kontrol sonucunu da ekle
              dikili_kontrol_sonucu: dikiliKontrolSonucu?.dikiliAlanKontrolSonucu,
              // Ağaç verilerini de ekle (API'nin beklediği format)
              eklenenAgaclar: dikiliKontrolSonucu?.eklenenAgaclar || [],
              // Summary'den tüm hesaplama detaylarını aktar
              ...uxResult.summary,
              // Advanced details'tan orijinal mesajı al (HTML içeriği için)
              html_mesaj: combinedMessage,
              // Form verilerini ekle
              alan_m2: formData.alan_m2,
              // Meta bilgileri
              calculation_type: uxResult.meta?.calculation_type,
              timestamp: uxResult.meta?.timestamp
            }
          };
          
          // Debug: dikiliKontrolSonucu içeriğini kontrol et (Tarla+Zeytinlik yolu)
          console.log('🔍 DEBUG (Tarla+Zeytinlik) - dikiliKontrolSonucu tam içeriği:', dikiliKontrolSonucu);
          console.log('🔍 DEBUG (Tarla+Zeytinlik) - dikiliKontrolSonucu?.eklenenAgaclar:', dikiliKontrolSonucu?.eklenenAgaclar);
          console.log('🔍 DEBUG (Tarla+Zeytinlik) - result.data.eklenenAgaclar:', result.data.eklenenAgaclar);
          
          console.log(`🔄 ${yapiTuru} Format Transformed Result:`, result);
          console.log('📞 CalculationForm - Calling checkIzmirBelediyesiUyari with:', result);
          checkIzmirBelediyesiUyari(result);
          console.log('✅ CalculationForm - checkIzmirBelediyesiUyari called successfully');
          return;
        }
        
        const result: CalculationResult = {
          success: uxResult.result?.success || false,
          message: uxResult.result?.main_message || uxResult.explanation?.detailed_message || 'Hesaplama tamamlandı',
          data: {
            // UX format'tan veri aktar
            izin_durumu: uxResult.result?.status === 'tesis_yapilabilir' ? 'izin_verilebilir' : 'izin_verilemez',
            ana_mesaj: uxResult.result?.main_message || 'Hesaplama tamamlandı',
            mesaj: uxResult.explanation?.detailed_message || '',
            // Summary'den tüm hesaplama detaylarını aktar
            ...uxResult.summary,
            // Advanced details'tan orijinal mesajı al (HTML içeriği için)
            html_mesaj: uxResult.advanced_details?.data?.mesaj || uxResult.advanced_details?.data?.html_mesaj || '',
            // Form verilerini ekle
            alan_m2: formData.alan_m2,
            // Meta bilgileri
            calculation_type: uxResult.meta?.calculation_type,
            timestamp: uxResult.meta?.timestamp
          }
        };
        
        console.log('🔄 UX Format Transformed Result:', result);
        console.log('📞 CalculationForm - Calling checkIzmirBelediyesiUyari with:', result);
        checkIzmirBelediyesiUyari(result);
        console.log('✅ CalculationForm - checkIzmirBelediyesiUyari called successfully');
        return;
      }
      
      // Legacy format için mapping düzeltmesi: results, detaylar ve data altındaki tüm alanları üst seviyeye merge et
      let baseResult: CalculationResult = {
        success: (apiResult as any).success || false,
        message: (apiResult as any).sonuc || (apiResult as any).message || 'Hesaplama tamamlandı',
        data: {
          ...(apiResult as any),
          ...(apiResult as any).results || {},
          ...(apiResult as any).detaylar || {},
          ...(apiResult as any).data || {},
          // results field'ını da doğrudan ekle
          results: (apiResult as any).results || {},
        }
      };
      
      // 🍇 Bağ evi/Tarımsal depo için Legacy format özel işlem
      if (calculationType === 'bag-evi' || calculationType === 'tarimsal-depo') {
        const yapiTuru = calculationType === 'tarimsal-depo' ? 'Tarımsal depo' : 'Bağ evi';
        
        // Backend dikili validasyon sonucunu kontrol et
        const backendDikiliValidasyon = (apiResult as any).results?.dikili_validasyon;
        const izinDurumu = (apiResult as any).results?.izin_durumu;
        const backendSuccess = (apiResult as any).success;
        
        console.log('🍇 Backend dikili validasyon:', backendDikiliValidasyon);
        console.log('🍇 Backend izin durumu:', izinDurumu);
        console.log('🍇 Backend success:', backendSuccess);
        
        // Orijinal mesajı al - KULLANICI DOSTU MESAJLARI KORU  
        const originalMessage = baseResult.message;
        
        // Backend'den gelen kullanıcı dostu mesaj varsa onu kullan, yoksa basit mesaj bırak
        let combinedMessage;
        
        // Backend'den kullanıcı dostu HTML mesajı kontrol et
        const hasUserFriendlyMessage = originalMessage && 
          (originalMessage.includes('<b>') || originalMessage.includes('<div>') || originalMessage.length > 100);
          
        if (hasUserFriendlyMessage) {
          // Backend'den detaylı kullanıcı dostu HTML mesajı geldi - doğrudan kullan
          combinedMessage = originalMessage;
          console.log(`🍇 ${yapiTuru} için backend'den gelen kullanıcı dostu HTML mesajı kullanılıyor (legacy)`);
        } else {
          // Basit mesaj - doğrudan kullan (eski uyarı wrapper mantığını kaldırdık)
          combinedMessage = originalMessage;
          console.log(`🍇 ${yapiTuru} için backend mesajı doğrudan kullanılıyor (legacy)`);
        }
        
        baseResult = {
          ...baseResult,
          message: combinedMessage,
          data: {
            ...baseResult.data,
            ana_mesaj: combinedMessage,
            mesaj: combinedMessage,
            html_mesaj: combinedMessage,
            // Dikili kontrol sonucunu da ekle
            dikili_kontrol_sonucu: dikiliKontrolSonucu?.dikiliAlanKontrolSonucu,
            // Ağaç verilerini de ekle (API'nin beklediği format)
            eklenenAgaclar: dikiliKontrolSonucu?.eklenenAgaclar || [],
          }
        };
        
        // Debug: dikiliKontrolSonucu içeriğini kontrol et
        console.log('🔍 DEBUG - dikiliKontrolSonucu tam içeriği:', dikiliKontrolSonucu);
        console.log('🔍 DEBUG - dikiliKontrolSonucu?.eklenenAgaclar:', dikiliKontrolSonucu?.eklenenAgaclar);
        console.log('🔍 DEBUG - baseResult.data.eklenenAgaclar:', baseResult.data.eklenenAgaclar);
        
        console.log(`🔄 ${yapiTuru} Legacy Format Transformed Result:`, baseResult);
      }
      
      console.log('🔄 Transformed Result:', baseResult);
      console.log('📞 CalculationForm - Calling checkIzmirBelediyesiUyari with:', baseResult);
      checkIzmirBelediyesiUyari(baseResult);
      console.log('✅ CalculationForm - checkIzmirBelediyesiUyari called successfully');
    } catch (err) {
      console.log('❌ CalculationForm - Error occurred:', err);
      const errorMessage = err instanceof Error ? err.message : 'Hesaplama sırasında bir hata oluştu';
      setError(errorMessage);
      
      const errorResult: CalculationResult = {
        success: false,
        message: errorMessage,
        data: {
          izin_durumu: 'izin_verilemez',
          ana_mesaj: errorMessage
        }
      };
      
      console.log('📞 CalculationForm - Calling onResult with error:', errorResult);
      onResult(errorResult);
      console.log('✅ CalculationForm - onResult called with error');
    } finally {
      setIsLoading(false);
    }
  };

  // Nokta seçilmeden uyarı gösteren bileşen
  const LocationPrompt: React.FC = () => (
    <div style={{
      background: '#fff3cd',
      color: '#856404',
      border: '1px solid #ffeeba',
      borderRadius: 8,
      padding: 24,
      textAlign: 'center',
      fontSize: 18,
      margin: '32px 0'
    }}>
      <strong>Lütfen harita üzerinde arazinizin yakınında veya üzerinde bir nokta seçiniz.</strong>
    </div>
  );

  // Formun render kısmı
  if (!selectedCoordinate) {
    return <LocationPrompt />;
  }

  return (
    <FormContainer>
      <FormTitle>
        Hesaplama
        {structureTypeLabels && calculationType && structureTypeLabels[calculationType] && (
          <span style={{
            display: 'block',
            fontSize: 18,
            fontWeight: 500,
            color: '#1976d2',
            marginTop: 4
          }}>
            {structureTypeLabels[calculationType]}
          </span>
        )}
      </FormTitle>
      <FormContent>
        {error && <ErrorMessage>{error}</ErrorMessage>}



        <form onSubmit={handleSubmit}>
          {/* Temel Bilgiler */}
          <FormSectionComponent title="📊 Temel Bilgiler">
            <FormGrid>
              {/* Bağ evi dışındaki hesaplamalar için genel alan inputu */}
              {calculationType !== 'bag-evi' && (
                <FormField
                  label="Alan (m²)"
                  name="alan_m2"
                  type="number"
                  value={formData.alan_m2 || ''}
                  onChange={handleInputChange}
                  placeholder="Örn: 5000"
                  min="1"
                  max="200000"
                  step="1"
                  required
                  error={validationErrors.alan_m2}
                  disabled={!hasCoordinate}
                  onClick={() => setShowLocationModal(true)}
                />
              )}

              {/* Arıcılık için özel kovan sayısı girişi */}
              {calculationType === 'aricilik' && (
                <FormField
                  label="Kovan Sayısı (Opsiyonel)"
                  name="kovan_sayisi"
                  type="number"
                  value={formData.kovan_sayisi || ''}
                  onChange={handleInputChange}
                  placeholder="Minimum 50 adet"
                  min="50"
                  max="10000"
                  step="1"
                  error={validationErrors.kovan_sayisi}
                  disabled={!hasCoordinate}
                  helpText="Boş bırakırsanız araziye göre maksimum kapasite hesaplanır. Girdiğiniz kovan sayısına göre emsal alanı kontrolü yapılır."
                />
              )}

              <FormGroup>
                <Label>
                  Arazi Vasfı <RequiredIndicator>*</RequiredIndicator>
                </Label>
                <AnimatedSelectContainer>
                  <AnimatedSelect
                    name="arazi_vasfi"
                    value={formData.arazi_vasfi}
                    onChange={handleInputChange}
                    onFocus={() => setSelectFocused(true)}
                    onBlur={() => {
                      setSelectFocused(false);
                      setSelectOpen(false);
                    }}
                    onMouseDown={() => {
                      if (isFormDisabled) {
                        setShowLocationModal(true);
                      } else {
                        setSelectOpen(true);
                      }
                    }}
                    onClick={() => {
                      if (isFormDisabled) {
                        setShowLocationModal(true);
                      } else {
                        setSelectOpen(true);
                      }
                    }}
                    required
                    disabled={araziTipleriLoading || !hasCoordinate}
                    $hasValue={!!formData.arazi_vasfi}
                    style={{
                      opacity: !hasCoordinate ? 0.5 : 1,
                      cursor: !hasCoordinate ? 'not-allowed' : 'pointer',
                      backgroundColor: !hasCoordinate ? '#f5f5f5' : undefined
                    }}
                  >
                    {araziTipleriLoading ? (
                      <option>Arazi tipleri yükleniyor...</option>
                    ) : (
                      <>
                        <option value="" disabled style={{ display: 'none' }}>
                          {/* Gizli placeholder option */}
                        </option>
                        {calculationType === 'ipek-bocekciligi'
                          ? (
                              // Sadece 'Dikili vasıflı' seçeneğini göster
                              <option value="Dikili vasıflı">Dikili vasıflı</option>
                            )
                          : (
                              araziTipleri.map((araziTipi: AraziTipi) => (
                                <option key={araziTipi.id} value={araziTipi.ad}>
                                  {araziTipi.ad}
                                </option>
                              ))
                            )
                        }
                      </>
                    )}
                  </AnimatedSelect>
                  
                  {/* Animasyonlu placeholder */}
                  <TypewriterPlaceholder 
                    $show={!formData.arazi_vasfi && !selectOpen && !araziTipleriLoading}
                  >
                    {displayedText}
                    {displayedText.length < 'Arazi vasfınızı seçiniz'.length && (
                      <span className="cursor">|</span>
                    )}
                  </TypewriterPlaceholder>
                </AnimatedSelectContainer>
                {validationErrors.arazi_vasfi && (
                  <ErrorMessage>{validationErrors.arazi_vasfi}</ErrorMessage>
                )}
              </FormGroup>

              {/* Su Tahsis Belgesi Kontrolü */}
              {WATER_DEPENDENT_FACILITIES.includes(calculationType) && 
               (locationState.kmlCheckResult?.insideYasPolygons?.length || 0) > 0 && (
                <FormGroup>
                  <div
                    style={{
                      padding: window.innerWidth <= 600 ? '8px' : '16px',
                      backgroundColor: 'rgba(14, 165, 233, 0.1)',
                      borderRadius: window.innerWidth <= 600 ? '4px' : '8px',
                      border: '2px solid rgba(14, 165, 233, 0.3)',
                      marginBottom: window.innerWidth <= 600 ? '8px' : '16px',
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: window.innerWidth <= 600 ? '4px' : '8px',
                        marginBottom: window.innerWidth <= 600 ? '4px' : '12px',
                        color: '#0c4a6e',
                        fontWeight: 600,
                        fontSize: window.innerWidth <= 600 ? '12px' : 'inherit',
                      }}
                    >
                      <span>💧</span>
                      <span>Kapalı Su Havzası Kontrolü</span>
                    </div>
                    <p
                      style={{
                        margin: window.innerWidth <= 600 ? '0 0 6px 0' : '0 0 12px 0',
                        color: '#0c4a6e',
                        fontSize: window.innerWidth <= 600 ? '11px' : '14px',
                      }}
                    >
                      Bu tesis için kapalı su havzası içinde olduğunuz için su tahsis belgesi gereklidir.
                    </p>
                    <label
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: window.innerWidth <= 600 ? '6px' : '8px',
                        cursor: 'pointer',
                        color: '#0c4a6e',
                        fontWeight: 600,
                        fontSize: window.innerWidth <= 600 ? '11px' : 'inherit',
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={suTahsisBelgesi}
                        onChange={(e) => {
                          setSuTahsisBelgesi(e.target.checked);
                          setValidationErrors((prev) => {
                            const next = { ...prev };
                            delete next.suTahsisBelgesi;
                            return next;
                          });
                        }}
                        style={{
                          width: window.innerWidth <= 600 ? '12px' : '16px',
                          height: window.innerWidth <= 600 ? '12px' : '16px',
                          accentColor: 'rgb(14, 165, 233)'
                        }}
                      />
                      <span>Su tahsis belgem mevcut</span>
                      <span className="sc-jVxTAy eMzjLw">*</span>
                    </label>
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: window.innerWidth <= 600 ? '4px' : '6px',
                        fontSize: window.innerWidth <= 600 ? '10px' : '12px',
                        color: 'rgba(12, 74, 110, 0.7)',
                        marginTop: window.innerWidth <= 600 ? '2px' : '6px',
                        marginLeft: window.innerWidth <= 600 ? '12px' : '24px',
                      }}
                    >
                      <span>Bu belge olmadan hesaplama yapılamaz</span>
                      <button
                        type="button"
                        aria-label="Su tahsis belgesi hakkında bilgi al"
                        style={{
                          background: 'none',
                          border: 'none',
                          color: '#3b82f6',
                          fontSize: window.innerWidth <= 600 ? '12px' : '15px',
                          cursor: 'pointer',
                          padding: 0,
                          marginLeft: '2px',
                          lineHeight: 1
                        }}
                        onClick={() => setShowSuTahsisModal(true)}
                      >
                        ❓
                      </button>
                    </div>
                    <SuTahsisModal
                      isOpen={showSuTahsisModal}
                      onClose={() => setShowSuTahsisModal(false)}
                      onResponse={() => setShowSuTahsisModal(false)}
                      calculationType={calculationType}
                    />
                  </div>
                </FormGroup>
              )}

              {/* Su Kısıtı Uyarısı - Büyükbaş hayvancılık için */}
              {isWaterRestrictedForLivestock(calculationType) && (
                <FormGroup>
                  <div
                    style={{
                      padding: window.innerWidth <= 600 ? '12px' : '20px',
                      backgroundColor: 'rgba(239, 68, 68, 0.1)',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                      borderRadius: window.innerWidth <= 600 ? '6px' : '12px',
                      color: '#b91c1c',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: window.innerWidth <= 600 ? '8px' : '12px',
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: window.innerWidth <= 600 ? '6px' : '8px',
                        fontSize: window.innerWidth <= 600 ? '14px' : '16px',
                        fontWeight: 'bold',
                      }}
                    >
                      <span>⛔</span>
                      Su Kısıtı Nedeniyle Yasaklı Bölge
                    </div>
                    <p
                      style={{
                        margin: 0,
                        lineHeight: 1.5,
                        fontSize: window.innerWidth <= 600 ? '12px' : '14px',
                      }}
                    >
                      📍 Haritada işaretlediğiniz nokta su kısıtı olan yerler arasında olup 
                      büyükbaş hayvancılık işletmesi tesisi için yeni yapılacak tesis 
                      müracaatları ret edilmektedir.
                    </p>
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: window.innerWidth <= 600 ? '4px' : '6px',
                        fontSize: window.innerWidth <= 600 ? '10px' : '12px',
                        color: 'rgba(185, 28, 28, 0.8)',
                        fontStyle: 'italic'
                      }}
                    >
                      <span>ℹ️</span>
                      Bu bölgede hesaplama yapılamaz.
                    </div>
                  </div>
                </FormGroup>
              )}

              {/* Alan Kontrol Butonları - Konsolide Edilmiş */}
              {calculationType === 'bag-evi' && (
                formData.arazi_vasfi === 'Tarla + herhangi bir dikili vasıflı' ||
                formData.arazi_vasfi === 'Dikili vasıflı' ||
                formData.arazi_vasfi === 'Tarla + Zeytinlik' ||
                formData.arazi_vasfi === 'Zeytin ağaçlı + herhangi bir dikili vasıf' ||
                formData.arazi_vasfi === '… Adetli Zeytin Ağacı bulunan tarla' ||
                formData.arazi_vasfi === '… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf'
              ) && (
                <AlanKontrolButtons
                  dikiliKontrolSonucu={dikiliKontrolSonucu}
                  onOpenDikiliKontrol={handleDikiliKontrolOpen}
                  formData={formData}
                />
              )}
            </FormGrid>

            {/* Emsal Türü Seçimi artık ResultDisplay bileşeninde */}
          </FormSectionComponent>

          {/* Özel Parametreler */}
          {(calculationType === 'hububat-silo' || calculationType === 'ipek-bocekciligi' || calculationType === 'bag-evi' || calculationType === 'sera' || calculationType === 'tarimsal-depo') && (
            <FormSectionComponent title="⚙️ Özel Parametreler">
              <FormGrid>
                {/* Sera için özel alan */}
                {calculationType === 'sera' && (
                  <FormField
                    label="Planlanan Sera Alanı (m²)"
                    name="sera_alani_m2"
                    type="number"
                    value={formData.sera_alani_m2 || ''}
                    onChange={handleInputChange}
                    placeholder="Örn: 4000"
                    min="1"
                    max="200000"
                    step="1"
                    required
                    error={validationErrors.sera_alani_m2}
                    disabled={!hasCoordinate}
                    onClick={() => setShowLocationModal(true)}
                  />
                )}

                {/* Hububat silo için özel alan */}
                {calculationType === 'hububat-silo' && (
                  <FormField
                    label="Planlanan Silo Taban Alanı (m²)"
                    name="silo_taban_alani_m2"
                    type="number"
                    value={formData.silo_taban_alani_m2 || ''}
                    onChange={handleInputChange}
                    placeholder="Örn: 1000"
                    min="1"
                    max="200000"
                    step="1"
                    required
                    error={validationErrors.silo_taban_alani_m2}
                    disabled={!hasCoordinate}
                    onClick={() => setShowLocationModal(true)}
                  />
                )}

                {/* İpek böcekçiliği için özel alan */}
                {calculationType === 'ipek-bocekciligi' && (
                  <FormGroup>
                    <Label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <input
                        type="checkbox"
                        name="dut_bahcesi_var_mi"
                        checked={formData.dut_bahcesi_var_mi !== undefined ? formData.dut_bahcesi_var_mi : true}
                        onChange={(e) => {
                          setFormData(prev => ({
                            ...prev,
                            dut_bahcesi_var_mi: e.target.checked
                          }));
                        }}
                        disabled={!hasCoordinate}
                        onClick={!hasCoordinate ? () => setShowLocationModal(true) : undefined}
                        style={{
                          opacity: !hasCoordinate ? 0.5 : 1,
                          cursor: !hasCoordinate ? 'not-allowed' : 'pointer'
                        }}
                      />
                      Arazide dut bahçesi var mı? <RequiredIndicator>*</RequiredIndicator>
                    </Label>
                    <div style={{ fontSize: '14px', color: '#666', marginTop: '4px' }}>
                      İpek böcekçiliği tesisleri için arazide dut bahçesi bulunması zorunludur; dut bahçesi kurulumu için İl Tarım ve Orman Müdürlüğü'nden uygun görüş/izin alınması zorunludur.
                    </div>
                    {/* Dut Bahçesi Kontrolü Butonu */}
                    <div className="sc-fvwycc gydjLY" style={{ marginTop: '12px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <label className="sc-cvhvLv exyTmG" style={{ fontWeight: 600, fontSize: '15px', marginRight: '8px' }}>Dut Bahçesi Kontrolü</label>
                      <button
                        type="button"
                        className="sc-haFjst gbvHbo"
                        style={{
                          background: 'linear-gradient(135deg, #059669, #10b981)',
                          color: 'white',
                          border: 'none',
                          borderRadius: '8px',
                          padding: '8px 18px',
                          fontSize: '15px',
                          fontWeight: 600,
                          cursor: !hasCoordinate ? 'not-allowed' : 'pointer',
                          opacity: !hasCoordinate ? 0.5 : 1
                        }}
                        disabled={!hasCoordinate}
                        onClick={() => {
                          if (hasCoordinate) setDutBahcesiKontrolOpen(true);
                        }}
                      >
                        🌳 Dut Bahçesi Kontrolü
                      </button>
                    </div>
                  </FormGroup>
                )}

      {/* Dut Bahçesi Kontrolü Paneli (ipek böcekçiliği için özelleştirilmiş) */}
      {calculationType === 'ipek-bocekciligi' && (
        <AlanKontrol
          isOpen={dutBahcesiKontrolOpen}
          onClose={() => setDutBahcesiKontrolOpen(false)}
          onSuccess={(result) => {
            // Sadece dut ağacı ve alanı ile ilgili verileri aktar
            setFormData(prev => ({
              ...prev,
              dut_bahcesi_alani: result?.dikiliAlan ?? prev.dut_bahcesi_alani,
              dut_agaci_sayisi: result?.agacSayisi ?? prev.dut_agaci_sayisi
            }));
            setDutBahcesiKontrolOpen(false);
          }}
          alanTipi="dikiliAlan"
          araziVasfi={formData.arazi_vasfi || ''}
          initialDikiliAlan={formData.dut_bahcesi_alani || 0}
          initialTarlaAlani={0}
          initialCoordinate={locationState.selectedPoint || undefined}
          initialZoom={15}
          agacTuruSecimiSadeceDut={true}
        />
      )}

                {/* Bağ evi için özel alanlar - Modular component */}
                {calculationType === 'bag-evi' && (
                  <BagEviForm
                    formData={formData}
                    validationErrors={validationErrors}
                    onInputChange={handleInputChange}
                    renderSmartDetectionFeedback={renderSmartDetectionFeedback}
                    isFormDisabled={!hasCoordinate}
                    onDisabledClick={() => setShowLocationModal(true)}
                  />
                )}

                {/* Tarımsal depo için özel alanlar - Bağ evi mantığı ile */}
                {calculationType === 'tarimsal-depo' && (
                  <TarimsalDepoFormFields
                    formData={formData}
                    validationErrors={validationErrors}
                    onInputChange={handleInputChange}
                    renderSmartDetectionFeedback={renderSmartDetectionFeedback}
                    isFormDisabled={!hasCoordinate}
                    onDisabledClick={() => setShowLocationModal(true)}
                  />
                )}


              </FormGrid>
            </FormSectionComponent>
          )}

          {/* Hesaplama Butonu */}
          <SubmitButton
            type="submit"
            $isLoading={isLoading}
            disabled={isLoading || isWaterRestrictedForLivestock(calculationType)}
            style={{
              opacity: isWaterRestrictedForLivestock(calculationType) ? 0.5 : 1,
              cursor: isLoading ? 'not-allowed' : isWaterRestrictedForLivestock(calculationType) ? 'not-allowed' : 'pointer'
            }}
          >
            {isLoading ? (
              <>
                <span>⏳</span>
                Hesaplanıyor...
              </>
            ) : isWaterRestrictedForLivestock(calculationType) ? (
              <>
                <span>⛔</span>
                Su Kısıtı Nedeniyle Yapılamaz
              </>
            ) : (
              <>
                <span>🧮</span>
                Hesapla
              </>
            )}
          </SubmitButton>
        </form>
      </FormContent>

      {/* Alan Kontrolü Paneli */}
      <AlanKontrol
        isOpen={dikiliKontrolOpen}
        onClose={handleDikiliKontrolClose}
        onSuccess={handleDikiliKontrolSuccess}
        alanTipi="dikiliAlan"
        araziVasfi={formData.arazi_vasfi || ''}
        calculationType={calculationType}
        initialDikiliAlan={
          formData.arazi_vasfi === 'Dikili vasıflı' 
            ? (formData.alan_m2 || 0) 
            : (formData.dikili_alani || 0)
        }
        initialTarlaAlani={formData.tarla_alani || 0}
        initialCoordinate={locationState.selectedPoint || undefined}
        initialZoom={15} // Hesaplama sayfasında kullanılan zoom seviyesi
      />

      {/* Lokasyon Seçimi Uyarı Modalı */}
      <LocationSelectionModal
        isOpen={showLocationModal}
        onClose={() => setShowLocationModal(false)}
      />

      {/* İzmir Belediyesi Uyarı Modalı */}
      {showIzmirUyari && izmirUyariData && (
        <IzmirBelediyesiUyari
          arazi_alani_m2={izmirUyariData.arazi_alani_m2}
          yapiTuru={izmirUyariData.yapiTuru}
          koordinatlar={izmirUyariData.koordinatlar}
          onClose={handleIzmirUyariClose}
          onContinue={handleIzmirUyariContinue}
        />
      )}
    </FormContainer>
  );
};

export default CalculationForm;

// Hayvancılık tesisleri ve tarımsal ürün yıkama tesisleri
const WATER_DEPENDENT_FACILITIES = [
  'sut-sigirciligi',
  'besi-sigirciligi', 
  'agil-kucukbas',
  'kumes-yumurtaci',
  'kumes-etci',
  'kumes-hindi',
  'kaz-ordek',
  'kumes-gezen',
  'hara',
  'evcil-hayvan',
  'yikama-tesisi'
];
