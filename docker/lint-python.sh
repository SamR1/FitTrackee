#!/bin/bash
set -e
cd /usr/src/app

source .env

pytest --flake8 --isort --black -m "flake8 or isort or black" fittrackee e2e --ignore=fittrackee/migrations