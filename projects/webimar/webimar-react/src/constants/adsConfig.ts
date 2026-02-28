/**
 * İl Bazlı Reklam Konfigürasyonu
 * 
 * Bu dosya, il bazlı reklam verenlerinin merkezi kaydını tutar.
 * Şu anda aktif reklam veren bulunmuyor; altyapı hazır halde bekliyor.
 * 
 * Yeni reklam veren eklemek için:
 * 1. Aşağıdaki PROVINCE_ADS map'ine ilgili il adını (Türkçe, büyük harfle) key olarak ekleyin.
 * 2. Advertiser dizisine reklam veren bilgilerini girin.
 * 3. isActive: true yaparak reklamı aktif edin.
 * 
 * Örnek (aktif olduğunda):
 * ```ts
 * PROVINCE_ADS.set('İzmir', [
 *   {
 *     id: 'izmir-emlak-01',
 *     name: 'Ege Emlak Danışmanlık',
 *     category: 'emlakci',
 *     description: 'İzmir ve çevresinde tarımsal arazi alım-satım ve danışmanlık.',
 *     phone: '0232 123 45 67',
 *     website: 'https://egeemlakilanlar.com',
 *     isActive: true,
 *     priority: 1,
 *   },
 * ]);
 * ```
 */

import { Advertiser } from '../types/ads';

/**
 * İl adı → Reklam veren listesi.
 * Key: İl adı (Türkçe, büyük harfle başlar — "İzmir", "Ankara", "İstanbul" vb.)
 * Value: O ilde faaliyet gösteren reklam verenler dizisi.
 */
export const PROVINCE_ADS = new Map<string, Advertiser[]>([
  // ──────────────────────────────────────────
  //  ŞU ANDA AKTİF REKLAM VEREN BULUNMUYOR
  //  Aşağıya yeni il/reklam veren eklenecek
  // ──────────────────────────────────────────

  // Örnek şablon (yorum satırı — aktifleştirmek için yorum kaldırılır):
  //
  // ['İzmir', [
  //   {
  //     id: 'izmir-emlak-01',
  //     name: 'Ege Emlak Danışmanlık',
  //     category: 'emlakci',
  //     description: 'İzmir ve çevresinde tarımsal arazi alım-satım ve danışmanlık.',
  //     phone: '0232 123 45 67',
  //     website: 'https://egeemlakilanlar.com',
  //     isActive: true,
  //     priority: 1,
  //   },
  // ]],
  //
  // ['Ankara', [
  //   {
  //     id: 'ankara-planci-01',
  //     name: 'Başkent Şehir Planlama',
  //     category: 'sehir_plancisi',
  //     description: 'Tarımsal alan imar planlaması ve ruhsat danışmanlığı.',
  //     phone: '0312 987 65 43',
  //     website: 'https://baskentsehirplanlama.com',
  //     isActive: true,
  //     priority: 1,
  //   },
  // ]],
]);

/**
 * Belirli bir il için aktif reklam verenleri döndürür.
 * İl bulunamazsa veya aktif reklam veren yoksa boş dizi döner.
 * Sonuçlar priority'ye göre sıralıdır (düşük → yüksek).
 */
export function getActiveAdvertisersForProvince(province: string | null): Advertiser[] {
  if (!province) return [];

  // İl adını normalize et (baş harfleri büyük, trim)
  const normalized = province
    .trim()
    .split(' ')
    .map(w => w.charAt(0).toLocaleUpperCase('tr-TR') + w.slice(1).toLocaleLowerCase('tr-TR'))
    .join(' ');

  const advertisers = PROVINCE_ADS.get(normalized) || PROVINCE_ADS.get(province.trim()) || [];

  return advertisers
    .filter(a => a.isActive)
    .sort((a, b) => a.priority - b.priority);
}

/**
 * Herhangi bir ilde aktif reklam veren olup olmadığını kontrol eder.
 * Genel "reklam sistemi aktif mi?" kontrolü için kullanılabilir.
 */
export function hasAnyActiveAdvertiser(): boolean {
  for (const [, advertisers] of PROVINCE_ADS) {
    if (advertisers.some(a => a.isActive)) return true;
  }
  return false;
}

/**
 * İletişim e-posta/bilgi (placeholder CTA'da gösterilir).
 */
export const AD_CONTACT_INFO = {
  email: 'info@tarimimar.com.tr',
  description: 'Bölgenizde tarımsal yapı hesaplaması yapan kullanıcılara ulaşın.',
};
