/**
 * CSS Modül Performans İzleyicisi
 * Geliştirme ve production ortamlarında CSS modül yükleme performansını izler
 */

window.CSSPerformanceMonitor = {
    isEnabled: true, // Production'da false yapılabilir
    metrics: {
        totalModulesLoaded: 0,
        totalLoadTime: 0,
        loadHistory: [],
        errors: []
    },
    
    /**
     * Performans izlemeyi başlat
     */
    init() {
        if (!this.isEnabled) return;
        
        // Sayfa yüklenme zamanını takip et
        window.addEventListener('load', () => {
            this.logPageLoadMetrics();
        });
        
        // CSS modül yüklemelerini gözlemle
        this.observeCSSLoading();
        
        console.log('🔍 CSS Performance Monitor initialized');
    },
    
    /**
     * CSS modül yükleme işlemlerini gözlemle
     */
    observeCSSLoading() {
        const originalLoadModule = window.CSSModuleManager.loadModule;
        const self = this;
        
        window.CSSModuleManager.loadModule = async function(moduleName, force = false) {
            const startTime = performance.now();
            
            try {
                const result = await originalLoadModule.call(this, moduleName, force);
                const endTime = performance.now();
                const loadTime = endTime - startTime;
                
                self.recordModuleLoad(moduleName, loadTime, true);
                return result;
            } catch (error) {
                const endTime = performance.now();
                const loadTime = endTime - startTime;
                
                self.recordModuleLoad(moduleName, loadTime, false, error);
                throw error;
            }
        };
    },
    
    /**
     * Modül yükleme kaydını tut
     */
    recordModuleLoad(moduleName, loadTime, success, error = null) {
        this.metrics.totalModulesLoaded++;
        this.metrics.totalLoadTime += loadTime;
        
        const record = {
            moduleName,
            loadTime: Math.round(loadTime * 100) / 100,
            success,
            timestamp: new Date().toISOString(),
            error: error ? error.message : null
        };
        
        this.metrics.loadHistory.push(record);
        
        if (!success) {
            this.metrics.errors.push(record);
        }
        
        if (this.isEnabled) {
            const status = success ? '✅' : '❌';
            console.log(`${status} CSS Module: ${moduleName} (${record.loadTime}ms)`);
        }
    },
    
    /**
     * Sayfa yükleme metriklerini logla
     */
    logPageLoadMetrics() {
        const navigation = performance.getEntriesByType('navigation')[0];
        const cssResources = performance.getEntriesByType('resource')
            .filter(resource => resource.name.includes('.css'));
            
        console.group('📊 CSS Loading Performance Report');
        console.log(`📄 Page Load Time: ${Math.round(navigation.loadEventEnd - navigation.navigationStart)}ms`);
        console.log(`🎨 Total CSS Resources: ${cssResources.length}`);
        console.log(`📦 Modular CSS Loaded: ${this.metrics.totalModulesLoaded}`);
        console.log(`⏱️ Total Module Load Time: ${Math.round(this.metrics.totalLoadTime)}ms`);
        
        if (this.metrics.errors.length > 0) {
            console.warn(`⚠️ CSS Loading Errors: ${this.metrics.errors.length}`);
            this.metrics.errors.forEach(error => {
                console.error(`- ${error.moduleName}: ${error.error}`);
            });
        }
        
        console.groupEnd();
    },
    
    /**
     * Detaylı performans raporu al
     */
    getPerformanceReport() {
        const avgLoadTime = this.metrics.totalModulesLoaded > 0 
            ? this.metrics.totalLoadTime / this.metrics.totalModulesLoaded 
            : 0;
            
        return {
            summary: {
                totalModules: this.metrics.totalModulesLoaded,
                totalLoadTime: Math.round(this.metrics.totalLoadTime),
                averageLoadTime: Math.round(avgLoadTime * 100) / 100,
                errorCount: this.metrics.errors.length,
                successRate: this.metrics.totalModulesLoaded > 0 
                    ? Math.round((1 - this.metrics.errors.length / this.metrics.totalModulesLoaded) * 100)
                    : 100
            },
            details: this.metrics.loadHistory,
            errors: this.metrics.errors
        };
    },
    
    /**
     * Console'da performans raporu göster
     */
    showReport() {
        const report = this.getPerformanceReport();
        
        console.group('🔍 CSS Module Performance Report');
        console.table(report.summary);
        
        if (report.details.length > 0) {
            console.group('📋 Module Loading Details');
            console.table(report.details);
            console.groupEnd();
        }
        
        if (report.errors.length > 0) {
            console.group('❌ Loading Errors');
            console.table(report.errors);
            console.groupEnd();
        }
        
        console.groupEnd();
    },
    
    /**
     * Performans metriklerini döndür
     */
    getMetrics() {
        return {
            ...this.metrics,
            averageLoadTime: this.metrics.totalModulesLoaded > 0 
                ? this.metrics.totalLoadTime / this.metrics.totalModulesLoaded 
                : 0
        };
    }
};

// Sayfa yüklendiğinde başlat
document.addEventListener('DOMContentLoaded', () => {
    window.CSSPerformanceMonitor.init();
});

// Global fonksiyon olarak erişilebilir yap
window.showCSSReport = () => window.CSSPerformanceMonitor.showReport();
