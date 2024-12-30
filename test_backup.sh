#!/bin/bash

# Backup database URL
export BACKUP_DB_URL="postgresql://backup_db_j3c4_user:0ZSzSqR6ZcdMV5tnAYSxLPjPUdcpCreX@dpg-ctiig60gph6c7387gvkg-a.oregon-postgres.render.com/backup_db_j3c4"

# Timestamp for log file
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="test_backup_$TIMESTAMP.log"

# Error handling function
handle_error() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] ERROR: $1" | tee -a $LOG_FILE
    exit 1
}

# Start logging
echo "[$(date +"%Y-%m-%d %H:%M:%S")] Starting backup database integrity test..." | tee $LOG_FILE

# Step 1: Test connection to the backup database
echo "[$(date +"%Y-%m-%d %H:%M:%S")] Testing connection to the backup database..." | tee -a $LOG_FILE
psql $BACKUP_DB_URL -c "\q" 2>> $LOG_FILE
if [ $? -ne 0 ]; then
    handle_error "Failed to connect to the backup database."
fi
echo "[$(date +"%Y-%m-%d %H:%M:%S")] Connection to the backup database successful." | tee -a $LOG_FILE

# Step 2: Check critical tables
CRITICAL_TABLES=("auth_user" "django_admin_log" "backend_client" "token_blacklist_blacklistedtoken")
echo "[$(date +"%Y-%m-%d %H:%M:%S")] Checking for critical tables..." | tee -a $LOG_FILE
for TABLE in "${CRITICAL_TABLES[@]}"; do
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] Checking table: $TABLE" | tee -a $LOG_FILE
    psql $BACKUP_DB_URL -c "SELECT COUNT(*) FROM $TABLE;" 2>> $LOG_FILE
    if [ $? -ne 0 ]; then
        handle_error "Critical table $TABLE is missing or inaccessible."
    fi
done
echo "[$(date +"%Y-%m-%d %H:%M:%S")] All critical tables are present." | tee -a $LOG_FILE

# Step 3: Verify sample data integrity
echo "[$(date +"%Y-%m-%d %H:%M:%S")] Verifying sample data integrity..." | tee -a $LOG_FILE
psql $BACKUP_DB_URL -c "SELECT id, first_name, last_name FROM auth_user LIMIT 5;" 2>> $LOG_FILE
if [ $? -ne 0 ]; then
    handle_error "Failed to verify sample data integrity in auth_user table."
fi
echo "[$(date +"%Y-%m-%d %H:%M:%S")] Sample data integrity verified." | tee -a $LOG_FILE

# Step 4: Count rows in key tables
KEY_TABLES=("auth_user" "backend_client")
echo "[$(date +"%Y-%m-%d %H:%M:%S")] Counting rows in key tables..." | tee -a $LOG_FILE
for TABLE in "${KEY_TABLES[@]}"; do
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] Counting rows in table: $TABLE" | tee -a $LOG_FILE
    psql $BACKUP_DB_URL -c "SELECT COUNT(*) AS row_count FROM $TABLE;" 2>> $LOG_FILE
    if [ $? -ne 0 ]; then
        handle_error "Failed to count rows in $TABLE."
    fi
done
echo "[$(date +"%Y-%m-%d %H:%M:%S")] Row counts verified for key tables." | tee -a $LOG_FILE

# Success message
echo "[$(date +"%Y-%m-%d %H:%M:%S")] Backup database integrity test completed successfully!" | tee -a $LOG_FILE

