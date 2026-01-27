import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import Seo from '../components/Seo';
import Layout from '../components/Layout';
import styled from 'styled-components';
import axios from 'axios';

// Dynamic Map import (client-side only)
const DynamicMap = dynamic(() => import('../components/HavzaHaritasi'), {
  ssr: false,
  loading: () => <div style={{ height: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f8fafc', borderRadius: '8px' }}>Harita yükleniyor...</div>
});

interface UrunSecimi {
  urun: string;
  dekar: number;
  uretimTipi?: 'acikta' | 'ortualti';
  sulamaTipi?: 'kuru' | 'sulu';
  destekTipi?: 'yok' | 'organik' | 'iyiTarim';
  sertifikaliTohum: boolean;
  yerliSertifikaliTohum: boolean;
  katiOrganikGubre: boolean;
  organikTarim: {
    urunGrubu?: 'birinci_kategori' | 'ikinci_kategori' | 'ucuncu_kategori';
    sertifikaTuru: 'bireysel' | 'grup';
  };
  iyiTarim: {
    urunGrubu?: 'birinci_kategori' | 'ikinci_kategori' | 'ucuncu_kategori';
    uretimTipi: 'ortualti' | 'acikta' | null;
    sertifikaTuru: 'bireysel' | 'grup';
  };
}

interface HesaplamaResponseDetaylar {
  temel_destek: number;
  planli_uretim: number;
  genclik_ilavesi: number;
  sut_havzasi_ilavesi: number;
  su_kisiti: number;
  sertifikali_tohum: number;
  yerli_sertifikali_tohum: number;
  organik_tarim: number;
  iyi_tarim: number;
  gubre: number;
  toplam: number;
}

interface HesaplamaResponse {
  uygun: boolean;
  mesaj: string;
  detaylar: HesaplamaResponseDetaylar;
}

// Styled Components
const PageOuter = styled.main`
  width: 100%;
`;

const Container = styled.div`
  display: flex;
  flex-direction: column;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  
  @media (max-width: 768px) {
    padding: 15px;
  }
`;

const Title = styled.h1`
  margin: 0 0 24px;
  font-size: 28px;
  color: #1e293b;
  
  @media (max-width: 768px) {
    font-size: 24px;
    text-align: center;
  }
`;

const FormSection = styled.section`
  padding: 24px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
  
  @media (max-width: 768px) {
    padding: 16px;
  }
`;

const SectionTitle = styled.h2`
  margin: 0 0 16px;
  font-size: 18px;
  color: #374151;
  font-weight: 600;
`;

const UrunRow = styled.div`
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  align-items: center;
  flex-wrap: wrap;
  
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: stretch;
  }
`;

const Select = styled.select`
  flex: 1;
  min-width: 220px;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  
  &:focus {
    outline: none;
    border-color: #059669;
    box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.1);
  }
  
  @media (max-width: 768px) {
    font-size: 16px;
  }
`;

const Input = styled.input`
  flex: 0 0 120px;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #059669;
    box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.1);
  }
  
  @media (max-width: 768px) {
    font-size: 16px;
    flex: 1;
  }
`;

const Button = styled.button`
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  
  @media (max-width: 768px) {
    padding: 14px 20px;
    font-size: 16px;
  }
`;

const AddButton = styled(Button)`
  background: #059669;
  color: white;
  
  &:hover {
    background: #047857;
  }
`;

const RemoveButton = styled(Button)`
  background: #dc2626;
  color: white;
  flex-shrink: 0;
  
  &:hover {
    background: #b91c1c;
  }
  
  @media (max-width: 768px) {
    width: 100%;
  }
`;

const CalculateButton = styled(Button)`
  background: #2563eb;
  color: white;
  font-size: 16px;
  padding: 16px 32px;
  
  &:hover {
    background: #1d4ed8;
  }
  
  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const CheckboxGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
`;

const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  cursor: pointer;
  
  input[type="checkbox"] {
    width: 18px;
    height: 18px;
    accent-color: #059669;
  }
  
  @media (max-width: 768px) {
    font-size: 16px;
    
    input[type="checkbox"] {
      width: 20px;
      height: 20px;
    }
  }
`;

const SubCheckboxGroup = styled.div`
  margin-left: 26px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  
  @media (max-width: 768px) {
    margin-left: 28px;
  }
`;

const ResultSection = styled(FormSection)`
  background: #f8fafc;
  border-color: #059669;
`;

const ResultTable = styled.div`
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  
  @media (max-width: 768px) {
    gap: 12px;
  }
`;

const ResultRow = styled.div`
  display: contents;
  
  &:nth-child(even) {
    background: rgba(5, 150, 105, 0.05);
  }
`;

const ResultLabel = styled.div`
  padding: 8px 0;
  font-weight: 500;
  
  @media (max-width: 768px) {
    padding: 12px 0;
  }
`;

const ResultValue = styled.div`
  padding: 8px 0;
  font-weight: 600;
  text-align: right;
  color: #059669;
  
  @media (max-width: 768px) {
    padding: 12px 0;
  }
`;

const ErrorMessage = styled.div`
  background: #fee2e2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 20px;
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid #f3f4f6;
  border-top: 2px solid #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 8px;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

// Ürün verileri - 2026 yılı destek listesine (MD) göre sıralanmış ve gruplanmış
type UrunDropdownGrup = {
  label: string;
  urunler: string[];
};

const URUN_DROPDOWN_GRUPLARI: UrunDropdownGrup[] = [
  {
    label: '1. Grup Yem Bitkileri',
    urunler: [
      'Fiğ',
      'Burçak',
      'Mürdümük',
      'Hayvan Pancarı',
      'Yem Şalgamı',
      'Yem Bezelyesi',
      'Yem Baklası',
      'Üçgül',
      'İtalyan Çimi',
      'Yulaf (yem)',
      'Çavdar (yem)',
      'Tritikale (yem)'
    ]
  },
  {
    label: '2. Grup Yem Bitkileri',
    urunler: [
      'Yonca',
      'Korunga',
      'Yapay Çayır Mera',
      'Silajlık Mısır',
      'Silajlık Soya',
      'Sorgum Otu',
      'Sudan Otu',
      'Sorgum-Sudan Otu Melezi'
    ]
  },
  {
    label: '1. Kategori',
    urunler: ['Aspir', 'Mercimek', 'Nohut', 'Patates', 'Soğan (kuru)']
  },
  {
    label: '2. Kategori',
    urunler: ['Arpa', 'Buğday', 'Mısır (dane)']
  },
  {
    label: '3. Kategori',
    urunler: ['Ayçiçeği (yağlık)', 'Fındık', 'Kolza (kanola)', 'Fasulye (kuru)', 'Soya', 'Çay']
  },
  {
    label: '4. Kategori',
    urunler: ['Çeltik', 'Pamuk (kütlü)']
  },
  {
    label: 'Nadas',
    urunler: ['Nadas']
  },
  {
    label: 'Diğer',
    urunler: ['Diğer Ürünler']
  }
];

const GUBRE_DESTEK_BIRIM_TL = 99.2;

const ORGANIK_IYI_TARIM_KATEGORI_URUN_METIN = {
  birinci_kategori:
    'Acur, Ahududu, Alıç, Altınçilek, Altıntop, Armut, Avokado, Ayva, Badem, Bakla, Balkabağı, Bamya, Barbunya Fasulye, Barbunya Fasulye (kuru), Bergamot, Biber, Böğürtlen, Brokoli, Ceviz, Çay, Çilek, Dereotu, Domates, Dut, Elma, Enginar, Erik, Fasulye (kuru), Fasulye, Fındık, Gilaburu, Hıyar, Ispanak, İğde, İncir, Kabak, Kuşüzümü, Karnabahar, Karpuz, Kavun, Kayısı, Kereviz, Kestane, Kızılcık, Kiraz, Kivi, Kuşkonmaz, Kuzukulağı, Lahana, Limon, Mandalina, Mantar, Marul, Maydanoz, Meyve Fidanı, Sebze Fideleri, Muşmula, Muz, Nane, Nar, Nektarin, Örtü Altı Fidecilik, Palamut, Patlıcan, Pazı, Pepino, Pırasa, Portakal, Roka, Sarımsak, Semizotu, Soğan, Şalgam, Şeftali, Tere, Trabzon Hurması, Turp, Turunç, Üvez, Üzüm, Üzüm Kurutmalık, Üzüm Sofralık, Vişne, Yenidünya, Yerelması, Zerdali.',
  ikinci_kategori:
    'Adaçayı, Anason, Antep Fıstığı, Biberiye, Civanperçemi, Çemen, Çörekotu, Defne, Ebegümeci, Fesleğen (reyhan), Hünnap, Kekik, Isırganotu, Kantaron, Kimyon, Kişniş, Kuşburnu, Melissa, Mercanköşk, Rezene, Safran, Şerbetçiotu, Tarçın, Zahter, Zencefil, Zeytin.',
  ucuncu_kategori:
    'Ayçiçeği, Bakla (kuru), Bezelye, Börülce, Çeltik, Gül, Kenevir Lif, Keten Lif, Mercimek, Mürdümük, Nohut, Pamuk, Sarımsak (kuru), Soğan (kuru), Soya, Susam, Tütün, Yerfıstığı.'
} as const;

const parseKategoriUrunleri = (metin: string): string[] =>
  metin
    .trim()
    .replace(/\.$/, '')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);

const normalizeUrunKey = (urun: string): string =>
  urun
    .trim()
    .toLocaleLowerCase('tr-TR')
    .replace(/\.+$/, '')
    .replace(/\s+/g, ' ');

const ORGANIK_IYI_TARIM_KATEGORI_URUN_SET = {
  birinci_kategori: new Set(parseKategoriUrunleri(ORGANIK_IYI_TARIM_KATEGORI_URUN_METIN.birinci_kategori).map(normalizeUrunKey)),
  ikinci_kategori: new Set(parseKategoriUrunleri(ORGANIK_IYI_TARIM_KATEGORI_URUN_METIN.ikinci_kategori).map(normalizeUrunKey)),
  ucuncu_kategori: new Set(parseKategoriUrunleri(ORGANIK_IYI_TARIM_KATEGORI_URUN_METIN.ucuncu_kategori).map(normalizeUrunKey))
} as const;

const ORGANIK_IYI_TARIM_TUM_URUN_SET: Set<string> = (() => {
  const s = new Set<string>();
  ORGANIK_IYI_TARIM_KATEGORI_URUN_SET.birinci_kategori.forEach((v) => s.add(v));
  ORGANIK_IYI_TARIM_KATEGORI_URUN_SET.ikinci_kategori.forEach((v) => s.add(v));
  ORGANIK_IYI_TARIM_KATEGORI_URUN_SET.ucuncu_kategori.forEach((v) => s.add(v));
  return s;
})();

// Sertifikalı tohum kullanım desteği (STKD) - MD tablosuna göre
const SERTIFIKALI_TOHUM_URUN_METIN =
  'Arpa, Buğday, Çavdar, Çeltik, Fasulye (kuru), Tritikale, Yulaf, Aspir, Kolza (kanola), Susam, Korunga, Soya, Yer fıstığı, Yonca, Fiğ, Mercimek, Nohut, Yem bezelyesi, Patates';

// Yerli sertifikalı tohum kullanım desteği (YSTKD) - MD tablosuna göre
const YERLI_SERTIFIKALI_TOHUM_URUN_METIN = 'Ayçiçeği (yağlık), Mısır, Mısır (dane), Soya, Patates';

const SERTIFIKALI_TOHUM_URUN_SET = new Set(
  parseKategoriUrunleri(SERTIFIKALI_TOHUM_URUN_METIN)
    .concat(['Yulaf (yem)', 'Çavdar (yem)', 'Tritikale (yem)'])
    .map(normalizeUrunKey)
);

const YERLI_SERTIFIKALI_TOHUM_URUN_SET = new Set(
  parseKategoriUrunleri(YERLI_SERTIFIKALI_TOHUM_URUN_METIN).map(normalizeUrunKey)
);

type TarimsalOrgut = {
  il: string;
  ilce: string;
  orgut: string;
};

type YeniDestekSSSItem = {
  no: number;
  soru: string;
  cevap: string;
};

const ORGUT_LISTESI_DOSYA_YOLU = '/2025_birinci_derece_tarimsal_orgut_listesi';
const YENI_DESTEK_SORULAR_DOSYA_YOLU = '/yenidestek_sorular.md';

const YENI_DESTEK_KAYNAK_PDF_URL =
  'https://www.tarimorman.gov.tr/BUGEM/Belgeler/Tar%C4%B1m%20Havzalar%C4%B1/Sorularla%20Yeni%20Destek%20Modeli%20-%202026.pdf';

const DESTEKLEME_TEBLIGI_PDF_URL =
  'https://www.tarimorman.gov.tr/BUGEM/Belgeler/Tar%C4%B1m%20Havzalar%C4%B1/2024-39%20Bitkisel%20%C3%9Cretime%20Y%C3%B6nelik%20Desteklemeler%20ile%20Di%C4%9Fer%20Baz%C4%B1%20Tar%C4%B1msal%20Desteklemelere%20%C3%96deme%20Yap%C4%B1lmas%C4%B1na%20Dair%20Tebli%C4%9F%20(Tebli%C4%9F%20No%202024-39).pdf';

// Ek kaynaklar
const HAVZA_2026_URUN_DESENI_PDF_URL =
  'https://www.tarimorman.gov.tr/BUGEM/Belgeler/Tar%C4%B1m%20Havzalar%C4%B1/2025%20Y%C4%B1l%C4%B1%20Planlamaya%20Konu%20Havza%20%C3%9Cr%C3%BCn%20Deseni%20Listesi.pdf';

const URETIM_2026_DESTEK_BIRIM_FIATLARI_PDF_URL =
  'https://www.tarimorman.gov.tr/BUGEM/Belgeler/Tar%C4%B1m%20Havzalar%C4%B1/2026%20Y%C4%B1l%C4%B1%20Destekleme%20Birim%20Fiyatlar%C4%B1.pdf';

const parseOrgutListesiMarkdown = (md: string): TarimsalOrgut[] => {
  const lines = md.split(/\r?\n/).map((l) => l.trim());
  const rows: TarimsalOrgut[] = [];

  for (const line of lines) {
    if (!line.startsWith('|')) continue;
    // Header separator satırlarını atla
    if (line.includes('---')) continue;

    const parts = line
      .split('|')
      .map((p) => p.trim())
      .filter((p) => p.length > 0);

    // Beklenen: Sıra | İl | İlçe | Örgüt Adı
    if (parts.length < 4) continue;
    // Başlık satırıysa atla
    if (parts[0].toLocaleLowerCase('tr-TR') === 'sıra' || parts[1]?.toLocaleLowerCase('tr-TR') === 'il') continue;

    const il = (parts[1] || '').toString().trim();
    const ilce = (parts[2] || '').toString().trim();
    const orgut = (parts[3] || '').toString().trim();
    if (!il || !ilce || !orgut) continue;

    rows.push({ il, ilce, orgut });
  }

  return rows;
};

const parseYeniDestekSorularMarkdown = (md: string): YeniDestekSSSItem[] => {
  const lines = md.split(/\r?\n/);
  const items: YeniDestekSSSItem[] = [];

  let currentNo: number | null = null;
  let currentSoru = '';
  let currentCevapLines: string[] = [];

  const pushCurrent = () => {
    if (currentNo === null) return;
    const cevap = currentCevapLines.join('\n').trim();
    if (!currentSoru.trim() || !cevap) return;
    items.push({ no: currentNo, soru: currentSoru.trim(), cevap });
  };

  for (const rawLine of lines) {
    const line = rawLine.replace(/\s+$/, '');
    if (line.trim().startsWith('#')) continue;

    const qMatch = line.match(/^\s*(\d+)\.\s+(.+?)\s*$/);
    if (qMatch) {
      pushCurrent();
      currentNo = Number(qMatch[1]);
      currentSoru = qMatch[2];
      currentCevapLines = [];
      continue;
    }

    if (currentNo !== null) {
      currentCevapLines.push(line);
    }
  }

  pushCurrent();
  return items;
};

// Süt havzası illeri
const SUT_HAVZASI_ILLERI = [
  'Amasya', 'Bingöl', 'Bitlis', 'Çorum', 'Elâzığ', 'Erzincan', 
  'Erzurum', 'Muş', 'Tokat', 'Tunceli'
];

// Su kısıtı olan ilçeler
const SU_KISITI_ILCELERI = [
  { il: 'Aksaray', ilce: 'Merkez' },
  { il: 'Aksaray', ilce: 'Eskil' },
  { il: 'Aksaray', ilce: 'Gülağaç' },
  { il: 'Aksaray', ilce: 'Güzelyurt' },
  { il: 'Aksaray', ilce: 'Sultanhanı' },
  { il: 'Ankara', ilce: 'Bala' },
  { il: 'Ankara', ilce: 'Gölbaşı' },
  { il: 'Ankara', ilce: 'Haymana' },
  { il: 'Ankara', ilce: 'Şereflikoçhisar' },
  { il: 'Eskişehir', ilce: 'Alpu' },
  { il: 'Eskişehir', ilce: 'Beylikova' },
  { il: 'Eskişehir', ilce: 'Çifteler' },
  { il: 'Eskişehir', ilce: 'Mahmudiye' },
  { il: 'Eskişehir', ilce: 'Mihalıçcık' },
  { il: 'Eskişehir', ilce: 'Sivrihisar' },
  { il: 'Hatay', ilce: 'Kumlu' },
  { il: 'Hatay', ilce: 'Reyhanlı' },
  { il: 'Karaman', ilce: 'Ayrancı' },
  { il: 'Karaman', ilce: 'Merkez' },
  { il: 'Karaman', ilce: 'Kazımkarabekir' },
  { il: 'Kırşehir', ilce: 'Boztepe' },
  { il: 'Kırşehir', ilce: 'Mucur' },
  { il: 'Konya', ilce: 'Akören' },
  { il: 'Konya', ilce: 'Akşehir' },
  { il: 'Konya', ilce: 'Altınekin' },
  { il: 'Konya', ilce: 'Cihanbeyli' },
  { il: 'Konya', ilce: 'Çumra' },
  { il: 'Konya', ilce: 'Derbent' },
  { il: 'Konya', ilce: 'Doğanhisar' },
  { il: 'Konya', ilce: 'Emirgazi' },
  { il: 'Konya', ilce: 'Ereğli' },
  { il: 'Konya', ilce: 'Güneysınır' },
  { il: 'Konya', ilce: 'Halkapınar' },
  { il: 'Konya', ilce: 'Kadınhanı' },
  { il: 'Konya', ilce: 'Karapınar' },
  { il: 'Konya', ilce: 'Karatay' },
  { il: 'Konya', ilce: 'Kulu' },
  { il: 'Konya', ilce: 'Meram' },
  { il: 'Konya', ilce: 'Sarayönü' },
  { il: 'Konya', ilce: 'Selçuklu' },
  { il: 'Konya', ilce: 'Tuzlukçu' },
  { il: 'Mardin', ilce: 'Artuklu' },
  { il: 'Mardin', ilce: 'Derik' },
  { il: 'Mardin', ilce: 'Kızıltepe' },
  { il: 'Nevşehir', ilce: 'Acıgöl' },
  { il: 'Nevşehir', ilce: 'Derinkuyu' },
  { il: 'Nevşehir', ilce: 'Gülşehir' },
  { il: 'Niğde', ilce: 'Altunhisar' },
  { il: 'Niğde', ilce: 'Bor' },
  { il: 'Niğde', ilce: 'Çiftlik' },
  { il: 'Niğde', ilce: 'Merkez' },
  { il: 'Şanlıurfa', ilce: 'Viranşehir' }
];

export default function HavzaBazliDesteklemeModeliPage() {
  // State değişkenleri
  const [urunler, setUrunler] = useState<UrunSecimi[]>([
    {
      urun: '',
      dekar: 0,
      uretimTipi: 'acikta',
      sulamaTipi: 'kuru',
      destekTipi: 'yok',
      sertifikaliTohum: false,
      yerliSertifikaliTohum: false,
      katiOrganikGubre: false,
      organikTarim: { sertifikaTuru: 'bireysel' },
      iyiTarim: { uretimTipi: null, sertifikaTuru: 'bireysel' }
    }
  ]);
  const [gencCiftci, setGencCiftci] = useState(false);
  const [kadinCiftci, setKadinCiftci] = useState(false);
  const [orgutUyesi, setOrgutUyesi] = useState(false);
  const [orgutListesiGoster, setOrgutListesiGoster] = useState(false);
  const [tarimsalOrgutListesi, setTarimsalOrgutListesi] = useState<TarimsalOrgut[]>([]);
  const [tarimsalOrgutLoading, setTarimsalOrgutLoading] = useState(false);
  const [tarimsalOrgutError, setTarimsalOrgutError] = useState('');
  const [yeniDestekSSS, setYeniDestekSSS] = useState<YeniDestekSSSItem[]>([]);
  const [yeniDestekSSSLoading, setYeniDestekSSSLoading] = useState(false);
  const [yeniDestekSSSError, setYeniDestekSSSError] = useState('');
  const [organikModalGoster, setOrganikModalGoster] = useState(false);
  const [organikModalKategori, setOrganikModalKategori] = useState('');
  const [iyiTarimModalGoster, setIyiTarimModalGoster] = useState(false);
  const [iyiTarimModalKategori, setIyiTarimModalKategori] = useState('');
  const [uyariModalGoster, setUyariModalGoster] = useState(false);
  const [uyariModalBaslik, setUyariModalBaslik] = useState('');
  const [uyariModalMetin, setUyariModalMetin] = useState('');
  const [havzaData, setHavzaData] = useState<Record<string, Record<string, string[]>>>({});
  const [il, setIl] = useState('');
  const [ilce, setIlce] = useState('');
  const [loading, setLoading] = useState(false);
  const [sonuc, setSonuc] = useState<HesaplamaResponse | null>(null);
  const [hata, setHata] = useState('');
  const [gosterDigerIlceler, setGosterDigerIlceler] = useState(false);
  const [haritaUrunModalGoster, setHaritaUrunModalGoster] = useState(false);
  const [haritaUrunSecimi, setHaritaUrunSecimi] = useState('');
  const [haritaUrunSecimiDraft, setHaritaUrunSecimiDraft] = useState('');

  const gosterUyariModal = (baslik: string, metin: string) => {
    setUyariModalBaslik(baslik);
    setUyariModalMetin(metin);
    setUyariModalGoster(true);
  };

  const openOrgutListesiModal = async () => {
    if (!il) {
      window.alert('Lütfen önce il seçiniz.');
      setHata('Lütfen önce il seçin.');
      return;
    }

    setOrgutListesiGoster(true);

    // Zaten yüklüyse tekrar fetch etme
    if (tarimsalOrgutListesi.length > 0 || tarimsalOrgutLoading) return;

    setTarimsalOrgutLoading(true);
    setTarimsalOrgutError('');
    try {
      const res = await fetch(ORGUT_LISTESI_DOSYA_YOLU);
      if (!res.ok) {
        throw new Error(`Liste yüklenemedi (HTTP ${res.status})`);
      }
      const text = await res.text();
      const parsed = parseOrgutListesiMarkdown(text);
      setTarimsalOrgutListesi(parsed);
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : 'Liste yüklenemedi.';
      setTarimsalOrgutError(message);
    } finally {
      setTarimsalOrgutLoading(false);
    }
  };

  const openHaritaUrunModal = () => {
    setHaritaUrunSecimiDraft(haritaUrunSecimi);
    setHaritaUrunModalGoster(true);
  };

  const applyHaritaUrunSecimi = () => {
    const next = String(haritaUrunSecimiDraft || '');
    setHaritaUrunSecimi(next);
    setGosterDigerIlceler(Boolean(next));
    setHaritaUrunModalGoster(false);
  };

  const urunDigerMi = (urunAdi: string): boolean => {
    const key = normalizeUrunKey(urunAdi);
    return key === 'diğer ürünler' || key === 'diger urunler';
  };

  const kategoriUrunUyumluMu = (
    urunAdi: string,
    kategori: 'birinci_kategori' | 'ikinci_kategori' | 'ucuncu_kategori',
    destekAdi: 'Organik Tarım' | 'İyi Tarım'
  ): boolean => {
    if (!urunAdi || urunDigerMi(urunAdi)) return true;

    const izinliSet = ORGANIK_IYI_TARIM_KATEGORI_URUN_SET[kategori];
    const uyumluMu = izinliSet.has(normalizeUrunKey(urunAdi));
    if (uyumluMu) return true;

    const kategoriEtiketi =
      kategori === 'birinci_kategori'
        ? '1. Kategori'
        : kategori === 'ikinci_kategori'
          ? '2. Kategori'
          : '3. Kategori';

    gosterUyariModal(
      'Uygun ürün seçiniz',
      `${destekAdi} desteği için seçtiğiniz ${kategoriEtiketi} listesinde yer almayan ürün var:\n\n- ${urunAdi}\n\nLütfen destek hesabı yapmak istediğiniz ürünü bu kategori içindeki ürünlerden birini seçiniz.\nNot: "Diğer Ürünler" seçiliyse bu kontrol yapılmaz.`
    );
    return false;
  };

  const organikIyiTarimUrunUygunMu = (urunAdi: string, destekAdi: 'Organik Tarım' | 'İyi Tarım'): boolean => {
    if (!urunAdi) return false;
    if (urunDigerMi(urunAdi)) return true;

    const urunKey = normalizeUrunKey(urunAdi);
    if (ORGANIK_IYI_TARIM_TUM_URUN_SET.has(urunKey)) return true;

    gosterUyariModal(
      'Uygun ürün seçiniz',
      `${destekAdi} desteği için seçtiğiniz ürün destek listesinde yer almıyor:\n\n- ${urunAdi}\n\nLütfen Organik/İyi Tarım desteği hesaplamak istediğiniz ürünü destek kapsamındaki ürünlerden seçiniz.\nNot: "Diğer Ürünler" seçiliyse bu kontrol yapılmaz.`
    );
    return false;
  };

  const tohumUrunUyumluMu = (
    urunAdi: string,
    destekAdi: 'Sertifikalı Tohum' | 'Yerli Sertifikalı Tohum'
  ): boolean => {
    if (!urunAdi) return false;

    const urunKey = normalizeUrunKey(urunAdi);
    const izinliSet =
      destekAdi === 'Sertifikalı Tohum' ? SERTIFIKALI_TOHUM_URUN_SET : YERLI_SERTIFIKALI_TOHUM_URUN_SET;

    if (izinliSet.has(urunKey)) return true;

    gosterUyariModal(
      'Tohum desteği yok',
      `${destekAdi} Kullanım Desteği için seçtiğiniz ürün destek listesinde yer almıyor:\n\n- ${urunAdi}\n\nBu ürünlere tohum desteği verilmemektedir.`
    );
    return false;
  };

  const organikSeciliMi = urunler.some((u) => u.destekTipi === 'organik');

  // Organik tarım seçili değilse 1. derece örgüt üyeliğini sıfırla
  useEffect(() => {
    if (!organikSeciliMi && orgutUyesi) {
      setOrgutUyesi(false);
    }
  }, [organikSeciliMi, orgutUyesi]);

  // Ürün ekleme
  const urunEkle = () => {
    if (urunler.length >= 20) {
      setHata('En fazla 20 ürün ekleyebilirsiniz.');
      return;
    }
    setUrunler([
      ...urunler,
      {
        urun: '',
        dekar: 0,
        uretimTipi: 'acikta',
        sulamaTipi: 'kuru',
        destekTipi: 'yok',
        sertifikaliTohum: false,
        yerliSertifikaliTohum: false,
        katiOrganikGubre: false,
        organikTarim: { sertifikaTuru: 'bireysel' },
        iyiTarim: { uretimTipi: null, sertifikaTuru: 'bireysel' }
      }
    ]);
  };

  // Ürün silme
  const urunSil = (index: number) => {
    if (urunler.length > 1) {
      setUrunler(urunler.filter((_, i) => i !== index));
    }
  };

  // Havza verisi yükleme
  useEffect(() => {
    const loadHavzaData = async () => {
      try {
        const response = await fetch('/havza_urun_desen.json');
        if (!response.ok) throw new Error(`Havza verisi yüklenemedi (HTTP ${response.status})`);
        const data = await response.json();
        setHavzaData(data);
      } catch (error) {
        console.error('Havza verisi yüklenirken hata:', error);
        setHata('Konum verileri yüklenemedi. Lütfen sayfayı yenileyiniz.');
      }
    };
    
    loadHavzaData();
  }, []);

  // SSS (Yeni Destek Modeli) yükleme
  useEffect(() => {
    const loadSSS = async () => {
      setYeniDestekSSSLoading(true);
      setYeniDestekSSSError('');
      try {
        const res = await fetch(YENI_DESTEK_SORULAR_DOSYA_YOLU);
        if (!res.ok) throw new Error(`SSS yüklenemedi (HTTP ${res.status})`);
        const text = await res.text();
        const parsed = parseYeniDestekSorularMarkdown(text);
        setYeniDestekSSS(parsed);
      } catch (e: unknown) {
        const message = e instanceof Error ? e.message : 'SSS yüklenemedi.';
        setYeniDestekSSSError(message);
      } finally {
        setYeniDestekSSSLoading(false);
      }
    };

    void loadSSS();
  }, []);

  // Ürün güncelleme
  const urunGuncelle = (index: number, field: keyof UrunSecimi, value: string | number | boolean) => {
    const yeniUrunler = [...urunler];

    if (field === 'destekTipi') {
      const nextDestekTipi = value as UrunSecimi['destekTipi'];

      if (nextDestekTipi === 'organik') {
        const urunAdi = yeniUrunler[index]?.urun;
        if (!urunAdi) {
          setHata('Lütfen önce ürün seçiniz.');
          return;
        }
        if (!organikIyiTarimUrunUygunMu(urunAdi, 'Organik Tarım')) return;
      }

      if (nextDestekTipi === 'iyiTarim') {
        const urunAdi = yeniUrunler[index]?.urun;
        if (!urunAdi) {
          setHata('Lütfen önce ürün seçiniz.');
          return;
        }
        if (!organikIyiTarimUrunUygunMu(urunAdi, 'İyi Tarım')) return;
      }

      yeniUrunler[index] = {
        ...yeniUrunler[index],
        destekTipi: nextDestekTipi,
        organikTarim:
          nextDestekTipi === 'organik'
            ? { ...yeniUrunler[index].organikTarim, sertifikaTuru: yeniUrunler[index].organikTarim?.sertifikaTuru || 'bireysel', urunGrubu: undefined }
            : yeniUrunler[index].organikTarim,
        iyiTarim:
          nextDestekTipi === 'iyiTarim'
            ? {
                ...yeniUrunler[index].iyiTarim,
                uretimTipi: null,
                sertifikaTuru: yeniUrunler[index].iyiTarim?.sertifikaTuru || 'bireysel',
                urunGrubu: undefined
              }
            : yeniUrunler[index].iyiTarim
      };
      setUrunler(yeniUrunler);
      return;
    }

    // Ürün değiştiyse ve organik/iyi tarım seçili ama yeni ürün bu desteklerde yoksa otomatik kapat
    if (field === 'urun') {
      const nextUrun = String(value || '');
      const current = yeniUrunler[index];
      if (current?.destekTipi === 'organik' && !organikIyiTarimUrunUygunMu(nextUrun, 'Organik Tarım')) {
        yeniUrunler[index] = {
          ...current,
          urun: nextUrun,
          destekTipi: 'yok',
          katiOrganikGubre: false,
          organikTarim: { ...current.organikTarim, sertifikaTuru: current.organikTarim?.sertifikaTuru || 'bireysel', urunGrubu: undefined },
          iyiTarim: { ...current.iyiTarim, uretimTipi: null, sertifikaTuru: current.iyiTarim?.sertifikaTuru || 'bireysel', urunGrubu: undefined }
        };
        setUrunler(yeniUrunler);
        return;
      }
      if (current?.destekTipi === 'iyiTarim' && !organikIyiTarimUrunUygunMu(nextUrun, 'İyi Tarım')) {
        yeniUrunler[index] = {
          ...current,
          urun: nextUrun,
          destekTipi: 'yok',
          katiOrganikGubre: false,
          organikTarim: { ...current.organikTarim, sertifikaTuru: current.organikTarim?.sertifikaTuru || 'bireysel', urunGrubu: undefined },
          iyiTarim: { ...current.iyiTarim, uretimTipi: null, sertifikaTuru: current.iyiTarim?.sertifikaTuru || 'bireysel', urunGrubu: undefined }
        };
        setUrunler(yeniUrunler);
        return;
      }
    }

    yeniUrunler[index] = { ...yeniUrunler[index], [field]: value };
    setUrunler(yeniUrunler);
  };

  const formSelectedProducts = urunler.map((u) => u.urun).filter(Boolean) as string[];
  const selectedProductsForMap = formSelectedProducts.length > 0 ? formSelectedProducts : (haritaUrunSecimi ? [haritaUrunSecimi] : []);
  const haritaUrunModuAktif = formSelectedProducts.length === 0;

  const gubreDestegiSeciliMi = urunler.some((u) => u.katiOrganikGubre);

  const toggleKatiOrganikGubre = (index: number) => {
    const yeniUrunler = [...urunler];
    const current = yeniUrunler[index];
    if (!current) return;
    yeniUrunler[index] = { ...current, katiOrganikGubre: !current.katiOrganikGubre };
    setUrunler(yeniUrunler);
  };

  const toggleTohumSecimi = (index: number, alan: 'sertifikaliTohum' | 'yerliSertifikaliTohum') => {
    const mevcut = urunler[index]?.[alan];
    const next = !mevcut;

    const yeniUrunler = [...urunler];
    const current = yeniUrunler[index];
    if (!current) return;

    // Kapatma her zaman serbest
    if (!next) {
      yeniUrunler[index] = { ...current, [alan]: false };
      setUrunler(yeniUrunler);
      return;
    }

    const urunAdi = current.urun;
    const destekAdi = alan === 'sertifikaliTohum' ? 'Sertifikalı Tohum' : 'Yerli Sertifikalı Tohum';
    const digerAlan = alan === 'sertifikaliTohum' ? 'yerliSertifikaliTohum' : 'sertifikaliTohum';

    if (!urunAdi) {
      setHata('Lütfen önce ürün seçiniz.');
      return;
    }

    if (!tohumUrunUyumluMu(urunAdi, destekAdi)) return;

    // Aynı anda sadece biri seçilebilir: seçilen açılırken diğeri kapanır
    yeniUrunler[index] = { ...current, [alan]: true, [digerAlan]: false };
    setUrunler(yeniUrunler);
  };

  // Form validasyonu
  const validateForm = (): boolean => {
    if (!il || !ilce) {
      setHata('Lütfen il ve ilçe seçiniz.');
      return false;
    }

    for (const u of urunler) {
      const hasUrun = Boolean(u.urun);
      const hasDekar = Number(u.dekar) > 0;

      if (hasUrun && !hasDekar) {
        setHata('Seçtiğiniz ürün için dekar miktarı giriniz.');
        return false;
      }

      if (!hasUrun && hasDekar) {
        setHata('Dekar girdiniz ama ürün seçmediniz. Lütfen ürün seçiniz.');
        return false;
      }

      if (Number(u.dekar) > 9999) {
        setHata('Dekar değeri en fazla 9999 olabilir.');
        return false;
      }
    }
    
    const gecerliUrunler = urunler.filter(u => u.urun && u.dekar > 0);
    if (gecerliUrunler.length === 0) {
      setHata('Lütfen en az bir ürün ve dekar miktarı giriniz.');
      return false;
    }
    
    setHata('');

    for (const urunInfo of gecerliUrunler) {
      if (urunInfo.destekTipi === 'organik') {
        const kategori = urunInfo.organikTarim?.urunGrubu;
        if (!kategori) {
          setHata('Organik tarım seçtiğiniz ürün için ürün kategorisi seçiniz.');
          return false;
        }
        if (!kategoriUrunUyumluMu(urunInfo.urun, kategori, 'Organik Tarım')) return false;
      }

      if (urunInfo.destekTipi === 'iyiTarim') {
        const kategori = urunInfo.iyiTarim?.urunGrubu;
        if (!kategori) {
          setHata('İyi tarım seçtiğiniz ürün için ürün kategorisi seçiniz.');
          return false;
        }
        if (!kategoriUrunUyumluMu(urunInfo.urun, kategori, 'İyi Tarım')) return false;
      }

      if (urunInfo.sertifikaliTohum) {
        if (!tohumUrunUyumluMu(urunInfo.urun, 'Sertifikalı Tohum')) return false;
      }

      if (urunInfo.yerliSertifikaliTohum) {
        if (!tohumUrunUyumluMu(urunInfo.urun, 'Yerli Sertifikalı Tohum')) return false;
      }
    }

    return true;
  };

  // Herhangi bir üründe örtü altı seçili mi kontrol et
  const ortualtiSeciliMi = urunler.some(u => u.uretimTipi === 'ortualti');

  // KOBÜKS kaydı: bu hesaplayıcıda örtü altı seçildiyse otomatik varsayılır
  const kobuksKayitli = ortualtiSeciliMi;

  // Hesaplama işlemi
  const hesapla = async () => {
    if (!validateForm()) return;
    
    setLoading(true);
    setSonuc(null);
    
    try {
      // Use configured API URL or safe default
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://tarimimar.com.tr/api';
      
      const response = await axios.post(`${API_BASE_URL}/calculations/havza-bazli-destekleme-modeli/`, {
        il,
        ilce,
        urunler: urunler.filter(u => u.urun && u.dekar > 0),
        gencCiftci,
        kadinCiftci,
        kobuksKayitli,
        orgutUyesi,
        uretimiGelistirme: { katiOrganikGubre: gubreDestegiSeciliMi }
      });
      
      setSonuc(response.data);
    } catch (error: any) {
      setHata(error.response?.data?.mesaj || 'Hesaplama sırasında hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <Seo
        title="2026 Mazot Gübre Desteği Ne Kadar | Bitkisel Üretim Desteği Hesaplama"
        description="2026 mazot gübre desteği ne kadar öğrenin. Bitkisel üretim destekleri hesaplama aracı. Temel destek, planlı üretim, organik tarım ve iyi tarım uygulamaları desteklerini hesaplayın. Genç ve kadın çiftçiler için özel destekler."
        canonical="https://tarimimar.com.tr/havza-bazli-destekleme-modeli/"
        keywords="2026 mazot gübre desteği ne kadar, 2026 bitkisel üretim desteği, tarım destekleri, havza bazlı destekleme modeli, organik tarım desteği, iyi tarım desteği, genç çiftçi desteği, kadın çiftçi desteği, KOBÜKS, bitkisel üretim destek fiyatları"
        jsonLd={{
          "@context": "https://schema.org",
          "@type": "WebApplication",
          "name": "2026 Mazot Gübre Desteği Hesaplayıcı",
          "description": "2026 mazot gübre desteği ne kadar öğrenin. Türkiye'de 2026 yılı tarımsal desteklerini hesaplayın. Temel destek, planlı üretim, organik ve iyi tarım destekleri.",
          "url": "https://tarimimar.com.tr/havza-bazli-destekleme-modeli/",
          "applicationCategory": "FinanceApplication",
          "operatingSystem": "Web Browser",
          "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "TRY",
            "availability": "https://schema.org/InStock"
          },
          "provider": {
            "@type": "Organization",
            "name": "Webimar",
            "url": "https://tarimimar.com.tr"
          },
          "audience": {
            "@type": "Audience",
            "audienceType": "farmers"
          },
          "featureList": [
            "Temel destek hesaplama",
            "Planlı üretim desteği",
            "Organik tarım desteği",
            "İyi tarım uygulamaları desteği",
            "Genç çiftçi desteği",
            "Kadın çiftçi desteği",
            "Sertifikalı tohum desteği",
            "Su kısıtı desteği"
          ]
        }}
      />

      <PageOuter>
        <Container>
          <Title>Havza Bazlı Destekleme Modeli</Title>
          
          {/* Ürün Seçimi */}
          <FormSection>
            <SectionTitle>🌾 Ürün Seçimi</SectionTitle>
            {urunler.map((urun, index) => (
              <React.Fragment key={index}>
              <UrunRow>
                <Select
                  value={urun.urun}
                  onChange={(e) => urunGuncelle(index, 'urun', e.target.value)}
                >
                  <option value="">Ürün Seçiniz</option>
                  {URUN_DROPDOWN_GRUPLARI.map((grup) => (
                    <optgroup key={grup.label} label={grup.label}>
                      {grup.urunler.map((urunAdi) => (
                        <option key={urunAdi} value={urunAdi}>
                          {urunAdi}
                        </option>
                      ))}
                    </optgroup>
                  ))}
                </Select>
                <Input
                  type="number"
                  placeholder="Dekar"
                  min="0"
                  max="9999"
                  step="0.1"
                  value={urun.dekar || ''}
                  onChange={(e) => {
                    const parsed = parseFloat(e.target.value);
                    const next = Number.isFinite(parsed) ? Math.min(parsed, 9999) : 0;
                    urunGuncelle(index, 'dekar', next);
                  }}
                />
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
                  <label style={{ display: 'flex', alignItems: 'center', fontSize: '11px', gap: '4px' }}>
                    <input
                      type="radio"
                      name={`uretimTipi-${index}`}
                      checked={urun.uretimTipi === 'acikta'}
                      onChange={() => urunGuncelle(index, 'uretimTipi', 'acikta')}
                    />
                    Açıkta
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', fontSize: '11px', gap: '4px' }}>
                    <input
                      type="radio"
                      name={`uretimTipi-${index}`}
                      checked={urun.uretimTipi === 'ortualti'}
                      onChange={() => urunGuncelle(index, 'uretimTipi', 'ortualti')}
                    />
                    Örtü altı
                  </label>

                  <label style={{ display: 'flex', alignItems: 'center', fontSize: '11px', gap: '4px' }}>
                    <input
                      type="radio"
                      name={`sulamaTipi-${index}`}
                      checked={(urun.sulamaTipi || 'kuru') === 'kuru'}
                      onChange={() => urunGuncelle(index, 'sulamaTipi', 'kuru')}
                    />
                    Kuru
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', fontSize: '11px', gap: '4px' }}>
                    <input
                      type="radio"
                      name={`sulamaTipi-${index}`}
                      checked={urun.sulamaTipi === 'sulu'}
                      onChange={() => urunGuncelle(index, 'sulamaTipi', 'sulu')}
                    />
                    Sulu
                  </label>
                </div>

                <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
                  <label style={{ display: 'flex', alignItems: 'center', fontSize: '11px', gap: '4px', whiteSpace: 'nowrap' }}>
                    <input
                      type="checkbox"
                      checked={urun.destekTipi === 'organik'}
                      onChange={() =>
                        urunGuncelle(index, 'destekTipi', urun.destekTipi === 'organik' ? 'yok' : 'organik')
                      }
                    />
                    Organik
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', fontSize: '11px', gap: '4px', whiteSpace: 'nowrap' }}>
                    <input
                      type="checkbox"
                      checked={urun.destekTipi === 'iyiTarim'}
                      onChange={() =>
                        urunGuncelle(index, 'destekTipi', urun.destekTipi === 'iyiTarim' ? 'yok' : 'iyiTarim')
                      }
                    />
                    İyi Tarım
                  </label>
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'nowrap', width: '100%' }}>
                    <label style={{ display: 'flex', alignItems: 'center', fontSize: '11px', gap: '4px', whiteSpace: 'nowrap' }}>
                      <input
                        type="checkbox"
                        checked={urun.sertifikaliTohum}
                        onChange={() => toggleTohumSecimi(index, 'sertifikaliTohum')}
                      />
                      Sertifikalı Tohum
                    </label>

                    <label style={{ display: 'flex', alignItems: 'center', fontSize: '11px', gap: '4px', whiteSpace: 'nowrap' }}>
                      <input
                        type="checkbox"
                        checked={urun.yerliSertifikaliTohum}
                        onChange={() => toggleTohumSecimi(index, 'yerliSertifikaliTohum')}
                      />
                      Yerli Sertifikalı
                    </label>
                  </div>

                  <label style={{ display: 'flex', alignItems: 'center', fontSize: '11px', gap: '4px', whiteSpace: 'nowrap' }}>
                    <input
                      type="checkbox"
                      checked={urun.katiOrganikGubre}
                      onChange={() => toggleKatiOrganikGubre(index)}
                    />
                    Katı Organik / Organomineral Gübre
                  </label>
                </div>

                {urunler.length > 1 && (
                  <RemoveButton onClick={() => urunSil(index)}>🗑️</RemoveButton>
                )}
              </UrunRow>

              </React.Fragment>
            ))}
            <AddButton onClick={urunEkle} disabled={urunler.length >= 20}>
              + Ürün Ekle
            </AddButton>
          </FormSection>

          {/* Yaş ve Cinsiyet (sadece örtü altı seçiliyse göster) */}
          {ortualtiSeciliMi && (
            <FormSection>
              <SectionTitle>👤 Çiftçi Bilgileri</SectionTitle>
              <CheckboxGroup>
                <>
                  <CheckboxLabel>
                    <input
                      type="checkbox"
                      checked={gencCiftci}
                      onChange={(e) => setGencCiftci(e.target.checked)}
                    />
                    41 yaş altı genç çiftçi miyim?
                    {gencCiftci && (
                      <span style={{ color: '#27ae60', fontSize: '11px', marginLeft: '8px' }}>
                        ✅ 3 katsayı ilave destek alacaksınız
                      </span>
                    )}
                  </CheckboxLabel>
                  <CheckboxLabel>
                    <input
                      type="checkbox"
                      checked={kadinCiftci}
                      onChange={(e) => setKadinCiftci(e.target.checked)}
                    />
                    Kadın çiftçi miyim?
                    {kadinCiftci && (
                      <span style={{ color: '#27ae60', fontSize: '11px', marginLeft: '8px' }}>
                        ✅ 3 katsayı ilave destek alacaksınız
                      </span>
                    )}
                  </CheckboxLabel>
                </>
              </CheckboxGroup>
            </FormSection>
          )}

          {/* Üretimi Geliştirme Desteği */}
          <FormSection>
            <SectionTitle>🚀 Üretimi Geliştirme Destekleri</SectionTitle>
            <CheckboxGroup>
              {urunler
                .map((u, idx) => ({ u, idx }))
                .filter(({ u }) => u.destekTipi === 'organik')
                .map(({ u, idx }) => (
                  <SubCheckboxGroup key={`organik-panel-${idx}`} style={{ marginBottom: '12px' }}>
                    <div style={{ fontSize: '12px', fontWeight: 700, marginBottom: '8px' }}>
                      Organik Tarım — Ürün: {u.urun || `#${idx + 1}`}
                    </div>
                    <div style={{ marginBottom: '12px' }}>
                      <label style={{ fontSize: '12px', fontWeight: '600', marginBottom: '8px', display: 'block' }}>
                        Ürün Kategorisi Seçin:
                      </label>
                      <Select
                        value={u.organikTarim.urunGrubu || ''}
                        onChange={(e) => {
                          const nextValue = e.target.value as any;
                          if (!nextValue) {
                            const yeniUrunler = [...urunler];
                            yeniUrunler[idx] = {
                              ...yeniUrunler[idx],
                              organikTarim: { ...yeniUrunler[idx].organikTarim, urunGrubu: undefined }
                            };
                            setUrunler(yeniUrunler);
                            return;
                          }

                          if (
                            (nextValue === 'birinci_kategori' ||
                              nextValue === 'ikinci_kategori' ||
                              nextValue === 'ucuncu_kategori') &&
                            !kategoriUrunUyumluMu(urunler[idx]?.urun || '', nextValue, 'Organik Tarım')
                          ) {
                            return;
                          }

                          const yeniUrunler = [...urunler];
                          yeniUrunler[idx] = {
                            ...yeniUrunler[idx],
                            organikTarim: {
                              ...yeniUrunler[idx].organikTarim,
                              urunGrubu: nextValue
                            }
                          };
                          setUrunler(yeniUrunler);
                        }}
                        style={{ marginBottom: '8px', fontSize: '12px' }}
                      >
                        <option value="">Kategori seçiniz...</option>
                        <option value="birinci_kategori">1. Grup Ürünler</option>
                        <option value="ikinci_kategori">2. Grup Ürünler</option>
                        <option value="ucuncu_kategori">3. Grup Ürünler</option>
                      </Select>
                      {u.organikTarim.urunGrubu && (
                        <Button
                          className="secondary"
                          onClick={() => {
                            setOrganikModalKategori(u.organikTarim.urunGrubu || '');
                            setOrganikModalGoster(true);
                          }}
                          style={{ fontSize: '11px', padding: '4px 8px', marginTop: '4px' }}
                        >
                          ℹ️ Bu kategorideki ürünleri göster
                        </Button>
                      )}
                    </div>

                    <div style={{ marginBottom: '8px' }}>
                      <label style={{ fontSize: '12px', fontWeight: '600' }}>Sertifika Türü:</label>
                    </div>
                    <CheckboxLabel>
                      <input
                        type="radio"
                        name={`organikSertifika-${idx}`}
                        checked={(u.organikTarim.sertifikaTuru || 'bireysel') === 'bireysel'}
                        onChange={() => {
                          const yeniUrunler = [...urunler];
                          yeniUrunler[idx] = {
                            ...yeniUrunler[idx],
                            organikTarim: { ...yeniUrunler[idx].organikTarim, sertifikaTuru: 'bireysel' }
                          };
                          setUrunler(yeniUrunler);
                        }}
                      />
                      Bireysel sertifika
                    </CheckboxLabel>
                    <CheckboxLabel>
                      <input
                        type="radio"
                        name={`organikSertifika-${idx}`}
                        checked={(u.organikTarim.sertifikaTuru || 'bireysel') === 'grup'}
                        onChange={() => {
                          const yeniUrunler = [...urunler];
                          yeniUrunler[idx] = {
                            ...yeniUrunler[idx],
                            organikTarim: { ...yeniUrunler[idx].organikTarim, sertifikaTuru: 'grup' }
                          };
                          setUrunler(yeniUrunler);
                        }}
                      />
                      Grup sertifikası
                    </CheckboxLabel>
                  </SubCheckboxGroup>
                ))}

              {urunler
                .map((u, idx) => ({ u, idx }))
                .filter(({ u }) => u.destekTipi === 'iyiTarim')
                .map(({ u, idx }) => (
                  <SubCheckboxGroup key={`iyiTarim-panel-${idx}`} style={{ marginBottom: '12px' }}>
                    <div style={{ fontSize: '12px', fontWeight: 700, marginBottom: '8px' }}>
                      İyi Tarım — Ürün: {u.urun || `#${idx + 1}`}
                    </div>
                    <div style={{ marginBottom: '12px' }}>
                      <label style={{ fontSize: '12px', fontWeight: '600', marginBottom: '8px', display: 'block' }}>
                        Ürün Kategorisi Seçin:
                      </label>
                      <Select
                        value={u.iyiTarim.urunGrubu || ''}
                        onChange={(e) => {
                          const nextValue = e.target.value as any;
                          if (!nextValue) {
                            const yeniUrunler = [...urunler];
                            yeniUrunler[idx] = {
                              ...yeniUrunler[idx],
                              iyiTarim: { ...yeniUrunler[idx].iyiTarim, urunGrubu: undefined }
                            };
                            setUrunler(yeniUrunler);
                            return;
                          }

                          if (
                            (nextValue === 'birinci_kategori' ||
                              nextValue === 'ikinci_kategori' ||
                              nextValue === 'ucuncu_kategori') &&
                            !kategoriUrunUyumluMu(urunler[idx]?.urun || '', nextValue, 'İyi Tarım')
                          ) {
                            return;
                          }

                          const yeniUrunler = [...urunler];
                          yeniUrunler[idx] = {
                            ...yeniUrunler[idx],
                            iyiTarim: { ...yeniUrunler[idx].iyiTarim, urunGrubu: nextValue }
                          };
                          setUrunler(yeniUrunler);
                        }}
                        style={{ marginBottom: '8px', fontSize: '12px' }}
                      >
                        <option value="">Kategori seçiniz...</option>
                        <option value="birinci_kategori">1. Grup Ürünler</option>
                        <option value="ikinci_kategori">2. Grup Ürünler</option>
                        <option value="ucuncu_kategori">3. Grup Ürünler</option>
                      </Select>
                      {u.iyiTarim.urunGrubu && (
                        <Button
                          className="secondary"
                          onClick={() => {
                            setIyiTarimModalKategori(u.iyiTarim.urunGrubu || '');
                            setIyiTarimModalGoster(true);
                          }}
                          style={{ fontSize: '11px', padding: '4px 8px', marginTop: '4px' }}
                        >
                          ℹ️ Bu kategorideki ürünleri göster
                        </Button>
                      )}
                    </div>

                    <div style={{ marginBottom: '8px' }}>
                      <label style={{ fontSize: '12px', fontWeight: '600' }}>Sertifika Türü:</label>
                    </div>
                    <CheckboxLabel>
                      <input
                        type="radio"
                        name={`iyiTarimSertifika-${idx}`}
                        checked={(u.iyiTarim.sertifikaTuru || 'bireysel') === 'bireysel'}
                        onChange={() => {
                          const yeniUrunler = [...urunler];
                          yeniUrunler[idx] = {
                            ...yeniUrunler[idx],
                            iyiTarim: { ...yeniUrunler[idx].iyiTarim, sertifikaTuru: 'bireysel' }
                          };
                          setUrunler(yeniUrunler);
                        }}
                      />
                      Bireysel sertifika
                    </CheckboxLabel>
                    <CheckboxLabel>
                      <input
                        type="radio"
                        name={`iyiTarimSertifika-${idx}`}
                        checked={(u.iyiTarim.sertifikaTuru || 'bireysel') === 'grup'}
                        onChange={() => {
                          const yeniUrunler = [...urunler];
                          yeniUrunler[idx] = {
                            ...yeniUrunler[idx],
                            iyiTarim: { ...yeniUrunler[idx].iyiTarim, sertifikaTuru: 'grup' }
                          };
                          setUrunler(yeniUrunler);
                        }}
                      />
                      Grup sertifikası
                    </CheckboxLabel>
                  </SubCheckboxGroup>
                ))}

              {organikSeciliMi && (
                <SubCheckboxGroup style={{ marginBottom: '12px' }}>
                  <CheckboxLabel style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <input
                      type="checkbox"
                      checked={orgutUyesi}
                      onChange={(e) => setOrgutUyesi(e.target.checked)}
                    />
                    1. derece tarımsal amaçlı örgüt üyesiyim (%25 ilave organik destek)
                    <Button
                      className="secondary"
                      onClick={() => {
                        void openOrgutListesiModal();
                      }}
                      style={{ marginLeft: '12px', fontSize: '12px', padding: '4px 8px' }}
                    >
                      Hangileri?
                    </Button>
                  </CheckboxLabel>
                </SubCheckboxGroup>
              )}
            </CheckboxGroup>
          </FormSection>

          {/* İl/İlçe Seçimi */}
          <FormSection>
            <SectionTitle>📍 Konum Seçimi</SectionTitle>
            <UrunRow>
              <Select
                value={il}
                onChange={(e) => {
                  setIl(e.target.value);
                  setIlce(''); // İl değişince ilçe sıfırla
                }}
              >
                <option value="">İl seçiniz...</option>
                {Object.keys(havzaData).sort((a, b) => a.localeCompare(b, 'tr')).map(ilAdi => (
                  <option key={ilAdi} value={ilAdi}>{ilAdi}</option>
                ))}
              </Select>
              <Select
                value={ilce}
                onChange={(e) => setIlce(e.target.value)}
                disabled={!il}
              >
                <option value="">İlçe seçiniz...</option>
                {il && havzaData[il] && Object.keys(havzaData[il]).sort((a, b) => a.localeCompare(b, 'tr')).map(ilceAdi => (
                  <option key={ilceAdi} value={ilceAdi}>{ilceAdi}</option>
                ))}
              </Select>
            </UrunRow>
            
            {/* Havza Haritası */}
            <div style={{ marginTop: '16px' }}>
              <h4 style={{ marginBottom: '8px', color: '#374151' }}>🗺️ Havza Bazlı Ürün Dağılım Haritası</h4>
              <DynamicMap 
                selectedLocation={{ il, ilce }}
                selectedProducts={selectedProductsForMap}
                havzaData={havzaData}
                showSupportedDistricts={gosterDigerIlceler || (formSelectedProducts.length > 0)}
              />
            </div>
          </FormSection>

          {/* Hata Mesajı */}
          {hata && <ErrorMessage>{hata}</ErrorMessage>}

          {/* Butonlar */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: '10px', marginBottom: '20px', flexWrap: 'wrap' }}>
            <CalculateButton onClick={hesapla} disabled={loading}>
              {loading && <LoadingSpinner />}
              {loading ? 'Hesaplanıyor...' : '💰 Desteği Hesapla'}
            </CalculateButton>

            <Button 
                onClick={() => {
                    // Formda hiç ürün seçilmediyse: ürün seçme modalı aç (butona her basışta)
                    if (haritaUrunModuAktif) {
                      openHaritaUrunModal();
                      return;
                    }

                    // Form ürünleri seçiliyse: mevcut toggle davranışı
                    if (gosterDigerIlceler) {
                      setGosterDigerIlceler(false);
                    } else {
                      setGosterDigerIlceler(true);
                    }
                }}
                type="button"
                style={{ 
                    backgroundColor: gosterDigerIlceler ? '#F59E0B' : '#6B7280', 
                    color: 'white',
                    padding: '16px 20px', 
                    fontSize: '16px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                }}
            >
                {haritaUrunModuAktif
                  ? (gosterDigerIlceler ? '🗺️ Ürünü Değiştir' : '🗺️ Destek Verilen Diğer İlçeleri Göster')
                  : (gosterDigerIlceler ? '👁️ Haritayı Temizle' : '🗺️ Destek Verilen Diğer İlçeleri Göster')}
            </Button>
          </div>

          {/* Sonuç */}
          {sonuc && sonuc.uygun && (
            <ResultSection>
              <SectionTitle>📊 Hesaplama Sonucu</SectionTitle>
              <ResultTable>
                <ResultRow>
                  <ResultLabel>Temel Destek</ResultLabel>
                  <ResultValue>{sonuc.detaylar.temel_destek.toFixed(2)} TL</ResultValue>
                </ResultRow>
                <ResultRow>
                  <ResultLabel>Planlı Üretim Desteği</ResultLabel>
                  <ResultValue>{sonuc.detaylar.planli_uretim.toFixed(2)} TL</ResultValue>
                </ResultRow>
                {sonuc.detaylar.genclik_ilavesi > 0 && (
                  <ResultRow>
                    <ResultLabel>Genç/Kadın Çiftçi İlavesi</ResultLabel>
                    <ResultValue>{sonuc.detaylar.genclik_ilavesi.toFixed(2)} TL</ResultValue>
                  </ResultRow>
                )}
                {sonuc.detaylar.sut_havzasi_ilavesi > 0 && (
                  <ResultRow>
                    <ResultLabel>Süt Havzası İlavesi</ResultLabel>
                    <ResultValue>{sonuc.detaylar.sut_havzasi_ilavesi.toFixed(2)} TL</ResultValue>
                  </ResultRow>
                )}
                {sonuc.detaylar.su_kisiti > 0 && (
                  <ResultRow>
                    <ResultLabel>Su Kısıtı Desteği</ResultLabel>
                    <ResultValue>{sonuc.detaylar.su_kisiti.toFixed(2)} TL</ResultValue>
                  </ResultRow>
                )}
                {sonuc.detaylar.sertifikali_tohum > 0 && (
                  <ResultRow>
                    <ResultLabel>Sertifikalı Tohum Desteği</ResultLabel>
                    <ResultValue>{sonuc.detaylar.sertifikali_tohum.toFixed(2)} TL</ResultValue>
                  </ResultRow>
                )}
                {sonuc.detaylar.yerli_sertifikali_tohum > 0 && (
                  <ResultRow>
                    <ResultLabel>Yerli Sertifikalı Tohum Desteği</ResultLabel>
                    <ResultValue>{sonuc.detaylar.yerli_sertifikali_tohum.toFixed(2)} TL</ResultValue>
                  </ResultRow>
                )}
                {sonuc.detaylar.organik_tarim > 0 && (
                  <ResultRow>
                    <ResultLabel>Organik Tarım Desteği</ResultLabel>
                    <ResultValue>{sonuc.detaylar.organik_tarim.toFixed(2)} TL</ResultValue>
                  </ResultRow>
                )}
                {sonuc.detaylar.iyi_tarim > 0 && (
                  <ResultRow>
                    <ResultLabel>İyi Tarım Desteği</ResultLabel>
                    <ResultValue>{sonuc.detaylar.iyi_tarim.toFixed(2)} TL</ResultValue>
                  </ResultRow>
                )}
                {sonuc.detaylar.gubre > 0 && (
                  <ResultRow>
                    <ResultLabel>Gübre Desteği</ResultLabel>
                    <ResultValue>{sonuc.detaylar.gubre.toFixed(2)} TL</ResultValue>
                  </ResultRow>
                )}
                <ResultRow style={{ borderTop: '2px solid #059669', marginTop: '8px' }}>
                  <ResultLabel style={{ fontSize: '18px', fontWeight: 'bold' }}>TOPLAM DESTEK</ResultLabel>
                  <ResultValue style={{ fontSize: '20px', fontWeight: 'bold' }}>{sonuc.detaylar.toplam.toFixed(2)} TL</ResultValue>
                </ResultRow>
              </ResultTable>
              <div style={{ marginTop: '16px', fontSize: '14px', color: '#6b7280' }}>
                {sonuc.mesaj}
              </div>
            </ResultSection>
          )}

          {/* Harita Ürün Seçimi Modal (Ürün seçilmeden diğer ilçeleri göstermek için) */}
          {haritaUrunModalGoster && (
            <div style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0,0,0,0.6)',
              zIndex: 9999,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '20px',
              backdropFilter: 'blur(4px)'
            }}>
              <div style={{
                backgroundColor: 'white',
                borderRadius: '16px',
                padding: '24px',
                maxWidth: '560px',
                width: '100%',
                maxHeight: '85vh',
                overflow: 'hidden',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid #e2e8f0', paddingBottom: '12px' }}>
                  <div>
                    <h3 style={{ margin: 0, color: '#1e293b', fontSize: '1.15rem', fontWeight: 600 }}>Desteklenen İlçeler - Ürün Seçimi</h3>
                    <span style={{ fontSize: '0.875rem', color: '#64748b', marginTop: '4px', display: 'block' }}>
                      Haritada hangi ürünün desteklendiğini görmek için ürün seçiniz.
                    </span>
                  </div>
                  <Button className="secondary" onClick={() => setHaritaUrunModalGoster(false)} style={{ minWidth: '40px', padding: '8px' }}>✕</Button>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <Select value={haritaUrunSecimiDraft} onChange={(e) => setHaritaUrunSecimiDraft(e.target.value)}>
                    <option value="">Ürün Seçiniz</option>
                    {URUN_DROPDOWN_GRUPLARI.map((grup) => (
                      <optgroup key={grup.label} label={grup.label}>
                        {grup.urunler.map((urunAdi) => (
                          <option key={urunAdi} value={urunAdi}>
                            {urunAdi}
                          </option>
                        ))}
                      </optgroup>
                    ))}
                  </Select>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '8px' }}>
                    <Button
                      type="button"
                      className="secondary"
                      onClick={() => {
                        setHaritaUrunModalGoster(false);
                      }}
                    >
                      Vazgeç
                    </Button>
                    <Button
                      type="button"
                      onClick={applyHaritaUrunSecimi}
                      style={{ backgroundColor: '#059669', color: 'white' }}
                    >
                      Haritada Göster
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Örgüt Listesi Modal */}
          {orgutListesiGoster && (
            <div style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0,0,0,0.6)',
              zIndex: 9999,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '20px',
              backdropFilter: 'blur(4px)'
            }}>
              <div style={{
                backgroundColor: 'white',
                borderRadius: '16px',
                padding: '24px',
                maxWidth: '800px',
                width: '100%',
                maxHeight: '85vh',
                overflow: 'hidden',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid #e2e8f0', paddingBottom: '16px' }}>
                  <div>
                    <h3 style={{ margin: 0, color: '#1e293b', fontSize: '1.25rem', fontWeight: 600 }}>Tarımsal Örgüt Listesi</h3>
                    {il && <span style={{fontSize: '0.875rem', color: '#64748b', marginTop: '4px', display: 'block'}}>Seçili İl: <strong>{il}</strong></span>}
                  </div>
                  <Button className="secondary" onClick={() => setOrgutListesiGoster(false)} style={{ minWidth: '40px', padding: '8px' }}>✕</Button>
                </div>
                
                <div style={{ flex: 1, overflowY: 'auto', paddingRight: '4px' }}>
                  {(() => {
                    const seciliIl = il ? il.toLocaleUpperCase('tr-TR') : '';
                    const filtreli = tarimsalOrgutListesi.filter((o) => !seciliIl || o.il === seciliIl);

                    if (tarimsalOrgutLoading) {
                      return (
                        <div style={{ padding: '32px', textAlign: 'center', color: '#64748b' }}>
                          Liste yükleniyor...
                        </div>
                      );
                    }

                    if (tarimsalOrgutError) {
                      return (
                        <div style={{ padding: '32px', textAlign: 'center', color: '#b91c1c' }}>
                          {tarimsalOrgutError}
                        </div>
                      );
                    }

                    if (filtreli.length === 0) {
                      return (
                        <div style={{ padding: '32px', textAlign: 'center', color: '#64748b' }}>
                          Bu il için kayıtlı örgüt bulunamadı.
                        </div>
                      );
                    }

                    return filtreli.map((orgut, index) => (
                        <div key={index} style={{
                          padding: '16px',
                          borderBottom: '1px solid #f1f5f9',
                          transition: 'background-color 0.2s',
                          backgroundColor: index % 2 === 0 ? '#fff' : '#f8fafc'
                        }}>
                          <div style={{ display: 'flex', alignItems: 'baseline', marginBottom: '4px' }}>
                             <span style={{ fontWeight: '700', color: '#0f172a', marginRight: '8px' }}>{orgut.ilce}</span>
                             <span style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{orgut.il}</span>
                          </div>
                          <div style={{ fontSize: '0.95rem', color: '#334155', lineHeight: '1.5' }}>{orgut.orgut}</div>
                        </div>
                    ));
                  })()}
                </div>
              </div>
            </div>
          )}

          {/* Organik Tarım Kategori Modal */}
          {organikModalGoster && (
            <div style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0,0,0,0.6)',
              zIndex: 9999,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '20px',
              backdropFilter: 'blur(4px)'
            }}>
              <div style={{
                backgroundColor: 'white',
                borderRadius: '16px',
                padding: '24px',
                maxWidth: '800px',
                width: '100%',
                maxHeight: '85vh',
                overflow: 'hidden',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
              }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '20px',
                  borderBottom: '1px solid #e2e8f0',
                  paddingBottom: '16px'
                }}>
                  <div>
                    <h3 style={{ margin: 0, color: '#1e293b', fontSize: '1.25rem', fontWeight: '600' }}>
                      Organik Tarım - {organikModalKategori === 'birinci_kategori' ? '1. Kategori' : 
                                        organikModalKategori === 'ikinci_kategori' ? '2. Kategori' : '3. Kategori'} Ürünler
                    </h3>
                    <span style={{ fontSize: '0.875rem', color: '#64748b', marginTop: '4px', display: 'block' }}>
                      Bu kategorideki desteklenen ürün listesi
                    </span>
                  </div>
                  <Button 
                    className="secondary"
                    onClick={() => setOrganikModalGoster(false)}
                    style={{ minWidth: '40px', padding: '8px' }}
                  >
                    ✕
                  </Button>
                </div>
                <div style={{ flex: 1, overflowY: 'auto', paddingRight: '4px' }}>
                  <div style={{ padding: '16px', fontSize: '14px', lineHeight: '1.6', color: '#374151' }}>
                    {organikModalKategori === 'birinci_kategori' && 
                      ORGANIK_IYI_TARIM_KATEGORI_URUN_METIN.birinci_kategori
                    }
                    {organikModalKategori === 'ikinci_kategori' && 
                      ORGANIK_IYI_TARIM_KATEGORI_URUN_METIN.ikinci_kategori
                    }
                    {organikModalKategori === 'ucuncu_kategori' && 
                      ORGANIK_IYI_TARIM_KATEGORI_URUN_METIN.ucuncu_kategori
                    }
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Uyarı Modal */}
          {uyariModalGoster && (
            <div style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0,0,0,0.6)',
              zIndex: 9999,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '20px',
              backdropFilter: 'blur(4px)'
            }}>
              <div style={{
                backgroundColor: 'white',
                borderRadius: '16px',
                padding: '24px',
                maxWidth: '800px',
                width: '100%',
                maxHeight: '85vh',
                overflow: 'hidden',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
              }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '20px',
                  borderBottom: '1px solid #e2e8f0',
                  paddingBottom: '16px'
                }}>
                  <div>
                    <h3 style={{ margin: 0, color: '#1e293b', fontSize: '1.25rem', fontWeight: '600' }}>
                      {uyariModalBaslik || 'Uyarı'}
                    </h3>
                    <span style={{ fontSize: '0.875rem', color: '#64748b', marginTop: '4px', display: 'block' }}>
                      Lütfen ürün seçimi ve kategori seçimini kontrol ediniz
                    </span>
                  </div>
                  <Button
                    className="secondary"
                    onClick={() => setUyariModalGoster(false)}
                    style={{ minWidth: '40px', padding: '8px' }}
                  >
                    ✕
                  </Button>
                </div>
                <div style={{ flex: 1, overflowY: 'auto', paddingRight: '4px' }}>
                  <div style={{ padding: '16px', fontSize: '14px', lineHeight: '1.6', color: '#374151', whiteSpace: 'pre-wrap' }}>
                    {uyariModalMetin}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* İyi Tarım Kategori Modal */}
          {iyiTarimModalGoster && (
            <div style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0,0,0,0.6)',
              zIndex: 9999,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '20px',
              backdropFilter: 'blur(4px)'
            }}>
              <div style={{
                backgroundColor: 'white',
                borderRadius: '16px',
                padding: '24px',
                maxWidth: '800px',
                width: '100%',
                maxHeight: '85vh',
                overflow: 'hidden',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
              }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '20px',
                  borderBottom: '1px solid #e2e8f0',
                  paddingBottom: '16px'
                }}>
                  <div>
                    <h3 style={{ margin: 0, color: '#1e293b', fontSize: '1.25rem', fontWeight: '600' }}>
                      İyi Tarım Uygulamaları - {iyiTarimModalKategori === 'birinci_kategori' ? '1. Kategori' : 
                                                iyiTarimModalKategori === 'ikinci_kategori' ? '2. Kategori' : '3. Kategori'} Ürünler
                    </h3>
                    <span style={{ fontSize: '0.875rem', color: '#64748b', marginTop: '4px', display: 'block' }}>
                      Bu kategorideki desteklenen ürün listesi
                    </span>
                  </div>
                  <Button 
                    className="secondary"
                    onClick={() => setIyiTarimModalGoster(false)}
                    style={{ minWidth: '40px', padding: '8px' }}
                  >
                    ✕
                  </Button>
                </div>
                <div style={{ flex: 1, overflowY: 'auto', paddingRight: '4px' }}>
                  <div style={{ padding: '16px', fontSize: '14px', lineHeight: '1.6', color: '#374151' }}>
                    {iyiTarimModalKategori === 'birinci_kategori' && 
                      ORGANIK_IYI_TARIM_KATEGORI_URUN_METIN.birinci_kategori
                    }
                    {iyiTarimModalKategori === 'ikinci_kategori' && 
                      ORGANIK_IYI_TARIM_KATEGORI_URUN_METIN.ikinci_kategori
                    }
                    {iyiTarimModalKategori === 'ucuncu_kategori' && 
                      ORGANIK_IYI_TARIM_KATEGORI_URUN_METIN.ucuncu_kategori
                    }
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Sorularla Yeni Destek Modeli (SSS) */}
          <FormSection>
            <SectionTitle>❓ Sorularla Yeni Destek Modeli (2026)</SectionTitle>
            <div style={{ fontSize: '14px', color: '#374151', lineHeight: '1.6' }}>
              <strong>Kaynaklar:</strong>
              <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginTop: '8px' }}>
                <a
                  href={YENI_DESTEK_KAYNAK_PDF_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="Sorularla Yeni Destek Modeli - 2026 (PDF)"
                  style={{ color: '#2563eb', fontWeight: 600, flex: '1 1 220px', minWidth: 0 }}
                >
                  Sorularla Yeni Destek Modeli - 2026 (PDF)
                </a>

                <a
                  href={HAVZA_2026_URUN_DESENI_PDF_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="2026 bitkisel üretim planlanması havza ürün deseni listesi (PDF)"
                  style={{ color: '#2563eb', fontWeight: 600, flex: '1 1 220px', minWidth: 0 }}
                >
                  2026 bitkisel üretim planlanması havza ürün deseni listesi (PDF)
                </a>

                <a
                  href={URETIM_2026_DESTEK_BIRIM_FIATLARI_PDF_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="2026 üretim yılı bitkisel üretim destekleme birim fiyatları (PDF)"
                  style={{ color: '#2563eb', fontWeight: 600, flex: '1 1 220px', minWidth: 0 }}
                >
                  2026 üretim yılı bitkisel üretim destekleme birim fiyatları (PDF)
                </a>
              </div>
            </div>

            <div style={{ marginTop: '14px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {yeniDestekSSSLoading ? (
                <div style={{ padding: '12px', color: '#64748b' }}>Sorular yükleniyor...</div>
              ) : yeniDestekSSSError ? (
                <div style={{ padding: '12px', color: '#b91c1c' }}>{yeniDestekSSSError}</div>
              ) : yeniDestekSSS.length === 0 ? (
                <div style={{ padding: '12px', color: '#64748b' }}>Soru listesi bulunamadı.</div>
              ) : (
                yeniDestekSSS.map((item) => (
                  <details
                    key={item.no}
                    style={{
                      border: '1px solid #e2e8f0',
                      borderRadius: '10px',
                      padding: '10px 12px',
                      background: '#ffffff'
                    }}
                  >
                    <summary style={{ cursor: 'pointer', fontWeight: 700, color: '#0f172a' }}>
                      {item.no}. {item.soru}
                    </summary>
                    <div style={{ marginTop: '10px', color: '#334155', whiteSpace: 'pre-wrap', lineHeight: '1.65', fontSize: '14px' }}>
                      {item.cevap}
                    </div>
                  </details>
                ))
              )}
            </div>
          </FormSection>

          {/* Ek Mevzuat */}
          <FormSection>
            <SectionTitle>📄 Ek Mevzuat</SectionTitle>
            <div style={{ fontSize: '14px', color: '#374151', lineHeight: '1.6' }}>
              <a href={DESTEKLEME_TEBLIGI_PDF_URL} target="_blank" rel="noopener noreferrer" style={{ color: '#2563eb', fontWeight: 600 }}>
                Destekleme Tebliği (Tebliğ No: 2024-39)
              </a>
            </div>
          </FormSection>
        </Container>
      </PageOuter>
    </Layout>
  );
}
