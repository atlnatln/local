#!/bin/bash
set -e

LOCAL_DIR="/home/akn/local"
VPS_DIR="/home/akn/vps"

echo "=== VPS Dev Ortamı Kurulumu ==="
echo "Tarih: $(date)"

# 1. Yedek al
echo "[1/12] Mevcut VPS dizini yedekleniyor..."
tar czf "$HOME/vps-backup-$(date +%Y%m%d).tar.gz" "$VPS_DIR" 2>/dev/null || true

# 2. Git clone
echo "[2/12] GitHub'dan local repo çekiliyor..."
if [ ! -d "$LOCAL_DIR/.git" ]; then
    if [ -d "$LOCAL_DIR" ] && [ "$(ls -A $LOCAL_DIR)" ]; then
        mv "$LOCAL_DIR" "$LOCAL_DIR.backup.$(date +%s)"
    fi
    git clone https://github.com/atlnatln/local.git "$LOCAL_DIR"
fi

cd "$LOCAL_DIR"

# 3. Git config
echo "[3/12] Git config ayarlanıyor..."
git config user.name "VPS Developer"
git config user.email "vps@localhost"

# 4. Git auth
echo "[4/12] Git auth kontrolü..."
if [ -f "$HOME/.ssh/id_ed25519" ]; then
    git remote set-url origin git@github.com:atlnatln/local.git 2>/dev/null || true
    echo "  SSH key mevcut. Remote SSH olarak ayarlandı."
else
    echo "  UYARI: SSH key bulunamadı. HTTPS + token kullanılmalı."
    git config credential.helper store
fi

# 5. Python venv'leri
echo "[5/12] Python venv'leri kuruluyor..."
for proj in projects/telegram-kimi; do
    if [ -f "$proj/requirements.txt" ]; then
        echo "  → $proj"
        python3 -m venv "$proj/.venv" 2>/dev/null || true
        "$proj/.venv/bin/pip" install -q -r "$proj/requirements.txt" 2>/dev/null || true
    fi
done

# 6. Node.js
echo "[6/12] Node.js bağımlılıkları kuruluyor..."
for proj in projects/webimar/webimar-nextjs projects/anka/services/frontend; do
    if [ -f "$proj/package.json" ]; then
        echo "  → $proj"
        cd "$LOCAL_DIR/$proj"
        npm install --silent 2>/dev/null || true
    fi
done

# 7. Docker
echo "[7/12] Docker kontrolü..."
docker --version 2>/dev/null || echo "  UYARI: Docker kurulu değil."

# 8. Android SDK
echo "[8/12] Android SDK kontrolü..."
ANDROID_SDK_ROOT="$HOME/android-sdk"
if [ ! -d "$ANDROID_SDK_ROOT/cmdline-tools/latest" ]; then
    echo "  Android SDK kuruluyor..."
    mkdir -p "$ANDROID_SDK_ROOT"
    cd "$ANDROID_SDK_ROOT"
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip 2>/dev/null || true
    if [ -f commandlinetools-linux-*.zip ]; then
        unzip -q commandlinetools-linux-*.zip
        mkdir -p cmdline-tools/latest
        mv cmdline-tools/* cmdline-tools/latest/ 2>/dev/null || true
        yes | cmdline-tools/latest/bin/sdkmanager --licenses >/dev/null 2>&1 || true
        cmdline-tools/latest/bin/sdkmanager "platforms;android-34" "build-tools;34.0.0" >/dev/null 2>&1 || true
        echo "export ANDROID_SDK_ROOT=$ANDROID_SDK_ROOT" >> "$HOME/.bashrc"
        echo 'export PATH=$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$ANDROID_SDK_ROOT/platform-tools:$PATH' >> "$HOME/.bashrc"
        echo "  Android SDK kuruldu."
    else
        echo "  UYARI: Android SDK indirilemedi. Manuel kurulum gerekli."
    fi
else
    echo "  Android SDK zaten kurulu."
fi

# 9. Kimi CLI PATH
echo "[9/12] Kimi CLI PATH kontrolü..."
if ! grep -q "\.kimi/bin" "$HOME/.bashrc" 2>/dev/null; then
    echo 'export PATH="$HOME/.kimi/bin:$PATH"' >> "$HOME/.bashrc"
    echo "  Kimi CLI PATH eklendi."
fi

# 10. Wiki skill
echo "[10/12] Wiki skill symlink..."
mkdir -p "$HOME/.kimi/skills"
ln -sf "$LOCAL_DIR/.kimi/skills/local-wiki" "$HOME/.kimi/skills/local-wiki" 2>/dev/null || true

# 11. Git hooks
echo "[11/12] Git hooks kuruluyor..."
cd "$LOCAL_DIR"
ln -sf "$LOCAL_DIR/scripts/hooks/pre-commit" "$LOCAL_DIR/.git/hooks/pre-commit"
ln -sf "$LOCAL_DIR/scripts/hooks/pre-push" "$LOCAL_DIR/.git/hooks/pre-push"
ln -sf "$LOCAL_DIR/scripts/wiki-post-commit.sh" "$LOCAL_DIR/.git/hooks/post-commit"
echo "  → local: pre-commit, pre-push, post-commit"

# 12. Kimi CLI hooks
echo "[12/12] Kimi CLI hooks yapılandırılıyor..."
python3 << "PYEOF"
import pathlib

config_path = pathlib.Path.home() / ".kimi" / "config.toml"
if config_path.exists():
    content = config_path.read_text()
    old_hooks = "hooks = []"
    new_hooks = """[[hooks]]
event = "PreToolUse"
matcher = "WriteFile|StrReplaceFile"
command = "/home/akn/local/scripts/hooks/protect-env.sh"
timeout = 5

[[hooks]]
event = "PostToolUse"
matcher = "WriteFile|StrReplaceFile"
command = "/home/akn/local/scripts/hooks/wiki-auto-pending.sh"
timeout = 5

[[hooks]]
event = "Stop"
command = "/home/akn/local/scripts/hooks/wiki-lint-on-stop.sh"
timeout = 30"""
    if old_hooks in content:
        content = content.replace(old_hooks, new_hooks)
        config_path.write_text(content)
        print("  → Kimi CLI hooks güncellendi")
    else:
        print("  → UYARI: config.toml'da hooks = [] bulunamadı, manuel kontrol gerekli")
else:
    print("  → UYARI: ~/.kimi/config.toml bulunamadı")
PYEOF

echo ""
echo "=== Kurulum Tamamlandı ==="
echo "Geliştirme: $LOCAL_DIR"
echo "Deploy:     $VPS_DIR"
echo "Git remote: $(git remote get-url origin 2>/dev/null || echo 'AYARLANMADI')"
echo ""
echo "Sonraki adımlar:"
echo "  1. Yeni bir terminal açın (veya 'source ~/.bashrc' çalıştırın)"
echo "  2. cd $LOCAL_DIR"
echo "  3. git status"
