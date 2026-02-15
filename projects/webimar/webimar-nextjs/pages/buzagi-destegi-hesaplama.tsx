import { useMemo, useState } from 'react';
import Head from 'next/head';
import styled from 'styled-components';
import Layout from '../components/Layout';
import Seo from '../components/Seo';
import { BUZAGI_DESTEGI_CONFIG, PLANLI_URETIM_ILLERI } from '../data/buzagiDestegiConfig';

type SoyKutuguSinifi = 'ab' | 'c' | null;

type HesapInput = {
  toplamBuyukbas: number;
  disiBuzagi: number;
  erkekBuzagi: number;
  cinsiyet: 'erkek' | 'kadin' | '';
  yasGrubu: 'alti' | 'ustu';
  birinciDereceOrgut: boolean;
  suniTohumlamaVeyaEmbriyo: boolean;
  suniTohumlamaSayisi: number;
  yerliSperma: boolean;
  yerliSpermaSayisi: number;
  sutBesiBolgesi: boolean;
  sutBesiBolgesiSayisi: number;
  soyKutuguVar: boolean;
  soyKutuguSinifi: SoyKutuguSinifi;
  soyKutuguAbSayisi: number;
  soyKutuguCSayisi: number;
  genomikTest: boolean;
  genomikTestDisiBuzagiSayisi: number;
  ariIsletme: boolean;
  ariIsletmeDisiBuzagiSayisi: number;
  abOnayliIsletme: boolean;
  abOnayliDisiBuzagiSayisi: number;
};

type DestekSatiri = {
  key: string;
  ad: string;
  oran: number;
  hakEdisAdet: number;
  birimTutar: number;
  toplamTutar: number;
};

type TarimsalOrgut = {
  il: string;
  ilce: string;
  orgut: string;
};

type DestekDetaySatiri = {
  destekTuru: string;
  tutar: string;
  kosullar: string[];
};

const initialInput: HesapInput = {
  toplamBuyukbas: 0,
  disiBuzagi: 0,
  erkekBuzagi: 0,
  cinsiyet: '',
  yasGrubu: 'ustu',
  birinciDereceOrgut: false,
  suniTohumlamaVeyaEmbriyo: false,
  suniTohumlamaSayisi: 0,
  yerliSperma: false,
  yerliSpermaSayisi: 0,
  sutBesiBolgesi: false,
  sutBesiBolgesiSayisi: 0,
  soyKutuguVar: false,
  soyKutuguSinifi: null,
  soyKutuguAbSayisi: 0,
  soyKutuguCSayisi: 0,
  genomikTest: false,
  genomikTestDisiBuzagiSayisi: 0,
  ariIsletme: false,
  ariIsletmeDisiBuzagiSayisi: 0,
  abOnayliIsletme: false,
  abOnayliDisiBuzagiSayisi: 0,
};

const ORGUT_LISTESI_DOSYA_YOLU = '/2025_birinci_derece_tarimsal_orgut_listesi';

const ILAVE_DESTEK_KRITERLERI = [
  'Aile işletmesi (en fazla 20 baş): temel desteğe ilave %100 (en fazla 10 baş).',
  'Cinsiyetten bağımsız 41 yaşından gün almamış genç üretici veya her yaştan kadın üretici: ilave %70.',
  'Planlı üretim bölgesi (süt/besi havzası): ilave %50.',
  'Birinci derece tarımsal örgüt üyeliği: ilave %20.',
  'Suni tohumlama / embriyo transferi: ilave %80.',
  'Yerli sperma kullanımı: ilave %50.',
  'Soy kütüğü (A-B): ilave %150, Soy kütüğü (C): ilave %80.',
  'Genomik test (uygun ırklar): ilave %150.',
  'Ari işletmede doğan dişi buzağı: ilave %400.',
  'AB onaylı işletmede doğan dişi buzağı: ilave %60.',
];

const DESTEK_DETAY_SATIRLARI: DestekDetaySatiri[] = [
  {
    destekTuru: 'Temel Buzağı Desteği',
    tutar: '1.400 TL/baş',
    kosullar: [
      'Yurtiçinde doğmuş olma.',
      'Küpelenerek TÜRKVET sistemine kayıtlı olma.',
      'Bakanlık programlı aşılarının yapılmış olması.',
      'En az 4 ay (120 gün) yaşamış olma.',
    ],
  },
  {
    destekTuru: 'Aile İşletmesi İlave Desteği',
    tutar: '1.400 TL/baş',
    kosullar: [
      'Destekleme yılı son iş günü itibariyle işletmede 1-20 baş sığır/manda varlığı bulunması.',
      'En fazla 10 baş buzağı/malak için ilave destek uygulanması.',
    ],
  },
  {
    destekTuru: 'Genç / Kadın Yetiştirici Desteği',
    tutar: '980 TL/baş',
    kosullar: [
      'Destekleme yılı sonunda 41 yaşından gün almamış genç üretici olma.',
      'veya kadın yetiştirici olma.',
    ],
  },
  {
    destekTuru: 'Planlı Bölge Desteği',
    tutar: '700 TL/baş',
    kosullar: [
      'Süt üretim planlama bölgesinde tanımlanan sütçü ırk / sütçü ırk melezi olma.',
      'veya besilik materyal üretim planlama bölgesinde tanımlanan etçi ırk / etçi ırk melezi olma.',
    ],
  },
  {
    destekTuru: '1. Derece Örgüt Üyeliği İlave Desteği',
    tutar: '280 TL/baş',
    kosullar: [
      'Bakanlık derecelendirmesi sonucunda 1. derece tarımsal örgüt (birlik/kooperatif) üyesi olma.',
    ],
  },
  {
    destekTuru: 'Soy Kütüğü İlave Desteği',
    tutar: 'A-B: 2.100 TL/baş, C: 1.120 TL/baş',
    kosullar: [
      'E-Islah veritabanında işletme soy kütüğü sınıfının A, B veya C olması.',
    ],
  },
  {
    destekTuru: 'Genomik Test Desteği',
    tutar: '2.100 TL/baş',
    kosullar: [
      'E-Islah sisteminde soy kütüğü sınıfı A-B hayvanlardan doğmuş olma.',
      'Bakanlıkça onaylı Genomik Damızlık Değerinin belirlenmiş olması.',
    ],
  },
  {
    destekTuru: 'Suni Tohumlama / Embriyo Transferi İlave Desteği',
    tutar: '1.120 TL/baş',
    kosullar: [
      'Suni tohumlama veya embriyo transferi uygulamasından doğmuş olma.',
    ],
  },
  {
    destekTuru: 'Yerli Sperma Kullanımı İlave Desteği',
    tutar: '700 TL/baş',
    kosullar: [
      'Yerli üretim sperma ile yapılan suni tohumlama/embriyo transferinden doğmuş olma.',
    ],
  },
  {
    destekTuru: 'Ari İşletme İlave Desteği',
    tutar: '5.600 TL/baş',
    kosullar: [
      'Hastalıktan ari işletmede doğan dişi buzağı/malak olma.',
    ],
  },
  {
    destekTuru: 'AB Onaylı İşletme İlave Desteği',
    tutar: '840 TL/baş',
    kosullar: [
      'AB onaylı işletmede doğan dişi buzağı/malak olma.',
    ],
  },
];

const BASVURU_DONEMI_BILGILERI = [
  'Desteklemeye esas doğum aralığı: 01.01.2025 - 31.12.2025.',
  '1. dönem başvuruları 01.09.2025 tarihinde başlar ve 01.12.2025 tarihinde son bulur.',
  '2. dönem başvuruları 01.04.2026 tarihinde başlar ve 12.06.2026 tarihinde son bulur.',
];

const BASVURU_YERI_SEKLI = [
  'Bireysel başvurular İl/İlçe Müdürlüklerine yapılır.',
  'Tarımsal örgüt üzerinden başvurular üyesi olunan Birlik/Kooperatife yapılır.',
];

const parseOrgutListesiMarkdown = (md: string): TarimsalOrgut[] => {
  const lines = md.split(/\r?\n/).map((line) => line.trim());
  const rows: TarimsalOrgut[] = [];

  for (const line of lines) {
    if (!line.startsWith('|')) continue;
    if (line.includes('---')) continue;

    const parts = line
      .split('|')
      .map((part) => part.trim())
      .filter((part) => part.length > 0);

    if (parts.length < 4) continue;
    if (parts[0].toLocaleLowerCase('tr-TR') === 'sıra' || parts[1]?.toLocaleLowerCase('tr-TR') === 'il') continue;

    const il = (parts[1] || '').trim();
    const ilce = (parts[2] || '').trim();
    const orgut = (parts[3] || '').trim();

    if (il && ilce && orgut) {
      rows.push({ il, ilce, orgut });
    }
  }

  return rows;
};

const Page = styled.main`
  width: 100%;
  min-height: 100vh;
  background: #f8fafc;
`;

const Container = styled.div`
  max-width: 1080px;
  margin: 0 auto;
  padding: clamp(12px, 2.6vw, 20px);
  padding-bottom: calc(16px + env(safe-area-inset-bottom, 0px));
  padding-left: calc(clamp(12px, 2.6vw, 20px) + env(safe-area-inset-left, 0px));
  padding-right: calc(clamp(12px, 2.6vw, 20px) + env(safe-area-inset-right, 0px));
  display: grid;
  gap: 18px;
`;

const Card = styled.section`
  min-width: 0;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: clamp(14px, 2vw, 18px);
`;

const Title = styled.h1`
  margin: 0;
  color: #1f2937;
  font-size: clamp(22px, 3.3vw, 30px);
  line-height: 1.2;
`;

const Subtitle = styled.p`
  margin: 8px 0 0;
  color: #4b5563;
  line-height: 1.5;
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;

  @media (max-width: 1040px) {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
`;

const Field = styled.label`
  display: grid;
  gap: 6px;
  color: #374151;
  font-size: 14px;
`;

const Input = styled.input`
  height: 48px;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 0 12px;
  font-size: 16px;
`;

const Select = styled.select`
  height: 48px;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 0 12px;
  font-size: 16px;
  background: #fff;
`;

const CheckGrid = styled.div`
  margin-top: 14px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
`;

const Check = styled.label`
  display: flex;
  align-items: flex-start;
  gap: 8px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 10px 12px;
  color: #1f2937;

  input[type='checkbox'] {
    width: 18px;
    height: 18px;
    margin-top: 2px;
    accent-color: #fd7e3a;
  }
`;

const RowInline = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
`;

const SecondaryButton = styled.button`
  margin-left: 12px;
  font-size: 13px;
  padding: 6px 10px;
  border: 1px solid #d1d5db;
  background: #f9fafb;
  color: #1f2937;
  border-radius: 8px;
  cursor: pointer;
`;

const PrimaryButton = styled.button`
  border: none;
  background: #fd7e3a;
  color: #fff;
  font-weight: 700;
  border-radius: 10px;
  height: 48px;
  padding: 0 20px;
  cursor: pointer;

  @media (max-width: 640px) {
    width: 100%;
  }
`;

const FormActions = styled.div`
  margin-top: 14px;
`;

const MetaRow = styled.div`
  margin-top: 10px;
  color: #6b7280;
  font-size: 14px;
`;

const Summary = styled.div`
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
`;

const SummaryBox = styled.div`
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 12px;
  background: #f9fafb;
`;

const SummaryLabel = styled.div`
  color: #6b7280;
  font-size: 13px;
`;

const SummaryValue = styled.div`
  margin-top: 4px;
  color: #111827;
  font-size: clamp(20px, 3.4vw, 26px);
  font-weight: 700;
`;

const TableWrap = styled.div`
  min-width: 0;
  overflow-x: auto;
  margin-top: 12px;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;

  th,
  td {
    border-bottom: 1px solid #e5e7eb;
    padding: 10px;
    text-align: left;
    white-space: nowrap;
  }

  th:first-child,
  td:first-child {
    white-space: normal;
    min-width: 180px;
  }

  th {
    color: #374151;
    font-weight: 700;
    background: #f9fafb;
  }

  tfoot td {
    font-weight: 700;
  }

  @media (max-width: 768px) {
    th,
    td {
      font-size: 13px;
      padding: 8px;
    }
  }
`;

const ModalOverlay = styled.div`
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
`;

const ModalContent = styled.div`
  width: min(900px, 100%);
  max-height: 90vh;
  overflow: auto;
  background: #fff;
  border-radius: 14px;
  padding: 16px;
`;

const ModalHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
`;

const OrgutList = styled.div`
  display: grid;
  gap: 8px;
  margin-top: 10px;
`;

const OrgutItem = styled.div`
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 10px;
  color: #1f2937;
  font-size: 14px;
`;

const InfoTitle = styled.h2`
  margin: 0;
  color: #111827;
  font-size: clamp(20px, 2.6vw, 24px);
`;

const InfoSubTitle = styled.h3`
  margin: 14px 0 8px;
  color: #1f2937;
  font-size: clamp(17px, 2.3vw, 20px);
`;

const InfoText = styled.p`
  margin: 8px 0 0;
  color: #374151;
  line-height: 1.65;
`;

const InfoList = styled.ul`
  margin: 10px 0 0;
  padding-left: 18px;
  color: #374151;
  line-height: 1.65;
`;

const InfoStrong = styled.strong`
  color: #111827;
`;

const DetailTableWrap = styled.div`
  margin-top: 10px;
  overflow-x: auto;
`;

const DetailTable = styled.table`
  width: 100%;
  border-collapse: collapse;

  th,
  td {
    border: 1px solid #e5e7eb;
    padding: 10px;
    text-align: left;
    vertical-align: top;
  }

  th {
    background: #f3f4f6;
    color: #111827;
    font-weight: 700;
    font-size: 14px;
    white-space: nowrap;
  }

  td {
    font-size: 14px;
    color: #374151;
  }

  ul {
    margin: 0;
    padding-left: 18px;
    line-height: 1.55;
  }

  @media (max-width: 768px) {
    th,
    td {
      font-size: 13px;
      padding: 8px;
    }
  }
`;

const normalizeCount = (value: number, max: number): number => {
  if (!Number.isFinite(value)) return 0;
  if (value < 0) return 0;
  if (value > max) return max;
  return Math.floor(value);
};

const formatCurrency = (value: number) => `${value.toLocaleString('tr-TR')} TL`;
const toInputValue = (value: number) => (value === 0 ? '' : String(value));

export default function BuzagiDestegiHesaplamaPage() {
  const [input, setInput] = useState<HesapInput>(initialInput);
  const [submittedInput, setSubmittedInput] = useState<HesapInput | null>(null);
  const [orgutModalOpen, setOrgutModalOpen] = useState(false);
  const [orgutListesi, setOrgutListesi] = useState<TarimsalOrgut[]>([]);
  const [orgutListesiLoading, setOrgutListesiLoading] = useState(false);
  const [orgutListesiError, setOrgutListesiError] = useState('');

  const toplamBuzagi = Math.max(0, input.disiBuzagi) + Math.max(0, input.erkekBuzagi);
  const temelDestek = BUZAGI_DESTEGI_CONFIG.temelDestekTl;

  const kadinVeyaGencUygun = input.cinsiyet === 'kadin' || input.yasGrubu === 'alti';
  const aileIsletmesiUygun = input.toplamBuyukbas <= BUZAGI_DESTEGI_CONFIG.aileIsletmesiMaksimumBuyukbas;

  const loadOrgutListesi = async () => {
    setOrgutModalOpen(true);
    if (orgutListesi.length > 0 || orgutListesiLoading) return;

    setOrgutListesiLoading(true);
    setOrgutListesiError('');

    try {
      const res = await fetch(ORGUT_LISTESI_DOSYA_YOLU);
      if (!res.ok) throw new Error(`Liste yüklenemedi (HTTP ${res.status})`);
      const text = await res.text();
      setOrgutListesi(parseOrgutListesiMarkdown(text));
    } catch (error) {
      setOrgutListesiError(error instanceof Error ? error.message : 'Liste yüklenemedi.');
    } finally {
      setOrgutListesiLoading(false);
    }
  };

  const filteredOrgutListesi = useMemo(() => {
    return orgutListesi;
  }, [orgutListesi]);

  const rows = useMemo<DestekSatiri[]>(() => {
    if (!submittedInput) return [];

    const hesapInput = submittedInput;
    const o = BUZAGI_DESTEGI_CONFIG.ilaveOranlar;
    const satirlar: DestekSatiri[] = [];

    const ekle = (key: string, ad: string, oran: number, hakEdisAdet: number) => {
      const uygunAdet = Math.max(0, hakEdisAdet);
      const birim = Math.round(temelDestek * oran);
      satirlar.push({
        key,
        ad,
        oran,
        hakEdisAdet: uygunAdet,
        birimTutar: birim,
        toplamTutar: birim * uygunAdet,
      });
    };

    const hesapToplamBuzagi = Math.max(0, hesapInput.disiBuzagi) + Math.max(0, hesapInput.erkekBuzagi);
    const hesapAileIsletmesiUygun = hesapInput.toplamBuyukbas <= BUZAGI_DESTEGI_CONFIG.aileIsletmesiMaksimumBuyukbas;
    const hesapKadinVeyaGencUygun = hesapInput.cinsiyet === 'kadin' || hesapInput.yasGrubu === 'alti';

    const aileAdedi = hesapAileIsletmesiUygun
      ? Math.min(hesapToplamBuzagi, BUZAGI_DESTEGI_CONFIG.aileIsletmesiMaksimumBuzagi)
      : 0;

    const suniAdet = hesapInput.suniTohumlamaVeyaEmbriyo ? normalizeCount(hesapInput.suniTohumlamaSayisi, hesapToplamBuzagi) : 0;
    const yerliAdet = hesapInput.yerliSperma ? normalizeCount(hesapInput.yerliSpermaSayisi, hesapToplamBuzagi) : 0;
    const sutBesiAdet = hesapInput.sutBesiBolgesi ? normalizeCount(hesapInput.sutBesiBolgesiSayisi, hesapToplamBuzagi) : 0;

    const soyAbAdet = hesapInput.soyKutuguVar && hesapInput.soyKutuguSinifi === 'ab' ? normalizeCount(hesapInput.soyKutuguAbSayisi, hesapToplamBuzagi) : 0;
    const soyCAdet = hesapInput.soyKutuguVar && hesapInput.soyKutuguSinifi === 'c' ? normalizeCount(hesapInput.soyKutuguCSayisi, hesapToplamBuzagi) : 0;

    const genomikAdet = hesapInput.soyKutuguVar && hesapInput.soyKutuguSinifi === 'ab' && hesapInput.genomikTest
      ? normalizeCount(hesapInput.genomikTestDisiBuzagiSayisi, hesapInput.disiBuzagi)
      : 0;

    const ariAdet = hesapInput.ariIsletme ? normalizeCount(hesapInput.ariIsletmeDisiBuzagiSayisi, hesapInput.disiBuzagi) : 0;
    const abOnayAdet = hesapInput.abOnayliIsletme ? normalizeCount(hesapInput.abOnayliDisiBuzagiSayisi, hesapInput.disiBuzagi) : 0;

    ekle('temel', 'Temel Buzağı Desteği', 1, hesapToplamBuzagi);
    ekle('aile', '0-20 Baş Aile İşletmesi İlavesi', o.aileIsletmesi, aileAdedi);
    ekle('kadin_genc', 'Kadın veya 41 Yaşından Gün Almamış Genç Üretici', o.kadinVeyaGenc, hesapKadinVeyaGencUygun ? hesapToplamBuzagi : 0);
    ekle('planli', 'Planlı Üretim (Süt/Besi Havzası)', o.planliUretim, sutBesiAdet);
    ekle('orgut', '1. Derece Tarımsal Örgüt Üyeliği', o.birinciDereceOrgut, hesapInput.birinciDereceOrgut ? hesapToplamBuzagi : 0);
    ekle('suni', 'Suni Tohumlama / Embriyo Transferi', o.suniTohumlamaVeyaEmbriyo, suniAdet);
    ekle('yerli', 'Yerli Sperma', o.yerliSperma, yerliAdet);
    ekle('soy_ab', 'Soy Kütüğü A-B Sınıfı İlavesi', o.soyKutuguAB, soyAbAdet);
    ekle('soy_c', 'Soy Kütüğü C Sınıfı İlavesi', o.soyKutuguC, soyCAdet);
    ekle('genomik', 'Buzağı Genomik Seleksiyon Desteği', o.genomikTest, genomikAdet);
    ekle('ari', 'Ari İşletmede Doğan Dişi Buzağı', o.ariIsletmeDisiBuzagi, ariAdet);
    ekle('ab_onay', 'AB Onaylı İşletmede Doğan Dişi Buzağı', o.abOnayliIsletmeDisiBuzagi, abOnayAdet);

    return satirlar;
  }, [
    submittedInput,
    temelDestek,
  ]);

  const toplamDestekTutari = rows.reduce((sum, row) => sum + row.toplamTutar, 0);
  const hesaplananToplamBuzagi = submittedInput
    ? Math.max(0, submittedInput.disiBuzagi) + Math.max(0, submittedInput.erkekBuzagi)
    : 0;

  return (
    <Layout>
      <Seo
        title={`Buzağı Destekleme Hesaplaması (${BUZAGI_DESTEGI_CONFIG.year}) | Şartlar ve İlave Destekler`}
        description="Buzağı destekleme hesaplamasını temel destek ve ilave oranlarla yapın. 4 ay yaşama şartı, TÜRKVET/VETBİS kayıtları, başvuru dönemleri ve ilave destek kriterlerini tek sayfada inceleyin."
        canonical="https://tarimimar.com.tr/buzagi-destegi-hesaplama/"
        url="https://tarimimar.com.tr/buzagi-destegi-hesaplama/"
        type="website"
        keywords="buzağı destekleme hesaplama, buzağı desteği şartları, 2025 buzağı desteği, TÜRKVET VETBİS, hayvancılık destekleme modeli, malak desteği"
        jsonLd={{
          '@context': 'https://schema.org',
          '@graph': [
            {
              '@type': 'WebApplication',
              name: 'Buzağı Destekleme Hesaplaması',
              applicationCategory: 'BusinessApplication',
              operatingSystem: 'Android, iOS, Web Browser',
              url: 'https://tarimimar.com.tr/buzagi-destegi-hesaplama/',
              description: 'Buzağı ve malak destekleme tutarını temel ve ilave kriterlere göre hesaplama aracı.',
              offers: {
                '@type': 'Offer',
                price: '0',
                priceCurrency: 'TRY',
              },
            },
            {
              '@type': 'Article',
              headline: 'Buzağı destekleme modeli ve ilave destek kriterleri',
              description: 'Yönlendirici ve verimlilik esaslı hayvancılık destekleme modelinde buzağı destekleri, ilave oranlar ve başvuru dönemleri.',
              inLanguage: 'tr-TR',
              mainEntityOfPage: 'https://tarimimar.com.tr/buzagi-destegi-hesaplama/',
            },
            {
              '@type': 'FAQPage',
              mainEntity: [
                {
                  '@type': 'Question',
                  name: 'Buzağı desteği için temel şartlar nelerdir?',
                  acceptedAnswer: {
                    '@type': 'Answer',
                    text: 'Desteklemeden yararlanacak buzağı/malakların yurtiçinde doğmuş, küpelenip TÜRKVET sistemine kayıtlı, programlı aşıları yapılmış ve VETBİS kayıtları tamamlanmış, en az 4 ay (120 gün) yaşamış olması gerekir.',
                  },
                },
                {
                  '@type': 'Question',
                  name: '2025 yılı temel destek tutarı ne kadar?',
                  acceptedAnswer: {
                    '@type': 'Answer',
                    text: '2025 yılı için temel destek buzağıda 1.400 TL/baş, malakta 2.800 TL/baş olarak uygulanır.',
                  },
                },
                {
                  '@type': 'Question',
                  name: 'Ari işletmelerde doğan dişi buzağı için ilave destek var mı?',
                  acceptedAnswer: {
                    '@type': 'Answer',
                    text: 'Evet. Ari işletmede doğan dişi buzağı ve dişi malaklar için temel desteğe ilave %400 destek uygulanır.',
                  },
                },
              ],
            },
          ],
        }}
      />

      <Head>
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="format-detection" content="telephone=no" />
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
      </Head>

      <Page>
        <Container>
          <Card>
            <Title>🐄 Buzağı Destekleme Hesaplaması ({BUZAGI_DESTEGI_CONFIG.year})</Title>
            <Subtitle>
              Hayvancılık destekleme modelinde verimlilik ve sürdürülebilirlik odaklı kriterler esas alınır. Bu hesaplama aracı,
              <strong> temel destek</strong> ve uygun ilave oranları birlikte değerlendirerek tahmini destek tutarını gösterir.
            </Subtitle>
            <MetaRow>Temel destek tutarı: <strong>{formatCurrency(temelDestek)}</strong></MetaRow>
            <MetaRow>
              Uygunluk için buzağı/malakların en az <strong>120 gün yaşamış</strong>, programlı aşıları yapılmış ve
              TÜRKVET + VETBİS kayıtlarının tamamlanmış olması gerekir.
            </MetaRow>
          </Card>

          <Card>
            <Grid>
              <Field>
                İşletmedeki toplam sığır (buzağı dahil) (baş)
                <Input
                  type="number"
                  min={0}
                  inputMode="numeric"
                  value={toInputValue(input.toplamBuyukbas)}
                  onChange={(event) => setInput((prev) => ({ ...prev, toplamBuyukbas: Number(event.target.value || 0) }))}
                />
              </Field>

              <Field>
                Dişi buzağı sayısı
                <Input
                  type="number"
                  min={0}
                  inputMode="numeric"
                  value={toInputValue(input.disiBuzagi)}
                  onChange={(event) => setInput((prev) => ({ ...prev, disiBuzagi: Number(event.target.value || 0) }))}
                />
              </Field>

              <Field>
                Erkek buzağı sayısı
                <Input
                  type="number"
                  min={0}
                  inputMode="numeric"
                  value={toInputValue(input.erkekBuzagi)}
                  onChange={(event) => setInput((prev) => ({ ...prev, erkekBuzagi: Number(event.target.value || 0) }))}
                />
              </Field>

              <Field>
                İşletme sahibi cinsiyeti
                <Select value={input.cinsiyet} onChange={(event) => setInput((prev) => ({ ...prev, cinsiyet: event.target.value as 'erkek' | 'kadin' | '' }))}>
                  <option value="">Seçiniz</option>
                  <option value="erkek">Erkek</option>
                  <option value="kadin">Kadın</option>
                </Select>
              </Field>

              <Field>
                İşletme sahibi yaş grubu (cinsiyetten bağımsız genç üretici kontrolü)
                <Select
                  value={input.yasGrubu}
                  onChange={(event) =>
                    setInput((prev) => ({
                      ...prev,
                      yasGrubu: event.target.value === 'alti' ? 'alti' : 'ustu',
                    }))
                  }
                >
                  <option value="alti">41 yaş altı</option>
                  <option value="ustu">41 yaş üstü</option>
                </Select>
              </Field>
            </Grid>

            <CheckGrid>
              <Check>
                <RowInline>
                  <input
                    type="checkbox"
                    checked={input.birinciDereceOrgut}
                    onChange={(event) => setInput((prev) => ({ ...prev, birinciDereceOrgut: event.target.checked }))}
                  />
                  1. derece tarımsal örgüt üyesiyim
                  <SecondaryButton type="button" onClick={loadOrgutListesi}>Hangileri?</SecondaryButton>
                </RowInline>
              </Check>

              <Check>
                <RowInline>
                  <input
                    type="checkbox"
                    checked={input.suniTohumlamaVeyaEmbriyo}
                    onChange={(event) =>
                      setInput((prev) => ({
                        ...prev,
                        suniTohumlamaVeyaEmbriyo: event.target.checked,
                        suniTohumlamaSayisi: event.target.checked ? prev.suniTohumlamaSayisi : 0,
                      }))
                    }
                  />
                  Suni tohumlama / embriyo transferi
                </RowInline>
              </Check>

              {input.suniTohumlamaVeyaEmbriyo && (
                <Field>
                  Suni tohumlamadan doğan buzağı sayısı
                  <Input
                    type="number"
                    min={0}
                    inputMode="numeric"
                    value={toInputValue(input.suniTohumlamaSayisi)}
                    onChange={(event) => setInput((prev) => ({ ...prev, suniTohumlamaSayisi: Number(event.target.value || 0) }))}
                  />
                </Field>
              )}

              <Check>
                <RowInline>
                  <input
                    type="checkbox"
                    checked={input.yerliSperma}
                    onChange={(event) =>
                      setInput((prev) => ({
                        ...prev,
                        yerliSperma: event.target.checked,
                        yerliSpermaSayisi: event.target.checked ? prev.yerliSpermaSayisi : 0,
                      }))
                    }
                  />
                  Yerli sperma
                </RowInline>
              </Check>

              {input.yerliSperma && (
                <Field>
                  Yerli spermadan doğan buzağı sayısı
                  <Input
                    type="number"
                    min={0}
                    inputMode="numeric"
                    value={toInputValue(input.yerliSpermaSayisi)}
                    onChange={(event) => setInput((prev) => ({ ...prev, yerliSpermaSayisi: Number(event.target.value || 0) }))}
                  />
                </Field>
              )}

              <Check>
                <RowInline>
                  <input
                    type="checkbox"
                    checked={input.sutBesiBolgesi}
                    onChange={(event) =>
                      setInput((prev) => ({
                        ...prev,
                        sutBesiBolgesi: event.target.checked,
                        sutBesiBolgesiSayisi: event.target.checked ? prev.sutBesiBolgesiSayisi : 0,
                      }))
                    }
                  />
                  Süt veya besi bölgesi
                </RowInline>
              </Check>

              {input.sutBesiBolgesi && (
                <Field>
                  Sütçü/etçi/kombine ırk ve melezi buzağı sayısı
                  <Input
                    type="number"
                    min={0}
                    inputMode="numeric"
                    value={toInputValue(input.sutBesiBolgesiSayisi)}
                    onChange={(event) => setInput((prev) => ({ ...prev, sutBesiBolgesiSayisi: Number(event.target.value || 0) }))}
                  />
                </Field>
              )}

              <Check>
                <RowInline>
                  <input
                    type="checkbox"
                    checked={input.soyKutuguVar}
                    onChange={(event) =>
                      setInput((prev) => ({
                        ...prev,
                        soyKutuguVar: event.target.checked,
                        soyKutuguSinifi: event.target.checked ? prev.soyKutuguSinifi : null,
                        soyKutuguAbSayisi: event.target.checked ? prev.soyKutuguAbSayisi : 0,
                        soyKutuguCSayisi: event.target.checked ? prev.soyKutuguCSayisi : 0,
                        genomikTest: event.target.checked ? prev.genomikTest : false,
                        genomikTestDisiBuzagiSayisi: event.target.checked ? prev.genomikTestDisiBuzagiSayisi : 0,
                      }))
                    }
                  />
                  İşletme soy kütüğü kaydı var
                </RowInline>
              </Check>

              {input.soyKutuguVar && (
                <Field>
                  Soy kütüğü sınıfı
                  <Select
                    value={input.soyKutuguSinifi || ''}
                    onChange={(event) =>
                      setInput((prev) => ({
                        ...prev,
                        soyKutuguSinifi: event.target.value === 'ab' || event.target.value === 'c' ? (event.target.value as SoyKutuguSinifi) : null,
                        genomikTest: event.target.value === 'ab' ? prev.genomikTest : false,
                        genomikTestDisiBuzagiSayisi: event.target.value === 'ab' ? prev.genomikTestDisiBuzagiSayisi : 0,
                      }))
                    }
                  >
                    <option value="">Seçiniz</option>
                    <option value="ab">Test A-B</option>
                    <option value="c">Test C</option>
                  </Select>
                </Field>
              )}

              {input.soyKutuguVar && input.soyKutuguSinifi === 'ab' && (
                <>
                  <Field>
                    Test A-B buzağı sayısı
                    <Input
                      type="number"
                      min={0}
                      inputMode="numeric"
                      value={toInputValue(input.soyKutuguAbSayisi)}
                      onChange={(event) => setInput((prev) => ({ ...prev, soyKutuguAbSayisi: Number(event.target.value || 0) }))}
                    />
                  </Field>

                  <Check>
                    <RowInline>
                      <input
                        type="checkbox"
                        checked={input.genomikTest}
                        onChange={(event) =>
                          setInput((prev) => ({
                            ...prev,
                            genomikTest: event.target.checked,
                            genomikTestDisiBuzagiSayisi: event.target.checked ? prev.genomikTestDisiBuzagiSayisi : 0,
                          }))
                        }
                      />
                      Genomik test
                    </RowInline>
                  </Check>

                  {input.genomikTest && (
                    <Field>
                      Genomik test yapılan dişi buzağı sayısı
                      <Input
                        type="number"
                        min={0}
                        inputMode="numeric"
                        value={toInputValue(input.genomikTestDisiBuzagiSayisi)}
                        onChange={(event) => setInput((prev) => ({ ...prev, genomikTestDisiBuzagiSayisi: Number(event.target.value || 0) }))}
                      />
                    </Field>
                  )}
                </>
              )}

              {input.soyKutuguVar && input.soyKutuguSinifi === 'c' && (
                <Field>
                  Test C buzağı sayısı
                  <Input
                    type="number"
                    min={0}
                    inputMode="numeric"
                    value={toInputValue(input.soyKutuguCSayisi)}
                    onChange={(event) => setInput((prev) => ({ ...prev, soyKutuguCSayisi: Number(event.target.value || 0) }))}
                  />
                </Field>
              )}

              <Check>
                <RowInline>
                  <input
                    type="checkbox"
                    checked={input.ariIsletme}
                    onChange={(event) =>
                      setInput((prev) => ({
                        ...prev,
                        ariIsletme: event.target.checked,
                        ariIsletmeDisiBuzagiSayisi: event.target.checked ? prev.ariIsletmeDisiBuzagiSayisi : 0,
                      }))
                    }
                  />
                  Ari işletme
                </RowInline>
              </Check>

              {input.ariIsletme && (
                <Field>
                  Ari işletmede doğan dişi buzağı sayısı
                  <Input
                    type="number"
                    min={0}
                    inputMode="numeric"
                    value={toInputValue(input.ariIsletmeDisiBuzagiSayisi)}
                    onChange={(event) => setInput((prev) => ({ ...prev, ariIsletmeDisiBuzagiSayisi: Number(event.target.value || 0) }))}
                  />
                </Field>
              )}

              <Check>
                <RowInline>
                  <input
                    type="checkbox"
                    checked={input.abOnayliIsletme}
                    onChange={(event) =>
                      setInput((prev) => ({
                        ...prev,
                        abOnayliIsletme: event.target.checked,
                        abOnayliDisiBuzagiSayisi: event.target.checked ? prev.abOnayliDisiBuzagiSayisi : 0,
                      }))
                    }
                  />
                  AB onaylı işletme
                </RowInline>
              </Check>

              {input.abOnayliIsletme && (
                <Field>
                  AB onaylı işletmede doğan dişi buzağı sayısı
                  <Input
                    type="number"
                    min={0}
                    inputMode="numeric"
                    value={toInputValue(input.abOnayliDisiBuzagiSayisi)}
                    onChange={(event) => setInput((prev) => ({ ...prev, abOnayliDisiBuzagiSayisi: Number(event.target.value || 0) }))}
                  />
                </Field>
              )}
            </CheckGrid>

            <MetaRow>
              Kadın/Genç uygunluğu (her yaştan kadın veya 41 yaş altı): <strong>{kadinVeyaGencUygun ? 'Uygun' : 'Uygun değil'}</strong>
              {' · '}
              Aile işletmesi uygunluğu: <strong>{aileIsletmesiUygun ? 'Uygun' : 'Uygun değil'}</strong>
            </MetaRow>
            <MetaRow>
              Aile işletmesi desteği, destek yılı son iş günü itibariyle işletmede en fazla 20 baş sığır (buzağı dahil) ve en fazla 10 baş buzağı için uygulanır.
            </MetaRow>

            <FormActions>
              <PrimaryButton type="button" onClick={() => setSubmittedInput({ ...input })}>
                Destek Hesapla
              </PrimaryButton>
            </FormActions>

            {submittedInput && (
              <>
                <Summary style={{ marginTop: '14px' }}>
                  <SummaryBox>
                    <SummaryLabel>Toplam buzağı</SummaryLabel>
                    <SummaryValue>{hesaplananToplamBuzagi}</SummaryValue>
                  </SummaryBox>
                  <SummaryBox>
                    <SummaryLabel>Temel destek tutarı</SummaryLabel>
                    <SummaryValue>{formatCurrency(temelDestek)}</SummaryValue>
                  </SummaryBox>
                  <SummaryBox>
                    <SummaryLabel>Toplam destek</SummaryLabel>
                    <SummaryValue>{formatCurrency(toplamDestekTutari)}</SummaryValue>
                  </SummaryBox>
                </Summary>

                <TableWrap>
                  <Table>
                    <thead>
                      <tr>
                        <th>Destek kalemi</th>
                        <th>Oran</th>
                        <th>Hak ediş adedi</th>
                        <th>Birim tutar</th>
                        <th>Toplam</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map((row) => (
                        <tr key={row.key}>
                          <td>{row.ad}</td>
                          <td>%{Math.round(row.oran * 100)}</td>
                          <td>{row.hakEdisAdet}</td>
                          <td>{formatCurrency(row.birimTutar)}</td>
                          <td>{formatCurrency(row.toplamTutar)}</td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot>
                      <tr>
                        <td colSpan={4}>Genel Toplam</td>
                        <td>{formatCurrency(toplamDestekTutari)}</td>
                      </tr>
                    </tfoot>
                  </Table>
                </TableWrap>
              </>
            )}
          </Card>

          <Card>
            <InfoTitle>Hayvancılık Destekleme Modeli ve Buzağı Desteği Özeti</InfoTitle>
            <InfoText>
              Hayvancılık destekleme modelinde yönlendirici ve verimlilik esaslı kriterlerle işletmelerin ekonomik olarak güçlendirilmesi,
              üretim faaliyetlerinin sürdürülebilir hale getirilmesi hedeflenmektedir. Doğan yavru üzerinden kurgulanan yaklaşım ile
              üreme verimliliğinin artırılması, yerli üretimin teşvik edilmesi ve ithalat baskısının azaltılması amaçlanır.
            </InfoText>

            <InfoSubTitle>Temel koşullar</InfoSubTitle>
            <InfoList>
              <li>Yurtiçinde doğum ve küpeleme sonrası TÜRKVET kaydı bulunmalıdır.</li>
              <li>Bakanlık programlı aşıları yapılmalı ve VETBİS kayıtları tamamlanmalıdır.</li>
              <li>Buzağı/malak en az 4 ay (120 gün) yaşamış olmalıdır.</li>
              <li>2025 temel destek tutarı: <InfoStrong>Buzağı 1.400 TL/baş</InfoStrong>, <InfoStrong>Malak 2.800 TL/baş</InfoStrong>.</li>
            </InfoList>

            <InfoSubTitle>İlave destekler (özet)</InfoSubTitle>
            <InfoList>
              {ILAVE_DESTEK_KRITERLERI.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </InfoList>

            <InfoSubTitle>Başvuru dönemleri ve başvuru şekli</InfoSubTitle>
            <InfoText>
              Destekleme yılına ait doğum tarih aralığı içinde doğan ve temel koşulları sağlayan buzağılar için başvurular iki dönem halinde
              yapılır. Başvurular bireysel olarak İl/İlçe Müdürlüklerine veya üyesi olunan Birlik/Kooperatif üzerinden gerçekleştirilebilir.
            </InfoText>
            <InfoList>
              <li>1. dönem başlangıç: <InfoStrong>01.09.2025</InfoStrong></li>
              <li>2. dönem aralığı: <InfoStrong>01.04.2026 - 12.06.2026</InfoStrong></li>
            </InfoList>

            <InfoSubTitle>Destek türü / koşullar detay tablosu</InfoSubTitle>
            <DetailTableWrap>
              <DetailTable>
                <thead>
                  <tr>
                    <th>Destek türü</th>
                    <th>Tutar</th>
                    <th>Koşullar</th>
                  </tr>
                </thead>
                <tbody>
                  {DESTEK_DETAY_SATIRLARI.map((satir) => (
                    <tr key={satir.destekTuru}>
                      <td><InfoStrong>{satir.destekTuru}</InfoStrong></td>
                      <td>{satir.tutar}</td>
                      <td>
                        <ul>
                          {satir.kosullar.map((kosul) => (
                            <li key={kosul}>{kosul}</li>
                          ))}
                        </ul>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </DetailTable>
            </DetailTableWrap>

            <InfoSubTitle>Başvuru tarihleri (detay)</InfoSubTitle>
            <InfoList>
              {BASVURU_DONEMI_BILGILERI.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </InfoList>

            <InfoSubTitle>Başvuru yeri / şekli</InfoSubTitle>
            <InfoList>
              {BASVURU_YERI_SEKLI.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </InfoList>
          </Card>

        </Container>
      </Page>

      {orgutModalOpen && (
        <ModalOverlay>
          <ModalContent>
            <ModalHeader>
              <h3 style={{ margin: 0 }}>1. Derece Tarımsal Örgüt Listesi</h3>
              <SecondaryButton type="button" onClick={() => setOrgutModalOpen(false)}>Kapat</SecondaryButton>
            </ModalHeader>

            <MetaRow>
              Tüm iller için sonuçlar
            </MetaRow>

            {orgutListesiLoading && <MetaRow>Liste yükleniyor...</MetaRow>}
            {orgutListesiError && <MetaRow>{orgutListesiError}</MetaRow>}

            {!orgutListesiLoading && !orgutListesiError && (
              <OrgutList>
                {filteredOrgutListesi.length === 0 ? (
                  <MetaRow>Kayıt bulunamadı.</MetaRow>
                ) : (
                  filteredOrgutListesi.map((item, index) => (
                    <OrgutItem key={`${item.il}-${item.ilce}-${item.orgut}-${index}`}>
                      <strong>{item.il}</strong> / {item.ilce} — {item.orgut}
                    </OrgutItem>
                  ))
                )}
              </OrgutList>
            )}
          </ModalContent>
        </ModalOverlay>
      )}
    </Layout>
  );
}
