/**
 * Bağ Evi Hesaplamaları - Validation Fonksiyonları
 */

import { 
  BagEviFormData, 
  BagEviValidationResult, 
  BagEviValidationError 
} from '../types';

import { 
  MINIMUM_DIKILI_ALAN,
  BUYUK_TARLA_ALANI,
  MAX_ZEYTIN_AGAC_YOGUNLUGU,
  VALIDATION_MESSAGES 
} from '../constants';

/**
 * Ana bağ evi form validation fonksiyonu
 */
export const validateBagEviForm = (formData: BagEviFormData): BagEviValidationResult => {
  const errors: BagEviValidationError[] = [];
  const warnings: BagEviValidationError[] = [];

  // Arazi vasfı kontrolü
  if (!formData.arazi_vasfi) {
    errors.push({
      field: 'arazi_vasfi',
      message: 'Lütfen arazi vasfını seçin.',
      type: 'error'
    });
  }

  // Arazi vasfına göre özel kontroller
  switch (formData.arazi_vasfi) {
    case 'Dikili vasıflı':
      validateDikiliVasifli(formData, errors, warnings);
      break;
    case 'Tarla':
      validateTarla(formData, errors, warnings);
      break;
    case 'Sera':
      validateSera(formData, errors, warnings);
      break;
    case 'Tarla + herhangi bir dikili vasıflı':
      validateTarlaDikili(formData, errors, warnings);
      break;
    case '… Adetli Zeytin Ağacı bulunan tarla':
      validateZeytinliTarla(formData, errors, warnings);
      break;
  }

  // Genel alan kontrolleri
  validateGeneral(formData, errors, warnings);

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  };
};

/**
 * Dikili vasıflı arazi validation
 */
const validateDikiliVasifli = (
  formData: BagEviFormData, 
  errors: BagEviValidationError[], 
  warnings: BagEviValidationError[]
) => {
  if (!formData.alan_m2 || formData.alan_m2 <= 0) {
    errors.push({
      field: 'alan_m2',
      message: 'Dikili alan pozitif bir sayı olmalıdır.',
      type: 'error'
    });
  }

  // Minimum alan kontrolü
  if (formData.alan_m2 && formData.alan_m2 < MINIMUM_DIKILI_ALAN) {
    warnings.push({
      field: 'alan_m2',
      message: VALIDATION_MESSAGES.MIN_ALAN_DIKILI,
      type: 'warning'
    });
  }

  // Zeytin ağacı yoğunluk kontrolü
  if (formData.alan_m2 && formData.zeytin_agac_adedi && formData.zeytin_agac_adedi > 0) {
    const agacYogunlugu = (formData.zeytin_agac_adedi / formData.alan_m2) * 1000;
    if (agacYogunlugu > MAX_ZEYTIN_AGAC_YOGUNLUGU) {
      errors.push({
        field: 'zeytin_agac_adedi',
        message: `Dekara ${MAX_ZEYTIN_AGAC_YOGUNLUGU} ağaçtan fazla zeytin ağacı olamaz.`,
        type: 'error'
      });
    }
  }
};

/**
 * Tarla arazi validation
 */
const validateTarla = (
  formData: BagEviFormData, 
  errors: BagEviValidationError[], 
  warnings: BagEviValidationError[]
) => {
  if (!formData.alan_m2 || formData.alan_m2 <= 0) {
    errors.push({
      field: 'alan_m2',
      message: 'Tarla alanı pozitif bir sayı olmalıdır.',
      type: 'error'
    });
  }

  // Minimum alan kontrolü
  if (formData.alan_m2 && formData.alan_m2 < BUYUK_TARLA_ALANI) {
    warnings.push({
      field: 'alan_m2',
      message: VALIDATION_MESSAGES.MIN_ALAN_TARLA,
      type: 'warning'
    });
  }
};

/**
 * Sera validation
 */
const validateSera = (
  formData: BagEviFormData, 
  errors: BagEviValidationError[], 
  warnings: BagEviValidationError[]
) => {
  if (!formData.sera_alani || formData.sera_alani <= 0) {
    errors.push({
      field: 'sera_alani',
      message: 'Sera alanı pozitif bir sayı olmalıdır.',
      type: 'error'
    });
  }

  // Minimum sera alanı kontrolü
  if (formData.sera_alani && formData.sera_alani < 3000) {
    warnings.push({
      field: 'sera_alani',
      message: VALIDATION_MESSAGES.MIN_ALAN_SERA,
      type: 'warning'
    });
  }
};

/**
 * Tarla + dikili validation
 */
const validateTarlaDikili = (
  formData: BagEviFormData, 
  errors: BagEviValidationError[], 
  warnings: BagEviValidationError[]
) => {
  if (!formData.tarla_alani || formData.tarla_alani <= 0) {
    errors.push({
      field: 'tarla_alani',
      message: 'Tarla alanı pozitif bir sayı olmalıdır.',
      type: 'error'
    });
  }
  
  if (!formData.dikili_alani || formData.dikili_alani <= 0) {
    errors.push({
      field: 'dikili_alani',
      message: 'Dikili alan pozitif bir sayı olmalıdır.',
      type: 'error'
    });
  }
};

/**
 * Zeytinli tarla validation
 */
const validateZeytinliTarla = (
  formData: BagEviFormData, 
  errors: BagEviValidationError[], 
  warnings: BagEviValidationError[]
) => {
  if (!formData.tarla_alani || formData.tarla_alani <= 0) {
    errors.push({
      field: 'tarla_alani',
      message: 'Tarla alanı pozitif bir sayı olmalıdır.',
      type: 'error'
    });
  }

  // Zeytin ağacı sayısı kontrolleri
  if (formData.tapu_zeytin_agac_adedi !== undefined && formData.tapu_zeytin_agac_adedi < 0) {
    errors.push({
      field: 'tapu_zeytin_agac_adedi',
      message: 'Tapu zeytin ağacı sayısı 0 veya pozitif olmalıdır.',
      type: 'error'
    });
  }

  if (formData.mevcut_zeytin_agac_adedi !== undefined && formData.mevcut_zeytin_agac_adedi < 0) {
    errors.push({
      field: 'mevcut_zeytin_agac_adedi',
      message: 'Mevcut zeytin ağacı sayısı 0 veya pozitif olmalıdır.',
      type: 'error'
    });
  }

  // Zeytin ağacı yoğunluk kontrolü
  if (formData.tarla_alani && formData.mevcut_zeytin_agac_adedi) {
    const agacYogunlugu = (formData.mevcut_zeytin_agac_adedi / formData.tarla_alani) * 1000;
    if (agacYogunlugu > MAX_ZEYTIN_AGAC_YOGUNLUGU) {
      errors.push({
        field: 'mevcut_zeytin_agac_adedi',
        message: `Dekara ${MAX_ZEYTIN_AGAC_YOGUNLUGU} ağaçtan fazla zeytin ağacı olamaz.`,
        type: 'error'
      });
    }
  }
};

/**
 * Genel validation kontrolleri
 */
const validateGeneral = (
  formData: BagEviFormData, 
  errors: BagEviValidationError[], 
  warnings: BagEviValidationError[]
) => {
  // Negatif değer kontrolleri
  const numberFields = ['alan_m2', 'bag_alani_m2', 'dikili_alani', 'tarla_alani', 'zeytinlik_alani'];
  
  numberFields.forEach(field => {
    const value = (formData as any)[field];
    if (value !== undefined && value < 0) {
      errors.push({
        field,
        message: VALIDATION_MESSAGES.NEGATIVE_VALUE,
        type: 'error'
      });
    }
  });

  // Koordinat kontrolleri
  if (formData.latitude !== undefined) {
    if (formData.latitude < -90 || formData.latitude > 90) {
      errors.push({
        field: 'latitude',
        message: 'Enlem -90 ile 90 arasında olmalıdır.',
        type: 'error'
      });
    }
  }

  if (formData.longitude !== undefined) {
    if (formData.longitude < -180 || formData.longitude > 180) {
      errors.push({
        field: 'longitude', 
        message: 'Boylam -180 ile 180 arasında olmalıdır.',
        type: 'error'
      });
    }
  }
};
