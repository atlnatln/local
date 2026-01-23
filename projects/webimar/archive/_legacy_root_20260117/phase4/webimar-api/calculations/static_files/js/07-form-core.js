// Form çekirdek yönetimi - temel kurulum ve event listener'ları
const FormCore = {
    originalOptions: [], 
    ui: {}, // DOM elemanlarını saklamak için

    /**
     * Form elemanlarını ve event listener'ları ayarla
     */
    init() {
        // Dikili arazi kontrolü için bayrak
        window.dikiliAraziKontrolGecildi = false;
        
        this.cacheDOMElements(); // Önbelleğe alma fonksiyonunu çağır
        this.setupFormControls();
        this.setupEventListeners();
    },

    /**
     * Sık kullanılan DOM elemanlarını önbelleğe al
     */
    cacheDOMElements() {
        this.ui.form = Utils.getElement('#imar-durumu-form');
        this.ui.tapuVasfiSelect = Utils.getElement(CONFIG.selectors.form.tapuVasfi);
        this.ui.araziBuyukluguInput = Utils.getElement(CONFIG.selectors.form.araziBuyuklugu);
        this.ui.yapiTuruSelect = Utils.getElement(CONFIG.selectors.form.yapiTuru);
        this.ui.submitButton = Utils.getElement(CONFIG.selectors.form.submitButton);
        this.ui.suTahsisBelgesiGroup = Utils.getElement(CONFIG.selectors.suTahsisBelgesi);
        this.ui.sonuclarDiv = Utils.getElement(CONFIG.selectors.sonuclar);
        this.ui.buyukOvaUyariDiv = Utils.getElement(CONFIG.selectors.buyukOvaUyari);
        this.ui.bagEviUyariDiv = Utils.getElement(CONFIG.selectors.bagEviUyari);
        this.ui.dikiliAraziKontrolPanel = document.getElementById('dikili-arazi-kontrol-panel');
        this.ui.suTahsisVarRadio = Utils.getElement(CONFIG.selectors.form.suTahsisVarRadio);
        this.ui.suTahsisYokRadio = Utils.getElement(CONFIG.selectors.form.suTahsisYokRadio);
    },
    
    /**
     * Form kontrollerinin başlangıç durumunu ayarla
     */
    setupFormControls() {
        // this.ui üzerinden erişim
        if (this.ui.araziBuyukluguInput) {
            const araziBuyukluguGroup = this.ui.araziBuyukluguInput.closest('.form-group');
            if (araziBuyukluguGroup) araziBuyukluguGroup.style.display = 'none';
            this.ui.araziBuyukluguInput.disabled = true;
        }
        
        if (this.ui.yapiTuruSelect) {
            const yapiTuruGroup = this.ui.yapiTuruSelect.closest('.form-group');
            if (yapiTuruGroup) yapiTuruGroup.style.display = 'none';
            this.ui.yapiTuruSelect.disabled = true;
        }
        
        if (this.ui.submitButton) {
            this.ui.submitButton.disabled = true;
            this.ui.submitButton.closest('.button-group').style.display = 'none';
        }
        
        Utils.setVisibility(this.ui.suTahsisBelgesiGroup, false);
        
        // Tapu vasfına ve yapı türüne placeholder stil ekle
        if (this.ui.tapuVasfiSelect) {
            this.setupSelectPlaceholder(this.ui.tapuVasfiSelect);
        }
        
        // Yapı türüne placeholder stil ekle
        if (this.ui.yapiTuruSelect) {
            this.setupSelectPlaceholder(this.ui.yapiTuruSelect);
        }
    },
    
    /**
     * Select elemanında placeholder stillemesi
     */
    setupSelectPlaceholder(selectElement) {
        // İlk option'a placeholder stil ekle
        const firstOption = selectElement.options[0];
        if (firstOption && firstOption.value === '') {
            firstOption.setAttribute('selected', true);
            firstOption.setAttribute('disabled', true);
            firstOption.classList.add('placeholder-option');
            
            // Seçim değiştiğinde placeholder stilini kaldır
            selectElement.addEventListener('change', function() {
                firstOption.classList.remove('placeholder-option');
            });
        }
    },
    
    /**
     * Event listener'ları ekle
     */
    setupEventListeners() {
        // Önbelleğe alınmış ui elemanlarını kullan
        if (this.ui.form) {
            this.ui.form.addEventListener('submit', FormSubmission.handleFormSubmit.bind(FormSubmission));
        }
        
        if (this.ui.tapuVasfiSelect) {
            this.ui.tapuVasfiSelect.addEventListener('change', () => {
                // Tapu vasfı değiştiğinde arazi büyüklüğü alanını sıfırla
                if (this.ui.araziBuyukluguInput) {
                    this.ui.araziBuyukluguInput.value = '';
                }
                
                // Tapu vasfı değiştiğinde yapı türü seçimini sıfırla
                if (this.ui.yapiTuruSelect) {
                    this.ui.yapiTuruSelect.value = '';
                    this.ui.yapiTuruSelect.disabled = true;
                    const yapiTuruGroup = this.ui.yapiTuruSelect.closest('.form-group');
                    if (yapiTuruGroup) yapiTuruGroup.style.display = 'none';
                }
                
                // Tapu vasfı değiştiğinde su tahsis belgesi alanını gizle
                if (this.ui.suTahsisBelgesiGroup) {
                    this.ui.suTahsisBelgesiGroup.style.display = 'none';
                    
                    // Radyo butonlarını sıfırla
                    if (this.ui.suTahsisVarRadio) this.ui.suTahsisVarRadio.checked = false;
                    if (this.ui.suTahsisYokRadio) this.ui.suTahsisYokRadio.checked = false;
                }
                
                // Submit butonunu devre dışı bırak ve gizle
                if (this.ui.submitButton) {
                    this.ui.submitButton.disabled = true;
                    this.ui.submitButton.closest('.button-group').style.display = 'none';
                }
                
                // Sorgu sonuçları bölümünü temizle
                if (this.ui.sonuclarDiv) {
                    this.ui.sonuclarDiv.innerHTML = '';
                    Utils.setVisibility(this.ui.sonuclarDiv, false);
                }
                
                // Büyük Ova uyarısını gizle
                if (this.ui.buyukOvaUyariDiv) {
                    Utils.setVisibility(this.ui.buyukOvaUyariDiv, false);
                }
                
                // Bağ Evi uyarısını gizle
                if (this.ui.bagEviUyariDiv) {
                    Utils.setVisibility(this.ui.bagEviUyariDiv, false);
                }
                
                // Tapu vasfı değişince dikili arazi kontrol panelini gizle
                const dikiliPanel = document.getElementById('dikili-arazi-kontrol-panel');
                if (dikiliPanel) dikiliPanel.style.display = 'none';
                
                FormVisibility.handleTapuVasfiChange(this.ui.tapuVasfiSelect);
            });
            
            if (this.ui.yapiTuruSelect) {
                this.originalOptions = Array.from(this.ui.yapiTuruSelect.options);
                this.ui.tapuVasfiSelect.addEventListener('change', () => {
                    this.filterYapiTuruByTapuVasfi(this.ui.tapuVasfiSelect, this.ui.yapiTuruSelect);
                });
            }
        }
        
        if (this.ui.yapiTuruSelect) {
            this.ui.yapiTuruSelect.addEventListener('change', () => {
                SpecialFormFields.updateSuTahsisBelgesiVisibility();
                SpecialFormFields.updateSeraFormuVisibility();
                this.checkBagEviUyarisi();
            });
        }
        
        if (this.ui.araziBuyukluguInput) {
            this.ui.araziBuyukluguInput.addEventListener('input', () => {
                this.checkBagEviUyarisi();
            });
        }
    },
    
    /**
     * Bağ evi - Dikili tarım arazisi kontrolü
     * Bağ evi için 0.5 hektar (5000 m²) asgari alan kontrolü yapılır
     * Alan yeterli ise isteğe bağlı dikili arazi doğrulama paneli gösterilir
     */
    checkBagEviUyarisi() {
        // Önbelleğe alınmış ui elemanlarını kullan
        if (!this.ui.yapiTuruSelect || !this.ui.tapuVasfiSelect || !this.ui.araziBuyukluguInput || !this.ui.bagEviUyariDiv) {
            return;
        }
        
        // TarlaBagEviPanel aktifse, bağ evi sorusu onun tarafından kontrol ediliyor
        if (window.TarlaBagEviPanel && window.TarlaBagEviPanel.isActive) {
            return;
        }
        
        const yapiTuruValue = this.ui.yapiTuruSelect.value;
        const tapuVasfiText = this.ui.tapuVasfiSelect.options[this.ui.tapuVasfiSelect.selectedIndex].text.trim();
        const araziBuyuklugu = parseFloat(this.ui.araziBuyukluguInput.value.replace(',', '.'));
        
        const isBagEvi = yapiTuruValue === '14'; 
        const isDikiliVasifli = tapuVasfiText.includes('Dikili vasıflı');
        // Yeni: Zeytinlik vasfı dışındaki tüm arazilerde soruyu gösterilir
        const isNotZeytinlik = !tapuVasfiText.includes('Zeytinlik');
        const isAraziBuyuklukYetersiz = !isNaN(araziBuyuklugu) && araziBuyuklugu < 5000;
        
        // Bağ evi kısıtlaması alanını gösterme/gizleme
        const bagEviKisitlamasiGroup = document.getElementById('bag-evi-kisitlamasi-group');
        
        if (bagEviKisitlamasiGroup) {
            const shouldShowBagEviQuestion = isBagEvi && isDikiliVasifli && isNotZeytinlik && !isAraziBuyuklukYetersiz;
            
            if (shouldShowBagEviQuestion) {
                // CSS override ile güçlü gösterme
                bagEviKisitlamasiGroup.style.cssText = 'display: block !important;';
                bagEviKisitlamasiGroup.style.visibility = 'visible';
                bagEviKisitlamasiGroup.removeAttribute('hidden');
                
                // Bağ evi kısıtlaması için bir kez animasyon ekle
                bagEviKisitlamasiGroup.classList.add('highlight');
                setTimeout(() => {
                    bagEviKisitlamasiGroup.classList.remove('highlight');
                }, 2000);
            } else {
                bagEviKisitlamasiGroup.style.display = 'none';
            }
        }
        
        if (isBagEvi && isDikiliVasifli && isNotZeytinlik && !isAraziBuyuklukYetersiz && this.ui.submitButton) {
            this.ui.submitButton.disabled = true;
            this.ui.submitButton.closest('.button-group').style.display = 'none';
        }
        
        if (isBagEvi && isDikiliVasifli && isAraziBuyuklukYetersiz) {
            Utils.setVisibility(this.ui.bagEviUyariDiv, true);
            if (this.ui.dikiliAraziKontrolPanel) this.ui.dikiliAraziKontrolPanel.style.display = 'none';
            
            if (this.ui.submitButton) {
                this.ui.submitButton.disabled = false;
                this.ui.submitButton.closest('.button-group').style.display = 'block';
            }
        } else if (isBagEvi && isDikiliVasifli && !isAraziBuyuklukYetersiz) {
            Utils.setVisibility(this.ui.bagEviUyariDiv, false);
            // Bağ evi var/yok sorusunun cevabını kontrol et
            const bagEviVarRadio = document.getElementById('bag_evi_var');
            const bagEviYokRadio = document.getElementById('bag_evi_yok');
            
            // TarlaBagEviPanel aktif mi kontrol et (Panel öncelik mantığı)
            const isTarlaBagEviPanelActive = window.TarlaBagEviPanel && window.TarlaBagEviPanel.isActive;
            
            if (bagEviVarRadio && bagEviVarRadio.checked) {
                // Bağ evi var seçilmişse, uyarı göster ve devam etmeyi engelle
                if (this.ui.dikiliAraziKontrolPanel) this.ui.dikiliAraziKontrolPanel.style.display = 'none';
                
                // Uyarı mesajı göster
                const bagEviUyariMesaj = document.createElement('div');
                bagEviUyariMesaj.className = 'alert alert-warning mt-3';
                bagEviUyariMesaj.id = 'bag-evi-kisitlama-uyari';
                bagEviUyariMesaj.innerHTML = `
                    <strong>Uyarı:</strong> Aynı ilçede ailenize ait bir bağ evi bulunduğunu belirttiniz. 
                    Mevzuat gereği, her aile için aynı ilçe sınırları içerisinde sadece bir adet bağ evi izni verilebilir.
                `;
                
                // Eski uyarı mesajını kaldır ve yenisini ekle
                const eskiUyari = document.getElementById('bag-evi-kisitlama-uyari');
                if (eskiUyari) eskiUyari.remove();
                
                if (bagEviKisitlamasiGroup) {
                    bagEviKisitlamasiGroup.after(bagEviUyariMesaj);
                }
                
                if (this.ui.submitButton) {
                    this.ui.submitButton.disabled = true;
                    this.ui.submitButton.closest('.button-group').style.display = 'none';
                }
            } else if (bagEviYokRadio && bagEviYokRadio.checked) {
                // Bağ evi yok seçilmişse, dikili arazi kontrol panelini göster
                // ANCAK sadece TarlaBagEviPanel aktif değilse
                const eskiUyari = document.getElementById('bag-evi-kisitlama-uyari');
                if (eskiUyari) eskiUyari.remove();
                
                if (!isTarlaBagEviPanelActive) {
                    this.showDikiliAraziKontrolPanel();
                } else {
                    // TarlaBagEviPanel aktifse, dikili arazi panelini gizle
                    if (this.ui.dikiliAraziKontrolPanel) this.ui.dikiliAraziKontrolPanel.style.display = 'none';
                }
            } else {
                // Henüz seçim yapılmadıysa, dikili arazi kontrol panelini gizle
                if (this.ui.dikiliAraziKontrolPanel) this.ui.dikiliAraziKontrolPanel.style.display = 'none';
                
                if (this.ui.submitButton) {
                    this.ui.submitButton.disabled = true;
                    this.ui.submitButton.closest('.button-group').style.display = 'none';
                }
            }
        } else {
            Utils.setVisibility(this.ui.bagEviUyariDiv, false);
            if (this.ui.dikiliAraziKontrolPanel) this.ui.dikiliAraziKontrolPanel.style.display = 'none';
            
            if (this.ui.submitButton) {
                this.ui.submitButton.disabled = false;
                this.ui.submitButton.closest('.button-group').style.display = 'block';
            }
        }
    },
    
    /**
     * Dikili arazi kontrol panelini göster
     * Kullanıcı doğrudan imar durumu sorgulaması veya dikili arazi doğrulaması seçebilir
     */
    showDikiliAraziKontrolPanel() {
        // Önbelleğe alınmış ui elemanını kullan
        if (this.ui.dikiliAraziKontrolPanel) {
            this.ui.dikiliAraziKontrolPanel.style.display = 'block';
            // Otomatik olarak haritadan alan seçme moduna geçme kodu kaldırıldı
        }
    },
    
    /**
     * Tapu vasfına göre yapı türü seçeneklerini filtrele
     */
    filterYapiTuruByTapuVasfi(tapuVasfiSelect, yapiTuruSelect) {
        const selectedText = tapuVasfiSelect.options[tapuVasfiSelect.selectedIndex].text.trim();
        yapiTuruSelect.innerHTML = '';
        
        const defaultOption = this.originalOptions.find(opt => opt.value === ''); // this.originalOptions kullanıldı
        if (defaultOption) yapiTuruSelect.appendChild(defaultOption.cloneNode(true));
        
        if (selectedText === 'Zeytinlik') {
            this.originalOptions.forEach(opt => { // this.originalOptions kullanıldı
                if (opt.text.includes('Zeytinyağı üretim tesisi') || opt.text.includes('Zeytinyağı fabrikası')) {
                    yapiTuruSelect.appendChild(opt.cloneNode(true));
                }
            });
        } else {
            this.originalOptions.forEach(opt => { // this.originalOptions kullanıldı
                if (opt.value !== '') {
                    yapiTuruSelect.appendChild(opt.cloneNode(true));
                }
            });
        }
    }
};
