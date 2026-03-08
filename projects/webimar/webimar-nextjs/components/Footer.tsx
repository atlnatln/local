import React from 'react';
import Link from 'next/link';
import styles from '../styles/Footer.module.css';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className={styles.footer}>
      <div className={styles.footerContent}>
        <div className={styles.footerSection}>
          <h3 className={styles.footerTitle}>🌾 Tarım İmar</h3>
          <p className={styles.footerDescription}>
            Tarımsal arazilerde yapılaşma süreçlerinde güncel mevzuata uygun, 
            güvenilir hesaplama çözümleri sunuyoruz.
          </p>
        </div>

        <div className={styles.footerSection}>
          <h4 className={styles.sectionTitle}>Hızlı Erişim</h4>
          <nav className={styles.footerNav}>
            <Link href="/">Ana Sayfa</Link>
            <Link href="/bag-evi">Bağ Evi</Link>
            <Link href="/sera">Sera</Link>
            <Link href="/aricilik-planlama">Arıcılık Planlama</Link>
          </nav>
        </div>

        <div className={styles.footerSection}>
          <h4 className={styles.sectionTitle}>Hukuki Metinler</h4>
          <nav className={styles.footerNav}>
            <Link href="/gizlilik-politikasi">Gizlilik Politikası</Link>
            <Link href="/kvkk-aydinlatma">KVKK Aydınlatma Metni</Link>
            <Link href="/cerez-politikasi">Çerez Politikası</Link>
            <Link href="/kullanim-kosullari">Kullanım Koşulları</Link>
          </nav>
        </div>

        <div className={styles.footerSection}>
          <h4 className={styles.sectionTitle}>İletişim</h4>
          <nav className={styles.footerNav}>
            <Link href="/iletisim">İletişim Formu</Link>
          </nav>
          <div className={styles.contactInfo}>
            <a href="mailto:info@tarimimar.com.tr">📧 info@tarimimar.com.tr</a>
          </div>
        </div>
      </div>

      <div className={styles.footerBottom}>
        <p>© {currentYear} Tarım İmar. Tüm hakları saklıdır.</p>
        <p className={styles.legalNotice}>
          Bu site 6698 sayılı KVKK ve GDPR kapsamında kişisel verilerin korunması ilkelerine uygun olarak işletilmektedir.
        </p>
      </div>
    </footer>
  );
};

export default Footer;
