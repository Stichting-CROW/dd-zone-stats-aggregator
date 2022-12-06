from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import os

class DBHelper:
    def __init__(self, conn_str):
        self._connection_pool = None
        self.conn_str = conn_str

    def initialize_connection_pool(self):
        self._connection_pool = pool.ThreadedConnectionPool(2, 10 , self.conn_str)

    @contextmanager
    def get_resource(self):
        if self._connection_pool is None:
            self.initialize_connection_pool()

        conn = self._connection_pool.getconn()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor, conn
        finally:
            cursor.close()
            self._connection_pool.putconn(conn)

    def shutdown_connection_pool(self):
        if self._connection_pool is not None:
            self._connection_pool.closeall()

# Init normal db
conn_str = "dbname=deelfietsdashboard"

if "DB_HOST" in os.environ:
    conn_str += " host={} ".format(os.environ['DB_HOST'])
if "DB_USER" in os.environ:
    conn_str += " user={}".format(os.environ['DB_USER'])
if "DB_PASSWORD" in os.environ:
    conn_str += " password={}".format(os.environ['DB_PASSWORD'])
if "DB_PORT" in os.environ:
    conn_str += " port={}".format(os.environ['DB_PORT'])

db_helper = DBHelper(conn_str)

# Init timescaledb
# Init normal db
conn_str_timescale_db = "dbname=dashboardeelmobiliteit-timescaledb"
if os.getenv('DEV') == 'true':
    conn_str_timescale_db = "dbname=dashboardeelmobiliteit-timescaledb-dev"

if "TIMESCALE_DB_HOST" in os.environ:
    conn_str_timescale_db += " host={} ".format(os.environ['TIMESCALE_DB_HOST'])
if "TIMESCALE_DB_USER" in os.environ:
    conn_str_timescale_db += " user={}".format(os.environ['TIMESCALE_DB_USER'])
if "TIMESCALE_DB_PASSWORD" in os.environ:
    conn_str_timescale_db += " password={}".format(os.environ['TIMESCALE_DB_PASSWORD'])
if "TIMESCALE_DB_PORT" in os.environ:
    conn_str_timescale_db += " port={}".format(os.environ['TIMESCALE_DB_PORT'])

timescale_db_helper = DBHelper(conn_str_timescale_db)