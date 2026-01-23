import { useState } from 'react';
import Link from 'next/link';
import Layout from '../components/Layout';
import Seo from '../components/Seo';
import DebouncedInput from '../components/DebouncedInput';
import { useGA4 } from '../lib/useGA4';
import styles from '../styles/CalculationPage.module.css';

interface CalculationResult {
  maksimumHayvanSayisi: number;
  kullanilabilirAlanM2: number;
  detaylar: string[];
  tesisDetaylari?: {
    [key: string]: {
      tip: string;
      alan: number;
      hayvanSayisi: number;
      yasGrupDagilimi: {
        [key: string]: {
          yuzde: number;
          hayvanSayisi: number;
          hayvanBasinaAlan: number;
          toplamAlan: number;
          aciklama?: string;
        };
      };
    };
  };
}

type YasGrupDetay = {
  yuzde: number;
  hayvanSayisi: number;
  hayvanBasinaAlan: number;
  toplamAlan: number;
  aciklama?: string;
};

export default function KapasiteHesaplama() {
  const { trackCalculationStart } = useGA4();
  
  // Hayvan tipi seçimi - sadece biri seçilebilir
  const [hayvanTipi, setHayvanTipi] = useState<'buyukbas' | 'kucukbas'>('buyukbas');
  
  // Büyükbaş için tesis tipleri - birden fazla seçilebilir
  const [buyukbasTesisTipleri, setBuyukbasTesisTipleri] = useState<{
    kapali: boolean;
    yariAcik: boolean;
    acik: boolean;
  }>({
    kapali: false,
    yariAcik: false,
    acik: false
  });
  
  // Not: Alanlar, kapasite hesabında yaş grubu bazında ayrı toplanır (serbest/gezinti/gölgelik).
  
  // Küçükbaş için tesis tipleri
  const [kucukbasTesisTipleri, setKucukbasTesisTipleri] = useState<{
    kapali: boolean;
    yariAcik: boolean;
  }>({
    kapali: false,
    yariAcik: false
  });
  
  // Yaş grupları seçimi
  const [yasGruplari, setYasGruplari] = useState<string[]>([]);
  
  // Büyükbaş için bağlı durak seçimi (sadece kapalı ve yarı açık için)
  const [bagliDurak, setBagliDurak] = useState<{
    kapali: boolean;
    yariAcik: boolean;
  }>({
    kapali: false,
    yariAcik: false
  });

  // Bağlı durak sayıları (yaş grubuna göre)
  const [bagliDurakSayilari, setBagliDurakSayilari] = useState<{
    [tesisTipi: string]: {[yasGrubu: string]: number};
  }>({kapali: {}, yariAcik: {}});

  // Serbest alan (bağlı duraklı sistemde her yaş grubu için opsiyonel serbest alan)
  const [bagliSistemSerbestAlanlari, setBagliSistemSerbestAlanlari] = useState<{
    [tesisTipi: string]: {[yasGrubu: string]: number};
  }>({kapali: {}, yariAcik: {}});

  // Serbest sistem alanları (her yaş grubu için ayrılan alan)
  const [serbestSistemAlanlari, setSerbestSistemAlanlari] = useState<{
    [tesisTipi: string]: {[yasGrubu: string]: number};
  }>({kapali: {}, yariAcik: {}, acik: {}});

  // Gölgelik alanları (Yarı açık ve Açık sistemler için)
  const [golgelikAlanlari, setGolgelikAlanlari] = useState<{
    [tesisTipi: string]: number;
  }>({yariAcik: 0, acik: 0});

  // Buzağı barınma tipi ve sayısı
  // const [buzagiBarinmaTipi, setBuzagiBarinmaTipi] = useState<'padok' | 'kulube'>('padok'); // Artık kullanılmıyor (Karma sistem)
  const [buzagiKulubeSayisi, setBuzagiKulubeSayisi] = useState<number>(0);
  
  const [sonuc, setSonuc] = useState<CalculationResult | null>(null);

  // Büyükbaş serbest duraklı sistem alan gereksinimleri (m²/baş)
  const BUYUKBAS_SERBEST_DURAK: Record<string, number> = {
    '0-6': 1.8,    // 0-6 aylık
    '7-12': 4,     // 7-12 aylık
    '13-18': 6,    // 13-18 aylık
    '19+': 7       // 19 aylık ve üzeri
  };

  // Büyükbaş bağlı duraklı sistem durak boyutları (cm)
  const BUYUKBAS_BAGLI_DURAK: Record<string, {minGen: number; maxGen: number; minUz: number; maxUz: number}> = {
    '0-6': { minGen: 60, maxGen: 80, minUz: 130, maxUz: 160 },
    '7-12': { minGen: 70, maxGen: 100, minUz: 120, maxUz: 180 },
    '13-18': { minGen: 90, maxGen: 120, minUz: 145, maxUz: 240 },
    '19+': { minGen: 90, maxGen: 120, minUz: 145, maxUz: 240 }
  };

  // Küçükbaş kapalı/yarı açık kapalı alan gereksinimleri (m²/baş)
  const KUCUKBAS_KAPALI_ALAN: Record<string, number> = {
    '0-6': 0.7,
    '7-12': 1.4,
    '13+': 2
  };

  const hesapla = () => {
    trackCalculationStart('kapasite-hesaplama');
    
    const detaylar: string[] = [];
    let toplamHayvanSayisi = 0;
    let toplamKullanilabilirAlan = 0;
    const tesisDetaylari: CalculationResult['tesisDetaylari'] = {};

    if (hayvanTipi === 'buyukbas') {
      detaylar.push('=== BÜYÜKBAŞ HAYVAN KAPASİTE HESAPLAMASI ===');
      
      const secilenTesisTipleri = Object.entries(buyukbasTesisTipleri)
        .filter(([, secili]) => secili)
        .map(([tip]) => tip);

      let kulubeEklendi = false;

      secilenTesisTipleri.forEach(tesisTipi => {
        detaylar.push(`\n--- ${tesisTipi.toUpperCase()} TESİS ---`);
        
        const isBagliDurak = tesisTipi !== 'acik' && bagliDurak[tesisTipi as keyof typeof bagliDurak];
        
        let tesisHayvanSayisi = 0;
        let tesisToplamAlan = 0;
        const yasGrupDagilimi: Record<string, YasGrupDetay> = {};

        // AÇIK TESİS veya YARI AÇIK EK GÖLGELİK HESABI
        if (tesisTipi === 'acik') {
          const golgelikAlan = golgelikAlanlari.acik || 0;
          const kapasite = Math.floor(golgelikAlan / 2);
          
          tesisHayvanSayisi += kapasite;
          tesisToplamAlan += golgelikAlan;
          
          detaylar.push(`  AÇIK ALAN (GÖLGELİK): ${kapasite} baş (${golgelikAlan}m² / 2m²/baş)`);
          
          yasGrupDagilimi['genel'] = {
            yuzde: 100,
            hayvanSayisi: kapasite,
            hayvanBasinaAlan: 2,
            toplamAlan: golgelikAlan
          };
        } else {
          // KAPALI ve YARI AÇIK (KAPALI KISIM)
          yasGruplari.forEach(grup => {
            // 0-6 Ay Özel Hesaplama (Padok + Kulübe)
            if (grup === '0-6') {
              let grupKapasite = 0;
              let grupToplamAlan = 0;
              let detayText = '';

              if (isBagliDurak) {
                // Bağlı Durak (0-6 Ay)
                const durakSayisi = bagliDurakSayilari[tesisTipi]?.[grup] || 0;
                const padokAlani = bagliSistemSerbestAlanlari[tesisTipi]?.[grup] || 0;
                
                const durakOlculeri = BUYUKBAS_BAGLI_DURAK[grup];
                const durakGen = durakOlculeri ? durakOlculeri.minGen / 100 : 0;
                const durakUz = durakOlculeri ? durakOlculeri.minUz / 100 : 0;
                const durakAlani = durakGen * durakUz;
                
                grupKapasite += durakSayisi;
                grupToplamAlan += durakSayisi * durakAlani;
                detayText = `${durakSayisi} adet durak`;

                // Buzağılar için padok/padoğa benzer serbest alan kapasiteye dahil edilebilir (1.8 m²/buzağı)
                if (padokAlani > 0) {
                  const hayvanBasinaPadokAlan = BUYUKBAS_SERBEST_DURAK[grup]; // 1.8
                  const padokKapasite = Math.floor(padokAlani / hayvanBasinaPadokAlan);
                  grupKapasite += padokKapasite;
                  grupToplamAlan += padokAlani;
                  detayText += ` + ${padokKapasite} baş (Padok: ${padokAlani}m² / ${hayvanBasinaPadokAlan}m²/buzağı)`;
                }
              } else {
                // Serbest Sistem (Padok)
                const padokAlani = serbestSistemAlanlari[tesisTipi]?.[grup] || 0;
                const hayvanBasinaAlan = BUYUKBAS_SERBEST_DURAK[grup]; // 1.8
                
                if (hayvanBasinaAlan) {
                  const padokKapasite = Math.floor(padokAlani / hayvanBasinaAlan);
                  grupKapasite += padokKapasite;
                  grupToplamAlan += padokAlani;
                  detayText = `${padokKapasite} baş (Padok: ${padokAlani}m²)`;
                }
              }

              // Kulübe Hesabı (Her iki sisteme de eklenebilir)
              // Kulübe sayısı sadece bir kere eklenmeli (ilk tesise veya kullanıcı seçimine göre)
              // Şimdilik sadece ilk karşılaşılan tesise ekleyelim veya kullanıcıya tesis bazlı giriş yaptıralım.
              // UI'da kulübe sayısı global state'de tutuluyor (buzagiKulubeSayisi).
              // Bu yüzden sadece ilk uygun tesise ekleyelim.
              if (!kulubeEklendi && buzagiKulubeSayisi > 0) {
                grupKapasite += buzagiKulubeSayisi;
                detayText += ` + ${buzagiKulubeSayisi} baş (Kulübe)`;
                kulubeEklendi = true;
              }

              yasGrupDagilimi[grup] = {
                yuzde: 0,
                hayvanSayisi: grupKapasite,
                // Karma senaryoda ortalama alanı hesaplayıp tabloya yansıtıyoruz
                hayvanBasinaAlan: grupKapasite > 0 ? grupToplamAlan / grupKapasite : 0,
                toplamAlan: grupToplamAlan,
                aciklama: isBagliDurak
                  ? `Buzağı kapasitesi: durak + padok + kulübe (padok varsa ${BUYUKBAS_SERBEST_DURAK[grup]} m²/buzağı)`
                  : `Padok kapasitesi: alan / ${BUYUKBAS_SERBEST_DURAK[grup]} m²/buzağı`
              };
              
              tesisHayvanSayisi += grupKapasite;
              tesisToplamAlan += grupToplamAlan;
              detaylar.push(`  ${grup} ay: ${grupKapasite} baş (${detayText})`);
              
              return; // 0-6 ay işlemi tamamlandı
            }

            if (isBagliDurak) {
              // BAĞLI DURAK SİSTEMİ + Kapalı Alan (Serbest Duraklı)
              const durakSayisi = bagliDurakSayilari[tesisTipi]?.[grup] || 0;
              const kapaliAlanSerbestDurak = bagliSistemSerbestAlanlari[tesisTipi]?.[grup] || 0;

              // Mevzuat: Bağlı duraklı sistemde kapasite = durak sayısı
              let grupKapasite = durakSayisi;
              let grupToplamAlan = 0;
              let detayText = `${durakSayisi} adet durak ⇒ ${durakSayisi} baş`;

              // Eğer aynı tesiste serbest duraklı kapalı alan da varsa (7 m²/baş ile kapasite hesaplanır)
              if (kapaliAlanSerbestDurak > 0) {
                const hayvanBasinaAlan = BUYUKBAS_SERBEST_DURAK[grup]; // 7 m²/baş (19+ için)
                const serbestKapasite = Math.floor(kapaliAlanSerbestDurak / hayvanBasinaAlan);
                grupKapasite += serbestKapasite;
                grupToplamAlan += kapaliAlanSerbestDurak;
                detayText += ` + ${serbestKapasite} baş (Serbest duraklı kapalı alan: ${kapaliAlanSerbestDurak}m² / ${hayvanBasinaAlan}m²/baş)`;
              }

              yasGrupDagilimi[grup] = {
                yuzde: 0,
                hayvanSayisi: grupKapasite,
                hayvanBasinaAlan: grupKapasite > 0 && grupToplamAlan > 0 ? grupToplamAlan / grupKapasite : 0,
                toplamAlan: grupToplamAlan,
                aciklama: detayText
              };
              
              tesisHayvanSayisi += grupKapasite;
              tesisToplamAlan += grupToplamAlan;
              detaylar.push(`  ${grup} ay: ${grupKapasite} baş (${detayText})`);

            } else {
              // SERBEST SİSTEM
              const ayrilanAlan = serbestSistemAlanlari[tesisTipi]?.[grup] || 0;
              const hayvanBasinaAlan = BUYUKBAS_SERBEST_DURAK[grup];
              
              if (hayvanBasinaAlan) {
                const kapasite = Math.floor(ayrilanAlan / hayvanBasinaAlan);
                
                yasGrupDagilimi[grup] = {
                  yuzde: 0,
                  hayvanSayisi: kapasite,
                  hayvanBasinaAlan: hayvanBasinaAlan,
                  toplamAlan: ayrilanAlan
                };
                
                tesisHayvanSayisi += kapasite;
                tesisToplamAlan += ayrilanAlan;
                detaylar.push(`  ${grup} ay: ${kapasite} baş (${ayrilanAlan}m² / ${hayvanBasinaAlan}m²/baş)`);
              }
            }
          });

          // YARI AÇIK İÇİN EK GÖLGELİK HESABI
          if (tesisTipi === 'yariAcik') {
            const golgelikAlan = golgelikAlanlari.yariAcik || 0;
            if (golgelikAlan > 0) {
              const golgelikKapasite = Math.floor(golgelikAlan / 2);
              tesisHayvanSayisi += golgelikKapasite;
              tesisToplamAlan += golgelikAlan;
              detaylar.push(`  AÇIK ALAN (GÖLGELİK): ${golgelikKapasite} baş (${golgelikAlan}m² / 2m²/baş)`);
              
              yasGrupDagilimi['golgelik'] = {
                yuzde: 0,
                hayvanSayisi: golgelikKapasite,
                hayvanBasinaAlan: 2,
                toplamAlan: golgelikAlan
              };
            }
          }
        }

        // Büyükbaş sonuç tablosu için yüzde ve ortalama alanları normalize et
        Object.entries(yasGrupDagilimi).forEach(([grupKey, grupDetay]) => {
          const yuzde = tesisHayvanSayisi > 0
            ? Math.round((grupDetay.hayvanSayisi / tesisHayvanSayisi) * 100)
            : 0;

          const hayvanBasinaAlan = grupDetay.hayvanBasinaAlan > 0
            ? grupDetay.hayvanBasinaAlan
            : (grupDetay.hayvanSayisi > 0 ? grupDetay.toplamAlan / grupDetay.hayvanSayisi : 0);

          yasGrupDagilimi[grupKey] = {
            ...grupDetay,
            yuzde,
            hayvanBasinaAlan,
          };
        });

        tesisDetaylari[tesisTipi] = {
          tip: tesisTipi,
          alan: tesisToplamAlan,
          hayvanSayisi: tesisHayvanSayisi,
          yasGrupDagilimi
        };

        toplamHayvanSayisi += tesisHayvanSayisi;
        toplamKullanilabilirAlan += tesisToplamAlan;
        detaylar.push(`Tesis toplamı: ${tesisHayvanSayisi} baş`);
      });
      
    } else {
      // KÜÇÜKBAŞ
      detaylar.push('=== KÜÇÜKBAŞ HAYVAN KAPASİTE HESAPLAMASI ===');
      
      const secilenTesisTipleri = Object.entries(kucukbasTesisTipleri)
        .filter(([, secili]) => secili)
        .map(([tip]) => tip);

      secilenTesisTipleri.forEach(tesisTipi => {
        detaylar.push(`\n--- ${tesisTipi.toUpperCase()} TESİS ---`);
        
        let tesisHayvanSayisi = 0;
        let tesisToplamAlan = 0;
        const yasGrupDagilimi: Record<string, YasGrupDetay> = {};

        yasGruplari.forEach(grup => {
           const ayrilanAlan = serbestSistemAlanlari[tesisTipi]?.[grup] || 0;
           const hayvanBasinaAlan = KUCUKBAS_KAPALI_ALAN[grup];
           
           if (hayvanBasinaAlan) {
             const kapasite = Math.floor(ayrilanAlan / hayvanBasinaAlan);
             
             yasGrupDagilimi[grup] = {
               yuzde: 0,
               hayvanSayisi: kapasite,
               hayvanBasinaAlan: hayvanBasinaAlan,
               toplamAlan: ayrilanAlan
             };
             
             tesisHayvanSayisi += kapasite;
             tesisToplamAlan += ayrilanAlan;
             detaylar.push(`  ${grup} ay: ${kapasite} baş (${ayrilanAlan}m² / ${hayvanBasinaAlan}m²/baş)`);
           }
        });

        // YARI AÇIK İÇİN EK GÖLGELİK HESABI (KÜÇÜKBAŞ)
        if (tesisTipi === 'yariAcik') {
          const golgelikAlan = golgelikAlanlari.yariAcik || 0;
          if (golgelikAlan > 0) {
            const golgelikKapasite = Math.floor(golgelikAlan / 0.8);
            tesisHayvanSayisi += golgelikKapasite;
            tesisToplamAlan += golgelikAlan;
            detaylar.push(`  AÇIK ALAN (GÖLGELİK): ${golgelikKapasite} baş (${golgelikAlan}m² / 0.8m²/baş)`);
            
            yasGrupDagilimi['golgelik'] = {
              yuzde: 0,
              hayvanSayisi: golgelikKapasite,
              hayvanBasinaAlan: 0.8,
              toplamAlan: golgelikAlan
            };
          }
        }

        // Yüzde ve ortalama alanları nihai tablo için normalize et
        Object.entries(yasGrupDagilimi).forEach(([grupKey, grupDetay]) => {
          const yuzde = tesisHayvanSayisi > 0
            ? Math.round((grupDetay.hayvanSayisi / tesisHayvanSayisi) * 100)
            : 0;

          const hayvanBasinaAlan = grupDetay.hayvanBasinaAlan > 0
            ? grupDetay.hayvanBasinaAlan
            : (grupDetay.hayvanSayisi > 0 ? grupDetay.toplamAlan / grupDetay.hayvanSayisi : 0);

          yasGrupDagilimi[grupKey] = {
            ...grupDetay,
            yuzde,
            hayvanBasinaAlan,
          };
        });

        tesisDetaylari[tesisTipi] = {
          tip: tesisTipi,
          alan: tesisToplamAlan,
          hayvanSayisi: tesisHayvanSayisi,
          yasGrupDagilimi
        };

        toplamHayvanSayisi += tesisHayvanSayisi;
        toplamKullanilabilirAlan += tesisToplamAlan;
        detaylar.push(`Tesis toplamı: ${tesisHayvanSayisi} baş`);
      });
    }

    detaylar.push(`\n=== GENEL TOPLAM: ${toplamHayvanSayisi} BAŞ ===`);

    const sonuc: CalculationResult = {
      maksimumHayvanSayisi: toplamHayvanSayisi,
      kullanilabilirAlanM2: toplamKullanilabilirAlan,
      detaylar,
      tesisDetaylari
    };
    
    setSonuc(sonuc);
  };

  const yasGrupOlustur = (hayvanTipi: string) => {
    if (hayvanTipi === 'buyukbas') {
      return ['0-6', '7-12', '13-18', '19+'];
    } else {
      return ['0-6', '7-12', '13+'];
    }
  };

  const yasGrupLabel = (grup: string, hayvanTipi: string) => {
    if (hayvanTipi === 'buyukbas') {
      const labels: Record<string, string> = {
        '0-6': '0-6 aylık (buzağı)',
        '7-12': '7-12 aylık',
        '13-18': '13-18 aylık',
        '19+': '19+ aylık (yetişkin)',
        'golgelik': 'Açık Alan / Gölgelik',
        'genel': 'Genel Kapasite'
      };
      return labels[grup] || grup;
    } else {
      const labels: Record<string, string> = {
        '0-6': '0-6 aylık',
        '7-12': '7-12 aylık',
        '13+': '13+ aylık',
        'golgelik': 'Açık Alan / Gölgelik'
      };
      return labels[grup] || grup;
    }
  };

  const hesaplaButtonDisabled = () => {
    const tesisSec = hayvanTipi === 'buyukbas' 
      ? !Object.values(buyukbasTesisTipleri).some(v => v)
      : !Object.values(kucukbasTesisTipleri).some(v => v);
    
    if (tesisSec) return true;
    if (yasGruplari.length === 0) return true;
    
    // Alan kontrolü
    const secilenTesisler = hayvanTipi === 'buyukbas'
      ? Object.entries(buyukbasTesisTipleri).filter(([, v]) => v).map(([k]) => k)
      : Object.entries(kucukbasTesisTipleri).filter(([, v]) => v).map(([k]) => k);
    
    for (const tesis of secilenTesisler) {
      const isBagliDurak = tesis !== 'acik' && hayvanTipi === 'buyukbas' && bagliDurak[tesis as keyof typeof bagliDurak];
      
      // 0-6 Ay için özel kontrol (Padok veya Kulübe veya Durak)
      const has06 = yasGruplari.includes('0-6');
      if (has06) {
        // 0-6 ay için en az bir veri girilmiş olmalı
        // Bağlı ise: Durak sayısı > 0
        // Serbest ise: Padok alanı > 0
        // VEYA Kulübe sayısı > 0 (her iki durumda da)
        
        let hasData06 = false;
        if (isBagliDurak) {
          const durak = bagliDurakSayilari[tesis as keyof typeof bagliDurakSayilari]?.['0-6'] || 0;
          const padok = bagliSistemSerbestAlanlari[tesis as keyof typeof bagliSistemSerbestAlanlari]?.['0-6'] || 0;
          if (durak > 0 || padok > 0) hasData06 = true;
        } else {
          const padok = serbestSistemAlanlari[tesis as keyof typeof serbestSistemAlanlari]?.['0-6'] || 0;
          if (padok > 0) hasData06 = true;
        }
        
        if (buzagiKulubeSayisi > 0) hasData06 = true;
        
        // Eğer sadece 0-6 seçili ise ve veri yoksa disable et
        if (yasGruplari.length === 1 && !hasData06) return true;
        
        // Diğer yaş grupları varsa ve 0-6 için veri yoksa, bu bir hata olmayabilir (belki sadece diğerleri için tesis var)
        // Ancak kullanıcı 0-6 seçtiyse bir şeyler girmeli.
        if (!hasData06) return true;
      }

      const yasGruplariFiltered = yasGruplari.filter(g => g !== '0-6');

      if (isBagliDurak) {
        // Bağlı durak: Durak sayıları zorunlu
        const duraklar = bagliDurakSayilari[tesis as keyof typeof bagliDurakSayilari] || {};
        
        for (const grup of yasGruplariFiltered) {
          if (!duraklar[grup] || duraklar[grup] <= 0) return true;
        }
      } else {
        // Serbest sistem: Ayrılan alanlar zorunlu
        const alanlar = serbestSistemAlanlari[tesis as keyof typeof serbestSistemAlanlari] || {};
        
        for (const grup of yasGruplariFiltered) {
          // Açık tesis için alan kontrolü farklı (gölgelik)
          if (tesis === 'acik') continue; 
          
          if (!alanlar[grup] || alanlar[grup] <= 0) return true;
        }
      }
      
      // Açık tesis kontrolü
      if (tesis === 'acik' && hayvanTipi === 'buyukbas') {
         if ((golgelikAlanlari.acik || 0) <= 0) return true;
      }
    }
    
    return false;
  };

  return (
    <>
      <Seo
        title="Hayvancılık İşletmeleri Kapasite Hesaplama | Büyükbaş ve Küçükbaş"
        description="Büyükbaş ve küçükbaş hayvancılık işletmeleri için kapasite raporu hesaplama. Kapalı, yarı açık ve açık tesis tipleri için detaylı kapasite analizi."
        canonical="https://tarimimar.com.tr/sigir-ahiri-kapasite-hesaplama/"
        keywords="hayvancılık kapasite hesaplama, büyükbaş kapasite, küçükbaş kapasite, ahır kapasitesi, kapalı işletme, yarı açık işletme, açık işletme"
      />

      <Layout>
        <div className={styles.calculationContainer}>
          <div className={styles.calculationHeader}>
            <h1>🐄 Hayvancılık İşletmeleri Kapasite Hesaplama</h1>
            <p>Büyükbaş ve küçükbaş hayvancılık işletmeleriniz için mevzuata uygun kapasite hesaplaması yapın.</p>
          </div>

          <div className={styles.calculationForm}>
            {/* Hayvan Tipi Seçimi */}
            <div className={styles.formSection}>
              <h3>1. Hayvan Tipi Seçimi</h3>
              <div className={styles.radioGroup}>
                <label>
                  <input
                    type="radio"
                    checked={hayvanTipi === 'buyukbas'}
                    onChange={() => {
                      setHayvanTipi('buyukbas');
                      setYasGruplari([]);
                      setSonuc(null);
                    }}
                  />
                  🐄 Büyükbaş (Sığır, Dana, vb.)
                </label>
                <label>
                  <input
                    type="radio"
                    checked={hayvanTipi === 'kucukbas'}
                    onChange={() => {
                      setHayvanTipi('kucukbas');
                      setYasGruplari([]);
                      setSonuc(null);
                    }}
                  />
                  🐑 Küçükbaş (Koyun, Keçi, vb.)
                </label>
              </div>
              <small style={{display: 'block', marginTop: '0.5rem', color: '#6c757d'}}>
                ⚠️ Büyükbaş ve küçükbaş için evraklar farklı olduğundan aynı anda hesaplama yapılamaz.
              </small>
            </div>

            {/* Tesis Tipi Seçimi */}
            <div className={styles.formSection}>
              <h3>2. Tesis Tipi Seçimi {hayvanTipi === 'buyukbas' ? '(Birden fazla seçilebilir)' : ''}</h3>
              
              {hayvanTipi === 'buyukbas' && (
                <div className={styles.checkboxGroup}>
                  <label>
                    <input
                      type="checkbox"
                      checked={buyukbasTesisTipleri.kapali}
                      onChange={(e) => {
                        setBuyukbasTesisTipleri({...buyukbasTesisTipleri, kapali: e.target.checked});
                        setSonuc(null);
                      }}
                    />
                    🏠 Kapalı İşletme
                  </label>
                  <label>
                    <input
                      type="checkbox"
                      checked={buyukbasTesisTipleri.yariAcik}
                      onChange={(e) => {
                        setBuyukbasTesisTipleri({...buyukbasTesisTipleri, yariAcik: e.target.checked});
                        setSonuc(null);
                      }}
                    />
                    🏚️ Yarı Açık İşletme
                  </label>
                  <label>
                    <input
                      type="checkbox"
                      checked={buyukbasTesisTipleri.acik}
                      onChange={(e) => {
                        setBuyukbasTesisTipleri({...buyukbasTesisTipleri, acik: e.target.checked});
                        setSonuc(null);
                      }}
                    />
                    🌳 Açık İşletme
                  </label>
                </div>
              )}

              {hayvanTipi === 'kucukbas' && (
                <div className={styles.checkboxGroup}>
                  <label>
                    <input
                      type="checkbox"
                      checked={kucukbasTesisTipleri.kapali}
                      onChange={(e) => {
                        setKucukbasTesisTipleri({...kucukbasTesisTipleri, kapali: e.target.checked});
                        setSonuc(null);
                      }}
                    />
                    🏠 Kapalı İşletme
                  </label>
                  <label>
                    <input
                      type="checkbox"
                      checked={kucukbasTesisTipleri.yariAcik}
                      onChange={(e) => {
                        setKucukbasTesisTipleri({...kucukbasTesisTipleri, yariAcik: e.target.checked});
                        setSonuc(null);
                      }}
                    />
                    🏚️ Yarı Açık İşletme
                  </label>
                </div>
              )}

              <small style={{display: 'block', marginTop: '0.5rem', color: '#6c757d'}}>
                <strong>Tanımlar:</strong><br />
                • <strong>Kapalı:</strong> Dört tarafı duvarla çevrili, üzeri kapalı<br />
                • <strong>Yarı Açık:</strong> En az bir tarafı açık, genellikle üç tarafı duvarla çevrili, üzeri kapalı<br />
                {hayvanTipi === 'buyukbas' && '• '}
                {hayvanTipi === 'buyukbas' && <strong>Açık:</strong>}
                {hayvanTipi === 'buyukbas' && ' Çevresi duvar/tel örgü ile çevrili, gölgeliklerin olduğu'}
              </small>
            </div>

            {/* Yaş Grubu Seçimi */}
            {((hayvanTipi === 'buyukbas' && Object.values(buyukbasTesisTipleri).some(v => v)) ||
              (hayvanTipi === 'kucukbas' && Object.values(kucukbasTesisTipleri).some(v => v))) && (
              <div className={styles.formSection}>
                <h3>3. Yaş Grubu Seçimi</h3>
                <div className={styles.checkboxGroup}>
                  {yasGrupOlustur(hayvanTipi).map(grup => (
                    <div key={grup} style={{marginBottom: '0.5rem'}}>
                      <label>
                        <input
                          type="checkbox"
                          checked={yasGruplari.includes(grup)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setYasGruplari([...yasGruplari, grup]);
                            } else {
                              setYasGruplari(yasGruplari.filter(g => g !== grup));
                            }
                            setSonuc(null);
                          }}
                        />
                        {yasGrupLabel(grup, hayvanTipi)}
                      </label>
                      
                      {/* Buzağı Barınma Tipi Seçimi - KALDIRILDI (Tesis Alanları bölümüne taşındı) */}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tesis Alanları */}
            {(hayvanTipi === 'buyukbas' && Object.values(buyukbasTesisTipleri).some(v => v)) ||
             (hayvanTipi === 'kucukbas' && Object.values(kucukbasTesisTipleri).some(v => v)) ? (
              <div className={styles.formSection}>
                <h3>4. Tesis Alanları ve Kapasite Bilgileri</h3>

                <div style={{marginTop: '0.75rem', marginBottom: '1rem', padding: '0.75rem 1rem', border: '1px solid #e0e0e0', borderRadius: '8px', background: '#fafafa'}}>
                  <div style={{fontWeight: 700, marginBottom: '0.25rem'}}>Mevzuat Notu (Özet)</div>
                  <div style={{fontSize: '0.9rem', color: '#555', lineHeight: 1.5}}>
                    <strong>Bağlı duraklı sistem:</strong> Kapasite = durak sayısı. Aynı tesiste serbest duraklı kapalı alan da varsa o alan için ayrıca m²/baş üzerinden kapasite hesaplanır.<br/>
                    <strong>Serbest duraklı/serbest dolaşımlı sistem:</strong> Kapasite, yaş grubuna göre gereken asgari alan (m²/baş) üzerinden hesaplanır.<br/>
                    <strong>Açık/yarı açık işletmeler:</strong> Gölgelik alanı ayrıca dikkate alınır (asgari 2 m²/baş).<br/>
                    <strong>Not:</strong> Depo/yem deposu gibi hayvanın fiilen bulunmadığı alanlar kapasite hesabına dahil edilmez.
                  </div>
                </div>
                
                {/* BÜYÜKBAŞ KAPALI */}
                {hayvanTipi === 'buyukbas' && buyukbasTesisTipleri.kapali && (
                  <div style={{marginBottom: '1.5rem', padding: '1rem', border: '2px solid #4caf50', borderRadius: '8px', background: '#f1f8f4'}}>
                    <h4 style={{marginTop: 0}}>🏠 Kapalı Tesis</h4>
                    
                    <div className={styles.checkboxGroup}>
                      <label>
                        <input
                          type="checkbox"
                          checked={bagliDurak.kapali}
                          onChange={(e) => {
                            setBagliDurak({...bagliDurak, kapali: e.target.checked});
                            setSonuc(null);
                          }}
                        />
                        Bağlı duraklı sistem kullanılacak
                      </label>
                    </div>
                    
                    {yasGruplari.length === 0 ? (
                      <div style={{color: '#d32f2f'}}>⚠️ Lütfen önce yaş grubu seçiniz.</div>
                    ) : (
                      <div style={{marginTop: '1rem'}}>
                        {yasGruplari.map(grup => {
                          // 0-6 Ay için özel görünüm
                          if (grup === '0-6') {
                            return (
                              <div key={grup} style={{marginBottom: '1rem', padding: '0.5rem', borderBottom: '1px solid #ddd', background: '#e3f2fd', borderRadius: '4px'}}>
                                <div style={{fontWeight: 'bold', marginBottom: '0.5rem'}}>{yasGrupLabel(grup, hayvanTipi)}</div>
                                
                                {bagliDurak.kapali ? (
                                  <>
                                    <div className={styles.inputGroup}>
                                      <label>Durak Sayısı (adet):</label>
                                      <DebouncedInput
                                        type="number"
                                        min="0"
                                        value={bagliDurakSayilari.kapali[grup] || ''}
                                        onChange={(val) => setBagliDurakSayilari({
                                          ...bagliDurakSayilari,
                                          kapali: {...bagliDurakSayilari.kapali, [grup]: parseInt(val) || 0}
                                        })}
                                      />
                                      <small style={{color: '#d32f2f'}}>
                                        ⚠️ Durak Ölçüleri: Genişlik {BUYUKBAS_BAGLI_DURAK[grup].minGen}-{BUYUKBAS_BAGLI_DURAK[grup].maxGen}cm, 
                                        Uzunluk {BUYUKBAS_BAGLI_DURAK[grup].minUz}-{BUYUKBAS_BAGLI_DURAK[grup].maxUz}cm olmalıdır.
                                      </small>
                                    </div>
                                    <div className={styles.inputGroup}>
                                      <label>Padok Alanı (m²) [Opsiyonel]:</label>
                                      <DebouncedInput
                                        type="number"
                                        min="0"
                                        value={bagliSistemSerbestAlanlari.kapali[grup] || ''}
                                        onChange={(val) => setBagliSistemSerbestAlanlari({
                                          ...bagliSistemSerbestAlanlari,
                                          kapali: {...bagliSistemSerbestAlanlari.kapali, [grup]: parseFloat(val) || 0}
                                        })}
                                      />
                                      <small>Padokta kapasite {BUYUKBAS_SERBEST_DURAK[grup]}m²/buzağı üzerinden hesaplanır.</small>
                                    </div>
                                  </>
                                ) : (
                                  <div className={styles.inputGroup}>
                                    <label>Padok Alanı (m²):</label>
                                    <DebouncedInput
                                      type="number"
                                      min="0"
                                      value={serbestSistemAlanlari.kapali[grup] || ''}
                                      onChange={(val) => setSerbestSistemAlanlari({
                                        ...serbestSistemAlanlari,
                                        kapali: {...serbestSistemAlanlari.kapali, [grup]: parseFloat(val) || 0}
                                      })}
                                    />
                                    <small>Hayvan başına {BUYUKBAS_SERBEST_DURAK[grup]}m² gereklidir.</small>
                                  </div>
                                )}

                                {/* Kulübe Sayısı - Her iki durumda da girilebilir */}
                                <div className={styles.inputGroup} style={{marginTop: '0.5rem', borderTop: '1px dashed #ccc', paddingTop: '0.5rem'}}>
                                  <label>Kulübe Sayısı (Adet) [Opsiyonel]:</label>
                                  <DebouncedInput
                                    type="number"
                                    min="0"
                                    value={buzagiKulubeSayisi || ''}
                                    onChange={(val) => {
                                      setBuzagiKulubeSayisi(parseInt(val) || 0);
                                      setSonuc(null);
                                    }}
                                  />
                                  <small>Her kulübe 1 buzağı kapasitesi ekler.</small>
                                </div>
                              </div>
                            );
                          }
                          
                          return (
                            <div key={grup} style={{marginBottom: '1rem', padding: '0.5rem', borderBottom: '1px solid #ddd'}}>
                              <div style={{fontWeight: 'bold', marginBottom: '0.5rem'}}>{yasGrupLabel(grup, hayvanTipi)}</div>
                              
                              {bagliDurak.kapali ? (
                                <>
                                  <div className={styles.inputGroup}>
                                    <label>Durak Sayısı (adet):</label>
                                    <DebouncedInput
                                      type="number"
                                      min="0"
                                      value={bagliDurakSayilari.kapali[grup] || ''}
                                      onChange={(val) => setBagliDurakSayilari({
                                        ...bagliDurakSayilari,
                                        kapali: {...bagliDurakSayilari.kapali, [grup]: parseInt(val) || 0}
                                      })}
                                    />
                                    <small style={{color: '#d32f2f'}}>
                                      ⚠️ Durak Ölçüleri: Genişlik {BUYUKBAS_BAGLI_DURAK[grup].minGen}-{BUYUKBAS_BAGLI_DURAK[grup].maxGen}cm, 
                                      Uzunluk {BUYUKBAS_BAGLI_DURAK[grup].minUz}-{BUYUKBAS_BAGLI_DURAK[grup].maxUz}cm olmalıdır.
                                    </small>
                                  </div>
                                  <div className={styles.inputGroup}>
                                    <label>Serbest Duraklı Kapalı Alan (m²) [Opsiyonel]:</label>
                                    <DebouncedInput
                                      type="number"
                                      min="0"
                                      value={bagliSistemSerbestAlanlari.kapali[grup] || ''}
                                      onChange={(val) => setBagliSistemSerbestAlanlari({
                                        ...bagliSistemSerbestAlanlari,
                                        kapali: {...bagliSistemSerbestAlanlari.kapali, [grup]: parseFloat(val) || 0}
                                      })}
                                    />
                                    <small>Bağlı durak dışında aynı tesiste serbest duraklı alan varsa kapasite {BUYUKBAS_SERBEST_DURAK[grup]}m²/baş üzerinden eklenir.</small>
                                  </div>
                                </>
                              ) : (
                                <div className={styles.inputGroup}>
                                  <label>Ayrılan Alan (m²):</label>
                                  <DebouncedInput
                                    type="number"
                                    min="0"
                                    value={serbestSistemAlanlari.kapali[grup] || ''}
                                    onChange={(val) => setSerbestSistemAlanlari({
                                      ...serbestSistemAlanlari,
                                      kapali: {...serbestSistemAlanlari.kapali, [grup]: parseFloat(val) || 0}
                                    })}
                                  />
                                  <small>Hayvan başına {BUYUKBAS_SERBEST_DURAK[grup]}m² gereklidir.</small>
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                )}

                {/* BÜYÜKBAŞ YARI AÇIK */}
                {hayvanTipi === 'buyukbas' && buyukbasTesisTipleri.yariAcik && (
                  <div style={{marginBottom: '1.5rem', padding: '1rem', border: '2px solid #ff9800', borderRadius: '8px', background: '#fff8f0'}}>
                    <h4 style={{marginTop: 0}}>🏚️ Yarı Açık Tesis</h4>
                    
                    <div className={styles.checkboxGroup}>
                      <label>
                        <input
                          type="checkbox"
                          checked={bagliDurak.yariAcik}
                          onChange={(e) => {
                            setBagliDurak({...bagliDurak, yariAcik: e.target.checked});
                            setSonuc(null);
                          }}
                        />
                        Kapalı kısımda bağlı duraklı sistem kullanılacak
                      </label>
                    </div>

                    {yasGruplari.length === 0 ? (
                      <div style={{color: '#d32f2f'}}>⚠️ Lütfen önce yaş grubu seçiniz.</div>
                    ) : (
                      <div style={{marginTop: '1rem'}}>
                        {yasGruplari.map(grup => {
                          // 0-6 Ay Özel UI (Karma Sistem)
                          if (grup === '0-6') {
                            return (
                              <div key={grup} style={{marginBottom: '1rem', padding: '0.5rem', borderBottom: '1px solid #ddd', backgroundColor: '#fff'}}>
                                <div style={{fontWeight: 'bold', marginBottom: '0.5rem', color: '#d35400'}}>
                                  {yasGrupLabel(grup, hayvanTipi)} (Karma Barınma)
                                </div>
                                <small style={{display: 'block', marginBottom: '0.5rem', color: '#666'}}>
                                  Buzağılar için hem padok/durak hem de bireysel kulübe kapasitesi birlikte hesaplanır.
                                </small>

                                {bagliDurak.yariAcik ? (
                                  <>
                                    <div className={styles.inputGroup}>
                                      <label>Durak Sayısı (adet):</label>
                                      <DebouncedInput
                                        type="number"
                                        min="0"
                                        value={bagliDurakSayilari.yariAcik[grup] || ''}
                                        onChange={(val) => setBagliDurakSayilari({
                                          ...bagliDurakSayilari,
                                          yariAcik: {...bagliDurakSayilari.yariAcik, [grup]: parseInt(val) || 0}
                                        })}
                                      />
                                      <small style={{color: '#d32f2f'}}>
                                        ⚠️ Durak Ölçüleri: Genişlik {BUYUKBAS_BAGLI_DURAK[grup].minGen}-{BUYUKBAS_BAGLI_DURAK[grup].maxGen}cm, 
                                        Uzunluk {BUYUKBAS_BAGLI_DURAK[grup].minUz}-{BUYUKBAS_BAGLI_DURAK[grup].maxUz}cm olmalıdır.
                                      </small>
                                    </div>
                                    <div className={styles.inputGroup}>
                                      <label>Padok Alanı (m²) [Opsiyonel]:</label>
                                      <DebouncedInput
                                        type="number"
                                        min="0"
                                        value={bagliSistemSerbestAlanlari.yariAcik[grup] || ''}
                                        onChange={(val) => setBagliSistemSerbestAlanlari({
                                          ...bagliSistemSerbestAlanlari,
                                          yariAcik: {...bagliSistemSerbestAlanlari.yariAcik, [grup]: parseFloat(val) || 0}
                                        })}
                                      />
                                      <small>Padokta kapasite {BUYUKBAS_SERBEST_DURAK[grup]}m²/buzağı üzerinden hesaplanır.</small>
                                    </div>
                                  </>
                                ) : (
                                  <div className={styles.inputGroup}>
                                    <label>Ayrılan Kapalı Alan (m²):</label>
                                    <DebouncedInput
                                      type="number"
                                      min="0"
                                      value={serbestSistemAlanlari.yariAcik[grup] || ''}
                                      onChange={(val) => setSerbestSistemAlanlari({
                                        ...serbestSistemAlanlari,
                                        yariAcik: {...serbestSistemAlanlari.yariAcik, [grup]: parseFloat(val) || 0}
                                      })}
                                    />
                                    <small>Hayvan başına {BUYUKBAS_SERBEST_DURAK[grup]}m² gereklidir.</small>
                                  </div>
                                )}

                                {/* Kulübe Sayısı - Her iki durumda da girilebilir */}
                                <div className={styles.inputGroup} style={{marginTop: '0.5rem', borderTop: '1px dashed #ccc', paddingTop: '0.5rem'}}>
                                  <label>Kulübe Sayısı (Adet) [Opsiyonel]:</label>
                                  <DebouncedInput
                                    type="number"
                                    min="0"
                                    value={buzagiKulubeSayisi || ''}
                                    onChange={(val) => {
                                      setBuzagiKulubeSayisi(parseInt(val) || 0);
                                      setSonuc(null);
                                    }}
                                  />
                                  <small>Her kulübe 1 buzağı kapasitesi ekler.</small>
                                </div>
                              </div>
                            );
                          }
                          
                          return (
                            <div key={grup} style={{marginBottom: '1rem', padding: '0.5rem', borderBottom: '1px solid #ddd'}}>
                              <div style={{fontWeight: 'bold', marginBottom: '0.5rem'}}>{yasGrupLabel(grup, hayvanTipi)}</div>
                              
                              {bagliDurak.yariAcik ? (
                                <>
                                  <div className={styles.inputGroup}>
                                    <label>Durak Sayısı (adet):</label>
                                    <DebouncedInput
                                      type="number"
                                      min="0"
                                      value={bagliDurakSayilari.yariAcik[grup] || ''}
                                      onChange={(val) => setBagliDurakSayilari({
                                        ...bagliDurakSayilari,
                                        yariAcik: {...bagliDurakSayilari.yariAcik, [grup]: parseInt(val) || 0}
                                      })}
                                    />
                                  </div>
                                  <div className={styles.inputGroup}>
                                    <label>Serbest Duraklı Kapalı Alan (m²) [Opsiyonel]:</label>
                                    <DebouncedInput
                                      type="number"
                                      min="0"
                                      value={bagliSistemSerbestAlanlari.yariAcik[grup] || ''}
                                      onChange={(val) => setBagliSistemSerbestAlanlari({
                                        ...bagliSistemSerbestAlanlari,
                                        yariAcik: {...bagliSistemSerbestAlanlari.yariAcik, [grup]: parseFloat(val) || 0}
                                      })}
                                    />
                                    <small>Bağlı durak dışında aynı tesiste serbest duraklı alan varsa kapasite {BUYUKBAS_SERBEST_DURAK[grup]}m²/baş üzerinden eklenir.</small>
                                  </div>
                                </>
                              ) : (
                                <div className={styles.inputGroup}>
                                  <label>Ayrılan Kapalı Alan (m²):</label>
                                  <DebouncedInput
                                    type="number"
                                    min="0"
                                    value={serbestSistemAlanlari.yariAcik[grup] || ''}
                                    onChange={(val) => setSerbestSistemAlanlari({
                                      ...serbestSistemAlanlari,
                                      yariAcik: {...serbestSistemAlanlari.yariAcik, [grup]: parseFloat(val) || 0}
                                    })}
                                  />
                                  <small>Hayvan başına {BUYUKBAS_SERBEST_DURAK[grup]}m² gereklidir.</small>
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}

                    <div style={{marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #ddd'}}>
                      <div className={styles.inputGroup}>
                        <label style={{fontWeight: 'bold'}}>Açık Alan / Gölgelik Alanı (m²) [Opsiyonel]:</label>
                        <DebouncedInput
                          type="number"
                          min="0"
                          value={golgelikAlanlari.yariAcik || ''}
                          onChange={(val) => setGolgelikAlanlari({
                            ...golgelikAlanlari,
                            yariAcik: parseFloat(val) || 0
                          })}
                        />
                        <small>Kapalı alan dışındaki gölgelikli alanlar (2m²/baş)</small>
                      </div>
                    </div>
                  </div>
                )}

                {/* BÜYÜKBAŞ AÇIK */}
                {hayvanTipi === 'buyukbas' && buyukbasTesisTipleri.acik && (
                  <div style={{marginBottom: '1.5rem', padding: '1rem', border: '2px solid #2196f3', borderRadius: '8px', background: '#f0f8ff'}}>
                    <h4 style={{marginTop: 0}}>🌳 Açık Tesis</h4>
                    
                    <div className={styles.inputGroup}>
                      <label style={{fontWeight: 'bold'}}>Toplam Gölgelik Alanı (m²):</label>
                      <DebouncedInput
                        type="number"
                        min="0"
                        value={golgelikAlanlari.acik || ''}
                        onChange={(val) => setGolgelikAlanlari({
                          ...golgelikAlanlari,
                          acik: parseFloat(val) || 0
                        })}
                      />
                      <small>Açık tesislerde kapasite gölgelik alanına göre hesaplanır (2m²/baş).</small>
                    </div>
                  </div>
                )}

                {/* KÜÇÜKBAŞ KAPALI */}
                {hayvanTipi === 'kucukbas' && kucukbasTesisTipleri.kapali && (
                  <div style={{marginBottom: '1.5rem', padding: '1rem', border: '2px solid #4caf50', borderRadius: '8px', background: '#f1f8f4'}}>
                    <h4 style={{marginTop: 0}}>🏠 Kapalı Tesis</h4>
                    
                    {yasGruplari.length === 0 ? (
                      <div style={{color: '#d32f2f'}}>⚠️ Lütfen önce yaş grubu seçiniz.</div>
                    ) : (
                      <div style={{marginTop: '1rem'}}>
                        {yasGruplari.map(grup => (
                          <div key={grup} style={{marginBottom: '1rem', padding: '0.5rem', borderBottom: '1px solid #ddd'}}>
                            <div style={{fontWeight: 'bold', marginBottom: '0.5rem'}}>{yasGrupLabel(grup, hayvanTipi)}</div>
                            
                            <div className={styles.inputGroup}>
                              <label>Ayrılan Alan (m²):</label>
                              <DebouncedInput
                                type="number"
                                min="0"
                                value={serbestSistemAlanlari.kapali[grup] || ''}
                                onChange={(val) => setSerbestSistemAlanlari({
                                  ...serbestSistemAlanlari,
                                  kapali: {...serbestSistemAlanlari.kapali, [grup]: parseFloat(val) || 0}
                                })}
                              />
                              <small>Hayvan başına {KUCUKBAS_KAPALI_ALAN[grup]}m² gereklidir.</small>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* KÜÇÜKBAŞ YARI AÇIK */}
                {hayvanTipi === 'kucukbas' && kucukbasTesisTipleri.yariAcik && (
                  <div style={{marginBottom: '1.5rem', padding: '1rem', border: '2px solid #ff9800', borderRadius: '8px', background: '#fff8f0'}}>
                    <h4 style={{marginTop: 0}}>🏚️ Yarı Açık Tesis</h4>
                    
                    {yasGruplari.length === 0 ? (
                      <div style={{color: '#d32f2f'}}>⚠️ Lütfen önce yaş grubu seçiniz.</div>
                    ) : (
                      <div style={{marginTop: '1rem'}}>
                        {yasGruplari.map(grup => (
                          <div key={grup} style={{marginBottom: '1rem', padding: '0.5rem', borderBottom: '1px solid #ddd'}}>
                            <div style={{fontWeight: 'bold', marginBottom: '0.5rem'}}>{yasGrupLabel(grup, hayvanTipi)}</div>
                            
                            <div className={styles.inputGroup}>
                              <label>Ayrılan Alan (m²):</label>
                              <DebouncedInput
                                type="number"
                                min="0"
                                value={serbestSistemAlanlari.yariAcik[grup] || ''}
                                onChange={(val) => setSerbestSistemAlanlari({
                                  ...serbestSistemAlanlari,
                                  yariAcik: {...serbestSistemAlanlari.yariAcik, [grup]: parseFloat(val) || 0}
                                })}
                              />
                              <small>Hayvan başına {KUCUKBAS_KAPALI_ALAN[grup]}m² gereklidir.</small>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    <div style={{marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #ddd'}}>
                      <div className={styles.inputGroup}>
                        <label style={{fontWeight: 'bold'}}>Açık Alan / Gölgelik Alanı (m²) [Opsiyonel]:</label>
                        <DebouncedInput
                          type="number"
                          min="0"
                          value={golgelikAlanlari.yariAcik || ''}
                          onChange={(val) => setGolgelikAlanlari({
                            ...golgelikAlanlari,
                            yariAcik: parseFloat(val) || 0
                          })}
                        />
                        <small>Kapalı alan dışındaki gölgelikli alanlar (0.8m²/baş)</small>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : null}

            {/* Hesapla Butonu */}
            <button
              className={styles.calculateButton}
              onClick={hesapla}
              disabled={hesaplaButtonDisabled()}
            >
              {hesaplaButtonDisabled() ? '⚠️ Lütfen Tüm Bilgileri Girin' : '🧮 Kapasiteyi Hesapla'}
            </button>
          </div>

          {/* Sonuçlar */}
          {sonuc && (
            <div className={styles.resultSection}>
              <h3>📊 Hesaplama Sonuçları</h3>
              
              <div className={styles.resultGrid}>
                <div className={styles.resultCard}>
                  <h4>🐄 Toplam Kapasite</h4>
                  <div className={styles.resultItem}>
                    <span>Toplam Hayvan Sayısı:</span>
                    <strong style={{fontSize: '1.5rem', color: '#4caf50'}}>{sonuc.maksimumHayvanSayisi} baş</strong>
                  </div>
                    {sonuc.kullanilabilirAlanM2 > 0 ? (
                      <div className={styles.resultItem}>
                        <span>Toplam Hesaplamaya Esas Alan:</span>
                        <strong>{sonuc.kullanilabilirAlanM2.toFixed(2)} m²</strong>
                      </div>
                    ) : null}
                </div>

                {sonuc.tesisDetaylari && Object.entries(sonuc.tesisDetaylari).map(([tesisTipi, detay]) => (
                  <div key={tesisTipi} className={styles.resultCard}>
                    <h4>
                      {tesisTipi === 'kapali' && '🏠'} 
                      {tesisTipi === 'yariAcik' && '🏚️'}
                      {tesisTipi === 'acik' && '🌳'}
                      {' '}
                      {tesisTipi.charAt(0).toUpperCase() + tesisTipi.slice(1)} Tesis
                    </h4>
                    <div className={styles.resultItem}>
                      <span>Tesis Toplamı:</span>
                      <strong>{detay.hayvanSayisi} baş</strong>
                    </div>
                    {detay.alan > 0 ? (
                      <div className={styles.resultItem}>
                        <span>Hesaplamaya Esas Alan:</span>
                        <strong>{detay.alan.toFixed(2)} m²</strong>
                      </div>
                    ) : null}
                    
                    {Object.entries(detay.yasGrupDagilimi).map(([grup, grupDetay]) => (
                      <div key={grup} style={{marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid #e0e0e0'}}>
                        <div style={{fontWeight: 'bold', marginBottom: '0.25rem'}}>
                          {yasGrupLabel(grup, hayvanTipi)} (%{grupDetay.yuzde})
                        </div>
                        <div style={{fontSize: '0.9rem', color: '#666'}}>
                          {grupDetay.aciklama
                            ? grupDetay.aciklama
                            : `${grupDetay.hayvanSayisi} baş × ${grupDetay.hayvanBasinaAlan.toFixed(2)}m² = ${grupDetay.toplamAlan.toFixed(2)}m²`}
                        </div>
                      </div>
                    ))}
                  </div>
                ))}
              </div>

              <div className={styles.detailsSection}>
                <h4>📝 Hesaplama Detayları</h4>
                <pre style={{whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '0.85rem', background: '#f5f5f5', padding: '1rem', borderRadius: '8px', lineHeight: '1.6'}}>
                  {sonuc.detaylar.join('\n')}
                </pre>
              </div>
            </div>
          )}
        </div>

        <footer style={{textAlign: 'center', marginTop: '2rem', padding: '1rem', background: '#f8f9fa', borderTop: '1px solid #dee2e6'}}>
          <Link
            href="/"
            style={{
              display: 'inline-block',
              background: 'linear-gradient(90deg, rgb(210, 105, 30), rgb(139, 69, 19))',
              color: 'rgb(255, 255, 255)',
              padding: '0.75rem 2.5rem',
              borderRadius: '8px',
              fontWeight: 700,
              fontSize: '1.1rem',
              textDecoration: 'none',
              boxShadow: 'rgba(139, 69, 19, 0.08) 0px 2px 8px',
              transition: 'background 0.2s',
            }}
          >
            Ana Sayfaya Dön
          </Link>
        </footer>
      </Layout>
    </>
  );
}
