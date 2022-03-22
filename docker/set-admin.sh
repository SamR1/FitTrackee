#!/bin/bash
set -e
cd /usr/src/app

source .env.docker

flask users set-admin $1
