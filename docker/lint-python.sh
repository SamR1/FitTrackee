#!/bin/bash
set -e
cd /usr/src/app

source .env

mypy fittrackee
pytest --isort --black -m "isort or black" fittrackee e2e --ignore=fittrackee/migrations
echo 'Running flake8...'
flake8 fittrackee e2e