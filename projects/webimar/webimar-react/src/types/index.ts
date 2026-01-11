// Type definitions for Webimar React Frontend

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
  errors?: Record<string, string[]>;
}

// Calculation Input Types
export interface BaseCalculationInput {
  alan_m2: number;
  arazi_vasfi: string;
}

export interface DetailedCalculationInput extends BaseCalculationInput {
  // Gereksiz form alanları kaldırıldı (İl, İlçe, Parsel, Ada, Pafta, Ek Notlar)
  // Bu alanlar hesaplama işleminde kullanılmadığı için interface'den çıkarıldı
  
  // Hububat silo için özel alanlar
  silo_taban_alani_m2?: number;
  
  // Sera için özel alanlar
  sera_alani_m2?: number;
  
  // İpek böcekçiliği için dut bahçesi durumu
  dut_bahcesi_var_mi?: boolean;

  // Emsal türü seçimi (tarımsal yapılar için)
  emsal_turu?: 'marjinal' | 'mutlak_dikili';

  // Bağ evi için özel alanlar
  tarla_alani?: number;
  dikili_alani?: number;
  zeytinlik_alani?: number; // Tarla + Zeytinlik arazi tipi için
  zeytin_agac_sayisi?: number; // Zeytin ağaçlı + tarla arazi tipi için (zeytin ağacı sayısı)
  
  // Tarımsal depo için özel alan
  depo_alani?: number; // Tarımsal depo taban alanı
  
  // "… Adetli Zeytin Ağacı bulunan tarla" arazi tipi için özel alanlar
  tapu_zeytin_agac_adedi?: number; // Tapu senesinde yazılan zeytin ağacı sayısı
  mevcut_zeytin_agac_adedi?: number; // Mevcut zeytin ağacı sayısı
  zeytin_agac_adedi?: number; // Backend için (mevcut_zeytin_agac_adedi'den kopyalanır)
  
  // Manuel ağaç kontrolü sonucu
  manuel_kontrol_sonucu?: any;

  // Koordinat bilgileri
  latitude?: number;
  longitude?: number;

  // Emsal oranı (dinamik emsal için)
  emsal_orani?: number;
  
  // Arıcılık için kovan sayısı
  kovan_sayisi?: number;
  
  // Su kuyusu için kapalı su havzası kontrolü
  kapaliSuHavzasiIcinde?: boolean;
  // Büyükbaş hayvancılık için büyük ova alanı kontrolü
  buyuk_ova_icinde?: boolean;
}

// Calculation Result Types
export interface CalculationData {
  kapasite?: number;
  hayvan_sayisi?: number;
  izin_durumu: 'izin_verilir' | 'izin_verilemez' | 'izin_verilebilir' | 'izin_verilebilir_varsayimsal';
  ana_mesaj: string;
  detaylar?: Record<string, any>;
  hesaplama_detaylari?: {
    kullanilan_katsayi?: number;
    minimum_alan?: number;
    maksimum_alan?: number;
    [key: string]: any;
  };
  // Specific calculation result fields
  alan_m2?: number;
  yapi_alani?: number;
  insaat_alani?: number;
  taban_alani?: number;
  sera_alani?: number;
  depolama_kapasitesi?: number;
  silo_kapasitesi?: number;
  soguk_depo_kapasitesi?: number;
  uretim_kapasitesi?: number;
  kovan_sayisi?: number;
  havuz_alani?: number;
  yumurta_kapasitesi?: number;
  kulucka_kapasitesi?: number;
  maksimum_insaat_alani?: number;
  uretim_alani?: number;
  aciklama?: string;
  [key: string]: any; // Allow for additional dynamic properties
}

export interface CalculationResult {
  success: boolean;
  message: string;
  data: CalculationData;
  timestamp?: string;
}

// Backend constants.py ile uyumlu yapı türleri (27 adet) - YAPI_TURU_ID_MAPPING ile tam uyum
export type StructureType = 
  // Özel Üretim Tesisleri (4 tür) - ID: 1-4
  | 'solucan-tesisi'            // ID: 1 - "Solucan ve solucan gübresi üretim tesisi"
  | 'mantar-tesisi'             // ID: 2 - "Mantar üretim tesisi"
  | 'sera'                      // ID: 3 - "Sera"
  | 'aricilik'                  // ID: 4 - "Arıcılık tesisleri"
  
  // Depolama ve İşleme Tesisleri (12 tür) - ID: 5-16
  | 'hububat-silo'              // ID: 5 - "Hububat ve yem depolama silosu"
  | 'tarimsal-depo'             // ID: 6 - "Tarımsal amaçlı depo"
  | 'lisansli-depo'             // ID: 7 - "Lisanslı depolar"
  | 'yikama-tesisi'             // ID: 8 - "Tarımsal ürün yıkama tesisi"
  | 'kurutma-tesisi'            // ID: 9 - "Hububat, çeltik, ayçiçeği kurutma tesisi"
  | 'meyve-sebze-kurutma'       // ID: 10 - "Açıkta meyve/sebze kurutma alanı"
  | 'zeytinyagi-fabrikasi'      // ID: 11 - "Zeytinyağı fabrikası"
  | 'su-depolama'               // ID: 12 - "Su depolama"
  | 'su-kuyulari'               // ID: 13 - "Su kuyuları"
  | 'bag-evi'                   // ID: 14 - "Bağ evi"
  | 'zeytinyagi-uretim-tesisi'   // ID: 28 - "Zeytinyağı üretim tesisi"
  | 'soguk-hava-deposu'         // ID: 16 - "Soğuk hava deposu"
  
  // Hayvancılık Tesisleri (11 tür) - ID: 17-27
  | 'sut-sigirciligi'           // ID: 17 - "Süt Sığırcılığı Tesisi"
  | 'agil-kucukbas'             // ID: 18 - "Ağıl (küçükbaş hayvan barınağı)"
  | 'kumes-yumurtaci'           // ID: 19 - "Kümes (yumurtacı tavuk)"
  | 'kumes-etci'                // ID: 20 - "Kümes (etçi tavuk)"
  | 'kumes-gezen'               // ID: 21 - "Kümes (gezen tavuk)"
  | 'kumes-hindi'               // ID: 22 - "Kümes (hindi)"
  | 'kaz-ordek'                 // ID: 23 - "Kaz Ördek çiftliği"
  | 'hara'                      // ID: 24 - "Hara (at üretimi/yetiştiriciliği tesisi)"
  | 'ipek-bocekciligi'          // ID: 25 - "İpek böcekçiliği tesisi"
  | 'evcil-hayvan'              // ID: 26 - "Evcil hayvan ve bilimsel araştırma hayvanı üretim tesisi"
  | 'besi-sigirciligi';         // ID: 27 - "Besi Sığırcılığı Tesisi"

// Backend constants.py ile uyumlu ID mapping (1-27) - YAPI_TURU_ID_MAPPING ile tam uyum
export const STRUCTURE_TYPE_MAPPING: Record<number, StructureType> = {
  1: 'solucan-tesisi',
  2: 'mantar-tesisi',
  3: 'sera',
  4: 'aricilik',
  5: 'hububat-silo',
  6: 'tarimsal-depo',
  7: 'lisansli-depo',
  8: 'yikama-tesisi',
  9: 'kurutma-tesisi',
  10: 'meyve-sebze-kurutma',
  11: 'zeytinyagi-fabrikasi',
  12: 'su-depolama',
  13: 'su-kuyulari',
  14: 'bag-evi',
  16: 'soguk-hava-deposu',
  17: 'sut-sigirciligi',
  18: 'agil-kucukbas',
  19: 'kumes-yumurtaci',
  20: 'kumes-etci',
  21: 'kumes-gezen',
  22: 'kumes-hindi',
  23: 'kaz-ordek',
  24: 'hara',
  25: 'ipek-bocekciligi',
  26: 'evcil-hayvan',
  27: 'besi-sigirciligi',
  28: 'zeytinyagi-uretim-tesisi'
};

// Ters mapping - frontend type'dan backend ID'ye
export const STRUCTURE_TYPE_TO_ID: Record<StructureType, number> = Object.entries(STRUCTURE_TYPE_MAPPING)
  .reduce((acc, [id, type]) => ({ ...acc, [type]: parseInt(id) }), {} as Record<StructureType, number>);

// Form State Types
export interface FormState {
  isLoading: boolean;
  error: string | null;
  result: CalculationResult | null;
}

// Component Props
export interface CalculationFormProps {
  structureType: StructureType;
  onSubmit: (data: DetailedCalculationInput) => void;
  isLoading?: boolean;
  error?: string | null;
}

export interface ResultDisplayProps {
  result: CalculationResult | null;
  isLoading: boolean;
  error: string | null;
  araziVasfi?: string; // Arazi vasfı bilgisi manuel kontrol butonu için
}

// Arazi Vasıf Types
export type AraziVasfi = 
  | 'Dikili tarım'
  | 'Mutlak tarım'
  | 'Özel ürün'
  | 'Marjinal tarım'
  | 'Çayır-Mera'
  | 'Orman'
  | 'Örtüaltı tarım'
  | 'Su ürünleri'
  | 'Rekreasyon alanı'
  | 'Sanayi alanı';

// Navigation Types
export interface NavigationItem {
  id: string;
  label: string;
  path: string;
  structureType?: StructureType;
  category: 'livestock' | 'agriculture' | 'storage' | 'residential' | 'other';
}

// Error Types
export interface FormError {
  field: string;
  message: string;
}

export interface ApiError {
  message: string;
  status?: number;
  details?: any;
}

// UI State Types
export interface UIState {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  activeSection: string;
}

// Health Check Type
export interface HealthCheckResult {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  version?: string;
  database?: boolean;
}
