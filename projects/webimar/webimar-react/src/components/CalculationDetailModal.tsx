import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import DOMPurify from 'dompurify';
import { CalculationHistory } from '../services/cachedApi';
import MapComponent from './Map/MapComponent';

const Overlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const Modal = styled.div`
  background: white;
  border-radius: 12px;
  padding: 32px;
  width: 90%;
  max-width: 700px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  max-height: 90vh;
  overflow-y: auto;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
`;

const Title = styled.h2`
  color: #2563eb;
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  flex: 1;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
  margin-left: 16px;
  
  &:hover {
    color: #374151;
  }
`;

const MetaInfo = styled.div`
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
`;

const MetaItem = styled.div`
  display: flex;
  flex-direction: column;
`;

const MetaLabel = styled.span`
  color: #6b7280;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
`;

const MetaValue = styled.span`
  color: #1f2937;
  font-weight: 500;
`;

const Section = styled.div`
  margin-bottom: 24px;
`;

const SectionTitle = styled.h3`
  color: #1f2937;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SectionContent = styled.div`
  background: #f9fafb;
  border-radius: 8px;
  padding: 16px;
`;

const JsonDisplay = styled.pre`
  background: #1f2937;
  color: #f9fafb;
  padding: 16px;
  border-radius: 8px;
  font-size: 14px;
  overflow-x: auto;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
`;

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const ResultsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
`;

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const ResultCard = styled.div`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
`;

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const ResultLabel = styled.div`
  color: #6b7280;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
`;

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const ResultValue = styled.div`
  color: #1f2937;
  font-size: 18px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
`;

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const ParametersGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
`;

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const ParameterItem = styled.div`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 12px;
`;

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const ParameterLabel = styled.div`
  color: #6b7280;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
`;

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const ParameterValue = styled.div`
  color: #1f2937;
  font-weight: 500;
`;

const Description = styled.p`
  color: #4b5563;
  line-height: 1.6;
  margin: 0;
`;

const LoadingWrapper = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: #6b7280;
`;

const ErrorWrapper = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: #dc2626;
  text-align: center;
`;

interface CalculationDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  calculation: CalculationHistory;
}

const CalculationDetailModal: React.FC<CalculationDetailModalProps> = ({
  isOpen,
  onClose,
  calculation
}) => {
  const [loading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Modal açıldığında <style> taglarını head'e ekle, kapandığında kaldır
  React.useEffect(() => {
    if (!isOpen) return;
    const htmlMessage = getHtmlMessage();
    if (!htmlMessage) return;
    // <style> taglarını bul
    const styleRegex = /<style[^>]*>([\s\S]*?)<\/style>/gi;
    let match;
    const styleElements: HTMLStyleElement[] = [];
    while ((match = styleRegex.exec(htmlMessage)) !== null) {
      const styleContent = match[1];
      const styleEl = document.createElement('style');
      styleEl.setAttribute('data-modal-style', 'calculation-detail');
      styleEl.textContent = styleContent;
      document.head.appendChild(styleEl);
      styleElements.push(styleEl);
    }
    // Temizlik: modal kapanınca eklenen style'ları kaldır
    return () => {
      styleElements.forEach((el) => {
        if (el.parentNode) el.parentNode.removeChild(el);
      });
      // Ayrıca, data-modal-style ile eklenmiş eski style'ları da temizle
      const oldStyles = document.querySelectorAll('style[data-modal-style="calculation-detail"]');
      oldStyles.forEach((el) => el.parentNode && el.parentNode.removeChild(el));
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]); // getHtmlMessage is defined inside component and depends on calculation

  useEffect(() => {
    if (isOpen && calculation) {
      setError(null);
    }
  }, [isOpen, calculation]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('tr-TR');
  };

  const getCalculationTypeName = (type: string) => {
    const typeMap: { [key: string]: string } = {
      'sera': 'Sera Hesaplaması',
      'bag-evi': 'Bağ Evi Hesaplaması',
      'aricilik': 'Arıcılık Tesisi Hesaplaması',
      'mantar-tesisi': 'Mantar Tesisi Hesaplaması',
      'solucan-tesisi': 'Solucan Tesisi Hesaplaması',
      'buyukbas': 'Büyükbaş Hayvancılık Hesaplaması',
      'kucukbas': 'Küçükbaş Hayvancılık Hesaplaması',
      'kanatli': 'Kanatlı Hayvancılık Hesaplaması',
      'hara': 'Hara Tesisi Hesaplaması',
      'tarimsal-depo': 'Tarımsal Depo Hesaplaması',
      'tarimsal-amacli-depo': 'Tarımsal Amaçlı Depo Hesaplaması',
      'lisansli-depo': 'Lisanslı Depo Hesaplaması',
      'hububat-silo': 'Hububat Silo Hesaplaması',
      'yikama-tesisi': 'Yıkama Tesisi Hesaplaması',
      'kurutma-tesisi': 'Kurutma Tesisi Hesaplaması',
      'soguk-hava-deposu': 'Soğuk Hava Deposu Hesaplaması',
      'zeytinyagi-fabrikasi': 'Zeytinyağı Fabrikası Hesaplaması',
      'zeytinyagi-uretim-tesisi': 'Zeytinyağı Üretim Tesisi Hesaplaması',
      'meyve-sebze-kurutma': 'Meyve-Sebze Kurutma Tesisi Hesaplaması',
      'su-depolama': 'Su Depolama Tesisi Hesaplaması',
      'su-kuyulari': 'Su Kuyuları Hesaplaması',
      'evcil-hayvan': 'Evcil Hayvan Bakımevi Hesaplaması',
      'sut-sigirciligi': 'Süt Sığırcılığı Hesaplaması',
      'besi-sigirciligi': 'Besi Sığırcılığı Hesaplaması',
      'agil-kucukbas': 'Ağıl (Küçükbaş) Hesaplaması',
      'kumes-yumurtaci': 'Kümes (Yumurtacı) Hesaplaması',
      'kumes-etci': 'Kümes (Etçi) Hesaplaması',
      'kumes-gezen': 'Kümes (Gezen) Hesaplaması',
      'kumes-hindi': 'Kümes (Hindi) Hesaplaması',
      'kaz-ordek': 'Kaz-Ördek Hesaplaması',
      'ipek-bocekciligi': 'İpek Böcekçiliği Hesaplaması',
      'arazi_alani': 'Arazi Alanı Hesaplama',
      'dikili_alan': 'Dikili Alan Hesaplama',
      'bag_evi': 'Bağ Evi Hesaplama',
      'yapilasma': 'Yapılaşma Hesaplama',
      'mesafe': 'Mesafe Hesaplama',
      'other': 'Diğer Hesaplama',
    };
    return typeMap[type] || type;
  };

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const formatParameterKey = (key: string) => {
    const keyMap: { [key: string]: string } = {
      'alan_m2': 'Alan (m²)',
      'arazi_vasfi': 'Arazi Vasfi',
      'il': 'İl',
      'ilce': 'İlçe',
      'mahalle': 'Mahalle',
      'pafta': 'Pafta',
      'ada': 'Ada',
      'parsel': 'Parsel',
      'yuzolcumu': 'Yüzölçümü',
      'nitelik': 'Nitelik',
      'sinif': 'Sınıf',
      'mevki': 'Mevki',
      'kisitlama': 'Kısıtlama',
      'cins': 'Cins',
      'hayvan_sayisi': 'Hayvan Sayısı',
      'kapasite': 'Kapasite',
      'depo_turu': 'Depo Türü',
      'isletme_turu': 'İşletme Türü',
      'uretim_kapasitesi': 'Üretim Kapasitesi',
      'tesis_turu': 'Tesis Türü',
      'teknoloji_turu': 'Teknoloji Türü',
      'sulama_sistemi': 'Sulama Sistemi',
      'sera_tipi': 'Sera Tipi',
      'ortu_malzemesi': 'Örtü Malzemesi',
      'ısıtma_sistemi': 'Isıtma Sistemi',
      'sogutma_sistemi': 'Soğutma Sistemi',
      'ventilasyon_sistemi': 'Ventilasyon Sistemi',
      'elektrik_guc': 'Elektrik Gücü',
      'su_ihtiyaci': 'Su İhtiyacı',
      'atik_yonetimi': 'Atık Yönetimi',
      'cevre_etki': 'Çevre Etkisi',
      'yatirim_maliyeti': 'Yatırım Maliyeti',
      'isletme_maliyeti': 'İşletme Maliyeti',
      'gelir_tahmini': 'Gelir Tahmini',
      'kar_marji': 'Kar Marjı',
      'geri_odeme_suresi': 'Geri Ödeme Süresi',
    };
    return keyMap[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const formatParameterValue = (value: any) => {
    if (typeof value === 'number') {
      return value.toLocaleString('tr-TR');
    }
    if (typeof value === 'boolean') {
      return value ? 'Evet' : 'Hayır';
    }
    if (Array.isArray(value)) {
      return value.join(', ');
    }
    if (typeof value === 'object' && value !== null) {
      return JSON.stringify(value, null, 2);
    }
    return String(value);
  };

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const formatResultKey = (key: string) => {
    const keyMap: { [key: string]: string } = {
      'toplam_alan': 'Toplam Alan',
      'yapilasma_alani': 'Yapılaşma Alanı',
      'acik_alan': 'Açık Alan',
      'yesil_alan': 'Yeşil Alan',
      'otopark_alani': 'Otopark Alanı',
      'toplam_maliyet': 'Toplam Maliyet',
      'birim_maliyet': 'Birim Maliyet',
      'yillik_gelir': 'Yıllık Gelir',
      'yillik_gider': 'Yıllık Gider',
      'net_kar': 'Net Kar',
      'yatirim_getirisi': 'Yatırım Getirisi',
      'geri_odeme_suresi': 'Geri Ödeme Süresi',
      'kapasite_kullanimi': 'Kapasite Kullanımı',
      'verimlilik_orani': 'Verimlilik Oranı',
      'enerji_tuketimi': 'Enerji Tüketimi',
      'su_tuketimi': 'Su Tüketimi',
      'sera_alani': 'Sera Alanı',
      'uretim_miktari': 'Üretim Miktarı',
      'hayvan_kapasitesi': 'Hayvan Kapasitesi',
      'yem_ihtiyaci': 'Yem İhtiyacı',
      'su_ihtiyaci': 'Su İhtiyacı',
      'elektrik_ihtiyaci': 'Elektrik İhtiyacı',
      'iscilik_ihtiyaci': 'İşçilik İhtiyacı',
      'bakim_maliyeti': 'Bakım Maliyeti',
      'sigorta_maliyeti': 'Sigorta Maliyeti',
      'vergi_maliyeti': 'Vergi Maliyeti',
      'toplam_gelir': 'Toplam Gelir',
      'toplam_gider': 'Toplam Gider',
      'brut_kar': 'Brüt Kar',
      'kar_marji': 'Kar Marjı',
      'yatirim_tutari': 'Yatırım Tutarı',
      'kredi_ihtiyaci': 'Kredi İhtiyacı',
      'ozkaynak_payi': 'Özkaynak Payı',
      'faiz_orani': 'Faiz Oranı',
      'kredi_vadesi': 'Kredi Vadesi',
      'aylik_taksit': 'Aylık Taksit',
      'toplam_faiz': 'Toplam Faiz',
      'toplam_odeme': 'Toplam Ödeme',
      'karlilk_orani': 'Karlılık Oranı',
      'risk_faktoru': 'Risk Faktörü',
      'pazar_potansiyeli': 'Pazar Potansiyeli',
      'rekabet_durumu': 'Rekabet Durumu',
      'teknoloji_seviyesi': 'Teknoloji Seviyesi',
      'cevresel_etki': 'Çevresel Etki',
      'sosyal_etki': 'Sosyal Etki',
      'kalite_standardi': 'Kalite Standardı',
      'sertifikasyon': 'Sertifikasyon',
      'ihracat_potansiyeli': 'İhracat Potansiyeli',
      'devlet_destegi': 'Devlet Desteği',
      'teşvik_miktari': 'Teşvik Miktarı',
      'vergi_avantaji': 'Vergi Avantajı',
      'kredi_faiz_destegi': 'Kredi Faiz Desteği',
      'hibе_miktari': 'Hibe Miktarı',
      'toplam_destek': 'Toplam Destek',
      'net_yatirim': 'Net Yatırım',
      'destekli_geri_odeme': 'Destekli Geri Ödeme',
      'toplam_fayda': 'Toplam Fayda',
      'sosyal_fayda': 'Sosyal Fayda',
      'ekonomik_fayda': 'Ekonomik Fayda',
      'cevresel_fayda': 'Çevresel Fayda',
      'toplam_etki': 'Toplam Etki',
      'basari_orani': 'Başarı Oranı',
      'oneri_puani': 'Öneri Puanı',
    };
    return keyMap[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const formatResultValue = (value: any, key: string) => {
    if (typeof value === 'number') {
      if (key.includes('alan') || key.includes('_m2')) {
        return `${value.toLocaleString('tr-TR')} m²`;
      }
      if (key.includes('maliyet') || key.includes('gelir') || key.includes('gider') || key.includes('kar') || key.includes('tutari') || key.includes('taksit') || key.includes('faiz') || key.includes('odeme') || key.includes('destek') || key.includes('yatirim') || key.includes('hibe') || key.includes('teşvik')) {
        return `${value.toLocaleString('tr-TR')} ₺`;
      }
      if (key.includes('oran') || key.includes('marj') || key.includes('getiri') || key.includes('puan') || key.includes('kullanim') || key.includes('verim') || key.includes('karlilk') || key.includes('risk') || key.includes('basari')) {
        return `${value.toFixed(2)}%`;
      }
      if (key.includes('sure') || key.includes('vade')) {
        return `${value} ay`;
      }
      if (key.includes('miktar') || key.includes('kapasite') || key.includes('sayisi') || key.includes('ihtiyac') || key.includes('tuketim')) {
        return `${value.toLocaleString('tr-TR')} adet`;
      }
      if (key.includes('guc') || key.includes('elektrik')) {
        return `${value.toLocaleString('tr-TR')} kW`;
      }
      if (key.includes('su')) {
        return `${value.toLocaleString('tr-TR')} litre`;
      }
      return value.toLocaleString('tr-TR');
    }
    if (typeof value === 'boolean') {
      return value ? 'Evet' : 'Hayır';
    }
    if (Array.isArray(value)) {
      return value.join(', ');
    }
    if (typeof value === 'object' && value !== null) {
      return JSON.stringify(value, null, 2);
    }
    return String(value);
  };

  // === HTML mesajını al ===
  const getHtmlMessage = () => {
    try {
      const r = calculation.result || {};
      
      // Önce data.results.mesaj'dan al (yeni yapı)
      if (typeof r.data?.results?.mesaj === 'string' && r.data.results.mesaj) return r.data.results.mesaj;
      if (typeof r.data?.results?.ana_mesaj === 'string' && r.data.results.ana_mesaj) return r.data.results.ana_mesaj;
      if (typeof r.data?.results?.html_mesaj === 'string' && r.data.results.html_mesaj) return r.data.results.html_mesaj;
      
      // Fallback: eski yapılar için
      if (typeof r.mesaj === 'string' && r.mesaj) return r.mesaj;
      if (typeof r.html_mesaj === 'string' && r.html_mesaj) return r.html_mesaj;
      if (typeof r.data?.mesaj === 'string' && r.data.mesaj) return r.data.mesaj;
      if (typeof r.data?.html_mesaj === 'string' && r.data.html_mesaj) return r.data.html_mesaj;
      if (typeof r.results?.mesaj === 'string' && r.results.mesaj) return r.results.mesaj;
      if (typeof r.results?.html_mesaj === 'string' && r.results.html_mesaj) return r.results.html_mesaj;
      if (typeof r.ana_mesaj === 'string' && r.ana_mesaj) return r.ana_mesaj;
      if (typeof r.data?.ana_mesaj === 'string' && r.data.ana_mesaj) return r.data.ana_mesaj;
      if (typeof r.results?.ana_mesaj === 'string' && r.results.ana_mesaj) return r.results.ana_mesaj;
      
      return null;
    } catch {
      return null;
    }
  };

  if (!isOpen) return null;

  const htmlMessage = getHtmlMessage();
  
  // Defense-in-depth: Backend sanitize etse bile frontend'de de DOMPurify ile temizle
  const sanitizedHtml = htmlMessage ? DOMPurify.sanitize(htmlMessage, { 
    ALLOWED_ATTR: ['class', 'style', 'id', 'href', 'src', 'alt', 'width', 'height'],
    ALLOWED_URI_REGEXP: /^(?:(?:https?|mailto|tel):|[^a-z]|[a-z+.-]+:\/\/)/i,
    ALLOW_DATA_ATTR: false
  }) : null;

  return (
    <Overlay onClick={(e) => e.target === e.currentTarget && onClose()}>
      <Modal>
        <Header>
          <Title>Hesaplama Detayları</Title>
          <CloseButton onClick={onClose}>×</CloseButton>
        </Header>

        {loading && (
          <LoadingWrapper>
            Hesaplama detayları yükleniyor...
          </LoadingWrapper>
        )}

        {error && (
          <ErrorWrapper>
            <div>
              <div>❌</div>
              <div>{error}</div>
            </div>
          </ErrorWrapper>
        )}

        {calculation && !loading && !error && (
          <>
            <MetaInfo>
              <MetaItem>
                <MetaLabel>Başlık</MetaLabel>
                <MetaValue>{calculation.title || 'Başlık belirtilmemiş'}</MetaValue>
              </MetaItem>
              <MetaItem>
                <MetaLabel>Hesaplama Türü</MetaLabel>
                <MetaValue>{getCalculationTypeName(calculation.calculation_type)}</MetaValue>
              </MetaItem>
              <MetaItem>
                <MetaLabel>Tarih</MetaLabel>
                <MetaValue>{formatDate(calculation.created_at)}</MetaValue>
              </MetaItem>
              {/* Durum kısmı gizlendi */}
            </MetaInfo>

            {calculation.description && (
              <Section>
                <SectionTitle>📄 Açıklama</SectionTitle>
                <SectionContent>
                  <Description>{calculation.description}</Description>
                </SectionContent>
              </Section>
            )}

            {/* Parametreler bölümü gizlendi - kullanıcı isteği */}

            {calculation.result && htmlMessage && (
              <div style={{padding:0,background:'none',borderRadius:0}}>
                <div dangerouslySetInnerHTML={{ __html: sanitizedHtml || '' }} />
              </div>
            )}

            {calculation.map_coordinates && (
              <Section>
                <SectionTitle>🗺️ Harita</SectionTitle>
                <SectionContent>
                  <React.Suspense fallback={<div>Harita yükleniyor...</div>}>
                    <div style={{ width: '100%', height: '300px', marginBottom: 12 }}>
                      <MapComponent
                        center={[calculation.map_coordinates.lat, calculation.map_coordinates.lng]}
                        zoom={15}
                        selectedCoordinate={calculation.map_coordinates}
                        showMarker={true}
                        height="300px"
                      />
                    </div>
                  </React.Suspense>
                  <JsonDisplay>
                    {JSON.stringify(calculation.map_coordinates, null, 2)}
                  </JsonDisplay>
                </SectionContent>
              </Section>
            )}
          </>
        )}
      </Modal>
    </Overlay>
  );
};

export default CalculationDetailModal;
