import React from 'react';
import styled from 'styled-components';

const Input = styled.input<{ $hasError?: boolean }>`
  padding: 12px 16px;
  border: 2px solid ${props => props.$hasError ? '#dc2626' : '#d1d5db'};
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.2s;
  width: 100%;
  &:focus {
    outline: none;
    border-color: ${props => props.$hasError ? '#dc2626' : '#2563eb'};
  }
`;

const Label = styled.label`
  color: #374151;
  font-weight: 600;
  margin-bottom: 8px;
  font-size: 14px;
`;

const ErrorText = styled.span`
  color: #dc2626;
  font-size: 14px;
  margin-top: 4px;
`;

interface AuthFormInputProps {
  id: string;
  label: string;
  type?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  error?: string;
  maxLength?: number;
}

const AuthFormInput: React.FC<AuthFormInputProps> = ({
  id, label, type = 'text', value, onChange, placeholder, error, maxLength
}) => (
  <div style={{ marginBottom: 16 }}>
    <Label htmlFor={id}>{label}</Label>
    <Input
      id={id}
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      $hasError={!!error}
      maxLength={maxLength}
    />
    {error && <ErrorText>{error}</ErrorText>}
  </div>
);

export default AuthFormInput;
