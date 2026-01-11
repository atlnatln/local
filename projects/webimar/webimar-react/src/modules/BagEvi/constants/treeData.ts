/**
 * Bağ Evi Hesaplamaları - Ağaç Verisi
 * 
 * Bu dosya bağ evi için gerekli ağaç türü ve yoğunluk bilgilerini içerir
 * Veri kaynağı: dikili_arazi_agac_sayilari.md
 */

import { AgacVerisi } from '../types';

/**
 * Bağ evi hesaplamaları için ağaç verisi (1000 m² için gerekli adet)
 */
export const getDefaultTreeData = (): AgacVerisi[] => {
  return [
    { sira: 1, tur: "Kestane", normal: 20 },
    { sira: 2, tur: "Harnup", normal: 21 },
    { sira: 3, tur: "İncir (Kurutmalık)", normal: 16 },
    { sira: 4, tur: "İncir (Taze)", normal: 18 },
    { sira: 5, tur: "Armut", normal: 20, bodur: 220, yariBodur: 70 },
    { sira: 6, tur: "Elma", normal: 20, bodur: 220, yariBodur: 80 },
    { sira: 7, tur: "Trabzon Hurması", normal: 40 },
    { sira: 8, tur: "Kiraz", normal: 25, bodur: 50, yariBodur: 33 },
    { sira: 9, tur: "Ayva", normal: 24, bodur: 100 },
    { sira: 10, tur: "Nar", normal: 40 },
    { sira: 11, tur: "Erik", normal: 18, bodur: 100, yariBodur: 34 },
    { sira: 12, tur: "Kayısı", normal: 16, bodur: 50, yariBodur: 30 },
    { sira: 13, tur: "Zerdali", normal: 20, bodur: 50, yariBodur: 30 },
    { sira: 14, tur: "Muşmula", normal: 25 },
    { sira: 15, tur: "Yenidünya", normal: 21 },
    { sira: 16, tur: "Şeftali", normal: 40, bodur: 100, yariBodur: 67 },
    { sira: 17, tur: "Vişne", normal: 18, bodur: 60, yariBodur: 40 },
    { sira: 18, tur: "Ceviz", normal: 10 },
    { sira: 19, tur: "Dut", normal: 20 },
    { sira: 20, tur: "Üvez", normal: 40 },
    { sira: 21, tur: "Ünnap", normal: 40 },
    { sira: 22, tur: "Kızılcık", normal: 40 },
    { sira: 23, tur: "Limon", normal: 21 },
    { sira: 24, tur: "Portakal", normal: 27 },
    { sira: 25, tur: "Turunç", normal: 27 },
    { sira: 26, tur: "Altıntop", normal: 21 },
    { sira: 27, tur: "Mandarin", normal: 27 },
    { sira: 28, tur: "Avokado", normal: 21 },
    { sira: 29, tur: "Fındık (Düz)", normal: 30 },
    { sira: 30, tur: "Fındık (Eğimli)", normal: 50 },
    { sira: 31, tur: "Gül", normal: 300, yariBodur: 750 },
    { sira: 32, tur: "Çay", normal: 1800 },
    { sira: 33, tur: "Kivi", normal: 60 },
    { sira: 34, tur: "Böğürtlen", normal: 220 },
    { sira: 35, tur: "Ahududu", normal: 600 },
    { sira: 36, tur: "Likapa", normal: 260 },
    { sira: 37, tur: "Muz (Örtü altı)", normal: 170 },
    { sira: 38, tur: "Muz (Açıkta)", normal: 200 },
    { sira: 39, tur: "Kuşburnu", normal: 111 },
    { sira: 40, tur: "Mürver", normal: 85 },
    { sira: 41, tur: "Frenk Üzümü", normal: 220 },
    { sira: 42, tur: "Bektaşi Üzümü", normal: 220 },
    { sira: 43, tur: "Aronya", normal: 170 }
  ];
};

/**
 * Belirli ağaç türü için mevcut alt türleri getir
 */
export const getAvailableTreeTypes = (agacTuruId: string, agacVerileri: AgacVerisi[]) => {
  const agac = agacVerileri.find(a => a.sira.toString() === agacTuruId);
  if (!agac) return [];
  
  const tipler = [];
  if (agac.normal) tipler.push({ value: 'normal', label: 'Normal' });
  if (agac.bodur) tipler.push({ value: 'bodur', label: 'Bodur' });
  if (agac.yariBodur) tipler.push({ value: 'yaribodur', label: 'Yarı Bodur' });
  
  return tipler;
};

/**
 * Ağaç türü ID'sinden ağaç türü adını getir
 */
export const getAgacAdiFromId = (turid: string, agacVerileri: AgacVerisi[]): string => {
  const agac = agacVerileri.find(a => a.sira.toString() === turid);
  return agac ? agac.tur : `Bilinmeyen Ağaç (${turid})`;
};

/**
 * Ağaç türü ve tipi için gerekli ağaç sayısını getir (1000m² için)
 */
export const getGerekliAgacSayisi = (
  turid: string, 
  tipi: 'normal' | 'bodur' | 'yaribodur', 
  agacVerileri: AgacVerisi[]
): number => {
  const agac = agacVerileri.find(a => a.sira.toString() === turid);
  if (!agac) return 0;
  
  switch (tipi) {
    case 'normal': return agac.normal || 0;
    case 'bodur': return agac.bodur || 0;
    case 'yaribodur': return agac.yariBodur || 0;
    default: return 0;
  }
};
