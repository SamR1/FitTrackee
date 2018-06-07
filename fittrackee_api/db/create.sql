DROP DATABASE IF EXISTS fittrackee;
DROP DATABASE IF EXISTS fittrackee_test;
CREATE DATABASE fittrackee;
CREATE DATABASE fittrackee_test;
CREATE USER fittrackee WITH PASSWORD 'fittrackee';
GRANT ALL PRIVILEGES ON DATABASE fittrackee TO fittrackee;
GRANT ALL PRIVILEGES ON DATABASE fittrackee_test TO fittrackee;
