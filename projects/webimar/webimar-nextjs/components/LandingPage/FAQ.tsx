import React, { useState } from 'react';
import styles from './FAQ.module.css';

interface FaqItem {
  question: string;
  answer: string;
}

interface FAQProps {
  faq: FaqItem[];
}

const FAQ: React.FC<FAQProps> = ({ faq }) => {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggleFaq = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section className={styles.faq}>
      <div className={styles.container}>
        <h2 className={styles.sectionTitle}>Sıkça Sorulan Sorular</h2>
        <div className={styles.faqList}>
          {faq.map((item, index) => (
            <div 
              key={index} 
              className={`${styles.faqItem} ${openIndex === index ? styles.open : ''}`}
            >
              <button 
                className={styles.faqQuestion}
                onClick={() => toggleFaq(index)}
              >
                <span>{item.question}</span>
                <span className={styles.faqIcon}>
                  {openIndex === index ? '−' : '+'}
                </span>
              </button>
              {openIndex === index && (
                <div className={styles.faqAnswer}>
                  <p>{item.answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FAQ;
