// ========================
// 7. SONUÇLAR MODÜLÜ
// ========================
const ResultsModule = {
    /**
     * Yükleniyor göster
     */
    showLoading(container) {
        Utils.setVisibility(container, true);
        container.innerHTML = '<div class="yukleniyor-bilgi">İmar durumu sorgulanıyor, lütfen bekleyiniz...</div>';
    },
    
    /**
     * Sonuçları göster - UX-optimize format desteği ile
     */
    displayFormResults(data, container) {
        if (!data || Object.keys(data).length === 0) {
            container.innerHTML = `
                <h3 class="sonuc-baslik">İmar Durumu Sonucu</h3>
                <div class="sonuc-container">
                    <p><span class="sonuc-red">Sunucudan boş veya geçersiz yanıt alındı.</span></p>
                </div>`;
            return;
        }
        
        // UX-optimize format kontrolü (Issue #21)
        if (typeof UXOptimizedRenderer !== 'undefined' && 
            data.result && data.explanation && data.summary) {
            
            // Yeni UX-optimize format kullan
            UXOptimizedRenderer.renderOptimizedResults(data, container);
            return;
        }
        
        // Legacy format (mevcut sistem)
        let sonucHtml = '<h3 class="sonuc-baslik">İmar Durumu Sonucu</h3><div class="sonuc-container">';
        if (data.ozet_mesaj) {
            sonucHtml += `<div class="alert alert-secondary mt-3" style="white-space:pre-line;">${data.ozet_mesaj}</div>`;
        } else if (data.sonraki_adim_bilgisi) {
            sonucHtml += `<div class="alert alert-secondary mt-3" style="white-space:pre-line;">${data.sonraki_adim_bilgisi}</div>`;
        }
        
        if (data.durum) {
            sonucHtml += this.renderByDurumType(data);
        } else if (data.error && data.hata) {
            sonucHtml += this.renderErrorState(data);
        } else if (data.izin_durumu) {
            sonucHtml += this.renderByIzinDurumu(data);
        } else {
            sonucHtml += this.renderUnknownFormat(data);
        }
        
        sonucHtml += '</div>';
        container.innerHTML = sonucHtml;
        
        // Büyük ova uyarısı göster
        if (typeof isInsideBuyukOva !== "undefined" && isInsideBuyukOva) {
            Utils.setVisibility(Utils.getElement(CONFIG.selectors.buyukOvaUyari), true);
        }
        
        // Yeni sorgu butonunu ekle
        const newQueryButton = document.createElement('button');
        newQueryButton.className = 'btn btn-secondary yeni-sorgu-btn';
        newQueryButton.innerHTML = '<i class="fas fa-redo"></i> Yeni Sorgu';
        newQueryButton.addEventListener('click', () => {
            this.resetForm();
        });
        
        container.appendChild(newQueryButton);
    },
    
    /**
     * Durum tipine göre render et
     */
    renderByDurumType(data) {
        let html = '';
        switch (data.durum) {
            case 'limit_asildi':
                html += this.renderLimitAsildi(data);
                break;
            case 'uygun':
            case 'izin_verilebilir':
                html += this.renderIzinVerilir(data);
                break;
            case 'yetersiz':
            case 'izin_verilemez':
                html += this.renderIzinVerilmez(data);
                break;
            case 'su_tahsisi':
            case 'bulunamadi':
                html += this.renderSuTahsisiOrBulunamadi(data);
                break;
            case 'hata':
                html += this.renderHataDurumu(data);
                break;
        }
        if (data.surec_bilgisi_buyuk_ova) {
            html += `<div class="buyuk-ova-bilgi">${data.surec_bilgisi_buyuk_ova}</div>`;
        }
        return html;
    },
    
    /**
     * Limit aşıldı durumu için HTML
     */
    renderLimitAsildi(data) {
        return `
            <div class="limit-asildi-uyari">
                <p><i class="fas fa-exclamation-triangle"></i> ${data.mesaj}</p>
                <div class="login-buttons">
                    <a href="/hesaplar/login/" class="btn btn-primary">Giriş Yap</a>
                    <a href="/hesaplar/register/" class="btn btn-secondary">Kayıt Ol</a>
                </div>
            </div>
        `;
    },
    
    /**
     * İzin verilebilir durumu için HTML
     */
    renderIzinVerilir(data) {
        let html = `<p><span class="sonuc-green">✓ ${data.mesaj || 'Yapılaşma şartlarına uygundur'}</span></p>`;
        if (data.detay_mesaj_bakici_evi) {
            html += this.renderBakiciEviDetails(data.detay_mesaj_bakici_evi);
        }
        
        const yapiTuruId = data.yapi_turu_id || data.yapiTurId; // Yapı türü ID'sini al

        // Proje türünü belirle (Sera) - Mevcut Sera mantığı korunabilir veya o da yapiTuruId kullanabilir.
        const isSeraProjectResult =
            (data.hasOwnProperty('maksimum_idari_bina_alani') && !data.hasOwnProperty('maks_idari_teknik_bina_alani_m2')) ||
            (data.mesaj && data.mesaj.toLowerCase().includes('sera')) ||
            (data.ana_mesaj && data.ana_mesaj.toLowerCase().includes('sera'));
            
        // Eski isSiloProjectResult koşulunu kaldır/devre dışı bırak
        /*
        const isSiloProjectResult =
            data.hasOwnProperty('maks_idari_teknik_bina_alani_m2') ||
            data.hasOwnProperty('maks_toplam_kapali_yapi_hakki_m2') ||
            data.hasOwnProperty('senaryo_tipi') ||
            (data.mesaj && data.mesaj.toLowerCase().includes('silo')) ||
            (data.ana_mesaj && data.ana_mesaj.toLowerCase().includes('silo'));
        */
        
        if (isSeraProjectResult) {
            html += this.renderSeraDetails(data);
        }
        
        // Silo detaylarını yalnızca yapiTuruId 5 ise ekle
        if (yapiTuruId == 5) { // YALNIZCA Silo (ID 5) ise Silo detaylarını ekle
            html += this.renderSiloDetails(data);
        }
        
        if (data.detay_mesaj_bakici_evi) {
            html += this.renderBakiciEviDetails(data.detay_mesaj_bakici_evi);
        }
        
        if (data.surec_bilgisi_buyuk_ova) {
            html += `<div class="buyuk-ova-bilgi">${data.surec_bilgisi_buyuk_ova}</div>`;
        }
        
        return html;
    },
    
    /**
     * İzin verilemez durumu için HTML
     */
    renderIzinVerilmez(data) {
        return `<p><span class="sonuc-red">✗ ${data.mesaj}</span></p>`;
    },
    
    /**
     * Su tahsisi veya bulunamadı durumu için HTML
     */
    renderSuTahsisiOrBulunamadi(data) {
        return `<p><span class="sonuc-uyari">! ${data.mesaj}</span></p>`;
    },
    
    /**
     * Hata durumu için HTML
     */
    renderHataDurumu(data) {
        return `<p><span class="sonuc-red">✗ ${data.mesaj || 'Bir hata oluştu'}</span></p>`;
    },
    
    /**
     * İzin durumu bazlı formatlama
     */
    renderByIzinDurumu(data) {
        const durumClass = data.izin_durumu === 'izin_verilebilir' ? 'sonuc-green' : 
                         data.izin_durumu === 'izin_verilemez' ? 'sonuc-red' : 'sonuc-uyari';
        const icon = data.izin_durumu === 'izin_verilebilir' ? '✓' : '✗';
        let html = `<p><span class="${durumClass}">${icon} ${data.ana_mesaj || data.mesaj}</span></p>`;
        
        const yapiTuruId = data.yapi_turu_id || data.yapiTurId; // Yapı türü ID'sini al

        // Proje türünü belirle (Sera) - Mevcut Sera mantığı korunabilir veya o da yapiTuruId kullanabilir.
        const isSeraProjectResult =
            (data.hasOwnProperty('maksimum_idari_bina_alani') && !data.hasOwnProperty('maks_idari_teknik_bina_alani_m2')) ||
            (data.mesaj && data.mesaj.toLowerCase().includes('sera')) ||
            (data.ana_mesaj && data.ana_mesaj.toLowerCase().includes('sera'));
            
        // Eski isSiloProjectResult koşulunu kaldır/devre dışı bırak
        /*
        const isSiloProjectResult =
            data.hasOwnProperty('maks_idari_teknik_bina_alani_m2') ||
            data.hasOwnProperty('maks_toplam_kapali_yapi_hakki_m2') ||
            data.hasOwnProperty('senaryo_tipi') ||
            (data.mesaj && data.mesaj.toLowerCase().includes('silo')) ||
            (data.ana_mesaj && data.ana_mesaj.toLowerCase().includes('silo'));
        */
        
        if (isSeraProjectResult) {
            html += this.renderSeraDetails(data);
        }
        
        // Silo detaylarını yalnızca yapiTuruId 5 ise ekle
        if (yapiTuruId == 5) { // YALNIZCA Silo (ID 5) ise Silo detaylarını ekle
            html += this.renderSiloDetails(data);
        }
        
        if (data.detay_mesaj_bakici_evi) {
            html += this.renderBakiciEviDetails(data.detay_mesaj_bakici_evi);
        }
        
        // Bağ evi için özel kuralları listele
        if (yapiTuruId === 14 && Array.isArray(data.unmet_rules)) {
            if (data.unmet_rules.length > 0) {
                html += '<ul class="bag-evi-kurallari">';
                data.unmet_rules.forEach(rule => {
                    html += `<li>${rule}</li>`;
                });
                html += '</ul>';
            }
        }
        
        if (data.surec_bilgisi_buyuk_ova) {
            html += `<div class="buyuk-ova-bilgi">${data.surec_bilgisi_buyuk_ova}</div>`;
        }
        
        return html;
    },
    
    /**
     * Sera detayları için HTML
     */
    renderSeraDetails(data) {
        let seraHtml = '<div class="sera-bilgileri"><h4>Sera Projesi Bilgileri</h4>';
        if (data.maksimum_taban_alani) {
            seraHtml += `<p><strong>Planlanan Sera Alanı:</strong> ${data.maksimum_taban_alani} m²</p>`;
        }
        if (data.maksimum_idari_bina_alani !== undefined && data.maksimum_idari_bina_alani !== null) {
            seraHtml += `<div class="highlight-info"><strong>İzin Verilen Maksimum İdari Bina Alanı:</strong> ${data.maksimum_idari_bina_alani} m²</div>`;
        }
        if (data.idari_bina_durumu) {
            seraHtml += `<p><strong>İdari Bina Koşulları:</strong> ${data.idari_bina_durumu}</p>`;
        }
        if (data.ges_bilgisi) {
            seraHtml += `<div class="ges-bilgisi mt-3" style="white-space:pre-line;">${data.ges_bilgisi}</div>`;
        }
        if (data.ozet_mesaj) {
            seraHtml += `<div class="alert alert-secondary mt-3" style="white-space:pre-line;">${data.ozet_mesaj}</div>`;
        } else if (data.sonraki_adim_bilgisi) {
            seraHtml += `<div class="alert alert-secondary mt-3" style="white-space:pre-line;">${data.sonraki_adim_bilgisi}</div>`;
        }
        seraHtml += '</div>';
        return seraHtml;
    },
    
    /**
     * Silo detayları için HTML
     */
    renderSiloDetails(data) {
        let siloHtml = '<div class="silo-bilgileri"><h4>Silo Projesi Detaylı Bilgiler</h4>';
        
        // Arazi ve silo büyüklük bilgileri
        if (data.giris_bilgileri) {
            const giris = data.giris_bilgileri;
            siloHtml += '<div class="silo-proje-bilgileri p-2 border rounded mb-3">';
            siloHtml += `<p><strong>Arazi Büyüklüğü:</strong> ${giris.parsel_buyuklugu_m2 ? giris.parsel_buyuklugu_m2.toFixed(2) : "?"} m²</p>`;
            siloHtml += `<p><strong>Planlanan Silo Taban Alanı:</strong> ${giris.planlanan_silo_taban_alani_m2 ? giris.planlanan_silo_taban_alani_m2.toFixed(2) : "?"} m²</p>`;
            siloHtml += '</div>';
        }
        
        // Hesaplama sonuçları
        if (data.maksimum_taban_alani || data.maksimum_toplam_alan || data.maks_toplam_kapali_yapi_hakki_m2) {
            const maksKapali = data.maks_toplam_kapali_yapi_hakki_m2 || data.maksimum_taban_alani || data.maksimum_toplam_alan;
            
            siloHtml += '<div class="highlight-info p-2 border rounded">';
            siloHtml += `<p><strong>Maksimum Toplam Yapılaşma Hakkı (%20):</strong> ${maksKapali ? maksKapali.toFixed(2) : "?"} m²</p>`;
            
            if (data.maks_idari_teknik_bina_alani_m2) {
                siloHtml += `<p><strong>İdari ve Teknik Bina İçin İzin Verilen Alan (%10):</strong> ${data.maks_idari_teknik_bina_alani_m2.toFixed(2)} m²</p>`;
            }
            
            if (data.kalan_emsal_hakki_m2 !== undefined && data.kalan_emsal_hakki_m2 !== null) {
                const kalanEmsalClass = data.kalan_emsal_hakki_m2 <= 0 ? "text-danger" : "text-success";
                siloHtml += `<p class="${kalanEmsalClass}"><strong>Kalan Yapılaşma Hakkı:</strong> ${data.kalan_emsal_hakki_m2.toFixed(2)} m²</p>`;
            }
            siloHtml += '</div>';
        }
        
        // Senaryo ve mesaj bilgileri
        if (data.senaryo_tipi) {
            siloHtml += `<div class="alert alert-info mt-3"><strong>Değerlendirme Senaryosu:</strong> ${data.senaryo_tipi}</div>`;
        }
        
        if (data.mesaj) {
            siloHtml += `<div class="silo-detay-mesaj mt-3" style="white-space:pre-line;">${data.mesaj}</div>`;
        } else if (data.sonraki_adim_bilgisi) {
            siloHtml += `<div class="alert alert-secondary mt-3" style="white-space:pre-line;">${data.sonraki_adim_bilgisi}</div>`;
        }
        
        siloHtml += '</div>';
        return siloHtml;
    },
    
    /**
     * Bakıcı evi detayları için HTML
     */
    renderBakiciEviDetails(message) {
        // Sabit mesaj yerine bakıcı evi uygunluk durumunu kontrol edip,
        // gerçek duruma göre uygun mesaj gösterelim
        
        // Default başlık her durumda aynı
        let bakiciEviBaslik = '<h4>Bakıcı Evi Yapılabilir Mi?</h4>';
        
        // Eğer detay_mesaj_bakici_evi mesajı "yapımı uygundur" ifadesini içeriyorsa uygun demektir
        const isUygun = message && message.toLowerCase().includes('yapımı uygundur');
        
        let customMessage;
        if (isUygun) {
            customMessage = `Tesisiniz arazinizin <a href="#" id="marjinal-link" class="marjinal-modal-trigger">marjinal tarım arazisi</a> olması durumunda bakıcı evi yapımı için uygundur. Arazinizin yerinde yapılacak etüt sonucunda <a href="#" id="mutlak-link" class="modal-trigger">mutlak</a>, <a href="#" id="ozel-link" class="modal-trigger">özel</a> veya <a href="#" id="dikili-link" class="modal-trigger">dikili</a> vasıflı olarak tespit edilmesi durumunda yapılaşma koşulları farklılık gösterir, Detaylı bilgi için mail ile iletişime geçebilirsiniz`;
        } else {
            // Uygun değilse, backend'den gelen asıl mesajı göster
            customMessage = message || "Mevcut arazi büyüklüğünüz ve yapı türü ile bakıcı evi yapımına izin verilmemektedir.";
        }
        
        // Modal HTML ekleme kodları...
        if (!document.getElementById('marjinal-modal')) {
            const modalHtml = `
            <div id="marjinal-modal" class="modal" style="display:none;position:fixed;z-index:9999;left:0;top:0;width:100vw;height:100vh;background:rgba(0,0,0,0.35);">
              <div class="modal-content" style="background:#fff;max-width:540px;margin:60px auto;padding:28px 24px 18px 24px;border-radius:10px;box-shadow:0 2px 16px rgba(0,0,0,0.18);position:relative;">
                <button id="marjinal-modal-close" style="position:absolute;top:10px;right:14px;background:none;border:none;font-size:22px;color:#888;cursor:pointer;" aria-label="Kapat">&times;</button>
                <div id="marjinal-modal-body">Yükleniyor...</div>
              </div>
            </div>`;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }
        if (!document.getElementById('tarim-modal')) {
            const modalHtml = `
            <div id="tarim-modal" class="modal" style="display:none;position:fixed;z-index:9999;left:0;top:0;width:100vw;height:100vh;background:rgba(0,0,0,0.35);">
              <div class="modal-content" style="background:#fff;max-width:540px;margin:60px auto;padding:28px 24px 18px 24px;border-radius:10px;box-shadow:0 2px 16px rgba(0,0,0,0.18);position:relative;">
                <button id="tarim-modal-close" style="position:absolute;top:10px;right:14px;background:none;border:none;font-size:22px;color:#888;cursor:pointer;" aria-label="Kapat">&times;</button>
                <div id="tarim-modal-body">Yükleniyor...</div>
              </div>
            </div>`;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }

        setTimeout(() => {
            const link = document.getElementById('marjinal-link');
            const modal = document.getElementById('marjinal-modal');
            const closeBtn = document.getElementById('marjinal-modal-close');
            const modalBody = document.getElementById('marjinal-modal-body');
            if (link && modal && closeBtn && modalBody) {
                link.onclick = function(e) {
                    e.preventDefault();
                    fetch('/static/ibb_plan_notlari.md')
                        .then(r => r.text())
                        .then(mdText => {
                            const start = mdText.indexOf('#### Marjinal Tarım Arazileri');
                            if (start === -1) {
                                modalBody.innerHTML = 'İçerik bulunamadı.';
                                modal.style.display = 'block';
                                return;
                            }
                            const rest = mdText.slice(start);
                            const lines = rest.split('\n');
                            let sectionLines = [lines[0]];
                            for (let i = 1; i < lines.length; i++) {
                                const line = lines[i];
                                if (/^(#### |### |## |# )/.test(line) && !/^#### Marjinal Tarım Arazileri/.test(line)) {
                                    break;
                                }
                                sectionLines.push(line);
                            }
                            const section = sectionLines.join('\n');
                            const md = window.markdownit();
                            modalBody.innerHTML = md.render(section);
                            modal.style.display = 'block';
                        });
                };
                closeBtn.onclick = function() { modal.style.display = 'none'; };
                window.addEventListener('click', function(e) {
                    if (e.target === modal) modal.style.display = 'none';
                });
            }
            function normalize(str) {
                return str.toLocaleLowerCase('tr-TR')
                    .replace(/ç/g, 'c').replace(/ğ/g, 'g').replace(/ı/g, 'i')
                    .replace(/ö/g, 'o').replace(/ş/g, 's').replace(/ü/g, 'u');
            }
            function openTarimModalForBaslik(baslik) {
                const modal = document.getElementById('tarim-modal');
                const closeBtn = document.getElementById('tarim-modal-close');
                const modalBody = document.getElementById('tarim-modal-body');
                if (!modal || !closeBtn || !modalBody) return;
                fetch('/static/ibb_plan_notlari.md')
                    .then(r => r.text())
                    .then(mdText => {
                        let anahtar = '';
                        if (baslik.toLowerCase().includes('özel')) anahtar = 'özel';
                        else if (baslik.toLowerCase().includes('dikili')) anahtar = 'dikili';
                        else if (baslik.toLowerCase().includes('mutlak')) anahtar = 'mutlak';
                        else anahtar = baslik.toLowerCase();
                        const lines = mdText.split('\n');
                        let foundLineIdx = -1;
                        let foundBaslik = '';
                        for (let i = 0; i < lines.length; i++) {
                            const line = lines[i].trim();
                            if (line.startsWith('####') && normalize(line).includes(anahtar)) {
                                foundLineIdx = i;
                                foundBaslik = line;
                                break;
                            }
                        }
                        if (foundLineIdx === -1) {
                            modalBody.innerHTML = 'İçerik bulunamadı. Lütfen ibb_plan_notlari.md dosyanızda başlıkta ilgili anahtar kelimenin geçtiğinden emin olun.';
                            modal.style.display = 'block';
                            return;
                        }
                        let sectionLines = [lines[foundLineIdx]];
                        for (let j = foundLineIdx + 1; j < lines.length; j++) {
                            const line = lines[j];
                            if (/^(#### |### |## |# )/.test(line) && normalize(line) !== normalize(foundBaslik)) {
                                break;
                            }
                            sectionLines.push(line);
                        }
                        const section = sectionLines.join('\n');
                        const md = window.markdownit();
                        modalBody.innerHTML = md.render(section);
                        modal.style.display = 'block';
                    });
                closeBtn.onclick = function() { modal.style.display = 'none'; };
                window.addEventListener('click', function(e) {
                    if (e.target === modal) modal.style.display = 'none';
                });
            }
            const mutlakLink = document.getElementById('mutlak-link');
            if (mutlakLink) {
                mutlakLink.onclick = function(e) {
                    e.preventDefault();
                    openTarimModalForBaslik('Mutlak Tarım Arazisi');
                };
            }
            const ozelLink = document.getElementById('ozel-link');
            if (ozelLink) {
                ozelLink.onclick = function(e) {
                    e.preventDefault();
                    openTarimModalForBaslik('Özel Ürün Arazilerinde');
                };
            }
            const dikiliLink = document.getElementById('dikili-link');
            if (dikiliLink) {
                dikiliLink.onclick = function(e) {
                    e.preventDefault();
                    openTarimModalForBaslik('Dikili Tarım Arazilerinde');
                };
            }
        }, 100);
        
        return `
            <div class="bakici-evi-bilgisi">
                ${bakiciEviBaslik}
                <p>${customMessage}</p>
            </div>
        `;
    },
    
    /**
     * Bilinmeyen format için HTML
     */
    renderUnknownFormat(data) {
        let html = `<p><span class="sonuc-uyari">! Sunucudan beklenmeyen bir yanıt alındı.</span></p>`;
        html += `<p class="debug-message">Veri anahtarları: ${Object.keys(data).join(', ')}</p>`;
        if (data.mesaj) {
            html += `<p>${data.mesaj}</p>`;
        } else if (data.ana_mesaj) {
            html += `<p>${data.ana_mesaj}</p>`;
        }
        return html;
    },
    
    /**
     * Hata durumu için HTML
     */
    renderErrorState(data) {
        return `<p><span class="sonuc-red">✗ Sunucu Tarafında Bir Hata Oluştu: ${data.hata}</span></p>`;
    },
    
    /**
     * Form hatalarını göster
     */
    displayFormError(error, container) {
        console.error('Hata:', error);
        container.innerHTML = `
            <div class="sonuc-container">
                <p class="sonuc-red">Sorgulama sırasında bir hata oluştu: ${error.message}</p>
                <p>Lütfen daha sonra tekrar deneyiniz.</p>
            </div>
        `;
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

// Bu fonksiyonun, fetch().then(data => ...) içinde çağrıldığını varsayalım.
// Örneğin: renderResultsToContainer(data, document.getElementById('sonuc-mesaj'));

function renderResultsToContainer(data, containerElement) {
    if (!containerElement) {
        console.error("Sonuçları gösterecek HTML elementi bulunamadı.");
        return;
    }

    const yapiTuruId = data.yapi_turu_id || data.yapiTurId; // Backend'den gelen yapı türü ID'si

    if (yapiTuruId == 5) { // YALNIZCA Silo (ID 5) ise bu blok çalışır
        const giris = data.giris || {}; // data.giris objesinin varlığını kontrol et
        const araziBuyuklugu = giris.arazi_buyuklugu_m2 || data.arazi_buyuklugu_m2;
        const planlananSiloAlani = giris.planlanan_silo_taban_alani_m2;
        const maksimumToplamHak = data.maksimum_taban_alani;

        // Silo için özel HTML yapısını oluştur
        let siloFullHtml = `
            <div class="silo-bilgileri">
                <h4>Silo Projesi Detaylı Bilgiler</h4>
                <div class="silo-proje-bilgileri p-2 border rounded mb-3">
                    <p><strong>Arazi Büyüklüğü:</strong> ${araziBuyuklugu ? Number(araziBuyuklugu).toFixed(2) : "?"} m²</p>
                    <p><strong>Planlanan Silo Taban Alanı:</strong> ${planlananSiloAlani ? Number(planlananSiloAlani).toFixed(2) : "?"} m²</p>
                </div>
                <div class="highlight-info p-2 border rounded">
                    <p><strong>Maksimum Toplam Yapılaşma Hakkı (%20):</strong> ${maksimumToplamHak ? Number(maksimumToplamHak).toFixed(2) : "?"} m²</p>
                </div>
                <div class="silo-detay-mesaj mt-3" style="white-space:pre-line;">
                    ${data.mesaj || "Detaylı silo raporu bulunamadı."} 
                    {/* Silo sorgusunda data.mesaj, silo'nun detaylı raporunu içerir */}
                </div>
            </div>
        `;
        containerElement.innerHTML = siloFullHtml; // Konteynerin içeriğini silo HTML'i ile tamamen değiştir
    } else {
        // Diğer tüm yapı türleri için (Lisanslı Depo - ID 7 dahil)
        // sadece backend'den gelen ana mesajı göster.
        containerElement.innerHTML = data.mesaj || "Bilgi bulunamadı.";
    }
}

// Eğer form gönderimini ve sonuçların işlenmesini yöneten başka bir ana fonksiyonunuz varsa
// (örneğin form-module.js içinde), o fonksiyonun fetch().then() bloğunda
// yukarıdaki renderResultsToContainer fonksiyonunu çağırdığından emin olun:
//
// Örnek kullanım (form-module.js veya ana script dosyanızda):
/*
fetch('/sorgula-imar-durumu/', { ... })
    .then(response => response.json())
    .then(data => {
        const resultDisplayElement = document.getElementById('sonuc-mesaj'); // Sonuçların gösterileceği div
        if (typeof renderResultsToContainer === 'function') {
            renderResultsToContainer(data, resultDisplayElement);
        } else {
            // Fallback ya da hata durumu
            if (resultDisplayElement) {
                resultDisplayElement.innerHTML = data.mesaj || "Bir sorun oluştu.";
            }
            console.error("renderResultsToContainer fonksiyonu bulunamadı.");
        }
        // Gerekirse sayfayı sonuçlara kaydır:
        // if (typeof scrollToResults === 'function') scrollToResults();
    })
    .catch(error => {
        console.error('Veri alınırken hata oluştu:', error);
        const resultDisplayElement = document.getElementById('sonuc-mesaj');
        if (resultDisplayElement) {
            resultDisplayElement.innerHTML = "<p class='text-danger'>Sonuçlar yüklenirken bir hata oluştu.</p>";
        }
    });
*/
