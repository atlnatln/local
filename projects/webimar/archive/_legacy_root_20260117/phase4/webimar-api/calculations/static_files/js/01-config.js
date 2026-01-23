// ========================
// 1. SABİTLER VE KONFİGÜRASYON
// ========================

// Uygulama Konfigürasyonu - Global
const CONFIG = {
    selectors: {
        map: 'map',
        form: {
            yapiTuru: '#id_yapi_turu',
            tapuVasfi: '#id_tapu_vasfi',
            araziBuyuklugu: '#id_arazi_buyuklugu',
            submitButton: '#form-gonder',
            suTahsisVarRadio: '#su_tahsis_var',
            suTahsisYokRadio: '#su_tahsis_yok'
        },
        sonuclar: '#sonuclar',
        suTahsisBelgesi: '#su-tahsis-belgesi-group',
        bagEviUyari: '#bag-evi-kisitlamasi-group',
        buyukOvaUyari: '#buyuk-ova-uyari',
        infoSection: '#info-section',
        markdownContent: '#markdown-content'
    },
    map: {
        center: [38.4237, 27.1428], // İzmir
        zoom: 10,
        maxZoom: 20
    },
    endpoints: {
        checkCoordinate: '/check-coordinate/'
    }
};

// CSS Modül Yöneticisi - Global
window.CSSModuleManager = {
    loadedModules: new Set(),
    moduleMap: {
        'tarla-bag-evi': {
            filename: 'tarla-bag-evi',
            dependencies: ['common-panels'],
            size: '8KB',
            features: ['map-interface', 'area-input-forms', 'manual-entry-panels']
        },
        'dikili-arazi': {
            filename: 'dikili-arazi',
            dependencies: ['common-panels'],
            size: '12KB',
            features: ['dikili-options', 'agac-secici-forms', 'polygon-controls']
        },
        'common-panels': {
            filename: 'common-panels',
            dependencies: [],
            size: '8KB',
            features: ['rustic-panel-base', 'form-controls', 'animations']
        }
    },
    
    /**
     * CSS modülünü dinamik olarak yükle
     * @param {string} moduleName - Yüklenecek CSS modül adı
     * @param {boolean} force - Zaten yüklenmişse tekrar yükle
     */
    async loadModule(moduleName, force = false) {
        if (!force && this.loadedModules.has(moduleName)) {
            return Promise.resolve();
        }
        
        const moduleInfo = this.moduleMap[moduleName];
        if (!moduleInfo) {
            console.warn(`Unknown CSS module: ${moduleName}`);
            return Promise.reject(new Error(`Module ${moduleName} not found`));
        }
        
        // Bağımlılıkları önce yükle
        if (moduleInfo.dependencies.length > 0) {
            await Promise.all(
                moduleInfo.dependencies.map(dep => this.loadModule(dep))
            );
        }
        
        return new Promise((resolve, reject) => {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = `/static/css/modules/${moduleInfo.filename}.css`;
            link.setAttribute('data-module', moduleName);
            link.onload = () => {
                this.loadedModules.add(moduleName);
                console.log(`✅ CSS Module loaded: ${moduleName} (${moduleInfo.size})`);
                resolve();
            };
            link.onerror = () => {
                console.error(`❌ Failed to load CSS module: ${moduleName}`);
                reject(new Error(`Failed to load ${moduleName}`));
            };
            document.head.appendChild(link);
        });
    },
    
    /**
     * Birden fazla CSS modülünü yükle
     * @param {string[]} moduleNames - Yüklenecek modül adları
     */
    async loadModules(moduleNames) {
        const startTime = performance.now();
        try {
            await Promise.all(moduleNames.map(name => this.loadModule(name)));
            const endTime = performance.now();
            console.log(`🚀 CSS Modules loaded in ${(endTime - startTime).toFixed(2)}ms:`, moduleNames);
        } catch (error) {
            console.error('CSS Module loading failed:', error);
            throw error;
        }
    },
    
    /**
     * Yüklenen modüllerin bilgilerini al
     */
    getLoadedModulesInfo() {
        return Array.from(this.loadedModules).map(moduleName => ({
            name: moduleName,
            ...this.moduleMap[moduleName]
        }));
    },
    
    /**
     * Modül boyutlarının toplamını hesapla
     */
    getTotalSize() {
        return Array.from(this.loadedModules).reduce((total, moduleName) => {
            const size = this.moduleMap[moduleName]?.size || '0KB';
            const sizeNum = parseInt(size.replace('KB', ''));
            return total + sizeNum;
        }, 0);
    }
};

// Global değişkenler
window.CONFIG = CONFIG;
window.CSSModuleManager = CSSModuleManager;
