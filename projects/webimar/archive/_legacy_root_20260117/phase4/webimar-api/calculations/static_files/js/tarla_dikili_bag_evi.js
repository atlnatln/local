/**
 * Tarla + Dikili + Bağ Evi Panel Sistemi
 * 
 * Bu dosya, Tarla (id=1) ve Bağ Evi (id=14) kombinasyonu seçildiğinde
 * özel bir kontrol paneli gösterir. Panel üç seçenek sunar:
 * 1. Doğrudan devam et
 * 2. Bilgileri manuel gir
 * 3. Alanları harita üzerinden gir
 * 
 * dikili-arazi.js ile uyumlu modüler yapı
 */

const TarlaBagEviPanel = {
    // CSS modül gereksinimleri
    requiredCSSModules: ['tarla-bag-evi', 'common-panels'],
    
    // Konfigürasyon
    targetAraziTipi: 1, // "Tarla + herhangi bir dikili vasıflı"
    targetYapiTuru: 14, // "Bağ evi"
    panelId: 'tarla-bag-evi-panel',
    isActive: false,
    
    // Manuel giriş verileri
    manuelData: {
        tarlaAlani: 0,
        bagEviAlani: 0,
        aciklama: ''
    },
    
    // Harita giriş verileri
    mapData: {
        tarlaCoords: null,
        bagEviCoords: null,
        tarlaArea: 0,
        bagEviArea: 0
    },
    
    ui: {}, // DOM elemanlarını saklamak için

    /**
     * Modülü başlat
     */
    async init() {
        // CSS modüllerini yükle
        try {
            await window.CSSModuleManager.loadModules(this.requiredCSSModules);
            console.log('Tarla Bağ Evi CSS modülleri yüklendi');
        } catch (error) {
            console.warn('CSS modül yükleme hatası:', error);
        }
        
        this.cacheDOMElements();
        this.createPanelHTML();
        this.setupEventListeners();
        this.checkAndTogglePanel();
    },

    /**
     * Sık kullanılan DOM elemanlarını önbelleğe al
     */
    cacheDOMElements() {
        this.ui.tapuVasfiSelect = document.querySelector('#id_tapu_vasfi');
        this.ui.yapiTuruSelect = document.querySelector('#id_yapi_turu');
        this.ui.araziBuyukluguInput = document.querySelector('#id_arazi_buyuklugu');
        this.ui.form = document.querySelector('#imar-durumu-form');
        this.ui.submitButton = document.querySelector('#bilgi-al');
        
        // Bağ evi radio butonları için yeni elemanlar
        this.ui.bagEviVarRadio = document.querySelector('#bag_evi_var');
        this.ui.bagEviYokRadio = document.querySelector('#bag_evi_yok');
        this.ui.bagEviKisitlamasiGroup = document.querySelector('#bag-evi-kisitlamasi-group');
    },

    /**
     * Bildirim göster (dikili-arazi.js uyumlu - CSS sınıfları kullanarak)
     */
    showNotification(message, type = 'info', isError = false) {
        // Notification elementlerini dinamik oluştur
        let notificationEl = document.getElementById('tarla-bag-evi-notification');
        if (!notificationEl) {
            notificationEl = document.createElement('div');
            notificationEl.id = 'tarla-bag-evi-notification';
            notificationEl.className = 'notification';
            
            const messageSpan = document.createElement('span');
            messageSpan.id = 'tarla-bag-evi-notification-message';
            notificationEl.appendChild(messageSpan);
            
            // Panel'in içine ekle veya form container'a ekle
            const panel = document.getElementById(this.panelId);
            if (panel) {
                panel.insertBefore(notificationEl, panel.firstChild);
            } else {
                const formContainer = document.querySelector('#imar-durumu-form') || document.body;
                formContainer.appendChild(notificationEl);
            }
        }

        const messageEl = notificationEl.querySelector('#tarla-bag-evi-notification-message');
        
        // CSS sınıflarını kullanarak bildirim stilini ayarla
        notificationEl.className = 'notification';
        if (isError) {
            notificationEl.classList.add('error');
        } else if (type === 'success') {
            notificationEl.classList.add('success');
        } else {
            notificationEl.classList.add('info');
        }

        messageEl.textContent = message;
        notificationEl.style.display = 'block';
        
        // 5 saniye sonra otomatik gizle (hata değilse)
        if (!isError) {
            setTimeout(() => {
                notificationEl.style.display = 'none';
            }, 5000);
        }
    },

    createPanelHTML() {
        // Panel zaten varsa oluşturma
        if (document.getElementById(this.panelId)) {
            console.log('TarlaBagEviPanel: Panel zaten mevcut');
            return;
        }

        // Gerekli DOM elementlerinin varlığını kontrol et
        if (!document.querySelector('#info-section')) {
            console.warn('TarlaBagEviPanel: İmar Durum Sorgulaması bölümü bulunamadı');
            return;
        }

        const panelHTML = `
            <div id="${this.panelId}" class="rustic-panel hidden">
                <div class="panel-header panel-header-orange">
                    <i class="fas fa-seedling"></i> Tarla + Bağ Evi Kontrol Paneli
                </div>
                <div class="panel-content">
                    <p>Tarla arazinizde bulunan bağ evi bilgilerini aşağıdaki seçeneklerden birini kullanarak girebilirsiniz:</p>
                    
                    <div class="dikili-options">
                        <div class="option-card" onclick="tarlaDikiliDevamEt()">
                            <h4><i class="fas fa-arrow-right"></i> Doğrudan Devam Et</h4>
                            <p>Dikili arazi kontrolü yapmadan doğrudan imar durumu sorgulamasına devam edin.</p>
                        </div>
                        
                        <div class="option-card" onclick="tarlaBagEviManuelGir()">
                            <h4><i class="fas fa-keyboard"></i> Bilgileri Manuel Gir</h4>
                            <p>Tarla ve bağ evi bilgilerini form alanlarına manuel olarak girin.</p>
                        </div>
                        
                        <div class="option-card" onclick="tarlaBagEviHaritaGir()">
                            <h4><i class="fas fa-map-marked-alt"></i> Alanları Harita Üzerinden Gir</h4>
                            <p>Tarla ve bağ evi alanlarını harita üzerinde işaretleyerek tanımlayın.</p>
                        </div>
                    </div>
                    
                    <p class="panel-note">Not: Bu kombinasyon için özel veri girişi gereklidir. Lütfen tarla ve bağ evi alanlarını ayrı ayrı belirtiniz.</p>
                </div>
            </div>
        `;

        // Paneli dikili arazi panelinden önce ekle
        const dikiliAraziPanel = document.querySelector('#dikili-arazi-kontrol-panel');
        
        if (dikiliAraziPanel) {
            // Dikili arazi panelinden hemen önce ekle
            dikiliAraziPanel.insertAdjacentHTML('beforebegin', panelHTML);
        } else {
            // Fallback: İmar Durum Sorgulaması bölümünden önce ekle
            const infoSection = document.querySelector('#info-section');
            if (infoSection) {
                infoSection.insertAdjacentHTML('beforebegin', panelHTML);
            } else {
                // Son fallback: Form container'ın içine ekle
                const formContainer = document.querySelector('#imar-durumu-form') || 
                                     document.querySelector('form') || 
                                     document.querySelector('.info-form');
                if (formContainer) {
                    formContainer.insertAdjacentHTML('beforebegin', panelHTML);
                } else {
                    console.warn('TarlaBagEviPanel: Uygun container bulunamadı, panel body\'ye ekleniyor');
                    document.body.insertAdjacentHTML('beforeend', panelHTML);
                }
            }
        }
    },

    /**
     * Event listener'ları ayarla (dikili-arazi.js pattern uyumlu)
     */
    setupEventListeners() {
        // Arazi tipi dropdown değişikliği
        if (this.ui.tapuVasfiSelect) {
            this.ui.tapuVasfiSelect.addEventListener('change', () => this.checkAndTogglePanel());
        }

        // Yapı türü dropdown değişikliği  
        if (this.ui.yapiTuruSelect) {
            this.ui.yapiTuruSelect.addEventListener('change', () => this.checkAndTogglePanel());
        }

        // Arazi büyüklüğü değişikliği
        if (this.ui.araziBuyukluguInput) {
            this.ui.araziBuyukluguInput.addEventListener('change', () => this.checkAndTogglePanel());
            this.ui.araziBuyukluguInput.addEventListener('blur', () => this.checkAndTogglePanel());
        }

        // Bağ evi var/yok radio butonları
        if (this.ui.bagEviVarRadio) {
            this.ui.bagEviVarRadio.addEventListener('change', () => this.checkAndTogglePanel());
        }
        
        if (this.ui.bagEviYokRadio) {
            this.ui.bagEviYokRadio.addEventListener('change', () => this.checkAndTogglePanel());
        }
    },

    checkAndTogglePanel() {
        if (!this.ui.tapuVasfiSelect || !this.ui.yapiTuruSelect) {
            console.warn('TarlaBagEviPanel: Dropdown elementleri bulunamadı');
            return;
        }

        const araziTipiValue = parseInt(this.ui.tapuVasfiSelect.value);
        const yapiTuruValue = parseInt(this.ui.yapiTuruSelect.value);
        const araziBuyuklugu = this.ui.araziBuyukluguInput ? 
            parseFloat(this.ui.araziBuyukluguInput.value.replace(',', '.')) : 0;
        
        // Tarla (1) veya Dikili vasıflı (2) + Bağ Evi (14) kombinasyonu ve gerekli büyüklük kontrolü
        const isTarlaVeBagEvi = araziTipiValue === this.targetAraziTipi && yapiTuruValue === this.targetYapiTuru;
        const isDikiliVeBagEvi = araziTipiValue === 2 && yapiTuruValue === this.targetYapiTuru; // Dikili vasıflı desteği eklendi
        const isAraziBuyuklukYeterli = !isNaN(araziBuyuklugu) && araziBuyuklugu >= 5000; // 0.5 hektar = 5000 m²
        
        // Bağ evi var/yok radio butonlarının durumu
        const bagEviYokSecildi = this.ui.bagEviYokRadio && this.ui.bagEviYokRadio.checked;
        
        // Panel gösterilme koşulu: (Tarla VEYA Dikili vasıflı) + Bağ Evi + Yeterli Büyüklük + "Başka bağ evi yok" seçildi
        const shouldShow = (isTarlaVeBagEvi || isDikiliVeBagEvi) && isAraziBuyuklukYeterli && bagEviYokSecildi;
        
        // Bağ evi sorusunu göster (her iki durumda da)
        if ((isTarlaVeBagEvi || isDikiliVeBagEvi) && isAraziBuyuklukYeterli) {
            this.showBagEviQuestion();
        } else {
            this.hideBagEviQuestion();
        }
        
        // Debug bilgisi
        console.log('TarlaBagEviPanel Check:', {
            araziTipi: araziTipiValue,
            yapiTuru: yapiTuruValue,
            araziBuyuklugu: araziBuyuklugu,
            isTarlaVeBagEvi,
            isDikiliVeBagEvi,
            isAraziBuyuklukYeterli,
            bagEviYokSecildi,
            shouldShow
        });
        
        this.togglePanel(shouldShow);
    },

    togglePanel(show) {
        const panel = document.getElementById(this.panelId);
        if (!panel) {
            console.warn('TarlaBagEviPanel: Panel elementi bulunamadı');
            return;
        }

        // Eğer panel zaten istenen durumda ise hiçbir şey yapma
        const isCurrentlyVisible = panel.style.display !== 'none' && !panel.classList.contains('hidden');
        if (show === isCurrentlyVisible) {
            return;
        }

        if (show) {
            panel.style.display = 'block';
            panel.classList.remove('hidden');
            this.isActive = true;
            
            // Animasyon efekti
            panel.style.opacity = '0';
            panel.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                panel.style.transition = 'all 0.3s ease';
                panel.style.opacity = '1';
                panel.style.transform = 'translateY(0)';
            }, 10);
            
            console.log('TarlaBagEviPanel: Panel gösterildi');
            
            // Panel gösterildiğinde diğer panelleri gizle
            this.hideDikiliAraziKontrolPanel();
        } else {
            panel.style.display = 'none';
            panel.classList.add('hidden');
            this.isActive = false;
            console.log('TarlaBagEviPanel: Panel gizlendi');
            
            // Panel gizlendiğinde FormCore'un tekrar kontrol etmesini sağla
            this.triggerFormCoreRecheck();
        }
    },

    /**
     * Dikili arazi kontrol panelini gizle (Panel öncelik kontrolü)
     */
    hideDikiliAraziKontrolPanel() {
        const dikiliAraziPanel = document.getElementById('dikili-arazi-kontrol-panel');
        if (dikiliAraziPanel) {
            dikiliAraziPanel.style.display = 'none';
            console.log('TarlaBagEviPanel: Dikili arazi kontrol paneli gizlendi (öncelik kontrolü)');
        }
    },

    /**
     * Panel gizlendiğinde FormCore'un tekrar kontrol etmesini sağla
     */
    triggerFormCoreRecheck() {
        // FormCore.checkBagEviUyarisi'ni tekrar çağır
        if (window.FormCore && typeof window.FormCore.checkBagEviUyarisi === 'function') {
            console.log('TarlaBagEviPanel: FormCore recheck tetikleniyor');
            setTimeout(() => {
                window.FormCore.checkBagEviUyarisi();
            }, 100); // Kısa bir gecikme ile
        }
    },

    /**
     * Bağ evi sorusunu göster (FormCore ile uyumlu)
     */
    showBagEviQuestion() {
        if (this.ui.bagEviKisitlamasiGroup) {
            // CSS override ile güçlü gösterme (FormCore ile aynı yaklaşım)
            this.ui.bagEviKisitlamasiGroup.style.cssText = 'display: block !important;';
            this.ui.bagEviKisitlamasiGroup.style.visibility = 'visible';
            this.ui.bagEviKisitlamasiGroup.removeAttribute('hidden');
            
            // Animasyon efekti ekle
            this.ui.bagEviKisitlamasiGroup.classList.add('highlight');
            setTimeout(() => {
                this.ui.bagEviKisitlamasiGroup.classList.remove('highlight');
            }, 2000);
        }
    },

    /**
     * Bağ evi sorusunu gizle
     */
    hideBagEviQuestion() {
        if (this.ui.bagEviKisitlamasiGroup) {
            this.ui.bagEviKisitlamasiGroup.style.display = 'none';
            
            // Radio butonları sıfırla
            if (this.ui.bagEviVarRadio) this.ui.bagEviVarRadio.checked = false;
            if (this.ui.bagEviYokRadio) this.ui.bagEviYokRadio.checked = false;
        }
    },

    handleManuelEntry() {
        console.log('TarlaBagEviPanel: Manuel giriş seçeneği seçildi');
        this.showManuelEntryPanel();
    },

    handleMapEntry() {
        console.log('TarlaBagEviPanel: Harita giriş seçeneği seçildi');
        this.showMapEntryPanel();
    },

    handleDirectContinue() {
        console.log('TarlaBagEviPanel: Doğrudan devam et seçeneği seçildi');
        this.showAreaInputPanel();
    },

    /**
     * Tarla ve dikili alan girişi için form paneli oluştur ve göster
     */
    showAreaInputPanel() {
        const panel = document.getElementById(this.panelId);
        if (!panel) return;

        // Panel içeriğini alan girişi formu ile değiştir
        const panelContent = panel.querySelector('.panel-content');
        if (!panelContent) return;

        // Toplam arazi büyüklüğünü al
        const toplamAlan = this.ui.araziBuyukluguInput ? 
            parseFloat(this.ui.araziBuyukluguInput.value.replace(',', '.')) : 0;

        // Panel içeriğini alan girişi formu ile değiştir
        panelContent.innerHTML = this.createAreaInputPanelHTML(toplamAlan);
        
        // Alan girişi event listener'larını ayarla
        this.setupAreaInputEventListeners();
    },

    createAreaInputPanelHTML(toplamAlan = 0) {
        return `
            <h3><i class="fas fa-ruler-combined"></i> Tarla + Dikili Alan Bilgileri</h3>
            <p>Toplam arazi büyüklüğünüz: <strong>${toplamAlan ? toplamAlan.toLocaleString('tr-TR') : '0'} m²</strong></p>
            <p>Arazinizin tarla ve dikili alan miktarlarını aşağıya girerek devam ediniz:</p>
            
            <div class="form-group">
                <label for="tarla-alan-input" class="form-label">Tarla Alanı (m²):</label>
                <input type="number" 
                       id="tarla-alan-input" 
                       class="form-control full-width" 
                       placeholder="Tarla alanı büyüklüğü (m²)" 
                       min="0" 
                       max="${toplamAlan || ''}"
                       step="0.01">
                ${toplamAlan ? `<small class="input-hint">Maksimum: ${toplamAlan.toLocaleString('tr-TR')} m²</small>` : ''}
            </div>
            
            <div class="form-group">
                <label for="dikili-alan-input" class="form-label">Dikili Alan (m²):</label>
                <input type="number" 
                       id="dikili-alan-input" 
                       class="form-control full-width" 
                       placeholder="Dikili alan büyüklüğü (m²)" 
                       min="0"
                       max="${toplamAlan || ''}"
                       step="0.01">
                ${toplamAlan ? `<small class="input-hint">Maksimum: ${toplamAlan.toLocaleString('tr-TR')} m²</small>` : ''}
            </div>
            
            <div id="tarla-dikili-bildirim" class="notification hidden">
                <span id="tarla-dikili-bildirim-mesaj"></span>
            </div>
            
            <div class="button-group space-between top-margin">
                <button id="tarla-dikili-geri-btn" class="cancel-button">
                    <i class="fas fa-arrow-left"></i> Geri Dön
                </button>
                <button id="tarla-dikili-devam-btn" class="submit-button submit-button-orange">
                    <i class="fas fa-check"></i> Bilgileri Kaydet ve Devam Et
                </button>
            </div>
        `;
    },

    setupAreaInputEventListeners() {
        const tarlaInput = document.getElementById('tarla-alan-input');
        const dikiliInput = document.getElementById('dikili-alan-input');
        const geriBtn = document.getElementById('tarla-dikili-geri-btn');
        const devamBtn = document.getElementById('tarla-dikili-devam-btn');
        
        if (!tarlaInput || !dikiliInput || !geriBtn || !devamBtn) return;

        // Input değişikliklerini dinle
        [tarlaInput, dikiliInput].forEach(input => {
            input.addEventListener('input', () => this.validateAreaInputs());
            input.addEventListener('blur', () => this.validateAreaInputs());
        });

        // Geri dön butonu
        geriBtn.addEventListener('click', () => {
            this.returnToMainPanel();
        });

        // Devam et butonu
        devamBtn.addEventListener('click', () => {
            this.processAreaInput();
        });
    },

    validateAreaInputs() {
        const tarlaInput = document.getElementById('tarla-alan-input');
        const dikiliInput = document.getElementById('dikili-alan-input');
        const devamBtn = document.getElementById('tarla-dikili-devam-btn');
        
        if (!tarlaInput || !dikiliInput || !devamBtn) return;
        
        const tarlaAlan = parseFloat(tarlaInput.value) || 0;
        const dikiliAlan = parseFloat(dikiliInput.value) || 0;
        
        // Her iki alan da doldurulmuş ve pozitif olmalı
        const isValid = tarlaAlan > 0 && dikiliAlan > 0;
        
        devamBtn.disabled = !isValid;
        devamBtn.style.opacity = isValid ? '1' : '0.6';
        
        // Toplam alan kontrolü
        const toplamAlan = tarlaAlan + dikiliAlan;
        const formAraziBuyuklugu = parseFloat(this.ui.araziBuyukluguInput?.value?.replace(',', '.')) || 0;
        
        if (isValid && formAraziBuyuklugu > 0 && toplamAlan > formAraziBuyuklugu) {
            this.showAreaNotification('Uyarı: Girilen alanların toplamı (' + toplamAlan + ' m²) form alanında belirtilen arazi büyüklüğünden (' + formAraziBuyuklugu + ' m²) büyük olamaz.', true);
            devamBtn.disabled = true;
            devamBtn.style.opacity = '0.6';
        } else {
            this.hideAreaNotification();
        }
    },

    processAreaInput() {
        const tarlaInput = document.getElementById('tarla-alan-input');
        const dikiliInput = document.getElementById('dikili-alan-input');
        
        if (!tarlaInput || !dikiliInput) {
            this.showAreaNotification('Hata: Alan girişi bulunamadı.', true);
            return;
        }
        
        const tarlaAlan = parseFloat(tarlaInput.value) || 0;
        const dikiliAlan = parseFloat(dikiliInput.value) || 0;
        
        if (tarlaAlan <= 0 || dikiliAlan <= 0) {
            this.showAreaNotification('Hata: Lütfen geçerli alan değerleri giriniz.', true);
            return;
        }
        
        // Verileri kaydet
        this.manuelData.tarlaAlani = tarlaAlan;
        this.manuelData.dikiliAlani = dikiliAlan;
        this.manuelData.aciklama = `Tarla: ${tarlaAlan}m², Dikili: ${dikiliAlan}m²`;
        
        console.log('Alan bilgileri kaydedildi:', this.manuelData);
        
        // Paneli gizle ve form gönderimini başlat
        this.hideAreaInputForm();
        this.finalizeDirectContinue();
    },

    finalizeDirectContinue() {
        // Form gönderim butonunu etkinleştir ve göster
        if (this.ui.submitButton) {
            this.ui.submitButton.disabled = false;
            const buttonGroup = this.ui.submitButton.closest('.button-group');
            if (buttonGroup) buttonGroup.style.display = 'block';
        }
        
        // Tarla dikili bağ evi kontrolünü başarıyla geçtik bilgisini form gönderiminde kullanılmak üzere sakla
        window.tarlaDikiliBagEviKontrolGecildi = true;
        window.tarlaDikiliBagEviVerileri = this.manuelData;
        
        // Formu otomatik olarak gönder
        if (this.ui.form && this.ui.tapuVasfiSelect?.value && 
            this.ui.araziBuyukluguInput?.value && this.ui.yapiTuruSelect?.value) {
            
            // Yükleniyor göstergesini göster
            const loadingIndicator = document.getElementById('loading-indicator');
            if (loadingIndicator) loadingIndicator.style.display = 'block';
            
            // 30 saniye sonra yükleme göstergesini otomatik kapat (güvenlik önlemi)
            setTimeout(() => {
                if (loadingIndicator) loadingIndicator.style.display = 'none';
            }, 30000);
            
            // Submit butonuna tıklama
            this.ui.submitButton.click();
        }
        
        this.showNotification('Alan bilgileri alınarak imar durumu sorgulamasına devam ediliyor...', 'info', false);
    },

    showAreaNotification(message, isError = false) {
        const notificationEl = document.getElementById('tarla-dikili-bildirim');
        const messageEl = document.getElementById('tarla-dikili-bildirim-mesaj');
        
        if (!notificationEl || !messageEl) return;
        
        // CSS sınıflarını kullanarak bildirim stilini ayarla
        notificationEl.className = 'notification';
        if (isError) {
            notificationEl.classList.add('error');
        } else {
            notificationEl.classList.add('success');
        }
        
        messageEl.textContent = message;
        notificationEl.style.display = 'block';
    },

    hideAreaNotification() {
        const notificationEl = document.getElementById('tarla-dikili-bildirim');
        if (notificationEl) {
            notificationEl.style.display = 'none';
        }
    },

    returnToMainPanel() {
        const panel = document.getElementById(this.panelId);
        if (!panel) return;

        // Panel içeriğini ana panel içeriği ile değiştir
        const panelContent = panel.querySelector('.panel-content');
        if (!panelContent) return;

        // Orijinal panel HTML'ini geri yükle
        panelContent.innerHTML = `
            <p>Tarla arazinizde bulunan bağ evi bilgilerini aşağıdaki seçeneklerden birini kullanarak girebilirsiniz:</p>
            
            <div class="dikili-options">
                <div class="option-card" onclick="tarlaDikiliDevamEt()">
                    <h4><i class="fas fa-arrow-right"></i> Doğrudan Devam Et</h4>
                    <p>Dikili arazi kontrolü yapmadan doğrudan imar durumu sorgulamasına devam edin.</p>
                </div>
                
                <div class="option-card" onclick="tarlaBagEviManuelGir()">
                    <h4><i class="fas fa-keyboard"></i> Bilgileri Manuel Gir</h4>
                    <p>Tarla ve bağ evi bilgilerini form alanlarına manuel olarak girin.</p>
                </div>
                
                <div class="option-card" onclick="tarlaBagEviHaritaGir()">
                    <h4><i class="fas fa-map-marked-alt"></i> Alanları Harita Üzerinden Gir</h4>
                    <p>Tarla ve bağ evi alanlarını harita üzerinde işaretleyerek tanımlayın.</p>
                </div>
            </div>
            
            <p class="panel-note">Not: Bu kombinasyon için özel veri girişi gereklidir. Lütfen tarla ve bağ evi alanlarını ayrı ayrı belirtiniz.</p>
        `;

        // Panel göster
        panel.style.display = 'block';
        this.isActive = true;

        // Animasyon efekti
        panel.style.opacity = '0';
        panel.style.transform = 'translateY(-10px)';
        
        setTimeout(() => {
            panel.style.transition = 'all 0.3s ease';
            panel.style.opacity = '1';
            panel.style.transform = 'translateY(0)';
        }, 10);
    },

    showManuelEntryPanel() {
        this.showNotification('Manuel giriş özellikleri henüz aktif değil. Lütfen "Doğrudan Devam Et" seçeneğini kullanın.', 'info', false);
        
        // Doğrudan devam et'e yönlendir
        setTimeout(() => {
            this.showAreaInputPanel();
        }, 2000);
    },

    showMapEntryPanel() {
        this.showNotification('Harita özellikleri henüz aktif değil. Lütfen "Doğrudan Devam Et" seçeneğini kullanın.', 'info', false);
        
        // Doğrudan devam et'e yönlendir
        setTimeout(() => {
            this.showAreaInputPanel();
        }, 2000);
    },

    hideAreaInputForm() {
        // Bu fonksiyon createAreaInputPanelHTML ile oluşturulan formu gizlemez
        // çünkü form panel içeriğinin kendisi
        // Bu yüzden ana panele dönüş yapıyoruz
        this.returnToMainPanel();
    },

    /**
     * Modülü sıfırla (dikili-arazi.js pattern uyumlu)
     */
    reset() {
        this.isActive = false;
        this.manuelData = {
            tarlaAlani: 0,
            bagEviAlani: 0,
            aciklama: ''
        };
        this.mapData = {
            tarlaCoords: null,
            bagEviCoords: null,
            tarlaArea: 0,
            bagEviArea: 0
        };
        
        const panel = document.getElementById(this.panelId);
        if (panel) {
            panel.style.display = 'none';
        }
        
        // Notification'ı gizle
        const notification = document.getElementById('tarla-bag-evi-notification');
        if (notification) {
            notification.style.display = 'none';
        }
        
        // Radio butonları sıfırla
        if (this.ui.bagEviVarRadio) {
            this.ui.bagEviVarRadio.checked = false;
        }
        if (this.ui.bagEviYokRadio) {
            this.ui.bagEviYokRadio.checked = false;
        }
        
        // Panel sıfırlandığında FormCore'un tekrar kontrol etmesini sağla
        this.triggerFormCoreRecheck();
    },

    // Utility metodlar
    isCurrentCombination() {
        return this.isActive;
    },

    getPanelElement() {
        return document.getElementById(this.panelId);
    },

    destroy() {
        const panel = document.getElementById(this.panelId);
        if (panel) {
            panel.remove();
        }
        
        const notification = document.getElementById('tarla-bag-evi-notification');
        if (notification) {
            notification.remove();
        }
        
        this.isActive = false;
    }
};

// Global fonksiyonlar (dikili-arazi.js uyumlu)
window.tarlaBagEviManuelGir = function() {
    TarlaBagEviPanel.handleManuelEntry();
};

window.tarlaBagEviHaritaGir = function() {
    TarlaBagEviPanel.handleMapEntry();
};

window.tarlaDikiliDevamEt = function() {
    TarlaBagEviPanel.handleDirectContinue();
};

window.tarlaBagEviGeriDon = function() {
    TarlaBagEviPanel.returnToMainPanel();
};

// Panel sistemini başlat
document.addEventListener('DOMContentLoaded', () => {
    TarlaBagEviPanel.init();
});

// Global erişim için
window.TarlaBagEviPanel = TarlaBagEviPanel;

// CSS modüllerini yükle
document.addEventListener('DOMContentLoaded', () => {
    window.CSSModuleManager.loadModules(TarlaBagEviPanel.requiredCSSModules)
        .then(() => {
            console.log('Tüm CSS modülleri yüklendi');
        })
        .catch(err => {
            console.error('CSS modülleri yüklenirken hata:', err);
        });
});
