---
title: "ops-bot-deploy-script"
created: 2026-05-01
updated: 2026-05-01
type: raw
tags: [raw]
related: []
---


#!/bin/bash
# ========================================
# Ops-Bot Deploy Script
# Tek script ile VPS'e systemd service deploy
# ========================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
VPS_HOST="akn@89.252.152.222"
VPS_PATH="/home/akn/vps/ops-bot"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# SSH Multiplexing: tüm SSH/SCP komutları tek TCP bağlantısı üzerinden gider.
# Bu sayede UFW'nin SSH rate-limit kuralı (30sn'de 6+ bağlantı → geçici drop)
# deploy otomasyonunda tetiklenmez.
SSH_CONTROL_DIR="$(mktemp -d /tmp/ssh-deploy-XXXXXX)"
SSH_OPTS="-o ControlMaster=auto -o ControlPath=${SSH_CONTROL_DIR}/ctrl-%r@%h:%p -o ControlPersist=120"

# Override ssh/scp to use multiplexing options by default in this script
ssh() { command ssh $SSH_OPTS "$@"; }
scp() { command scp $SSH_OPTS "$@"; }

# Cleanup multiplexing socket on exit
trap 'command ssh -O exit -o ControlPath="${SSH_CONTROL_DIR}/ctrl-%r@%h:%p" "$VPS_HOST" 2>/dev/null; rm -rf "$SSH_CONTROL_DIR"' EXIT

# Parse arguments
SKIP_BUILD=false
SKIP_VPS=false
SKIP_GITHUB=false
DEPLOY_MODE="package"  # package (default) | git

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-build) SKIP_BUILD=true; shift ;;
        --skip-vps) SKIP_VPS=true; shift ;;
        --skip-github) SKIP_GITHUB=true; shift ;;
        --mode)
            DEPLOY_MODE="${2:-}"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --skip-build    Skip package build step"
            echo "  --skip-vps      Skip VPS deployment"
            echo "  --skip-github   Skip GitHub push"
            echo "  --mode <package|git>  Deploy mode:"
            echo "       package: create tar.gz package and scp to VPS (default)"
            echo "       git: VPS repo 'git pull' + systemctl restart"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

if [[ "$DEPLOY_MODE" != "package" && "$DEPLOY_MODE" != "git" ]]; then
    echo -e "${RED}❌ Invalid --mode: ${DEPLOY_MODE} (use: package|git)${NC}"
    exit 1
fi

echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║       Ops-Bot Deploy Script v1.0       ║${NC}"
echo -e "${CYAN}║       VPS Systemd Service Deploy       ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"

cd "$PROJECT_DIR"

# Env check
require_file() {
    local path="$1"
    local hint="$2"
    if [ ! -f "$path" ]; then
        echo -e "${RED}❌ Missing required file: ${path}${NC}"
        [ -n "$hint" ] && echo -e "   ${YELLOW}${hint}${NC}"
        exit 1
    fi
}

warn_file() {
    local path="$1"
    local hint="$2"
    if [ ! -f "$path" ]; then
        echo -e "${YELLOW}⚠️  Missing optional file: ${path}${NC}"
        [ -n "$hint" ] && echo -e "   ${YELLOW}${hint}${NC}"
    fi
}

# Preflight checks
if [[ "$DEPLOY_MODE" == "package" ]]; then
    require_file "requirements.txt" "Python dependencies file required"
    require_file "agent.py" "Main agent file required"
    require_file "report-audit.sh" "Audit report wrapper required (used by systemd oneshot)"
    warn_file ".env.production" "Create production environment file (copy from .env.example)"
fi

# Step 1: Build package (if not skipped)
if [ "$SKIP_BUILD" = false ]; then
    echo -e "\n${YELLOW}[1/4] 📦 Creating deployment package...${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BUILD_DIR="${PROJECT_DIR}/.deploy-tmp"
    rm -rf "$BUILD_DIR" && mkdir -p "$BUILD_DIR"

    if [[ "$DEPLOY_MODE" == "package" ]]; then
        # Copy Python source files
        cp -r *.py "$BUILD_DIR/" 2>/dev/null || true
        cp -r *.sh "$BUILD_DIR/" 2>/dev/null || true
        cp requirements.txt "$BUILD_DIR/"
        cp -r .github "$BUILD_DIR/" 2>/dev/null || true
        cp -r systemd "$BUILD_DIR/" 2>/dev/null || true
        cp -r scripts "$BUILD_DIR/" 2>/dev/null || true
        cp -r bin "$BUILD_DIR/" 2>/dev/null || true
        cp -r sec-agent "$BUILD_DIR/" 2>/dev/null || true
        echo -e "${GREEN}  ✓ Included sec-agent directory${NC}"
        
        # Copy production env as a reference file (do NOT overwrite VPS .env by default)
        if [ -f ".env.production" ]; then
            cp .env.production "$BUILD_DIR/.env.production"
            echo -e "${GREEN}  ✓ Included .env.production (will not overwrite existing VPS .env)${NC}"
        else
            echo -e "${YELLOW}  ⚠️  No .env.production found (OK if VPS already has .env)${NC}"
        fi

        # Create VPS deploy script
        cat > "$BUILD_DIR/setup.sh" << 'SETUP_SCRIPT'
#!/bin/bash
set -e
echo "🤖 Ops-Bot VPS Deployment"

        # Keep existing VPS .env (secrets). Only create .env from .env.production if missing.
        if [ -f .env ]; then
            cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
            echo "📄 Backed up existing .env"
        else
            if [ -f .env.production ]; then
                cp .env.production .env
                echo "📄 Created .env from .env.production"
            else
                echo "⚠️  No .env present and no .env.production provided"
            fi
        fi

# Setup Python virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p data logs

# Setup systemd service
if [ -f "systemd/ops-bot.service" ]; then
    echo "📋 Installing systemd service..."
    sudo cp systemd/ops-bot.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable ops-bot
fi

# Install oneshot audit report service (timer is intentionally disabled/removed)
if [ -f "systemd/ops-bot-audit-report.service" ]; then
    echo "📋 Installing ops-bot-audit-report.service (timer disabled)..."
    sudo cp systemd/ops-bot-audit-report.service /etc/systemd/system/
fi

# Install critical security alert service + timer
if [ -f "systemd/ops-bot-critical-alert.service" ]; then
    echo "📋 Installing ops-bot-critical-alert.service..."
    sudo cp systemd/ops-bot-critical-alert.service /etc/systemd/system/
fi
if [ -f "systemd/ops-bot-critical-alert.timer" ]; then
    echo "📋 Installing ops-bot-critical-alert.timer..."
    sudo cp systemd/ops-bot-critical-alert.timer /etc/systemd/system/
fi

# Disable/remove legacy hourly timers (explicitly cancelled)
echo "⏰ Disabling hourly timers (cancelled)..."
sudo systemctl disable --now ops-bot-audit-report.timer 2>/dev/null || true
sudo systemctl disable --now ops-bot-hourly-audit.timer 2>/dev/null || true
sudo rm -f /etc/systemd/system/ops-bot-audit-report.timer /etc/systemd/system/ops-bot-hourly-audit.timer /etc/systemd/system/ops-bot-hourly-audit.service 2>/dev/null || true
sudo systemctl daemon-reload

# Stop existing service
sudo systemctl stop ops-bot 2>/dev/null || true

# Reload systemd configuration after copying updated service file
sudo systemctl daemon-reload

# Ensure low-noise critical alert timer is enabled with current unit definitions
if [ -f "/etc/systemd/system/ops-bot-critical-alert.timer" ]; then
    sudo systemctl enable --now ops-bot-critical-alert.timer
fi

# Start the service
echo "🚀 Starting ops-bot service..."
sudo systemctl start ops-bot

# ── sec-agent güncelleme ──────────────────────────────────────────────────────
if [ -d "sec-agent" ]; then
    echo ""
    echo "🔒 sec-agent güncellemesi /opt/sec-agent → başlıyor..."
    echo "⏸️  sec-agent timer/service geçici olarak durduruluyor..."
    sudo systemctl stop sec-agent.timer sec-agent-whitelist.timer sec-agent-once.service sec-agent-whitelist.service 2>/dev/null || true
    sudo mkdir -p /opt/sec-agent
    sudo chown -R akn:akn /opt/sec-agent

    # Kod klasörlerini güncelle (store/ logs/ runtime/ korunur — canlı veri)
    for dir in actions collectors config docs engine explainability normalizers bin tests; do
        if [ -d "sec-agent/$dir" ]; then
            cp -r "sec-agent/$dir" /opt/sec-agent/
        fi
    done
    # Kök dosyaları
    cp sec-agent/*.md /opt/sec-agent/ 2>/dev/null || true
    chmod +x /opt/sec-agent/bin/* 2>/dev/null || true
    # Root çalışan servis, kullanıcı-yazılabilir kod ağacından doğrudan çalışmamalı.
    # Çalışma verisi (store/logs/runtime) hariç kodu yeniden root sahipliğine al.
    sudo chown -R root:root \
        /opt/sec-agent/actions \
        /opt/sec-agent/collectors \
        /opt/sec-agent/docs \
        /opt/sec-agent/engine \
        /opt/sec-agent/explainability \
        /opt/sec-agent/normalizers \
        /opt/sec-agent/tests \
        /opt/sec-agent/bin 2>/dev/null || true
    sudo chown root:root /opt/sec-agent/*.md 2>/dev/null || true
    sudo chown -R akn:akn /opt/sec-agent/config /opt/sec-agent/store /opt/sec-agent/logs /opt/sec-agent/runtime 2>/dev/null || true

    # systemd unit'lerini kur: kaynak limitli oneshot + timer
    if [ -f "systemd/sec-agent-once.service" ]; then
        sudo cp systemd/sec-agent-once.service /etc/systemd/system/
    fi
    if [ -f "systemd/sec-agent.timer" ]; then
        sudo cp systemd/sec-agent.timer /etc/systemd/system/
    fi
    # Whitelist otomatik güncelleme timer'ı
    if [ -f "systemd/sec-agent-whitelist.service" ]; then
        sudo cp systemd/sec-agent-whitelist.service /etc/systemd/system/
    fi
    if [ -f "systemd/sec-agent-whitelist.timer" ]; then
        sudo cp systemd/sec-agent-whitelist.timer /etc/systemd/system/
    fi

    # ip_state sifirla: eski 'automation' bazli yanlış skorlar temizlenir.
    # Gercek saldirganlari birkaç döngüde yeniden yakalar (false positive önlemi).
    # NOT: Bu adım SEC_AGENT_RESET_STATE=true ile manuel olarak aktif edilebilir.
    if [ "${SEC_AGENT_RESET_STATE:-false}" = "true" ]; then
        if [ -f /opt/sec-agent/store/ip_state.json ]; then
            cp /opt/sec-agent/store/ip_state.json \
               "/opt/sec-agent/store/ip_state.json.bak-$(date +%Y%m%d_%H%M%S)"
            echo '{}' > /opt/sec-agent/store/ip_state.json
        fi
        if [ -f /opt/sec-agent/store/sec_agent.db ]; then
            cp /opt/sec-agent/store/sec_agent.db \
               "/opt/sec-agent/store/sec_agent.db.bak-$(date +%Y%m%d_%H%M%S)"
            rm -f /opt/sec-agent/store/sec_agent.db
        fi
        echo "🔄 sec-agent state sıfırlandı (JSON + SQLite yedeklendi)"
    fi

    # Legacy daemon servisini kapat; timer tabanlı kaynak güvenli modeli aktif et
    sudo systemctl disable --now sec-agent.service 2>/dev/null || true
    sudo systemctl daemon-reload
    sudo systemctl enable --now sec-agent.timer
    sudo systemctl enable --now sec-agent-whitelist.timer

    # Manuel bir kez çalıştırarak deploy'u doğrula
    echo "🔄 sec-agent tek seferlik test çalıştırması yapılıyor..."
    sudo systemctl start sec-agent-once.service
    sleep 2
    sudo systemctl status sec-agent-once.service --no-pager | head -12 || true
    sudo systemctl status sec-agent.timer --no-pager | head -12 || true
    sudo systemctl status sec-agent-whitelist.timer --no-pager | head -8 || true
    echo "✅ sec-agent timer modeli güncellendi"
else
    echo "⚠️  sec-agent dizini pakette yok, atlanıyor"
fi
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo "✅ Deployment complete!"
sudo systemctl status ops-bot --no-pager
SETUP_SCRIPT
        chmod +x "$BUILD_DIR/setup.sh"

        # Create package
        echo -e "  → Creating deployment package..."
        cd "$BUILD_DIR"
        # exit code 1 = "file changed as we read it" (tar uyarisi, fatal degil)
        tar -czf ops-bot-deploy.tar.gz \
            --exclude='ops-bot-deploy.tar.gz' \
            --exclude='sec-agent/store' \
            --exclude='sec-agent/logs' \
            --exclude='sec-agent/runtime' \
            --exclude='sec-agent/.pytest_cache' \
            . || { code=$?; [ $code -eq 1 ] && echo "  (uyari: bazi dosyalar okuma sirasinda degisti, sorun degil)" || exit $code; }
        cd "$PROJECT_DIR"
    fi
else
    echo -e "\n${YELLOW}[1/4] ⏭️  Skipping build (--skip-build)${NC}"
fi

# Step 2: Deploy to VPS
if [ "$SKIP_VPS" = false ]; then
    echo -e "\n${YELLOW}[2/4] 🚀 Deploying to VPS...${NC}"

    if [[ "$DEPLOY_MODE" == "package" ]]; then
        # Create remote directory
        ssh "$VPS_HOST" "mkdir -p $VPS_PATH"

        # Upload package
        echo -e "  → Uploading package to VPS..."
        scp "$BUILD_DIR/ops-bot-deploy.tar.gz" "$VPS_HOST:$VPS_PATH/"

        # Extract and deploy
        echo -e "  → Extracting and deploying..."
        ssh "$VPS_HOST" "cd $VPS_PATH && tar -xzf ops-bot-deploy.tar.gz && ./setup.sh"
    else
        # Git-based deploy
        echo -e "  → Running git pull + systemctl restart on VPS..."
        ssh "$VPS_HOST" "set -euo pipefail; cd $VPS_PATH; \
            if [ ! -d .git ]; then echo '❌ VPS_PATH is not a git repo. Clone the repo or use --mode package.'; exit 1; fi; \
            git fetch origin; \
            git reset --hard origin/main; \
            source venv/bin/activate; \
            pip install -r requirements.txt; \
            sudo systemctl restart ops-bot; \
            sudo systemctl status ops-bot --no-pager"
    fi

    echo -e "  ${GREEN}✅ VPS deployment complete${NC}"

    # VPS health check
    echo -e "\n${YELLOW}[2b] 🩺 Running VPS health checks...${NC}"
    ssh "$VPS_HOST" bash -s <<'HEALTH'
set -euo pipefail

echo "📊 Checking ops-bot service status..."
if sudo systemctl is-active ops-bot >/dev/null 2>&1; then
    echo "✅ ops-bot service is active"
    sudo systemctl status ops-bot --no-pager | head -10
else
    echo "❌ ops-bot service is not active"
    sudo journalctl -u ops-bot --no-pager -n 10
    exit 1
fi

echo "📋 Checking recent logs..."
sudo journalctl -u ops-bot --no-pager -n 5 --since "5 minutes ago" || true

echo "🛡️ Checking read-only security report runtime..."
if /home/akn/vps/ops-bot/venv/bin/python /home/akn/vps/ops-bot/scripts/system_security_report.py self-check; then
    echo "✅ system_security_report self-check passed"
else
    echo "❌ system_security_report self-check failed"
    exit 1
fi

echo "✅ Health checks complete"
HEALTH

else
    echo -e "\n${YELLOW}[2/4] ⏭️  Skipping VPS deployment (--skip-vps)${NC}"
fi

# Step 3: Push to GitHub
if [ "$SKIP_GITHUB" = false ]; then
    echo -e "\n${YELLOW}[3/4] 📤 Pushing to GitHub...${NC}"
    
    # Add changes
    git add .
    
    # Check if there are changes
    if git diff --staged --quiet; then
        echo -e "  ${BLUE}No changes to commit${NC}"
    else
        # Commit with timestamp
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        git commit -m "deploy: ops-bot update ${TIMESTAMP}"
        
        # Push to origin
        git push origin main
        
        echo -e "  ${GREEN}✅ GitHub push complete${NC}"
    fi
else
    echo -e "\n${YELLOW}[3/4] ⏭️  Skipping GitHub push (--skip-github)${NC}"
fi

# Step 4: Cleanup
echo -e "\n${YELLOW}[4/4] 🧹 Cleaning up...${NC}"
if [[ "$DEPLOY_MODE" == "package" ]]; then
    rm -rf "$BUILD_DIR"
fi

# Summary
echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Deployment Complete!           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo -e ""
echo -e "${BLUE}Summary:${NC}"
[ "$SKIP_BUILD" = false ] && echo -e "  ✅ Package created"
[ "$SKIP_VPS" = false ] && echo -e "  ✅ Deployed to VPS: ${VPS_HOST}"
[ "$SKIP_GITHUB" = false ] && echo -e "  ✅ Pushed to GitHub"
echo -e ""
echo -e "${CYAN}Service Status:${NC}"
echo -e "  🤖 Service: sudo systemctl status ops-bot"
echo -e "  📋 Logs: sudo journalctl -u ops-bot -f"
echo -e "  🔄 Restart: sudo systemctl restart ops-bot"
