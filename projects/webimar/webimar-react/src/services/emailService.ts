import { tokenStorage } from '../utils/tokenStorage';
import { API_BASE_URL } from './api';

export interface EmailResponse {
  success: boolean;
  message: string;
  email?: string;
}

export interface VerificationResponse {
  success: boolean;
  message: string;
  user?: {
    id: number;
    username: string;
    email: string;
    is_active: boolean;
  };
}

class EmailService {
  // Rate limit hatası için kullanıcıya uygun mesaj dönme helper'ı
  private handleRateLimitError(response: Response): string {
    return 'Çok fazla istek gönderiyorsunuz. Lütfen bir süre bekleyip tekrar deneyin.';
  }

  async sendVerificationEmail(email: string): Promise<EmailResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/accounts/send-verification/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      // Rate limit hatası (429) kontrolü
      if (response.status === 429) {
        return {
          success: false,
          message: this.handleRateLimitError(response)
        };
      }

      return data;
    } catch (error) {
      console.error('Email verification send error:', error);
      return {
        success: false,
        message: 'Ağ hatası oluştu'
      };
    }
  }

  async verifyEmail(uid: string, token: string): Promise<VerificationResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/accounts/verify-email/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ uid, token }),
      });

      return await response.json();
    } catch (error) {
      console.error('Email verification error:', error);
      return {
        success: false,
        message: 'Ağ hatası oluştu'
      };
    }
  }

  async requestPasswordReset(email: string): Promise<EmailResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/accounts/request-password-reset/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      // Rate limit hatası (429) kontrolü
      if (response.status === 429) {
        return {
          success: false,
          message: this.handleRateLimitError(response)
        };
      }

      return data;
    } catch (error) {
      console.error('Password reset request error:', error);
      return {
        success: false,
        message: 'Ağ hatası oluştu'
      };
    }
  }

  async resetPassword(uid: string, token: string, newPassword: string): Promise<EmailResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/accounts/reset-password/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          uid, 
          token, 
          new_password: newPassword 
        }),
      });

      return await response.json();
    } catch (error) {
      console.error('Password reset error:', error);
      return {
        success: false,
        message: 'Ağ hatası oluştu'
      };
    }
  }

  async testEmailConnection(): Promise<EmailResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/accounts/test-email-connection/`);
      return await response.json();
    } catch (error) {
      console.error('Email connection test error:', error);
      return {
        success: false,
        message: 'Ağ hatası oluştu'
      };
    }
  }

  async sendTestEmail(email: string, type: 'simple' | 'welcome' | 'html' = 'simple'): Promise<EmailResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/accounts/test-email/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, type }),
      });

      return await response.json();
    } catch (error) {
      console.error('Test email send error:', error);
      return {
        success: false,
        message: 'Ağ hatası oluştu'
      };
    }
  }

  async requestEmailChange(newEmail: string, password: string): Promise<EmailResponse> {
    try {
      const token = tokenStorage.getAccessToken();
      const response = await fetch(`${API_BASE_URL}/accounts/request-email-change/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ new_email: newEmail, password }),
      });

      const data = await response.json();

      // Rate limit hatası (429) kontrolü
      if (response.status === 429) {
        return {
          success: false,
          message: this.handleRateLimitError(response)
        };
      }

      return data;
    } catch (error) {
      console.error('Email change request error:', error);
      return {
        success: false,
        message: 'Ağ hatası oluştu'
      };
    }
  }

  async confirmEmailChange(uid: string, token: string, newEmail: string): Promise<EmailResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/accounts/confirm-email-change/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ uid, token, new_email: newEmail }),
      });

      const data = await response.json();

      // Rate limit hatası (429) kontrolü
      if (response.status === 429) {
        return {
          success: false,
          message: this.handleRateLimitError(response)
        };
      }

      return data;
    } catch (error) {
      console.error('Email change confirmation error:', error);
      return {
        success: false,
        message: 'Ağ hatası oluştu'
      };
    }
  }
}

export const emailService = new EmailService();
