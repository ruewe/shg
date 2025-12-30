#!/bin/bash

# Script to restore the SHG PostgreSQL database
# Usage: ./restore_db.sh <path_to_backup_file.sql.gz>

CONTAINER_NAME="django_db"
ENV_FILE=".env.prod"

if [ -z "$1" ]; then
    echo "Usage: $0 <path_to_backup_file.sql.gz>"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: File $BACKUP_FILE not found."
    exit 1
fi

# Extract DB config
DB_USER=$(grep "^POSTGRES_USER=" $ENV_FILE | cut -d '=' -f2 | tr -d '\r"')
DB_NAME=$(grep "^POSTGRES_DB=" $ENV_FILE | cut -d '=' -f2 | tr -d '\r"')

echo "⚠️  WARNING: THIS WILL OVERWRITE THE CURRENT DATABASE '$DB_NAME'!"
echo "All current data will be lost/replaced by the backup."
echo "Backup file: $BACKUP_FILE"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Registration cancelled."
    exit 0
fi

echo "Stopping Django app to release DB connections..."
docker compose -f docker-compose.prod.yml stop web

echo "Restoring database..."

# Check if file is gzipped
if [[ "$BACKUP_FILE" == *.gz ]]; then
    # Unzip and pipe to psql
    gunzip -c "$BACKUP_FILE" | docker exec -i $CONTAINER_NAME psql -U "$DB_USER" -d "$DB_NAME"
else
    # Pipe plain sql
    cat "$BACKUP_FILE" | docker exec -i $CONTAINER_NAME psql -U "$DB_USER" -d "$DB_NAME"
fi

if [ $? -eq 0 ]; then
    echo "✅ Database restored successfully."
else
    echo "❌ Restore failed."
fi

echo "Restarting Django app..."
docker compose -f docker-compose.prod.yml start web
