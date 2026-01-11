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
  depo_alani: number; // Ana fark: depo alanı gerekli
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

  // Depo alanı kontrolü (en önemli alan)
  if (!formData.depo_alani || formData.depo_alani <= 0) {
    errors.push({
      field: 'depo_alani',
      message: 'Depo alanı girilmesi zorunludur ve 0\'dan büyük olmalıdır.',
      severity: 'error'
    });
  }

  if (formData.depo_alani && formData.depo_alani > 50000) {
    warnings.push({
      field: 'depo_alani',
      message: 'Depo alanı çok büyük görünüyor. Lütfen kontrol ediniz.',
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

  // Depo alan oranı kontrolü
  if (formData.depo_alani && toplamAlan) {
    const depoOrani = (formData.depo_alani / toplamAlan) * 100;
    if (depoOrani > 10) {
      warnings.push({
        field: 'depo_alani',
        message: `Depo alanı toplam arazinin %${depoOrani.toFixed(1)}'ini oluşturuyor. Bu oran yüksek olabilir.`,
        severity: 'warning'
      });
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings,
    canProceed: errors.length === 0
  };
}

/**
 * Tarımsal depo yeterlilik hesaplaması - Bağ evi mantığına benzer ama depo alanı ile
 */
export function calculateTarimsalDepoYeterlilik(formData: TarimsalDepoFormData): YeterlilikSonucu {
  const araziVasfi = formData.arazi_vasfi;
  let toplamAlan = 0;
  let dikiliAlan = 0;
  let tarlaAlan = 0;

  // Alan hesaplamaları
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

  // Emsal hesaplamaları (bağ evi mantığı)
  let emsalOrani = 0;
  const depoAlani = formData.depo_alani || 0;

  if (araziVasfi === 'Ham toprak, taşlık, kıraç, palamutluk, koruluk gibi diğer vasıflı') {
    emsalOrani = 0.01; // %1
  } else if (araziVasfi === 'Tarla' || araziVasfi === 'Sera') {
    emsalOrani = 0.02; // %2
  } else if (araziVasfi.includes('Dikili') || araziVasfi.includes('Zeytin')) {
    emsalOrani = 0.05; // %5
  } else {
    // Karma araziler için ağırlıklı ortalama
    const tarlaEmsal = (tarlaAlan / toplamAlan) * 0.02;
    const dikiliEmsal = (dikiliAlan / toplamAlan) * 0.05;
    emsalOrani = tarlaEmsal + dikiliEmsal;
  }

  const izinVerilenMaksAlan = toplamAlan * emsalOrani;
  const yeterli = depoAlani <= izinVerilenMaksAlan;
  const oran = toplamAlan > 0 ? (depoAlani / toplamAlan) * 100 : 0;

  return {
    yeterli,
    oran,
    minimumOran: emsalOrani * 100,
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
  const depoAlani = formData.depo_alani || 0;

  let message = '';
  let type: 'success' | 'error' = 'success';

  if (yeterlilik.yeterli) {
    const kalanAlan = ((yeterlilik.minimumOran / 100) * (formData.alan_m2 || 0)) - depoAlani;
    message = `✅ Tarımsal depo yapımına izin verilir. ${depoAlani} m² depo alanı mevzuata uygundur. `;
    if (kalanAlan > 0) {
      message += `${kalanAlan.toFixed(0)} m² daha yapı alanı hakkınız bulunmaktadır.`;
    }
  } else {
    const fazlaAlan = depoAlani - ((yeterlilik.minimumOran / 100) * (formData.alan_m2 || 0));
    message = `❌ Tarımsal depo yapımına izin verilemez. ${depoAlani} m² depo alanı mevzuata uygun değil. `;
    message += `${fazlaAlan.toFixed(0)} m² fazla alan bulunmaktadır.`;
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
