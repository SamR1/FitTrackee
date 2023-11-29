#!/bin/bash

cp .env.docker .env
docker-compose -f docker-compose-dev.yml build fittrackee
docker login -u 
docker-compose push
