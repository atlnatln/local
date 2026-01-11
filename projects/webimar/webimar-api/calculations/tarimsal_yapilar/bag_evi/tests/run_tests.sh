#!/usr/bin/env bash
# Bağ Evi Modülü Test Runner Scripti
# Tüm bag_evi testlerini çalıştırır ve sonuçları raporlar

set -e  # Hata durumunda dur

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}=================================================================="
echo -e "🧪 BAĞ EVİ MODÜLÜ TEST RUNNER"
echo -e "=================================================================="
echo -e "${NC}"

# Test dizini
TEST_DIR="/home/akn/Genel/webimar/webimar-api/calculations/tarimsal_yapilar/bag_evi/tests"
PROJECT_ROOT="/home/akn/Genel/webimar"
VENV_PYTHON="/home/akn/Genel/webimar/.venv/bin/python"

# Proje dizinine geç
cd "$PROJECT_ROOT"

echo -e "${BLUE}📁 Test Dizini: ${TEST_DIR}${NC}"
echo -e "${BLUE}🐍 Python Interpreter: ${VENV_PYTHON}${NC}"
echo ""

# Mevcut testleri listele
echo -e "${YELLOW}📋 Mevcut Test Dosyaları:${NC}"
ls -la "$TEST_DIR"/*.py | grep -E "test_.*\.py$" || echo "Hiç test dosyası bulunamadı"
echo ""

# Test fonksiyonu
run_test() {
    local test_file=$1
    local test_name=$(basename "$test_file" .py)
    
    echo -e "${BLUE}🔍 ${test_name} çalıştırılıyor...${NC}"
    
    if cd "$PROJECT_ROOT/webimar-api" && "$VENV_PYTHON" -m pytest "$test_file" -v --tb=short 2>&1; then
        echo -e "${GREEN}✅ ${test_name} - BAŞARILI${NC}"
        return 0
    else
        echo -e "${RED}❌ ${test_name} - BAŞARISIZ${NC}"
        return 1
    fi
}

# Test sayaçları
total_tests=0
passed_tests=0
failed_tests=0

echo -e "${YELLOW}🚀 Testler başlatılıyor...${NC}"
echo ""

# Her test dosyasını çalıştır
for test_file in "$TEST_DIR"/test_*.py; do
    if [ -f "$test_file" ]; then
        total_tests=$((total_tests + 1))
        
        if run_test "$test_file"; then
            passed_tests=$((passed_tests + 1))
        else
            failed_tests=$((failed_tests + 1))
        fi
        
        echo ""
    fi
done

# Özet rapor
echo -e "${BLUE}=================================================================="
echo -e "📊 TEST SONUÇLARI"
echo -e "=================================================================="
echo -e "${YELLOW}Toplam Test: ${total_tests}${NC}"
echo -e "${GREEN}Başarılı: ${passed_tests}${NC}"
echo -e "${RED}Başarısız: ${failed_tests}${NC}"

if [ $failed_tests -eq 0 ]; then
    echo -e "${GREEN}🎉 TÜM TESTLER BAŞARILI!${NC}"
    exit_code=0
else
    echo -e "${RED}⚠️  BAŞARISIZ TESTLER VAR!${NC}"
    exit_code=1
fi

echo -e "${BLUE}==================================================================${NC}"

# Ek test - Yeni zengin formatlama sistemi testi
echo ""
echo -e "${YELLOW}🎨 Zengin Formatlama Sistemi Testi${NC}"
echo ""

if cd "$PROJECT_ROOT" && "$VENV_PYTHON" test-bag-evi-rich-formatting.py; then
    echo -e "${GREEN}✅ Zengin Formatlama - BAŞARILI${NC}"
else
    echo -e "${RED}❌ Zengin Formatlama - BAŞARISIZ${NC}"
    exit_code=1
fi

# Test coverage bilgisi (eğer pytest-cov yüklüyse)
echo ""
echo -e "${YELLOW}📈 Test Coverage Raporu (eğer mevcut ise)${NC}"

if command -v "$VENV_PYTHON" -m pytest --cov 2>/dev/null; then
    cd "$PROJECT_ROOT/webimar-api"
    "$VENV_PYTHON" -m pytest "$TEST_DIR" --cov=calculations.tarimsal_yapilar.bag_evi --cov-report=term-missing 2>/dev/null || echo "Coverage raporu oluşturulamadı"
else
    echo "pytest-cov yüklü değil, coverage raporu atlandı"
fi

echo ""
echo -e "${BLUE}Test çalıştırma tamamlandı. Exit code: ${exit_code}${NC}"

exit $exit_code
