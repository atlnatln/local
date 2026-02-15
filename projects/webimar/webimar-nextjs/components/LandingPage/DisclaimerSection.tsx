import React from 'react';
import styles from '../../styles/HomePage.module.css';

export default function DisclaimerSection() {
  return (
    <div className={styles.disclaimerBox}>
      <p>
        <strong>⚠️ Yasal Uyarı:</strong> Bu platformda sunulan hesaplama araçları ve bilgiler, 
        kullanıcıları bilgilendirmek amacıyla hazırlanmıştır ve <strong>resmi belge niteliği taşımaz</strong>. 
        Tarımsal yatırımlarınız ve inşaat projeleriniz için nihai kararı vermeden önce mutlaka 
        ilgili resmi kurumlarla (İl/İlçe Tarım Müdürlükleri, Belediyeler) görüşmeniz ve 
        yetkili proje müelliflerinden profesyonel hizmet almanız gerekmektedir. 
        Oluşabilecek maddi/manevi zararlardan platformumuz sorumlu tutulamaz.
      </p>
    </div>
  );
}
