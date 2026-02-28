/**
 * sync-llms.mjs
 *
 * sitemap.xml'den URL'leri okuyup llms.txt içindeki
 * [AUTO-URLS-START] … [AUTO-URLS-END] bloğunu otomatik günceller.
 *
 * Kullanım:  node scripts/sync-llms.mjs
 *  ya da:    npm run sync-llms
 *
 * Bağımlılık: SIFIR — yalnızca Node.js built-in modüller (fs, path, url)
 */

import { readFileSync, writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

// ── Sabit yollar ──────────────────────────────────────────────────────────────
const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT      = resolve(__dirname, '..');
const SITEMAP   = resolve(ROOT, 'public', 'sitemap.xml');
const LLMS      = resolve(ROOT, 'public', 'llms.txt');
const BASE_URL  = 'https://tarimimar.com.tr';

// ── Kategori sınıflandırma kuralları ─────────────────────────────────────────
// Her kural: { test: (path) => boolean, category: string }
// İlk eşleşen kategori kazanır.

const CATEGORY_RULES = [
  // 4.2 — karar destek araçları (slug bazlı kontrol, 4.1'den önce gelmeli)
  {
    cat: '4.2',
    label: 'Çiftlik/Hayvancılık ve Karar Destek Araçları',
    test: (p) =>
      [
        '/gubre-cukuru-hesaplama/',
        '/sigir-ahiri-kapasite-hesaplama/',
        '/buzagi-destegi-hesaplama/',
        '/aricilik-planlama/',
        '/ciceklenme-takvimi/',
      ].includes(p),
  },
  // 4.3 — bitkisel destekleme
  {
    cat: '4.3',
    label: 'Bitkisel Üretim Destekleme',
    test: (p) => ['/havza-bazli-destekleme-modeli/'].includes(p),
  },
  // 4.4 — mevzuat ve belgeler
  {
    cat: '4.4',
    label: 'Mevzuat ve Referans Belgeleri',
    test: (p) => p.startsWith('/documents/') || p.startsWith('/mevzuat/'),
  },
  // 4.6 — il sayfaları (4.5'ten ÖNCE)
  {
    cat: '4.6',
    label: 'Çevre Düzeni Planları - İl Sayfaları',
    test: (p) => p.startsWith('/cevre-duzeni-planlari/il/'),
  },
  // 4.5 — bölgesel çevre düzeni planları
  {
    cat: '4.5',
    label: 'Çevre Düzeni Planları - Bölgesel Sayfalar',
    test: (p) => p.startsWith('/cevre-duzeni-planlari/'),
  },
  // 4.7 — hukuki ve kurumsal
  {
    cat: '4.7',
    label: 'Hukuki ve Kurumsal Sayfalar',
    test: (p) =>
      [
        '/iletisim/',
        '/gizlilik-politikasi/',
        '/kvkk-aydinlatma/',
        '/cerez-politikasi/',
        '/kullanim-kosullari/',
      ].includes(p),
  },
  // 4.1 — yapı landing sayfaları (priority >= 0.9, slug-bazlı)
  // Ana sayfa '/' hariç tutulur — llms.txt manuel başlığında zaten var
  {
    cat: '4.1',
    label: 'Tarımsal Yapı Hesaplama Landing Sayfaları',
    test: (_p, priority) => priority >= 0.9,
  },
];

// ── sitemap.xml'i parse et ───────────────────────────────────────────────────

function parseSitemap(xmlContent) {
  /** Tüm <url> bloklarını { loc, priority } dizisi olarak döndürür */
  const urls = [];
  const urlBlocks = xmlContent.match(/<url[\s\S]*?<\/url>/g) ?? [];

  for (const block of urlBlocks) {
    const locMatch      = block.match(/<loc>\s*(.*?)\s*<\/loc>/);
    const priorityMatch = block.match(/<priority>\s*([\d.]+)\s*<\/priority>/);
    if (!locMatch) continue;

    const fullUrl  = locMatch[1].trim();
    const path     = fullUrl.replace(BASE_URL, '');
    const priority = priorityMatch ? parseFloat(priorityMatch[1]) : 0.5;

    urls.push({ fullUrl, path, priority });
  }

  return urls;
}

// ── URL'leri kategorilere ayır ───────────────────────────────────────────────

function categorize(urls) {
  /** Sonuç: Map<catId, { label, urls[] }> — sıralama CATEGORY_RULES ile aynı */
  const result = new Map();

  // Kategorileri sırayla oluştur (boş bile olsa sıra korunsun)
  for (const rule of CATEGORY_RULES) {
    result.set(rule.cat, { label: rule.label, urls: [] });
  }

  for (const entry of urls) {
    // Ana sayfayı atla — llms.txt manuel başlık bölümünde zaten tanımlanmış
    if (entry.path === '/') continue;

    for (const rule of CATEGORY_RULES) {
      if (rule.test(entry.path, entry.priority)) {
        result.get(rule.cat).urls.push(entry.fullUrl);
        break;
      }
    }
    // Hiçbir kurala uymayan URL'ler sessizce atlanır
  }

  return result;
}

// ── Yeni AUTO-URLS bloğunu üret ──────────────────────────────────────────────

function buildBlock(categorized) {
  const lines = [];

  // Kategori ID'lerini sayısal olarak sırala (4.1 < 4.2 < … < 4.7)
  const sortedEntries = [...categorized.entries()].sort(([a], [b]) => {
    const toNum = (id) => parseFloat(id); // "4.1" → 4.1
    return toNum(a) - toNum(b);
  });

  for (const [catId, { label, urls }] of sortedEntries) {
    if (urls.length === 0) continue;

    lines.push(`### ${catId}) ${label}`);
    for (const url of urls) {
      lines.push(`- ${url}`);
    }
    lines.push('');
  }

  // Son boş satırı kaldır
  while (lines.length > 0 && lines[lines.length - 1] === '') lines.pop();

  return lines.join('\n');
}

// ── llms.txt'i güncelle ──────────────────────────────────────────────────────

function updateLlms(llmsContent, newBlock) {
  const START_MARKER = '[AUTO-URLS-START]';
  const END_MARKER   = '[AUTO-URLS-END]';

  const startIdx = llmsContent.indexOf(START_MARKER);
  const endIdx   = llmsContent.indexOf(END_MARKER);

  if (startIdx === -1 || endIdx === -1) {
    throw new Error(
      `llms.txt içinde "${START_MARKER}" veya "${END_MARKER}" marker'ı bulunamadı.`,
    );
  }
  if (startIdx >= endIdx) {
    throw new Error('START marker END marker\'dan sonra geliyor — hatalı sıralama.');
  }

  const before  = llmsContent.slice(0, startIdx + START_MARKER.length);
  const after   = llmsContent.slice(endIdx);

  return `${before}\n${newBlock}\n${after}`;
}

// ── "Last updated" tarihini güncelle ─────────────────────────────────────────

function updateLastUpdated(content) {
  const today = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
  return content.replace(
    /Last updated:\s*\d{4}-\d{2}-\d{2}/g,
    `Last updated: ${today}`,
  );
}

// ── Ana akış ─────────────────────────────────────────────────────────────────

function main() {
  console.log('→ sitemap.xml okunuyor…');
  const xmlContent  = readFileSync(SITEMAP,  'utf8');

  console.log('→ llms.txt okunuyor…');
  let llmsContent   = readFileSync(LLMS, 'utf8');

  console.log('→ URL\'ler parse ediliyor…');
  const urls        = parseSitemap(xmlContent);
  console.log(`   ${urls.length} URL bulundu.`);

  const categorized = categorize(urls);

  // İstatistik yazdır
  let total = 0;
  for (const [catId, { urls: catUrls }] of categorized) {
    if (catUrls.length > 0) {
      console.log(`   ${catId}: ${catUrls.length} URL`);
      total += catUrls.length;
    }
  }
  console.log(`   Toplam kategorize: ${total} URL`);

  console.log('→ AUTO-URLS bloğu yeniden üretiliyor…');
  const newBlock    = buildBlock(categorized);

  console.log('→ llms.txt güncelleniyor…');
  llmsContent       = updateLlms(llmsContent, newBlock);
  llmsContent       = updateLastUpdated(llmsContent);

  writeFileSync(LLMS, llmsContent, 'utf8');
  console.log('✓ llms.txt başarıyla güncellendi:', LLMS);
}

main();
