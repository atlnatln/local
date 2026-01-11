/**
 * Su kısıtı olan bölgelerde büyükbaş hayvancılık işletmesi yapımı yasağı kontrolü.
 */

// Su kısıtı olan il ve ilçelerin listesi
const WATER_RESTRICTED_AREAS = [
  { province: "AKSARAY", district: "AKSARAY" },        // Merkez = il adı
  { province: "AKSARAY", district: "ESKİL" },
  { province: "AKSARAY", district: "GÜLAĞAÇ" },
  { province: "AKSARAY", district: "GÜZELYURT" },
  { province: "AKSARAY", district: "SULTANHANI" },
  { province: "ANKARA", district: "BALA" },
  { province: "ANKARA", district: "GÖLBAŞI" },
  { province: "ANKARA", district: "HAYMANA" },
  { province: "ANKARA", district: "ŞEREFLİKOÇHİSAR" },
  { province: "ESKİŞEHİR", district: "ALPU" },
  { province: "ESKİŞEHİR", district: "BEYLİKOVA" },
  { province: "ESKİŞEHİR", district: "ÇİFTELER" },
  { province: "ESKİŞEHİR", district: "MAHMUDİYE" },
  { province: "ESKİŞEHİR", district: "MİHALIÇÇIK" },
  { province: "ESKİŞEHİR", district: "SİVRİHİSAR" },
  { province: "HATAY", district: "KUMLU" },
  { province: "HATAY", district: "REYHANLI" },
  { province: "KARAMAN", district: "AYRANCI" },
  { province: "KARAMAN", district: "KARAMAN" },        // Merkez = il adı
  { province: "KARAMAN", district: "KAZIMKARABEKİR" },
  { province: "KIRŞEHİR", district: "BOZTEPE" },
  { province: "KIRŞEHİR", district: "MUCUR" },
  { province: "KONYA", district: "AKÖREN" },
  { province: "KONYA", district: "AKŞEHİR" },
  { province: "KONYA", district: "ALTINEKİN" },
  { province: "KONYA", district: "CİHANBEYLİ" },
  { province: "KONYA", district: "ÇUMRA" },
  { province: "KONYA", district: "DERBENT" },
  { province: "KONYA", district: "DOĞANHİSAR" },
  { province: "KONYA", district: "EMİRGAZİ" },
  { province: "KONYA", district: "EREĞLİ" },
  { province: "KONYA", district: "GÜNEYSINIR" },
  { province: "KONYA", district: "HALKAPINAR" },
  { province: "KONYA", district: "KADINHANI" },
  { province: "KONYA", district: "KARAPINAR" },
  { province: "KONYA", district: "KARATAY" },
  { province: "KONYA", district: "KULU" },
  { province: "KONYA", district: "MERAM" },
  { province: "KONYA", district: "SARAYÖNÜ" },
  { province: "KONYA", district: "SELÇUKLU" },
  { province: "KONYA", district: "TUZLUKÇU" },
  { province: "MARDİN", district: "ARTUKLU" },
  { province: "MARDİN", district: "DERİK" },
  { province: "MARDİN", district: "KIZILTEPE" },
  { province: "NEVŞEHİR", district: "ACIGÖL" },
  { province: "NEVŞEHİR", district: "DERİNKUYU" },
  { province: "NEVŞEHİR", district: "GÜLŞEHİR" },
  { province: "NİĞDE", district: "ALTUNHİSAR" },
  { province: "NİĞDE", district: "BOR" },
  { province: "NİĞDE", district: "ÇİFTLİK" },
  { province: "NİĞDE", district: "NİĞDE" },           // Merkez = il adı
  { province: "ŞANLIURFA", district: "VİRANŞEHİR" },
];

/**
 * Verilen il ve ilçenin su kısıtı olan bölgede olup olmadığını kontrol eder.
 */
export const isWaterRestrictedArea = (province: string | null, district: string | null): boolean => {
  if (!province || !district) {
    return false;
  }
  
  // Büyük harfe çevir
  const provinceUpper = province.toUpperCase().trim();
  const districtUpper = district.toUpperCase().trim();
  
  // Listede ara
  return WATER_RESTRICTED_AREAS.some(
    area => area.province === provinceUpper && area.district === districtUpper
  );
};

/**
 * Su kısıtı uyarı mesajını döndürür.
 */
export const getWaterRestrictionMessage = (): string => {
  return "📍 Haritada işaretlediğiniz nokta su kısıtı olan yerler arasında olup " +
         "büyükbaş hayvancılık işletmesi tesisi için yeni yapılacak tesis " +
         "müracaatları ret edilmektedir.";
};

/**
 * Hesaplama türünün büyükbaş hayvancılık olup olmadığını kontrol eder.
 */
export const isLivestockCalculationType = (calculationType?: string): boolean => {
  if (!calculationType) return false;
  
  const livestockTypes = [
    'sut-sigirciligi',
    'besi-sigirciligi',
    'buyukbas',
    'sut_sigirciligi',
    'besi_sigirciligi'
  ];
  
  return livestockTypes.includes(calculationType.toLowerCase().replace('_', '-'));
};