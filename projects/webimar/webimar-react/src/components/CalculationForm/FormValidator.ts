import { DetailedCalculationInput, StructureType } from '../../types';
import { BagEviCalculator } from '../../modules/BagEvi';

// Validation logic separated from the main component
export class FormValidator {
  private bagEviCalculator: BagEviCalculator;
  
  constructor() {
    this.bagEviCalculator = new BagEviCalculator();
  }

  validateForm(
    formData: DetailedCalculationInput, 
    calculationType: StructureType
  ): { isValid: boolean; errors: Record<string, string> } {
    const errors: Record<string, string> = {};

    // Bağ evi için konsolide hesaplama motoru kullan
    if (calculationType === 'bag-evi') {
      const bagEviFormData = {
        calculationType,
        arazi_vasfi: formData.arazi_vasfi,
        alan_m2: formData.alan_m2,
        tarla_alani: formData.tarla_alani,
        dikili_alani: formData.dikili_alani,
        zeytinlik_alani: formData.zeytinlik_alani,
        zeytin_agac_sayisi: formData.zeytin_agac_sayisi,
        zeytin_agac_adedi: formData.zeytin_agac_adedi,
        tapu_zeytin_agac_adedi: formData.tapu_zeytin_agac_adedi,
        mevcut_zeytin_agac_adedi: formData.mevcut_zeytin_agac_adedi,
        manuel_kontrol_sonucu: formData.manuel_kontrol_sonucu,
        latitude: formData.latitude,
        longitude: formData.longitude
      };

      const validationResult = this.bagEviCalculator.validateForm(bagEviFormData);
      
      // Konsolide hesaplama motorundan gelen hataları mevcut format ile uyumlu hale getir
      validationResult.errors.forEach(error => {
        errors[error.field] = error.message;
      });

      // Uyarıları da errors nesnesine ekle (mevcut sistem sadece errors kullanıyor)
      validationResult.warnings.forEach(warning => {
        if (!errors[warning.field]) { // Sadece hata yoksa uyarı göster
          errors[warning.field] = warning.message;
        }
      });
    } else {
      // Diğer hesaplama tipleri için geleneksel validation
      
      // Alan_m2 validation - Genel validation
      if (!formData.alan_m2 || formData.alan_m2 <= 0) {
        errors.alan_m2 = 'Alan (m²) pozitif bir sayı olmalıdır';
      }

      if (!formData.arazi_vasfi) {
        errors.arazi_vasfi = 'Arazi vasfı seçilmelidir';
      }

      // Hububat silo için özel validation
      if (calculationType === 'hububat-silo') {
        if (!formData.silo_taban_alani_m2 || formData.silo_taban_alani_m2 <= 0) {
          errors.silo_taban_alani_m2 = 'Planlanan silo taban alanı pozitif bir sayı olmalıdır';
        }
      }

      // Sera için özel validation
      if (calculationType === 'sera') {
        if (!formData.sera_alani_m2 || formData.sera_alani_m2 <= 0) {
          errors.sera_alani_m2 = 'Planlanan sera alanı pozitif bir sayı olmalıdır';
        }
      }
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    };
  }
}

export default FormValidator;
