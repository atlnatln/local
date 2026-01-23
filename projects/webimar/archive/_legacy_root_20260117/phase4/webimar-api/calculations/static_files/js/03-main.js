// ========================
// 2. GLOBAL DEĞIŞKENLER (Modüller tarafından erişilecek)
// ========================
let map, marker, popupMessage;
let secilenLat = null, secilenLng = null;
let izmirIcinde = false, isInsideBuyukOva = false, isInsideYasKapaliAlan = false;
let coords = [];

// Dikili arazi kontrol bayrağı - uyarı mesajı göstermemek için
window.noConfirmDikiliCheck = true;

// ========================
// 9. UYGULAMA BAŞLATMA
// ========================
document.addEventListener('DOMContentLoaded', function() {
    Utils.setVisibility(Utils.getElement(CONFIG.selectors.infoSection), false);
    MapModule.init();
    FormModule.init();
    
    // İlk yükleme sırasında sera formu kontrolü
    const yapiTuruSelect = Utils.getElement(CONFIG.selectors.form.yapiTuru);
    if (yapiTuruSelect && yapiTuruSelect.value) {
        FormModule.updateSeraFormuVisibility();
    }
    
    // Dikili arazi kontrol panellerine reset butonu ekle
    addResetButtonsToPanels();
    
    // Bağ evi kısıtlaması popup'ı için olay dinleyicisi ekle
    const bagEviInfoLink = document.getElementById('bag-evi-info-link');
    const bagEviInfoModal = document.getElementById('bag-evi-info-modal');
    const bagEviInfoModalClose = document.getElementById('bag-evi-info-modal-close');
    
    if (bagEviInfoLink && bagEviInfoModal) {
        bagEviInfoLink.addEventListener('click', function() {
            bagEviInfoModal.style.display = 'block';
        });
    }
    
    if (bagEviInfoModalClose && bagEviInfoModal) {
        bagEviInfoModalClose.addEventListener('click', function() {
            bagEviInfoModal.style.display = 'none';
        });
        
        // Modal dışına tıklandığında kapatma
        window.addEventListener('click', function(e) {
            if (e.target === bagEviInfoModal) {
                bagEviInfoModal.style.display = 'none';
            }
        });
    }
    
    // Bağ evi var/yok radiobutton değişikliğini izle
    const bagEviVarRadio = document.getElementById('bag_evi_var');
    const bagEviYokRadio = document.getElementById('bag_evi_yok');
    
    if (bagEviVarRadio && bagEviYokRadio) {
        bagEviVarRadio.addEventListener('change', function() {
            FormCore.checkBagEviUyarisi();
        });
        
        bagEviYokRadio.addEventListener('change', function() {
            FormCore.checkBagEviUyarisi();
        });
    }
});

function openSuTahsisModal() {
    const modal = document.getElementById('su-tahsis-modal');
    if (modal) modal.style.display = 'block';
}

function closeSuTahsisModal() {
    const modal = document.getElementById('su-tahsis-modal');
    if (modal) modal.style.display = 'none';
}

// Dikili arazi kontrol panellerine ve form sonuçlarına reset butonu ekle
function addResetButtonsToPanels() {
    // Panel butonları bölümü (alt kısımdaki buton grubuna eklenir)
    // Burada sadece buton grubuna ekleme yapacağız, sonuç içeriğine değil
    const panels = [
        'harita-secim-panel',
        'manuel-agac-panel'
    ];
    
    panels.forEach(panelId => {
        const panel = document.getElementById(panelId);
        if (!panel) return;
        
        // Önce mevcut TÜM reset butonlarını temizle (hem gruptaki hem sonuçtaki)
        const allResetBtns = panel.querySelectorAll('.reset-all-btn');
        allResetBtns.forEach(btn => btn.remove());
        
        const allResetContainers = panel.querySelectorAll('.reset-button-container');
        allResetContainers.forEach(container => container.remove());
        
        // Alt bölümdeki buton grubunu bul
        const buttonGroup = panel.querySelector('[id$="iptal-btn"]')?.parentElement;
        if (!buttonGroup) return;
        
        // Yeni Sorgu butonu oluştur
        const resetBtn = document.createElement('button');
        resetBtn.className = 'submit-button reset-all-btn';
        resetBtn.style.backgroundColor = '#7f8c8d';
        resetBtn.style.marginRight = '10px';
        resetBtn.innerHTML = '<i class="fas fa-redo"></i> Yeni Sorgu';
        resetBtn.onclick = function() {
            DikiliAraziKontrol.resetAll();
        };
        
        // Buton grubunun başına ekle
        buttonGroup.insertBefore(resetBtn, buttonGroup.firstChild);
    });
    
    // DEĞIŞIKLIK BURADA: Form sonuçları bölümündeki yeni sorgu butonlarını temizle
    // Tüm sonuç konteynerlerindeki reset butonlarını temizle
    const allSonucContainers = document.querySelectorAll('.sonuc-container');
    allSonucContainers.forEach(container => {
        // Sonuç konteyneri içindeki reset buton konteynerlerini bul ve kaldır
        const resetButtonContainers = container.querySelectorAll('.reset-button-container');
        resetButtonContainers.forEach(resetContainer => {
            resetContainer.remove();
        });
    });
    
    // Form sonuçlarına artık buton eklemiyoruz
    // Form sonuçlarına ekleme kodu kaldırıldı
}

// Form sonuçları gösterildiğinde de sıfırlama butonu eklemek için observer ekle
document.addEventListener('DOMContentLoaded', function() {
    // Mevcut panellere reset butonları ekle
    addResetButtonsToPanels();
    
    // Sonuçlar divini gözlemle
    const sonuclarDiv = document.getElementById('sonuclar');
    if (sonuclarDiv) {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && sonuclarDiv.style.display !== 'none') {
                    // Sonuçlar gösterildiğinde reset butonu ekle
                    addResetButtonsToPanels();
                }
            });
        });
        
        observer.observe(sonuclarDiv, { childList: true });
    }
    
    // Dikili alan sonuçlarını gözlemle
    const dikiliSonucDivs = [
        document.getElementById('dikili-alan-sonuc'),
        document.getElementById('manuel-dikili-alan-sonuc')
    ];
    
    dikiliSonucDivs.forEach(div => {
        if (!div) return;
        
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if ((mutation.type === 'attributes' && mutation.attributeName === 'style') ||
                    mutation.type === 'childList') {
                    // Görünürlük değiştiğinde veya içerik değiştiğinde kontrol et
                    if (div.style.display !== 'none') {
                        addResetButtonsToPanels();
                    }
                }
            });
        });
        
        observer.observe(div, { 
            attributes: true,
            attributeFilter: ['style'],
            childList: true
        });
    });
});
