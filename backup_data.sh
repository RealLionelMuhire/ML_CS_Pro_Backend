#!/bin/bash

# Set environment variables for production and backup database URLs
export PROD_DB_URL="postgresql:xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export BACKUP_DB_URL="postgresql:xxxxxxxxxxxxxxxxxxx"

# Timestamp for filenames and logs
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DUMP_FILE="prod_backup_$TIMESTAMP.dump"
SQL_FILE="prod_backup_cleaned_$TIMESTAMP.sql"
LOG_FILE="backup_restore_$TIMESTAMP.log"

# Error handling function
handle_error() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] ERROR: $1" | tee -a $LOG_FILE
    exit 1
}

# Start logging
echo "[$(date +"%Y-%m-%d %H:%M:%S")] Starting backup and restore process..." | tee $LOG_FILE

# Step 1: Dump production database
echo "[$(date +"%Y-%m-%d %H:%M:%S")] Dumping production database to $DUMP_FILE..." | tee -a $LOG_FILE
pg_dump $PROD_DB_URL --no-owner --format=custom --file=$DUMP_FILE 2>> $LOG_FILE
if [ $? -ne 0 ]; then
    handle_error "Failed to dump the production database."
fi
echo "[$(date +"%Y-%m-%d %H:%M:%S")] Database dump completed successfully." | tee -a $LOG_FILE

# Step 2: Extract and clean SQL file
echo "[$(date +"%Y-%m-%d %H:%M:%S")] Extracting and cleaning SQL dump to $SQL_FILE..." | tee -a $LOG_FILE
pg_restore --file=$SQL_FILE --no-owner --no-acl $DUMP_FILE 2>> $LOG_FILE
if [ $? -ne 0 ]; then
    handle_error "Failed to extract SQL from the dump file."
fi

# Remove unsupported configuration parameters (e.g., transaction_timeout)
sed -i '/SET transaction_timeout/d' $SQL_FILE
if [ $? -ne 0 ]; then
    handle_error "Failed to clean unsupported parameters from the SQL file."
fi
echo "[$(date +"%Y-%m-%d %H:%M:%S")] SQL dump cleaned successfully." | tee -a $LOG_FILE

# Step 3: Restore the cleaned SQL to the backup database
echo "[$(date +"%Y-%m-%d %H:%M:%S")] Restoring cleaned SQL to backup database..." | tee -a $LOG_FILE
psql $BACKUP_DB_URL < $SQL_FILE 2>> $LOG_FILE
if [ $? -ne 0 ]; then
    handle_error "Failed to restore the cleaned SQL file to the backup database."
fi
echo "[$(date +"%Y-%m-%d %H:%M:%S")] Database restore completed successfully." | tee -a $LOG_FILE

# Step 4: Cleanup (Optional)
echo "[$(date +"%Y-%m-%d %H:%M:%S")] Cleaning up temporary files..." | tee -a $LOG_FILE
rm -f $DUMP_FILE $SQL_FILE
if [ $? -ne 0 ]; then
    handle_error "Failed to delete temporary files."
fi
echo "[$(date +"%Y-%m-%d %H:%M:%S")] Cleanup completed successfully." | tee -a $LOG_FILE

# Success message
echo "[$(date +"%Y-%m-%d %H:%M:%S")] Backup and restore process completed successfully!" | tee -a $LOG_FILE
