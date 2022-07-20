#!/bin/bash
set -e
cd /usr/src/app

source .env

pytest fittrackee $*