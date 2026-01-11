// Tarımsal Amaçlı Depo specific form fields component
import React from 'react';
import FormField from './FormField';
import { FormGrid } from './styles';

interface TarimsalDepoFormFieldsProps {
  formData: any;
  validationErrors: Record<string, string>;
  onInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  renderSmartDetectionFeedback: (fieldName: string) => React.ReactNode;
  isFormDisabled?: boolean;
  onDisabledClick?: () => void;
}

const TarimsalDepoFormFields: React.FC<TarimsalDepoFormFieldsProps> = ({
  formData,
  validationErrors,
  onInputChange,
  renderSmartDetectionFeedback,
  isFormDisabled = false,
  onDisabledClick
}) => {
  // Tüm FormField'lar için ortak props
  const commonFieldProps = {
    disabled: isFormDisabled,
    onClick: onDisabledClick
  };

  return (
    <FormGrid>
      {/* Alan bilgileri - sadece belirli arazi tiplerinde göster */}
      {(formData.arazi_vasfi === 'Ham toprak, taşlık, kıraç, palamutluk, koruluk gibi diğer vasıflı' ||
        formData.arazi_vasfi === 'Tarla' ||
        formData.arazi_vasfi === 'Sera') && (
        <FormField
          label="Arazi Alanı (m²)"
          name="alan_m2"
          type="number"
          value={formData.alan_m2 || ''}
          onChange={onInputChange}
          placeholder="Örn: 5000"
          min="1"
          max="200000"
          step="1"
          required
          error={validationErrors.alan_m2}
          helpText="Toplam arazi alanınızı giriniz"
          {...commonFieldProps}
        >
          {renderSmartDetectionFeedback('alan_m2')}
        </FormField>
      )}

      {/* Tarla + Zeytinlik senaryosu için özel alanlar */}
      {formData.arazi_vasfi === 'Tarla + Zeytinlik' && (
        <>
          <FormField
            label="Tarla Alanı (m²)"
            name="tarla_alani"
            type="number"
            value={formData.tarla_alani || ''}
            onChange={onInputChange}
            placeholder="Tarla alanını giriniz"
            min="1"
            max="200000"
            step="1"
            required
            error={validationErrors.tarla_alani}
            {...commonFieldProps}
          >
            {renderSmartDetectionFeedback('tarla_alani')}
          </FormField>

          <FormField
            label="Zeytinlik Alanı (m²)"
            name="zeytinlik_alani"
            type="number"
            value={formData.zeytinlik_alani || ''}
            onChange={onInputChange}
            placeholder="Zeytinlik alanını giriniz"
            min="1"
            max="200000"
            step="1"
            required
            error={validationErrors.zeytinlik_alani}
            {...commonFieldProps}
          >
            {renderSmartDetectionFeedback('zeytinlik_alani')}
          </FormField>
        </>
      )}

      {/* Tarla + herhangi bir dikili vasıflı için alan girişleri */}
      {formData.arazi_vasfi === 'Tarla + herhangi bir dikili vasıflı' && (
        <>
          <FormField
            label="Tarla Alanı (m²)"
            name="tarla_alani"
            type="number"
            value={formData.tarla_alani || ''}
            onChange={onInputChange}
            placeholder="Örn: 15000"
            min="1"
            max="200000"
            step="1"
            required
            error={validationErrors.tarla_alani}
            helpText="Tarla alanınızı girin. Hesaplama sonucu pozitif veya negatif çıkabilir."
            {...commonFieldProps}
          >
            {renderSmartDetectionFeedback('tarla_alani')}
          </FormField>

          <FormField
            label="Dikili Alanı (m²)"
            name="dikili_alani"
            type="number"
            value={formData.dikili_alani || ''}
            onChange={onInputChange}
            placeholder="Örn: 12000"
            min="1"
            max="200000"
            step="1"
            required
            error={validationErrors.dikili_alani}
            {...commonFieldProps}
          >
            {renderSmartDetectionFeedback('dikili_alani')}
          </FormField>
        </>
      )}

      {/* Dikili alan için */}
      {(formData.arazi_vasfi === 'Dikili vasıflı' || 
        formData.arazi_vasfi === 'Zeytin ağaçlı + herhangi bir dikili vasıf' ||
        formData.arazi_vasfi === '… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf') && (
        <FormField
          label="Dikili Alanı (m²)"
          name="dikili_alani"
          type="number"
          value={formData.dikili_alani || ''}
          onChange={onInputChange}
          placeholder="Dikili alanını giriniz"
          min="1"
          max="200000"
          step="1"
          required
          error={validationErrors.dikili_alani}
          {...commonFieldProps}
        >
          {renderSmartDetectionFeedback('dikili_alani')}
        </FormField>
      )}

      {/* Zeytin ağaçlı + herhangi bir dikili vasıf için özel alanlar - Dikili alan ve zeytin ağacı sayısı */}
      {formData.arazi_vasfi === 'Zeytin ağaçlı + herhangi bir dikili vasıf' && (
        <FormField
          label="Zeytin Ağacı Sayısı (adet)"
          name="zeytin_agac_sayisi"
          type="number"
          value={formData.zeytin_agac_sayisi || ''}
          onChange={onInputChange}
          placeholder="Örn: 50"
          min="0"
          step="1"
          required
          error={validationErrors.zeytin_agac_sayisi}
          helpText="Zeytin ağacı sayınızı girin. Hesaplama sonucu pozitif veya negatif çıkabilir."
          {...commonFieldProps}
        />
      )}

      {/* Zeytin ağacı sayısı alanları */}
      {(formData.arazi_vasfi === '… Adetli Zeytin Ağacı bulunan tarla' ||
        formData.arazi_vasfi === '… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf') && (
        <>
          <FormField
            label="Tapu Zeytin Ağacı Adedi"
            name="tapu_zeytin_agac_adedi"
            type="number"
            value={formData.tapu_zeytin_agac_adedi || ''}
            onChange={onInputChange}
            placeholder="Tapudaki ağaç sayısı"
            min="1"
            step="1"
            required
            error={validationErrors.tapu_zeytin_agac_adedi}
            helpText="Tapu senesinde kayıtlı zeytin ağacı sayısı"
            {...commonFieldProps}
          />

          <FormField
            label="Mevcut Zeytin Ağacı Adedi"
            name="mevcut_zeytin_agac_adedi"
            type="number"
            value={formData.mevcut_zeytin_agac_adedi || ''}
            onChange={onInputChange}
            placeholder="Mevcut ağaç sayısı"
            min="1"
            step="1"
            required
            error={validationErrors.mevcut_zeytin_agac_adedi}
            helpText="Arazide mevcut bulunan zeytin ağacı sayısı. Dekara 10+ ağaç varsa izin verilmez."
            {...commonFieldProps}
          />
        </>
      )}

      {/* Zeytin ağaçlı + tarla için özel alanlar - Sadece tarla alanı ve zeytin ağacı sayısı */}
      {formData.arazi_vasfi === 'Zeytin ağaçlı + tarla' && (
        <>
          <FormField
            label="Tarla Alanı (m²)"
            name="tarla_alani"
            type="number"
            value={formData.tarla_alani || ''}
            onChange={onInputChange}
            placeholder="Örn: 25000"
            min="1"
            max="200000"
            step="1"
            required
            error={validationErrors.tarla_alani}
            helpText="Tarla alanınızı girin. Hesaplama sonucu pozitif veya negatif çıkabilir."
            {...commonFieldProps}
          />

          <FormField
            label="Zeytin Ağacı Sayısı (adet)"
            name="zeytin_agac_sayisi"
            type="number"
            value={formData.zeytin_agac_sayisi || ''}
            onChange={onInputChange}
            placeholder="Örn: 150"
            min="0"
            step="1"
            required
            error={validationErrors.zeytin_agac_sayisi}
            helpText="Zeytin ağacı sayınızı girin. Hesaplama sonucu pozitif veya negatif çıkabilir."
            {...commonFieldProps}
          />
        </>
      )}
    </FormGrid>
  );
};

export default TarimsalDepoFormFields;
