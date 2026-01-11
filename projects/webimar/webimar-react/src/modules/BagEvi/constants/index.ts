/**
 * Bağ Evi Hesaplamaları - Constants
 * 
 * Bu dosya tüm sabit değerleri ve konfigürasyonları içerir
 */

// Re-export tree data functions
export * from './treeData';

// Minimum dikili alan (m²)
export const MINIMUM_DIKILI_ALAN = 1000;

// Büyük tarla alanı minimum (m²)
export const BUYUK_TARLA_ALANI = 5000;

// Maximum dikili alan (m²) - tarla alanının %50'si
export const MAXIMUM_DIKILI_ALAN_RATIO = 0.5;

// Zeytin ağacı yoğunluk limitleri
export const MIN_ZEYTIN_AGAC_YOGUNLUGU = 10; // adet/1000m²
export const MAX_ZEYTIN_AGAC_YOGUNLUGU = 50; // adet/1000m²

// Ağaç türü kategorileri
export const AGAC_KATEGORILERI = {
  MEYVE_AGACLARI: 'Meyve Ağaçları',
  FINDIK: 'Fındık',
  BAG: 'Bağ',
  ZEYTIN: 'Zeytin',
  DIGER: 'Diğer'
};

// Validation mesajları
export const VALIDATION_MESSAGES = {
  // Genel
  BASARILI: 'Hesaplama başarıyla tamamlandı',
  HATA_GENEL: 'Hesaplama sırasında hata oluştu',
  
  // Alan validasyonları
  ALAN_COK_KUCUK: 'Alan çok küçük, minimum 1000 m² olmalıdır',
  MIN_ALAN_DIKILI: 'Dikili alan minimum 1000 m² olmalıdır',
  MIN_ALAN_TARLA: 'Tarla alanı minimum 5000 m² olmalıdır',
  MIN_ALAN_SERA: 'Sera alanı minimum 3000 m² olmalıdır',
  DIKILI_ALAN_COK_BUYUK: 'Dikili alan tarla alanının %50\'sinden büyük olamaz',
  DIKILI_ALAN_SIFIR: 'Dikili alan 0 olamaz',
  NEGATIVE_VALUE: 'Değer negatif olamaz',
  
  // Ağaç validasyonları
  AGAC_SAYISI_SIFIR: 'Ağaç sayısı 0 olamaz',
  AGAC_TURU_BULUNAMADI: 'Ağaç türü bulunamadı',
  AGAC_TIPI_GECERSIZ: 'Ağaç tipi geçersiz',
  
  // Zeytin ağacı validasyonları
  ZEYTIN_AGAC_COK_AZ: 'Zeytin ağacı sayısı çok az',
  ZEYTIN_AGAC_COK_FAZLA: 'Zeytin ağacı sayısı çok fazla',
  ZEYTIN_AGAC_YOGUNLUK_YUKSEK: 'Zeytin ağacı yoğunluğu çok yüksek',
  
  // Bağ validasyonları
  BAG_ALANI_COK_KUCUK: 'Bağ alanı çok küçük',
  BAG_ALANI_COK_BUYUK: 'Bağ alanı çok büyük',
  
  // Manuel kontrol
  MANUEL_KONTROL_GEREKLI: 'Manuel kontrol gerekli',
  MANUEL_KONTROL_TAMAM: 'Manuel kontrol tamamlandı'
};

// API endpoint'leri
export const API_ENDPOINTS = {
  CALCULATE_BAG_EVI: '/api/calculations/bag-evi/',
  VALIDATE_DIKILI: '/api/calculations/validate-dikili/',
  SAVE_CALCULATION: '/api/calculations/save/'
};

// Form alan tipleri
export const FORM_FIELD_TYPES = {
  TEXT: 'text',
  NUMBER: 'number',
  SELECT: 'select',
  CHECKBOX: 'checkbox',
  RADIO: 'radio'
};

// Hesaplama türleri
export const HESAPLAMA_TURLERI = {
  BAG_EVI: 'bag_evi',
  TARIMSAL_DEPO: 'tarimsal_depo',
  SOUK_HAVA_DEPOSU: 'soguk_hava_deposu'
};
