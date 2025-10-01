#!/bin/bash
set -e

echo 'Creating databases for dev and tests...'
psql -v ON_ERROR_STOP=1 --username postgres --dbname postgres <<-EOSQL
  DROP DATABASE IF EXISTS fittrackee;
  DROP DATABASE IF EXISTS fittrackee_test;
  DROP DATABASE IF EXISTS fittrackee_test_gw0;
  DROP DATABASE IF EXISTS fittrackee_test_gw1;
  DROP DATABASE IF EXISTS fittrackee_test_gw2;
  DROP DATABASE IF EXISTS fittrackee_test_gw3;
  DROP DATABASE IF EXISTS fittrackee_test_gw4;
  DROP DATABASE IF EXISTS fittrackee_test_gw5;
  DROP DATABASE IF EXISTS fittrackee_test_gw6;
  DROP DATABASE IF EXISTS fittrackee_test_gw7;
  DROP SCHEMA IF EXISTS fittrackee;
  DROP USER IF EXISTS fittrackee;

  CREATE USER fittrackee WITH PASSWORD 'fittrackee';
  CREATE SCHEMA fittrackee AUTHORIZATION fittrackee;
  CREATE DATABASE fittrackee OWNER fittrackee;
  CREATE DATABASE fittrackee_test OWNER fittrackee;
  CREATE DATABASE fittrackee_test_gw0 OWNER fittrackee;
  CREATE DATABASE fittrackee_test_gw1 OWNER fittrackee;
  CREATE DATABASE fittrackee_test_gw2 OWNER fittrackee;
  CREATE DATABASE fittrackee_test_gw3 OWNER fittrackee;
  CREATE DATABASE fittrackee_test_gw4 OWNER fittrackee;
  CREATE DATABASE fittrackee_test_gw5 OWNER fittrackee;
  CREATE DATABASE fittrackee_test_gw6 OWNER fittrackee;
  CREATE DATABASE fittrackee_test_gw7 OWNER fittrackee;
EOSQL

echo 'Installing postgis extension on each database...'
echo '- fittrackee'
psql -U postgres -d fittrackee -c 'CREATE EXTENSION IF NOT EXISTS postgis;'
echo '- fittrackee_test'
psql -U postgres -d fittrackee_test -c 'CREATE EXTENSION IF NOT EXISTS postgis;'

number=0
while [[ $number -le 7 ]]
do
    echo '- fittrackee_test_gw'$number
    psql -U postgres -d fittrackee_test_gw$number -c 'CREATE EXTENSION IF NOT EXISTS postgis;'
    number=$(( number+1 ))
done
