import Head from 'next/head';
import Seo from '../components/Seo';
import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import DebouncedInput from '../components/DebouncedInput';
import CalculationFeedbackAccordion from '../components/CalculationFeedbackAccordion';
import { useGA4 } from '../lib/useGA4';
import styles from '../styles/GubreCukuru.module.css';

// Hayvan türleri ve gübre miktarları
const hayvanTurleri = [
  {
    id: 'sut_inegi_6000',
    ad: 'Süt ineği (6000 L/yıl süt veren)',
    kati_gubre: 0.28,
    sivi_gubre: 0.04,
    bulamac: 0.33,
    hafta: 26
  },
  {
    id: 'sut_inegi_3000',
    ad: 'Süt ineği (3000 L/yıl süt veren)',
    kati_gubre: 0.25,
    sivi_gubre: 0.03,
    bulamac: 0.29,
    hafta: 26
  },
  {
    id: 'sigir_2_yas',
    ad: 'Sığır >2 yaş',
    kati_gubre: 0.23,
    sivi_gubre: 0.02,
    bulamac: 0.26,
    hafta: 26
  },
  {
    id: 'sigir_18_24',
    ad: 'Sığır (18-24 aylık)',
    kati_gubre: 0.23,
    sivi_gubre: 0.02,
    bulamac: 0.26,
    hafta: 26
  },
  {
    id: 'sigir_12_18',
    ad: 'Sığır (12-18 aylık)',
    kati_gubre: 0.13,
    sivi_gubre: 0.01,
    bulamac: 0.15,
    hafta: 26
  },
  {
    id: 'sigir_6_12',
    ad: 'Sığır (6-12 aylık)',
    kati_gubre: 0.13,
    sivi_gubre: 0.01,
    bulamac: 0.15,
    hafta: 26
  },
  {
    id: 'sigir_0_6',
    ad: 'Sığır (0-6 aylık)',
    kati_gubre: 0.07,
    sivi_gubre: 0.01,
    bulamac: 0.08,
    hafta: 26
  },
  {
    id: 'keci',
    ad: 'Keçi',
    kati_gubre: 0,
    sivi_gubre: 0,
    bulamac: 0.02,
    hafta: 26
  },
  {
    id: 'koyun',
    ad: 'Koyun',
    kati_gubre: 0,
    sivi_gubre: 0,
    bulamac: 0.03,
    hafta: 26
  },
  {
    id: 'kuzu',
    ad: 'Kuzu-son',
    kati_gubre: 0,
    sivi_gubre: 0,
    bulamac: 0.01,
    hafta: 26
  },
  {
    id: 'kumes_etci',
    ad: 'Kümes hayvanları-1000 adet (%30 Kuru Madde) Etçi',
    kati_gubre: 0,
    sivi_gubre: 0,
    bulamac: 0.28,
    hafta: 26
  },
  {
    id: 'kumes_yumurta',
    ad: 'Kümes hayvanları-1000 adet (%30 Kuru Madde) Yumurta Tavuğu',
    kati_gubre: 0,
    sivi_gubre: 0,
    bulamac: 0.81,
    hafta: 26
  }
];

interface HayvanAdedi {
  [key: string]: number;
}

interface DepoAlanlari {
  kati: number;
  sivi: number;
  bulamac: number;
}

interface DepoTipleri {
  kati: 'kapali' | 'acik';
  sivi: 'kapali' | 'acik';
  bulamac: 'kapali' | 'acik';
}

interface DepoYukseklikleri {
  kati: number;
  sivi: number;
  bulamac: number;
}

interface DepoAktiflik {
  kati: boolean;
  sivi: boolean;
  bulamac: boolean;
}

interface Sonuclar {
  kati_toplam: number;
  sivi_toplam: number;
  bulamac_toplam: number;
  kati_gerekli_alan: number;
  sivi_gerekli_alan: number;
  bulamac_gerekli_alan: number;
  kati_kapasite: number;
  sivi_kapasite: number;
  bulamac_kapasite: number;
}

export default function GubreCukuruHesaplamaPage() {
  const ga4 = useGA4();
  const [hayvanAdedleri, setHayvanAdedleri] = useState<HayvanAdedi>({});
  const [depoAlanlari, setDepoAlanlari] = useState<DepoAlanlari>({
    kati: 0,
    sivi: 0,
    bulamac: 0
  });
  const [depoTipleri, setDepoTipleri] = useState<DepoTipleri>({
    kati: 'kapali',
    sivi: 'kapali',
    bulamac: 'kapali'
  });
  const [depoYukseklikleri, setDepoYukseklikleri] = useState<DepoYukseklikleri>({
    kati: 3,
    sivi: 3,
    bulamac: 3
  });
  const [depoAktiflik, setDepoAktiflik] = useState<DepoAktiflik>({
    kati: false,
    sivi: false,
    bulamac: false
  });
  const [sonuclar, setSonuclar] = useState<Sonuclar | null>(null);
  const [aktifDepoTurleri, setAktifDepoTurleri] = useState<string[]>([]);
  const [uyariMesaji, setUyariMesaji] = useState<string>('');
  const [acikDetaylar, setAcikDetaylar] = useState<Record<string, boolean>>({});

  const trackPublicCalculation = () => {
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || '/api';

    fetch(`${apiBaseUrl}/calculations/public-track/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        event_type: 'calculation',
        calculation_type: 'gubre_cukuru',
        calculation_data: {
          total_hayvan_sayisi: Object.values(hayvanAdedleri).reduce((total, count) => total + (count || 0), 0),
          aktif_depo_sayisi: Object.values(depoAktiflik).filter(Boolean).length,
        },
      }),
    }).catch(() => {
      // İstatistik logu başarısızsa hesaplama akışı etkilenmesin
    });
  };

  // Sadece bulamaç hesaplanan hayvan türleri
  const sadeceBulamacHayvanlari = ['keci', 'koyun', 'kuzu', 'kumes_etci', 'kumes_yumurta'];

  const handleHayvanAdetiChange = (hayvanId: string, adet: number) => {
    setHayvanAdedleri(prev => ({
      ...prev,
      [hayvanId]: adet
    }));
  };

  const handleDepoAktiflikChange = (depoTuru: keyof DepoAktiflik, aktif: boolean) => {
    setDepoAktiflik(prev => ({
      ...prev,
      [depoTuru]: aktif
    }));
    
    // Eğer depo kapatılıyorsa alanını sıfırla
    if (!aktif) {
      setDepoAlanlari(prev => ({
        ...prev,
        [depoTuru]: 0
      }));
    }
  };

  const handleDepoAlaniChange = (depoTuru: keyof DepoAlanlari, alan: number) => {
    setDepoAlanlari(prev => ({
      ...prev,
      [depoTuru]: alan
    }));
  };

  const handleDepoTipiChange = (depoTuru: keyof DepoTipleri, tip: 'kapali' | 'acik') => {
    setDepoTipleri(prev => ({
      ...prev,
      [depoTuru]: tip
    }));
  };

  const handleDepoYuksekligiChange = (depoTuru: keyof DepoYukseklikleri, yukseklik: number) => {
    setDepoYukseklikleri(prev => ({
      ...prev,
      [depoTuru]: yukseklik
    }));
  };

  const hesapla = () => {
    // GA4: Hesaplama başlatma event'i
    ga4.trackCalculationStart('gubre_cukuru');

    const startTime = Date.now();

    // Sadece bulamaç hesaplanan hayvanların kontrolü
    const sadeceBulamacHayvanSecildi = sadeceBulamacHayvanlari.some(hayvanId => 
      (hayvanAdedleri[hayvanId] || 0) > 0
    );

    // Uyarı kontrolü
    if (sadeceBulamacHayvanSecildi && (depoAktiflik.kati || depoAktiflik.sivi)) {
      const uyari = '⚠️ Uyarı: Keçi, koyun, kuzu-son ve kümes hayvanları için sadece bulamaç miktarı hesaplanır. Katı ve sıvı gübre depoları otomatik olarak devre dışı bırakıldı.';
      setUyariMesaji(uyari);
      
      // Katı ve sıvı depoları devre dışı bırak
      setDepoAktiflik(prev => ({
        ...prev,
        kati: false,
        sivi: false
      }));
    } else {
      setUyariMesaji('');
    }

    let kati_toplam = 0;
    let sivi_toplam = 0;
    let bulamac_toplam = 0;

    // Hayvan türlerine göre gübre hesaplama
    hayvanTurleri.forEach(hayvan => {
      const adet = hayvanAdedleri[hayvan.id] || 0;
      if (adet > 0) {
        kati_toplam += adet * hayvan.kati_gubre * hayvan.hafta;
        sivi_toplam += adet * hayvan.sivi_gubre * hayvan.hafta;
        bulamac_toplam += adet * hayvan.bulamac * hayvan.hafta;
      }
    });

    // Duvar yüksekliği hesaplama (açık ise 0.3m, kapalı ise 0.2m duvar yüksekliği eklenir)
    const duvar_yuksekligi_kati = depoTipleri.kati === 'kapali' ? 0.2 : 0.3;
    const duvar_yuksekligi_sivi = depoTipleri.sivi === 'kapali' ? 0.2 : 0.3;
    const duvar_yuksekligi_bulamac = depoTipleri.bulamac === 'kapali' ? 0.2 : 0.3;

    // Yıkama suyu hesaplama (sıvı gübre ve bulamaç için %1)
    const yikama_suyu_sivi = sivi_toplam * 0.01;
    const yikama_suyu_bulamac = bulamac_toplam * 0.01;

    // Gerekli toplam hacim hesaplama (gübre + yıkama suyu, duvar yüksekliği dahil edilmez)
    const kati_gerekli_hacim = kati_toplam;
    const sivi_gerekli_hacim = sivi_toplam + yikama_suyu_sivi;
    const bulamac_gerekli_hacim = bulamac_toplam + yikama_suyu_bulamac;

    // Gerekli alan hesaplama (hacim / yükseklik)
    const kati_gerekli_alan = depoAktiflik.kati ? kati_gerekli_hacim / depoYukseklikleri.kati : 0;
    const sivi_gerekli_alan = depoAktiflik.sivi ? sivi_gerekli_hacim / depoYukseklikleri.sivi : 0;
    const bulamac_gerekli_alan = depoAktiflik.bulamac ? bulamac_gerekli_hacim / depoYukseklikleri.bulamac : 0;

    // Mevcut depo kapasitesi (sadece kullanıcının belirlediği alan varsa)
    const kati_kapasite = depoAktiflik.kati ? kati_gerekli_hacim : 0;
    const sivi_kapasite = depoAktiflik.sivi ? sivi_gerekli_hacim : 0;
    const bulamac_kapasite = depoAktiflik.bulamac ? bulamac_gerekli_hacim : 0;

    // Alan otomatik hesaplama
    setDepoAlanlari({
      kati: kati_gerekli_alan,
      sivi: sivi_gerekli_alan,
      bulamac: bulamac_gerekli_alan
    });

    setSonuclar({
      kati_toplam,
      sivi_toplam,
      bulamac_toplam,
      kati_gerekli_alan,
      sivi_gerekli_alan,
      bulamac_gerekli_alan,
      kati_kapasite,
      sivi_kapasite,
      bulamac_kapasite
    });

    // GA4: Hesaplama tamamlama event'i
    const duration = Date.now() - startTime;
    ga4.trackCalculationComplete('gubre_cukuru', true, duration);

    // Ana sayfa istatistik bileşeni için event kaydı
    trackPublicCalculation();
  };

  const renderDepoGorseli = () => {
    if (!sonuclar) return null;

    // Önce hayvan sayısı kontrolü
    const toplamHayvanSayisi = Object.values(hayvanAdedleri).reduce((toplam, adet) => toplam + (adet || 0), 0);
    if (toplamHayvanSayisi === 0) {
      return (
        <div className={styles.depoGorseli}>
          <h3>🏗️ Depo Görselleştirmesi</h3>
          <div className={styles.depoBosMesaj}>
            <p>🐄 Hesaplama yapmak için en az bir hayvan türü için adet girin</p>
          </div>
        </div>
      );
    }

    const aktifDepolar = [];
    if (depoAktiflik.kati && depoAlanlari.kati > 0) aktifDepolar.push('kati');
    if (depoAktiflik.sivi && depoAlanlari.sivi > 0) aktifDepolar.push('sivi');
    if (depoAktiflik.bulamac && depoAlanlari.bulamac > 0) aktifDepolar.push('bulamac');

    if (aktifDepolar.length === 0) {
      return (
        <div className={styles.depoGorseli}>
          <h3>🏗️ Depo Görselleştirmesi</h3>
          <div className={styles.depoBosMesaj}>
            <p>🚧 Hesaplama yapmak için en az bir depo türünü aktifleştirin</p>
          </div>
        </div>
      );
    }

    return (
      <div className={styles.depoGorseli}>
        <h3>🏗️ 3D Depo Görselleştirmesi</h3>
        
        {/* 3D Sahnesi */}
        <div className={styles.gorsellestirmeContainer}>
          {aktifDepolar.map((depoTuru, index) => {
            const kapasite = sonuclar[`${depoTuru}_kapasite` as keyof Sonuclar] as number;
            const alan = depoAlanlari[depoTuru as keyof DepoAlanlari];
            const yukseklik = depoYukseklikleri[depoTuru as keyof DepoYukseklikleri];
            const tip = depoTipleri[depoTuru as keyof DepoTipleri];
            
            // Depo boyutlarını dinamik ve orantılı hesapla
            const kenarUzunlugu = Math.sqrt(alan);
            
            // Orantılı 3D görselleştirme için pixel hesaplama
            // Referans: 1 metre = 10 pixel olsun
            const pixelPerMeter = 10;
            const cubeWidth = Math.max(50, Math.min(150, kenarUzunlugu * pixelPerMeter));
            const cubeHeight = Math.max(40, Math.min(180, yukseklik * pixelPerMeter));
            const cubeDepth = cubeWidth; // Kare taban
            
            // CSS custom properties ile dinamik boyutlar
            const cubeStyle = {
              '--cube-width': `${cubeWidth}px`,
              '--cube-height': `${cubeHeight}px`,
              '--cube-depth': `${cubeDepth}px`,
            } as React.CSSProperties;

            let depoRenk = 'kati';
            let simge = '🟫';
            if (depoTuru === 'sivi') {
              depoRenk = 'sivi';
              simge = '💧';
            }
            if (depoTuru === 'bulamac') {
              depoRenk = 'bulamac';
              simge = '🌿';
            }

            const kapasiteYuvarlanmis = Math.round(kapasite);
            const depoBaslik = depoTuru.charAt(0).toUpperCase() + depoTuru.slice(1);

            const acik = !!acikDetaylar[depoTuru];

            const toggleDetay = () => {
              setAcikDetaylar(prev => ({ ...prev, [depoTuru]: !acik }));
            };

            return (
              <div key={depoTuru} className={`${styles.depoWrapper} ${acik ? styles.open : ''}`}>
                {/* Tip rozeti (her zaman görünür) */}
                <button
                  type="button"
                  className={styles.depoBadge}
                  onClick={toggleDetay}
                  aria-expanded={acik}
                  aria-controls={`depo-panel-${depoTuru}`}
                  title={`${depoBaslik} detaylarını ${acik ? 'kapat' : 'aç'}`}
                >
                  <span className={styles.depoIcon} aria-hidden="true">{simge}</span>
                  <span className={styles.depoBadgeText}>{depoBaslik}</span>
                </button>

                <div className={`${styles.depo3D} ${styles.depoOrantili}`} style={cubeStyle} aria-hidden="true">
                  <div className={`${styles.depo3DFace} ${styles[depoRenk]} ${styles.front}`}></div>
                  <div className={`${styles.depo3DFace} ${styles[depoRenk]} ${styles.back}`}></div>
                  <div className={`${styles.depo3DFace} ${styles[depoRenk]} ${styles.right}`}></div>
                  <div className={`${styles.depo3DFace} ${styles[depoRenk]} ${styles.left}`}></div>
                </div>

                <div
                  id={`depo-panel-${depoTuru}`}
                  className={styles.depoDetails}
                  role="region"
                  aria-label={`${depoBaslik} depo hesaplama değerleri`}
                >
                  <div className={styles.depoDetailsGrid}>
                    <div className={styles.detRow}>
                      <span className={styles.detLabel}>Boyut</span>
                      <span className={styles.detValue}>{kenarUzunlugu.toFixed(1)}×{kenarUzunlugu.toFixed(1)}×{yukseklik} m</span>
                    </div>
                    <div className={styles.detRow}>
                      <span className={styles.detLabel}>Alan</span>
                      <span className={styles.detValue}>{alan.toFixed(1)} m²</span>
                    </div>
                    <div className={styles.detRow}>
                      <span className={styles.detLabel}>Hacim</span>
                      <span className={styles.detValue}>{kapasiteYuvarlanmis} m³</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        
        {/* Depo Detayları */}
        <div className={styles.depoDetayContainer}>
          {aktifDepolar.map((depoTuru, index) => {
            const kapasite = sonuclar[`${depoTuru}_kapasite` as keyof Sonuclar] as number;
            const alan = depoAlanlari[depoTuru as keyof DepoAlanlari];
            const yukseklik = depoYukseklikleri[depoTuru as keyof DepoYukseklikleri];
            const tip = depoTipleri[depoTuru as keyof DepoTipleri];
            const kenarUzunlugu = Math.sqrt(alan);
            const duvarYuksekligi = tip === 'kapali' ? 0.2 : 0.3;
            
            let simge = '🟫';
            if (depoTuru === 'sivi') simge = '💧';
            if (depoTuru === 'bulamac') simge = '🌿';

            return (
              <div key={depoTuru} className={styles.depoDetayKart}>
                <h4>{simge} {depoTuru.charAt(0).toUpperCase() + depoTuru.slice(1)} Gübre Deposu</h4>
                
                <div className={styles.depoDetayGrid}>
                  <div className={styles.detayItem}>
                    <span className={styles.detayIcon}>📏</span>
                    <span className={styles.detayBaslik}>Boyutlar</span>
                    <span className={styles.detayDeger}>{kenarUzunlugu.toFixed(1)} × {kenarUzunlugu.toFixed(1)} × {yukseklik} m</span>
                  </div>
                  
                  <div className={styles.detayItem}>
                    <span className={styles.detayIcon}>📐</span>
                    <span className={styles.detayBaslik}>Taban Alanı</span>
                    <span className={styles.detayDeger}>{alan.toFixed(1)} m²</span>
                  </div>
                  
                  <div className={styles.detayItem}>
                    <span className={styles.detayIcon}>📊</span>
                    <span className={styles.detayBaslik}>Hacim</span>
                    <span className={styles.detayDeger}>{kapasite.toFixed(1)} m³</span>
                  </div>
                  
                  <div className={styles.detayItem}>
                    <span className={styles.detayIcon}>{tip === 'kapali' ? '🏠' : '🌤️'}</span>
                    <span className={styles.detayBaslik}>Depo Tipi</span>
                    <span className={styles.detayDeger}>{tip === 'kapali' ? 'Kapalı' : 'Açık'}</span>
                  </div>
                  
                  <div className={styles.detayItem}>
                    <span className={styles.detayIcon}>🧱</span>
                    <span className={styles.detayBaslik}>Hava Payı</span>
                    <span className={styles.detayDeger}>{duvarYuksekligi} m</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <>
      <Seo
        title="Gübre Çukuru Kapasite Hesaplama - Tarım Bakanlığı Mevzuatına Uygun"
        description="Tarım Bakanlığı mevzuatına uygun gübre çukuru kapasite hesaplama sistemi"
        canonical="https://tarimimar.com.tr/gubre-cukuru-hesaplama/"
        url="https://tarimimar.com.tr/gubre-cukuru-hesaplama/"
        ogImage="https://tarimimar.com.tr/og-image.svg"
        type="website"
        keywords="gübre çukuru, hayvan gübresi, kapasite hesaplama, tarım mevzuatı, 3D görselleştirme, hayvan barınağı, çiftlik planlama"
      />
      <Layout>
        <div className={styles.container}>
          <div className={styles.header}>
            <h1>🐄 Gübre Çukuru Kapasite Hesaplama</h1>
            <p>Tarım Bakanlığı Mevzuatına Uygun Hesaplama Sistemi</p>
          </div>

          <CalculationFeedbackAccordion calculationType="gubre_cukuru" />

          <div className={styles.content}>
            {/* Hayvan Adetleri Girişi */}
            <section className={styles.section}>
              <h2>🐄 Hayvan Adedleri</h2>
              <div className={styles.hayvanGrid}>
                {hayvanTurleri.map(hayvan => (
                  <div key={hayvan.id} className={styles.hayvanItem}>
                    <label className={styles.hayvanLabel}>
                      {hayvan.ad}
                      {sadeceBulamacHayvanlari.includes(hayvan.id) && (
                        <span className={styles.bulamacBilgi} title="Bu hayvan türü için sadece bulamaç miktarı hesaplanır"> 🌿</span>
                      )}
                    </label>
                    <DebouncedInput
                      type="number"
                      min="0"
                      value={hayvanAdedleri[hayvan.id] || ''}
                      onChange={(val) => handleHayvanAdetiChange(hayvan.id, parseInt(val) || 0)}
                      className={styles.numberInput}
                      placeholder="Adet"
                    />
                  </div>
                ))}
              </div>
            </section>

            {/* Depo Alanları */}
            <section className={styles.section}>
              <h2>🏗️ Depo Alanları ve Özellikleri</h2>
              
              <div className={styles.depoGrid}>
                <div className={`${styles.depoKart} ${!depoAktiflik.kati ? styles.depoKartPasif : ''}`}>
                  <div className={styles.depoBaslik}>
                    <h3>Katı Gübre Deposu</h3>
                    <button
                      type="button"
                      onClick={() => handleDepoAktiflikChange('kati', !depoAktiflik.kati)}
                      className={`${styles.depoToggleBtn} ${depoAktiflik.kati ? styles.aktif : styles.pasif}`}
                    >
                      {depoAktiflik.kati ? '✅ Aktif' : '👆 Tıklayın'}
                    </button>
                  </div>
                  
                  {depoAktiflik.kati && (
                    <>
                      <div className={styles.inputGroup}>
                        <label>Depo Tipi</label>
                        <div className={styles.radioGroup}>
                          <label>
                            <input
                              type="radio"
                              value="kapali"
                              checked={depoTipleri.kati === 'kapali'}
                              onChange={(e) => handleDepoTipiChange('kati', 'kapali')}
                            />
                            🏠 Kapalı (Hava payı: 0.2m)
                          </label>
                          <label>
                            <input
                              type="radio"
                              value="acik"
                              checked={depoTipleri.kati === 'acik'}
                              onChange={(e) => handleDepoTipiChange('kati', 'acik')}
                            />
                            🌤️ Açık (Hava payı: 0.3m)
                          </label>
                        </div>
                      </div>
                      
                      <div className={styles.inputGroup}>
                        <label>Depo Yüksekliği (m)</label>
                        <DebouncedInput
                          type="number"
                          min="2"
                          max="6"
                          step="0.1"
                          value={depoYukseklikleri.kati}
                          onChange={(val) => handleDepoYuksekligiChange('kati', parseFloat(val) || 3)}
                          className={styles.numberInput}
                        />
                        <small className={styles.helpText}>Sistem gerekli alanı otomatik hesaplayacak</small>
                      </div>
                    </>
                  )}
                </div>

                <div className={`${styles.depoKart} ${!depoAktiflik.sivi ? styles.depoKartPasif : ''}`}>
                  <div className={styles.depoBaslik}>
                    <h3>Sıvı Gübre Deposu</h3>
                    <button
                      type="button"
                      onClick={() => handleDepoAktiflikChange('sivi', !depoAktiflik.sivi)}
                      className={`${styles.depoToggleBtn} ${depoAktiflik.sivi ? styles.aktif : styles.pasif}`}
                    >
                      {depoAktiflik.sivi ? '✅ Aktif' : '👆 Tıklayın'}
                    </button>
                  </div>
                  
                  {depoAktiflik.sivi && (
                    <>
                      <div className={styles.inputGroup}>
                        <label>Depo Tipi</label>
                        <div className={styles.radioGroup}>
                          <label>
                            <input
                              type="radio"
                              value="kapali"
                              checked={depoTipleri.sivi === 'kapali'}
                              onChange={(e) => handleDepoTipiChange('sivi', 'kapali')}
                            />
                            🏠 Kapalı (Hava payı: 0.2m)
                          </label>
                          <label>
                            <input
                              type="radio"
                              value="acik"
                              checked={depoTipleri.sivi === 'acik'}
                              onChange={(e) => handleDepoTipiChange('sivi', 'acik')}
                            />
                            🌤️ Açık (Hava payı: 0.3m)
                          </label>
                        </div>
                      </div>
                      
                      <div className={styles.inputGroup}>
                        <label>Depo Yüksekliği (m)</label>
                        <DebouncedInput
                          type="number"
                          min="2"
                          max="6"
                          step="0.1"
                          value={depoYukseklikleri.sivi}
                          onChange={(val) => handleDepoYuksekligiChange('sivi', parseFloat(val) || 3)}
                          className={styles.numberInput}
                        />
                        <small className={styles.helpText}>Sistem gerekli alanı otomatik hesaplayacak</small>
                      </div>
                    </>
                  )}
                </div>

                <div className={`${styles.depoKart} ${!depoAktiflik.bulamac ? styles.depoKartPasif : ''}`}>
                  <div className={styles.depoBaslik}>
                    <h3>Bulamaç Deposu</h3>
                    <button
                      type="button"
                      onClick={() => handleDepoAktiflikChange('bulamac', !depoAktiflik.bulamac)}
                      className={`${styles.depoToggleBtn} ${depoAktiflik.bulamac ? styles.aktif : styles.pasif}`}
                    >
                      {depoAktiflik.bulamac ? '✅ Aktif' : '👆 Tıklayın'}
                    </button>
                  </div>
                  
                  {depoAktiflik.bulamac && (
                    <>
                      <div className={styles.inputGroup}>
                        <label>Depo Tipi</label>
                        <div className={styles.radioGroup}>
                          <label>
                            <input
                              type="radio"
                              value="kapali"
                              checked={depoTipleri.bulamac === 'kapali'}
                              onChange={(e) => handleDepoTipiChange('bulamac', 'kapali')}
                            />
                            🏠 Kapalı (Hava payı: 0.2m)
                          </label>
                          <label>
                            <input
                              type="radio"
                              value="acik"
                              checked={depoTipleri.bulamac === 'acik'}
                              onChange={(e) => handleDepoTipiChange('bulamac', 'acik')}
                            />
                            🌤️ Açık (Hava payı: 0.3m)
                          </label>
                        </div>
                      </div>
                      
                      <div className={styles.inputGroup}>
                        <label>Depo Yüksekliği (m)</label>
                        <DebouncedInput
                          type="number"
                          min="2"
                          max="6"
                          step="0.1"
                          value={depoYukseklikleri.bulamac}
                          onChange={(val) => handleDepoYuksekligiChange('bulamac', parseFloat(val) || 3)}
                          className={styles.numberInput}
                        />
                        <small className={styles.helpText}>Sistem gerekli alanı otomatik hesaplayacak</small>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </section>

            {/* Hesaplama Butonu */}
            <section className={styles.section}>
              <div className={styles.hesaplaContainer}>
                <button onClick={hesapla} className={styles.hesaplaButon}>
                  📊 Hesapla
                </button>
              </div>
              
              {/* Uyarı Mesajı */}
              {uyariMesaji && (
                <div className={styles.uyariMesaji}>
                  <div className={styles.uyariIcerik}>
                    <span className={styles.uyariIcon}>⚠️</span>
                    <span>{uyariMesaji}</span>
                  </div>
                </div>
              )}
            </section>

            {/* Sonuçlar */}
            {sonuclar && (
              <section className={styles.section}>
                <h2>📊 Hesaplama Sonuçları</h2>
                
                <div className={styles.sonucGrid}>
                  {depoAktiflik.kati && (
                    <div className={styles.sonucKart}>
                      <h3>🟫 Katı Gübre Deposu</h3>
                      <div className={styles.sonucDetay}>
                        <p>Toplam Gübre Hacmi: <strong>{sonuclar.kati_toplam.toFixed(2)} m³</strong></p>
                        <p>Hava Payı: <strong>{depoTipleri.kati === 'kapali' ? '0.2' : '0.3'} m</strong></p>
                        <p>Toplam Gerekli Hacim: <strong>{sonuclar.kati_kapasite.toFixed(2)} m³</strong></p>
                        <p>Gerekli Alan: <strong>{sonuclar.kati_gerekli_alan.toFixed(2)} m²</strong></p>
                        <p>Depo Boyutları: <strong>{Math.sqrt(sonuclar.kati_gerekli_alan).toFixed(1)}×{Math.sqrt(sonuclar.kati_gerekli_alan).toFixed(1)}×{depoYukseklikleri.kati} m</strong></p>
                      </div>
                    </div>
                  )}

                  {depoAktiflik.sivi && (
                    <div className={styles.sonucKart}>
                      <h3>💧 Sıvı Gübre Deposu</h3>
                      <div className={styles.sonucDetay}>
                        <p>Toplam Gübre Hacmi: <strong>{sonuclar.sivi_toplam.toFixed(2)} m³</strong></p>
                        <p>Yıkama Suyu (%1): <strong>{(sonuclar.sivi_toplam * 0.01).toFixed(2)} m³</strong></p>
                        <p>Hava Payı: <strong>{depoTipleri.sivi === 'kapali' ? '0.2' : '0.3'} m</strong></p>
                        <p>Toplam Gerekli Hacim: <strong>{sonuclar.sivi_kapasite.toFixed(2)} m³</strong></p>
                        <p>Gerekli Alan: <strong>{sonuclar.sivi_gerekli_alan.toFixed(2)} m²</strong></p>
                        <p>Depo Boyutları: <strong>{Math.sqrt(sonuclar.sivi_gerekli_alan).toFixed(1)}×{Math.sqrt(sonuclar.sivi_gerekli_alan).toFixed(1)}×{depoYukseklikleri.sivi} m</strong></p>
                      </div>
                    </div>
                  )}

                  {depoAktiflik.bulamac && (
                    <div className={styles.sonucKart}>
                      <h3>🌿 Bulamaç Deposu</h3>
                      <div className={styles.sonucDetay}>
                        <p>Toplam Gübre Hacmi: <strong>{sonuclar.bulamac_toplam.toFixed(2)} m³</strong></p>
                        <p>Yıkama Suyu (%1): <strong>{(sonuclar.bulamac_toplam * 0.01).toFixed(2)} m³</strong></p>
                        <p>Hava Payı: <strong>{depoTipleri.bulamac === 'kapali' ? '0.2' : '0.3'} m</strong></p>
                        <p>Toplam Gerekli Hacim: <strong>{sonuclar.bulamac_kapasite.toFixed(2)} m³</strong></p>
                        <p>Gerekli Alan: <strong>{sonuclar.bulamac_gerekli_alan.toFixed(2)} m²</strong></p>
                        <p>Depo Boyutları: <strong>{Math.sqrt(sonuclar.bulamac_gerekli_alan).toFixed(1)}×{Math.sqrt(sonuclar.bulamac_gerekli_alan).toFixed(1)}×{depoYukseklikleri.bulamac} m</strong></p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Depo Görselleştirmesi */}
                {renderDepoGorseli()}
              </section>
            )}

            {/* Bilgilendirme Notları */}
            <section className={styles.section}>
              <h2>ℹ️ Önemli Notlar</h2>
              <div className={styles.bilgiNotlari}>
                <ul>
                  <li>Kapalı dönem hafta sayısı 26 hafta olarak hesaplanmıştır</li>
                  <li>Hava payı: Kapalı depolar için 0.2m, açık depolar için 0.3m eklenir</li>
                  <li>Yıkama suyu: Sıvı gübre ve bulamaç için toplam hacmin %1'i</li>
                  <li>Depo yüksekliği 2-6 metre arasında seçilebilir</li>
                  <li>Sistem gerekli alan büyüklüğünü otomatik olarak hesaplar</li>
                  <li><strong>🌿 Keçi, koyun, kuzu-son ve kümes hayvanları için sadece bulamaç miktarı hesaplanır</strong></li>
                  <li>Hesaplamalar Tarım Bakanlığı mevzuatına uygun olarak yapılmıştır</li>
                </ul>
              </div>
            </section>

            {/* Ana sayfaya dönüş butonu */}
            <div style={{ textAlign: 'center', marginTop: 48 }}>
              <a href="/" style={{
                display: 'inline-block',
                background: 'linear-gradient(90deg, #d2691e, #8b4513)',
                color: '#fff',
                padding: '0.75rem 2.5rem',
                borderRadius: 8,
                fontWeight: 700,
                fontSize: '1.1rem',
                textDecoration: 'none',
                boxShadow: '0 2px 8px rgba(139,69,19,0.08)',
                transition: 'background 0.2s',
              }}
                onMouseOver={e => (e.currentTarget.style.background = 'linear-gradient(90deg, #8b4513, #d2691e)')}
                onMouseOut={e => (e.currentTarget.style.background = 'linear-gradient(90deg, #d2691e, #8b4513)')}
              >
                Ana Sayfaya Dön
              </a>
            </div>
          </div>
        </div>
      </Layout>
    </>
  );
}
