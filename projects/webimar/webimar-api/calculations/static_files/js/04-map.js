// ========================
// 4. HARİTA MODÜLÜ 
// ========================

// Bu değişkenler main.js dosyasında global olarak tanımlanacak
// let map, marker, popupMessage; 
// let secilenLat = null, secilenLng = null;

const MapModule = {
    /**
     * Harita başlatma
     */
    init() {
        // Harita konteynerini doğrudan ID ile seç, CSS seçici (#) kullanma
        window.map = L.map('map').setView(CONFIG.map.center, CONFIG.map.zoom);
        
        // Uydu görüntüsü ekle
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
            maxZoom: CONFIG.map.maxZoom
        }).addTo(window.map);
        
        // KML katmanlarını yükle
        this.loadKmlLayers();
        
        // Harita tıklama olayı
        window.map.on('click', function(e) {
            secilenLat = e.latlng.lat;
            secilenLng = e.latlng.lng;
            
            MapModule.clearExistingMarker();
            MapModule.addNewMarker(secilenLat, secilenLng);
            
            // Koordinat kontrolü yap
            PolygonModule.checkCoordinateInPolygons(secilenLat, secilenLng);
        });
    },
    
    /**
     * KML katmanlarını yükle
     */
    loadKmlLayers() {
        omnivore.kml(KML_IZMIR_URL)
            .on('ready', function() {
                this.setStyle({color: '#006600', weight: 3, fillOpacity: 0.05});
                window.map.fitBounds(this.getBounds());
            }).addTo(window.map);
        
        omnivore.kml(KML_IZMIR_KAPALI_ALAN_URL)
            .on('ready', function() {
                this.setStyle({color: 'red', weight: 0, fillOpacity: 0, fillColor: 'red'});
            }).addTo(window.map);
        
        omnivore.kml(KML_BUYUK_OVALAR_IZMIR_URL)
            .on('ready', function() {
                this.setStyle({color: 'blue', weight: 0, fillOpacity: 0.0});
            }).addTo(window.map);
    },
    
    /**
     * İşaretçiyi temizle
     */
    clearExistingMarker() {
        if (marker) {
            window.map.removeLayer(marker);
        }
        
        if (popupMessage) {
            window.map.closePopup(popupMessage);
            popupMessage = null;
        }
    },
    
    /**
     * Yeni işaretçi ekle
     */
    addNewMarker(lat, lng) {
        marker = L.marker([lat, lng]).addTo(window.map);
    }
};
