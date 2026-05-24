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
    cur.execute(sql.SQL("""
        CREATE DATABASE fittrackee_test_gw2 OWNER fittrackee;
    """))
    cur.execute(sql.SQL("""
        CREATE DATABASE fittrackee_test_gw3 OWNER fittrackee;
    """))
    cur.execute(sql.SQL("""
        CREATE DATABASE fittrackee_test_gw4 OWNER fittrackee;
    """))
    cur.execute(sql.SQL("""
        CREATE DATABASE fittrackee_test_gw5 OWNER fittrackee;
    """))
    cur.execute(sql.SQL("""
        CREATE DATABASE fittrackee_test_gw6 OWNER fittrackee;
    """))
    cur.execute(sql.SQL("""
        CREATE DATABASE fittrackee_test_gw7 OWNER fittrackee;
    """))
conn.close()

for index in range(8):
    conn = psycopg2.connect(
        host="postgres",
        dbname=f"fittrackee_test_gw{index}",
        user="postgres",
        password="postgres",
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(sql.SQL("""
            CREATE EXTENSION IF NOT EXISTS postgis;
        """))
    conn.close()