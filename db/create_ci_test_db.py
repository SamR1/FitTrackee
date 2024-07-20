import psycopg2
from psycopg2 import sql

conn = psycopg2.connect(
    host="postgres", dbname="postgres", user="postgres", password="postgres"
)
conn.autocommit = True

with conn.cursor() as cur:
    cur.execute(sql.SQL("""
        CREATE USER fittrackee WITH PASSWORD 'fittrackee';
    """))
    cur.execute(sql.SQL("""
        CREATE SCHEMA fittrackee AUTHORIZATION fittrackee;
    """))
    cur.execute(sql.SQL("""
        CREATE DATABASE fittrackee_test_gw0 OWNER fittrackee;
    """))
    cur.execute(sql.SQL("""
        CREATE DATABASE fittrackee_test_gw1 OWNER fittrackee;
    """))
conn.close()
