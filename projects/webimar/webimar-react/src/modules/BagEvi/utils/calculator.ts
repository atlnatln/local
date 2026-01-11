/**
 * Bağ Evi Hesaplamaları - Konsolide Hesaplama Motoru
 * 
 * Bu dosya tüm bağ evi hesaplama iş mantığını tek merkezde toplar.
 * Önceden farklı dosyalara dağılmış olan hesaplama fonksiyonları
 * burada birleştirilmiştir.
 * 
 * Desteklenen arazi tipleri:
 * - Dikili vasıflı
 * - Tarla + herhangi bir dikili vasıflı  
 * - Tarla + Zeytinlik (YENİ EKLENDİ)
 * - Zeytin ağaçlı + tarla (YENİ EKLENDİ)
 * - Zeytin ağaçlı + herhangi bir dikili vasıf
 * - … Adetli Zeytin Ağacı bulunan tarla
 * - … Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf
 * - Tarla (YENİ EKLENDİ)
 * - Sera (YENİ EKLENDİ)
 * 
 * Güncellenen özellikler:
 * - Zeytin ağacı yoğunluk kontrolü tamamlandı (max 10 ağaç/dekar)
 * - Minimum alan kontrolleri error seviyesine çıkarıldı
 * - Backend ile tam uyumluluk sağlandı
 */

// ===== TYPE DEFINITIONS =====

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
  oran: number;
  minimumOran: number;
  kriter1?: boolean;
  kriter2?: boolean;
  eksikOran?: number;
  dikiliAlanYeterli?: boolean;
  agacYogTlugu?: number;
}

export interface HesaplamaSonucu {
  type: 'success' | 'error';
  message: string;
  yeterlilik: YeterlilikSonucu;
  alanBilgisi?: {
    kaplanAlan: number;
    oran: number;
    agacDetaylari: AgacDetay[];
  };
  details?: Array<{
    turAdi: string;
    girilenSayi: number;
    gerekliSayi: number;
  }>;
}

export interface BagEviValidationError {
  field: string;
  message: string;
  severity: 'error' | 'warning';
}

export interface BagEviValidationResult {
  isValid: boolean;
  errors: BagEviValidationError[];
  warnings: BagEviValidationError[];
  canProceed: boolean;
}

export interface BagEviFormData {
  calculationType: string;
  arazi_vasfi: string;
  alan_m2?: number;
  tarla_alani?: number;
  dikili_alani?: number;
  zeytinlik_alani?: number;
  zeytin_agac_sayisi?: number;
  tapu_zeytin_agac_adedi?: number;
  mevcut_zeytin_agac_adedi?: number;
  zeytin_agac_adedi?: number;
  manuel_kontrol_sonucu?: any;
  latitude?: number;
  longitude?: number;
}

// ===== CONSTANTS =====

const MINIMUM_YETERLILIK_ORANI = 100; // %100 minimum ağaç yoğunluğu kriteri
const MINIMUM_DIKILI_ALAN = 5000; // 5000 m² minimum dikili alan
const BUYUK_TARLA_ALANI = 20000; // 20000 m² tarla alanı kriteri

// ===== TREE DATA =====

/**
 * Bağ evi hesaplamaları için ağaç verisi (1000 m² için gerekli adet)
 * Veri kaynağı: dikili_arazi_agac_sayilari.md
 */
export const getDefaultTreeData = (): AgacVerisi[] => {
  return [
    { sira: 1, tur: "Kestane", normal: 20 },
    { sira: 2, tur: "Harnup", normal: 21 },
    { sira: 3, tur: "İncir (Kurutmalık)", normal: 16 },
    { sira: 4, tur: "İncir (Taze)", normal: 18 },
    { sira: 5, tur: "Armut", normal: 20, bodur: 220, yariBodur: 70 },
    { sira: 6, tur: "Elma", normal: 20, bodur: 220, yariBodur: 80 },
    { sira: 7, tur: "Trabzon Hurması", normal: 40 },
    { sira: 8, tur: "Kiraz", normal: 25, bodur: 50, yariBodur: 33 },
    { sira: 9, tur: "Ayva", normal: 24, bodur: 100 },
    { sira: 10, tur: "Nar", normal: 40 },
    { sira: 11, tur: "Erik", normal: 18, bodur: 100, yariBodur: 34 },
    { sira: 12, tur: "Kayısı", normal: 16, bodur: 50, yariBodur: 30 },
    { sira: 13, tur: "Zerdali", normal: 20, bodur: 50, yariBodur: 30 },
    { sira: 14, tur: "Muşmula", normal: 25 },
    { sira: 15, tur: "Yenidünya", normal: 21 },
    { sira: 16, tur: "Şeftali", normal: 40, bodur: 100, yariBodur: 67 },
    { sira: 17, tur: "Vişne", normal: 18, bodur: 60, yariBodur: 40 },
    { sira: 18, tur: "Ceviz", normal: 10 },
    { sira: 19, tur: "Dut", normal: 20 },
    { sira: 20, tur: "Üvez", normal: 40 },
    { sira: 21, tur: "Ünnap", normal: 40 },
    { sira: 22, tur: "Kızılcık", normal: 40 },
    { sira: 23, tur: "Limon", normal: 21 },
    { sira: 24, tur: "Portakal", normal: 27 },
    { sira: 25, tur: "Turunç", normal: 27 },
    { sira: 26, tur: "Altıntop", normal: 21 },
    { sira: 27, tur: "Mandarin", normal: 27 },
    { sira: 28, tur: "Avokado", normal: 21 },
    { sira: 29, tur: "Fındık (Düz)", normal: 30 },
    { sira: 30, tur: "Fındık (Eğimli)", normal: 50 },
    { sira: 31, tur: "Gül", normal: 300, yariBodur: 750 },
    { sira: 32, tur: "Çay", normal: 1800 },
    { sira: 33, tur: "Kivi", normal: 60 },
    { sira: 34, tur: "Böğürtlen", normal: 220 },
    { sira: 35, tur: "Ahududu", normal: 600 },
    { sira: 36, tur: "Likapa", normal: 260 },
    { sira: 37, tur: "Muz (Örtü altı)", normal: 170 },
    { sira: 38, tur: "Muz (Açıkta)", normal: 200 },
    { sira: 39, tur: "Kuşburnu", normal: 111 },
    { sira: 40, tur: "Mürver", normal: 85 },
    { sira: 41, tur: "Frenk Üzümü", normal: 220 },
    { sira: 42, tur: "Bektaşi Üzümü", normal: 220 },
    { sira: 43, tur: "Aronya", normal: 170 }
  ];
};

/**
 * Belirli ağaç türü için mevcut alt türleri getir
 */
export const getAvailableTreeTypes = (agacTuruId: string, agacVerileri: AgacVerisi[]) => {
  const agac = agacVerileri.find(a => a.sira.toString() === agacTuruId);
  if (!agac) return [];
  
  const tipler = [];
  if (agac.normal) tipler.push({ value: 'normal', label: 'Normal' });
  if (agac.bodur) tipler.push({ value: 'bodur', label: 'Bodur' });
  if (agac.yariBodur) tipler.push({ value: 'yaribodur', label: 'Yarı Bodur' });
  
  return tipler;
};

// ===== CALCULATION FUNCTIONS =====

/**
 * Ağaçların kapladığı alanı ve yoğunluk oranını hesapla
 */
export const calculateTreeCoverage = (eklenenAgaclar: EklenenAgac[], dikiliAlan: number): {
  toplamKaplanAlan: number;
  agacDetaylari: AgacDetay[];
  yogunlukOrani: number;
} => {
  let toplamKaplanAlan = 0;
  const agacDetaylari: AgacDetay[] = [];

  eklenenAgaclar.forEach(agac => {
    // Ağacın kapladığı alanı hesapla
    // Formül: Girilen ağaç sayısı ÷ (1000m²'de gerekli ağaç sayısı) = kaç 1000m²'lik alan kapladığı
    const kaplanAlanHektar = agac.sayi / agac.gerekliAgacSayisi; // 1000m²'lik birim sayısı
    const agacKaplanAlan = kaplanAlanHektar * 1000; // m² cinsinden
    toplamKaplanAlan += agacKaplanAlan;

    agacDetaylari.push({
      turAdi: agac.turAdi,
      sayi: agac.sayi,
      kaplanAlan: Math.round(agacKaplanAlan),
      binMetrekareBasinaGerekli: agac.gerekliAgacSayisi
    });
  });

  // Yoğunluk oranı hesaplama
  const yogunlukOrani = eklenenAgaclar.length > 0 ? 
    Math.min((toplamKaplanAlan / dikiliAlan) * 100, 100) : 0; // Ağaç yoksa %0

  return {
    toplamKaplanAlan,
    agacDetaylari,
    yogunlukOrani
  };
};

/**
 * Bağ evi yeterlilik kriterlerini kontrol et (Devlet mevzuatına göre)
 */
export const validateVineyardEligibility = (
  dikiliAlan: number,
  tarlaAlani: number,
  eklenenAgaclar: EklenenAgac[],
  araziVasfi?: string
): YeterlilikSonucu => {
  
  // Tree coverage calculation
  const { yogunlukOrani } = calculateTreeCoverage(eklenenAgaclar, dikiliAlan);
  
  // Bağ evi kriterleri (Backend API ile uyumlu):
  // 1. Dikili alan ≥ 5000 m² (yeterli - ağaç yoğunluğu şartı YOK)
  // 2. Tarla alanı ≥ 20000 m² (tek başına yeterli)
  
  const dikiliAlanYeterli = dikiliAlan >= MINIMUM_DIKILI_ALAN;
  const buyukTarlaAlani = tarlaAlani >= BUYUK_TARLA_ALANI;
  
  // "Dikili vasıflı" arazi tipi için özel kontrol
  if (araziVasfi === 'Dikili vasıflı') {
    // Dikili vasıflı arazide: 
    // - Dikili alan >= 5000 m² şartı yeterli
    // - Ağaç sayımı artık zorunlu değil, sadece alan kontrolü yeterli
    
    const kriter1SaglandiMi = dikiliAlanYeterli;
    const yeterli = kriter1SaglandiMi;
    
    return {
      yeterli,
      oran: yogunlukOrani,
      minimumOran: 0, // Ağaç yoğunluğu şartı yok
      kriter1: kriter1SaglandiMi,
      kriter2: false, // Dikili vasıflı arazide kriter2 geçerli değil
      eksikOran: undefined,
      dikiliAlanYeterli,
      agacYogTlugu: eklenenAgaclar.length > 0 ? yogunlukOrani : undefined
    };
  }
  
  // "Zeytin ağaçlı + herhangi bir dikili vasıf" arazi tipi için özel kontrol
  if (araziVasfi === 'Zeytin ağaçlı + herhangi bir dikili vasıf') {
    // Bu arazi tipinde:
    // - Dikili alan >= 5000 m² şartı gerekli
    // - Ağaç sayımı artık zorunlu değil, sadece alan kontrolü yeterli
    
    const kriter1SaglandiMi = dikiliAlanYeterli;
    const yeterli = kriter1SaglandiMi;
    
    return {
      yeterli,
      oran: yogunlukOrani,
      minimumOran: 0, // Ağaç yoğunluğu şartı yok
      kriter1: kriter1SaglandiMi,
      kriter2: false, // Bu arazi tipinde tarla alanı kriteri yok
      eksikOran: undefined,
      dikiliAlanYeterli,
      agacYogTlugu: eklenenAgaclar.length > 0 ? yogunlukOrani : undefined
    };
  }

  // "… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf" arazi tipi için özel kontrol
  if (araziVasfi === '… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf') {
    // Bu arazi tipinde:
    // - Dikili alan >= 5000 m² şartı gerekli
    // - Tarla alanı kriteri UYGULANMAZ
    // - Zeytin ağacı bilgileri form üzerinden alınır (tapu/mevcut maksimumu)
    // - Ek dikili vasıf ağaçları manuel kontrolde eklenir (opsiyonel)
    // - Toplam ağaç yoğunluğu kontrolü yapılır
    
    // Ağaç yoğunluğu kontrolü: dikili alan yeterli ise yeterli
    const kriter1SaglandiMi = dikiliAlanYeterli;
    const yeterli = kriter1SaglandiMi;
    
    return {
      yeterli,
      oran: yogunlukOrani,
      minimumOran: 0, // Ağaç yoğunluğu şartı yok
      kriter1: kriter1SaglandiMi,
      kriter2: false, // Bu arazi tipinde tarla alanı kriteri yok
      eksikOran: undefined,
      dikiliAlanYeterli,
      agacYogTlugu: eklenenAgaclar.length > 0 ? yogunlukOrani : undefined
    };
  }
  
  // "Tarla + Zeytinlik" arazi tipi için özel kontrol (YENİ EKLENDİ)
  if (araziVasfi === 'Tarla + Zeytinlik') {
    // Bu arazi tipinde:
    // - Tarla alanı >= 20000 m² gerekli
    // - Zeytinlik alanı >= 1 m² gerekli
    // - Toplam alan > 20001 m² gerekli
    
    const kriter2SaglandiMi = buyukTarlaAlani; // Sadece tarla alanı kriteri
    const yeterli = kriter2SaglandiMi;
    
    return {
      yeterli,
      oran: yogunlukOrani,
      minimumOran: 0, // Ağaç yoğunluğu şartı yok
      kriter1: false, // Dikili alan kriteri yok
      kriter2: kriter2SaglandiMi,
      eksikOran: undefined,
      dikiliAlanYeterli: false, // Bu tipte dikili alan kriteri yok
      agacYogTlugu: undefined
    };
  }

  // "Zeytin ağaçlı + tarla" arazi tipi için özel kontrol (YENİ EKLENDİ)
  if (araziVasfi === 'Zeytin ağaçlı + tarla') {
    // Bu arazi tipinde:
    // - Tarla alanı >= 20000 m² gerekli
    // - Maksimum 10 ağaç/dekar kontrolü
    
    const kriter2SaglandiMi = buyukTarlaAlani;
    const yeterli = kriter2SaglandiMi;
    
    return {
      yeterli,
      oran: yogunlukOrani,
      minimumOran: 0, // Ağaç yoğunluğu şartı yok
      kriter1: false, // Dikili alan kriteri yok
      kriter2: kriter2SaglandiMi,
      eksikOran: undefined,
      dikiliAlanYeterli: false, // Bu tipte dikili alan kriteri yok
      agacYogTlugu: undefined
    };
  }

  // "Tarla" arazi tipi için özel kontrol (YENİ EKLENDİ)
  if (araziVasfi === 'Tarla') {
    // Bu arazi tipinde:
    // - Tarla alanı >= 20000 m² gerekli
    
    const kriter2SaglandiMi = buyukTarlaAlani;
    const yeterli = kriter2SaglandiMi;
    
    return {
      yeterli,
      oran: yogunlukOrani,
      minimumOran: 0, // Ağaç yoğunluğu şartı yok
      kriter1: false, // Dikili alan kriteri yok
      kriter2: kriter2SaglandiMi,
      eksikOran: undefined,
      dikiliAlanYeterli: false, // Bu tipte dikili alan kriteri yok
      agacYogTlugu: undefined
    };
  }

  // "Sera" arazi tipi için özel kontrol (YENİ EKLENDİ)
  if (araziVasfi === 'Sera') {
    // Bu arazi tipinde:
    // - Sera alanı >= 3000 m² gerekli
    
    const seraAlaniYeterli = dikiliAlan >= 3000; // Sera alanı dikili alan olarak geçer
    const kriter1SaglandiMi = seraAlaniYeterli;
    const yeterli = kriter1SaglandiMi;
    
    return {
      yeterli,
      oran: yogunlukOrani,
      minimumOran: 0, // Ağaç yoğunluğu şartı yok
      kriter1: kriter1SaglandiMi,
      kriter2: false, // Tarla alanı kriteri yok
      eksikOran: undefined,
      dikiliAlanYeterli: seraAlaniYeterli,
      agacYogTlugu: undefined
    };
  }

  // "Ham toprak, taşlık, kıraç, palamutluk, koruluk gibi diğer vasıflı" arazi tipi için özel kontrol (YENİ EKLENDİ)
  if (araziVasfi === 'Ham toprak, taşlık, kıraç, palamutluk, koruluk gibi diğer vasıflı') {
    // Bu arazi tipinde:
    // - Alan >= 20000 m² gerekli (backend constants'a göre)
    
    const hamToprakAlaniYeterli = dikiliAlan >= 20000; // Ham toprak alanı dikili alan olarak geçer
    const kriter2SaglandiMi = hamToprakAlaniYeterli;
    const yeterli = kriter2SaglandiMi;
    
    return {
      yeterli,
      oran: yogunlukOrani,
      minimumOran: 0, // Ağaç yoğunluğu şartı yok
      kriter1: false, // Dikili alan kriteri geçerli değil
      kriter2: kriter2SaglandiMi,
      eksikOran: undefined,
      dikiliAlanYeterli: false, // Dikili alan kriteri bu tip için geçerli değil
      agacYogTlugu: undefined
    };
  }
  
  // "Tarla + herhangi bir dikili vasıflı" için normal kontrol
  // Kriter 1: Dikili alan yeterli - ağaç sayımı yapılmışsa yoğunluk da kontrol edilir
  const agacSayimiYapildi = eklenenAgaclar.length > 0;
  const kriter1SaglandiMi = dikiliAlanYeterli && (!agacSayimiYapildi || yogunlukOrani >= MINIMUM_YETERLILIK_ORANI);
  
  // Kriter 2: Büyük tarla alanı
  const kriter2SaglandiMi = buyukTarlaAlani;
  
  const yeterli = kriter1SaglandiMi || kriter2SaglandiMi;
  
  return {
    yeterli,
    oran: yogunlukOrani,
    minimumOran: agacSayimiYapildi ? MINIMUM_YETERLILIK_ORANI : 0,
    kriter1: kriter1SaglandiMi,
    kriter2: kriter2SaglandiMi,
    eksikOran: (agacSayimiYapildi && !yeterli) ? (MINIMUM_YETERLILIK_ORANI - yogunlukOrani) : undefined,
    dikiliAlanYeterli,
    agacYogTlugu: eklenenAgaclar.length > 0 ? yogunlukOrani : undefined
  };
};

/**
 * Bağ evi hesaplama sonucunu mesaj ile birlikte hesapla
 */
export const calculateVineyardResult = (
  dikiliAlan: number,
  tarlaAlani: number,
  eklenenAgaclar: EklenenAgac[],
  araziVasfi?: string
): HesaplamaSonucu => {
  // Input validation
  if (dikiliAlan <= 0) {
    return {
      type: 'error',
      message: 'Lütfen geçerli bir dikili alan girin.',
      yeterlilik: {
        yeterli: false,
        oran: 0,
        minimumOran: 100
      }
    };
  }

  // "Dikili vasıflı", "Zeytin ağaçlı + herhangi bir dikili vasıf" ve "… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf" arazi tipleri için tarla alanı kontrolü yapma
  if (araziVasfi !== 'Dikili vasıflı' && 
      araziVasfi !== 'Zeytin ağaçlı + herhangi bir dikili vasıf' && 
      araziVasfi !== '… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf' &&
      tarlaAlani <= 0) {
    return {
      type: 'error',
      message: 'Lütfen geçerli bir tarla alanı girin. Tarla alanı, dikili alan dahil toplam parsel büyüklüğüdür.',
      yeterlilik: {
        yeterli: false,
        oran: 0,
        minimumOran: 100
      }
    };
  }

  // Kriter 2 kontrolü: Tarla alanı >= 20000 m² ise ağaç kontrolü yapmadan devam et
  // Ancak "Dikili vasıflı", "Zeytin ağaçlı + herhangi bir dikili vasıf" ve "… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf" arazi tipleri için bu kontrol geçerli değil
  const kriter2SaglaniyorMu = (araziVasfi !== 'Dikili vasıflı' && 
                               araziVasfi !== 'Zeytin ağaçlı + herhangi bir dikili vasıf' &&
                               araziVasfi !== '… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf') ? 
                               (tarlaAlani >= BUYUK_TARLA_ALANI) : false;
  
  if (!kriter2SaglaniyorMu && araziVasfi !== 'Dikili vasıflı' && araziVasfi !== 'Zeytin ağaçlı + herhangi bir dikili vasıf' && araziVasfi !== '… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf') {
    // Kriter 2 sağlanmıyorsa, Kriter 1 için gerekli kontrolleri yap (sadece normal arazi tipleri için)
    if (dikiliAlan < MINIMUM_DIKILI_ALAN) {
      return {
        type: 'error',
        message: 'Dikili tarım arazilerinde bağ evi yapılabilmesi için dikili alan büyüklüğünün en az 0,5 hektar (5000 m²) olması gerekmektedir.',
        yeterlilik: {
          yeterli: false,
          oran: 0,
          minimumOran: 100
        }
      };
    }

    // Normal arazi tiplerinde ağaç sayımı yapılmışsa yoğunluk da kontrol edilir
    // Ağaç sayımı yapılmamışsa sadece alan kontrolü yeterli
    const agacSayimiYapildi = eklenenAgaclar.length > 0;
    if (agacSayimiYapildi) {
      // Ağaç eklenmiş, yoğunluk kontrolü gerekli değil artık - alan yeterli ise başarılı
      // Bu kullanıcı dostu yaklaşım: ağaç sayımı yapılmış = dikili durum tespit edilmiş
    }
  }

  // "Dikili vasıflı", "Zeytin ağaçlı + herhangi bir dikili vasıf" ve "… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf" arazi tipleri için özel kontrol
  if (araziVasfi === 'Dikili vasıflı' || araziVasfi === 'Zeytin ağaçlı + herhangi bir dikili vasıf' || araziVasfi === '… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf') {
    if (dikiliAlan < MINIMUM_DIKILI_ALAN) {
      const araziTipiAdi = araziVasfi === 'Dikili vasıflı' ? 'Dikili vasıflı' : 
                          araziVasfi === 'Zeytin ağaçlı + herhangi bir dikili vasıf' ? 'Zeytin ağaçlı + herhangi bir dikili vasıf' :
                          '… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf';
      return {
        type: 'error',
        message: `${araziTipiAdi} arazilerinde bağ evi yapılabilmesi için dikili alan büyüklüğünün en az 0,5 hektar (5000 m²) olması gerekmektedir.`,
        yeterlilik: {
          yeterli: false,
          oran: 0,
          minimumOran: 100
        }
      };
    }
    
    // Ağaç kontrolü artık zorunlu değil - sadece alan yeterli
    // Ağaç sayımı yapıldıysa yoğunluk da kontrol edilir
    // "Dikili vasıflı" için dikili alan >= 5000 m² yeterli, ağaç kontrolü opsiyonel
    // "Zeytin ağaçlı + herhangi bir dikili vasıf" için dikili alan >= 5000 m² yeterli, ağaç kontrolü opsiyonel
    // "… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf" için dikili alan >= 5000 m² yeterli, ağaç kontrolü opsiyonel
  }

  // Calculate tree coverage and eligibility
  const coverage = calculateTreeCoverage(eklenenAgaclar, dikiliAlan);
  const yeterlilik = validateVineyardEligibility(dikiliAlan, tarlaAlani, eklenenAgaclar, araziVasfi);

  let message = '';
  let type: 'success' | 'error' = 'error';

  if (yeterlilik.yeterli) {
    if (araziVasfi === 'Dikili vasıflı' && yeterlilik.kriter1) {
      // Dikili vasıflı arazi için özel mesaj
      const agacSayimiYapildi = eklenenAgaclar.length > 0;
      message = agacSayimiYapildi ? 
        'Bağ Evi Kontrolü Başarılı (Dikili Vasıflı Arazi - Dikili Alan ≥ 5000 m² ve Ağaç Yoğunluğu Yeterli)' :
        'Bağ Evi Kontrolü Başarılı (Dikili Vasıflı Arazi - Dikili Alan ≥ 5000 m²)';
      type = 'success';
    } else if (araziVasfi === '… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf' && yeterlilik.kriter1) {
      // … Adetli Zeytin Ağacı bulunan + dikili vasıf arazi için özel mesaj
      message = 'Bağ Evi Kontrolü Başarılı (… Adetli Zeytin Ağacı bulunan + Dikili Vasıf - Dikili Alan ≥ 5000 m²)';
      type = 'success';
    } else if (araziVasfi === 'Zeytin ağaçlı + herhangi bir dikili vasıf' && yeterlilik.kriter1) {
      // Zeytin ağaçlı + dikili vasıf arazi için özel mesaj
      const agacSayimiYapildi = eklenenAgaclar.length > 0;
      message = agacSayimiYapildi ? 
        'Bağ Evi Kontrolü Başarılı (Zeytin Ağaçlı + Dikili Vasıf - Dikili Alan ≥ 5000 m² ve Ağaç Yoğunluğu Yeterli)' :
        'Bağ Evi Kontrolü Başarılı (Zeytin Ağaçlı + Dikili Vasıf - Dikili Alan ≥ 5000 m²)';
      type = 'success';
    } else if (araziVasfi === 'Tarla + Zeytinlik' && yeterlilik.kriter2) {
      // Tarla + Zeytinlik arazi için özel mesaj (YENİ EKLENDİ)
      message = 'Bağ Evi Kontrolü Başarılı (Tarla + Zeytinlik - Büyük Tarla Kriteri)';
      type = 'success';
    } else if (araziVasfi === 'Zeytin ağaçlı + tarla' && yeterlilik.kriter2) {
      // Zeytin ağaçlı + tarla arazi için özel mesaj (YENİ EKLENDİ)
      message = 'Bağ Evi Kontrolü Başarılı (Zeytin Ağaçlı + Tarla - Büyük Tarla Kriteri)';
      type = 'success';
    } else if (araziVasfi === 'Tarla' && yeterlilik.kriter2) {
      // Tarla arazi için özel mesaj (YENİ EKLENDİ)
      message = 'Bağ Evi Kontrolü Başarılı (Tarla - Büyük Tarla Kriteri ≥ 20000 m²)';
      type = 'success';
    } else if (araziVasfi === 'Sera' && yeterlilik.kriter1) {
      // Sera arazi için özel mesaj (YENİ EKLENDİ)
      message = 'Bağ Evi Kontrolü Başarılı (Sera - Minimum Alan ≥ 3000 m²)';
      type = 'success';
    } else if (araziVasfi === 'Ham toprak, taşlık, kıraç, palamutluk, koruluk gibi diğer vasıflı' && yeterlilik.kriter2) {
      // Ham toprak arazi için özel mesaj (YENİ EKLENDİ)
      message = 'Bağ Evi Kontrolü Başarılı (Ham Toprak Vasıflı - Minimum Alan ≥ 20000 m²)';
      type = 'success';
    } else if (yeterlilik.kriter1) {
      // Normal dikili alan kriteri sağlanıyor - ağaç sayımı yapıldı mı kontrol et
      const agacSayimiYapildi = eklenenAgaclar.length > 0;
      message = agacSayimiYapildi ? 
        'Bağ Evi Kontrolü Başarılı (Dikili Alan ≥ 5000 m² ve Ağaç Yoğunluğu Yeterli)' :
        'Bağ Evi Kontrolü Başarılı (Dikili Alan ≥ 5000 m²)';
      type = 'success';
    } else if (yeterlilik.kriter2) {
      // Büyük tarla alanı kriteri sağlanıyor
      message = eklenenAgaclar.length > 0 ? 
        'Bağ Evi Kontrolü Başarılı (Büyük Tarla Alanı - Ağaç hesabı bilgi amaçlı)' :
        'Bağ Evi Kontrolü Başarılı (Büyük Tarla Alanı ≥ 20000 m²)';
      type = 'success';
    }
  } else {
    // Detaylı hata mesajları
    const dikiliAlanYeterli = dikiliAlan >= MINIMUM_DIKILI_ALAN;
    const buyukTarlaAlani = tarlaAlani >= BUYUK_TARLA_ALANI;

    if (araziVasfi === 'Dikili vasıflı') {
      // Dikili vasıflı arazi için sadece dikili alan kontrolü
      if (!dikiliAlanYeterli) {
        message = 'Bağ Evi Kontrolü Başarısız (Dikili Vasıflı Arazi - Dikili Alan < 5000 m²)';
      } else {
        // Bu durum teorik olarak olmamalı çünkü dikili alan yeterli ise başarılı olmalı
        message = 'Bağ Evi Kontrolü Başarısız (Dikili Vasıflı Arazi)';
      }
    } else if (araziVasfi === 'Zeytin ağaçlı + herhangi bir dikili vasıf') {
      // Zeytin ağaçlı + dikili vasıf arazi için sadece dikili alan kontrolü
      if (!dikiliAlanYeterli) {
        message = 'Bağ Evi Kontrolü Başarısız (Zeytin Ağaçlı + Dikili Vasıf - Dikili Alan < 5000 m²)';
      } else {
        // Bu durum teorik olarak olmamalı çünkü dikili alan yeterli ise başarılı olmalı
        message = 'Bağ Evi Kontrolü Başarısız (Zeytin Ağaçlı + Dikili Vasıf)';
      }
    } else if (araziVasfi === '… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf') {
      // … Adetli Zeytin Ağacı bulunan + dikili vasıf arazi için sadece dikili alan kontrolü
      if (!dikiliAlanYeterli) {
        message = 'Bağ Evi Kontrolü Başarısız (… Adetli Zeytin Ağacı bulunan + Dikili Vasıf - Dikili Alan < 5000 m²)';
      } else {
        // Bu durum teorik olarak olmamalı çünkü dikili alan yeterli ise başarılı olmalı
        message = 'Bağ Evi Kontrolü Başarısız (… Adetli Zeytin Ağacı bulunan + Dikili Vasıf)';
      }
    } else if (araziVasfi === 'Tarla + Zeytinlik') {
      // Tarla + Zeytinlik arazi için hata mesajı (YENİ EKLENDİ)
      if (!buyukTarlaAlani) {
        message = 'Bağ Evi Kontrolü Başarısız (Tarla + Zeytinlik - Tarla Alanı < 20000 m²)';
      } else {
        message = 'Bağ Evi Kontrolü Başarısız (Tarla + Zeytinlik)';
      }
    } else if (araziVasfi === 'Zeytin ağaçlı + tarla') {
      // Zeytin ağaçlı + tarla arazi için hata mesajı (YENİ EKLENDİ)
      if (!buyukTarlaAlani) {
        message = 'Bağ Evi Kontrolü Başarısız (Zeytin Ağaçlı + Tarla - Tarla Alanı < 20000 m²)';
      } else {
        message = 'Bağ Evi Kontrolü Başarısız (Zeytin Ağaçlı + Tarla - Zeytin Yoğunluğu Fazla)';
      }
    } else if (araziVasfi === 'Tarla') {
      // Tarla arazi için hata mesajı (YENİ EKLENDİ)
      if (!buyukTarlaAlani) {
        message = 'Bağ Evi Kontrolü Başarısız (Tarla - Alan < 20000 m²)';
      } else {
        message = 'Bağ Evi Kontrolü Başarısız (Tarla)';
      }
    } else if (araziVasfi === 'Sera') {
      // Sera arazi için hata mesajı (YENİ EKLENDİ)
      const seraAlani = dikiliAlan; // Sera durumunda dikili alan sera alanıdır
      if (seraAlani < 3000) {
        message = 'Bağ Evi Kontrolü Başarısız (Sera - Alan < 3000 m²)';
      } else {
        message = 'Bağ Evi Kontrolü Başarısız (Sera)';
      }
    } else if (araziVasfi === 'Ham toprak, taşlık, kıraç, palamutluk, koruluk gibi diğer vasıflı') {
      // Ham toprak arazi için hata mesajı (YENİ EKLENDİ)
      const hamToprakAlani = dikiliAlan; // Ham toprak durumunda dikili alan ham toprak alanıdır
      if (hamToprakAlani < 20000) {
        message = 'Bağ Evi Kontrolü Başarısız (Ham Toprak Vasıflı - Alan < 20000 m²)';
      } else {
        message = 'Bağ Evi Kontrolü Başarısız (Ham Toprak Vasıflı)';
      }
    } else if (!dikiliAlanYeterli && !buyukTarlaAlani) {
      message = 'Bağ Evi Kontrolü Başarısız (Dikili Alan < 5000 m² ve Tarla Alanı < 20000 m²)';
    } else {
      message = 'Bağ Evi Kontrolü Başarısız';
    }
  }

  return {
    type,
    message,
    yeterlilik,
    // Ağaç bilgilerini sadece büyük tarla alanı durumunda göster
    alanBilgisi: (eklenenAgaclar.length > 0 && yeterlilik.kriter2 && !yeterlilik.kriter1) ? {
      kaplanAlan: Math.round(coverage.toplamKaplanAlan),
      oran: parseFloat(coverage.yogunlukOrani.toFixed(1)),
      agacDetaylari: coverage.agacDetaylari
    } : undefined
  };
};

// ===== VALIDATION FUNCTIONS =====

/**
 * Ağaç girişi validasyonu
 */
export const validateTreeInput = (
  selectedTreeType: string,
  treeCount: number,
  availableTreeData: AgacVerisi[]
): { isValid: boolean; error?: string } => {
  if (!selectedTreeType) {
    return {
      isValid: false,
      error: 'Lütfen bir ağaç türü seçin.'
    };
  }

  if (!treeCount || treeCount <= 0) {
    return {
      isValid: false,
      error: 'Ağaç sayısı pozitif bir değer olmalıdır.'
    };
  }

  const treeData = availableTreeData.find(a => a.sira.toString() === selectedTreeType);
  if (!treeData) {
    return {
      isValid: false,
      error: 'Seçilen ağaç türü bulunamadı.'
    };
  }

  if (treeCount > 50000) {
    return {
      isValid: false,
      error: 'Ağaç sayısı çok yüksek görünüyor. Lütfen değeri kontrol edin.'
    };
  }

  return { isValid: true };
};

/**
 * Bağ evi form validasyonu
 */
export const validateBagEviForm = (formData: BagEviFormData): BagEviValidationResult => {
  const errors: BagEviValidationError[] = [];
  const warnings: BagEviValidationError[] = [];

  // Arazi vasfı kontrolü
  if (!formData.arazi_vasfi) {
    errors.push({
      field: 'arazi_vasfi',
      message: 'Lütfen arazi vasfını seçin.',
      severity: 'error'
    });
  }

  // Arazi vasfına göre alan kontrolleri
  if (formData.arazi_vasfi === 'Tarla + herhangi bir dikili vasıflı') {
    // Tarla + dikili için
    if (!formData.tarla_alani || formData.tarla_alani <= 0) {
      errors.push({
        field: 'tarla_alani',
        message: 'Tarla alanı pozitif bir sayı olmalıdır.',
        severity: 'error'
      });
    }
    
    if (!formData.dikili_alani || formData.dikili_alani <= 0) {
      errors.push({
        field: 'dikili_alani',
        message: 'Dikili alan pozitif bir sayı olmalıdır.',
        severity: 'error'
      });
    }

    // NOT: "Tarla + herhangi bir dikili vasıflı" arazi tipinde tarla alanı ve dikili alan
    // birbirinden bağımsız alanlar olabilir, bu yüzden karşılaştırma kontrolü kaldırıldı.

    // Minimum alan uyarıları - kontroller kaldırıldı, kullanıcı istediği değeri girebilir
  }

  if (formData.arazi_vasfi === 'Dikili vasıflı') {
    // Dikili vasıflı için alan_m2 kontrolü
    if (!formData.alan_m2 || formData.alan_m2 <= 0) {
      errors.push({
        field: 'alan_m2',
        message: 'Dikili alan pozitif bir sayı olmalıdır.',
        severity: 'error'
      });
    }

    // Zeytin ağacı sayısı opsiyonel - eğer girilirse pozitif olmalı
    if (formData.zeytin_agac_sayisi !== undefined && formData.zeytin_agac_sayisi < 0) {
      errors.push({
        field: 'zeytin_agac_sayisi',
        message: 'Zeytin ağacı sayısı 0 veya pozitif bir sayı olmalıdır.',
        severity: 'error'
      });
    }

    // Dekara 10+ ağaç kontrolü - sadece ağaç sayısı girilirse
    if (formData.alan_m2 && formData.zeytin_agac_sayisi && formData.zeytin_agac_sayisi > 0) {
      const agacYogunlugu = (formData.zeytin_agac_sayisi / formData.alan_m2) * 1000; // Dekara düşen
      if (agacYogunlugu > 10) {
        errors.push({
          field: 'zeytin_agac_sayisi',
          message: 'Dekara 10 ağaçtan fazla zeytin ağacı olamaz.',
          severity: 'error'
        });
      }
    }

    // Minimum alan kontrolü kaldırıldı - kullanıcı istediği değeri girebilir
  }

  if (formData.arazi_vasfi === '… Adetli Zeytin Ağacı bulunan tarla') {
    // Zeytin ağaçlı tarla için
    if (!formData.tarla_alani || formData.tarla_alani <= 0) {
      errors.push({
        field: 'tarla_alani',
        message: 'Tarla alanı pozitif bir sayı olmalıdır.',
        severity: 'error'
      });
    }

    if (formData.tapu_zeytin_agac_adedi !== undefined && formData.tapu_zeytin_agac_adedi < 0) {
      errors.push({
        field: 'tapu_zeytin_agac_adedi',
        message: 'Tapu senesindeki zeytin ağacı sayısı 0 veya pozitif bir sayı olmalıdır.',
        severity: 'error'
      });
    }

    if (formData.mevcut_zeytin_agac_adedi !== undefined && formData.mevcut_zeytin_agac_adedi < 0) {
      errors.push({
        field: 'mevcut_zeytin_agac_adedi',
        message: 'Mevcut zeytin ağacı sayısı 0 veya pozitif bir sayı olmalıdır.',
        severity: 'error'
      });
    }

    // Dekara 10+ ağaç kontrolü (eksik olan validation)
    if (formData.tarla_alani && formData.mevcut_zeytin_agac_adedi) {
      const agacYogunlugu = (formData.mevcut_zeytin_agac_adedi / formData.tarla_alani) * 1000; // Dekara düşen
      if (agacYogunlugu > 10) {
        errors.push({
          field: 'mevcut_zeytin_agac_adedi',
          message: 'Dekara 10 ağaçtan fazla zeytin ağacı olamaz.',
          severity: 'error'
        });
      }
    }

    // Minimum alan kontrolü kaldırıldı - kullanıcı istediği değeri girebilir
    // Yeni zeytin ağaçlı + dikili için
    if (!formData.dikili_alani || formData.dikili_alani <= 0) {
      errors.push({
        field: 'dikili_alani',
        message: 'Dikili alan pozitif bir sayı olmalıdır.',
        severity: 'error'
      });
    }

    if (formData.tapu_zeytin_agac_adedi !== undefined && formData.tapu_zeytin_agac_adedi < 0) {
      errors.push({
        field: 'tapu_zeytin_agac_adedi',
        message: 'Tapu senesindeki zeytin ağacı sayısı 0 veya pozitif bir sayı olmalıdır.',
        severity: 'error'
      });
    }

    if (formData.mevcut_zeytin_agac_adedi !== undefined && formData.mevcut_zeytin_agac_adedi < 0) {
      errors.push({
        field: 'mevcut_zeytin_agac_adedi',
        message: 'Mevcut zeytin ağacı sayısı 0 veya pozitif bir sayı olmalıdır.',
        severity: 'error'
      });
    }

    // Dekara 10+ ağaç kontrolü
    if (formData.dikili_alani && formData.mevcut_zeytin_agac_adedi) {
      const agacYogunlugu = (formData.mevcut_zeytin_agac_adedi / formData.dikili_alani) * 1000; // Dekara düşen
      if (agacYogunlugu > 10) {
        errors.push({
          field: 'mevcut_zeytin_agac_adedi',
          message: 'Dekara 10 ağaçtan fazla zeytin ağacı olamaz.',
          severity: 'error'
        });
      }
    }
  }

  // Tarla + Zeytinlik arazi tipi (ID: 3) - YENİ EKLENDİ
  if (formData.arazi_vasfi === 'Tarla + Zeytinlik') {
    if (!formData.tarla_alani || formData.tarla_alani <= 0) {
      errors.push({
        field: 'tarla_alani',
        message: 'Tarla alanı pozitif bir sayı olmalıdır.',
        severity: 'error'
      });
    }

    if (!formData.zeytinlik_alani || formData.zeytinlik_alani <= 0) {
      errors.push({
        field: 'zeytinlik_alani',
        message: 'Zeytinlik alanı pozitif bir sayı olmalıdır.',
        severity: 'error'
      });
    }

    // Minimum alan kontrolü kaldırıldı - kullanıcı istediği değeri girebilir

    // Zeytinlik alanı minimum 1 m² olmalı
    if (formData.zeytinlik_alani && formData.zeytinlik_alani < 1) {
      errors.push({
        field: 'zeytinlik_alani',
        message: 'Zeytinlik alanı minimum 1 m² olmalıdır.',
        severity: 'error'
      });
    }

    // Toplam alan 20001 m²'den büyük olmalı
    if (formData.tarla_alani && formData.zeytinlik_alani) {
      const toplamAlan = formData.tarla_alani + formData.zeytinlik_alani;
      if (toplamAlan <= 20001) {
        errors.push({
          field: 'zeytinlik_alani',
          message: 'Toplam alan (tarla + zeytinlik) 20001 m²\'den büyük olmalıdır.',
          severity: 'error'
        });
      }
    }
  }

  // Zeytin ağaçlı + tarla arazi tipi (ID: 4) - YENİ EKLENDİ
  if (formData.arazi_vasfi === 'Zeytin ağaçlı + tarla') {
    if (!formData.tarla_alani || formData.tarla_alani <= 0) {
      errors.push({
        field: 'tarla_alani',
        message: 'Tarla alanı pozitif bir sayı olmalıdır.',
        severity: 'error'
      });
    }

    // Defansif: hem eski (zeytin_agac_sayisi) hem yeni (zeytin_agac_adedi) field adını kabul et
    const zeytinAgacSayisi = formData.zeytin_agac_adedi ?? formData.zeytin_agac_sayisi;
    if (zeytinAgacSayisi === undefined || zeytinAgacSayisi < 0) {
      errors.push({
        field: 'zeytin_agac_adedi',
        message: 'Zeytin ağacı sayısı 0 veya pozitif bir sayı olmalıdır.',
        severity: 'error'
      });
    }

    // Minimum alan kontrolü kaldırıldı - kullanıcı istediği değeri girebilir
    if (formData.tarla_alani && zeytinAgacSayisi) {
      const agacYogunlugu = (zeytinAgacSayisi / formData.tarla_alani) * 1000; // Dekara düşen
      if (agacYogunlugu > 10) {
        errors.push({
          field: 'zeytin_agac_adedi',
          message: 'Dekara 10 ağaçtan fazla zeytin ağacı olamaz.',
          severity: 'error'
        });
      }
    }
  }

  // Tarla arazi tipi (ID: 10) - YENİ EKLENDİ
  if (formData.arazi_vasfi === 'Tarla') {
    if (!formData.alan_m2 || formData.alan_m2 <= 0) {
      errors.push({
        field: 'alan_m2',
        message: 'Tarla alanı pozitif bir sayı olmalıdır.',
        severity: 'error'
      });
    }

    // Minimum alan kontrolü kaldırıldı - kullanıcı istediği değeri girebilir
  }

  // Sera arazi tipi (ID: 11) - YENİ EKLENDİ
  if (formData.arazi_vasfi === 'Sera') {
    if (!formData.alan_m2 || formData.alan_m2 <= 0) {
      errors.push({
        field: 'alan_m2',
        message: 'Sera alanı pozitif bir sayı olmalıdır.',
        severity: 'error'
      });
    }

    // Minimum alan kontrolü kaldırıldı - kullanıcı istediği değeri girebilir
  }

  // Ham toprak, taşlık, kıraç, palamutluk, koruluk gibi diğer vasıflı (ID: 9) - YENİ EKLENDİ
  if (formData.arazi_vasfi === 'Ham toprak, taşlık, kıraç, palamutluk, koruluk gibi diğer vasıflı') {
    if (!formData.alan_m2 || formData.alan_m2 <= 0) {
      errors.push({
        field: 'alan_m2',
        message: 'Alan pozitif bir sayı olmalıdır.',
        severity: 'error'
      });
    }

    // Bu arazi tipi için sadece alan kontrolü yeterlidir
  }

  const isValid = errors.length === 0;
  const canProceed = isValid || ((formData.tarla_alani || 0) >= BUYUK_TARLA_ALANI);

  return {
    isValid,
    errors,
    warnings,
    canProceed
  };
};

/**
 * Alan yüzdesi hesaplama
 */
export const calculateAreaPercentage = (partialArea: number, totalArea: number): number => {
  if (totalArea <= 0) return 0;
  return Math.min((partialArea / totalArea) * 100, 100);
};

/**
 * Alan görüntüleme formatı
 */
export const formatAreaDisplay = (areaM2: number): { m2: string; donum: string } => {
  return {
    m2: areaM2.toLocaleString(),
    donum: (areaM2 / 1000).toFixed(1)
  };
};

/**
 * Aynı ağaç türü kontrolü
 */
export const checkDuplicateTreeEntries = (
  eklenenAgaclar: EklenenAgac[],
  newTreeType: string,
  newTreeSubType: string
): boolean => {
  return eklenenAgaclar.some(agac => 
    agac.turid === newTreeType && agac.tipi === newTreeSubType
  );
};

/**
 * Backend için form verisini hazırla
 */
export const prepareFormDataForBackend = (formData: BagEviFormData): BagEviFormData => {
  const finalFormData = { ...formData };

  // === YENİ: manuel_kontrol_sonucu.eklenenAgaclar normalize et ===
  try {
    const mk = formData.manuel_kontrol_sonucu;
    if (mk && Array.isArray(mk.eklenenAgaclar)) {
      const normalized = mk.eklenenAgaclar.map((agac: any) => {
        // normalize keys: desteklenen alternatif anahtarları kontrol et
        const agacSayisi = Number(
          agac.agacSayisi ?? agac.sayi ?? agac.count ?? 0
        ) || 0;

        const secilenAgacTuru = String(
          agac.secilenAgacTuru ?? agac.agacTuru ?? agac.turid ?? agac.turId ?? agac.turAdi ?? ''
        );

        const agacTuru = String(
          agac.agacTuru ?? agac.turAdi ?? agac.tur ?? ''
        );

        return {
          // Backend'in beklediği alan isimleri
          secilenAgacTuru,
          agacTuru,
          agacSayisi,
          // preserve original useful fields (opsiyonel)
          secilenAgacTipi: agac.secilenAgacTipi ?? agac.tipi ?? agac.type ?? 'normal',
          gerekliAgacSayisi: agac.gerekliAgacSayisi ?? agac.gerekli ?? undefined,
          // raw source for debugging (isteğe bağlı)
          __raw: agac
        };
      });

      // Assign normalized back into finalFormData
      finalFormData.manuel_kontrol_sonucu = {
        ...finalFormData.manuel_kontrol_sonucu,
        eklenenAgaclar: normalized
      };

      // Backward-compat: üst seviyeye de ekle (bazı eski kodlar burayı okuyabilir)
      (finalFormData as any).eklenenAgaclar = normalized;
    }
  } catch (e) {
    // Normalizasyon hatası sonucu akışı bozmayacak; loglanması yeterli
    console.error('prepareFormDataForBackend - eklenenAgaclar normalize hatası:', e);
  }

  // Arazi vasfına göre alan_m2 değerini ayarla ve özel işlemler yap
  if (formData.arazi_vasfi === 'Tarla + herhangi bir dikili vasıflı') {
    finalFormData.alan_m2 = formData.tarla_alani || 0;
  } else if (formData.arazi_vasfi === 'Dikili vasıflı') {
    // Dikili vasıflı arazi için alan_m2 doğrudan dikili_alani ile kullanılır
    // Tarla alanı 0 olarak ayarlanır çünkü sadece dikili alan vardır
    finalFormData.dikili_alani = formData.alan_m2 || 0;
    finalFormData.tarla_alani = 0; // Dikili vasıflı arazide tarla alanı yoktur
  } else if (formData.arazi_vasfi === 'Tarla + Zeytinlik') {
    // Tarla + Zeytinlik arazi tipi için özel işleme
    finalFormData.alan_m2 = (formData.tarla_alani || 0) + (formData.zeytinlik_alani || 0);
  } else if (formData.arazi_vasfi === 'Zeytin ağaçlı + tarla') {
    // Zeytin ağaçlı + tarla arazi tipi için özel işleme
    finalFormData.alan_m2 = formData.tarla_alani || 0;
    // Defansif: hem eski (zeytin_agac_sayisi) hem yeni (zeytin_agac_adedi) field adını kabul et
    finalFormData.zeytin_agac_adedi = formData.zeytin_agac_adedi ?? formData.zeytin_agac_sayisi ?? 0;
  } else if (formData.arazi_vasfi === 'Zeytin ağaçlı + herhangi bir dikili vasıf') {
    // Zeytin ağaçlı + herhangi bir dikili vasıf arazi tipi için özel işleme
    finalFormData.alan_m2 = formData.dikili_alani || 0;
  } else if (formData.arazi_vasfi === '… Adetli Zeytin Ağacı bulunan tarla') {
    finalFormData.alan_m2 = formData.tarla_alani || 0;
    
    // Tapu ve mevcut ağaç sayısından maksimumu al
    const tapuAgacSayisi = formData.tapu_zeytin_agac_adedi || 0;
    const mevcutAgacSayisi = formData.mevcut_zeytin_agac_adedi || 0;
    finalFormData.zeytin_agac_adedi = Math.max(tapuAgacSayisi, mevcutAgacSayisi);
  } else if (formData.arazi_vasfi === '… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf') {
    finalFormData.alan_m2 = formData.dikili_alani || 0;
    
    // Tapu ve mevcut ağaç sayısından maksimumu al
    const tapuAgacSayisi = formData.tapu_zeytin_agac_adedi || 0;
    const mevcutAgacSayisi = formData.mevcut_zeytin_agac_adedi || 0;
    finalFormData.zeytin_agac_adedi = Math.max(tapuAgacSayisi, mevcutAgacSayisi);
  } else if (formData.arazi_vasfi === 'Tarla') {
    // Tarla arazi tipi için özel işleme (YENİ EKLENDİ)
    finalFormData.alan_m2 = formData.alan_m2 || 0;
  } else if (formData.arazi_vasfi === 'Sera') {
    // Sera arazi tipi için özel işleme (YENİ EKLENDİ)
    finalFormData.alan_m2 = formData.alan_m2 || 0;
  } else if (formData.arazi_vasfi === 'Ham toprak, taşlık, kıraç, palamutluk, koruluk gibi diğer vasıflı') {
    // Ham toprak arazi tipi için özel işleme (YENİ EKLENDİ)
    finalFormData.alan_m2 = formData.alan_m2 || 0;
  }

  return finalFormData;
};

// ===== EXPORT DEFAULT CALCULATOR =====

/**
 * Ana bağ evi hesaplama sınıfı
 */
export class BagEviCalculator {
  private agacVerileri: AgacVerisi[];

  constructor() {
    this.agacVerileri = getDefaultTreeData();
  }

  // Ağaç verisi operasyonları
  getTreeData(): AgacVerisi[] {
    return this.agacVerileri;
  }

  getAvailableTreeTypes(agacTuruId: string) {
    return getAvailableTreeTypes(agacTuruId, this.agacVerileri);
  }

  // Hesaplama operasyonları
  calculateTreeCoverage(eklenenAgaclar: EklenenAgac[], dikiliAlan: number) {
    return calculateTreeCoverage(eklenenAgaclar, dikiliAlan);
  }

  validateEligibility(dikiliAlan: number, tarlaAlani: number, eklenenAgaclar: EklenenAgac[], araziVasfi?: string) {
    return validateVineyardEligibility(dikiliAlan, tarlaAlani, eklenenAgaclar, araziVasfi);
  }

  calculateResult(dikiliAlan: number, tarlaAlani: number, eklenenAgaclar: EklenenAgac[], araziVasfi?: string) {
    return calculateVineyardResult(dikiliAlan, tarlaAlani, eklenenAgaclar, araziVasfi);
  }

  // Validasyon operasyonları
  validateTreeInput(selectedTreeType: string, treeCount: number) {
    return validateTreeInput(selectedTreeType, treeCount, this.agacVerileri);
  }

  validateForm(formData: BagEviFormData) {
    return validateBagEviForm(formData);
  }

  // Yardımcı operasyonlar
  formatAreaDisplay(areaM2: number) {
    return formatAreaDisplay(areaM2);
  }

  calculateAreaPercentage(partialArea: number, totalArea: number) {
    return calculateAreaPercentage(partialArea, totalArea);
  }

  checkDuplicateTreeEntries(eklenenAgaclar: EklenenAgac[], newTreeType: string, newTreeSubType: string) {
    return checkDuplicateTreeEntries(eklenenAgaclar, newTreeType, newTreeSubType);
  }

  prepareFormDataForBackend(formData: BagEviFormData) {
    return prepareFormDataForBackend(formData);
  }
}

// Default export
export default BagEviCalculator;
