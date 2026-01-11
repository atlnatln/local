import React from 'react';
import { checkIzmirBelediyesi5000M2 } from '../utils/izmirBelediyesiKontrol';
import styles from './IzmirBelediyesiUyari.module.css';
import { getNextJsUrl } from '../utils/environment';

interface IzmirBelediyesiUyariProps {
  arazi_alani_m2: number;
  yapiTuru: string;
  koordinatlar?: {
    lat: number;
    lng: number;
  };
  onClose: () => void;
  onContinue: () => void;
}

const IzmirBelediyesiUyari: React.FC<IzmirBelediyesiUyariProps> = ({
  arazi_alani_m2,
  yapiTuru,
  koordinatlar,
  onClose,
  onContinue
}) => {
  // Kontrol sonucunu al
  const uyariSonuc = checkIzmirBelediyesi5000M2(arazi_alani_m2, yapiTuru, koordinatlar);

  // Eğer uyarı gösterilmeyecekse, null döndür
  if (!uyariSonuc.uyariGosterilsinMi) {
    return null;
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        {/* Header */}
        <div className={styles.header}>
          <span className={styles.icon}>🏛️</span>
          <h3 className={styles.title}>İzmir Büyükşehir Belediyesi Uyarısı</h3>
        </div>

        {/* Content */}
        <div className={styles.content}>
          {/* Warning Box */}
          <div className={styles.warningBox}>
            <span className={styles.warningIcon}>⚠️</span>
            <div>
              <h4>Dikkat: Minimum Parsel Büyüklüğü</h4>
              <p>{uyariSonuc.uyariMesaji}</p>
            </div>
          </div>

          {/* Statistics Box */}
          {uyariSonuc.eksikAlan && (
            <div className={styles.statisticsBox}>
              <div className={styles.statItem}>
                <span className={styles.statLabel}>Mevcut Alan</span>
                <span className={styles.statValue}>
                  {arazi_alani_m2.toLocaleString('tr-TR')} m²
                </span>
              </div>
              <div className={styles.statItem}>
                <span className={styles.statLabel}>Eksik Alan</span>
                <span className={styles.statValue}>
                  {uyariSonuc.eksikAlan.toLocaleString('tr-TR')} m²
                </span>
              </div>
              <div className={styles.statItem}>
                <span className={styles.statLabel}>Gerekli Alan</span>
                <span className={styles.statValue}>5.000 m²</span>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className={styles.actionButtons}>
            <button 
              className={styles.secondaryButton}
              onClick={onContinue}
            >
              ⚡ Hesaplamaya Devam Et
            </button>
          </div>

          {/* Detail Box */}
          <div className={styles.detailBox}>
            <h5>📋 İlgili Plan Notu Detayları</h5>
            <h6>Madde 7.12.15.2: Tarımsal Amaçlı Yapılar</h6>
            <div className={styles.planNotuContent}>
              <p className={styles.planNotuLine}>
                <strong>🌾 Mutlak Tarım Arazisi, Dikili Tarım Arazisi ve Özel Ürün Arazileri:</strong>
              </p>
              <p className={styles.planNotuLine}>
                • Minimum parsel cephesi 10 metre ve minimum parsel büyüklüğü 5000 m²
              </p>
              <p className={styles.planNotuLine}>
                • Yollara 10 metre'den, komşu parsel sınırlarına 5 metre'den fazla yaklaşmamak
              </p>
              <p className={styles.planNotuLine}>
                • İnşaat emsali 0.05'i, yüksekliği 2 katı aşmamak
              </p>
              <p className={styles.planNotuLine}>
                • Maksimum yapı inşaat alanı (brüt inşaat alanı) 2000 m²'den fazla olamaz
              </p>
              
              <p className={styles.planNotuLine} style={{marginTop: '15px'}}>
                <strong>🌿 Marjinal Tarım Arazileri:</strong>
              </p>
              <p className={styles.planNotuLine}>
                • Minimum parsel cephesi 10 metre ve minimum parsel büyüklüğü 5000 m²
              </p>
              <p className={styles.planNotuLine}>
                • Yollara 10 metre'den, komşu parsel sınırlarına 5 metre'den fazla yaklaşmamak
              </p>
              <p className={styles.planNotuLine}>
                • Parsellerin 5000 m².lik kısmı için inşaat emsali 0,20'yi aşmamak
              </p>
              <p className={styles.planNotuLine}>
                • Geri kalan parsel alanı için inşaat emsali 0.10'u aşmamak
              </p>
              <p className={styles.planNotuLine}>
                • Yüksekliği 2 katı aşmamak
              </p>
              <p className={styles.planNotuLine}>
                • Maksimum yapı inşaat alanı (brüt inşaat alanı) 10000 m²'den fazla olamaz
              </p>
            </div>

            {/* Contact Info */}
            <div className={styles.contactInfo}>
              <h6>📞 İletişim Bilgileri</h6>
              <div className={styles.contactDetails}>
                <span>📍 İzmir Büyükşehir Belediyesi</span>
                <span>📞 İletişim: 0232 293 46 46</span>
                <span>🌐 Web: www.izmir.bel.tr</span>
                <span>📧 E-posta: bilgi@izmir.bel.tr</span>
                <a 
                  href={`${getNextJsUrl()}/documents/izmir-buyuksehir-plan-notlari/`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{color: '#007bff', textDecoration: 'underline'}}
                >
                  📋 Detaylı Plan Notları
                </a>
              </div>
            </div>
          </div>

          {/* Legal Notice */}
          <div className={styles.legalNotice}>
            <small>
              ⚖️ Bu uyarı İzmir Büyükşehir Belediyesi mevzuatına dayanır. 
              Kesin bilgi için belediye ile iletişime geçiniz.
            </small>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IzmirBelediyesiUyari;
