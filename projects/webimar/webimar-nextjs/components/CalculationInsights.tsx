import { useEffect, useMemo, useState } from 'react';
import styles from '../styles/HomePage.module.css';

type ProvinceCount = {
  province: string;
  count: number;
  count_7d: number;
  count_28d: number;
};

type InsightsPayload = {
  totals: {
    gubre_cukuru: number;
    havza_bazli_destekleme: number;
    tarimsal_yapi: number;
  };
  tarimsal_yapi_by_province: ProvinceCount[];
  province_count: number;
};

const EMPTY_PAYLOAD: InsightsPayload = {
  totals: {
    gubre_cukuru: 0,
    havza_bazli_destekleme: 0,
    tarimsal_yapi: 0,
  },
  tarimsal_yapi_by_province: [],
  province_count: 0,
};

export default function CalculationInsights() {
  const [insights, setInsights] = useState<InsightsPayload>(EMPTY_PAYLOAD);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [showProvinceBreakdown, setShowProvinceBreakdown] = useState(false);
  const [selectedProvince, setSelectedProvince] = useState<string | null>(null);

  const apiBaseUrl = useMemo(() => {
    const configuredBase = process.env.NEXT_PUBLIC_API_BASE_URL;

    if (configuredBase && configuredBase.startsWith('http')) {
      return configuredBase;
    }

    return configuredBase || '/api';
  }, []);

  useEffect(() => {
    const abortController = new AbortController();

    const loadInsights = async () => {
      try {
        setIsLoading(true);
        setHasError(false);

        const response = await fetch(`${apiBaseUrl}/calculations/homepage-insights/?_ts=${Date.now()}`, {
          method: 'GET',
          signal: abortController.signal,
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`Insights endpoint failed with status ${response.status}`);
        }

        const responseData = await response.json();
        if (responseData?.success && responseData?.data) {
          setInsights(responseData.data);
        } else {
          setInsights(EMPTY_PAYLOAD);
        }
      } catch (error) {
        if (!abortController.signal.aborted) {
          setHasError(true);
          setInsights(EMPTY_PAYLOAD);
        }
      } finally {
        if (!abortController.signal.aborted) {
          setIsLoading(false);
        }
      }
    };

    loadInsights();
    return () => abortController.abort();
  }, [apiBaseUrl]);

  return (
    <section className={styles.insightsSection} aria-label="Hesaplama İstatistikleri">
      <div className={styles.insightsHeaderRow}>
        <h2 className={styles.insightsTitle}>📊 Türkiye Geneli Hesaplama İstatistikleri</h2>
        <p className={styles.insightsSubtitle}>Platformumuzda gerçekleştirilen anlık hesaplama verileri</p>
      </div>
      <div className={styles.insightsMetaBar}>
        <span className={styles.insightsMeta}>📍 {insights.province_count} farklı ilden hesaplama yapıldı</span>
      </div>

      {isLoading ? (
        <p className={styles.insightsStatus}>İstatistikler yükleniyor...</p>
      ) : hasError ? (
        <p className={styles.insightsStatus}>İstatistik servisine erişilemedi. Lütfen tekrar deneyin.</p>
      ) : (
        <>
          <div className={styles.insightsGrid}>
            <article className={styles.insightCard}>
              <div className={styles.insightIcon}>🐄</div>
              <h3>Gübre Çukuru Hesabı</h3>
              <p className={styles.insightCount}>{insights.totals.gubre_cukuru}</p>
            </article>

            <article className={styles.insightCard}>
              <div className={styles.insightIcon}>🌾</div>
              <h3>Havza Destekleme</h3>
              <p className={styles.insightCount}>{insights.totals.havza_bazli_destekleme}</p>
            </article>

            <article className={styles.insightCard}>
              <button
                type="button"
                className={styles.insightToggleButton}
                onClick={() => setShowProvinceBreakdown((current) => !current)}
                aria-expanded={showProvinceBreakdown}
                aria-controls="tarimsal-yapi-il-dagilimi"
              >
                <div className={styles.insightIcon}>🏗️</div>
                <h3>Tarımsal Yapı Hesabı</h3>
                <p className={styles.insightCount}>{insights.totals.tarimsal_yapi}</p>
                <span className={styles.insightHint}>İl dağılımını görüntüle</span>
              </button>
            </article>
          </div>

          {showProvinceBreakdown && (
            <div id="tarimsal-yapi-il-dagilimi" className={styles.provinceBreakdown}>
              <h3 className={styles.provinceBreakdownTitle}>🗺️ İllere Göre Tarımsal Yapı Hesaplama Dağılımı</h3>
              <p className={styles.provinceBreakdownSubtitle}>
                Bağ evi, sera, arıcılık, mantar tesisi gibi yapıların il bazında hesaplama sayıları
              </p>
              {insights.tarimsal_yapi_by_province.length === 0 ? (
                <p className={styles.insightsStatus}>İl bazlı kayıt henüz bulunmuyor.</p>
              ) : (
                <div className={styles.provinceBreakdownGrid}>
                  {insights.tarimsal_yapi_by_province.map((item) => {
                    const isSelected = selectedProvince === item.province;
                    const detailsId = `province-period-${item.province.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
                    return (
                      <div key={item.province} className={styles.provinceItemWrapper}>
                        <button
                          type="button"
                          className={`${styles.provinceBreakdownItem} ${isSelected ? styles.provinceBreakdownItemActive : ''}`}
                          onClick={() => setSelectedProvince((current) => (current === item.province ? null : item.province))}
                          aria-expanded={isSelected}
                          aria-controls={detailsId}
                          aria-label={`${item.province} detaylarını göster`}
                        >
                          <span className={styles.provinceName}>{item.province}</span>
                          <span className={styles.provinceValue}>{item.count}</span>
                        </button>

                        {isSelected && (
                          <div id={detailsId} className={styles.provincePeriodStats}>
                            <p className={styles.provincePeriodTitle}>📍 {item.province} zaman bazlı hesaplama</p>
                            <div className={styles.provincePeriodGrid}>
                              <div className={styles.provincePeriodItem}>
                                <span>Toplam</span>
                                <strong>{item.count}</strong>
                              </div>
                              <div className={styles.provincePeriodItem}>
                                <span>Son 7 gün</span>
                                <strong>{item.count_7d}</strong>
                              </div>
                              <div className={styles.provincePeriodItem}>
                                <span>Son 28 gün</span>
                                <strong>{item.count_28d}</strong>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </>
      )}
    </section>
  );
}
