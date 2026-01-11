#!/bin/bash
# ============================================================================
# Optimized VPS Directory FTP Backup System
# Full VPS directory backup with intelligent compression and FTP upload
# ============================================================================

set -euo pipefail

# Configuration
LOCAL_BACKUP_DIR="/home/akn/vps/backups"
VPS_ROOT="/home/akn/vps"
FTP_HOST="yedek1.guzelhosting.com"
FTP_USER="service-349231"
FTP_PASS="0FT5wcJK8X18"
FTP_DIR="/vps-full-backup"
DATE=$(date +%Y%m%d-%H%M%S)
RETENTION_DAYS=3    # Local retention shorter for full backups
FTP_RETENTION_DAYS=30

# Create backup directory
mkdir -p "$LOCAL_BACKUP_DIR"

echo "🔄 Starting optimized VPS full backup at $(date)"

# Function to upload to FTP
upload_to_ftp() {
    local file=$1
    local remote_name=$2
    
    echo "🌐 Uploading $(basename "$file") ($(du -h "$file" | cut -f1)) to FTP..."
    
    lftp -c "
        set ftp:list-options -a;
        set ftp:passive-mode true;
        set ssl:verify-certificate false;
        open -u $FTP_USER,$FTP_PASS $FTP_HOST;
        mkdir -p $FTP_DIR;
        cd $FTP_DIR;
        put '$file' -o '$remote_name';
        bye;
    " && echo "✅ Upload successful: $remote_name" || echo "❌ Upload failed: $remote_name"
}

# Install lftp if not present
if ! command -v lftp &> /dev/null; then
    echo "📦 Installing lftp..."
    sudo apt-get update && sudo apt-get install -y lftp
fi

# 1. Database backups (most critical)
echo "📦 Creating database backups..."
DB_BACKUP="$LOCAL_BACKUP_DIR/databases-$DATE.tar.gz"
{
    # Webimar DB
    if docker ps --format '{{.Names}}' | grep -q webimar-postgres; then
        echo "Backing up webimar database..."
        docker exec webimar-postgres pg_dump -U webimar webimar | gzip > /tmp/webimar-db.sql.gz
    fi
    
    # Anka DB (if running)
    if docker ps --format '{{.Names}}' | grep -q anka_postgres; then
        echo "Backing up anka database..."
        docker exec anka_postgres_prod pg_dump -U anka_user anka_prod | gzip > /tmp/anka-db.sql.gz
    fi
    
    # Create databases archive
    tar -czf "$DB_BACKUP" -C /tmp *.sql.gz 2>/dev/null || echo "Some databases may not exist"
    rm -f /tmp/*.sql.gz
}

upload_to_ftp "$DB_BACKUP" "databases-$DATE.tar.gz"

# 2. Critical configuration backup 
echo "📦 Creating configuration backup..."
CONFIG_BACKUP="$LOCAL_BACKUP_DIR/vps-config-$DATE.tar.gz"
tar -czf "$CONFIG_BACKUP" \
    -C "$VPS_ROOT" \
    --exclude="*/node_modules" \
    --exclude="*/logs" \
    --exclude="*/backups" \
    --exclude="*/.git" \
    --exclude="*/build" \
    --exclude="*/dist" \
    --exclude="*/__pycache__" \
    --exclude="*/staticfiles" \
    infrastructure/nginx/ \
    scripts/ \
    projects/*/docker-compose*.yml \
    projects/*/.env.example \
    projects/*/deploy.sh \
    projects/*/dev-*.sh \
    .github/ \
    *.md \
    2>/dev/null || echo "Some config files skipped"

upload_to_ftp "$CONFIG_BACKUP" "vps-config-$DATE.tar.gz"

# 3. Full VPS backup (weekly only - too large for daily)
if [ "$(date +%u)" -eq 7 ]; then  # Sunday
    echo "📦 Creating FULL VPS backup (weekly)..."
    FULL_BACKUP="$LOCAL_BACKUP_DIR/vps-full-$DATE.tar.gz"
    
    tar -czf "$FULL_BACKUP" \
        -C "$(dirname "$VPS_ROOT")" \
        --exclude="vps/backups" \
        --exclude="vps/*/node_modules" \
        --exclude="vps/*/.git" \
        --exclude="vps/*/build" \
        --exclude="vps/*/dist" \
        --exclude="vps/*/__pycache__" \
        --exclude="vps/*/staticfiles" \
        --exclude="vps/*/logs" \
        --exclude="vps/infrastructure/volumes" \
        "$(basename "$VPS_ROOT")"
    
    upload_to_ftp "$FULL_BACKUP" "vps-full-$DATE.tar.gz"
    echo "✅ Full backup: $(du -h "$FULL_BACKUP" | cut -f1)"
fi

# 4. Docker system information
echo "📦 Creating system state backup..."
SYSTEM_BACKUP="$LOCAL_BACKUP_DIR/system-state-$DATE.txt"
{
    echo "=== VPS System State - $DATE ==="
    echo ""
    echo "### Docker Containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}\t{{.Ports}}"
    echo ""
    echo "### Docker Images:"
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
    echo ""
    echo "### Docker Volumes:"
    docker volume ls --format "table {{.Name}}\t{{.Driver}}"
    echo ""
    echo "### Disk Usage:"
    df -h
    echo ""
    echo "### Network Ports:"
    ss -tulpn | grep LISTEN
    echo ""
    echo "### System Resources:"
    free -h
    echo ""
    echo "### Docker System Usage:"
    docker system df
} > "$SYSTEM_BACKUP"

upload_to_ftp "$SYSTEM_BACKUP" "system-state-$DATE.txt"

# Cleanup old local backups
echo "🧹 Cleaning up local backups older than $RETENTION_DAYS days..."
find "$LOCAL_BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete

# Cleanup old FTP backups
echo "🧹 Cleaning up FTP backups older than $FTP_RETENTION_DAYS days..."
lftp -c "
    set ftp:list-options -a;
    set ftp:passive-mode true;
    set ssl:verify-certificate false;
    open -u $FTP_USER,$FTP_PASS $FTP_HOST;
    cd $FTP_DIR;
    find . -type f -mtime +$FTP_RETENTION_DAYS -delete 2>/dev/null || true;
    bye;
" || echo "⚠️  FTP cleanup had issues (non-critical)"

# Final report
echo ""
echo "📊 === Optimized Backup Summary ==="
echo "🕐 Completed at: $(date)"
echo "📁 Local backups: $(du -sh "$LOCAL_BACKUP_DIR" | cut -f1)"
echo "🌐 FTP uploads completed"
echo ""
echo "📋 Recent local backups:"
ls -lht "$LOCAL_BACKUP_DIR" | head -5

echo "✅ Optimized VPS backup completed!"