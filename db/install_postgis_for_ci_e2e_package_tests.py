import psycopg2
from psycopg2 import sql

conn = psycopg2.connect(
    host="postgres",
    dbname="fittrackee_test",
    user="fittrackee",
    password="fittrackee",
)
conn.autocommit = True
with conn.cursor() as cur:
    cur.execute(
        sql.SQL("CREATE EXTENSION IF NOT EXISTS postgis;")
    )
conn.close()
