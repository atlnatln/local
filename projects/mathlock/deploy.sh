#!/bin/bash
# ============================================================================
# MathLock Android - Deploy Script
# Yerel derleme → versionCode otomatik artır → VPS'e OTA yükle
#
# Çalıştırma:
#   ./deploy.sh              # versionCode artır + derle + VPS'e gönder
#   ./deploy.sh --adb        # Ayrıca USB ile telefona ADB kurulumu yap
#   ./deploy.sh --release    # Release APK (keystore gerekir)
#   ./deploy.sh --skip-vps   # VPS'e yüklemeyi atla
#   ./deploy.sh --build-only # Sadece derle, bir yere yükleme
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
VPS_PATH="/home/akn/vps/projects/mathlock"
VPS_DIST_PATH="/home/akn/vps/projects/mathlock/dist"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

# ─── Argümanlar ─────────────────────────────────────────────────────────────
BUILD_TYPE="debug"
SKIP_ADB=true   # Varsayılan: ADB kapalı (OTA ile güncelleme). Açmak için: --adb
SKIP_VPS=false
BUILD_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --release)    BUILD_TYPE="release"; shift ;;
        --adb)        SKIP_ADB=false; shift ;;
        --skip-adb)   SKIP_ADB=true; shift ;;   # geriye dönük uyumluluk
        --skip-vps)   SKIP_VPS=true; shift ;;
        --build-only) BUILD_ONLY=true; SKIP_ADB=true; SKIP_VPS=true; shift ;;
        --help)
            echo "Kullanım: $0 [seçenekler]"
            echo "  --adb         USB ile telefona ADB kurulumu yap"
            echo "  --release     Release APK derle (keystore.jks gerekir)"
            echo "  --skip-vps    VPS'e yüklemeyi atla"
            echo "  --build-only  Sadece derle, bir yere yükleme"
            exit 0
            ;;
        *) log_error "Bilinmeyen seçenek: $1"; exit 1 ;;
    esac
done

echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║         📱 MathLock Android Deploy                    ║${NC}"
echo -e "${CYAN}║         Build: ${BUILD_TYPE}                                 ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"

cd "$PROJECT_DIR"

# ─── 0. Versiyon otomatik artırma ────────────────────────────────────────────
GRADLE_FILE="$PROJECT_DIR/app/build.gradle.kts"
CURRENT_CODE=$(grep 'versionCode\s*=' "$GRADLE_FILE" | grep -o '[0-9]\+')
NEW_CODE=$((CURRENT_CODE + 1))
NEW_NAME="1.${NEW_CODE}"
sed -i "s/versionCode = ${CURRENT_CODE}/versionCode = ${NEW_CODE}/" "$GRADLE_FILE"
sed -i "s/versionName = \"[^\"]*\"/versionName = \"${NEW_NAME}\"/" "$GRADLE_FILE"
log_info "Versiyon: ${CURRENT_CODE} → ${NEW_CODE} (v${NEW_NAME})"

# ─── Release keystore kontrolü ───────────────────────────────────────────────
if [[ "$BUILD_TYPE" == "release" ]]; then
    if [ ! -f "keystore.jks" ]; then
        log_error "keystore.jks bulunamadı!"
        echo ""
        echo "  Release APK için önce bir keystore oluştur:"
        echo "  keytool -genkeypair -v \\"
        echo "    -keystore keystore.jks \\"
        echo "    -keyalg RSA -keysize 2048 -validity 10000 \\"
        echo "    -alias mathlock \\"
        echo "    -storepass <şifre> -keypass <şifre>"
        echo ""
        echo "  Ardından app/build.gradle.kts dosyasına signing config ekle."
        echo "  Şimdilik --release yerine debug kullanılabilir."
        exit 1
    fi
fi

# ─── 1. Derleme ─────────────────────────────────────────────────────────────
echo -e "\n${YELLOW}[1/3] 🔨 APK derleniyor (${BUILD_TYPE})...${NC}"

GRADLE_TASK="assemble$(echo "${BUILD_TYPE^}")"
./gradlew "$GRADLE_TASK" --no-daemon 2>&1 | grep -E "(BUILD|ERROR|error:|warning:|WARN|Task :)" || true

# APK yolunu bul
if [[ "$BUILD_TYPE" == "release" ]]; then
    APK_PATH="app/build/outputs/apk/release/app-release.apk"
    # unsigned release de olabilir
    if [ ! -f "$APK_PATH" ]; then
        APK_PATH="app/build/outputs/apk/release/app-release-unsigned.apk"
    fi
else
    APK_PATH="app/build/outputs/apk/debug/app-debug.apk"
fi

if [ ! -f "$APK_PATH" ]; then
    log_error "APK bulunamadı: $APK_PATH"
    exit 1
fi

# output-metadata.json'dan versionCode/versionName oku
METADATA_FILE="app/build/outputs/apk/${BUILD_TYPE}/output-metadata.json"
VERSION_CODE=1
VERSION_NAME="1.0"
if [ -f "$METADATA_FILE" ]; then
    VERSION_CODE=$(python3 -c "import json; d=json.load(open('$METADATA_FILE')); print(d['elements'][0]['versionCode'])" 2>/dev/null || echo "1")
    VERSION_NAME=$(python3 -c "import json; d=json.load(open('$METADATA_FILE')); print(d['elements'][0]['versionName'])" 2>/dev/null || echo "1.0")
fi

APK_SIZE=$(du -sh "$APK_PATH" | cut -f1)
log_success "APK hazır: $APK_PATH ($APK_SIZE) — v${VERSION_NAME} (code: ${VERSION_CODE})"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
APK_VERSIONED="app-mathlock-${BUILD_TYPE}-${TIMESTAMP}.apk"

# ─── version.json oluştur (OTA güncellemesi için) ───────────────────────────
VERSION_JSON=$(cat <<EOF
{
  "versionCode": ${VERSION_CODE},
  "versionName": "${VERSION_NAME}",
  "buildType": "${BUILD_TYPE}",
  "buildTime": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "apkUrl": "http://89.252.152.222/mathlock/dist/mathlock-latest.apk",
  "releaseNotes": ""
}
EOF
)

# ─── 2. Telefona ADB kurulumu ────────────────────────────────────────────────
if [ "$SKIP_ADB" = false ]; then
    echo -e "\n${YELLOW}[2/3] 📱 Telefona kuruluyor (ADB)...${NC}"

    # ADB mevcut mu?
    if ! command -v adb &>/dev/null; then
        log_warning "adb komutu bulunamadı. Android SDK platform-tools PATH'de olmalı."
        log_warning "ADB yükleme atlanıyor."
    else
        # Bağlı cihaz var mı?
        DEVICES=$(adb devices | grep -v "List of devices" | grep "device$" | wc -l)
        if [ "$DEVICES" -eq 0 ]; then
            log_warning "Bağlı telefon bulunamadı."
            log_warning "Telefonu USB ile bağlayın ve USB hata ayıklamayı açın."
            log_warning "ADB yükleme atlanıyor."
        else
            log_info "Bağlı cihaz sayısı: $DEVICES"
            adb install -r "$APK_PATH" && log_success "Telefona kuruldu!"
        fi
    fi
else
    echo -e "\n${YELLOW}[2/3] ⏭️  ADB kurulum atlandı${NC}"
fi

# ─── 3. VPS'e yükleme + OTA güncelleme manifest ─────────────────────────────
if [ "$SKIP_VPS" = false ]; then
    echo -e "\n${YELLOW}[3/3] 🚀 VPS'e yükleniyor (OTA)...${NC}"

    # VPS dist dizinini hazırla
    ssh "$VPS_HOST" "mkdir -p ${VPS_DIST_PATH}"

    # APK'yı timestamplı yükle, sonra latest olarak linkle
    scp "$APK_PATH" "${VPS_HOST}:${VPS_DIST_PATH}/${APK_VERSIONED}"
    ssh "$VPS_HOST" "cp ${VPS_DIST_PATH}/${APK_VERSIONED} ${VPS_DIST_PATH}/mathlock-latest.apk"

    # version.json'ı yükle (telefon bunu kontrol eder → yeni sürüm varsa APK indirir)
    echo "$VERSION_JSON" | ssh "$VPS_HOST" "cat > ${VPS_DIST_PATH}/version.json"
    log_success "version.json yüklendi: v${VERSION_NAME} (code: ${VERSION_CODE})"

    # Eski APK'ları temizle (son 5 tane kalsın)
    ssh "$VPS_HOST" "cd ${VPS_DIST_PATH} && ls -t app-mathlock-*.apk 2>/dev/null | tail -n +6 | xargs -r rm -f"

    log_success "APK yüklendi: ${VPS_DIST_PATH}/${APK_VERSIONED}"

    # ─── Data dosyalarını sync et (questions.json, topics.json) ──────────────
    DATA_SYNC_DIR="$PROJECT_DIR/data"
    VPS_DATA_DIR="/home/akn/vps/projects/mathlock/data"
    if [ -d "$DATA_SYNC_DIR" ]; then
        ssh "$VPS_HOST" "mkdir -p ${VPS_DATA_DIR}"
        if [ -f "$DATA_SYNC_DIR/questions.json" ]; then
            scp "$DATA_SYNC_DIR/questions.json" "${VPS_HOST}:${VPS_DATA_DIR}/questions.json"
            log_success "questions.json VPS'e senkronize edildi"
        fi
        if [ -f "$DATA_SYNC_DIR/topics.json" ]; then
            scp "$DATA_SYNC_DIR/topics.json" "${VPS_HOST}:${VPS_DATA_DIR}/topics.json"
            log_success "topics.json VPS'e senkronize edildi"
        fi
    fi

    # nginx'i reload et (mathlock.conf zaten repoda var, nginx container'ı yenile)
    # Önce conf'u VPS'e kopyala (conf.d volume host'tan mount edilir)
    MATHLOCK_CONF_LOCAL="/home/akn/vps/infrastructure/nginx/conf.d/mathlock.conf"
    if [ -f "$MATHLOCK_CONF_LOCAL" ]; then
        scp "$MATHLOCK_CONF_LOCAL" "${VPS_HOST}:/home/akn/vps/infrastructure/nginx/conf.d/mathlock.conf" 2>/dev/null && \
            log_success "mathlock.conf VPS'e kopyalandı" || log_warning "mathlock.conf kopyalanamadı"
    fi
    NGINX_RELOAD=$(ssh "$VPS_HOST" "docker exec vps_nginx_main nginx -s reload 2>&1 || true")
    log_info "nginx reload: ${NGINX_RELOAD:-ok}"

    # Sağlık kontrolü (Host header ile — server_name 89.x.x.x ile eşleşmeli)
    sleep 1
    HEALTH=$(ssh "$VPS_HOST" "curl -sf -H 'Host: 89.252.152.222' http://localhost/mathlock/health 2>/dev/null || echo 'FAIL'")
    if [ "$HEALTH" = "mathlock ok" ]; then
        log_success "OTA endpoint sağlıklı: /mathlock/health"
    else
        log_warning "OTA endpoint yanıt vermedi"
    fi

    echo ""
    echo -e "${CYAN}OTA Güncelleme Endpoint'leri:${NC}"
    echo -e "  📋 Versiyon : http://89.252.152.222/mathlock/dist/version.json"
    echo -e "  📦 Son APK  : http://89.252.152.222/mathlock/dist/mathlock-latest.apk"
    echo -e "  📦 Bu APK   : http://89.252.152.222/mathlock/dist/${APK_VERSIONED}"
    echo -e "  ❤️  Sağlık  : http://89.252.152.222/mathlock/health"
    echo -e "  📊 Sorular  : http://89.252.152.222/mathlock/data/questions.json"
    echo -e "  📚 Konular  : http://89.252.152.222/mathlock/data/topics.json"
else
    echo -e "\n${YELLOW}[3/3] ⏭️  VPS yükleme atlandı${NC}"
fi

# ─── Özet ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✅ Deploy tamamlandı!                    ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}APK:${NC}      $APK_PATH ($APK_SIZE)"
echo -e "${BLUE}Sürüm:${NC}    v${VERSION_NAME} (versionCode: ${VERSION_CODE})"
echo -e "${BLUE}Build:${NC}    ${BUILD_TYPE}"
[ "$SKIP_ADB" = false ] && echo -e "${BLUE}Telefon:${NC}  ADB kurulumu denendi"
[ "$SKIP_VPS" = false ] && echo -e "${BLUE}VPS:${NC}      ${VPS_HOST}:${VPS_DIST_PATH}"
echo ""
echo -e "${CYAN}OTA Akışı:${NC}"
echo -e "  1. Değişiklik yap"
echo -e "  2. ./deploy.sh çalıştır  (versionCode otomatik artar)"
echo -e "  3. Telefon uygulamayı açtığında version.json kontrol eder"
echo -e "  4. Yeni sürüm varsa 'Güncelle' dialog'u çıkar → otomatik indirir ve kurar"
