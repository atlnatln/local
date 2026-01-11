import React, { useState, useEffect, useRef } from 'react';

interface DebouncedInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'onChange'> {
  value: string | number;
  onChange: (value: string) => void;
  debounce?: number;
}

export default function DebouncedInput({
  value: initialValue,
  onChange,
  debounce = 300,
  ...props
}: DebouncedInputProps) {
  const [value, setValue] = useState<string | number>(initialValue);
  const isTyping = useRef(false);

  useEffect(() => {
    if (!isTyping.current) {
      setValue(initialValue);
    }
  }, [initialValue]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setValue(newValue);
    isTyping.current = true;

    const timeoutId = setTimeout(() => {
      onChange(newValue);
      isTyping.current = false;
    }, debounce);

    // Clear previous timeout is handled by the fact that we create a new timeout
    // But we need to clear it if the component unmounts or value changes again
    // Actually, a simple debounce function wrapper is better.
  };

  // Better implementation using useEffect for debounce
  useEffect(() => {
    if (!isTyping.current) return;

    const timeout = setTimeout(() => {
      onChange(String(value));
      isTyping.current = false;
    }, debounce);

    return () => clearTimeout(timeout);
  }, [value, debounce, onChange]);

  return (
    <input
      {...props}
      value={value}
      onChange={(e) => {
        setValue(e.target.value);
        isTyping.current = true;
      }}
    />
  );
}
