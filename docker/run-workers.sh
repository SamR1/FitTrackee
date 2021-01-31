#!/bin/bash
set -e
cd /usr/src/app

source .env.docker

flask worker --processes=$WORKERS_PROCESSES >> dramatiq.log  2>&1
