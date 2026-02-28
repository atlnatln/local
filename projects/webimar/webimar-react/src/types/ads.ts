/**
 * Reklam Altyapısı – Tip Tanımları
 * 
 * İl bazlı reklam verenler için temel veri modeli.
 * - Bir ilde birden fazla reklam veren olabilir.
 * - Bir reklam veren birden fazla ilde faaliyet gösterebilir.
 * - Reklam veren kategorileri: emlakçı, şehir plancısı, müteahhit vb.
 */

/** Reklam veren faaliyet kategorisi */
export type AdvertiserCategory =
  | 'emlakci'
  | 'sehir_plancisi'
  | 'muteahhit'
  | 'ziraat_muhendisi'
  | 'diger';

/** Tek bir reklam vereni tanımlar */
export type Advertiser = {
  /** Benzersiz tanımlayıcı */
  id: string;
  /** Firma / kişi adı */
  name: string;
  /** Faaliyet kategorisi */
  category: AdvertiserCategory;
  /** Kısa açıklama (maks ~120 karakter) */
  description: string;
  /** Telefon numarası (isteğe bağlı) */
  phone?: string;
  /** Web sitesi (isteğe bağlı) */
  website?: string;
  /** Reklam görseli URL'i (isteğe bağlı) */
  imageUrl?: string;
  /** Aktif mi? Kapalı reklam verenler gösterilmez */
  isActive: boolean;
  /** Sıralama önceliği — düşük sayı önce gösterilir */
  priority: number;
};

/** Bir ile ait reklam veren listesi */
export type ProvinceAds = {
  /** İl adı (tam Türkçe, büyük harfle başlar: "İzmir", "Ankara") */
  province: string;
  /** Bu ildeki aktif reklam verenler */
  advertisers: Advertiser[];
};

/** Reklam bileşenine dışarıdan verilen prop'lar */
export type AdPlacementProps = {
  /** Harita doğrulamasından gelen il adı (null ise bileşen render edilmez) */
  selectedProvince: string | null;
  /** Hesaplama yapılan yapı türü (ileride hedefleme için) */
  calculationType?: string;
};

/** Kategori etiketleri (UI'da gösterilecek Türkçe karşılıklar) */
export const CATEGORY_LABELS: Record<AdvertiserCategory, string> = {
  emlakci: 'Emlakçı',
  sehir_plancisi: 'Şehir Plancısı',
  muteahhit: 'Müteahhit',
  ziraat_muhendisi: 'Ziraat Mühendisi',
  diger: 'Diğer',
};
