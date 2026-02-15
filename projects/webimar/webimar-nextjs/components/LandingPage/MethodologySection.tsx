import React from 'react';
import styles from '../../styles/HomePage.module.css';

export default function MethodologySection() {
  return (
    <section className={styles.methodologySection}>
      <div className={styles.container}>
        <h2 className={styles.sectionTitle}>Hesaplama Metodolojimiz ve Mevzuat Temeli</h2>
        <div className={styles.methodologyGrid}>
          <div className={styles.methodologyCard}>
            <h3>🔍 Yasal Mevzuat ve Dayanak</h3>
            <p>
              Tüm hesaplamalarımız, <strong>5403 Sayılı Toprak Koruma ve Arazi Kullanımı Kanunu</strong> ve 
              ilgili uygulama yönetmeliklerine tam uyumlu olarak gerçekleştirilmektedir. 
              Verilerimiz Resmi Gazete'de yayımlanan en güncel tebliğler (Örn: Tarımsal Yapıların Tasarım Kriterleri) 
              baz alınarak sürekli revize edilir.
            </p>
          </div>
          <div className={styles.methodologyCard}>
            <h3>📐 Mühendislik Doğruluğu</h3>
            <p>
              Sistemimiz, parsel büyüklüğü, taban alanı katsayısı (TAKS) ve emsal değerlerini 
              otomatik olarak analiz eder. Şehir Plancıları ve Ziraat Mühendisleri tarafından 
              doğrulanmış algoritmalarımız sayesinde, manuel hata payını sıfıra indirmeyi hedefleriz.
            </p>
          </div>
          <div className={styles.methodologyCard}>
            <h3>🔄 Sürekli Güncellenen Veritabanı</h3>
            <p>
              İl Tarım ve Orman Müdürlüklerinin yerel kısıtlamaları ve Bakanlık genelgeleri 
              sistemimize entegre edilir. Böylece sadece genel kanuna değil, yerel uygulama 
              farklılıklarına dair de en doğru ön bilgiyi sunarız.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
