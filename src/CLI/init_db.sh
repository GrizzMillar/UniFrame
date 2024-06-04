#!/bin/bash
set -e

if ! command -v sqlite3 > /dev/null 2>&1; then
    echo "sqlite3 not found, installing...."
    sudo DEBIAN_FRONTEND=noninteractive apt get update
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y sqlite3
fi

DATABASE_DIR="database"
DATABASE_FILE="$DATABASE_DIR/test_database.db"

echo "Creating database directory...."
mkdir -p $DATABASE_DIR

echo "Creating and Initialising Database...."
sqlite3 $DATABASE_FILE <<EOF
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL
);

INSERT INTO users (username, email) VALUES ('alice', 'alice@example.com');
EOF

echo "Database setup complete!"
