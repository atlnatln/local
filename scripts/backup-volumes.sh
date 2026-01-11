#!/bin/bash
# ============================================================================
# VPS Backup Automation Script
# Daily automated backups for PostgreSQL databases and Docker volumes
# ============================================================================

set -euo pipefail

# Configuration
BACKUP_DIR="/home/akn/vps/backups"
DATE=$(date +%Y%m%d-%H%M%S)
RETENTION_DAYS=7

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

log_info "Starting VPS backup process - $DATE"

# Function to backup PostgreSQL database
backup_postgres() {
    local container_name=$1
    local db_name=$2
    local db_user=$3
    local backup_file="$BACKUP_DIR/${container_name}-db-${DATE}.sql"
    
    log_info "Backing up PostgreSQL: $container_name -> $backup_file"
    
    if docker exec "$container_name" pg_dump -U "$db_user" "$db_name" > "$backup_file"; then
        log_success "PostgreSQL backup completed: $backup_file"
        
        # Compress the backup
        gzip "$backup_file"
        log_success "PostgreSQL backup compressed: ${backup_file}.gz"
    else
        log_error "Failed to backup PostgreSQL: $container_name"
        return 1
    fi
}

# Function to backup Docker volume
backup_volume() {
    local volume_name=$1
    local backup_file="$BACKUP_DIR/volume-${volume_name}-${DATE}.tar.gz"
    
    log_info "Backing up Docker volume: $volume_name -> $backup_file"
    
    if docker run --rm \
        -v "$volume_name:/data:ro" \
        -v "$BACKUP_DIR:/backup" \
        alpine:latest \
        tar czf "/backup/volume-${volume_name}-${DATE}.tar.gz" -C /data .; then
        log_success "Volume backup completed: $backup_file"
    else
        log_error "Failed to backup volume: $volume_name"
        return 1
    fi
}

# Backup Webimar PostgreSQL (if container is running)
if docker ps --format '{{.Names}}' | grep -q '^webimar-postgres$'; then
    backup_postgres "webimar-postgres" "webimar" "webimar" || log_warning "Webimar PostgreSQL backup failed"
else
    log_warning "Webimar PostgreSQL container not running, skipping database backup"
fi

# Backup Anka PostgreSQL (if container is running)  
if docker ps --format '{{.Names}}' | grep -q '^anka-postgres$'; then
    backup_postgres "anka-postgres" "anka_prod" "anka_user" || log_warning "Anka PostgreSQL backup failed"
else
    log_warning "Anka PostgreSQL container not running, skipping database backup"
fi

# Backup critical Docker volumes
CRITICAL_VOLUMES=(
    "webimar_postgres_data"
    "webimar_api_staticfiles" 
    "webimar_api_media"
    "anka_postgres_prod_data"
    "anka_minio_prod_data"
    "vps_prometheus_data"
    "vps_grafana_data"
)

for volume in "${CRITICAL_VOLUMES[@]}"; do
    if docker volume ls --format '{{.Name}}' | grep -q "^$volume$"; then
        backup_volume "$volume" || log_warning "Volume backup failed: $volume"
    else
        log_warning "Volume not found: $volume"
    fi
done

# Cleanup old backups
log_info "Cleaning up backups older than $RETENTION_DAYS days"

# Remove old database backups
find "$BACKUP_DIR" -name "*-db-*.sql.gz" -mtime +$RETENTION_DAYS -delete -print | while read -r file; do
    log_info "Deleted old database backup: $file"
done

# Remove old volume backups
find "$BACKUP_DIR" -name "volume-*.tar.gz" -mtime +$RETENTION_DAYS -delete -print | while read -r file; do
    log_info "Deleted old volume backup: $file"
done

# Generate backup report
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR" | wc -l)

log_success "Backup process completed successfully"
log_info "Backup directory: $BACKUP_DIR"
log_info "Total backup size: $BACKUP_SIZE"
log_info "Total backup files: $BACKUP_COUNT"

# Optional: Send notification (if telegram token available)
if [[ -n "${TELEGRAM_BOT_TOKEN:-}" && -n "${TELEGRAM_CHAT_ID:-}" ]]; then
    MESSAGE="🔄 VPS Backup Completed
📅 Date: $DATE
📂 Size: $BACKUP_SIZE  
📄 Files: $BACKUP_COUNT
✅ Status: Success"
    
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d chat_id="$TELEGRAM_CHAT_ID" \
        -d text="$MESSAGE" > /dev/null || log_warning "Failed to send Telegram notification"
fi

log_info "Backup script finished"