/**
 * Bağ Evi Form Field Component
 *
 * Bu bileşen bağ evi formları için yeniden kullanılabilir form alanları sağlar
 */

import React from 'react';
import styled from 'styled-components';

interface FormFieldProps {
  label: string;
  type?: string;
  value?: any;
  onChange?: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => void;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  error?: string;
  options?: { value: string; label: string }[];
  min?: number | string;
  max?: number | string;
  step?: number | string;
  name?: string;
  helpText?: string;
  className?: string;
  children?: React.ReactNode;
}

const FieldContainer = styled.div`
  margin-bottom: 1rem;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
`;

const Input = styled.input<{ $hasError?: boolean }>`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid ${props => props.$hasError ? '#ef4444' : '#d1d5db'};
  border-radius: 0.375rem;
  font-size: 0.875rem;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;

  &:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  &:disabled {
    background-color: #f9fafb;
    cursor: not-allowed;
  }
`;

const Select = styled.select<{ $hasError?: boolean }>`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid ${props => props.$hasError ? '#ef4444' : '#d1d5db'};
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background-color: white;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;

  &:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  &:disabled {
    background-color: #f9fafb;
    cursor: not-allowed;
  }
`;

const TextArea = styled.textarea<{ $hasError?: boolean }>`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid ${props => props.$hasError ? '#ef4444' : '#d1d5db'};
  border-radius: 0.375rem;
  font-size: 0.875rem;
  min-height: 100px;
  resize: vertical;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;

  &:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  &:disabled {
    background-color: #f9fafb;
    cursor: not-allowed;
  }
`;

const CheckboxContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const Checkbox = styled.input`
  width: 1rem;
  height: 1rem;
  accent-color: #3b82f6;
`;

const ErrorMessage = styled.div`
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #ef4444;
`;

const HelpText = styled.div`
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #6b7280;
`;

const FormField: React.FC<FormFieldProps> = ({
  label,
  type = 'text',
  value,
  onChange,
  placeholder,
  required = false,
  disabled = false,
  error,
  options = [],
  min,
  max,
  step,
  name,
  helpText,
  className,
  children
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    if (onChange) {
      // React event'i direkt olarak parent'a ilet - bu CalculationForm ile uyumlu
      onChange(e);
    }
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (onChange) {
      // Checkbox için özel handler - event'i direkt ilet
      onChange(e);
    }
  };

  const renderInput = () => {
    const commonProps = {
      value: value || '',
      onChange: handleChange,
      placeholder,
      disabled,
      required,
      className,
      $hasError: !!error,
      name
    };

    switch (type) {
      case 'select':
        return (
          <Select {...commonProps}>
            {options.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </Select>
        );

      case 'textarea':
        return (
          <TextArea {...commonProps} />
        );

      case 'checkbox':
        return (
          <CheckboxContainer>
            <Checkbox
              type="checkbox"
              checked={value || false}
              onChange={handleCheckboxChange}
              disabled={disabled}
              required={required}
            />
            <span>{label}</span>
          </CheckboxContainer>
        );

      default:
        return (
          <Input
            type={type}
            {...commonProps}
            min={min}
            max={max}
            step={step}
          />
        );
    }
  };

  // Checkbox için label'ı render etmeyiz çünkü zaten container içinde
  if (type === 'checkbox') {
    return (
      <FieldContainer className={className}>
        {renderInput()}
        {error && <ErrorMessage>{error}</ErrorMessage>}
        {helpText && <HelpText>{helpText}</HelpText>}
        {children}
      </FieldContainer>
    );
  }

  return (
    <FieldContainer className={className}>
      <Label>
        {label}
        {required && <span style={{ color: '#ef4444' }}> *</span>}
      </Label>
      {renderInput()}
      {error && <ErrorMessage>{error}</ErrorMessage>}
      {helpText && <HelpText>{helpText}</HelpText>}
      {children}
    </FieldContainer>
  );
};

export default FormField;
