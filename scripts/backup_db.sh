#!/bin/bash

# Exhaust Fan IoT System - Database Backup Script
# This script creates a backup of the SQLite database

# Exit on error
set -e

# Variables
PROJECT_DIR="/opt/exhaust-fan-system"
BACKEND_DIR="$PROJECT_DIR/backend"
DB_FILE="$BACKEND_DIR/exhaust_fan.db"
BACKUP_DIR="$PROJECT_DIR/backups"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/exhaust_fan_$DATE.db"
LOG_FILE="$PROJECT_DIR/logs/backup.log"

# Check if database file exists
if [ ! -f "$DB_FILE" ]; then
    echo "$(date) - ERROR: Database file not found at $DB_FILE" >> "$LOG_FILE"
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Create backup
echo "$(date) - Starting database backup..." >> "$LOG_FILE"
sqlite3 "$DB_FILE" ".backup '$BACKUP_FILE'"

# Check if backup was successful
if [ -f "$BACKUP_FILE" ]; then
    # Compress the backup file
    gzip -f "$BACKUP_FILE"
    echo "$(date) - Backup successful: ${BACKUP_FILE}.gz" >> "$LOG_FILE"
    
    # Clean up old backups (keep last 30 days)
    find "$BACKUP_DIR" -name "exhaust_fan_*.db.gz" -type f -mtime +30 -delete
    echo "$(date) - Cleaned up old backups older than 30 days" >> "$LOG_FILE"
else
    echo "$(date) - ERROR: Backup failed" >> "$LOG_FILE"
    exit 1
fi

echo "$(date) - Backup process completed" >> "$LOG_FILE"
exit 0