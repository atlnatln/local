/**
 * Tarımsal Amaçlı Depo Hesaplamaları - Bağ Evi Mantığı Üzerine Kurulu
 * 
 * Bu dosya bağ evi hesaplama mantığını tarımsal depo için uyarlar.
 * Ana fark: Bağ evinde sabit 75m² taban alan varken, tarımsal depoda 
 * kullanıcının girdiği depo alanı kadar hesaplama yapılır.
 * 
 * Desteklenen arazi tipleri:
 * - Dikili vasıflı
 * - Tarla + herhangi bir dikili vasıflı  
 * - Tarla + Zeytinlik
 * - Zeytin ağaçlı + tarla
 * - Zeytin ağaçlı + herhangi bir dikili vasıf
 * - … Adetli Zeytin Ağacı bulunan tarla
 * - … Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf
 * - Tarla
 * - Sera
 * - Ham toprak, taşlık, kıraç, palamutluk, koruluk gibi diğer vasıflı
 */

// Bağ evi calculator'dan gerekli tipleri import et
import {
  AgacVerisi,
  EklenenAgac,
  AgacDetay,
  YeterlilikSonucu,
  HesaplamaSonucu,
  BagEviValidationError,
  BagEviValidationResult,
  getDefaultTreeData
} from '../modules/BagEvi';

// ===== TYPE DEFINITIONS =====

export interface TarimsalDepoFormData {
  calculationType: string;
  arazi_vasfi: string;
  depo_alani: number; // Legacy — kullanılmıyor ama uyumluluk için
  toplam_arazi_varligi?: number; // İlçe geneli toplam arazi varlığı (m²)
  alan_m2?: number;
  tarla_alani?: number;
  dikili_alani?: number;
  zeytinlik_alani?: number;
  zeytin_agac_sayisi?: number;
  tapu_zeytin_agac_adedi?: number;
  mevcut_zeytin_agac_adedi?: number;
  zeytin_agac_adedi?: number;
  manuel_kontrol_sonucu?: any;
}

export interface TarimsalDepoValidationError extends BagEviValidationError {}

export interface TarimsalDepoValidationResult extends BagEviValidationResult {}

// ===== VALIDATION FUNCTIONS =====

/**
 * Tarımsal depo form verilerini doğrula
 */
export function validateTarimsalDepoForm(formData: TarimsalDepoFormData): TarimsalDepoValidationResult {
  const errors: TarimsalDepoValidationError[] = [];
  const warnings: TarimsalDepoValidationError[] = [];

  // Toplam arazi varlığı kontrolü (depo hakkı hesabı için zorunlu)
  if (!formData.toplam_arazi_varligi || formData.toplam_arazi_varligi <= 0) {
    errors.push({
      field: 'toplam_arazi_varligi',
      message: 'İlçe içi toplam arazi varlığı girilmesi zorunludur.',
      severity: 'error'
    });
  }

  if (formData.toplam_arazi_varligi && formData.toplam_arazi_varligi > 10000000) {
    warnings.push({
      field: 'toplam_arazi_varligi',
      message: 'Toplam arazi varlığı çok büyük görünüyor. Lütfen kontrol ediniz.',
      severity: 'warning'
    });
  }

  // Arazi vasfı kontrolü
  if (!formData.arazi_vasfi) {
    errors.push({
      field: 'arazi_vasfi',
      message: 'Arazi vasfı seçilmesi zorunludur.',
      severity: 'error'
    });
  }

  // Arazi vasıfına göre alan kontrolleri
  const araziVasfi = formData.arazi_vasfi;

  if (araziVasfi === 'Ham toprak, taşlık, kıraç, palamutluk, koruluk gibi diğer vasıflı' ||
      araziVasfi === 'Tarla' ||
      araziVasfi === 'Sera') {
    if (!formData.alan_m2 || formData.alan_m2 <= 0) {
      errors.push({
        field: 'alan_m2',
        message: 'Bu arazi vasfı için alan bilgisi girilmesi zorunludur.',
        severity: 'error'
      });
    }
  }

  if (araziVasfi === 'Tarla + Zeytinlik') {
    if (!formData.tarla_alani || formData.tarla_alani <= 0) {
      errors.push({
        field: 'tarla_alani',
        message: 'Tarla alanı girilmesi zorunludur.',
        severity: 'error'
      });
    }
    if (!formData.zeytinlik_alani || formData.zeytinlik_alani <= 0) {
      errors.push({
        field: 'zeytinlik_alani',
        message: 'Zeytinlik alanı girilmesi zorunludur.',
        severity: 'error'
      });
    }
  }

  if (araziVasfi === 'Tarla + herhangi bir dikili vasıflı') {
    if (!formData.tarla_alani || formData.tarla_alani <= 0) {
      errors.push({
        field: 'tarla_alani',
        message: 'Tarla alanı girilmesi zorunludur.',
        severity: 'error'
      });
    }
    if (!formData.dikili_alani || formData.dikili_alani <= 0) {
      errors.push({
        field: 'dikili_alani',
        message: 'Dikili alanı girilmesi zorunludur.',
        severity: 'error'
      });
    }
  }

  if (araziVasfi === 'Dikili vasıflı' || 
      araziVasfi === 'Zeytin ağaçlı + herhangi bir dikili vasıf' ||
      araziVasfi === '… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf') {
    if (!formData.dikili_alani || formData.dikili_alani <= 0) {
      errors.push({
        field: 'dikili_alani',
        message: 'Dikili alanı girilmesi zorunludur.',
        severity: 'error'
      });
    }
  }

  // Zeytin ağacı kontrolleri
  if (araziVasfi === 'Zeytin ağaçlı + herhangi bir dikili vasıf' ||
      araziVasfi === 'Zeytin ağaçlı + tarla') {
    if (!formData.zeytin_agac_sayisi || formData.zeytin_agac_sayisi < 0) {
      errors.push({
        field: 'zeytin_agac_sayisi',
        message: 'Zeytin ağacı sayısı girilmesi zorunludur.',
        severity: 'error'
      });
    }
  }

  if (araziVasfi === '… Adetli Zeytin Ağacı bulunan tarla' ||
      araziVasfi === '… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf') {
    if (!formData.tapu_zeytin_agac_adedi || formData.tapu_zeytin_agac_adedi <= 0) {
      errors.push({
        field: 'tapu_zeytin_agac_adedi',
        message: 'Tapu zeytin ağacı adedi girilmesi zorunludur.',
        severity: 'error'
      });
    }
    if (!formData.mevcut_zeytin_agac_adedi || formData.mevcut_zeytin_agac_adedi <= 0) {
      errors.push({
        field: 'mevcut_zeytin_agac_adedi',
        message: 'Mevcut zeytin ağacı adedi girilmesi zorunludur.',
        severity: 'error'
      });
    }
  }

  // Minimum alan kontrolleri
  const toplamAlan = formData.alan_m2 || 
                    (formData.tarla_alani || 0) + (formData.dikili_alani || 0) + (formData.zeytinlik_alani || 0);

  if (toplamAlan && toplamAlan < 1000) {
    errors.push({
      field: 'alan_m2',
      message: 'Toplam alan minimum 1000 m² olmalıdır.',
      severity: 'error'
    });
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings,
    canProceed: errors.length === 0
  };
}

/**
 * Tarımsal depo yeterlilik hesaplaması — Talimat Madde 7.1
 * %1 = depo yapma HAKKI (toplam arazi varlığına göre). Emsal DEĞİL.
 */
export function calculateTarimsalDepoYeterlilik(formData: TarimsalDepoFormData): YeterlilikSonucu {
  const araziVasfi = formData.arazi_vasfi;
  let toplamAlan = 0;
  let dikiliAlan = 0;
  let tarlaAlan = 0;

  // Parsel alan hesaplamaları
  switch (araziVasfi) {
    case 'Ham toprak, taşlık, kıraç, palamutluk, koruluk gibi diğer vasıflı':
    case 'Tarla':
    case 'Sera':
      toplamAlan = formData.alan_m2 || 0;
      break;

    case 'Tarla + Zeytinlik':
      tarlaAlan = formData.tarla_alani || 0;
      dikiliAlan = formData.zeytinlik_alani || 0;
      toplamAlan = tarlaAlan + dikiliAlan;
      break;

    case 'Tarla + herhangi bir dikili vasıflı':
      tarlaAlan = formData.tarla_alani || 0;
      dikiliAlan = formData.dikili_alani || 0;
      toplamAlan = tarlaAlan + dikiliAlan;
      break;

    case 'Dikili vasıflı':
    case 'Zeytin ağaçlı + herhangi bir dikili vasıf':
    case '… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf':
      dikiliAlan = formData.dikili_alani || 0;
      toplamAlan = dikiliAlan;
      break;

    case 'Zeytin ağaçlı + tarla':
      tarlaAlan = formData.tarla_alani || 0;
      toplamAlan = tarlaAlan;
      break;

    case '… Adetli Zeytin Ağacı bulunan tarla':
      toplamAlan = formData.alan_m2 || 0;
      break;
  }

  // Depo hakkı hesabı: toplam arazi varlığının %1'i
  const toplamAraziVarligi = formData.toplam_arazi_varligi || 0;
  const depoHakkiM2 = toplamAraziVarligi * 0.01;
  const yeterli = toplamAlan >= 1000 && toplamAraziVarligi > 0;

  return {
    yeterli,
    oran: toplamAraziVarligi > 0 ? 1 : 0, // %1 sabit hak oranı
    minimumOran: 1, // %1
    dikiliAlanYeterli: toplamAlan >= 1000
  };
}

/**
 * Tarımsal depo hesaplama sonucunu mesaj ile birlikte hesapla
 */
export function calculateTarimsalDepoWithMessage(formData: TarimsalDepoFormData): HesaplamaSonucu {
  const validation = validateTarimsalDepoForm(formData);
  
  if (!validation.isValid) {
    return {
      type: 'error',
      message: 'Form verilerinde hatalar bulundu. Lütfen düzeltin.',
      yeterlilik: {
        yeterli: false,
        oran: 0,
        minimumOran: 0
      }
    };
  }

  const yeterlilik = calculateTarimsalDepoYeterlilik(formData);
  const toplamAraziVarligi = formData.toplam_arazi_varligi || 0;
  const depoHakkiM2 = toplamAraziVarligi * 0.01;

  let message = '';
  let type: 'success' | 'error' = 'success';

  if (yeterlilik.yeterli) {
    message = `✅ Toplam arazi varlığınız: ${toplamAraziVarligi.toLocaleString('tr-TR')} m². `;
    message += `Depo yapma hakkınız (%1): ${depoHakkiM2.toLocaleString('tr-TR', { maximumFractionDigits: 1 })} m². `;
    message += `Fiili yapım alanı belediye plan notlarındaki emsal oranına göre belirlenir.`;
  } else {
    message = `❌ Parsel minimum alan şartını karşılamıyor veya toplam arazi varlığı bilgisi eksik.`;
    type = 'error';
  }

  return {
    type,
    message,
    yeterlilik
  };
}

// Export edilen ana fonksiyonlar
export {
  getDefaultTreeData
};

// ===== DİKİLİ ALAN KONTROL FONKSİYONLARI =====

/**
 * Tarımsal depo için dikili alan kontrolü
 * Bağ evi mantığını kullanır ancak sabit 75m² yerine kullanıcı girdisi kullanır
 */
export const performTarimsalDepoDikiliAlanKontrol = (
  dikiliAlan: number,
  tarlaAlani: number,
  agacVerileri: AgacVerisi[],
  araziVasfi: string,
  depoAlani: number = 0
): YeterlilikSonucu => {
  console.log('Tarımsal Depo Dikili Alan Kontrolü:', {
    dikiliAlan,
    tarlaAlani, 
    agacVerileri,
    araziVasfi,
    depoAlani
  });

  // Basit implementasyon - şimdilik her durumda başarılı döndür
  // Gerçek business logic'i daha sonra implement edilecek
  return {
    yeterli: true,
    oran: 100,
    minimumOran: 100,
    kriter1: true,
    kriter2: true
  };
};

// Yardımcı fonksiyonlar - şimdilik basit implement edilmiş
const performTarlaVeDikiliVasifKontrol = (
  dikiliAlan: number,
  tarlaAlani: number,
  agacVerileri: AgacVerisi[],
  depoAlani: number
): YeterlilikSonucu => {
  return {
    yeterli: dikiliAlan >= 5000 || tarlaAlani >= 20000,
    oran: 100,
    minimumOran: 100,
    kriter1: dikiliAlan >= 5000,
    kriter2: tarlaAlani >= 20000
  };
};

const performDikiliVasifKontrol = (
  dikiliAlan: number,
  agacVerileri: AgacVerisi[],
  depoAlani: number
): YeterlilikSonucu => {
  return {
    yeterli: dikiliAlan >= 5000,
    oran: dikiliAlan >= 5000 ? 100 : (dikiliAlan / 5000) * 100,
    minimumOran: 100,
    kriter1: dikiliAlan >= 5000,
    kriter2: false
  };
};

const performTarlaVeZeytinlikKontrol = (
  dikiliAlan: number,
  tarlaAlani: number,
  agacVerileri: AgacVerisi[],
  depoAlani: number
): YeterlilikSonucu => {
  const toplamAlan = dikiliAlan + tarlaAlani;
  return {
    yeterli: toplamAlan >= 20000,
    oran: toplamAlan >= 20000 ? 100 : (toplamAlan / 20000) * 100,
    minimumOran: 100,
    kriter1: true,
    kriter2: true
  };
};

const performZeytinliVeDikiliVasifKontrol = (
  dikiliAlan: number,
  tarlaAlani: number,
  agacVerileri: AgacVerisi[],
  depoAlani: number
): YeterlilikSonucu => {
  return {
    yeterli: dikiliAlan >= 5000,
    oran: dikiliAlan >= 5000 ? 100 : (dikiliAlan / 5000) * 100,
    minimumOran: 100,
    kriter1: dikiliAlan >= 5000,
    kriter2: true
  };
};

const performZeytinliTarlaKontrol = (
  dikiliAlan: number,
  tarlaAlani: number,
  agacVerileri: AgacVerisi[],
  depoAlani: number
): YeterlilikSonucu => {
  return {
    yeterli: tarlaAlani >= 20000,
    oran: tarlaAlani >= 20000 ? 100 : (tarlaAlani / 20000) * 100,
    minimumOran: 100,
    kriter1: false,
    kriter2: tarlaAlani >= 20000
  };
};

const performZeytinliDikiliVasifKontrol = (
  dikiliAlan: number,
  tarlaAlani: number,
  agacVerileri: AgacVerisi[],
  depoAlani: number
): YeterlilikSonucu => {
  return {
    yeterli: dikiliAlan >= 5000,
    oran: dikiliAlan >= 5000 ? 100 : (dikiliAlan / 5000) * 100,
    minimumOran: 100,
    kriter1: dikiliAlan >= 5000,
    kriter2: false
  };
};
