// Kimlik doğrulama ile ilgili API fonksiyonları

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

// Kullanıcı kayıt interface'i
export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

// Kullanıcı giriş interface'i
export interface LoginData {
  username: string;
  password: string;
}

// Şifre değiştirme interface'i
export interface ChangePasswordData {
  current_password: string;
  new_password: string;
}

// Kullanıcı kayıt fonksiyonu
export const register = async (data: RegisterData) => {
  const response = await fetch(`${API_BASE_URL}/accounts/register/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Kayıt başarısız');
  }

  return response.json();
};

// Kullanıcı giriş fonksiyonu
export const login = async (data: LoginData) => {
  console.warn('Legacy login() çağrısı engellendi.', { username: data.username });
  throw new Error('Mail/şifre girişi kapalı. Lütfen Google ile giriş yapın.');
};

// Kullanıcı çıkış fonksiyonu
export const logout = async (token: string) => {
  const response = await fetch(`${API_BASE_URL}/accounts/me/logout/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Çıkış başarısız');
  }

  return response.json();
};

// Şifre değiştirme fonksiyonu
export const changePassword = async (token: string, data: ChangePasswordData) => {
  const response = await fetch(`${API_BASE_URL}/accounts/me/change-password/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Şifre değiştirme başarısız');
  }

  return response.json();
};

// Kullanıcı oturumları fonksiyonu
export const getUserSessions = async (token: string) => {
  const response = await fetch(`${API_BASE_URL}/accounts/me/sessions/`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Oturumlar alınamadı');
  }

  return response.json();
};

// Oturum sonlandırma fonksiyonu
export const terminateSession = async (token: string, sessionKey: string) => {
  const response = await fetch(`${API_BASE_URL}/accounts/me/sessions/${sessionKey}/`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Oturum sonlandırılamadı');
  }

  return response.json();
};

// Kullanıcı adı benzersizlik kontrolü
export const checkUsernameUnique = async (username: string) => {
  const response = await fetch(`${API_BASE_URL}/accounts/check-username/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ value: username }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Kontrol başarısız');
  }

  return response.json();
};

// E-posta benzersizlik kontrolü
export const checkEmailUnique = async (email: string) => {
  const response = await fetch(`${API_BASE_URL}/accounts/check-email/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ value: email }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Kontrol başarısız');
  }

  return response.json();
};

// Diğer API fonksiyonları için re-export
export * from '../services/api';
