/* Su Tahsis Modal İşlevselliği - index.html'den taşındı */

document.addEventListener('DOMContentLoaded', function() {
    // Su Tahsis Info Modal
    const suTahsisInfoLink = document.getElementById('su-tahsis-info-link');
    const suTahsisModal = document.getElementById('su-tahsis-info-modal');
    const suTahsisCloseBtn = document.getElementById('su-tahsis-info-modal-close');
    const suTahsisModalBody = document.getElementById('su-tahsis-info-modal-body');
    
    if (suTahsisInfoLink && suTahsisModal && suTahsisCloseBtn && suTahsisModalBody) {
        suTahsisInfoLink.onclick = function(e) {
            e.preventDefault();
            fetch('/static/genelge.md')
                .then(r => r.text())
                .then(mdText => {
                    // Başlığı bul
                    const lines = mdText.split('\n');
                    let foundLineIdx = -1;
                    let foundBaslik = '';
                    
                    for (let i = 0; i < lines.length; i++) {
                        const line = lines[i].trim();
                        if (line.startsWith('**Kapalı Su Havzalarında Su Tahsisi ile İlgili Özel Hüküm:**')) {
                            foundLineIdx = i;
                            foundBaslik = line;
                            break;
                        }
                    }
                    
                    if (foundLineIdx === -1) {
                        suTahsisModalBody.innerHTML = 'İçerik bulunamadı.';
                        suTahsisModal.style.display = 'block';
                        return;
                    }
                    
                    // Sonraki başlığa kadar olan kısmı al
                    let sectionLines = [lines[foundLineIdx]];
                    for (let j = foundLineIdx + 1; j < lines.length; j++) {
                        const line = lines[j];
                        if (/^(#|##|###|####|\*\*)/.test(line) && line.trim() !== foundBaslik) {
                            break;
                        }
                        sectionLines.push(line);
                    }
                    
                    const section = sectionLines.join('\n');
                    const md = window.markdownit();
                    suTahsisModalBody.innerHTML = md.render(section);
                    suTahsisModal.style.display = 'block';
                })
                .catch(error => {
                    console.error('Genelge yüklenirken hata:', error);
                    suTahsisModalBody.innerHTML = 'İçerik yüklenirken bir hata oluştu.';
                    suTahsisModal.style.display = 'block';
                });
        };
        
        suTahsisCloseBtn.onclick = function() { 
            suTahsisModal.style.display = 'none'; 
        };
        
        // Modal dışına tıklandığında kapat
        window.addEventListener('click', function(e) {
            if (e.target === suTahsisModal) {
                suTahsisModal.style.display = 'none';
            }
        });
    }
    
    // Bağ Evi Info Modal
    const bagEviInfoLink = document.getElementById('bag-evi-info-link');
    const bagEviModal = document.getElementById('bag-evi-info-modal');
    const bagEviCloseBtn = document.getElementById('bag-evi-info-modal-close');
    
    if (bagEviInfoLink && bagEviModal && bagEviCloseBtn) {
        bagEviInfoLink.onclick = function(e) {
            e.preventDefault();
            bagEviModal.style.display = 'block';
        };
        
        bagEviCloseBtn.onclick = function() { 
            bagEviModal.style.display = 'none'; 
        };
        
        // Modal dışına tıklandığında kapat
        window.addEventListener('click', function(e) {
            if (e.target === bagEviModal) {
                bagEviModal.style.display = 'none';
            }
        });
    }
});
