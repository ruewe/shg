#!/bin/bash

# Script to backup the SHG PostgreSQL database
# Usage: ./backup_db.sh [optional_output_directory]

# Configuration
CONTAINER_NAME="django_db"
ENV_FILE=".env.prod"

# Ensure we are in the project root or find the env file
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: $ENV_FILE not found. Please run this script from the project folder."
    exit 1
fi

# Extract DB user and name from .env.prod
# We use grep/cut to simple extraction. 
# It assumes lines like POSTGRES_USER=django_user
DB_USER=$(grep "^POSTGRES_USER=" $ENV_FILE | cut -d '=' -f2 | tr -d '\r"')
DB_NAME=$(grep "^POSTGRES_DB=" $ENV_FILE | cut -d '=' -f2 | tr -d '\r"')

if [ -z "$DB_USER" ] || [ -z "$DB_NAME" ]; then
    echo "Error: Could not extract POSTGRES_USER or POSTGRES_DB from $ENV_FILE"
    exit 1
fi

# Set output directory
OUTPUT_DIR="${1:-./backups}"
mkdir -p "$OUTPUT_DIR"

# Generate filename with timestamp
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$OUTPUT_DIR/backup_shg_${TIMESTAMP}.sql"

echo "Starting backup for database '$DB_NAME'..."
echo "Container: $CONTAINER_NAME"
echo "Target: $BACKUP_FILE"

# Execute pg_dump
# We don't need the password if we execute as the postgres user inside the container,
# or we can rely on .pgpass. But simpler is usually just running it.
# Docker exec usually runs as root, so we might need to specify user inside container.
# The official postgres image runs as 'postgres' user usually, or we pass credentials.
# Best practice: use PGPASSWORD env var inline inside the exec or rely on trust auth (since local).
# Actually, 'docker exec' runs as root by default, so we can su to postgres or just run pg_dump.
# Since we know the DB user (django_user), we force that user.

docker exec -t $CONTAINER_NAME pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup successful: $BACKUP_FILE"
    # Gzip the backup to save space
    gzip "$BACKUP_FILE"
    echo "📦 Compressed: $BACKUP_FILE.gz"
else
    echo "❌ Backup failed!"
    # Clean up empty file if it exists and size is 0
    if [ ! -s "$BACKUP_FILE" ]; then
        rm -f "$BACKUP_FILE"
    fi
    exit 1
fi
