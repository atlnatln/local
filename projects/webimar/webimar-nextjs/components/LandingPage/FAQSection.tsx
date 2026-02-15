import React, { useState } from 'react';
import styles from '../../styles/HomePage.module.css';

interface FAQItem {
  question: string;
  answer: string;
}

const faqs: FAQItem[] = [
  {
    question: "Tarım arazisine ev yapılabilir mi?",
    answer: "Tarım arazilerine yapılaşma izni, 5403 sayılı Toprak Koruma ve Arazi Kullanımı Kanunu'na tabidir. Bağ evi gibi yapılar için belirli bir parsel 'büyüklüğü (genellikle 5.000 m²) ve yola cephe şartı aranmaktadır. Sistemimiz, parselinizin bu şartları sağlayıp sağlamadığını kontrol etmenize yardımcı olur."
  },
  {
    question: "Tarımsal amaçlı yapı izni nasıl alınır?",
    answer: "Tarımsal amaçlı yapılar (ahır, kümes, depo vb.) için İl/İlçe Tarım ve Orman Müdürlüklerinden 'Tarımsal Amaçlı Yapı İzni' alınmalıdır. Bu süreçte gerekli olan avan projeler ve kapasite raporları için hesaplama araçlarımızı kullanabilirsiniz."
  },
  {
    question: "Tarım dışı kullanım izni nedir?",
    answer: "Tarım arazisinin, tarımsal üretim amacı dışında (konut, sanayi, enerji vb.) kullanılması için Bakanlıktan alınan izindir. Bu izin, arazinin sınıfına, büyüklüğüne ve planlanan yatırımın kamu yararı taşıyıp taşımadığına göre değerlendirilir."
  },
  {
    question: "Zecri kıymet takdiri hesaplaması ne işe yarar?",
    answer: "İmar uygulamaları sırasında veya kamulaştırma işlemlerinde, arazinin üzerindeki ağaç, yapı ve diğer varlıkların değerinin belirlenmesi işlemidir. Hesaplaryıcımız, yerel rayiç bedellere ve ağaç yaşlarına göre tahmini bir değer sunar."
  },
   {
    question: "Webimar hesaplamaları resmi geçerlilik taşır mı?",
    answer: "Hayır. Webimar tarafından sunulan hesaplamalar, mevzuat rehberliğinde hazırlanan bilgilendirme amaçlı ön çalışmalardır. Resmi başvurularınızda yetkili kurumların (Tarım Orman Bakanlığı, Belediyeler) görüşleri ve onaylı projeler esastır."
  }
];

export default function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const toggleFAQ = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section className={styles.faqSection}>
      <div className={styles.container}>
        <h2 className={styles.sectionTitle}>Sıkça Sorulan Sorular</h2>
        <div className={styles.faqList}>
          {faqs.map((faq, index) => (
            <div key={index} className={`${styles.faqItem} ${openIndex === index ? styles.active : ''}`}>
              <button 
                className={styles.faqQuestion} 
                onClick={() => toggleFAQ(index)}
                aria-expanded={openIndex === index}
              >
                {faq.question}
                <span className={styles.faqIcon}>{openIndex === index ? '−' : '+'}</span>
              </button>
              <div className={styles.faqAnswer} style={{ maxHeight: openIndex === index ? '500px' : '0' }}>
                <div className={styles.faqAnswerText}>{faq.answer}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
