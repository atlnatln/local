import React, { memo } from 'react';
import { FormGroup, Label, Input, ErrorMessage, RequiredIndicator } from './styles';
import DebouncedInput from '../DebouncedInput';

interface FormFieldProps {
  label: string;
  name: string;
  type?: 'text' | 'number' | 'email';
  value: string | number;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  required?: boolean;
  min?: string;
  max?: string;
  step?: string;
  error?: string;
  helpText?: string;
  children?: React.ReactNode; // For additional content like smart detection feedback
  disabled?: boolean; // Form alanının devre dışı bırakılması için
  onClick?: () => void; // Devre dışı durumdayken tıklanınca çağrılacak fonksiyon
  useDebounce?: boolean; // Debouncing kullanılıp kullanılmayacağı
}

// 🚀 OPTIMIZATION: React.memo ile unnecessary re-renders'ı engelle
const FormField = memo<FormFieldProps>(({
  label,
  name,
  type = 'text',
  value,
  onChange,
  placeholder,
  required = false,
  min,
  max,
  step,
  error,
  helpText,
  children,
  disabled = false,
  onClick,
  useDebounce = true // Default olarak debouncing kullan
}) => {
  const handleClick = () => {
    if (disabled && onClick) {
      onClick();
    }
  };

  // 🔒 Güvenli onChange wrapper - event undefined kontrolü burada yapılıyor
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Event validation - FormField seviyesinde güvenlik kontrolü
    if (!e || !e.target) {
      console.error('❌ FormField handleChange: Event or target is undefined', {
        name,
        eventExists: !!e,
        targetExists: e && !!e.target
      });
      return;
    }

    // Event'i parent onChange'e güvenli şekilde ilet
    onChange(e);
  };

  const renderInput = () => {
    // Number input'lar için debouncing kullan (performans optimizasyonu)
    if (useDebounce && type === 'number') {
      return (
        <DebouncedInput
          type={type}
          name={name}
          value={value || ''}
          onChange={(newValue) => {
            // DebouncedInput string döndürür, onu event formatına çevir
            const mockEvent = {
              target: {
                name,
                value: newValue,
                type
              }
            } as React.ChangeEvent<HTMLInputElement>;
            onChange(mockEvent);
          }}
          placeholder={placeholder}
          min={min}
          max={max}
          step={step}
          required={required}
          disabled={disabled}
          onClick={handleClick}
          style={{
            opacity: disabled ? 0.5 : 1,
            cursor: disabled ? 'not-allowed' : 'text',
            backgroundColor: disabled ? '#f5f5f5' : undefined,
            // FormField styling'i korumak için
            width: '100%',
            padding: '12px 16px',
            border: '1px solid #d1d5db',
            borderRadius: '8px',
            fontSize: '14px',
            transition: 'border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out',
          }}
        />
      );
    }

    // Diğer input türleri için standard Input component
    return (
      <Input
        type={type}
        name={name}
        value={value || ''}
        onChange={handleChange} // Güvenli wrapper kullanılıyor
        placeholder={placeholder}
        min={min}
        max={max}
        step={step}
        required={required}
        disabled={disabled}
        onClick={handleClick}
        style={{
          opacity: disabled ? 0.5 : 1,
          cursor: disabled ? 'not-allowed' : 'text',
          backgroundColor: disabled ? '#f5f5f5' : undefined
        }}
      />
    );
  };

  return (
    <FormGroup>
      <Label>
        {label} {required && <RequiredIndicator>*</RequiredIndicator>}
      </Label>
      {renderInput()}
      {error && <ErrorMessage>{error}</ErrorMessage>}
      {children}
      {helpText && (
        <div style={{ fontSize: '12px', color: '#777', marginTop: '4px' }}>
          {helpText}
        </div>
      )}
    </FormGroup>
  );
}); // memo closing

// 🚀 Display name for React DevTools
FormField.displayName = 'FormField';

export default FormField;
