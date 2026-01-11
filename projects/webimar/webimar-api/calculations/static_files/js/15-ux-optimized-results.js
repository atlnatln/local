/**
 * UX-Optimized Results Renderer
 * Issue #21 - Hesaplama Sonuçları UX İyileştirmeleri
 */

const UXOptimizedRenderer = {
    
    /**
     * UX-optimize edilmiş response'ları render eder
     */
    renderOptimizedResults(data, container) {
        if (!data || typeof data !== 'object') {
            container.innerHTML = this.renderError('Geçersiz yanıt formatı');
            return;
        }

        // UX-optimize format kontrol et
        if (data.result && data.explanation && data.summary) {
            container.innerHTML = this.renderUXOptimizedFormat(data);
        } else {
            // Fallback: eski format
            container.innerHTML = this.renderLegacyFormat(data);
        }
    },

    /**
     * Yeni UX-optimize format renderer
     */
    renderUXOptimizedFormat(data) {
        const result = data.result;
        const explanation = data.explanation;
        const summary = data.summary;
        const meta = data.meta;

        let html = '<div class="ux-optimized-results">';
        
        // 1. Ana Sonuç (En üstte, vurgulu)
        html += this.renderMainResult(result);
        
        // 2. Gerekçeler ve Öneriler
        if (explanation.reasons.length > 0 || explanation.recommendations.length > 0) {
            html += this.renderExplanation(explanation);
        }
        
        // 3. Özet Bilgiler
        if (Object.keys(summary).length > 0) {
            html += this.renderSummary(summary);
        }
        
        // 4. Harita Bağlantısı
        if (data.map_info && data.map_info.show_on_map_available) {
            html += this.renderMapLink(data.map_info);
        }
        
        // 5. Meta Bilgiler
        html += this.renderMetaInfo(meta);
        
        // 6. Aksiyonlar (Kopyala, Sil vs.)
        html += this.renderActions(data);
        
        // 7. Teknik Detaylar (Accordion)
        if (meta.has_technical_details) {
            html += this.renderTechnicalDetails(data.technical_details);
        }
        
        // 8. Gelişmiş Detaylar (Accordion)
        if (meta.has_advanced_details) {
            html += this.renderAdvancedDetails(data.advanced_details);
        }
        
        html += '</div>';
        
        return html;
    },

    /**
     * Ana sonuç kutusu (Issue #21 - 4. Sonuç mesajı hiyerarşisi)
     */
    renderMainResult(result) {
        const statusClass = this.getStatusClass(result.result_type);
        const icon = this.getStatusIcon(result.result_type);
        
        return `
            <div class="main-result-box ${statusClass}">
                <div class="result-icon">${icon}</div>
                <div class="result-content">
                    <h2 class="main-result-title">${result.main_message}</h2>
                    <span class="result-status">${result.status.replace('_', ' ').toUpperCase()}</span>
                </div>
            </div>
        `;
    },

    /**
     * Gerekçeler ve öneriler (Issue #21 - 1. Olumsuz sonuçlarda neden ve öneriler)
     */
    renderExplanation(explanation) {
        let html = '<div class="explanation-section">';
        
        if (explanation.reasons.length > 0) {
            html += '<div class="reasons-box">';
            html += '<h4><i class="fas fa-info-circle"></i> Gerekçeler</h4>';
            html += '<ul class="reasons-list">';
            explanation.reasons.forEach(reason => {
                html += `<li>${reason}</li>`;
            });
            html += '</ul></div>';
        }
        
        if (explanation.recommendations.length > 0) {
            html += '<div class="recommendations-box">';
            html += '<h4><i class="fas fa-lightbulb"></i> Öneriler</h4>';
            html += '<ul class="recommendations-list">';
            explanation.recommendations.forEach(rec => {
                html += `<li>${rec}</li>`;
            });
            html += '</ul></div>';
        }
        
        html += '</div>';
        return html;
    },

    /**
     * Özet bilgiler (Issue #21 - 2. Sadece anlamlı bilgiler)
     */
    renderSummary(summary) {
        if (Object.keys(summary).length === 0) return '';
        
        let html = '<div class="summary-section">';
        html += '<h4><i class="fas fa-chart-bar"></i> Özet Bilgiler</h4>';
        html += '<div class="summary-grid">';
        
        // Önemli bilgileri önce göster
        const priorityFields = ['arazi_alani_m2', 'emsal_m2', 'hayvan_kapasitesi', 'kapasite'];
        const displayedFields = new Set();
        
        priorityFields.forEach(field => {
            if (summary[field] !== undefined) {
                html += this.renderSummaryItem(field, summary[field]);
                displayedFields.add(field);
            }
        });
        
        // Diğer alanları göster
        Object.entries(summary).forEach(([key, value]) => {
            if (!displayedFields.has(key) && value !== undefined && value !== null && value !== '') {
                html += this.renderSummaryItem(key, value);
            }
        });
        
        html += '</div></div>';
        return html;
    },

    /**
     * Özet item renderer
     */
    renderSummaryItem(key, value) {
        const label = this.getFieldLabel(key);
        const formattedValue = this.formatValue(key, value);
        
        return `
            <div class="summary-item">
                <span class="summary-label">${label}:</span>
                <span class="summary-value">${formattedValue}</span>
            </div>
        `;
    },

    /**
     * Harita bağlantısı (Issue #21 - 6. Harita ve sonuç bağlantısı)
     */
    renderMapLink(mapInfo) {
        if (!mapInfo.coordinates || !mapInfo.coordinates.lat) return '';
        
        return `
            <div class="map-link-section">
                <button class="btn btn-outline-primary show-on-map-btn" 
                        onclick="showResultOnMap(${mapInfo.coordinates.lat}, ${mapInfo.coordinates.lng})">
                    <i class="fas fa-map-marker-alt"></i> Haritada Göster
                </button>
            </div>
        `;
    },

    /**
     * Meta bilgiler (Issue #21 - 7. Tarih/saat bilgisi)
     */
    renderMetaInfo(meta) {
        return `
            <div class="meta-info">
                <small class="text-muted">
                    <i class="fas fa-clock"></i> ${meta.calculation_date}
                    ${meta.calculation_type ? ` • ${this.getCalculationTypeLabel(meta.calculation_type)}` : ''}
                </small>
            </div>
        `;
    },

    /**
     * Aksiyonlar (Issue #21 - 5. Kopyala/Sil butonları)
     */
    renderActions(data) {
        return `
            <div class="actions-section">
                <button class="btn btn-sm btn-outline-secondary" 
                        onclick="copyResultToClipboard()" 
                        title="Sonucu panoya kopyala">
                    <i class="fas fa-copy"></i> Kopyala
                </button>
                <button class="btn btn-sm btn-outline-danger" 
                        onclick="deleteCalculation()" 
                        title="Bu hesabı sil">
                    <i class="fas fa-trash"></i> Sil
                </button>
                <button class="btn btn-sm btn-outline-primary" 
                        onclick="startNewCalculation()" 
                        title="Yeni hesaplama başlat">
                    <i class="fas fa-plus"></i> Yeni Hesaplama
                </button>
            </div>
        `;
    },

    /**
     * Teknik detaylar accordion (Issue #21 - 1. Teknik detaylar gizli)
     */
    renderTechnicalDetails(technicalDetails) {
        return `
            <div class="technical-details-section">
                <div class="accordion" id="technicalAccordion">
                    <div class="accordion-item">
                        <h5 class="accordion-header">
                            <button class="accordion-button collapsed" type="button" 
                                    data-bs-toggle="collapse" data-bs-target="#technicalCollapse">
                                <i class="fas fa-cog"></i> Teknik Detaylar
                            </button>
                        </h5>
                        <div id="technicalCollapse" class="accordion-collapse collapse" 
                             data-bs-parent="#technicalAccordion">
                            <div class="accordion-body">
                                ${this.renderObjectAsTable(technicalDetails)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Gelişmiş detaylar accordion (Issue #21 - 2. Ham veri gizli)
     */
    renderAdvancedDetails(advancedDetails) {
        return `
            <div class="advanced-details-section">
                <div class="accordion" id="advancedAccordion">
                    <div class="accordion-item">
                        <h5 class="accordion-header">
                            <button class="accordion-button collapsed" type="button" 
                                    data-bs-toggle="collapse" data-bs-target="#advancedCollapse">
                                <i class="fas fa-code"></i> Gelişmiş Detaylar
                            </button>
                        </h5>
                        <div id="advancedCollapse" class="accordion-collapse collapse" 
                             data-bs-parent="#advancedAccordion">
                            <div class="accordion-body">
                                <pre class="json-display">${JSON.stringify(advancedDetails, null, 2)}</pre>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Legacy format fallback
     */
    renderLegacyFormat(data) {
        return `
            <div class="legacy-format-warning">
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i> 
                    Bu sonuç eski formatta gösteriliyor. Gelişmiş görünüm için lütfen sayfayı yenileyin.
                </div>
                ${ResultsModule.renderUnknownFormat(data)}
            </div>
        `;
    },

    /**
     * Hata durumu renderer
     */
    renderError(message) {
        return `
            <div class="error-container">
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i> ${message}
                </div>
            </div>
        `;
    },

    // Utility fonksiyonlar
    getStatusClass(resultType) {
        switch(resultType) {
            case 'positive': return 'result-positive';
            case 'negative': return 'result-negative';
            case 'neutral': return 'result-neutral';
            default: return 'result-unknown';
        }
    },

    getStatusIcon(resultType) {
        switch(resultType) {
            case 'positive': return '<i class="fas fa-check-circle"></i>';
            case 'negative': return '<i class="fas fa-times-circle"></i>';
            case 'neutral': return '<i class="fas fa-info-circle"></i>';
            default: return '<i class="fas fa-question-circle"></i>';
        }
    },

    getFieldLabel(key) {
        const labels = {
            'arazi_alani_m2': 'Arazi Alanı',
            'emsal_m2': 'Emsal Alanı',
            'hayvan_kapasitesi': 'Hayvan Kapasitesi',
            'kapasite': 'Kapasite',
            'maksimum_taban_alani': 'Maksimum Taban Alanı',
            'maksimum_toplam_alan': 'Maksimum Toplam Alan'
        };
        return labels[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    },

    formatValue(key, value) {
        if (key.includes('m2') || key.includes('alan')) {
            return `${Number(value).toLocaleString('tr-TR')} m²`;
        }
        if (key.includes('kapasite') || key.includes('sayisi')) {
            return `${Number(value).toLocaleString('tr-TR')} adet`;
        }
        return value;
    },

    getCalculationTypeLabel(type) {
        const labels = {
            'hara': 'Hara Tesisi',
            'evcil_hayvan': 'Evcil Hayvan Tesisi',
            'sut_sigirciligi': 'Süt Sığırcılığı',
            'besi_sigirciligi': 'Besi Sığırcılığı'
        };
        return labels[type] || type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    },

    renderObjectAsTable(obj) {
        let html = '<table class="table table-sm">';
        Object.entries(obj).forEach(([key, value]) => {
            html += `<tr><td><strong>${this.getFieldLabel(key)}</strong></td><td>${value}</td></tr>`;
        });
        html += '</table>';
        return html;
    }
};

// Global fonksiyonlar (buton onclick'ler için)
function copyResultToClipboard() {
    // Implementation
    console.log('Sonuç kopyalandı');
}

function deleteCalculation() {
    // Implementation
    console.log('Hesaplama silindi');
}

function startNewCalculation() {
    // Implementation
    window.location.reload();
}

function showResultOnMap(lat, lng) {
    // Implementation
    console.log(`Haritada göster: ${lat}, ${lng}`);
}
