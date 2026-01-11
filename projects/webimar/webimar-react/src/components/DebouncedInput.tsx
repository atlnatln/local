import React, { useState, useEffect, memo } from 'react';

interface DebouncedInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'onChange'> {
  onChange: (value: string) => void;
  delay?: number;
}

const DebouncedInput = memo<DebouncedInputProps>(({ 
  onChange, 
  delay = 300, 
  value: propValue = '', 
  ...props 
}) => {
  const [internalValue, setInternalValue] = useState(propValue.toString());

  // Prop value değiştiğinde internal value'yu güncelle
  useEffect(() => {
    setInternalValue(propValue.toString());
  }, [propValue]);

  // Debounced onChange effect
  useEffect(() => {
    if (internalValue === propValue.toString()) return; // Değişiklik yoksa skip
    
    const timeoutId = setTimeout(() => {
      onChange(internalValue);
    }, delay);

    return () => clearTimeout(timeoutId);
  }, [internalValue, onChange, delay, propValue]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInternalValue(e.target.value);
  };

  return (
    <input
      {...props}
      value={internalValue}
      onChange={handleInputChange}
    />
  );
});

DebouncedInput.displayName = 'DebouncedInput';

export default DebouncedInput;