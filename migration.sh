#!/bin/bash
set -e

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=SKN23

echo "▶ Database migration start"

mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD <<EOF
DROP DATABASE IF EXISTS $DB_NAME;
CREATE DATABASE $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE $DB_NAME;
EOF

echo "▶ Apply schema.sql"
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD $DB_NAME < assets/db/schema.sql

echo "▶ Apply seed.sql"
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD $DB_NAME < assets/db/seed.sql

echo "✅ Migration completed successfully"
