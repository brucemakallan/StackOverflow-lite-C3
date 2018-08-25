import psycopg2

from app.database.connect import connect_to_db


def create_tables():
    """ Create tables in the PostgreSQL database (only if tables do NOT exist) """

    commands = []
    commands.append(""" CREATE TABLE IF NOT EXISTS questions (
                question_id SERIAL PRIMARY KEY, 
                question_question VARCHAR(255) NOT NULL,  
                question_date_posted VARCHAR(255)
                )
        """)
    commands.append("""
        CREATE TABLE IF NOT EXISTS answers (
                answer_id INTEGER PRIMARY KEY, 
                question_id INTEGER, 
                answer_answer VARCHAR(255) NOT NULL, 
                answer_date_posted VARCHAR(255), 
                FOREIGN KEY (question_id) 
                REFERENCES questions (question_id) 
                ON UPDATE CASCADE ON DELETE CASCADE
        )
        """)

    conn = None
    try:
        # get connection, and cursor from connection method
        conn, cur = connect_to_db()
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()  # close database connection
