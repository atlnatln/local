/**
 * İzmir Büyükşehir Belediyesi Plan Notları Kontrol Sistemi
 * 
 * Madde 7.12.15.2: Tarımsal amaçlı yapılar için minimum 5000 m² parsel büyüklüğü kriteri
 */

// İzmir koordinat sınırları (yaklaşık)
const IZMIR_BOUNDS = {
  north: 39.0,
  south: 38.0, 
  east: 28.5,
  west: 26.0
};

// İstisna olan hesaplama türleri (5000m² kuralı uygulanmaz)
const ISTISNA_HESAPLAMA_TURLERI = [
  'bag-evi',           // Çiftçinin barınması - farklı kural (7.12.15.1)
  'sera',              // Örtü altı tarım - ayrı düzenleme (7.12.15.3)  
  'su-kuyulari'        // Su altyapısı - genel istisna
];

export interface IzmirUyariSonuc {
  uyariGosterilsinMi: boolean;
  uyariMesaji: string;
  planNotuDetayi: string;
  eksikAlan?: number;
  iletisimBilgileri?: {
    telefon: string;
    email: string;
    adres: string;
  };
}

export interface Koordinat {
  lat: number;
  lng: number;
}

/**
 * İzmir Büyükşehir Belediyesi 5000m² kuralı kontrolü
 */
export function checkIzmirBelediyesi5000M2(
  alan_m2: number,
  hesaplamaTuru: string,
  koordinatlar?: Koordinat
): IzmirUyariSonuc {
  
  // 1. İstisna kontrolü - bazı hesaplama türleri için uyarı gösterilmez
  if (ISTISNA_HESAPLAMA_TURLERI.includes(hesaplamaTuru)) {
    return {
      uyariGosterilsinMi: false,
      uyariMesaji: '',
      planNotuDetayi: ''
    };
  }

  // 2. İzmir sınırları kontrolü - koordinat yoksa veya İzmir dışındaysa uyarı gösterilmez
  let izmirIcindeMi = false;
  if (koordinatlar) {
    izmirIcindeMi = isInsideIzmir(koordinatlar);
  }

  // 3. Alan kontrolü - 5000m² altı ise uyarı göster
  if (alan_m2 < 5000 && izmirIcindeMi) {
    const eksikAlan = 5000 - alan_m2;
    
    return {
      uyariGosterilsinMi: true,
      eksikAlan,
      uyariMesaji: createUyariMesaji(alan_m2, eksikAlan, hesaplamaTuru),
      planNotuDetayi: createPlanNotuDetayi(),
      iletisimBilgileri: {
        telefon: '0232 293 46 46',
        email: 'imar@izmir.bel.tr', 
        adres: 'İzmir Büyükşehir Belediyesi İmar ve Şehircilik Dairesi Başkanlığı'
      }
    };
  }

  // 4. Kural ihlali yok
  return {
    uyariGosterilsinMi: false,
    uyariMesaji: '',
    planNotuDetayi: ''
  };
}

/**
 * Koordinatın İzmir sınırları içinde olup olmadığını kontrol et
 */
function isInsideIzmir(koordinat: Koordinat): boolean {
  return (
    koordinat.lat >= IZMIR_BOUNDS.south &&
    koordinat.lat <= IZMIR_BOUNDS.north &&
    koordinat.lng >= IZMIR_BOUNDS.west &&
    koordinat.lng <= IZMIR_BOUNDS.east
  );
}

/**
 * Kullanıcı dostu uyarı mesajı oluştur
 */
function createUyariMesaji(alan_m2: number, eksikAlan: number, hesaplamaTuru: string): string {
  const hesaplamaAdlari: Record<string, string> = {
    'hububat-silo': 'Hububat Silo',
    'tarimsal-depo': 'Tarımsal Depo', 
    'lisansli-depo': 'Lisanslı Depo',
    'yikama-tesisi': 'Yıkama Tesisi',
    'kurutma-tesisi': 'Kurutma Tesisi',
    'meyve-sebze-kurutma': 'Meyve/Sebze Kurutma',
    'zeytinyagi-fabrikasi': 'Zeytinyağı Fabrikası',
    'soguk-hava-deposu': 'Soğuk Hava Deposu',
    'solucan-tesisi': 'Solucan Tesisi',
    'mantar-tesisi': 'Mantar Tesisi',
    'aricilik': 'Arıcılık Tesisi',
    'sut-sigirciligi': 'Süt Sığırcılığı',
    'agil-kucukbas': 'Ağıl (Küçükbaş)',
    'kumes-yumurtaci': 'Kümes (Yumurtacı)',
    'kumes-etci': 'Kümes (Etçi)',
    'kumes-gezen': 'Kümes (Gezen)',
    'kumes-hindi': 'Kümes (Hindi)',
    'kaz-ordek': 'Kaz-Ördek Çiftliği',
    'hara': 'Hara (At Yetiştiriciliği)',
    'ipek-bocekciligi': 'İpek Böcekçiliği',
    'evcil-hayvan': 'Evcil Hayvan Tesisi',
    'besi-sigirciligi': 'Besi Sığırcılığı',
    'su-depolama': 'Su Depolama Tesisi'
  };

  const hesaplamaAdi = hesaplamaAdlari[hesaplamaTuru] || 'Tarımsal Tesis';

  return `İzmir Büyükşehir Belediyesi plan notları gereğince ${hesaplamaAdi} için minimum 5000 m² parsel büyüklüğü gerekiyor. Mevcut parsel: ${alan_m2.toLocaleString('tr-TR')} m² (${eksikAlan.toLocaleString('tr-TR')} m² eksik). Belediye İmar Müdürlüğü ile görüşmeniz önerilir.`;
}

/**
 * Plan notu detay metni
 */
function createPlanNotuDetayi(): string {
  return `
**Madde 7.12.15.2: Tarımsal Amaçlı Yapılar**

**🌾 Mutlak Tarım Arazisi, Dikili Tarım Arazisi ve Özel Ürün Arazileri:**
- Minimum parsel cephesi 10 metre ve minimum parsel büyüklüğü 5000 m²
- Yollara 10 metre'den, komşu parsel sınırlarına 5 metre'den fazla yaklaşmamak
- İnşaat emsali 0.05'i, yüksekliği 2 katı aşmamak
- Maksimum yapı inşaat alanı (brüt inşaat alanı) 2000 m²'den fazla olamaz

**🌿 Marjinal Tarım Arazileri:**
- Minimum parsel cephesi 10 metre ve minimum parsel büyüklüğü 5000 m²
- Yollara 10 metre'den, komşu parsel sınırlarına 5 metre'den fazla yaklaşmamak
- Parsellerin 5000 m².lik kısmı için inşaat emsali 0,20'yi aşmamak
- Geri kalan parsel alanı için inşaat emsali 0.10'u aşmamak
- Yüksekliği 2 katı aşmamak
- Maksimum yapı inşaat alanı (brüt inşaat alanı) 10000 m²'den fazla olamaz

**📋 Detaylı bilgi için:** İzmir Büyükşehir Belediyesi Plan Notları
  `.trim();
}

/**
 * Hesaplama türünün İzmir belediyesi kurallarına tabi olup olmadığını kontrol et
 */
export function isSubjectToIzmirRules(hesaplamaTuru: string): boolean {
  return !ISTISNA_HESAPLAMA_TURLERI.includes(hesaplamaTuru);
}

/**
 * İzmir Belediyesi iletişim bilgilerini getir
 */
export function getIzmirBelediyesiIletisim() {
  return {
    telefon: '0232 293 46 46',
    email: 'imar@izmir.bel.tr',
    website: 'https://izmir.bel.tr',
    adres: 'İzmir Büyükşehir Belediyesi İmar ve Şehircilik Dairesi Başkanlığı, Konak/İZMİR',
    mesaiSaatleri: 'Pazartesi-Cuma 08:30-17:30'
  };
}
