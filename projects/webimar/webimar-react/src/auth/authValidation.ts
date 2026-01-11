// Kimlik doğrulama ile ilgili validasyon fonksiyonları

export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

// E-posta validasyonu
export const validateEmail = (email: string): ValidationResult => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  
  if (!email.trim()) {
    return {
      isValid: false,
      error: 'E-posta adresi gereklidir.'
    };
  }
  
  if (!emailRegex.test(email)) {
    return {
      isValid: false,
      error: 'Geçerli bir e-posta adresi girin.'
    };
  }
  
  return {
    isValid: true
  };
};

// Kullanıcı adı validasyonu
export const validateUsername = (username: string): ValidationResult => {
  if (!username.trim()) {
    return {
      isValid: false,
      error: 'Kullanıcı adı gereklidir.'
    };
  }
  
  if (username.length < 3) {
    return {
      isValid: false,
      error: 'Kullanıcı adı en az 3 karakter olmalıdır.'
    };
  }
  
  if (username.length > 30) {
    return {
      isValid: false,
      error: 'Kullanıcı adı en fazla 30 karakter olabilir.'
    };
  }
  
  // Sadece harf, rakam ve alt çizgi (backend ile uyumlu)
  const usernameRegex = /^[a-zA-Z0-9_]+$/;
  if (!usernameRegex.test(username)) {
    return {
      isValid: false,
      error: 'Kullanıcı adı sadece harf, rakam ve alt çizgi (_) içerebilir. Türkçe karakterler desteklenmemektedir.'
    };
  }
  
  return {
    isValid: true
  };
};

// Şifre validasyonu
export const validatePassword = (password: string): ValidationResult => {
  if (!password) {
    return {
      isValid: false,
      error: 'Şifre gereklidir.'
    };
  }
  
  // En az 4 karakter olmalı (tüm karakterler kabul edilir)
  if (password.length < 4) {
    return {
      isValid: false,
      error: 'Şifre en az 4 karakter olmalıdır.'
    };
  }
  
  return {
    isValid: true
  };
};

// Şifre onay validasyonu
export const validatePasswordConfirm = (password: string, confirmPassword: string): ValidationResult => {
  if (!confirmPassword) {
    return {
      isValid: false,
      error: 'Şifre onayı gereklidir.'
    };
  }
  
  if (password !== confirmPassword) {
    return {
      isValid: false,
      error: 'Şifreler uyuşmuyor.'
    };
  }
  
  return {
    isValid: true
  };
};
