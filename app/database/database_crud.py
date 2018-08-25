import psycopg2

from app.database.connect import connect_to_db
from app.database.create_tables import create_tables
from app.question import Question


def add_question(question_obj):
    conn = None
    try:
        # create database tables if they don't exist
        create_tables()

        # execute SQL
        conn, cur = connect_to_db()
        sql = """INSERT INTO questions(question_question, question_date_posted)
                     VALUES(%s, %s) RETURNING question_id;"""
        cur.execute(sql, (question_obj.question, question_obj.date_posted))
        new_id = cur.fetchone()[0]
        print("Added! New id: ", new_id)

        cur.close()
        conn.commit()
        return new_id
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def get_all_questions():
    conn = None
    try:
        # create database tables if they don't exist
        create_tables()

        # fetch form database and save in list
        questions = []
        # get connection and cursor
        conn, cur = connect_to_db()
        cur.execute("SELECT question_id, question_question, question_date_posted FROM questions")
        print("Number of rows in db: ", cur.rowcount)
        row = cur.fetchone()
        while row is not None:
            # add / append an object to the list
            questions.append(Question(row[0], row[1], row[2]))
            row = cur.fetchone()

        # close communication with the PostgreSQL database server and commit the changes
        cur.close()
        conn.commit()
        return questions
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()  # close database connection


def get_one_question(question_id):
    conn = None
    try:
        # create database tables if they don't exist
        create_tables()

        question_obj = None
        conn, cur = connect_to_db()
        cur.execute("SELECT question_id, question_question, question_date_posted FROM questions WHERE question_id=" + str(question_id))
        row = cur.fetchone()
        if row is not None:
             question_obj = Question(row[0], row[1], row[2])

        cur.close()
        conn.commit()
        return question_obj
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
