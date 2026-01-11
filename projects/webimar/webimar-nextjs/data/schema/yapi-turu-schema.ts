/**
 * Tarımsal Yapı Türü Landing Page Veri Şeması
 * SEO-optimized landing page'ler için veri yapısı
 */

export interface YapiTuruSeo {
  title: string;              // SEO title - örn: "Bağ Evi Nasıl Yapılır? | Tarım İmar"
  description: string;        // Meta description
  keywords: string[];         // Anahtar kelimeler
  canonical: string;          // Canonical URL - örn: "/bag-evi"
  ogImage?: string;          // Özel Open Graph image
}

export interface YapiTuruHero {
  title: string;              // Hero başlık - örn: "Bağ Evi Yapımı ve Hesaplama"
  subtitle: string;           // Alt başlık / kısa açıklama
  icon: string;               // Emoji icon - örn: "🏡"
  backgroundImage?: string;  // Hero arka plan resmi (opsiyonel)
}

export interface YapiTuruFeature {
  title: string;              // Özellik başlığı
  description: string;        // Özellik açıklaması
  icon: string;               // Özellik ikonu
}

export interface YapiTuruLegalRequirements {
  minArea?: number;           // Minimum arazi büyüklüğü (m² veya dekar)
  minAreaUnit?: string;       // Birim: "m²", "dekar", "hektar"
  maxBuildingArea?: number;   // Maksimum inşaat alanı (m²)
  maxFloorArea?: number;      // Maksimum taban alanı (m²)
  restrictions: string[];     // Kısıtlamalar listesi
  genelge: string[];          // Genelge maddeleri
  specialConditions?: string[]; // Özel koşullar
}

export interface YapiTuruTechnicalRequirements {
  specifications: string[];   // Teknik özellikler
  capacity?: {                // Kapasite bilgileri (hayvancılık için)
    unit: string;             // Birim: "baş", "adet", "m²"
    perUnit?: number;         // Birim başına alan (m²)
    minCapacity?: number;     // Minimum kapasite
    maxCapacity?: number;     // Maksimum kapasite
  };
  materials?: string[];       // Malzeme gereksinimleri
  infrastructure?: string[];  // Altyapı ihtiyaçları
}

export interface YapiTuruRequirements {
  legal: YapiTuruLegalRequirements;
  technical: YapiTuruTechnicalRequirements;
}

export interface YapiTuruCalculator {
  title: string;              // Hesaplama bölümü başlığı
  description: string;        // Hesaplama açıklaması
  ctaText: string;            // Call-to-action metni - örn: "Bağ Evi Hesapla"
  ctaLink: string;            // Hesaplama sayfası linki - örn: "/hesaplama/bag-evi"
}

export interface YapiTuruFaq {
  question: string;           // Soru
  answer: string;             // Cevap (markdown destekli)
}

export interface YapiTuruSources {
  genelge: boolean;           // Genelge'den veri alındı mı?
  pythonModule: boolean;      // Python modülünden veri alındı mı?
  webScraping: boolean;       // Web scraping yapıldı mı?
  scrapedUrls?: string[];    // Scrape edilen URL'ler
  lastUpdated: string;        // Son güncelleme tarihi (ISO format)
  notes?: string;             // Ek notlar
}

export interface YapiTuruRelatedPages {
  title: string;              // İlgili sayfa başlığı
  url: string;                // İlgili sayfa URL'i
  icon?: string;              // İlgili sayfa ikonu
}

/**
 * Ana veri yapısı - Her tarımsal yapı türü için
 */
export interface YapiTuruData {
  // Yapı türü temel bilgileri
  slug: string;               // URL slug - örn: "bag-evi"
  id: number;                 // Yapı türü ID (constants.py ile uyumlu)
  name: string;               // Yapı adı - örn: "Bağ evi"
  category: string;           // Kategori - örn: "Barınma", "Hayvancılık"
  
  // SEO bilgileri
  seo: YapiTuruSeo;
  
  // Landing page içeriği
  hero: YapiTuruHero;
  
  // Giriş metni
  introduction: {
    whatIs: string;           // Nedir? açıklaması (markdown)
    purpose: string;          // Amaç ve kullanım
    whoCanBuild: string;      // Kimler yapabilir?
  };
  
  // Özellikler
  features: YapiTuruFeature[];
  
  // Gereksinimler
  requirements: YapiTuruRequirements;
  
  // Hesaplama bölümü
  calculator: YapiTuruCalculator;
  
  // SSS
  faq: YapiTuruFaq[];
  
  // İlgili sayfalar
  relatedPages?: YapiTuruRelatedPages[];
  
  // Structured data (Schema.org JSON-LD)
  structuredData?: any;
  
  // İmar / Yapı Ruhsatı Bilgileri (opsiyonel)
  imar?: {
    title: string;
    summary: string;
    requirements?: string[];
    referenceUrl?: string;
  };
  
  // Veri kaynakları
  sources: YapiTuruSources;
}

/**
 * Tüm yapı türlerinin listesi için
 */
export interface YapiTurleriIndex {
  slug: string;
  name: string;
  category: string;
  icon: string;
  description: string;
}

/**
 * Kategori bazında gruplama için
 */
export interface YapiTuruCategory {
  name: string;               // Kategori adı
  icon: string;               // Kategori ikonu
  description: string;        // Kategori açıklaması
  yapiTurleri: YapiTurleriIndex[]; // Bu kategorideki yapı türleri
}
