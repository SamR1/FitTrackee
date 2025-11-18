#!/bin/bash
set -e

# Init database
echo "Initializing database..."
ftcli db upgrade || { echo "Failed to upgrade database!"; exit 1; }

# Run workers
echo "Starting workers..."
dramatiq fittrackee.tasks:broker --processes="${WORKERS_PROCESSES:-1}" --log-file="${DRAMATIQ_LOG:-data/logs/dramatiq.log}" &

# Wait for workers to start
sleep 3

# Run app
echo "Starting app with debugpy..."
# Use internal VS Code debugger instead of Flask's built-in debugger (--no-debugger)
# Prevent Flask from implicitly killing a debugging session on code changes (--no-reload)
exec python -m debugpy --connect host.docker.internal:5678 -m \
    flask run --debug --with-threads --host=0.0.0.0 --port=5000 --no-debugger --no-reload
