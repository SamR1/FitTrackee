DROP DATABASE IF EXISTS fittrackee;
DROP DATABASE IF EXISTS fittrackee_test;
DROP SCHEMA IF EXISTS fittrackee;
DROP USER IF EXISTS fittrackee;

CREATE USER fittrackee WITH PASSWORD 'fittrackee';
CREATE SCHEMA fittrackee AUTHORIZATION fittrackee;
CREATE DATABASE fittrackee OWNER fittrackee;
CREATE DATABASE fittrackee_test OWNER fittrackee;
