import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../services/api';

interface UniqueValidationResult {
  isChecking: boolean;
  isUnique: boolean | null;
  error: string;
}

export const useUniqueValidation = (
  value: string,
  endpoint: string,
  debounceMs: number = 500,
  currentValue?: string
): UniqueValidationResult => {
  const [isChecking, setIsChecking] = useState(false);
  const [isUnique, setIsUnique] = useState<boolean | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    // Eğer değer boş veya mevcut değer ile aynı ise kontrol etme
    if (!value || value === currentValue) {
      setIsChecking(false);
      setIsUnique(null);
      setError('');
      return;
    }

    // Debounce için timeout
    const timeoutId = setTimeout(async () => {
      setIsChecking(true);
      setError('');

      try {
        // API_BASE_URL imported from services/api
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            // Authorization header göndermeyin - AllowAny endpoint'leri için gerekli değil
          },
          body: JSON.stringify({ value }),
        });

        if (response.ok) {
          const data = await response.json();
          setIsUnique(data.is_unique);
          if (!data.is_unique) {
            setError(data.message || 'Bu değer zaten kullanılıyor');
          }
        } else {
          setError('Kontrol edilemedi');
          setIsUnique(null);
        }
      } catch (err) {
        setError('Bağlantı hatası');
        setIsUnique(null);
      } finally {
        setIsChecking(false);
      }
    }, debounceMs);

    return () => clearTimeout(timeoutId);
  }, [value, endpoint, currentValue, debounceMs]);

  return { isChecking, isUnique, error };
};
