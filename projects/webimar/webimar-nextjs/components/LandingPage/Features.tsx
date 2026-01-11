import React from 'react';
import styles from './Features.module.css';

interface Feature {
  title: string;
  description: string;
  icon: string;
}

interface FeaturesProps {
  features: Feature[];
}

const Features: React.FC<FeaturesProps> = ({ features }) => {
  return (
    <section className={styles.features}>
      <div className={styles.container}>
        <h2 className={styles.sectionTitle}>Özellikler ve Avantajlar</h2>
        <div className={styles.featuresGrid}>
          {features.map((feature, index) => (
            <div key={index} className={styles.featureCard}>
              <div className={styles.featureIcon}>{feature.icon}</div>
              <h3 className={styles.featureTitle}>{feature.title}</h3>
              <p className={styles.featureDescription}>{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
