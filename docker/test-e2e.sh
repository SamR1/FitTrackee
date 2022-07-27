#!/bin/bash
set -e
cd /usr/src/app

source .env

export TEST_APP_URL=http://$(hostname --ip-address):5000
pytest e2e --driver Remote --capability browserName firefox --selenium-host selenium --selenium-port 4444 $*