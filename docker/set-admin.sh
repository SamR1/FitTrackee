#!/bin/bash
set -e
cd /usr/src/app

source .env.docker

flask set-admin $1
