#!/bin/bash
set -e

MYSQL_BASE="/opt/mysql/usr/local/mysql"
DATA_DIR="/opt/mysql/data"

if [ ! -d "$DATA_DIR/mysql" ]; then
    echo "Initializing MySQL data directory..."

    $MYSQL_BASE/bin/mysqld --initialize-insecure --datadir="$DATA_DIR" --user=1001
    echo "MySQL initialized."
fi

exec "$@"