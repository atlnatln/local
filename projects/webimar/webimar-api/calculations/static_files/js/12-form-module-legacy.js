// ========================
// 6. FORM MODÜLÜ - YENİDEN YAPILANDIRILDI
// ========================
// Bu dosya artık form-module-new.js tarafından yüklenen modüler yapıya
// yönlendirme yapar. Form-module.js modüler yapıya bölünmüştür:
// - form-core.js: Temel form işlevleri
// - form-visibility.js: Form görünürlüğü kontrolü
// - form-special-fields.js: Özel form alanları (Sera, Silo, Su Tahsis)
// - form-submission.js: Form gönderimi ve doğrulama
// - form-module-new.js: Tüm modülleri bir araya getiren ana modül

// Geriye dönük uyumluluk için eski FormModule yapısını koruyoruz
const FormModule = {
    originalOptions: [], // Orijinal seçenekleri saklamak için modül özelliği

    /**
     * Form elemanlarını ve event listener'ları ayarla
     */
    init() {
        // Form-module-new.js'nin init'ini çağır
        if (window.FormCore) {
            this.originalOptions = FormCore.originalOptions;
            FormCore.init();
        } else {
            console.error("Form modülleri yüklenemedi. Sayfa yenilenerek tekrar denenebilir.");
        }
    },
    
    // Tüm fonksiyonlar modüler yapıdaki karşılıklarına yönlendiriliyor
    
    // Form çekirdek (FormCore) fonksiyonları
    setupFormControls: function() { 
        if (window.FormCore) return FormCore.setupFormControls(); 
    },
    setupSelectPlaceholder: function(selectElement) { 
        if (window.FormCore) return FormCore.setupSelectPlaceholder(selectElement); 
    },
    setupEventListeners: function() { 
        if (window.FormCore) return FormCore.setupEventListeners(); 
    },
    filterYapiTuruByTapuVasfi: function(tapuVasfiSelect, yapiTuruSelect) { 
        if (window.FormCore) return FormCore.filterYapiTuruByTapuVasfi(tapuVasfiSelect, yapiTuruSelect); 
    },
    
    // Form görünürlük (FormVisibility) fonksiyonları
    handleTapuVasfiChange: function(tapuVasfiSelect) { 
        if (window.FormVisibility) return FormVisibility.handleTapuVasfiChange(tapuVasfiSelect); 
    },
    handleAraziBuyukluguChange: function(araziBuyukluguInput) { 
        if (window.FormVisibility) return FormVisibility.handleAraziBuyukluguChange(araziBuyukluguInput); 
    },
    
    // Özel form alanları (SpecialFormFields) fonksiyonları
    updateSuTahsisBelgesiVisibility: function() { 
        if (window.SpecialFormFields) return SpecialFormFields.updateSuTahsisBelgesiVisibility(); 
    },
    updateSeraFormuVisibility: function() { 
        if (window.SpecialFormFields) return SpecialFormFields.updateSeraFormuVisibility(); 
    },
    createSeraFormFields: function() { 
        if (window.SpecialFormFields) return SpecialFormFields.createSeraFormFields(); 
    },
    createSiloFormFields: function() { 
        if (window.SpecialFormFields) return SpecialFormFields.createSiloFormFields(); 
    },
    updateDutBahcesiSorusu: function(group, yapiTuru) { 
        if (window.SpecialFormFields) return SpecialFormFields.updateDutBahcesiSorusu(group, yapiTuru); 
    },
    showSuTahsisBelgesiQuestion: function(group, yapiTuru) { 
        if (window.SpecialFormFields) return SpecialFormFields.showSuTahsisBelgesiQuestion(group, yapiTuru); 
    },
    hideSuTahsisBelgesiQuestion: function(group) { 
        if (window.SpecialFormFields) return SpecialFormFields.hideSuTahsisBelgesiQuestion(group); 
    },
    
    // Form gönderim (FormSubmission) fonksiyonları 
    handleFormSubmit: function(e) { 
        if (window.FormSubmission) return FormSubmission.handleFormSubmit(e); 
    },
    validateForm: function(sonuclarDiv) { 
        return window.FormSubmission ? FormSubmission.validateForm(sonuclarDiv) : true; 
    },
    prepareFormData: function(form) { 
        return window.FormSubmission ? FormSubmission.prepareFormData(form) : new FormData(form); 
    },
    submitForm: function(form, formData, sonuclarDiv) { 
        if (window.FormSubmission) return FormSubmission.submitForm(form, formData, sonuclarDiv); 
    }
};

// Sonuç mesajı eklenmeden önce eski içeriği temizleyerek tekrarı önleyin:
function submitForm() {
    // ...existing fetch/AJAX kodu...
    fetch('/sorgula-imar-durumu/', { /* ...existing fetch options... */ })
        .then(res => res.json())
        .then(data => {
            // Sonuç için ana kapsayıcıyı bul
            const resultContainer = document.getElementById('sonuc-mesaj') || document.querySelector('.sonuc-mesaj');
            
            if (resultContainer) {
                // Önceki içeriği tamamen temizle
                resultContainer.innerHTML = '';
                
                // Yapı türüne göre özel içerik ekleme
                const yapiTuruSelect = document.getElementById('id_yapi_turu');
                const yapiTuruId = yapiTuruSelect ? yapiTuruSelect.value : null;
                
                if (yapiTuruId === "7") { // Lisanslı Depolar
                    // Lisanslı depo için yalnızca ana mesajı ekle, silo bilgilerini eklemeden
                    const sonucDiv = document.createElement('div');
                    sonucDiv.className = 'sonuc-container';
                    sonucDiv.innerHTML = data.mesaj;
                    resultContainer.appendChild(sonucDiv);
                } else if (yapiTuruId === "5") { // Silo
                    // Silo için normal içerik ekleme
                    const sonucDiv = document.createElement('div');
                    sonucDiv.className = 'sonuc-container';
                    sonucDiv.innerHTML = data.mesaj;
                    resultContainer.appendChild(sonucDiv);
                    
                    // Buraya gelecekte silo özel bilgileri eklenebilir
                } else {
                    // Diğer yapı türleri için normal içerik ekleme
                    resultContainer.innerHTML = data.mesaj;
                }
            }
            
            // Sayfayı sonuç bölümüne kaydır
            scrollToResults();
        })
        .catch(err => {
            // ...existing error handling...
        });
}