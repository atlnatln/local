// UI Message Constants
// Standardized messages for consistent user experience

export const UI_MESSAGES = {
  // Authentication Messages
  AUTH: {
    LOGIN_SUCCESS: 'Giriş başarılı',
    LOGIN_FAILED: 'Giriş başarısız. Kullanıcı adı ve şifrenizi kontrol edin.',
    LOGOUT_SUCCESS: 'Başarıyla çıkış yapıldı',
    REGISTER_SUCCESS: 'Kayıt başarılı! Giriş yapabilirsiniz.',
    REGISTER_FAILED: 'Kayıt başarısız. Bilgilerinizi kontrol edin.',
    SESSION_EXPIRED: 'Oturumunuz sona erdi. Lütfen tekrar giriş yapın.',
    UNAUTHORIZED: 'Bu işlem için giriş yapmanız gerekiyor.',
  },

  // Calculation Messages
  CALCULATION: {
    SAVE_SUCCESS: 'Hesaplama başarıyla kaydedildi!',
    SAVE_FAILED: 'Hesaplama kaydedilemedi',
    DELETE_SUCCESS: 'Hesaplama başarıyla silindi.',
    DELETE_FAILED: 'Hesaplama silinirken hata oluştu.',
    COPY_SUCCESS: 'Hesaplama kopyalandı!',
    COPY_FAILED: 'Kopyalama başarısız',
    LOAD_FAILED: 'Hesaplamalar yüklenirken hata oluştu.',
  },

  // Email Messages
  EMAIL: {
    VERIFICATION_SENT: 'E-posta doğrulama maili gönderildi.',
    VERIFICATION_SUCCESS: 'E-posta başarıyla doğrulandı.',
    VERIFICATION_FAILED: 'E-posta doğrulama başarısız.',
    CHANGE_SUCCESS: 'E-posta değişiklik talebiniz alındı.',
    CHANGE_FAILED: 'E-posta değiştirilemedi.',
  },

  // Password Messages
  PASSWORD: {
    RESET_SENT: 'Şifre sıfırlama maili gönderildi.',
    RESET_SUCCESS: 'Şifreniz başarıyla güncellendi.',
    RESET_FAILED: 'Şifre sıfırlama başarısız.',
    CHANGE_SUCCESS: 'Şifreniz başarıyla değiştirildi.',
    CHANGE_FAILED: 'Şifre değiştirilemedi.',
  },

  // Profile Messages
  PROFILE: {
    UPDATE_SUCCESS: 'Profiliniz güncellendi.',
    UPDATE_FAILED: 'Profil güncellenemedi.',
    LOAD_FAILED: 'Profil bilgileri yüklenemedi.',
  },

  // General Messages
  GENERAL: {
    LOADING: 'Yükleniyor...',
    SAVING: 'Kaydediliyor...',
    PROCESSING: 'İşleniyor...',
    ERROR_OCCURRED: 'Bir hata oluştu.',
    NETWORK_ERROR: 'Bağlantı hatası. İnternet bağlantınızı kontrol edin.',
    SERVER_ERROR: 'Sunucu hatası. Lütfen daha sonra tekrar deneyin.',
    VALIDATION_ERROR: 'Girilen bilgilerde hata var.',
    REQUIRED_FIELD: 'Bu alan zorunludur.',
    INVALID_FORMAT: 'Geçersiz format.',
  },

  // Form Messages
  FORM: {
    REQUIRED: 'Bu alan zorunludur',
    INVALID_EMAIL: 'Geçerli bir e-posta adresi girin',
    PASSWORD_MISMATCH: 'Şifreler eşleşmiyor',
    PASSWORD_TOO_SHORT: 'Şifre en az 8 karakter olmalıdır',
    USERNAME_TAKEN: 'Bu kullanıcı adı alınmış',
    EMAIL_TAKEN: 'Bu e-posta adresi kullanılıyor',
  },

  // Map Messages
  MAP: {
    COORDINATES_COPIED: 'Koordinatlar kopyalandı',
    AREA_CALCULATED: 'Alan hesaplandı',
    LOCATION_ERROR: 'Konum alınamadı',
    DRAWING_COMPLETE: 'Çizim tamamlandı',
  },

  // File Messages
  FILE: {
    UPLOAD_SUCCESS: 'Dosya başarıyla yüklendi',
    UPLOAD_FAILED: 'Dosya yüklenemedi',
    INVALID_TYPE: 'Geçersiz dosya türü',
    SIZE_TOO_LARGE: 'Dosya boyutu çok büyük',
    DOWNLOAD_FAILED: 'Dosya indirilemedi',
  }
};

// Helper function to get message with fallback
export const getMessage = (category: string, key: string, fallback: string = 'Bir hata oluştu'): string => {
  try {
    const categoryMessages = (UI_MESSAGES as any)[category.toUpperCase()];
    if (categoryMessages && categoryMessages[key.toUpperCase()]) {
      return categoryMessages[key.toUpperCase()];
    }
    return fallback;
  } catch {
    return fallback;
  }
};

// Type definitions for better IDE support
export type AuthMessages = keyof typeof UI_MESSAGES.AUTH;
export type CalculationMessages = keyof typeof UI_MESSAGES.CALCULATION;
export type EmailMessages = keyof typeof UI_MESSAGES.EMAIL;
export type PasswordMessages = keyof typeof UI_MESSAGES.PASSWORD;
export type ProfileMessages = keyof typeof UI_MESSAGES.PROFILE;
export type GeneralMessages = keyof typeof UI_MESSAGES.GENERAL;
export type FormMessages = keyof typeof UI_MESSAGES.FORM;
export type MapMessages = keyof typeof UI_MESSAGES.MAP;
export type FileMessages = keyof typeof UI_MESSAGES.FILE;
