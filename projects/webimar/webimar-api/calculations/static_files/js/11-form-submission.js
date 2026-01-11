// Form gönderimi ve doğrulama işlemleri
const FormSubmission = {
    /**
     * Form gönderimi işle
     */
    handleFormSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const sonuclarDiv = Utils.getElement(CONFIG.selectors.sonuclar);
        const buyukOvaUyariElement = Utils.getElement(CONFIG.selectors.buyukOvaUyari);
        
        Utils.setVisibility(buyukOvaUyariElement, false);
        
        if (!this.validateForm(sonuclarDiv)) {
            return;
        }
        
        const formData = this.prepareFormData(form);
        if (formData === false) {
            return; // Form gönderimi iptal edildi
        }
        
        // Dikili arazi kontrolü bayrağını sıfırla
        window.dikiliAraziKontrolGecildi = false;
        
        ResultsModule.showLoading(sonuclarDiv);
        this.submitForm(form, formData, sonuclarDiv);
    },
    
    /**
     * Form verilerini kullanarak doğrudan form gönderimi
     * @param {FormData} formData - Gönderilecek form verileri
     */
    submitFormWithData(formData) {
        const form = document.getElementById('imar-durumu-form');
        const sonuclarDiv = Utils.getElement(CONFIG.selectors.sonuclar);
        
        if (form && sonuclarDiv) {
            ResultsModule.showLoading(sonuclarDiv);
            this.submitForm(form, formData, sonuclarDiv);
        }
    },
    
    /**
     * Form doğrulama
     */
    validateForm(sonuclarDiv) {
        const yapiTuruSelect = Utils.getElement(CONFIG.selectors.form.yapiTuru);
        const selectedIndex = yapiTuruSelect.selectedIndex;
        let selectedYapiTuruText = selectedIndex > -1 ? yapiTuruSelect.options[selectedIndex].text : '';
        
        if (selectedYapiTuruText) {
            const parts = selectedYapiTuruText.split(' - ');
            selectedYapiTuruText = parts.length > 1 ? parts.slice(1).join(' - ') : parts[0];
        }
        
        // Silo seçildiğinde planlanan silo taban alanı kontrolü
        if (selectedYapiTuruText.includes("Hububat ve yem depolama silosu")) {
            const siloAlaniInput = Utils.getElement('#id_silo_alani_m2'); // createSiloFormFields içinde oluşturulan ID
            if (!siloAlaniInput || !siloAlaniInput.value) {
                sonuclarDiv.innerHTML = `<div class="sonuc-container"><p class="sonuc-red">Lütfen planlanan silo taban alanını giriniz.</p></div>`;
                siloAlaniInput?.classList.add('is-invalid');
                return false;
            }
            const siloAlaniValue = parseFloat(siloAlaniInput.value.replace(',', '.'));
            if (isNaN(siloAlaniValue) || siloAlaniValue <= 0) {
                sonuclarDiv.innerHTML = `<div class="sonuc-container"><p class="sonuc-red">Planlanan silo taban alanı geçerli bir pozitif sayı olmalıdır.</p></div>`;
                siloAlaniInput?.classList.add('is-invalid');
                return false;
            }
            siloAlaniInput?.classList.remove('is-invalid');
        }
        
        const suTahsisBelgesiGroup = Utils.getElement(CONFIG.selectors.suTahsisBelgesi);
        if (suTahsisBelgesiGroup && suTahsisBelgesiGroup.style.display === 'block') {
            // İpek böcekçiliği tesisi için özel kontrol
            const ipekBocekcilikTesisi = selectedYapiTuruText.includes("İpek böcekçiliği tesisi");
            
            // Radio butonlar için doğru ID'leri seç
            const evetRadioId = ipekBocekcilikTesisi ? '#dut_bahcesi_var' : '#su_tahsis_var';
            const hayirRadioId = ipekBocekcilikTesisi ? '#dut_bahcesi_yok' : '#su_tahsis_yok';
            
            const evetRadio = Utils.getElement(evetRadioId);
            const hayirRadio = Utils.getElement(hayirRadioId);
            
            if (!evetRadio.checked && !hayirRadio.checked) {
                const errorMessage = ipekBocekcilikTesisi 
                    ? 'İpek böcekçiliği tesisi için dut bahçesi durumunu belirtmelisiniz.'
                    : 'YAS Kapalı Alan içinde seçtiğiniz yapı türü için Su Tahsis Belgesi durumunu belirtmelisiniz.';
                    
                sonuclarDiv.innerHTML = `<div class="sonuc-container"><p class="sonuc-red">${errorMessage}</p></div>`;
                return false;
            }
        }
        return true;
    },
    
    /**
     * Form verilerini hazırla
     */
    prepareFormData(form) {
        const formData = new FormData(form);
        
        const yapiTuruSelect = Utils.getElement(CONFIG.selectors.form.yapiTuru);
        const selectedIndex = yapiTuruSelect?.selectedIndex || -1;
        const selectedText = selectedIndex > -1 ? yapiTuruSelect.options[selectedIndex].text : '';
        const selectedValue = yapiTuruSelect?.value || '';
        
        const tapuVasfiSelect = Utils.getElement(CONFIG.selectors.form.tapuVasfi);
        const tapuVasfiText = tapuVasfiSelect?.options[tapuVasfiSelect.selectedIndex]?.text || '';
        const isDikiliVasifli = tapuVasfiText.includes('Dikili vasıflı');
        
        const araziBuyukluguInput = Utils.getElement(CONFIG.selectors.form.araziBuyuklugu);
        const araziBuyuklugu = parseFloat(araziBuyukluguInput?.value?.replace(',', '.') || '0');
        
        const isBagEvi = selectedValue === '14';
        
        // Eğer doğrudan "Yapılaşma Durumunu Sorgula" butonuna basılmışsa ve gönderim uyarısı istenmiyorsa,
        // dikiliAraziKontrolGecildi bayrağını kontrol etme
        if (isBagEvi && isDikiliVasifli && araziBuyuklugu >= 5000) {
            // Burada form gönderiminden önce global bir değişkeni kontrol ediyoruz
            // Bu değişken, kullanıcı dikili arazi kontrolünü geçtiğinde veya doğrudan atladığında true olarak ayarlanır
            // Eğer submit butonuna doğrudan tıklandıysa, bu değişkenin değeri false olacaktır
            
            // Eğer zaten window.noConfirmDikiliCheck=true ise veya window.dikiliAraziKontrolGecildi=true ise
            // onay kutusu gösterme ve doğrudan form gönder
            if (window.noConfirmDikiliCheck || window.dikiliAraziKontrolGecildi) {
                // Doğrudan devam et, dikili arazi kontrolü tamamlanmış kabul edilir
            } else {
                // Onay kutusu göster
                DikiliAraziKontrol.showConfirmation(
                    'Dikili arazi kontrol adımını geçmediniz. Devam etmek istiyor musunuz?',
                    'Kontrol Uyarısı',
                    () => {
                        // Onay verildiğinde bir sonraki gönderimde tekrar sormamak için bayrağı ayarla
                        window.dikiliAraziKontrolGecildi = true;
                        FormSubmission.submitFormWithData(new FormData(form));
                    },
                    () => {
                        // İptal
                    }
                );
                return false; 
            }
        }
        
        if (!isBagEvi) {
            formData.append('yas_kapali_alan_durumu', isInsideYasKapaliAlan ? 'içinde' : 'dışında');
        } else {
            formData.append('yas_kapali_alan_durumu', 'dışında');
        }
        
        if (isInsideBuyukOva) {
            formData.append('buyuk_ova_poligon_icinde_mi', 'true');
        }
        if (secilenLat && secilenLng) {
            formData.append('lat', secilenLat);
            formData.append('lng', secilenLng);
        }
        
        const yapiBilgileri = {
            tur_ad: selectedText
        };
        
        if (selectedText.includes('Sera')) {
            const seraAlaniInput = document.getElementById('id_sera_alani_m2');
            if (seraAlaniInput && seraAlaniInput.value) {
                yapiBilgileri.sera_alani_m2 = parseFloat(seraAlaniInput.value.replace(',', '.'));
            }
            formData.append('idari_bina_isteniyor', 'true');
            yapiBilgileri.idari_bina_isteniyor = true;
        }
        
        if (selectedText.includes('Hububat ve yem depolama silosu')) {
            const siloAlaniInput = document.getElementById('id_silo_alani_m2'); 
            if (siloAlaniInput && siloAlaniInput.value) {
                yapiBilgileri.planlanan_silo_taban_alani_m2 = parseFloat(siloAlaniInput.value.replace(',', '.'));
                // console.log("Kullanıcıdan alınan silo alanı:", yapiBilgileri.planlanan_silo_taban_alani_m2, "m²"); // Kaldırıldı
            } else {
                // console.warn("Silo alanı input değeri alınamadı. Backend varsayılanı kullanılabilir veya hata verecektir."); // İsteğe bağlı tutulabilir
            }
        }
        
        formData.append('yapi_bilgileri', JSON.stringify(yapiBilgileri));
        
        formData.append('arazi_vasfi_id', formData.get('tapu_vasfi'));
        formData.append('yapi_turu_id', formData.get('yapi_turu'));
        formData.append('arazi_buyuklugu_m2', formData.get('arazi_buyuklugu'));
        
        // console.log("Gönderilecek form verileri:", Array.from(formData.entries())); // Kaldırıldı
        // console.log("Yapı bilgileri:", yapiBilgileri); // Kaldırıldı
        return formData;
    },
    
    /**
     * Form gönderimi
     */
    submitForm(form, formData, sonuclarDiv) {
        const csrftoken = Utils.getCookie('csrftoken');
        const buyukOvaUyariElement = Utils.getElement(CONFIG.selectors.buyukOvaUyari);
        
        // Form gönderilmeden önce Büyük Ova uyarısını gizleyelim
        if (buyukOvaUyariElement) {
            Utils.setVisibility(buyukOvaUyariElement, false);
        }
        
        fetch(form.action, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // console.log("Sunucudan dönen JSON verisi:", data); // Kaldırıldı
            
            const loadingIndicator = document.getElementById('loading-indicator');
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
            
            ResultsModule.displayFormResults(data, sonuclarDiv);

            // İzin durumuna göre Büyük Ova uyarısının görünürlüğünü ayarla
            if (buyukOvaUyariElement) {
                // İzin verilemez durumunda, büyük ova içinde olsa bile uyarıyı gösterme
                if (isInsideBuyukOva && data.izin_durumu !== "izin_verilemez") {
                    Utils.setVisibility(buyukOvaUyariElement, true);
                } else {
                    Utils.setVisibility(buyukOvaUyariElement, false);
                }
                
                // ResultsModule sonuçları gösterdikten sonra ek bir kontrol
                setTimeout(() => {
                    if (data.izin_durumu === "izin_verilemez") {
                        // Herhangi bir büyük ova içeriği DOM'da varsa gizle
                        const buyukOvaIcerenElementler = document.querySelectorAll('.buyuk-ova-bilgi, [data-buyuk-ova]');
                        buyukOvaIcerenElementler.forEach(el => {
                            Utils.setVisibility(el, false);
                        });
                    }
                }, 100);
            }
        })
        .catch(error => {
            // Hata durumunda da yükleme göstergesini kapat
            const loadingIndicator = document.getElementById('loading-indicator');
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
            
            ResultsModule.displayFormError(error, sonuclarDiv);
        });
    },
    
    /**
     * Form sonuçlarını görüntüle
     */
    displayFormResults(data, sonuclarDiv) {
        // Sonuçları içeren ana kapsayıcı div
        const sonucContainer = document.createElement('div');
        sonucContainer.className = 'sonuc-container';
        
        // Başlık
        const baslik = document.createElement('h3');
        baslik.className = 'sonuc-baslik';
        baslik.innerText = 'Sorgu Sonucu';
        sonucContainer.appendChild(baslik);
        
        // İzin durumu
        const izinDurumu = document.createElement('p');
        izinDurumu.className = 'izin-durumu';
        izinDurumu.innerHTML = `İzin Durumu: <strong>${data.izin_durumu || 'Belirtilmemiş'}</strong>`;
        sonucContainer.appendChild(izinDurumu);
        
        // Açıklama
        if (data.aciklama) {
            const aciklama = document.createElement('p');
            aciklama.className = 'sonuc-aciklama';
            aciklama.innerHTML = data.aciklama;
            sonucContainer.appendChild(aciklama);
        }
        
        // Büyük Ova içindeki için bilgilendirme
        if (data.buyuk_ova_icerisinde) {
            const buyukOvaBilgi = document.createElement('p');
            buyukOvaBilgi.className = 'buyuk-ova-bilgi';
            buyukOvaBilgi.setAttribute('data-buyuk-ova', 'true');
            buyukOvaBilgi.innerHTML = 'Seçilen alan Büyük Ova Koruma Alanı sınırları içerisinde yer almaktadır. Bu nedenle ilgili değerlendirme süreci standarttan daha uzun sürebilir.';
            sonucContainer.appendChild(buyukOvaBilgi);
        }
        
        // Ekstralar varsa ekle
        if (data.ekstralar && data.ekstralar.length > 0) {
            const ekstralarListesi = document.createElement('ul');
            ekstralarListesi.className = 'ekstralar-listesi';
            
            data.ekstralar.forEach(ekstra => {
                const ekstraItem = document.createElement('li');
                ekstraItem.className = 'ekstra-item';
                ekstraItem.innerText = ekstra;
                ekstralarListesi.appendChild(ekstraItem);
            });
            
            sonucContainer.appendChild(ekstralarListesi);
        }
        
        // Sonuçları göster
        sonuclarDiv.innerHTML = '';
        sonuclarDiv.appendChild(sonucContainer);
        
        // Sıfırlama butonu ekle (eski kodu kaldır, bunu addResetButtonToResults ile yapacağız)
    },
    
    /**
     * Form gönderimi hata mesajını görüntüle
     */
    displayFormError(error, resultsContainer) {
        resultsContainer.innerHTML = `
            <div class="sonuc-container">
                <p class="sonuc-red">&#10007; Sorgu işlenirken bir hata oluştu. Lütfen daha sonra tekrar deneyiniz.</p>
                <!-- Buton eklenmiyor, bunu addResetButtonToResults ile yapacağız -->
            </div>
        `;
        
        console.error('Form gönderimi hatası:', error);
        
        // Hata sonuçlarının altına da sıfırlama butonu ekle
        this.addResetButtonToResults(resultsContainer.querySelector('.sonuc-container'));
    },
    
    /**
     * Sonuç kutusuna yeni sorgu butonu ekle (ayrı bir fonksiyon olarak)
     */
    addResetButtonToResults(containerElement) {
        if (!containerElement) return;
        
        // Mevcut bir Yeni Sorgu butonu varsa kaldır
        const existingResetBtn = containerElement.querySelector('.reset-button-container');
        if (existingResetBtn) {
            existingResetBtn.remove();
        }
        
        // Yeni buton konteynerı ve butonu oluştur
        const resetButtonContainer = document.createElement('div');
        resetButtonContainer.className = 'reset-button-container';
        resetButtonContainer.style.marginTop = '20px';
        resetButtonContainer.style.textAlign = 'center';
        
        const resetButton = document.createElement('button');
        resetButton.className = 'submit-button';
        resetButton.style.backgroundColor = '#7f8c8d'; // Gri renk
        resetButton.innerHTML = '<i class="fas fa-redo"></i> Yeni Sorgu';
        resetButton.addEventListener('click', this.resetForm.bind(this));
        
        resetButtonContainer.appendChild(resetButton);
        containerElement.appendChild(resetButtonContainer);
    },
    
    /**
     * Formu sıfırla ve yeni sorgu başlat
     */
    resetForm() {
        // Form alanlarını sıfırla
        const form = document.getElementById('imar-durumu-form');
        if (form) form.reset();
        
        // Tapu vasfı değişim olayını tetikle (diğer alanların görünürlüğünü sıfırlamak için)
        const tapuVasfiSelect = document.getElementById('id_tapu_vasfi');
        if (tapuVasfiSelect) {
            // Event nesnesi yoksa manuel olarak oluşturup tetikliyoruz
            const event = new Event('change');
            tapuVasfiSelect.dispatchEvent(event);
        }
        
        // Sonuçlar bölümünü temizle
        const sonuclarDiv = document.getElementById('sonuclar');
        if (sonuclarDiv) {
            sonuclarDiv.innerHTML = '';
            Utils.setVisibility(sonuclarDiv, false);
        }
        
        // Dikili arazi kontrol panellerini gizle
        const dikiliPaneller = [
            'dikili-arazi-kontrol-panel',
            'harita-secim-panel',
            'manuel-agac-panel'
        ];
        
        dikiliPaneller.forEach(id => {
            const panel = document.getElementById(id);
            if (panel) panel.style.display = 'none';
        });
        
        // Harita üzerindeki çizimleri temizle
        if (typeof DikiliAraziKontrol === 'object' && typeof DikiliAraziKontrol.clearPolygon === 'function') {
            DikiliAraziKontrol.clearPolygon();
        }
        
        // DikiliAraziKontrol'ün eklediği verileri sıfırla
        if (typeof DikiliAraziKontrol === 'object') {
            DikiliAraziKontrol.eklenenAgaclar = [];
            DikiliAraziKontrol.manuelEklenenAgaclar = [];
            DikiliAraziKontrol.secilenAlanMetrekare = 0;
            DikiliAraziKontrol.manuelAlanMetrekare = 0;
            
            if (DikiliAraziKontrol.ui.manuelAlanInput) {
                DikiliAraziKontrol.ui.manuelAlanInput.value = '';
            }
            
            DikiliAraziKontrol.updateAgacListesi('harita');
            DikiliAraziKontrol.updateAgacListesi('manuel');
            
            // Sonuç bölümlerini gizle
            if (DikiliAraziKontrol.ui.dikiliAlanSonuc) {
                DikiliAraziKontrol.ui.dikiliAlanSonuc.style.display = 'none';
            }
            if (DikiliAraziKontrol.ui.manuelDikiliAlanSonuc) {
                DikiliAraziKontrol.ui.manuelDikiliAlanSonuc.style.display = 'none';
            }
            
            // Devam butonlarını gizle
            if (DikiliAraziKontrol.ui.haritaDevamBtn) {
                DikiliAraziKontrol.ui.haritaDevamBtn.style.display = 'none';
            }
            if (DikiliAraziKontrol.ui.manuelDevamBtn) {
                DikiliAraziKontrol.ui.manuelDevamBtn.style.display = 'none';
            }
        }
        
        // Dikili arazi kontrolü bayrağını sıfırla
        window.dikiliAraziKontrolGecildi = false;
        
        // Scrollu en başa al
        window.scrollTo(0, 0);
    }
};
