#!/bin/bash
# ============================================================================
# MathLock Play — Deploy Script (Google Play Store + Debug)
#
# Play Store sürümü: AAB (Android App Bundle) + ADB test
# OTA yok — dağıtım Play Store üzerinden yapılır.
# AI soru pipeline'ı aynı şekilde çalışır (data sync).
#
# Çalıştırma:
#   ./deploy.sh              # versionCode artır + debug APK derle
#   ./deploy.sh --release    # Release AAB derle (keystore gerekir)
#   ./deploy.sh --adb        # Debug APK derle + USB ile telefona kur
#   ./deploy.sh --build-only # Sadece derle, hiçbir yere yükleme
#   ./deploy.sh --sync-data  # Sadece data sync (build yok)
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ─── Yapılandırma ───────────────────────────────────────────────────────────
VPS_HOST="akn@89.252.152.222"
VPS_DATA_PATH="/var/www/mathlock/data"
HEALTH_URL="https://mathlock.com.tr/mathlock/data/questions.json"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

# ─── Argümanlar ─────────────────────────────────────────────────────────────
BUILD_TYPE="debug"
SKIP_ADB=true
BUILD_ONLY=false
SYNC_DATA_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --release)       BUILD_TYPE="release"; shift ;;
        --adb)           SKIP_ADB=false; shift ;;
        --build-only)    BUILD_ONLY=true; SKIP_ADB=true; shift ;;
        --sync-data)     SYNC_DATA_ONLY=true; shift ;;
        --help)
            echo "Kullanım: $0 [seçenekler]"
            echo "  --release      Release AAB derle (keystore.jks gerekir)"
            echo "  --adb          Debug APK derle + USB ile telefona kur"
            echo "  --build-only   Sadece derle, yükleme yapma"
            echo "  --sync-data    Sadece VPS data sync (build yok)"
            exit 0
            ;;
        *) log_error "Bilinmeyen seçenek: $1"; exit 1 ;;
    esac
done

echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║      📱 MathLock Play — Deploy (Play Store)          ║${NC}"
echo -e "${CYAN}║      Build: ${BUILD_TYPE}                                    ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"

cd "$PROJECT_DIR"

# ─── Sadece data sync ────────────────────────────────────────────────────────
if [ "$SYNC_DATA_ONLY" = true ]; then
    echo -e "\n${YELLOW}[DATA SYNC] VPS ile soru verileri senkronize ediliyor...${NC}"
    DATA_SYNC_DIR="$PROJECT_DIR/data"

    if [ ! -d "$DATA_SYNC_DIR" ]; then
        log_error "data/ dizini bulunamadı"
        exit 1
    fi

    ssh "$VPS_HOST" "sudo mkdir -p ${VPS_DATA_PATH}"

    # VPS'teki version'u kontrol et
    VPS_Q_VERSION=$(ssh "$VPS_HOST" "python3 -c \"import json; print(json.load(open('${VPS_DATA_PATH}/questions.json'))['version'])\" 2>/dev/null || echo 0")
    LOCAL_Q_VERSION=$(python3 -c "import json; print(json.load(open('$DATA_SYNC_DIR/questions.json'))['version'])" 2>/dev/null || echo 0)

    if [ "$LOCAL_Q_VERSION" -gt "$VPS_Q_VERSION" ] 2>/dev/null; then
        scp "$DATA_SYNC_DIR/questions.json" "${VPS_HOST}:/tmp/ml-q.json"
        ssh "$VPS_HOST" "sudo cp /tmp/ml-q.json ${VPS_DATA_PATH}/questions.json && rm /tmp/ml-q.json"
        log_success "questions.json VPS'e senkronize edildi (v${LOCAL_Q_VERSION} > v${VPS_Q_VERSION})"
        if [ -f "$DATA_SYNC_DIR/topics.json" ]; then
            scp "$DATA_SYNC_DIR/topics.json" "${VPS_HOST}:/tmp/ml-t.json"
            ssh "$VPS_HOST" "sudo cp /tmp/ml-t.json ${VPS_DATA_PATH}/topics.json && rm /tmp/ml-t.json"
            log_success "topics.json VPS'e senkronize edildi"
        fi
    else
        log_info "VPS veri korundu (VPS: v${VPS_Q_VERSION}, yerel: v${LOCAL_Q_VERSION})"
        # Yerel'i VPS'ten güncelle
        scp "${VPS_HOST}:${VPS_DATA_PATH}/questions.json" "$DATA_SYNC_DIR/questions.json" 2>/dev/null && \
            log_success "questions.json VPS'ten yerele çekildi (v${VPS_Q_VERSION})" || true
        scp "${VPS_HOST}:${VPS_DATA_PATH}/topics.json" "$DATA_SYNC_DIR/topics.json" 2>/dev/null && \
            log_success "topics.json VPS'ten yerele çekildi" || true
    fi
    exit 0
fi

# ─── 0. Versiyon otomatik artırma ────────────────────────────────────────────
GRADLE_FILE="$PROJECT_DIR/app/build.gradle.kts"
CURRENT_CODE=$(grep 'versionCode\s*=' "$GRADLE_FILE" | grep -o '[0-9]\+')
NEW_CODE=$((CURRENT_CODE + 1))
NEW_NAME="1.0.${NEW_CODE}"
sed -i "s/versionCode = ${CURRENT_CODE}/versionCode = ${NEW_CODE}/" "$GRADLE_FILE"
sed -i "s/versionName = \"[^\"]*\"/versionName = \"${NEW_NAME}\"/" "$GRADLE_FILE"
log_info "Versiyon: ${CURRENT_CODE} → ${NEW_CODE} (v${NEW_NAME})"

# ─── Release keystore kontrolü ───────────────────────────────────────────────
if [[ "$BUILD_TYPE" == "release" ]]; then
    if [ ! -f "keystore.jks" ]; then
        log_error "keystore.jks bulunamadı!"
        echo ""
        echo "  Play Store için önce bir keystore oluştur:"
        echo "  keytool -genkeypair -v \\"
        echo "    -keystore keystore.jks \\"
        echo "    -keyalg RSA -keysize 2048 -validity 10000 \\"
        echo "    -alias mathlock-play \\"
        echo "    -storepass <şifre> -keypass <şifre>"
        echo ""
        echo "  Ardından app/build.gradle.kts dosyasına signing config ekle."
        exit 1
    fi
fi

# ─── 1. Derleme ─────────────────────────────────────────────────────────────
if [[ "$BUILD_TYPE" == "release" ]]; then
    echo -e "\n${YELLOW}[1/3] 🔨 AAB derleniyor (release — Play Store)...${NC}"
    GRADLE_TASK="bundleRelease"
else
    echo -e "\n${YELLOW}[1/3] 🔨 APK derleniyor (debug — test)...${NC}"
    GRADLE_TASK="assembleDebug"
fi

./gradlew "$GRADLE_TASK" --no-daemon 2>&1 | grep -E "(BUILD|ERROR|error:|warning:|WARN|Task :)" || true

# Çıktı dosyasını bul
if [[ "$BUILD_TYPE" == "release" ]]; then
    AAB_PATH="app/build/outputs/bundle/release/app-release.aab"
    if [ ! -f "$AAB_PATH" ]; then
        log_error "AAB bulunamadı: $AAB_PATH"
        exit 1
    fi
    OUTPUT_SIZE=$(du -sh "$AAB_PATH" | cut -f1)
    log_success "AAB hazır: $AAB_PATH ($OUTPUT_SIZE)"
else
    APK_PATH="app/build/outputs/apk/debug/app-debug.apk"
    if [ ! -f "$APK_PATH" ]; then
        log_error "APK bulunamadı: $APK_PATH"
        exit 1
    fi
    OUTPUT_SIZE=$(du -sh "$APK_PATH" | cut -f1)
    log_success "APK hazır: $APK_PATH ($OUTPUT_SIZE)"
fi

# output-metadata.json'dan bilgi oku
if [[ "$BUILD_TYPE" == "release" ]]; then
    VERSION_CODE=$NEW_CODE
    VERSION_NAME=$NEW_NAME
else
    METADATA_FILE="app/build/outputs/apk/debug/output-metadata.json"
    if [ -f "$METADATA_FILE" ]; then
        VERSION_CODE=$(python3 -c "import json; d=json.load(open('$METADATA_FILE')); print(d['elements'][0]['versionCode'])" 2>/dev/null || echo "$NEW_CODE")
        VERSION_NAME=$(python3 -c "import json; d=json.load(open('$METADATA_FILE')); print(d['elements'][0]['versionName'])" 2>/dev/null || echo "$NEW_NAME")
    else
        VERSION_CODE=$NEW_CODE
        VERSION_NAME=$NEW_NAME
    fi
fi

# ─── 2. Telefona ADB kurulumu (sadece debug) ────────────────────────────────
if [ "$SKIP_ADB" = false ] && [[ "$BUILD_TYPE" == "debug" ]]; then
    echo -e "\n${YELLOW}[2/3] 📱 Telefona kuruluyor (ADB)...${NC}"

    if ! command -v adb &>/dev/null; then
        log_warning "adb komutu bulunamadı. Android SDK platform-tools PATH'de olmalı."
    else
        DEVICES=$(adb devices | grep -v "List of devices" | grep "device$" | wc -l)
        if [ "$DEVICES" -eq 0 ]; then
            log_warning "Bağlı telefon bulunamadı."
        else
            log_info "Bağlı cihaz sayısı: $DEVICES"
            adb install -r "$APK_PATH" && log_success "Telefona kuruldu!"
        fi
    fi
else
    echo -e "\n${YELLOW}[2/3] ⏭️  ADB kurulum atlandı${NC}"
fi

# ─── 3. Data sync (soru verileri) ───────────────────────────────────────────
if [ "$BUILD_ONLY" = true ]; then
    echo -e "\n${YELLOW}[3/3] ⏭️  Data sync atlandı (build-only)${NC}"
else
    echo -e "\n${YELLOW}[3/3] 🔄 VPS data sync kontrol ediliyor...${NC}"
    DATA_SYNC_DIR="$PROJECT_DIR/data"

    if [ -d "$DATA_SYNC_DIR" ] && [ -f "$DATA_SYNC_DIR/questions.json" ]; then
        ssh "$VPS_HOST" "sudo mkdir -p ${VPS_DATA_PATH}" 2>/dev/null

        VPS_Q_VERSION=$(ssh "$VPS_HOST" "python3 -c \"import json; print(json.load(open('${VPS_DATA_PATH}/questions.json'))['version'])\" 2>/dev/null || echo 0" 2>/dev/null)
        LOCAL_Q_VERSION=$(python3 -c "import json; print(json.load(open('$DATA_SYNC_DIR/questions.json'))['version'])" 2>/dev/null || echo 0)

        if [ "$LOCAL_Q_VERSION" -gt "$VPS_Q_VERSION" ] 2>/dev/null; then
            scp "$DATA_SYNC_DIR/questions.json" "${VPS_HOST}:/tmp/ml-q.json"
            scp "$DATA_SYNC_DIR/topics.json" "${VPS_HOST}:/tmp/ml-t.json" 2>/dev/null
            ssh "$VPS_HOST" "sudo cp /tmp/ml-q.json ${VPS_DATA_PATH}/questions.json && sudo cp /tmp/ml-t.json ${VPS_DATA_PATH}/topics.json 2>/dev/null; rm -f /tmp/ml-q.json /tmp/ml-t.json"
            log_success "Data VPS'e senkronize edildi (v${LOCAL_Q_VERSION} > v${VPS_Q_VERSION})"
        else
            log_info "VPS verisi güncel (VPS: v${VPS_Q_VERSION}, yerel: v${LOCAL_Q_VERSION})"
        fi
    else
        log_warning "data/questions.json bulunamadı — data sync atlandı"
    fi

    # nginx config güncelle (mathlock.com.tr)
    NGINX_CONF="$PROJECT_DIR/website/nginx-mathlock.conf"
    if [ -f "$NGINX_CONF" ]; then
        scp "$NGINX_CONF" "${VPS_HOST}:/tmp/nginx-mathlock.conf" 2>/dev/null
        ssh "$VPS_HOST" "sudo cp /tmp/nginx-mathlock.conf /home/akn/vps/infrastructure/nginx/conf.d/mathlock-play.conf && rm /tmp/nginx-mathlock.conf" 2>/dev/null && \
            log_success "nginx config VPS'e kopyalandı" || log_warning "nginx config kopyalanamadı"
    fi
    NGINX_RELOAD=$(ssh "$VPS_HOST" "docker exec vps_nginx_main nginx -s reload 2>&1 || true" 2>/dev/null)
    log_info "nginx reload: ${NGINX_RELOAD:-ok}"
fi

# ─── Özet ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✅ Deploy tamamlandı!                    ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
if [[ "$BUILD_TYPE" == "release" ]]; then
    echo -e "${BLUE}AAB:${NC}      $AAB_PATH ($OUTPUT_SIZE)"
else
    echo -e "${BLUE}APK:${NC}      $APK_PATH ($OUTPUT_SIZE)"
fi
echo -e "${BLUE}Sürüm:${NC}    v${VERSION_NAME} (versionCode: ${VERSION_CODE})"
echo -e "${BLUE}Build:${NC}    ${BUILD_TYPE}"
echo -e "${BLUE}Paket:${NC}    com.akn.mathlock.play"
[ "$SKIP_ADB" = false ] && echo -e "${BLUE}Telefon:${NC}  ADB kurulumu denendi"
echo ""

if [[ "$BUILD_TYPE" == "release" ]]; then
    echo -e "${CYAN}Play Store Yükleme:${NC}"
    echo -e "  1. https://play.google.com/console adresine gidin"
    echo -e "  2. Uygulama seçin → Sürüm → Dahili test / Kapalı test"
    echo -e "  3. AAB dosyasını yükleyin: ${AAB_PATH}"
    echo -e "  4. Sürüm notlarını girin → İncele ve Yayınla"
    echo ""
fi

echo -e "${CYAN}Veri Endpoint'leri:${NC}"
echo -e "  📊 Sorular: https://mathlock.com.tr/mathlock/data/questions.json"
echo -e "  📚 Konular: https://mathlock.com.tr/mathlock/data/topics.json"
echo -e "  ❤️  Sağlık:  https://mathlock.com.tr/mathlock/health"
