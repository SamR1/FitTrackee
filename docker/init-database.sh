#!/bin/bash
set -e
cd /usr/src/app

source .env

ftcli db drop
ftcli db upgrade