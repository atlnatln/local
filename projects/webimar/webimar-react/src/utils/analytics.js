/**
 * Webimar Analytics Tracker
 * Tüm ziyaretçiler için sayfa görüntüleme ve etkileşim tracking
 * React ve Next.js uyumlu
 */

class WebimarAnalytics {
  constructor(apiUrl) {
    this.apiUrl = apiUrl || process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.sessionId = this.getOrCreateSessionId();
    this.currentPath = null;
    this.pageStartTime = null;
    this.platform = this.detectPlatform();
    this.browser = this.detectBrowser();
    this.os = this.detectOS();
  }

  /**
   * Session ID oluştur veya localStorage'dan al
   */
  getOrCreateSessionId() {
    if (typeof window === 'undefined') return null;
    
    let sessionId = sessionStorage.getItem('webimar_session_id');
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('webimar_session_id', sessionId);
    }
    return sessionId;
  }

  /**
   * Platform tespiti (mobile, tablet, desktop)
   */
  detectPlatform() {
    if (typeof window === 'undefined') return 'unknown';
    
    const ua = navigator.userAgent;
    if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) {
      return 'tablet';
    }
    if (/Mobile|Android|iP(hone|od)|IEMobile|BlackBerry|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/.test(ua)) {
      return 'mobile';
    }
    return 'desktop';
  }

  /**
   * Browser tespiti
   */
  detectBrowser() {
    if (typeof window === 'undefined') return 'unknown';
    
    const ua = navigator.userAgent;
    if (ua.indexOf('Firefox') > -1) return 'Firefox';
    if (ua.indexOf('Chrome') > -1 && ua.indexOf('Edg') === -1) return 'Chrome';
    if (ua.indexOf('Safari') > -1 && ua.indexOf('Chrome') === -1) return 'Safari';
    if (ua.indexOf('Edg') > -1) return 'Edge';
    if (ua.indexOf('MSIE') > -1 || ua.indexOf('Trident/') > -1) return 'IE';
    return 'Unknown';
  }

  /**
   * OS tespiti
   */
  detectOS() {
    if (typeof window === 'undefined') return 'unknown';
    
    const ua = navigator.userAgent;
    if (ua.indexOf('Win') > -1) return 'Windows';
    if (ua.indexOf('Mac') > -1) return 'MacOS';
    if (ua.indexOf('Linux') > -1) return 'Linux';
    if (ua.indexOf('Android') > -1) return 'Android';
    if (ua.indexOf('iOS') > -1 || ua.indexOf('iPhone') > -1 || ua.indexOf('iPad') > -1) return 'iOS';
    return 'Unknown';
  }

  /**
   * Sayfa görüntüleme kaydı
   */
  async trackPageView(path, pageTitle = null) {
    if (typeof window === 'undefined') return;
    
    // Önceki sayfadan çıkış süresini kaydet
    if (this.currentPath && this.pageStartTime) {
      const timeOnPage = Math.floor((Date.now() - this.pageStartTime) / 1000);
      await this.trackTimeOnPage(this.currentPath, timeOnPage);
    }

    // Yeni sayfa tracking başlat
    this.currentPath = path;
    this.pageStartTime = Date.now();
    
    const data = {
      session_id: this.sessionId,
      path: path,
      full_url: window.location.href,
      page_title: pageTitle || document.title,
      referrer: document.referrer,
      platform: this.platform,
      browser: this.browser,
      os: this.os,
      load_time: performance.timing ? performance.timing.loadEventEnd - performance.timing.navigationStart : null,
    };

    try {
      await fetch(`${this.apiUrl}/api/calculations/analytics/page-view/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
        credentials: 'include',
      });
      console.log('📊 Page view tracked:', path);
    } catch (error) {
      console.error('Failed to track page view:', error);
    }
  }

  /**
   * Sayfada geçirilen süre kaydı
   */
  async trackTimeOnPage(path, timeInSeconds) {
    if (typeof window === 'undefined' || timeInSeconds < 1) return;

    try {
      await fetch(`${this.apiUrl}/api/calculations/analytics/time-on-page/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: this.sessionId,
          path: path,
          time_on_page: timeInSeconds,
        }),
        credentials: 'include',
      });
    } catch (error) {
      console.error('Failed to track time on page:', error);
    }
  }

  /**
   * Kullanıcı etkileşimi kaydı
   */
  async trackInteraction(interactionType, elementData = {}) {
    if (typeof window === 'undefined') return;

    const data = {
      session_id: this.sessionId,
      interaction_type: interactionType,
      element_id: elementData.id || '',
      element_class: elementData.className || '',
      element_text: elementData.text || '',
      page_path: window.location.pathname,
      page_title: document.title,
      metadata: elementData.metadata || {},
    };

    try {
      await fetch(`${this.apiUrl}/api/calculations/analytics/interaction/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
        credentials: 'include',
      });
      console.log('🎯 Interaction tracked:', interactionType);
    } catch (error) {
      console.error('Failed to track interaction:', error);
    }
  }

  /**
   * Form gönderimi tracking
   */
  trackFormSubmit(formName, formData = {}) {
    return this.trackInteraction('form_submit', {
      id: formName,
      metadata: { form_data: formData }
    });
  }

  /**
   * Buton tıklama tracking
   */
  trackButtonClick(buttonId, buttonText = '') {
    return this.trackInteraction('click', {
      id: buttonId,
      text: buttonText
    });
  }

  /**
   * Arama tracking
   */
  trackSearch(searchQuery) {
    return this.trackInteraction('search', {
      metadata: { query: searchQuery }
    });
  }

  /**
   * Filtreleme tracking
   */
  trackFilter(filterType, filterValue) {
    return this.trackInteraction('filter', {
      metadata: { filter_type: filterType, filter_value: filterValue }
    });
  }

  /**
   * Sayfa değiştirme (unmount) event listener
   */
  setupUnloadTracking() {
    if (typeof window === 'undefined') return;

    window.addEventListener('beforeunload', () => {
      if (this.currentPath && this.pageStartTime) {
        const timeOnPage = Math.floor((Date.now() - this.pageStartTime) / 1000);
        
        // Beacon API ile sync olmadan gönder
        const data = new URLSearchParams({
          session_id: this.sessionId,
          path: this.currentPath,
          time_on_page: timeOnPage,
        });
        
        navigator.sendBeacon(
          `${this.apiUrl}/api/calculations/analytics/time-on-page/`,
          data
        );
      }
    });
  }

  /**
   * Visibility change tracking (tab değişimi)
   */
  setupVisibilityTracking() {
    if (typeof window === 'undefined') return;

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        // Tab gizlendi
        if (this.currentPath && this.pageStartTime) {
          const timeOnPage = Math.floor((Date.now() - this.pageStartTime) / 1000);
          this.trackTimeOnPage(this.currentPath, timeOnPage);
        }
      }
    });
  }

  /**
   * Tüm tracking'i başlat
   */
  init() {
    this.setupUnloadTracking();
    this.setupVisibilityTracking();
  }
}

// Singleton instance
let analyticsInstance = null;

export const getAnalytics = (apiUrl) => {
  if (!analyticsInstance) {
    analyticsInstance = new WebimarAnalytics(apiUrl);
    analyticsInstance.init();
  }
  return analyticsInstance;
};

export default WebimarAnalytics;
