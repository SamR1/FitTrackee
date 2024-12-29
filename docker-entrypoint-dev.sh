#!/bin/bash
set -e

# Init database
echo "Initializing database..."
ftcli db upgrade || { echo "Failed to upgrade database!"; exit 1; }

# Run workers
echo "Starting workers..."
flask worker --processes="${WORKERS_PROCESSES:-1}" >> data/logs/dramatiq.log 2>&1 &

# Wait for workers to start
sleep 3

# Run app
echo "Starting app..."
exec flask run --with-threads --host=0.0.0.0
