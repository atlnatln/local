/**
 * İmar durumu sorgulama formu için JavaScript işleyicisi - Optimize edilmiş versiyon
 */
document.addEventListener('DOMContentLoaded', function() {
    // ========================
    // Temel değişkenler ve sabitleri tanımlama
    // ========================
    // CONFIG.BAKICI_EVI_UYGUN_YAPI_TIPLERI kullanılmalı.

    // ========================
    // Yardımcı fonksiyonlar
    // ========================
    // Utils.getCookie kullanılmalı.

    // Form elemanlarını seçme
    function getFormElements() {
        return {
            form: document.getElementById('imar-durumu-form'),
            sonucContainer: document.getElementById('sonuc-container')
        };
    }
    
    // Form doğrulama
    function validateForm(formData) {
        // Burada gerekli form alanlarını kontrol edebilirsiniz
        return true; // Basit örnek
    }
    
    // Form verilerini hazırlama
    function prepareFormData(form) {
        const formData = new FormData(form);
        const formDataObj = {
            arazi_vasfi_id: formData.get('tapu_vasfi'),
            yapi_turu_id: formData.get('yapi_turu'),
            arazi_buyuklugu_m2: parseFloat(formData.get('arazi_buyuklugu') || 0)
        };
        
        // YAS Kapalı Alan durumu
        formDataObj.yas_kapali_alan_durumu = formData.get('yas_kapali_alan_durumu') || 'degerlendirilmedi';
        
        // Büyük Ova durumu
        if (formData.get('buyuk_ova_poligon_icinde_mi')) {
            formDataObj.buyuk_ova_poligon_icinde_mi = formData.get('buyuk_ova_poligon_icinde_mi') === 'true';
        }
        
        // Su tahsis belgesi durumu
        if (formData.get('su_tahsis_belgesi_var_mi')) {
            formDataObj.su_tahsis_belgesi_var_mi = formData.get('su_tahsis_belgesi_var_mi') === 'true';
        }
        
        // Dut bahçesi durumu
        if (formData.get('dut_bahcesi_var_mi')) {
            formDataObj.dut_bahcesi_var_mi = formData.get('dut_bahcesi_var_mi') === 'true';
        }

        // Silo için planlanan taban alanı (yapı türü silo ise ekle)
        const yapiTuruText = formData.get('yapi_turu_text') || '';
        // Eğer formda yapi_turu_text yoksa, yapi_turu_id ile kontrol edilebilir (gerekirse mapping eklenir)
        if (
            yapiTuruText === 'Hububat ve yem depolama silosu' ||
            formData.get('yapi_turu') === '5' // id ile kontrol (gerekirse güncelle)
        ) {
            const siloAlani = formData.get('planlanan_silo_taban_alani_m2');
            if (siloAlani) {
                formDataObj.planlanan_silo_taban_alani_m2 = parseFloat(siloAlani);
            }
        }

        return { formData, formDataObj };
    }
    
    // Yükleniyor gösterge
    function showLoading(container) {
        container.innerHTML = '<div class="alert alert-info">Sorgulanıyor, lütfen bekleyiniz...</div>';
    }
    
    // Form gönderimi
    function submitForm(form, formData, formDataObj, container) {
        console.log('Gönderilecek veri:', formDataObj);
        
        const csrftoken = Utils.getCookie('csrftoken');
        
        fetch('/sorgula-imar-durumu/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams(formData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Sunucu hatası: ' + response.status + ' ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            console.log('Yanıt:', data);
            renderResults(data, container);
        })
        .catch(error => {
            renderError(error, container);
        });
    }
    
    // Sonuçları render etme
    function renderResults(data, container) {
        if (!data) {
            renderError(new Error('Boş yanıt alındı'), container);
            return;
        }
        
        // Sonuç HTML'ini oluştur
        let html = '<div class="imar-sonuc">';
        html += '<h3>İmar Durumu Sonucu</h3>';
        
        // Ana mesaj
        if (data.ana_mesaj) {
            const durumClass = data.izin_durumu === 'izin_verilebilir' ? 'success' : 
                             data.izin_durumu === 'izin_verilemez' ? 'danger' : 'warning';
            html += `<div class="alert alert-${durumClass}">${data.ana_mesaj}</div>`;
        } else if (data.mesaj) {
            const durumClass = data.durum === 'uygun' || data.durum === 'izin_verilebilir' ? 'success' : 
                             data.durum === 'yetersiz' || data.durum === 'izin_verilemez' ? 'danger' : 'warning';
            html += `<div class="alert alert-${durumClass}">${data.mesaj}</div>`;
        }
        
        // Bakıcı evi bilgileri
        html += renderBakiciEviBilgileri(data);
        
        // Özel durumlar ve ek bilgiler
        html += renderEkBilgiler(data);
        
        // Hata durumu
        if (data.error) {
            html += renderErrorInfo(data);
        }
        
        html += '</div>';
        container.innerHTML = html;
    }
    
    // Bakıcı evi bilgileri
    function renderBakiciEviBilgileri(data) {
        let html = '';
        
        if (data.detay_mesaj_bakici_evi) {
            html += '<div class="card mt-3"><div class="card-header">Bakıcı Evi Bilgileri</div>';
            html += `<div class="card-body">${data.detay_mesaj_bakici_evi}</div></div>`;
            
            // Detaylı bakıcı evi mesajları
            const bakiciEviMesajlari = [
                'bilgi_mesaji_bakici_evi_buyukbas',
                'bilgi_mesaji_bakici_evi_agil',
                'bilgi_mesaji_bakici_evi_kanatli',
                'bilgi_mesaji_bakici_evi_hara',
                'bilgi_mesaji_bakici_evi_ipek_bocegi',
                'bilgi_mesaji_bakici_evi_evcil_hayvan'
            ];
            
            bakiciEviMesajlari.forEach(key => {
                if (data[key]) {
                    html += `<div class="card mt-2"><div class="card-body">${data[key]}</div></div>`;
                }
            });
        }
        
        return html;
    }
    
    // Ek bilgiler (özel durum, büyük ova, sonraki adım vb.)
    function renderEkBilgiler(data) {
        let html = '';
        
        // Özel durum uyarısı
        if (data.uyari_mesaji_ozel_durum) {
            html += `<div class="alert alert-warning mt-3">${data.uyari_mesaji_ozel_durum}</div>`;
        }
        
        // Büyük ova bilgisi
        if (data.surec_bilgisi_buyuk_ova) {
            html += `<div class="alert alert-info mt-3">${data.surec_bilgisi_buyuk_ova}</div>`;
        }
        
        // Sonraki adım bilgisi
        if (data.sonraki_adim_bilgisi) {
            html += `<div class="alert alert-secondary mt-3">${data.sonraki_adim_bilgisi}</div>`;
        }
        
        return html;
    }
    
    // Hata bilgisi
    function renderErrorInfo(data) {
        let html = '';
        
        html += `<div class="alert alert-danger mt-3">Hata: ${data.hata}</div>`;
        if (data.traceback) {
            html += `<div class="card mt-2"><div class="card-header">Hata Detayı</div>`;
            html += `<div class="card-body"><pre>${data.traceback}</pre></div></div>`;
        }
        
        return html;
    }
    
    // Genel hata mesajı
    function renderError(error, container) {
        console.error('Hata:', error);
        
        let html = `<div class="alert alert-danger">Bir hata oluştu: ${error.message}</div>`;
        html += `<div><p>Lütfen şunları kontrol edin:</p>
            <ul>
                <li>Sunucu çalışıyor mu?</li>
                <li>Ağ bağlantınız düzgün çalışıyor mu?</li>
                <li>Tarayıcı konsolunda (F12) başka hatalar var mı?</li>
            </ul></div>`;
            
        container.innerHTML = html;
    }
    
    // Form gönderim işleyicisi
    function handleFormSubmit(e) {
        e.preventDefault();
        console.log('Form gönderiliyor...');
        
        const { form, sonucContainer } = getFormElements();
        if (!form || !sonucContainer) {
            console.error('Form veya sonuç konteyner elemanı bulunamadı');
            return;
        }
        
        // Form verilerini hazırla
        const { formData, formDataObj } = prepareFormData(form);
        
        // Form verilerini göster (debug için)
        for (const pair of formData.entries()) {
            console.log(pair[0] + ': ' + pair[1]);
        }
        
        // Form doğrulama
        if (!validateForm(formData)) {
            return;
        }
        
        // Yükleniyor mesajını göster
        showLoading(sonucContainer);
        
        // Formu gönder
        submitForm(form, formData, formDataObj, sonucContainer);
    }
    
    // ========================
    // KML dosyalarını yükleme
    // ========================
    
    // KML handler fonksiyonları
    function handleIzmirKmlLoaded(kmlLayer) {
        console.log('İzmir KML dosyası yüklendi');
        // İzmir poligonu ile ilgili işlemler
        if (window.PolygonModule) {
            PolygonModule.addPolygon('izmir', kmlLayer);
        }
    }
    
    function handleYasKapaliAlanLoaded(kmlLayer) {
        console.log('YAŞ Kapalı Alan KML dosyası yüklendi');
        // YAŞ Kapalı Alan poligonu ile ilgili işlemler
        if (window.PolygonModule) {
            PolygonModule.addPolygon('yasKapaliAlan', kmlLayer);
        }
    }
    
    function handleBuyukOvaLoaded(kmlLayer) {
        console.log('Büyük Ova KML dosyası yüklendi');
        // Büyük Ova poligonu ile ilgili işlemler
        if (window.PolygonModule) {
            PolygonModule.addPolygon('buyukOva', kmlLayer);
        }
    }
    
    // KML cache sistemi - tekrarlı yüklemeyi önlemek için
    const kmlCache = new Map();
    
    // KML dosyası yükleme yardımcı fonksiyonları
    function loadSpecificKml(kmlConfig) {
        if (!kmlConfig || !kmlConfig.url) {
            console.error('Geçersiz KML yapılandırması');
            return Promise.reject('Geçersiz KML yapılandırması');
        }
        
        // Cache'de var mı kontrol et
        if (kmlCache.has(kmlConfig.url)) {
            console.log(`KML cache'den yüklendi: ${kmlConfig.url}`);
            const cachedKml = kmlCache.get(kmlConfig.url);
            
            // Callback fonksiyonunu çağır
            if (kmlConfig.onLoad && typeof kmlConfig.onLoad === 'function') {
                kmlConfig.onLoad(cachedKml);
            }
            
            return Promise.resolve(cachedKml);
        }
        
        console.log(`KML dosyası yükleniyor: ${kmlConfig.url}`);
        return fetch(kmlConfig.url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`KML dosyası yüklenemedi: ${response.status}`);
                }
                return response.text();
            })
            .then(kmlText => {
                // KML verisini işle ve harita katmanı oluştur
                const parser = new DOMParser();
                const kmlDoc = parser.parseFromString(kmlText, 'text/xml');
                
                // Cache'e kaydet
                kmlCache.set(kmlConfig.url, kmlDoc);
                console.log(`KML cache'e kaydedildi: ${kmlConfig.url}`);
                
                if (kmlConfig.onLoad && typeof kmlConfig.onLoad === 'function') {
                    kmlConfig.onLoad(kmlDoc);
                }
                
                return kmlDoc;
            })
            .catch(error => {
                console.error('KML yükleme hatası:', error);
                throw error;
            });
    }
    
    function loadVisibleKmlLayers(kmlLayers, bounds) {
        if (!Array.isArray(kmlLayers)) {
            console.error('KML katmanları geçersiz');
            return;
        }
        
        // Tüm KML dosyaları cache'de var mı kontrol et
        const allCached = kmlLayers.every(kmlConfig => kmlCache.has(kmlConfig.url));
        
        if (allCached) {
            console.log('Tüm KML dosyaları zaten cache\'de, yeniden yükleme yapılmıyor');
            return Promise.resolve('Tüm KML dosyaları cache\'de');
        }
        
        // Sadece cache'de olmayan KML dosyalarını yükle
        const loadPromises = kmlLayers
            .filter(kmlConfig => !kmlCache.has(kmlConfig.url))
            .map(kmlConfig => {
                console.log(`Cache'de olmayan KML yükleniyor: ${kmlConfig.url}`);
                return loadSpecificKml(kmlConfig).catch(error => {
                    console.warn(`KML katmanı yüklenemedi: ${kmlConfig.url}`, error);
                    return null; // Hata durumunda null döndür ama diğer yüklemeleri durdurma
                });
            });
        
        if (loadPromises.length === 0) {
            console.log('Yüklenecek yeni KML dosyası yok');
            return Promise.resolve('Tüm KML dosyaları zaten yüklü');
        }
        
        return Promise.allSettled(loadPromises);
    }
    
    function loadKmlLayers() {
        // Django static URL'lerini kullan (HTML'de tanımlı)
        const kmlLayersToLoad = [
            { url: typeof KML_IZMIR_URL !== 'undefined' ? KML_IZMIR_URL : '/static/izmir.kml', onLoad: handleIzmirKmlLoaded },
            { url: typeof KML_IZMIR_KAPALI_ALAN_URL !== 'undefined' ? KML_IZMIR_KAPALI_ALAN_URL : '/static/izmir_kapali_alan.kml', onLoad: handleYasKapaliAlanLoaded },
            { url: typeof KML_BUYUK_OVALAR_IZMIR_URL !== 'undefined' ? KML_BUYUK_OVALAR_IZMIR_URL : '/static/Büyük Ovalar İzmir.kml', onLoad: handleBuyukOvaLoaded }
        ];

        // Map nesnesinin hazır olmasını bekle - daha güvenli kontrol
        if (typeof window.map !== 'undefined' && 
            window.map !== null && 
            typeof window.map.on === 'function') {
            
            try {
                // moveend event'ini sadece bir kez ekle
                if (!loadKmlLayers.eventAdded) {
                    window.map.on('moveend', function() {
                        // Sadece koordinat kontrolü yap, KML yeniden yükleme
                        console.log('Harita hareket etti, koordinat kontrolü yapılıyor');
                        // Burada sadece koordinat bazlı kontroller yapılabilir
                        // KML dosyaları cache'den kullanılır
                    });
                    loadKmlLayers.eventAdded = true;
                }

                // İlk KML yüklemesini yap (tüm KML dosyalarını)
                console.log('İlk KML yüklemesi başlatılıyor');
                const loadPromises = kmlLayersToLoad.map(kmlConfig => 
                    loadSpecificKml(kmlConfig).catch(error => {
                        console.warn(`İlk KML yüklemesi başarısız: ${kmlConfig.url}`, error);
                        return null;
                    })
                );
                
                Promise.allSettled(loadPromises).then(results => {
                    const successCount = results.filter(result => result.status === 'fulfilled').length;
                    console.log(`KML yüklemesi tamamlandı: ${successCount}/${kmlLayersToLoad.length} dosya başarıyla yüklendi`);
                });
                
            } catch (error) {
                console.error('KML katmanları yüklenirken hata oluştu:', error);
            }
        } else {
            // Map henüz hazır değilse 200ms sonra tekrar dene (daha uzun süre bekle)
            // En fazla 10 saniye bekle (50 * 200ms = 10s)
            if (!loadKmlLayers.attempts) loadKmlLayers.attempts = 0;
            loadKmlLayers.attempts++;
            
            if (loadKmlLayers.attempts <= 50) {
                setTimeout(() => loadKmlLayers(), 200);
            } else {
                console.warn('Harita nesnesi 10 saniye içinde yüklenemedi, KML katmanları atlandı');
            }
        }
    }
    
    // ========================
    // Ana çalıştırma bloğu
    // ========================
    function init() {
        const { form } = getFormElements();
        
        if (form) {
            form.addEventListener('submit', handleFormSubmit);
        } else {
            console.error('İmar sorgu formu bulunamadı!');
        }

        // KML katmanlarını yüklemeyi biraz geciktir (diğer modüllerin yüklenmesini bekle)
        setTimeout(() => {
            loadKmlLayers();
        }, 500);
    }
    
    // Uygulamayı başlat
    init();
});