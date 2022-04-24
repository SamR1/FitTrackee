#!/bin/bash
set -e
cd /usr/src/app

source .env.docker

ftcli db drop
ftcli db upgrade