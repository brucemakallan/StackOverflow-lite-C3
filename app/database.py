import psycopg2
import os


class Database:

    def __init__(self):
        """Connect to the database and create all tables"""
        try:
            # use the current environment to determine which database to use
            database = 'stackoverflow'
            if os.getenv('APP_SETTINGS') == 'testing':
                database = 'stackoverflowtest'

            # connect to the database selected
            self.conn = psycopg2.connect(database=database,
                                         user='postgres',
                                         host='localhost',
                                         password='postgres',
                                         port='5432')
            self.conn.autocommit = True
            self.cur = self.conn.cursor()

            """Create all the tables required if they do not already exist"""
            commands = ["""CREATE TABLE IF NOT EXISTS users (
                                user_id SERIAL PRIMARY KEY, 
                                user_username VARCHAR(255) NOT NULL, 
                                user_password VARCHAR(255) NOT NULL 
                            )""",
                        """CREATE TABLE IF NOT EXISTS questions (
                                question_id SERIAL PRIMARY KEY,
                                user_id INTEGER, 
                                question_question VARCHAR(255) NOT NULL,  
                                question_date_posted VARCHAR(255)
                                )""",
                        """CREATE TABLE IF NOT EXISTS answers (
                                answer_id SERIAL PRIMARY KEY, 
                                question_id INTEGER,
                                user_id INTEGER, 
                                answer_answer VARCHAR(255) NOT NULL,
                                answer_accepted BOOLEAN NOT NULL,  
                                answer_date_posted VARCHAR(255), 
                                FOREIGN KEY (question_id) 
                                REFERENCES questions (question_id) 
                                ON UPDATE CASCADE ON DELETE CASCADE
                        )"""]

            for command in commands:
                self.cur.execute(command)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def drop_all_tables(self, tables):
        """Drop all tables passed in list"""
        try:
            for table in tables:
                self.cur.execute("DROP TABLE " + table)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
