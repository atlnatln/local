// ========================
// 5. POLİGON KONTROL MODÜLÜ
// ========================

// Bu değişkenler main.js dosyasında global olarak tanımlanacak
// let izmirIcinde = false, isInsideBuyukOva = false, isInsideYasKapaliAlan = false;

const PolygonModule = {
    /**
     * Koordinatın poligonlar içinde olup olmadığını kontrol et
     */
    checkCoordinateInPolygons(lat, lng) {
        const csrftoken = Utils.getCookie('csrftoken');
        
        fetch(CONFIG.endpoints.checkCoordinate, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({lat, lng})
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Sunucu hatası: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log('CHECK-COORDINATE YANITI:', data);
            this.handlePolygonResponse(data, lat, lng);
        })
        .catch(error => {
            console.error('Hata:', error);
        });
    },
    
    /**
     * Poligon yanıtını işle
     */
    handlePolygonResponse(data, lat, lng) {
        const infoSectionElement = Utils.getElement(CONFIG.selectors.infoSection);
        
        izmirIcinde = data.in_izmir;
        isInsideYasKapaliAlan = data.in_yas_kapali_alan || false;
        isInsideBuyukOva = data.inside_polygons && data.inside_polygons.length > 0;
        
        if (izmirIcinde) {
            this.handleInsideIzmir(infoSectionElement);
        } else {
            this.handleOutsideIzmir(infoSectionElement, lat, lng);
        }
        
        console.log('YAS Kapalı Alan içinde mi:', isInsideYasKapaliAlan);
        console.log('Büyük Ova içinde mi:', isInsideBuyukOva);
    },
    
    /**
     * İzmir ili içindeyse yapılacak işlemler
     */
    handleInsideIzmir(infoSectionElement) {
        Utils.setVisibility(infoSectionElement, true);
        
        if (popupMessage) {
            map.closePopup(popupMessage);
            popupMessage = null;
        }
        
        FormModule.updateSuTahsisBelgesiVisibility();
    },
    
    /**
     * İzmir dışındaysa yapılacak işlemler
     */
    handleOutsideIzmir(infoSectionElement, lat, lng) {
        Utils.setVisibility(infoSectionElement, false);
        
        popupMessage = L.popup({
            closeButton: false,
            autoClose: false,
            closeOnEscapeKey: false,
            closeOnClick: false,
            className: 'izmir-disinda-popup'
        })
        .setLatLng([lat, lng])
        .setContent('<div style="color: #d32f2f; font-weight: bold;">İzmir il sınırı dışında sorgulama yapılamamaktadır</div>')
        .openOn(map);
    }
};
