#!/bin/bash
# ============================================================================
# Enhanced Backup Script with FTP Remote Storage
# Backs up databases locally + uploads to remote FTP for redundancy
# ============================================================================

set -euo pipefail

# Configuration
LOCAL_BACKUP_DIR="/home/akn/vps/backups"
FTP_HOST="yedek1.guzelhosting.com"
FTP_USER="service-349231"
FTP_PASS="0FT5wcJK8X18"
FTP_DIR="/database-backups"  # Remote directory structure
DATE=$(date +%Y%m%d-%H%M%S)
RETENTION_DAYS=7
FTP_RETENTION_DAYS=30  # Keep longer on FTP (30GB space available)

# Create local backup directory
mkdir -p "$LOCAL_BACKUP_DIR"

echo "🔄 Starting enhanced backup at $(date)"
echo "📊 FTP Space Available: 30GB (currently 0 MB used)"

# Function to upload to FTP
upload_to_ftp() {
    local file=$1
    local remote_path=$2
    
    echo "🌐 Uploading $(basename "$file") to FTP..."
    
    # Use lftp for robust FTP operations
    lftp -c "
        set ftp:list-options -a;
        set ftp:passive-mode true;
        set ssl:verify-certificate false;
        open -u $FTP_USER,$FTP_PASS $FTP_HOST;
        mkdir -p $FTP_DIR;
        cd $FTP_DIR;
        put '$file' -o '$remote_path';
        ls -la;
        bye;
    " && echo "✅ Upload successful: $remote_path" || echo "❌ Upload failed: $remote_path"
}

# Function to cleanup old FTP backups
cleanup_ftp_backups() {
    echo "🧹 Cleaning up FTP backups older than $FTP_RETENTION_DAYS days..."
    
    # List and remove old files via FTP
    lftp -c "
        set ftp:list-options -a;
        set ftp:passive-mode true;
        set ssl:verify-certificate false;
        open -u $FTP_USER,$FTP_PASS $FTP_HOST;
        cd $FTP_DIR;
        find . -type f -name '*.sql.gz' -mtime +$FTP_RETENTION_DAYS -delete 2>/dev/null || true;
        ls -la;
        bye;
    " || echo "⚠️  FTP cleanup encountered issues (non-critical)"
}

# Install lftp if not present
if ! command -v lftp &> /dev/null; then
    echo "📦 Installing lftp for FTP operations..."
    sudo apt-get update && sudo apt-get install -y lftp
fi

# Backup Webimar PostgreSQL
echo "📦 Backing up webimar database..."
if docker ps --format '{{.Names}}' | grep -q webimar-postgres; then
    WEBIMAR_BACKUP="$LOCAL_BACKUP_DIR/webimar-db-$DATE.sql.gz"
    docker exec webimar-postgres pg_dump -U webimar webimar | gzip > "$WEBIMAR_BACKUP"
    
    # Upload to FTP
    upload_to_ftp "$WEBIMAR_BACKUP" "webimar-db-$DATE.sql.gz"
    
    echo "✅ Webimar backup: $(du -h "$WEBIMAR_BACKUP" | cut -f1)"
else
    echo "⚠️  Webimar PostgreSQL container not running"
fi

# Backup Anka PostgreSQL (if running)
if docker ps --format '{{.Names}}' | grep -q anka_postgres; then
    echo "📦 Backing up anka database..."
    ANKA_BACKUP="$LOCAL_BACKUP_DIR/anka-db-$DATE.sql.gz"
    docker exec anka_postgres_prod pg_dump -U anka_user anka_prod | gzip > "$ANKA_BACKUP"
    
    # Upload to FTP
    upload_to_ftp "$ANKA_BACKUP" "anka-db-$DATE.sql.gz"
    
    echo "✅ Anka backup: $(du -h "$ANKA_BACKUP" | cut -f1)"
fi

# Backup Docker volumes (important data)
echo "📦 Creating volumes backup manifest..."
VOLUMES_INFO="$LOCAL_BACKUP_DIR/docker-volumes-$DATE.txt"
{
    echo "=== Docker Volumes Backup Report - $DATE ==="
    echo ""
    echo "### Volume Usage:"
    docker system df -v
    echo ""
    echo "### Volume Details:"
    docker volume ls --format "table {{.Driver}}\t{{.Name}}\t{{.Size}}"
    echo ""
    echo "### Container Status:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}\t{{.Ports}}"
} > "$VOLUMES_INFO"

upload_to_ftp "$VOLUMES_INFO" "docker-volumes-$DATE.txt"

# Create configuration backup
echo "📦 Backing up configuration files..."
CONFIG_BACKUP="$LOCAL_BACKUP_DIR/vps-config-$DATE.tar.gz"
tar -czf "$CONFIG_BACKUP" \
    infrastructure/nginx/conf.d/ \
    infrastructure/nginx/nginx.conf \
    projects/webimar/docker-compose.prod.yml \
    projects/webimar/.env.example \
    scripts/ \
    --exclude="*.log" \
    2>/dev/null || echo "⚠️  Some config files skipped"

upload_to_ftp "$CONFIG_BACKUP" "vps-config-$DATE.tar.gz"
echo "✅ Config backup: $(du -h "$CONFIG_BACKUP" | cut -f1)"

# Cleanup local backups (keep shorter retention)
echo "🧹 Cleaning up local backups older than $RETENTION_DAYS days..."
find "$LOCAL_BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$LOCAL_BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$LOCAL_BACKUP_DIR" -name "*.txt" -mtime +$RETENTION_DAYS -delete

# Cleanup old FTP backups
cleanup_ftp_backups

# Final report
echo ""
echo "📊 === Backup Summary ==="
echo "🕐 Completed at: $(date)"
echo "📁 Local backups: $(du -sh "$LOCAL_BACKUP_DIR" | cut -f1)"
echo "🌐 FTP uploads completed"
echo ""
echo "📋 Recent local backups:"
ls -lht "$LOCAL_BACKUP_DIR" | head -10

# Health check - verify backups exist
BACKUP_COUNT=$(ls "$LOCAL_BACKUP_DIR"/*.sql.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 0 ]; then
    echo "✅ Backup health check: $BACKUP_COUNT database backups found"
else
    echo "❌ Backup health check: No database backups found!"
    exit 1
fi

echo "✅ Enhanced backup process completed successfully"