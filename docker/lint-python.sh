#!/bin/bash
set -e
cd /usr/src/app

source .env

mypy fittrackee
ruff check fittrackee e2e