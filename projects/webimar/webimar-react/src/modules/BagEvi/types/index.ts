/**
 * Bağ Evi Hesaplamaları - Type Definitions
 * 
 * Bu dosya tüm bağ evi hesaplama type'larını içerir
 */

export interface AgacVerisi {
  sira: number;
  tur: string;
  normal?: number;
  bodur?: number;
  yariBodur?: number;
}

export interface EklenenAgac {
  turid: string;
  turAdi: string;
  tipi: 'normal' | 'bodur' | 'yaribodur';
  sayi: number;
  gerekliAgacSayisi: number;
}

export interface AgacDetay {
  turAdi: string;
  sayi: number;
  kaplanAlan: number;
  binMetrekareBasinaGerekli: number;
}

export interface YeterlilikSonucu {
  yeterli: boolean;
  mesaj: string;
  gerekseme?: number;
}

export interface DikiliDetay {
  toplamDikiliAlan: number;
  toplamBinAdet: number;
  agacDetaylari: AgacDetay[];
  yeterlilikSonucu: YeterlilikSonucu;
}

export interface ZeytinAgacKontrolSonucu {
  uygunlukDurumu: string;
  fazlaAgacAdedi?: number;
  maksimumIzinVerilenAdet?: number;
  mevcutAdet?: number;
  yogunlukDurumu?: string;
  agacSilmeOnerisi?: boolean;
}

export interface ManuelKontrolSonucu {
  sonuc: 'yeterli' | 'yetersiz' | 'dikili_yeterli' | 'tarla_yeterli';
  dikiliDetay?: DikiliDetay;
  zeytinDetay?: ZeytinDetaylari;
  metinMesaj?: string;
}

export interface ZeytinDetaylari {
  tapu_zeytin_agac_adedi: number;
  mevcut_zeytin_agac_adedi: number;
  kontrol_sonucu: ZeytinAgacKontrolSonucu;
}

export interface BagEviValidationError {
  field: string;
  message: string;
  type: 'error' | 'warning';
}

export interface BagEviValidationResult {
  isValid: boolean;
  errors: BagEviValidationError[];
  warnings: BagEviValidationError[];
}

export interface BagEviFormData {
  // Arazi Bilgileri
  arazi_vasfi: string;
  alan_m2: number;
  bag_alani_m2?: number;
  dikili_alani?: number;
  tarla_alani?: number;
  zeytinlik_alani?: number;
  meyvelik_alani?: number;
  sera_alani?: number;
  
  // Zeytin Ağacı Bilgileri  
  zeytin_agac_adedi?: number;
  tapu_zeytin_agac_adedi?: number;
  mevcut_zeytin_agac_adedi?: number;
  
  // Lokasyon
  buyuk_ova_icinde?: boolean;
  latitude?: number;
  longitude?: number;
  
  // Manuel Kontrol
  manuel_kontrol_sonucu?: ManuelKontrolSonucu;
  
  // Ağaç bilgileri (eski sistem)
  eklenenAgaclar?: EklenenAgac[];
  
  // Meta
  bag_evi_var_mi?: boolean;
  hesaplama_turu?: string;
}
