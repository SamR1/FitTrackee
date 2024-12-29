#!/bin/bash
set -e

# Upgrade database
echo "Upgrading database..."
ftcli db upgrade || { echo "Failed to upgrade database!"; exit 1; }

# Run app w/ gunicorn
echo "Running app..."
exec gunicorn -b 0.0.0.0:5000 "fittrackee:create_app()" --error-logfile /usr/src/app/logs/gunicorn.log
