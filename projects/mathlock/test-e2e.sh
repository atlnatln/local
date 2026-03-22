#!/bin/bash
# ============================================================================
# MathLock - Uçtan Uca (E2E) Test Scripti
#
# Telefon USB ile bağlı olmalı. USB hata ayıklama açık olmalı.
#
# Kullanım:
#   ./test-e2e.sh                  # Tüm testler
#   ./test-e2e.sh timer            # Sadece timer testi
#   ./test-e2e.sh bypass           # Sadece ebeveyn bypass testi
#   ./test-e2e.sh foreground       # getForegroundPackage testi
# ============================================================================

set -e

ADB="/home/akn/Android/Sdk/platform-tools/adb"
PKG="com.akn.mathlock"
TEST_PKG="com.opera.browser"   # kilitlenecek uygulama
PREFS_FILE="/data/data/$PKG/shared_prefs/mathlock_prefs.xml"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

PASS=0
FAIL=0

pass() { echo -e "${GREEN}[PASS]${NC} $1"; ((PASS++)); }
fail() { echo -e "${RED}[FAIL]${NC} $1"; ((FAIL++)); }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
section() { echo -e "\n${CYAN}═══ $1 ═══${NC}"; }

# ─── Yardımcılar ────────────────────────────────────────────────────────────

check_device() {
    if ! $ADB devices | grep -q "device$"; then
        echo -e "${RED}HATA: Cihaz bulunamadı. USB bağlantısını ve hata ayıklama iznini kontrol edin.${NC}"
        exit 1
    fi
    DEVICE_MODEL=$($ADB shell getprop ro.product.model 2>/dev/null | tr -d '\r')
    info "Cihaz: $DEVICE_MODEL"
}

read_prefs() {
    $ADB shell "run-as $PKG cat $PREFS_FILE" 2>/dev/null
}

get_pref_int() {
    local key="$1"
    read_prefs | grep "name=\"$key\"" | sed 's/.*value="\([^"]*\)".*/\1/' | tr -d '\r'
}

get_pref_string() {
    local key="$1"
    read_prefs | grep "name=\"$key\"" | sed 's/.*>\(.*\)<\/string>/\1/' | tr -d '\r'
}

get_foreground() {
    $ADB shell "dumpsys activity activities 2>/dev/null | grep 'mResumedActivity' | head -1" | \
        grep -o '[a-z]\+\.[a-z.]\+' | head -1
}

get_logcat_service() {
    $ADB logcat -d 2>/dev/null | grep "AppLockService" | tail -20
}

clear_logcat() {
    $ADB logcat -c 2>/dev/null
}

open_app() {
    local pkg="$1"
    $ADB shell "monkey -p $pkg -c android.intent.category.LAUNCHER 1" &>/dev/null
    sleep 2
}

go_home() {
    $ADB shell input keyevent KEYCODE_HOME
    sleep 1
}

is_challenge_showing() {
    # ChallengePickerActivity veya MathChallengeActivity ön planda mı?
    $ADB shell "dumpsys activity activities 2>/dev/null | grep 'mResumedActivity'" | \
        grep -q "mathlock" && echo "yes" || echo "no"
}

is_app_foreground() {
    local pkg="$1"
    $ADB shell "dumpsys activity activities 2>/dev/null | grep 'mResumedActivity'" | \
        grep -q "$pkg" && echo "yes" || echo "no"
}

# ─── Test: Servis Çalışıyor Mu ───────────────────────────────────────────────

test_service_running() {
    section "Servis Kontrolü"
    local running
    running=$($ADB shell "dumpsys activity services $PKG 2>/dev/null | grep 'AppLockService'" | wc -l | tr -d ' ')
    if [[ "$running" -gt 0 ]]; then
        pass "AppLockService çalışıyor"
    else
        fail "AppLockService çalışmıyor"
        warn "MathLock uygulamasını açıp korumayı etkinleştirin"
    fi
}

# ─── Test: Ayarlar Okunabiliyor Mu ──────────────────────────────────────────

test_prefs_readable() {
    section "Ayarlar Testi"
    local prefs
    prefs=$(read_prefs 2>&1)
    if echo "$prefs" | grep -q "unlock_duration_minutes"; then
        pass "Shared preferences okunabildi"
        
        local duration locked_apps action
        duration=$(get_pref_int "unlock_duration_minutes")
        action=$(get_pref_string "unlock_expired_action")
        
        info "unlock_duration_minutes = $duration"
        info "unlock_expired_action   = $action"
        
        if [[ "$duration" -gt 0 ]]; then
            pass "Timer aktif ($duration dakika)"
        else
            warn "Timer devre dışı (unlock_duration_minutes=0) — timer testi atlanacak"
        fi
    else
        fail "Shared preferences okunamadı"
        info "Çıktı: $prefs"
    fi
}

# ─── Test: Kilit Açık Uydeğ Erişim ─────────────────────────────────────────

test_timer_expiry() {
    section "Timer Test (Kısa Süre)"
    
    local duration
    duration=$(get_pref_int "unlock_duration_minutes")
    
    if [[ "$duration" -le 0 ]]; then
        warn "Timer devre dışı — test atlandı. Ayarlardan 1 dakika ayarlayın."
        return
    fi
    
    if [[ "$duration" -gt 2 ]]; then
        warn "Timer $duration dakika — bu test 1-2 dakika için tasarlandı."
        warn "Ayarlardan 1 dakika ayarlayıp tekrar çalıştırın."
        return
    fi
    
    info "Test paketi: $TEST_PKG"
    info "Timer süresi: $duration dk"
    
    # Uygulama yüklü mü?
    if ! $ADB shell "pm list packages 2>/dev/null | grep $TEST_PKG" | grep -q "$TEST_PKG"; then
        warn "$TEST_PKG yüklü değil — timer testi atlanıyor"
        warn "Test için birkaç kilitli uygulama seçin"
        return
    fi
    
    # Kilitli mi?
    local prefs_content
    prefs_content=$(read_prefs)
    if ! echo "$prefs_content" | grep -q "$TEST_PKG"; then
        warn "$TEST_PKG kilitli değil — test atlanıyor"
        warn "MathLock ayarlarından $TEST_PKG'yi kilitleyin"
        return
    fi
    
    info "Logcat temizleniyor..."
    clear_logcat
    
    info "Opera açılıyor..."
    open_app "$TEST_PKG"
    sleep 2
    
    local challenge_initial
    challenge_initial=$(is_challenge_showing)
    if [[ "$challenge_initial" == "yes" ]]; then
        info "Challenge ekranı göründü (beklenen davranış)"
        warn "Challenge'ı tamamlamanız gerekiyor — bu adımı otomatikleştiremiyoruz"
        warn "Challenge tamamlandıktan sonra bu testi tekrar çalıştırın"
        info "Bekleniyor: ${duration} dakikadan fazla..."
        echo "Challenge tamamlandıktan ENTER'a basın:"
        read -r
    fi
    
    local wait_seconds=$(( duration * 60 + 15 ))
    info "Timer bekleniyor: $wait_seconds saniye..."
    
    for ((i=wait_seconds; i>0; i-=10)); do
        echo -ne "\r  Kalan: ${i}s  "
        sleep 10
    done
    echo ""
    
    # Şimdi challenge tekrar görünmeli (relock modunda)
    local challenge_after
    challenge_after=$(is_challenge_showing)
    
    # Logcat kontrol
    local timer_log
    timer_log=$($ADB logcat -d 2>/dev/null | grep "Timer doldu\|forceRelock\|Challenge activity" | tail -5)
    
    if [[ "$challenge_after" == "yes" ]]; then
        pass "Timer sonrası challenge ekranı göründü ✓"
    else
        # Kullanıcı zaten oraya bakıyor olmayabilir
        if [[ -n "$timer_log" ]]; then
            pass "Timer logcatta görüldü (challenge tetiklendi)"
            info "Log: $timer_log"
        else
            fail "Timer sonrası challenge görünmedi"
            info "Logcat (son 20 satır AppLockService):"
            get_logcat_service
        fi
    fi
}

# ─── Test: Ebeveyn Bypass ────────────────────────────────────────────────────

test_parent_bypass() {
    section "Ebeveyn Bypass Testi"
    
    warn "Bu test manuel müdahale gerektiriyor."
    info "Adımlar:"
    info "  1. Kilitli uygulamayı açın → challenge görünmeli"
    info "  2. 'Ebeveyn' butonuna basın → PIN/parmak izi girin"
    info "  3. Uygulama doğrudan açılmalı (challenge olmadan)"
    info "  4. Timer varsa ve dolduysa bile ebeveyn tekrar açabilmeli"
    echo ""
    echo "Adımları tamamlayın ve uygulamanın açılıp açılmadığını kontrol edin."
    echo "Uygulama açıldı mı? (e/h): "
    read -r answer
    
    if [[ "$answer" == "e" || "$answer" == "E" ]]; then
        pass "Ebeveyn bypass çalışıyor"
    else
        fail "Ebeveyn bypass çalışmıyor — loglara bakın"
        get_logcat_service
    fi
}

# ─── Test: getForegroundPackage ──────────────────────────────────────────────

test_foreground_detection() {
    section "Ön Plan Tespit Testi"
    
    if ! $ADB shell "pm list packages 2>/dev/null | grep $TEST_PKG" | grep -q "$TEST_PKG"; then
        warn "$TEST_PKG yüklü değil — ön plan testi atlanıyor"
        return
    fi
    
    info "Opera açılıyor..."
    open_app "$TEST_PKG"
    sleep 3  # 3 saniye bekle
    
    local fg_activity
    fg_activity=$($ADB shell "dumpsys activity activities 2>/dev/null | grep 'mResumedActivity' | head -1" | tr -d '\r')
    info "Ön plan (Activity Manager): $fg_activity"
    
    if echo "$fg_activity" | grep -q "$TEST_PKG"; then
        pass "Activity Manager $TEST_PKG'yi ön planda görüyor ✓"
    else
        fail "Activity Manager $TEST_PKG'yi ön planda görmüyor"
    fi
    
    # 10 saniye bekle ve tekrar kontrol (lastKnownForeground testi)
    info "10 saniye bekleniyor (servis 5s'lik UsageEvents penceresini aşsın)..."
    sleep 10
    
    fg_activity=$($ADB shell "dumpsys activity activities 2>/dev/null | grep 'mResumedActivity' | head -1" | tr -d '\r')
    if echo "$fg_activity" | grep -q "$TEST_PKG"; then
        pass "10 saniye sonra hâlâ ön planda görünüyor ✓"
        info "lastKnownForegroundPackage düzeltmesiyle timer tetiklenir"
    fi
    
    go_home
}

# ─── Test: Crash Yok Mu ──────────────────────────────────────────────────────

test_no_crashes() {
    section "Crash Kontrolü"
    
    local crashes
    crashes=$($ADB logcat -d 2>/dev/null | grep "FATAL EXCEPTION\|Process: $PKG" | wc -l | tr -d ' ')
    
    if [[ "$crashes" -gt 0 ]]; then
        fail "Crash bulundu ($crashes adet)"
        $ADB logcat -d 2>/dev/null | grep -A 10 "FATAL EXCEPTION" | grep -A 10 "$PKG" | tail -20
    else
        pass "Crash yok ✓"
    fi
    
    # ANR kontrolü
    local anrs
    anrs=$($ADB logcat -d 2>/dev/null | grep "ANR in $PKG" | wc -l | tr -d ' ')
    if [[ "$anrs" -gt 0 ]]; then
        fail "ANR bulundu ($anrs adet)"
    else
        pass "ANR yok ✓"
    fi
}

# ─── Özet ────────────────────────────────────────────────────────────────────

print_summary() {
    echo ""
    echo "╔══════════════════════════════════════╗"
    echo "║           TEST SONUÇLARI             ║"
    echo "╠══════════════════════════════════════╣"
    echo -e "║  ${GREEN}PASS: $PASS${NC}                              ║"
    echo -e "║  ${RED}FAIL: $FAIL${NC}                              ║"
    echo "╚══════════════════════════════════════╝"
    if [[ "$FAIL" -gt 0 ]]; then
        exit 1
    fi
}

# ─── Ana Akış ────────────────────────────────────────────────────────────────

check_device

case "${1:-all}" in
    timer)      test_service_running; test_prefs_readable; test_timer_expiry ;;
    bypass)     test_service_running; test_parent_bypass ;;
    foreground) test_foreground_detection ;;
    crash)      test_no_crashes ;;
    all)
        test_service_running
        test_prefs_readable
        test_no_crashes
        test_foreground_detection
        echo ""
        warn "Timer ve bypass testleri manuel adım gerektirir."
        echo "Timer testini çalıştırmak ister misiniz? (e/h): "
        read -r run_timer
        [[ "$run_timer" == "e" || "$run_timer" == "E" ]] && test_timer_expiry
        ;;
    *)
        echo "Kullanım: $0 [all|timer|bypass|foreground|crash]"
        exit 1
        ;;
esac

print_summary
