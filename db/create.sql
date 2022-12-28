DROP DATABASE IF EXISTS fittrackee;
DROP DATABASE IF EXISTS fittrackee_test;
DROP DATABASE IF EXISTS fittrackee_test_gw0;
DROP DATABASE IF EXISTS fittrackee_test_gw1;
DROP DATABASE IF EXISTS fittrackee_test_gw2;
DROP DATABASE IF EXISTS fittrackee_test_gw3;
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
