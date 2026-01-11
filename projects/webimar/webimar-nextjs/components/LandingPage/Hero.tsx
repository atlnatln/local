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
  const ctaHref = ctaLink
    ? ctaLink.startsWith('http://') || ctaLink.startsWith('https://')
      ? ctaLink
      : ctaLink.startsWith('/')
        ? ctaLink
        : `/${ctaLink}`
    : undefined;

  return (
    <div 
      className={styles.hero}
      style={backgroundImage ? { backgroundImage: `url(${backgroundImage})` } : undefined}
    >
      <div className={styles.heroContent}>
        <div className={styles.heroIcon}>{icon}</div>
        <h1 className={styles.heroTitle}>{title}</h1>
        <p className={styles.heroSubtitle}>{subtitle}</p>
        {ctaHref && (
          <a href={ctaHref}>
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
