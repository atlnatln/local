import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import styles from '../styles/CookieBanner.module.css';

interface CookiePreferences {
  necessary: boolean;
  analytics: boolean;
  functional: boolean;
}

const CookieBanner: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [preferences, setPreferences] = useState<CookiePreferences>({
    necessary: true, // Zorunlu çerezler her zaman aktif
    analytics: false,
    functional: false,
  });

  useEffect(() => {
    // Çerez tercihlerini kontrol et
    const savedConsent = localStorage.getItem('cookie_consent');
    if (!savedConsent) {
      // Kullanıcı daha önce tercih yapmamış
      setIsVisible(true);
    } else {
      try {
        const parsedConsent = JSON.parse(savedConsent);
        setPreferences(parsedConsent);
        // Analytics çerezleri etkinleştir
        if (parsedConsent.analytics) {
          enableAnalytics();
        }
      } catch (e) {
        setIsVisible(true);
      }
    }
  }, []);

  const enableAnalytics = () => {
    // Google Analytics'i etkinleştir
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('consent', 'update', {
        analytics_storage: 'granted',
      });
    }
  };

  const disableAnalytics = () => {
    // Google Analytics'i devre dışı bırak
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('consent', 'update', {
        analytics_storage: 'denied',
      });
    }
  };

  const savePreferences = (newPreferences: CookiePreferences) => {
    localStorage.setItem('cookie_consent', JSON.stringify(newPreferences));
    localStorage.setItem('cookie_consent_date', new Date().toISOString());
    
    if (newPreferences.analytics) {
      enableAnalytics();
    } else {
      disableAnalytics();
    }
    
    setIsVisible(false);
  };

  const handleAcceptAll = () => {
    const allAccepted: CookiePreferences = {
      necessary: true,
      analytics: true,
      functional: true,
    };
    setPreferences(allAccepted);
    savePreferences(allAccepted);
  };

  const handleRejectAll = () => {
    const onlyNecessary: CookiePreferences = {
      necessary: true,
      analytics: false,
      functional: false,
    };
    setPreferences(onlyNecessary);
    savePreferences(onlyNecessary);
  };

  const handleSavePreferences = () => {
    savePreferences(preferences);
  };

  const handlePreferenceChange = (key: keyof CookiePreferences) => {
    if (key === 'necessary') return; // Zorunlu çerezler değiştirilemez
    setPreferences(prev => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  if (!isVisible) return null;

  return (
    <div className={styles.overlay}>
      <div className={styles.banner}>
        <div className={styles.content}>
          <div className={styles.header}>
            <span className={styles.icon}>🍪</span>
            <h2>Çerez Kullanımı</h2>
          </div>
          
          <p className={styles.description}>
            Web sitemizde deneyiminizi iyileştirmek için çerezler kullanıyoruz. 
            Zorunlu çerezler sitenin çalışması için gereklidir. Diğer çerezleri 
            tercihlerinize göre yönetebilirsiniz.
          </p>

          {showDetails && (
            <div className={styles.details}>
              <div className={styles.cookieOption}>
                <div className={styles.optionInfo}>
                  <label className={styles.optionLabel}>
                    <input
                      type="checkbox"
                      checked={preferences.necessary}
                      disabled
                      className={styles.checkbox}
                    />
                    <span className={styles.checkmark}></span>
                    <strong>Zorunlu Çerezler</strong>
                  </label>
                  <p>
                    Sitenin temel işlevleri için gereklidir. Bu çerezler olmadan 
                    site düzgün çalışmaz.
                  </p>
                </div>
                <span className={styles.badge}>Her zaman aktif</span>
              </div>

              <div className={styles.cookieOption}>
                <div className={styles.optionInfo}>
                  <label className={styles.optionLabel}>
                    <input
                      type="checkbox"
                      checked={preferences.analytics}
                      onChange={() => handlePreferenceChange('analytics')}
                      className={styles.checkbox}
                    />
                    <span className={styles.checkmark}></span>
                    <strong>Analitik Çerezler</strong>
                  </label>
                  <p>
                    Site kullanımını analiz etmemize yardımcı olur. 
                    Google Analytics kullanılmaktadır.
                  </p>
                </div>
              </div>

              <div className={styles.cookieOption}>
                <div className={styles.optionInfo}>
                  <label className={styles.optionLabel}>
                    <input
                      type="checkbox"
                      checked={preferences.functional}
                      onChange={() => handlePreferenceChange('functional')}
                      className={styles.checkbox}
                    />
                    <span className={styles.checkmark}></span>
                    <strong>İşlevsellik Çerezleri</strong>
                  </label>
                  <p>
                    Tercihlerinizi hatırlar ve kişiselleştirilmiş deneyim sunar.
                  </p>
                </div>
              </div>
            </div>
          )}

          <div className={styles.actions}>
            <div className={styles.primaryActions}>
              <button 
                onClick={handleAcceptAll} 
                className={styles.acceptButton}
              >
                Tümünü Kabul Et
              </button>
              <button 
                onClick={handleRejectAll} 
                className={styles.rejectButton}
              >
                Sadece Zorunlu
              </button>
            </div>
            
            <div className={styles.secondaryActions}>
              {showDetails ? (
                <button 
                  onClick={handleSavePreferences} 
                  className={styles.saveButton}
                >
                  Tercihleri Kaydet
                </button>
              ) : (
                <button 
                  onClick={() => setShowDetails(true)} 
                  className={styles.detailsButton}
                >
                  Tercihleri Yönet
                </button>
              )}
            </div>
          </div>

          <div className={styles.links}>
            <Link href="/cerez-politikasi">Çerez Politikası</Link>
            <span className={styles.separator}>|</span>
            <Link href="/gizlilik-politikasi">Gizlilik Politikası</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CookieBanner;
