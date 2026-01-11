// ========================
// 3. YARDIMCI FONKSİYONLAR
// ========================
const Utils = {
    /**
     * CSRF token'ı cookie'den al
     */
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },
    
    /**
     * DOM elemanını seçmek için yardımcı fonksiyon
     */
    getElement(selector) {
        return document.querySelector(selector);
    },
    
    /**
     * Eleman görünürlüğünü değiştir
     */
    setVisibility(element, isVisible) {
        if (element) {
            element.style.display = isVisible ? 'block' : 'none';
        }
    },
    
    /**
     * Debounce fonksiyonu - çağrılmasının üzerinden belirtilen zaman
     * geçtikten sonra fonksiyonu çalıştırır, tekrarlanan çağrılarda
     * zamanlayıcıyı sıfırlar
     * 
     * @param {Function} func - Çağrılacak fonksiyon
     * @param {number} wait - Gecikme süresi (milisaniye)
     * @return {Function} - Geciktirilmiş fonksiyon
     */
    debounce(func, wait) {
        let timeout;
        return function(...args) {
            const context = this;
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                func.apply(context, args);
            }, wait);
        };
    }
};
