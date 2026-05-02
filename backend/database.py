import mysql.connector
from mysql.connector import pooling

class Database:
    def __init__(self):
        self.pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="metro_pool",
            pool_size=5,
            pool_reset_session=True,
            host="localhost",
            user="root",
            password="admin",
            database="MetroDB"
        )

    def get_connection(self):
        return self.pool.get_connection()

db = Database()

def get_db():
    conn = db.get_connection()
    try:
        yield conn
    finally:
        conn.close()
