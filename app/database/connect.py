import psycopg2

from app.database.config import config


def connect_to_db():
    """ Connect to the PostgreSQL database server """
    try:
        # read connection parameters from config file
        params = config()

        # return connection and cursor
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        return conn, cur
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
