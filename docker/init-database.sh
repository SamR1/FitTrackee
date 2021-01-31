#!/bin/bash
set -e
cd /usr/src/app

source .env.docker

flask drop-db
flask db upgrade --directory fittrackee/migrations
flask init-data