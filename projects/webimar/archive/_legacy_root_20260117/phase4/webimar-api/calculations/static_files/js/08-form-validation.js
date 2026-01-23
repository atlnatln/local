/**
 * Form değerlerinin doğrulaması için yardımcı fonksiyonlar
 */
const FormValidation = {
    /**
     * Sayısal bir alanı doğrula - pozitif sayısal değer kontrolü
     * @param {HTMLElement} input - Input elementi
     * @returns {boolean} Geçerli mi
     */
    validateNumericField(input) {
        if (!input) return false;
        const value = input.value.trim();
        
        // Boş mu?
        if (!value) {
            this.setValidationError(input, "Bu alan zorunludur");
            return false;
        }
        
        // Sayısal mı?
        // Virgül veya nokta içeren sayısal değerleri kabul et
        const cleanValue = value.replace(',', '.'); 
        const numValue = parseFloat(cleanValue);
        
        if (isNaN(numValue)) {
            this.setValidationError(input, "Lütfen geçerli bir sayı giriniz");
            return false;
        }
        
        // Pozitif mi?
        if (numValue <= 0) {
            this.setValidationError(input, "Değer sıfırdan büyük olmalıdır");
            return false;
        }
        
        // Doğrulama başarılı - hata mesajı varsa temizle
        this.clearValidationError(input);
        return true;
    },
    
    /**
     * Validasyon hatası göster
     * @param {HTMLElement} input - Input elementi
     * @param {string} message - Hata mesajı 
     */
    setValidationError(input, message) {
        // Mevcut hata mesajını temizle
        this.clearValidationError(input);
        
        // Yeni hata mesajı oluştur
        const errorElement = document.createElement('div');
        errorElement.className = 'validation-error';
        errorElement.style.color = 'red';
        errorElement.style.fontSize = '0.8rem';
        errorElement.style.marginTop = '0.25rem';
        errorElement.textContent = message;
        
        // Input elementinin sonrasına ekle
        if (input.parentNode) {
            input.parentNode.insertBefore(errorElement, input.nextSibling);
        }
        
        // Input'a hata sınıfı ekle
        input.classList.add('is-invalid');
    },
    
    /**
     * Validasyon hatasını temizle
     * @param {HTMLElement} input - Input elementi
     */
    clearValidationError(input) {
        // Input'un kardeşi olan hata mesajını bul ve kaldır
        const nextSibling = input.nextSibling;
        if (nextSibling && nextSibling.className === 'validation-error') {
            nextSibling.remove();
        }
        
        // Input'tan hata sınıfını kaldır
        input.classList.remove('is-invalid');
    },
    
    /**
     * Silo alanı input'unun değişikliklerini izle
     */
    initSiloFieldValidation() {
        // Sayfa yüklendiğinde veya DOM değiştiğinde silo input'unu bul
        const observer = new MutationObserver((mutations) => {
            const siloInput = document.getElementById('id_silo_alani_m2');
            if (siloInput && !siloInput.dataset.validationInitialized) {
                // Input için validasyon olayları ekle
                siloInput.addEventListener('blur', () => {
                    this.validateNumericField(siloInput);
                });
                
                siloInput.addEventListener('input', () => {
                    // Kullanıcı yazarken hata mesajını temizle
                    this.clearValidationError(siloInput);
                });
                
                // Bu input için validasyon başlatıldı işareti koy
                siloInput.dataset.validationInitialized = 'true';
                
                // İlk validasyon kontrolü (varsa mevcut değer için)
                if (siloInput.value) {
                    this.validateNumericField(siloInput);
                }
            }
        });
        
        observer.observe(document.body, { 
            childList: true,
            subtree: true 
        });
    }
};

// Sayfa yüklendiğinde validasyonu başlat
document.addEventListener('DOMContentLoaded', () => {
    FormValidation.initSiloFieldValidation();
    FormValidation.initAraziBuyukluguValidation();

    // Silo bilgi kutularını otomatik olarak kaldır
    document.querySelectorAll('.alert.alert-info.mt-2, .form-text.mt-2.silo-info-message').forEach(el => el.remove());
});

/**
 * Arazi büyüklüğü alanı için validasyon başlat 
 * ve alanın değişiklikleri üzerinde FormCore.checkBagEviUyarisi'ni çağır
 */
FormValidation.initAraziBuyukluguValidation = function() {
    const araziBuyukluguInput = Utils.getElement(CONFIG.selectors.form.araziBuyuklugu);
    
    if (araziBuyukluguInput && !araziBuyukluguInput.dataset.validationInitialized) {
        // Input için validasyon olayları ekle
        araziBuyukluguInput.addEventListener('blur', () => {
            this.validateNumericField(araziBuyukluguInput);
            // Bağ evi uyarısını kontrol et
            if (typeof FormCore.checkBagEviUyarisi === 'function') {
                FormCore.checkBagEviUyarisi();
            }
        });
        
        araziBuyukluguInput.addEventListener('input', () => {
            // Kullanıcı yazarken hata mesajını temizle
            this.clearValidationError(araziBuyukluguInput);
        });
        
        // Bu input için validasyon başlatıldı işareti koy
        araziBuyukluguInput.dataset.validationInitialized = 'true';
    }
};
