// Form görünürlük kontrolü ve form alanlarının dinamik güncellenmesi
const FormVisibility = {
    // Formların gösterilip gösterilmediğini izlemek için bayrak
    formsShown: false,
    
    /**
     * Tapu vasfı değişimini işle
     */
    handleTapuVasfiChange(tapuVasfiSelect) {
        const araziBuyukluguInput = Utils.getElement(CONFIG.selectors.form.araziBuyuklugu);
        const yapiTuruSelect = Utils.getElement(CONFIG.selectors.form.yapiTuru);
        const submitButton = Utils.getElement(CONFIG.selectors.form.submitButton);
        const suTahsisBelgesiGroup = Utils.getElement(CONFIG.selectors.suTahsisBelgesi);
        
        const isSelected = tapuVasfiSelect.value !== '';
        
        // Tapu vasfı değiştiğinde formların gösterilme durumunu sıfırla
        this.formsShown = false;
        
        // Tapu vasfı değiştiğinde arazi büyüklüğü alanını sıfırla
        if (araziBuyukluguInput) {
            araziBuyukluguInput.value = '';
        }
        
        // Tapu vasfı değiştiğinde yapı türü seçimini sıfırla
        if (yapiTuruSelect) {
            yapiTuruSelect.value = '';
            yapiTuruSelect.disabled = true;
            const yapiTuruGroup = yapiTuruSelect.closest('.form-group');
            if (yapiTuruGroup) yapiTuruGroup.style.display = 'none';
        }
        
        // Tapu vasfı değiştiğinde su tahsis belgesi alanını gizle
        if (suTahsisBelgesiGroup) {
            suTahsisBelgesiGroup.style.display = 'none';
            
            // Radyo butonlarını sıfırla
            const suTahsisVarRadio = Utils.getElement(CONFIG.selectors.form.suTahsisVarRadio);
            const suTahsisYokRadio = Utils.getElement(CONFIG.selectors.form.suTahsisYokRadio);
            if (suTahsisVarRadio) suTahsisVarRadio.checked = false;
            if (suTahsisYokRadio) suTahsisYokRadio.checked = false;
        }
        
        // Bağ evi kısıtlaması alanını gizle ve radio butonlarını sıfırla
        const bagEviKisitlamasiGroup = document.getElementById('bag-evi-kisitlamasi-group');
        if (bagEviKisitlamasiGroup) {
            bagEviKisitlamasiGroup.style.display = 'none';
            
            // Radio butonları sıfla
            const bagEviVarRadio = document.getElementById('bag_evi_var');
            const bagEviYokRadio = document.getElementById('bag_evi_yok');
            if (bagEviVarRadio) bagEviVarRadio.checked = false;
            if (bagEviYokRadio) bagEviYokRadio.checked = false;
        }
        
        // Submit butonunu devre dışı bırak ve gizle
        if (submitButton) {
            submitButton.disabled = true;
            const buttonGroup = submitButton.closest('.button-group');
            if (buttonGroup) buttonGroup.style.display = 'none';
        }
        
        // Tapu vasfı seçildiyse arazi büyüklüğü alanını göster
        if (araziBuyukluguInput) {
            const araziBuyukluguGroup = araziBuyukluguInput.closest('.form-group');
            if (araziBuyukluguGroup) {
                if (isSelected) {
                    araziBuyukluguGroup.style.display = 'block';
                    araziBuyukluguGroup.classList.add('form-fade-in');
                    // Animasyon bittikten sonra sınıfı kaldır
                    setTimeout(() => {
                        araziBuyukluguGroup.classList.remove('form-fade-in');
                    }, 600);
                } else {
                    araziBuyukluguGroup.style.display = 'none';
                }
            }
            araziBuyukluguInput.disabled = !isSelected;
        }
        
        // Yapı türü alanı ve submit butonu hala kapalı kalır (arazi büyüklüğü girilince açılacak)
        if (yapiTuruSelect) {
            yapiTuruSelect.disabled = true;
            const yapiTuruGroup = yapiTuruSelect.closest('.form-group');
            if (yapiTuruGroup) yapiTuruGroup.style.display = 'none';
        }
        
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.closest('.button-group').style.display = 'none';
        }
        
        // Tapu vasfı değiştiyse, arazi büyüklüğünü tekrar girmesi gerekebilir
        if (araziBuyukluguInput) {
            // Arazi büyüklüğü alanına event listener ekleme
            araziBuyukluguInput.oninput = () => this.handleAraziBuyukluguChange(araziBuyukluguInput);
        }
    },
    
    /**
     * Arazi büyüklüğü değiştiğinde çağrılacak fonksiyon
     */
    handleAraziBuyukluguChange(araziBuyukluguInput) {
        const yapiTuruSelect = Utils.getElement(CONFIG.selectors.form.yapiTuru);
        const submitButton = Utils.getElement(CONFIG.selectors.form.submitButton);
        
        // Arazi büyüklüğü girildi mi kontrol et 
        const isValid = araziBuyukluguInput.value.length > 0;
        
        // Statik bir flag tutarak formların açıldığını izlememize yardımcı olacak
        if (!this.formsShown) {
            this.formsShown = false;
        }
        
        // Eğer formlar daha önce gösterildiyse veya şu anda gösterilmeliyse
        const shouldShow = isValid || this.formsShown;
        
        // Eğer ilk kez geçerli bir değer girildiyse, formların açıldığını not edelim
        if (isValid && !this.formsShown) {
            this.formsShown = true;
        }
        
        // Yapı türü seçimi ve submit butonunu göster (bir kez açıldığında açık kalır)
        if (yapiTuruSelect) {
            const yapiTuruGroup = yapiTuruSelect.closest('.form-group');
            if (yapiTuruGroup) {
                // Form daha önce gösterilmemişse ve şimdi gösterilmesi gerekiyorsa
                if (shouldShow && yapiTuruGroup.style.display !== 'block') {
                    yapiTuruGroup.style.display = 'block';
                    yapiTuruGroup.classList.add('form-fade-in');
                    // Animasyon bittikten sonra sınıfı kaldır
                    setTimeout(() => {
                        yapiTuruGroup.classList.remove('form-fade-in');
                    }, 600);
                }
                
                // Submit buton hala arazi büyüklüğünün dolu olmasına bağlı olabilir
                yapiTuruSelect.disabled = !isValid;
            }
        }
        
        // --- YENİ KONTROL ---
        const buttonGroup = submitButton ? submitButton.closest('.button-group') : null;
        const formReady = this.isFormReady();
        if (buttonGroup) {
            if (formReady) {
                if (buttonGroup.style.display !== 'block') {
                    buttonGroup.style.display = 'block';
                    buttonGroup.classList.add('form-fade-in');
                    setTimeout(() => buttonGroup.classList.remove('form-fade-in'), 600);
                }
                submitButton.disabled = false;
            } else {
                buttonGroup.style.display = 'none';
                submitButton.disabled = true;
            }
        }
    },
    
    /**
     * Tüm gerekli alanlar dolu mu kontrolü (vasıf, arazi m², yapı türü, varsa ek sorular)
     */
    isFormReady() {
        const tapuVasfi = Utils.getElement(CONFIG.selectors.form.tapuVasfi);
        const araziBuyuklugu = Utils.getElement(CONFIG.selectors.form.araziBuyuklugu);
        const yapiTuru = Utils.getElement(CONFIG.selectors.form.yapiTuru);
        // Su tahsis sorusu aktifse radio kontrolü
        const suTahsisBelgesiGroup = Utils.getElement(CONFIG.selectors.suTahsisBelgesi);
        let suTahsisCevaplandi = true;
        if (suTahsisBelgesiGroup && suTahsisBelgesiGroup.style.display === 'block') {
            // Hem su_tahsis_var/yok hem de dut_bahcesi_var/yok radio'larını kontrol et
            const suTahsisVar = document.getElementById('su_tahsis_var');
            const suTahsisYok = document.getElementById('su_tahsis_yok');
            const dutBahcesiVar = document.getElementById('dut_bahcesi_var');
            const dutBahcesiYok = document.getElementById('dut_bahcesi_yok');
            // Eğer radio butonları DOM'da yoksa, cevaplanmadı say
            if (
                (!suTahsisVar && !suTahsisYok && !dutBahcesiVar && !dutBahcesiYok)
            ) {
                suTahsisCevaplandi = false;
            } else {
                suTahsisCevaplandi =
                    (suTahsisVar && suTahsisVar.checked) ||
                    (suTahsisYok && suTahsisYok.checked) ||
                    (dutBahcesiVar && dutBahcesiVar.checked) ||
                    (dutBahcesiYok && dutBahcesiYok.checked);
            }
        }
        // Bağ evi kısıtlaması sorusu aktifse radio kontrolü
        const bagEviKisitlamasiGroup = document.getElementById('bag-evi-kisitlamasi-group');
        let bagEviCevaplandi = true;
        if (bagEviKisitlamasiGroup && bagEviKisitlamasiGroup.style.display === 'block') {
            const bagEviVar = document.getElementById('bag_evi_var');
            const bagEviYok = document.getElementById('bag_evi_yok');
            bagEviCevaplandi = (bagEviVar && bagEviVar.checked) || (bagEviYok && bagEviYok.checked);
        }
        // Debug için log ekle
        // console.log('isFormReady:', {
        //   tapuVasfi: tapuVasfi && tapuVasfi.value,
        //   araziBuyuklugu: araziBuyuklugu && araziBuyuklugu.value,
        //   yapiTuru: yapiTuru && yapiTuru.value,
        //   suTahsisCevaplandi,
        //   bagEviCevaplandi
        // });
        return (
            tapuVasfi && tapuVasfi.value &&
            araziBuyuklugu && araziBuyuklugu.value &&
            yapiTuru && yapiTuru.value &&
            suTahsisCevaplandi &&
            bagEviCevaplandi
        );
    },
};

// Su tahsis radio butonlarına event listener ekle (her gösterildiğinde çağrılmalı)
function attachSuTahsisRadioListeners() {
    const suTahsisVar = document.getElementById('su_tahsis_var');
    const suTahsisYok = document.getElementById('su_tahsis_yok');
    const araziBuyukluguInput = document.getElementById('id_arazi_buyuklugu');
    // Listener eklemeden önce flag'i sıfırla (DOM yeniden oluşturulmuş olabilir)
    if (suTahsisVar) suTahsisVar._listenerAttached = false;
    if (suTahsisYok) suTahsisYok._listenerAttached = false;
    function checkButtonVisibility() {
        const submitButton = document.querySelector('button[type=submit]');
        const buttonGroup = submitButton ? submitButton.closest('.button-group') : null;
        const formReady = FormVisibility.isFormReady();
        console.log('[SU TAHSiS] Buton görünürlük kontrolü:', {formReady, buttonGroup, submitButton});
        if (buttonGroup) {
            if (formReady) {
                buttonGroup.style.display = 'block';
                buttonGroup.classList.add('form-fade-in');
                setTimeout(() => buttonGroup.classList.remove('form-fade-in'), 600);
                submitButton.disabled = false;
            } else {
                buttonGroup.style.display = 'none';
                submitButton.disabled = true;
            }
        } else {
            console.warn('[SU TAHSiS] .button-group bulunamadı!');
        }
    }
    if (suTahsisVar && !suTahsisVar._listenerAttached) {
        suTahsisVar.addEventListener('change', function() {
            console.log('[SU TAHSiS] EVET seçildi!');
            if (araziBuyukluguInput) FormVisibility.handleAraziBuyukluguChange(araziBuyukluguInput);
            checkButtonVisibility();
        });
        suTahsisVar._listenerAttached = true;
    }
    if (suTahsisYok && !suTahsisYok._listenerAttached) {
        suTahsisYok.addEventListener('change', function() {
            console.log('[SU TAHSiS] HAYIR seçildi!');
            if (araziBuyukluguInput) FormVisibility.handleAraziBuyukluguChange(araziBuyukluguInput);
            checkButtonVisibility();
        });
        suTahsisYok._listenerAttached = true;
    }
}

// Dışarıdan da çağrılabilsin diye global export
window.attachSuTahsisRadioListeners = attachSuTahsisRadioListeners;

document.addEventListener('DOMContentLoaded', function() {
    attachSuTahsisRadioListeners();
    // Yapı türü değiştiğinde de tekrar ekle
    const yapiTuru = document.getElementById('id_yapi_turu');
    if (yapiTuru) {
        yapiTuru.addEventListener('change', function() {
            setTimeout(attachSuTahsisRadioListeners, 100);
        });
    }
    // Tüm form alanlarında değişiklik olduğunda buton görünürlüğünü kontrol et
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('input', function() {
            const submitButton = document.querySelector('button[type=submit]');
            const buttonGroup = submitButton ? submitButton.closest('.button-group') : null;
            const formReady = FormVisibility.isFormReady();
            if (buttonGroup) {
                if (formReady) {
                    buttonGroup.style.display = 'block';
                    buttonGroup.classList.add('form-fade-in');
                    setTimeout(() => buttonGroup.classList.remove('form-fade-in'), 600);
                    submitButton.disabled = false;
                } else {
                    buttonGroup.style.display = 'none';
                    submitButton.disabled = true;
                }
            }
        });
    }
});

// Eğer SpecialFormFields.updateSuTahsisBelgesiVisibility fonksiyonunuz varsa, orada da attachSuTahsisRadioListeners() çağrısı ekleyin:
//  örnek:
// function updateSuTahsisBelgesiVisibility() {
//   ...
//   attachSuTahsisRadioListeners();
// }
