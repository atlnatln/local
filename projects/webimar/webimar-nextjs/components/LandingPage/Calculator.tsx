import React from 'react';
import Link from 'next/link';
import styles from './Calculator.module.css';

interface CalculatorProps {
  title: string;
  description: string;
  ctaText: string;
  ctaLink: string;
}

const Calculator: React.FC<CalculatorProps> = ({ 
  title, 
  description, 
  ctaText, 
  ctaLink 
}) => {
  return (
    <section className={styles.calculator}>
      <div className={styles.container}>
        <div className={styles.calculatorCard}>
          <div className={styles.calculatorIcon}>🔢</div>
          <h2 className={styles.calculatorTitle}>{title}</h2>
          <p className={styles.calculatorDescription}>{description}</p>
          <Link href={ctaLink} className={styles.calculatorCta}>
            {ctaText} →
          </Link>
        </div>
      </div>
    </section>
  );
};

export default Calculator;
