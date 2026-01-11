// ========================
// 8. İÇERİK MODÜLÜ
// ========================
const ContentModule = {
    /**
     * Büyük Ova uyarı HTML'ini oluştur
     */
    getBuyukOvaUyariHtml() {
        // Bu fonksiyon doğrudan HTML döndürdüğü için, onclick içindeki fonksiyon çağrısı
        // global scope'ta ContentModule.toggleBuyukOvaDetay şeklinde olmalı.
        // index.html'de bu fonksiyonlar window objesine atanmıştı.
        return `
            <div class="buyuk-ova-uyari">
                <div class="buyuk-ova-uyari-baslik">⚠️ Büyük Ova Sınırları İçerisinde</div>
                <div class="panel-content buyuk-ova-uyari-icerik">
                    Seçtiğiniz alan Büyük Ova sınırları içerisinde kalmaktadır. Bu bölgedeki tarım arazilerinde yapılaşma izni 
                    <span class="buyuk-ova-link" onclick="ContentModule.toggleBuyukOvaDetay()">Madde 14</span> 
                    kapsamında değerlendirilir ve işlemlerin tamamlanması daha uzun zaman alabilir.
                </div>
            </div>
            <div id="buyuk-ova-detay" class="buyuk-ova-detay" style="display:none;">
                <div id="markdown-content">Yükleniyor...</div>
            </div>
        `;
    },
    
    /**
     * Büyük ova detaylarını aç/kapat ve ilgili içeriği yükle
     */
    toggleBuyukOvaDetay() {
        const detay = Utils.getElement(CONFIG.selectors.buyukOvaUyari).querySelector('#buyuk-ova-detay'); // Daha spesifik seçici
        if (!detay) {
            console.error("Büyük ova detay elementi bulunamadı.");
            return;
        }
        const isVisible = detay.style.display === 'block';
        Utils.setVisibility(detay, !isVisible);
        
        if (!isVisible) {
            this.loadBuyukOvalarContent();
        }
    },
    
    /**
     * 5403 Sayılı Kanun'dan Büyük Ovalar bölümünü yükle
     */
    loadBuyukOvalarContent() {
        const markdownDiv = Utils.getElement(CONFIG.selectors.markdownContent);
        if (!markdownDiv) {
            console.error("Markdown content elementi bulunamadı.");
            return;
        }
        
        if (markdownDiv.innerHTML === 'Yükleniyor...') {
            fetch('/static/5403_sayili_kanun.md')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('5403 Sayılı Kanun dosyası yüklenemedi');
                    }
                    return response.text();
                })
                .then(text => {
                    // Büyük ovalar bölümünü bul
                    const sections = text.split('##');
                    let buyukOvalarSection = null;
                    
                    for (const section of sections) {
                        if (section.trim().startsWith('BÜYÜK OVALAR VE KORUMA İLKELERİ')) {
                            buyukOvalarSection = section;
                            break;
                        }
                    }
                    
                    if (buyukOvalarSection) {
                        const md = window.markdownit();
                        markdownDiv.innerHTML = md.render('## ' + buyukOvalarSection);
                    } else {
                        markdownDiv.innerHTML = 'Büyük Ovalar ve Koruma İlkeleri bölümü bulunamadı.';
                    }
                })
                .catch(error => {
                    console.error('Hata:', error);
                    markdownDiv.innerHTML = 'Bilgiler yüklenirken bir hata oluştu.';
                });
        }
    },
    
    /**
     * Mevzuat menüsünü aç/kapat
     */
    toggleMevzuatMenu() {
        const content = Utils.getElement('#mevzuat-dropdown-content');
        if (!content) {
            console.error("Mevzuat dropdown content elementi bulunamadı.");
            return;
        }
        const isVisible = content.style.display === 'block';
        Utils.setVisibility(content, !isVisible);
    }
};
