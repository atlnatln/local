const fs = require('fs');

// GeoJSON ve havza verilerini oku
const geoData = JSON.parse(fs.readFileSync('/home/akn/vps/projects/webimar/webimar-nextjs/public/turkey-districts.geojson', 'utf8'));
const havzaData = JSON.parse(fs.readFileSync('/home/akn/vps/projects/webimar/webimar-nextjs/public/havza_urun_desen.json', 'utf8'));

// Normalizasyon fonksiyonu
function normalizeName(name) {
  if (!name) return '';
  return name
    .toLocaleUpperCase('tr-TR')
    .replace(/\s+/g, '')
    .trim();
}

// GeoJSON'dan il/ilçe listesi oluştur
const geoDistricts = new Map();
const geoProvinces = new Set();

geoData.features.forEach(feature => {
  const il = feature.properties.ADM1_TR;
  const ilce = feature.properties.ADM2_TR;
  
  geoProvinces.add(il);
  
  if (!geoDistricts.has(il)) {
    geoDistricts.set(il, new Set());
  }
  geoDistricts.get(il).add(ilce);
});

// Havza verisinden il/ilçe listesi oluştur
const havzaDistricts = new Map();
const havzaProvinces = new Set();

Object.keys(havzaData).forEach(il => {
  havzaProvinces.add(il);
  
  if (!havzaDistricts.has(il)) {
    havzaDistricts.set(il, new Set());
  }
  
  if (havzaData[il]) {
    Object.keys(havzaData[il]).forEach(ilce => {
      havzaDistricts.get(il).add(ilce);
    });
  }
});

console.log('=== VERİ ANALİZİ ===\n');

console.log(`GeoJSON'da toplam il sayısı: ${geoProvinces.size}`);
console.log(`Havza verisinde toplam il sayısı: ${havzaProvinces.size}\n`);

// Eksik iller
const eksikIller = [];
geoProvinces.forEach(il => {
  if (!havzaProvinces.has(il)) {
    eksikIller.push(il);
  }
});

if (eksikIller.length > 0) {
  console.log(`Havza verisinde eksik iller (${eksikIller.length}):`, eksikIller);
}

// Her il için eksik ilçeleri bul
let toplamGeoIlce = 0;
let toplamHavzaIlce = 0;
let toplamEksikIlce = 0;

const ilBazindaAnaliz = [];

geoDistricts.forEach((ilceler, il) => {
  const geoIlceCount = ilceler.size;
  const havzaIlceler = havzaDistricts.get(il) || new Set();
  const havzaIlceCount = havzaIlceler.size;
  const eksikIlceler = [];
  
  ilceler.forEach(ilce => {
    if (!havzaIlceler.has(ilce)) {
      eksikIlceler.push(ilce);
    }
  });
  
  toplamGeoIlce += geoIlceCount;
  toplamHavzaIlce += havzaIlceCount;
  toplamEksikIlce += eksikIlceler.length;
  
  if (eksikIlceler.length > 0) {
    ilBazindaAnaliz.push({
      il,
      geoIlceCount,
      havzaIlceCount,
      eksikCount: eksikIlceler.length,
      eksikIlceler: eksikIlceler.slice(0, 5), // İlk 5 tanesini göster
      coveragePercent: Math.round((havzaIlceCount / geoIlceCount) * 100)
    });
  }
});

console.log(`\nTOPLAM İSTATİSTİK:`);
console.log(`- GeoJSON toplam ilçe: ${toplamGeoIlce}`);
console.log(`- Havza verisi toplam ilçe: ${toplamHavzaIlce}`);
console.log(`- Eksik ilçe sayısı: ${toplamEksikIlce}`);
console.log(`- Kapsam oranı: %${Math.round((toplamHavzaIlce / toplamGeoIlce) * 100)}\n`);

// En fazla eksik olan ilk 10 ili göster
ilBazindaAnaliz
  .sort((a, b) => b.eksikCount - a.eksikCount)
  .slice(0, 10)
  .forEach(analiz => {
    console.log(`${analiz.il}: ${analiz.havzaIlceCount}/${analiz.geoIlceCount} (%${analiz.coveragePercent}) - Eksik: ${analiz.eksikCount}`);
    if (analiz.eksikIlceler.length > 0) {
      console.log(`  Eksik ilçeler: ${analiz.eksikIlceler.join(', ')}${analiz.eksikCount > 5 ? '...' : ''}`);
    }
  });