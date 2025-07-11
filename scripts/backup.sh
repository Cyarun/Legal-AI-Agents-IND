#!/bin/sh
# Automated backup script for Neo4j and Redis

set -e

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
NEO4J_BACKUP="neo4j_backup_${TIMESTAMP}"
REDIS_BACKUP="redis_backup_${TIMESTAMP}.rdb"

echo "Starting backup at $(date)"

# Backup Neo4j
echo "Backing up Neo4j..."
mkdir -p "${BACKUP_DIR}/neo4j"
cd /neo4j-data
tar -czf "${BACKUP_DIR}/neo4j/${NEO4J_BACKUP}.tar.gz" .
echo "Neo4j backup completed: ${NEO4J_BACKUP}.tar.gz"

# Backup Redis
echo "Backing up Redis..."
mkdir -p "${BACKUP_DIR}/redis"
cp /redis-data/dump.rdb "${BACKUP_DIR}/redis/${REDIS_BACKUP}"
echo "Redis backup completed: ${REDIS_BACKUP}"

# Upload to S3 if configured
if [ ! -z "$S3_BUCKET" ]; then
    echo "Uploading to S3..."
    aws s3 cp "${BACKUP_DIR}/neo4j/${NEO4J_BACKUP}.tar.gz" "s3://${S3_BUCKET}/neo4j/" || echo "S3 upload failed for Neo4j"
    aws s3 cp "${BACKUP_DIR}/redis/${REDIS_BACKUP}" "s3://${S3_BUCKET}/redis/" || echo "S3 upload failed for Redis"
fi

# Clean up old backups (keep last 7 days)
echo "Cleaning up old backups..."
find "${BACKUP_DIR}/neo4j" -name "*.tar.gz" -mtime +7 -delete
find "${BACKUP_DIR}/redis" -name "*.rdb" -mtime +7 -delete

echo "Backup completed at $(date)"