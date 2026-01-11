// Dikili arazi kontrolü için yardımcı fonksiyonlar ve mantık

const DikiliAraziKontrol = {
    // CSS modül gereksinimleri
    requiredCSSModules: ['dikili-arazi', 'common-panels'],

    agacVerileri: [],
    eklenenAgaclar: [],
    manuelEklenenAgaclar: [],
    secilenAlanMetrekare: 0,
    manuelAlanMetrekare: 0,
    cizimModu: false,
    poligon: null,
    poligonLayer: null,
    firstMarker: null,
    ui: {}, // DOM elemanlarını saklamak için

    /**
     * Modülü başlat
     */
    async init() {
        // CSS modüllerini yükle
        try {
            await window.CSSModuleManager.loadModules(this.requiredCSSModules);
            console.log('Dikili Arazi CSS modülleri yüklendi');
        } catch (error) {
            console.warn('CSS modül yükleme hatası:', error);
        }
        
        this.cacheDOMElements(); // DOM elemanlarını önbelleğe al
        this.loadAgacVerileri();
        this.setupEventListeners();
    },

    /**
     * Sık kullanılan DOM elemanlarını önbelleğe al
     */
    cacheDOMElements() {
        this.ui.cizPoligonBtn = document.getElementById('ciz-poligon-btn');
        this.ui.temizlePoligonBtn = document.getElementById('temizle-poligon-btn');
        this.ui.haritaBildirim = document.getElementById('harita-bildirim');
        this.ui.haritaBildirimMesaj = document.getElementById('harita-bildirim-mesaj');
        this.ui.manuelBildirim = document.getElementById('manuel-bildirim');
        this.ui.manuelBildirimMesaj = document.getElementById('manuel-bildirim-mesaj');
        this.ui.secilenAlanBilgisi = document.getElementById('secilen-alan-bilgisi');
        this.ui.secilenAlanMetrekareEl = document.getElementById('secilen-alan-metrekare');
        this.ui.agacBilgileriForm = document.getElementById('agac-bilgileri-form');
        this.ui.dikiliAlanSonuc = document.getElementById('dikili-alan-sonuc');
        this.ui.manuelDikiliAlanSonuc = document.getElementById('manuel-dikili-alan-sonuc');

        this.ui.agacTuruSelect = document.getElementById('agac-turu-select');
        this.ui.agacTipiSelect = document.getElementById('agac-tipi-select');
        this.ui.agacSayisiInput = document.getElementById('agac-sayisi-input');
        this.ui.eklenenAgaclarList = document.getElementById('eklenen-agaclar');
        this.ui.agacEkleBtn = document.getElementById('agac-ekle-btn');
        this.ui.agacHesaplaBtn = document.getElementById('agac-hesapla-btn');
        this.ui.haritaIptalBtn = document.getElementById('harita-iptal-btn');
        this.ui.haritaDevamBtn = document.getElementById('harita-devam-btn');

        this.ui.manuelAlanInput = document.getElementById('manuel-alan-input');
        this.ui.manuelAgacTuruSelect = document.getElementById('manuel-agac-turu-select');
        this.ui.manuelAgacTipiSelect = document.getElementById('manuel-agac-tipi-select');
        this.ui.manuelAgacSayisiInput = document.getElementById('manuel-agac-sayisi-input');
        this.ui.manuelEklenenAgaclarList = document.getElementById('manuel-eklenen-agaclar');
        this.ui.manuelAgacEkleBtn = document.getElementById('manuel-agac-ekle-btn');
        this.ui.manuelHesaplaBtn = document.getElementById('manuel-hesapla-btn');
        this.ui.manuelIptalBtn = document.getElementById('manuel-iptal-btn');
        this.ui.manuelDevamBtn = document.getElementById('manuel-devam-btn');
    },
    
    /**
     * Bildirim göster (alert yerine)
     */
    showNotification(message, type = 'harita', isError = false) {
        const notificationEl = type === 'harita' ? this.ui.haritaBildirim : this.ui.manuelBildirim;
        const messageEl = type === 'harita' ? this.ui.haritaBildirimMesaj : this.ui.manuelBildirimMesaj;
        
        if (!notificationEl || !messageEl) return;
        
        // Bildirim stilini ayarla (hata veya bilgi)
        if (isError) {
            notificationEl.style.backgroundColor = '#f8d7da';
            notificationEl.style.color = '#721c24';
            notificationEl.style.borderLeftColor = '#e74c3c';
        } else {
            notificationEl.style.backgroundColor = '#d4edda';
            notificationEl.style.color = '#155724';
            notificationEl.style.borderLeftColor = type === 'harita' ? '#2ecc71' : '#9b59b6';
        }
        
        // Mesajı ayarla ve bildirimi göster
        messageEl.textContent = message;
        notificationEl.style.display = 'block';
        
        // 5 saniye sonra bildirimi gizle
        setTimeout(() => {
            notificationEl.style.display = 'none';
        }, 5000);
    },
    
    /**
     * Onay bildirimi göster (confirm yerine)
     * @param {string} message - Bildirim mesajı
     * @param {string} title - Bildirim başlığı
     * @param {Function} onConfirm - Onay verildiğinde çalıştırılacak fonksiyon
     * @param {Function} onCancel - İptal edildiğinde çalıştırılacak fonksiyon
     */
    showConfirmation(message, title = 'Onay', onConfirm = null, onCancel = null) {
        // Onay bildirimi için doğrudan confirm kullan
        if (confirm(message)) {
            if (typeof onConfirm === 'function') onConfirm();
        } else {
            if (typeof onCancel === 'function') onCancel();
        }
    },
    
    /**
     * Ağaç verilerini yükle
     */
    loadAgacVerileri() {
        fetch('/static/dikili_arazi_agac_sayilari.md')
            .then(response => response.text())
            .then(markdown => {
                // Markdown tablosunu işle
                const lines = markdown.split('\n');
                const agacVerileri = [];
                
                // Başlık satırını ve ayırıcı satırı atla (ilk 2 satır)
                for (let i = 2; i < lines.length; i++) {
                    const line = lines[i].trim();
                    if (!line) continue;
                    // Tablo satırını ayrıştır
                    const cells = line.split('|').map(cell => cell.trim()); // filter(cell => cell) kaldırıldı
                    if (cells.length >= 6) { // Baş ve son boş hücreler dahil, en az 6 hücre olmalı
                        const agacVeri = {
                            sira: parseInt(cells[1]),
                            tur: cells[2],
                            normal: cells[3] && cells[3] !== '-' ? parseInt(cells[3]) : null,
                            bodur: cells[4] && cells[4] !== '-' ? parseInt(cells[4]) : null,
                            yariBodur: cells[5] && cells[5] !== '-' ? parseInt(cells[5]) : null
                        };
                        agacVerileri.push(agacVeri);
                    }
                }
                
                this.agacVerileri = agacVerileri;
                this.populateAgacTuruDropdowns();
            })
            .catch(error => {
                console.error('Ağaç verileri yüklenirken hata oluştu:', error);
            });
    },
    
    /**
     * Dropdown'ları ağaç türleri ile doldur
     */
    populateAgacTuruDropdowns() {
        const dropdowns = [
            this.ui.agacTuruSelect, // Önbellekten kullan
            this.ui.manuelAgacTuruSelect // Önbellekten kullan
        ];
        // Ağaç türlerini alfabetik sırala
        const sortedAgacVerileri = [...this.agacVerileri].sort((a, b) => a.tur.localeCompare(b.tur, 'tr'));
        dropdowns.forEach(dropdown => {
            if (!dropdown) return;
            // Mevcut seçenekleri temizle (ilk seçenek hariç)
            const firstOption = dropdown.options[0];
            dropdown.innerHTML = '';
            dropdown.appendChild(firstOption);
            // Ağaç türlerini ekle (alfabetik)
            sortedAgacVerileri.forEach(agac => {
                const option = document.createElement('option');
                option.value = agac.sira.toString();
                option.textContent = agac.tur;
                dropdown.appendChild(option);
            });
        });
    },
    
    /**
     * Seçilen ağaç türüne göre tip dropdown'unu güncelle
     */
    updateAgacTipiDropdown(mode = 'harita') {
        const agacTuruSelect = mode === 'manuel' ? this.ui.manuelAgacTuruSelect : this.ui.agacTuruSelect;
        const agacTipiSelect = mode === 'manuel' ? this.ui.manuelAgacTipiSelect : this.ui.agacTipiSelect;
        if (!agacTuruSelect || !agacTipiSelect) return;
        const agacTuruId = agacTuruSelect.value;
        // Seçili türü bul
        const agac = this.agacVerileri.find(a => a.sira.toString() === agacTuruId);
        // Tipleri temizle
        agacTipiSelect.innerHTML = '';
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Ağaç tipi seçin';
        agacTipiSelect.appendChild(defaultOption);
        if (!agac) return;

        let availableTypes = [];
        if (agac.normal !== null) {
            const opt = document.createElement('option');
            opt.value = 'normal';
            opt.textContent = 'Normal';
            agacTipiSelect.appendChild(opt);
            availableTypes.push('normal');
        }
        if (agac.bodur !== null) {
            const opt = document.createElement('option');
            opt.value = 'bodur';
            opt.textContent = 'Bodur';
            agacTipiSelect.appendChild(opt);
            availableTypes.push('bodur');
        }
        if (agac.yariBodur !== null) {
            const opt = document.createElement('option');
            opt.value = 'yaribodur';
            opt.textContent = 'Yarı Bodur';
            agacTipiSelect.appendChild(opt);
            availableTypes.push('yaribodur');
        }

        // Eğer sadece bir ağaç tipi varsa otomatik seç
        if (availableTypes.length === 1) {
            agacTipiSelect.value = availableTypes[0];
        }
    },

    /**
     * Event listener'ları ayarla
     */
    setupEventListeners() {
        // Poligon çizimi butonları
        if (this.ui.cizPoligonBtn) {
            this.ui.cizPoligonBtn.addEventListener('click', () => {
                this.startDrawingPolygon();
            });
        }
        
        if (this.ui.temizlePoligonBtn) {
            this.ui.temizlePoligonBtn.addEventListener('click', () => {
                this.clearPolygon();
            });
        }
        
        // Ağaç ekleme butonları
        if (this.ui.agacEkleBtn) {
            this.ui.agacEkleBtn.addEventListener('click', () => {
                this.addAgac('harita');
            });
        }
        
        if (this.ui.manuelAgacEkleBtn) {
            this.ui.manuelAgacEkleBtn.addEventListener('click', () => {
                this.addAgac('manuel');
            });
        }
        
        // Hesaplama butonları
        if (this.ui.agacHesaplaBtn) {
            this.ui.agacHesaplaBtn.addEventListener('click', () => {
                this.calculateDikiliAlan('harita');
            });
        }
        
        if (this.ui.manuelHesaplaBtn) {
            this.ui.manuelHesaplaBtn.addEventListener('click', () => {
                this.calculateDikiliAlan('manuel');
            });
        }
        
        // İptal ve devam butonları
        if (this.ui.haritaIptalBtn) {
            this.ui.haritaIptalBtn.addEventListener('click', () => {
                this.cancelDikiliKontrol('harita');
            });
        }
        
        if (this.ui.haritaDevamBtn) {
            this.ui.haritaDevamBtn.addEventListener('click', () => {
                this.continueWithQuery();
            });
        }
        
        if (this.ui.manuelIptalBtn) {
            this.ui.manuelIptalBtn.addEventListener('click', () => {
                this.cancelDikiliKontrol('manuel');
            });
        }
        
        if (this.ui.manuelDevamBtn) {
            this.ui.manuelDevamBtn.addEventListener('click', () => {
                this.continueWithQuery();
            });
        }
        
        // Manuel alan input değişiklik olayı
        if (this.ui.manuelAlanInput) {
            this.ui.manuelAlanInput.addEventListener('input', (e) => {
                this.manuelAlanMetrekare = parseFloat(e.target.value) || 0;
            });
        }
        
        // Ağaç türü değişince tip dropdown'unu güncelle
        if (this.ui.agacTuruSelect && this.ui.agacTipiSelect) {
            this.ui.agacTuruSelect.addEventListener('change', () => {
                this.updateAgacTipiDropdown('harita');
            });
        }
        if (this.ui.manuelAgacTuruSelect && this.ui.manuelAgacTipiSelect) {
            this.ui.manuelAgacTuruSelect.addEventListener('change', () => {
                this.updateAgacTipiDropdown('manuel');
            });
        }
    },
    
    /**
     * Poligon çizimini başlat
     */
    startDrawingPolygon() {
        if (this.cizimModu) {
            return;
        }
        
        if (typeof window.map === 'undefined' || !window.map) {
            console.error('Harita bulunamadı');
            this.showNotification('Harita yüklenemedi, lütfen sayfayı yenileyin.', 'harita', true);
            return;
        }
        
        this.clearPolygon(); 
        this.cizimModu = true; 
        
        if (this.ui.cizPoligonBtn) this.ui.cizPoligonBtn.style.display = 'none';
        if (this.ui.temizlePoligonBtn) this.ui.temizlePoligonBtn.style.display = 'inline-block';
        
        this.poligon = [];
        this.poligonLayer = L.layerGroup();

        if (typeof window.map !== 'undefined' && window.map && typeof window.map.addLayer === 'function') {
            window.map.addLayer(this.poligonLayer);
        } else {
            console.error('Harita bulunamadı veya addLayer metodu yok (startDrawingPolygon)');
        }
        
        this.firstMarker = null;
        this.boundHandleMapClick = this.handleMapClick.bind(this);

        if (typeof window.map !== 'undefined' && window.map) {
            window.map.on('click', this.boundHandleMapClick);
            this.boundHandleDblClick = (e) => {
                if (this.cizimModu && this.poligon.length >= 3) {
                    this.completePolygon();
                }
            };
            window.map.on('dblclick', this.boundHandleDblClick);
        } else {
            console.error('Harita bulunamadı (event listeners eklenemiyor)');
        }
        
        // Haritaya yardımcı bilgiler ekle
        const helpMarker = L.marker(window.map.getCenter(), {
            icon: L.divIcon({
                className: 'help-marker',
                html: '<div style="background-color: rgba(52, 152, 219, 0.8); color: white; padding: 10px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">' +
                      '<i class="fas fa-info-circle"></i> Poligon çizmek için haritaya tıklayın</div>',
                iconSize: [220, 40],
                iconAnchor: [110, 20]
            })
        });
        // add to layer group or map
        if (this.poligonLayer && typeof this.poligonLayer.addLayer === 'function') {
            this.poligonLayer.addLayer(helpMarker);
        } else if (typeof window.map !== 'undefined' && window.map) {
            helpMarker.addTo(window.map);
        } else {
            console.error('Yardım işareti eklenemiyor: Katman veya harita bulunamadı');
        }
        
        // 3 saniye sonra yardımcı işareti kaldır
        setTimeout(() => {
            if (this.poligonLayer) {
                this.poligonLayer.removeLayer(helpMarker);
            }
        }, 3000);
        
        // Kullanıcıya detaylı bilgi ver
        this.showNotification('Harita üzerinde dikili alanınızın köşe noktalarını tıklayarak bir poligon çizin. Çizimi tamamlamak için ilk noktaya yakın bir yere tıklayın veya çift tıklayın. En az 3 nokta gereklidir.', 'harita', false);
    },
    
    /**
     * Harita tıklamasını işle
     */
    handleMapClick(e) {
        if (!this.cizimModu) {
            return;
        }
        
        L.DomEvent.stopPropagation(e);

        const lat = e.latlng.lat;
        const lng = e.latlng.lng;
        
        this.poligon.push([lat, lng]);
        
        const marker = L.marker([lat, lng], {
            pane: 'markerPane',
            icon: L.divIcon({
                className: 'polygon-marker',
                html: `<div style="background-color: #e74c3c; width: 12px; height: 12px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 5px rgba(0,0,0,0.5); position: relative; z-index: 1000;"></div>`,
                iconSize: [18, 18],
                iconAnchor: [9, 9]
            })
        });
        
        if (this.poligonLayer && typeof this.poligonLayer.addLayer === 'function') {
            this.poligonLayer.addLayer(marker);
        } else if (typeof window.map !== 'undefined' && window.map) {
            marker.addTo(window.map);
            console.warn("DikiliAraziKontrol: Marker doğrudan haritaya eklendi (poligonLayer bulunamadı).");
        } else {
            console.error('Marker eklenemiyor: Katman veya harita bulunamadı');
        }
        
        // İlk marker ise, kapatma tıklaması için sakla ve click listener ekle
        if (this.poligon.length === 1) {
            this.firstMarker = marker;
            marker.on('click', () => {
                if (this.poligon.length >= 3) {
                    this.completePolygon();
                }
            });
        }
        
        // Kullanıcıya geri bildirim ver
        if (this.poligon.length === 1) {
            this.showNotification('İlk köşe noktası eklendi. Daha fazla nokta ekleyin.', 'harita', false);
        } else if (this.poligon.length === 2) {
            this.showNotification('İkinci köşe noktası eklendi. En az bir nokta daha eklemeniz gerekmektedir.', 'harita', false);
        } else if (this.poligon.length === 3) {
            this.showNotification('Poligonu tamamlamak için ilk noktaya yakın bir yere tıklayın veya çift tıklayın.', 'harita', false);
        }
        
        // Eğer en az 2 nokta varsa, çizgi çiz
        if (this.poligon.length >= 2) {
            const lastIndex = this.poligon.length - 1;
            
            const line = L.polyline([
                this.poligon[lastIndex - 1],
                this.poligon[lastIndex]
            ], {
                color: '#e74c3c',
                weight: 4,
                opacity: 1,
                pane: 'markerPane'
            });
            
            if (this.poligonLayer && typeof this.poligonLayer.addLayer === 'function') {
                this.poligonLayer.addLayer(line);
            } else if (typeof window.map !== 'undefined' && window.map) {
                line.addTo(window.map);
                console.warn("DikiliAraziKontrol: Çizgi doğrudan haritaya eklendi (poligonLayer bulunamadı).");
            } else {
                console.error('Çizgi eklenemiyor: Katman veya harita bulunamadı');
            }
        }
        
        if (this.poligon.length >= 3) {
            const firstPoint = this.poligon[0];
            const lastPoint = this.poligon[this.poligon.length - 1];
            
            const distance = window.map.distance(
                [firstPoint[0], firstPoint[1]],
                [lastPoint[0], lastPoint[1]]
            );
            
            // console.log(`İlk ve son nokta arasındaki mesafe: ${distance} metre`); // İsteğe bağlı tutulabilir
            
            if (distance < 50) {
                this.completePolygon();
            }
        }
        
        if (e.originalEvent && e.originalEvent.detail === 2 && this.poligon.length >= 3) {
            this.completePolygon();
        }
    },
    
    /**
     * Poligonu tamamla
     */
    completePolygon() {
        // console.log("DikiliAraziKontrol.completePolygon çağrıldı. cizimModu:", this.cizimModu, "Poligon nokta sayısı:", this.poligon.length); // Kaldırıldı
        if (!this.cizimModu || this.poligon.length < 3) {
            // console.log("Poligon tamamlanamıyor: Çizim modu kapalı veya yeterli nokta yok"); // Kaldırıldı
            if (this.poligon.length < 3) {
                this.showNotification('Poligon tamamlamak için en az 3 nokta gereklidir.', 'harita', true);
            }
            return;
        }
        
        // console.log("Poligon tamamlanıyor...", this.poligon); // Kaldırıldı
        
        const firstPoint = this.poligon[0];
        const lastPoint = this.poligon[this.poligon.length - 1];
        
        const closingLine = L.polyline([lastPoint, firstPoint], {
            pane: 'markerPane',
            color: '#2ecc71',
            weight: 5,
            opacity: 1,
        });
        if (this.poligonLayer && typeof this.poligonLayer.addLayer === 'function') {
            this.poligonLayer.addLayer(closingLine);
            // console.log("DikiliAraziKontrol: Kapanış çizgisi poligonLayer'a eklendi."); // Kaldırıldı
        } else if (typeof window.map !== 'undefined' && window.map) {
            closingLine.addTo(window.map);
            console.warn("DikiliAraziKontrol: Kapanış çizgisi doğrudan haritaya eklendi (poligonLayer bulunamadı).");
        } else {
            console.error('Kapanış çizgisi eklenemiyor: Katman veya harita bulunamadı');
        }
        
        const polygonLayerObject = L.polygon(this.poligon, {
            pane: 'overlayPane',
            color: '#3498db',
            weight: 4,
            fillColor: '#3498db',
            fillOpacity: 0.3,
        });
        if (this.poligonLayer && typeof this.poligonLayer.addLayer === 'function') {
            this.poligonLayer.addLayer(polygonLayerObject);
            // console.log("DikiliAraziKontrol: Poligon nesnesi poligonLayer'a eklendi."); // Kaldırıldı
        } else if (typeof window.map !== 'undefined' && window.map) {
            polygonLayerObject.addTo(window.map);
            console.warn("DikiliAraziKontrol: Poligon nesnesi doğrudan haritaya eklendi (poligonLayer bulunamadı).");
        } else {
            console.error('Poligon katmanı eklenemiyor: Katman veya harita bulunamadı');
        }
        
        // Poligonun merkezine bir bilgi işareti ekle
        const bounds = polygonLayerObject.getBounds();
        const center = bounds.getCenter();
        
        const infoMarker = L.marker(center, {
            icon: L.divIcon({
                className: 'area-info-marker',
                html: '<i class="fas fa-info-circle" style="color: #3498db; font-size: 24px; text-shadow: 1px 1px 3px rgba(0,0,0,0.5);"></i>',
                iconSize: [24, 24],
                iconAnchor: [12, 12]
            })
        });
        
        if (this.poligonLayer && typeof this.poligonLayer.addLayer === 'function') {
            this.poligonLayer.addLayer(infoMarker);
        } else if (typeof window.map !== 'undefined' && window.map) {
            infoMarker.addTo(window.map);
        } else {
            console.error('Bilgi işareti eklenemiyor: Katman veya harita bulunamadı');
        }
        
        // Çizim modunu kapat
        // Çizim olaylarını kapat
        if (typeof window.map !== 'undefined' && window.map) {
            if (this.boundHandleMapClick) {
                window.map.off('click', this.boundHandleMapClick);
            }
            if (this.boundHandleDblClick) {
                window.map.off('dblclick', this.boundHandleDblClick);
            }
        } else {
            console.error('Event listener\'lar kaldırılamıyor: Harita bulunamadı');
        }
        
        // Başarılı bildirim
        this.showNotification('Poligon çizimi tamamlandı! Alan hesaplanıyor...', 'harita', false);
        
        // Alan hesapla (metrekare cinsinden)
        const areaSqMeters = this.calculatePolygonArea(this.poligon);
        this.secilenAlanMetrekare = areaSqMeters;
        
        if (this.ui.secilenAlanBilgisi) this.ui.secilenAlanBilgisi.style.display = 'block';
        if (this.ui.secilenAlanMetrekareEl) this.ui.secilenAlanMetrekareEl.textContent = Math.round(areaSqMeters).toLocaleString();
        
        if (this.ui.agacBilgileriForm) this.ui.agacBilgileriForm.style.display = 'block';
        
        // Poligon çiz butonunu GİZLE çünkü çizim tamamlandı
        if (this.ui.cizPoligonBtn) this.ui.cizPoligonBtn.style.display = 'none';
        if (this.ui.temizlePoligonBtn) this.ui.temizlePoligonBtn.style.display = 'inline-block';
        
        // 5000 m² altındaysa uyarı ver
        if (areaSqMeters < 5000) {
            if (this.ui.dikiliAlanSonuc) {
                this.ui.dikiliAlanSonuc.innerHTML = `
                    <div style="background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px;">
                        <h4 style="margin-top: 0;">Yetersiz Alan</h4>
                        <p>Seçtiğiniz alanın büyüklüğü <strong>${Math.round(areaSqMeters).toLocaleString()} m²</strong> olarak hesaplandı.</p>
                        <p>Dikili tarım arazilerinde bağ evi yapılabilmesi için arazi büyüklüğünün en az <strong>0,5 hektar (5000 m²)</strong> olması gerekmektedir.</p>
                    </div>
                `;
                this.ui.dikiliAlanSonuc.style.display = 'block';
            }
        }
    },
    
    /**
     * Poligon alanını hesapla (yaklaşık, metrekare cinsinden)
     */
    calculatePolygonArea(vertices) {
        // Haversine formülü kullanarak iki nokta arasındaki mesafeyi hesapla
        function haversineDistance(lat1, lon1, lat2, lon2) {
            const R = 6371000; // Earth radius in meters
            const dLat = (lat2 - lat1) * Math.PI / 180;
            const dLon = (lon2 - lon1) * Math.PI / 180;
            const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                    Math.sin(dLon/2) * Math.sin(dLon/2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
            return R * c;
        }

        // Shoelace formülü ile düzlemsel alan hesapla
        let area = 0;
        for (let i = 0; i < vertices.length; i++) {
            const j = (i + 1) % vertices.length;
            
            // İki noktanın koordinatları
            const lat1 = vertices[i][0];
            const lon1 = vertices[i][1];
            const lat2 = vertices[j][0];
            const lon2 = vertices[j][1];
            
            // Alan hesabının bir parçası
            area += lat1 * lon2 - lat2 * lon1;
        }
        area = Math.abs(area) / 2;
        
        // Alanı derece kareden metrekareye dönüştür (yaklaşık)
        // Bu hesaplama yaklaşıktır, daha doğru ölçümler için özel kütüphaneler kullanılmalıdır
        // Yaklaşık olarak 1 derece = 111000 metre
        const scaleFactor = 111000 * 111000; // Yaklaşık
        return area * scaleFactor;
    },
    
    /**
     * Çizilen poligonu temizle
     */
    clearPolygon() {
        // console.log("DikiliAraziKontrol.clearPolygon çağrıldı."); // Kaldırıldı
        if (this.poligonLayer) {
            if (typeof window.map !== 'undefined' && window.map && typeof window.map.removeLayer === 'function') {
                if (window.map.hasLayer(this.poligonLayer)) {
                    window.map.removeLayer(this.poligonLayer);
                    // console.log("DikiliAraziKontrol: poligonLayer haritadan kaldırıldı."); // Kaldırıldı
                } else {
                    // console.warn("DikiliAraziKontrol: poligonLayer haritada bulunamadı (kaldırma işlemi atlandı)."); 
                }
            } else {
                console.error('Harita bulunamadı veya removeLayer metodu yok (clearPolygon)');
            }
            this.poligonLayer = null;
        }
        
        this.poligon = [];
        this.cizimModu = false;
        
        if (typeof window.map !== 'undefined' && window.map) {
            if (this.boundHandleMapClick) {
                window.map.off('click', this.boundHandleMapClick);
            }
            if (this.boundHandleDblClick) {
                window.map.off('dblclick', this.boundHandleDblClick);
            }
        } else {
            console.error('Event listener\'lar kaldırılamıyor: Harita bulunamadı');
        }
        
        if (this.ui.cizPoligonBtn) this.ui.cizPoligonBtn.style.display = 'inline-block';
        if (this.ui.temizlePoligonBtn) this.ui.temizlePoligonBtn.style.display = 'none';
        
        if (this.ui.secilenAlanBilgisi) this.ui.secilenAlanBilgisi.style.display = 'none';
        if (this.ui.agacBilgileriForm) this.ui.agacBilgileriForm.style.display = 'none';
        if (this.ui.dikiliAlanSonuc) this.ui.dikiliAlanSonuc.style.display = 'none';
        
        this.eklenenAgaclar = [];
        this.updateAgacListesi('harita');
    },
    
    /**
     * Ağaç ekle 
     */
    addAgac(mode) {
        const prefix = mode === 'manuel' ? 'manuel-' : '';
        const agacTuruSelect = mode === 'manuel' ? this.ui.manuelAgacTuruSelect : this.ui.agacTuruSelect;
        const agacTipiSelect = mode === 'manuel' ? this.ui.manuelAgacTipiSelect : this.ui.agacTipiSelect;
        const agacSayisiInput = mode === 'manuel' ? this.ui.manuelAgacSayisiInput : this.ui.agacSayisiInput;
        
        if (!agacTuruSelect || !agacTipiSelect || !agacSayisiInput) return;
        
        // Değerleri al
        const agacTuruId = agacTuruSelect.value;
        const agacTipi = agacTipiSelect.value;
        const agacSayisi = parseInt(agacSayisiInput.value);
        
        // Geçerlilik kontrolü
        if (!agacTuruId) {
            this.showNotification('Lütfen bir ağaç türü seçin', mode, true);
            return;
        }
        
        if (!agacTipi) { // Ağaç tipi seçilmemişse (boş değer)
            this.showNotification('Lütfen bir ağaç tipi seçin', mode, true);
            return;
        }
        
        if (isNaN(agacSayisi) || agacSayisi <= 0) {
            this.showNotification('Lütfen geçerli bir ağaç sayısı girin', mode, true);
            return;
        }
        
        // Ağaç türü adını bul
        const agacTuru = this.agacVerileri.find(agac => agac.sira.toString() === agacTuruId);
        if (!agacTuru) return;
        
        // Yeni ağaç ekle
        const yeniAgac = {
            turid: agacTuruId,
            turAdi: agacTuru.tur,
            tipi: agacTipi,
            sayi: agacSayisi,
            gerekliAgacSayisi: this.getGerekliAgacSayisi(agacTuru, agacTipi)
        };
        
        // İlgili diziye ekle
        if (mode === 'manuel') {
            this.manuelEklenenAgaclar.push(yeniAgac);
        } else {
            this.eklenenAgaclar.push(yeniAgac);
        }
        
        // Formu sıfırla
        agacSayisiInput.value = '';
        
        // Ağaç listesini güncelle
        this.updateAgacListesi(mode);
    },
    
    /**
     * Ağaç türü ve tipine göre gerekli ağaç sayısını al
     */
    getGerekliAgacSayisi(agacTuru, tip) {
        if (!agacTuru) return null;
        
        switch (tip) {
            case 'normal':
                return agacTuru.normal;
            case 'bodur':
                return agacTuru.bodur;
            case 'yaribodur':
                return agacTuru.yariBodur;
            default:
                return null;
        }
    },
    
    /**
     * Ağaç listesini güncelle
     */
    updateAgacListesi(mode) {
        const agaclar = mode === 'manuel' ? this.manuelEklenenAgaclar : this.eklenenAgaclar;
        const listElement = mode === 'manuel' ? this.ui.manuelEklenenAgaclarList : this.ui.eklenenAgaclarList;
        
        if (!listElement) return;
        
        if (agaclar.length === 0) {
            listElement.innerHTML = '<p>Henüz ağaç eklemediniz.</p>';
            return;
        }
        
        // Liste HTML'i oluştur - Template literal kullanımı
        let html = '<ul style="list-style-type: none; padding: 0;">';
        const tipGosterim = {
            'normal': 'Normal',
            'bodur': 'Bodur',
            'yaribodur': 'Yarı Bodur'
        };

        agaclar.forEach((agac, index) => {
            html += `
                <li style="display: flex; justify-content: space-between; margin-bottom: 5px; padding: 5px; border-bottom: 1px solid #eee;">
                    <span><strong>${agac.turAdi}</strong> (${tipGosterim[agac.tipi] || agac.tipi}) - ${agac.sayi} adet</span>
                    <button 
                        class="btn-remove" 
                        style="background: none; border: none; color: #e74c3c; cursor: pointer;"
                        onclick="DikiliAraziKontrol.removeAgac(${index}, '${mode}')">
                        <i class="fas fa-times"></i>
                    </button>
                </li>
            `;
        });
        
        html += '</ul>';
        listElement.innerHTML = html;
    },
    
    /**
     * Ağacı kaldır
     */
    removeAgac(index, mode) {
        if (mode === 'manuel') {
            if (index >= 0 && index < this.manuelEklenenAgaclar.length) {
                this.manuelEklenenAgaclar.splice(index, 1);
                this.updateAgacListesi('manuel');
            }
        } else {
            if (index >= 0 && index < this.eklenenAgaclar.length) {
                this.eklenenAgaclar.splice(index, 1);
                this.updateAgacListesi('harita');
            }
        }
    },
    
    /**
     * Dikili alanı hesapla
     */
    calculateDikiliAlan(mode) {
        const agaclar = mode === 'manuel' ? this.manuelEklenenAgaclar : this.eklenenAgaclar;
        const sonucElement = mode === 'manuel' ? this.ui.manuelDikiliAlanSonuc : this.ui.dikiliAlanSonuc;
        const devamBtn = mode === 'manuel' ? this.ui.manuelDevamBtn : this.ui.haritaDevamBtn;
        
        if (!sonucElement || !devamBtn) return;
        
        // Ağaç listesi boşsa uyarı ver
        if (agaclar.length === 0) {
            this.showNotification('Lütfen önce ağaç ekleyin', mode, true);
            return;
        }
        
        // Manuel mod için alan kontrolü
        if (mode === 'manuel') {
            if (this.manuelAlanMetrekare <= 0) {
                this.showNotification('Lütfen geçerli bir alan büyüklüğü girin', mode, true);
                return;
            }
            
            // 5000 m² altındaysa uyarı ver ve işlemi bitir
            if (this.manuelAlanMetrekare < 5000) {
                sonucElement.innerHTML = `
                    <div style="background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px;">
                        <h4 style="margin-top: 0;">Yetersiz Alan</h4>
                        <p>Girdiğiniz alan büyüklüğü <strong>${Math.round(this.manuelAlanMetrekare).toLocaleString()} m²</strong> olarak hesaplanmıştır.</p>
                        <p>Dikili tarım arazilerinde bağ evi yapılabilmesi için arazi büyüklüğünün en az <strong>0,5 hektar (5000 m²)</strong> olması gerekmektedir.</p>
                    </div>
                `;
                sonucElement.style.display = 'block';
                return;
            }
        } else {
            // Harita modu için alan hesaplanmamışsa uyarı ver
            if (this.secilenAlanMetrekare <= 0) {
                this.showNotification('Lütfen önce haritadan alan seçin', mode, true);
                return;
            }
            
            // 5000 m² altındaysa, zaten uyarı verilmiştir
            if (this.secilenAlanMetrekare < 5000) return;
        }
        
        // Arazi büyüklüğü
        const araziBuyuklugu = mode === 'manuel' ? this.manuelAlanMetrekare : this.secilenAlanMetrekare;
        
        // Her bin metrekare başına düşen ağaç sayısını hesapla
        let toplamAlan = 0; // Ağaçların kapladığı toplam alan (m²)
        let yetersizAgacTurleri = [];
        
        agaclar.forEach(agac => {
            if (agac.gerekliAgacSayisi === null) return;
            
            // 1000 m² (1 dekar) başına düşen gerekli ağaç sayısı
            const binMetrekareBasinaGerekli = agac.gerekliAgacSayisi;
            
            // Ağaçların dikili kabul edilmesi için gereken toplam ağaç sayısı
            const toplamGerekliAgacSayisi = Math.ceil(araziBuyuklugu / 1000 * binMetrekareBasinaGerekli);
            
            // Kullanıcının girdiği ağaç sayısı
            const girilenAgacSayisi = agac.sayi;
            
            // Kontrolü geç
            if (girilenAgacSayisi < toplamGerekliAgacSayisi) {
                yetersizAgacTurleri.push({
                    turAdi: agac.turAdi,
                    girilenSayi: girilenAgacSayisi,
                    gerekliSayi: toplamGerekliAgacSayisi
                });
            }
            
            // Ağaçların kapladığı alanı hesapla (m²)
            const agacAlan = girilenAgacSayisi / binMetrekareBasinaGerekli * 1000;
            toplamAlan += agacAlan;
        });
        
        // Sonucu oluştur
        let html = '';
        
        if (yetersizAgacTurleri.length > 0) {
            // Ağaç sayısı yetersiz
            html = `
                <div style="background-color: #fff3cd; color: #856404; padding: 15px; border-radius: 5px;">
                    <h4 style="margin-top: 0;">Fiili Dikili Alan Şartı Karşılanmıyor</h4>
                    <p>Girdiğiniz ağaç sayıları, bu alanın fiili olarak dikili kabul edilmesi için yeterli değildir.</p>
                    <p>Aşağıdaki ağaç türleri için beklenen minimum sayılara ulaşılmamıştır:</p>
                    <ul>
            `;
            
            yetersizAgacTurleri.forEach(tur => {
                html += `<li><strong>${tur.turAdi}</strong>: ${tur.girilenSayi} adet (gerekli: ${tur.gerekliSayi} adet)</li>`;
            });
            
            html += `
                    </ul>
                    <p style="margin-top: 15px;">Bu alan için tapu vasfı "dikili" olsa da, fiili kullanım olarak dikili kabul edilebilmesi için yeterli ağaç bulunmamaktadır.</p>
                    <p>Kanunda belirtildiği üzere: <em>"Dikili veya örtü altı tarım arazisinin öncelikle tapudaki vasfının farklı olması durumunda hâlihazır kullanımı tespit edilir."</em></p>
                </div>
            `;
        } else if (toplamAlan < araziBuyuklugu * 0.7) {
            // Ağaç sayısı yeterli ama toplam alan arazinin %70'inden az
            html = `
                <div style="background-color: #fff3cd; color: #856404; padding: 15px; border-radius: 5px;">
                    <h4 style="margin-top: 0;">Yetersiz Dikili Alan Oranı</h4>
                    <p>Girdiğiniz ağaçların kapladığı alan, toplam arazinin %70'inden az olduğu için fiili olarak dikili kabul edilemez.</p>
                    <p>Ağaçların tahmini kapladığı alan: ${Math.round(toplamAlan).toLocaleString()} m² (Toplam alanın %${Math.round(toplamAlan/araziBuyuklugu*100)}'si)</p>
                    <p>Kanunda belirtildiği üzere: <em>"Dikili veya örtü altı tarım arazisinin öncelikle tapudaki vasfının farklı olması durumunda hâlihazır kullanımı tespit edilir."</em></p>
                </div>
            `;
        } else {
            // Şartları karşılıyor
            html = `
                <div style="background-color: #d4edda; color: #155724; padding: 15px; border-radius: 5px;">
                    <h4 style="margin-top: 0;">Fiili Dikili Alan Şartı Karşılanıyor</h4>
                    <p>Girdiğiniz ağaç sayıları ve alan büyüklüğü, bu arazinin fiili olarak dikili kabul edilmesi için yeterlidir.</p>
                    <p>Ağaçların tahmini kapladığı alan: ${Math.round(toplamAlan).toLocaleString()} m² (Toplam alanın %${Math.round(toplamAlan/araziBuyuklugu*100)}'si)</p>
                    <p>Dikili tarım arazilerinde bağ evi yapılabilmesi için gereken minimum 5000 m² şartı da sağlanmaktadır.</p>
                    <p>İmar durumu sorgulamasına devam edebilirsiniz.</p>
                </div>
            `;
            
            // Devam butonunu göster
            devamBtn.style.display = 'inline-block';
        }
        
        sonucElement.innerHTML = html;
        sonucElement.style.display = 'block';
    },
    
    /**
     * Tüm formu ve çizimleri sıfırla
     */
    resetAll() {
        // Dikili arazi kontrol panellerini gizle
        const paneller = [
            'dikili-arazi-kontrol-panel',
            'harita-secim-panel',
            'manuel-agac-panel'
        ];
        
        paneller.forEach(id => {
            const panel = document.getElementById(id);
            if (panel) panel.style.display = 'none';
        });
        
        // Harita temizliği
        this.clearPolygon();
        
        // Manuel ağaç verilerini temizle
        this.manuelEklenenAgaclar = [];
        this.manuelAlanMetrekare = 0;
        if (this.ui.manuelAlanInput) {
            this.ui.manuelAlanInput.value = '';
        }
        this.updateAgacListesi('manuel');
        
        // Ağaç verilerini temizle
        this.eklenenAgaclar = [];
        this.secilenAlanMetrekare = 0;
        this.updateAgacListesi('harita');
        
        // Sonuç bölümlerini gizle
        if (this.ui.dikiliAlanSonuc) this.ui.dikiliAlanSonuc.style.display = 'none';
        if (this.ui.manuelDikiliAlanSonuc) this.ui.manuelDikiliAlanSonuc.style.display = 'none';
        
        // Devam butonlarını gizle
        if (this.ui.haritaDevamBtn) this.ui.haritaDevamBtn.style.display = 'none';
        if (this.ui.manuelDevamBtn) this.ui.manuelDevamBtn.style.display = 'none';
        
        // Form alanlarını sıfırla
        const form = document.getElementById('imar-durumu-form');
        if (form) form.reset();
        
        // Tapu vasfı değişim olayını tetikle
        const tapuVasfiSelect = document.getElementById('id_tapu_vasfi');
        if (tapuVasfiSelect) {
            const event = new Event('change');
            tapuVasfiSelect.dispatchEvent(event);
        }
        
        // Sonuçlar bölümünü temizle
        const sonuclarDiv = document.getElementById('sonuclar');
        if (sonuclarDiv) {
            sonuclarDiv.innerHTML = '';
            sonuclarDiv.style.display = 'none';
        }
        
        // Dikili arazi kontrolü bayrağını sıfırla
        window.dikiliAraziKontrolGecildi = false;
        
        // Sayfayı yukarı kaydır
        window.scrollTo(0, 0);
    },
    
    /**
     * İptal - Ana dikili arazi kontrol paneline geri dön
     */
    cancelDikiliKontrol(mode) {
        // Geçerli paneli gizle
        const activePanel = mode === 'manuel' ? 'manuel-agac-panel' : 'harita-secim-panel';
        const panel = document.getElementById(activePanel);
        if (panel) panel.style.display = 'none';
        
        // Ana dikili arazi kontrol panelini göster
        const anaPanel = document.getElementById('dikili-arazi-kontrol-panel');
        if (anaPanel) anaPanel.style.display = 'block';
        
        // Eğer harita modunda ise çizimleri temizle
        if (mode !== 'manuel') {
            this.clearPolygon();
        }
    },
    
    /**
     * Sorgulamaya devam et - Dikili arazi kontrolü tamamlandı
     */
    continueWithQuery() {
        // Global bayrak - dikili arazi kontrolü başarıyla tamamlandı
        window.dikiliAraziKontrolGecildi = true;
        
        // Dikili arazi kontrol panellerini gizle
        const paneller = [
            'dikili-arazi-kontrol-panel',
            'harita-secim-panel',
            'manuel-agac-panel'
        ];
        
        paneller.forEach(id => {
            const panel = document.getElementById(id);
            if (panel) panel.style.display = 'none';
        });
        
        // Form gönderim butonunu etkinleştir ve göster
        const submitButton = document.querySelector(CONFIG.selectors.form.submitButton);
        if (submitButton) {
            submitButton.disabled = false;
            const buttonGroup = submitButton.closest('.button-group');
            if (buttonGroup) buttonGroup.style.display = 'block';
        }
        
        // Alternatif: Form'u otomatik olarak submit etmek için
        // const form = document.getElementById('imar-durumu-form');
        // if (form && submitButton) submitButton.click();
    },
};

// Hazır olduğunda modülü başlat
document.addEventListener('DOMContentLoaded', () => {
    DikiliAraziKontrol.init();
});

// Dikili arazi kontrolü ile ilgili global fonksiyonlar
window.devamEtSorgulamaSiz = function() {
    // Dikili arazi kontrol panelini gizle
    const panel = document.getElementById('dikili-arazi-kontrol-panel');
    if (panel) panel.style.display = 'none';
    
    // Form gönderim butonunu etkinleştir ve göster
    const submitButton = document.querySelector(CONFIG.selectors.form.submitButton);
    if (submitButton) {
        submitButton.disabled = false;
        const buttonGroup = submitButton.closest('.button-group');
        if (buttonGroup) buttonGroup.style.display = 'block';
    }
    
    // Dikili arazi kontrolünü başarıyla geçtik bilgisini form gönderiminde kullanılmak üzere sakla
    window.dikiliAraziKontrolGecildi = true;
    
    // Formu otomatik olarak gönder
    const form = document.getElementById('imar-durumu-form');
    if (form) {
        // Form alanları doldurulmuşsa devam et
        const tapuVasfi = document.querySelector('#id_tapu_vasfi');
        const araziBuyuklugu = document.querySelector('#id_arazi_buyuklugu'); // Düzeltildi: id_yapi_turu yerine id_arazi_buyuklugu
        const yapiTuru = document.querySelector('#id_yapi_turu');
        
        if (tapuVasfi && tapuVasfi.value && 
            araziBuyuklugu && araziBuyuklugu.value && 
            yapiTuru && yapiTuru.value) {
            // Yükleniyor göstergesini göster
            const loadingIndicator = document.getElementById('loading-indicator');
            if (loadingIndicator) loadingIndicator.style.display = 'block';
            
            // 30 saniye sonra yükleme göstergesini otomatik kapat (güvenlik önlemi)
            setTimeout(() => {
                if (loadingIndicator) loadingIndicator.style.display = 'none';
            }, 30000);
            
            // Submit butonuna tıklama
            submitButton.click();
        }
    }
};

window.haritadanAlanSec = function() {
    // Dikili arazi kontrol panelini gizle
    const anaPanel = document.getElementById('dikili-arazi-kontrol-panel');
    if (anaPanel) anaPanel.style.display = 'none';
    
    // Harita seçim panelini göster
    const haritaPanel = document.getElementById('harita-secim-panel');
    if (haritaPanel) haritaPanel.style.display = 'block';
};

window.elIleAgacGir = function() {
    // Dikili arazi kontrol panelini gizle
    const anaPanel = document.getElementById('dikili-arazi-kontrol-panel');
    if (anaPanel) anaPanel.style.display = 'none';
    
    // Manuel ağaç giriş panelini göster
    const manuelPanel = document.getElementById('manuel-agac-panel');
    if (manuelPanel) manuelPanel.style.display = 'block';
};
