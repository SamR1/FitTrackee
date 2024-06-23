#!/bin/bash
set -e

# Change to the application directory
cd /usr/src/app || exit 1

# Check if the .env file exists and source it
if [[ -f .env ]]; then
    source .env
else
    echo ".env file not found!"
    exit 1
fi

# Wait for postgres
#sleep 20

# Init database
echo "Initializing database..."
ftcli db upgrade || { echo "Failed to upgrade database!"; exit 1; }

# Run workers
echo "Initializing workers..."
flask worker --processes="${WORKERS_PROCESSES:-1}" >> dramatiq.log 2>&1 &

# Run app
echo "Initializing app..."
exec flask run --with-threads --host=0.0.0.0
