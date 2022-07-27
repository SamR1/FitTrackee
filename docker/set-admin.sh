#!/bin/bash
set -e
cd /usr/src/app

source .env

ftcli users update $1 --set-admin true
