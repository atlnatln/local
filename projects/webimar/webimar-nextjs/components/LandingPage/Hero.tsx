import React from 'react';
import styles from './Hero.module.css';

interface HeroProps {
  title: string;
  subtitle: string;
  icon: string;
  backgroundImage?: string;
  ctaLink?: string;
}

const Hero: React.FC<HeroProps> = ({ 
  title, 
  subtitle, 
  icon, 
  backgroundImage,
  ctaLink 
}) => {
  return (
    <div 
      className={styles.hero}
      style={backgroundImage ? { backgroundImage: `url(${backgroundImage})` } : undefined}
    >
      <div className={styles.heroContent}>
        <div className={styles.heroIcon}>{icon}</div>
        <h1 className={styles.heroTitle}>{title}</h1>
        <p className={styles.heroSubtitle}>{subtitle}</p>
        {ctaLink && (
          <a href={
            // Önce development ortamı kontrolü (localhost içeriyorsa)
            process.env.NEXT_PUBLIC_REACT_SPA_URL?.includes('localhost')
              ? `${process.env.NEXT_PUBLIC_REACT_SPA_URL}${ctaLink.replace('/hesaplama', '')}`
              // Sonra production için full URL kontrolü  
              : process.env.NEXT_PUBLIC_REACT_SPA_URL?.startsWith('http')
                ? `${process.env.NEXT_PUBLIC_REACT_SPA_URL}${ctaLink.replace('/hesaplama', '')}`
                // Fallback: production domain + ctaLink
                : `https://tarimimar.com.tr${ctaLink}`
          }>
            <button className={styles.heroCta}>
              Hemen Hesapla
            </button>
          </a>
        )}
      </div>
    </div>
  );
};

export default Hero;
