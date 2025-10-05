DROP DATABASE IF EXISTS fittrackee;
DROP SCHEMA IF EXISTS fittrackee;
DROP USER IF EXISTS fittrackee;

CREATE USER fittrackee WITH PASSWORD 'fittrackee';
CREATE SCHEMA fittrackee AUTHORIZATION fittrackee;
CREATE DATABASE fittrackee OWNER fittrackee;
