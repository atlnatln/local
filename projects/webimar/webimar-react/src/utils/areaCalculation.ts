// Area conversion and validation utilities
// Extracted from DikiliAlanKontrol.tsx for better separation of concerns
//
// NOT: Bağ evi spesifik hesaplamaları için bagEviCalculator.ts kullanın.
// Bu dosya genel alan hesaplamaları içindir.

export interface AreaValidationResult {
  isValid: boolean;
  error?: string;
}

export interface AreaConversion {
  m2: number;
  donum: number;
  hectare: number;
}

/**
 * Convert area between different units
 */
export const convertArea = (areaM2: number): AreaConversion => {
  return {
    m2: areaM2,
    donum: areaM2 / 1000, // 1 dönüm = 1000 m²
    hectare: areaM2 / 10000 // 1 hektar = 10000 m²
  };
};

/**
 * Format area for display with proper localization
 */
export const formatArea = (areaM2: number): { m2: string; donum: string; hectare: string } => {
  const conversion = convertArea(areaM2);
  
  return {
    m2: Math.round(conversion.m2).toLocaleString('tr-TR'),
    donum: conversion.donum.toFixed(1),
    hectare: conversion.hectare.toFixed(2)
  };
};

/**
 * Validate dikili alan input
 */
export const validateDikiliAlan = (dikiliAlan: number): AreaValidationResult => {
  if (dikiliAlan <= 0) {
    return {
      isValid: false,
      error: 'Dikili alan pozitif bir değer olmalıdır.'
    };
  }

  if (dikiliAlan < 1000) {
    return {
      isValid: false,
      error: 'Dikili alan çok küçük görünüyor. Lütfen değeri kontrol edin.'
    };
  }

  return { isValid: true };
};

/**
 * Validate tarla alan input
 * NOT: Proje kuralına göre tarla alanı ve dikili alan birbirinden bağımsızdır,
 * karşılaştırma kontrolü yapılmaz.
 */
export const validateTarlaAlani = (tarlaAlani: number, dikiliAlan?: number): AreaValidationResult => {
  if (tarlaAlani <= 0) {
    return {
      isValid: false,
      error: 'Tarla alanı pozitif bir değer olmalıdır.'
    };
  }

  // NOT: Tarla alanı ve dikili alan bağımsız alanlar olduğu için 
  // karşılaştırma kontrolü kaldırıldı (proje kuralı)
  // if (dikiliAlan && tarlaAlani < dikiliAlan) {
  //   return {
  //     isValid: false,
  //     error: 'Tarla alanı dikili alandan küçük olamaz. Tarla alanı toplam parsel büyüklüğüdür.'
  //   };
  // }

  if (tarlaAlani < 2000) {
    return {
      isValid: false,
      error: 'Tarla alanı çok küçük görünüyor. Lütfen değeri kontrol edin.'
    };
  }

  return { isValid: true };
};

/**
 * Calculate area percentage
 */
export const calculateAreaPercentage = (partialArea: number, totalArea: number): number => {
  if (totalArea <= 0) return 0;
  return Math.min((partialArea / totalArea) * 100, 100);
};

/**
 * Check if area meets minimum requirements for vineyard
 */
export const checkMinimumAreaRequirements = (dikiliAlan: number, tarlaAlani: number): {
  dikiliAlanYeterli: boolean;
  tarlaAlaniYeterli: boolean;
  genelDegerlendirme: 'yeterli' | 'kismen_yeterli' | 'yetersiz';
} => {
  const dikiliAlanYeterli = dikiliAlan >= 5000; // Minimum 5000 m²
  const tarlaAlaniYeterli = tarlaAlani >= 20000; // Büyük tarla kriteri

  let genelDegerlendirme: 'yeterli' | 'kismen_yeterli' | 'yetersiz';
  
  if (tarlaAlaniYeterli || dikiliAlanYeterli) {
    genelDegerlendirme = 'yeterli';
  } else if (dikiliAlan >= 3000 || tarlaAlani >= 10000) {
    genelDegerlendirme = 'kismen_yeterli';
  } else {
    genelDegerlendirme = 'yetersiz';
  }

  return {
    dikiliAlanYeterli,
    tarlaAlaniYeterli,
    genelDegerlendirme
  };
};

/**
 * Generate area summary for display
 */
export const generateAreaSummary = (dikiliAlan: number, tarlaAlani: number): string => {
  const dikiliFormatted = formatArea(dikiliAlan);
  const tarlaFormatted = formatArea(tarlaAlani);
  const toplamFormatted = formatArea(dikiliAlan + tarlaAlani);

  return `
    📊 Alan Özeti:
    • Dikili Alan: ${dikiliFormatted.m2} m² (${dikiliFormatted.donum} dönüm)
    • Tarla Alanı: ${tarlaFormatted.m2} m² (${tarlaFormatted.donum} dönüm)
    • Toplam Parsel: ${toplamFormatted.m2} m² (${toplamFormatted.donum} dönüm)
  `.trim();
};
