import psycopg2

from app.modals.answer import Answer
from app.database.connect import connect_to_db
from app.database.create_tables import create_tables
from app.modals.question import Question
from app.modals.user import User


def add_entity(entity_obj):
    """Add an entity (e.g. Question or Answer or User ) to the database"""
    conn = None
    try:
        # create database tables if they don't exist
        create_tables()

        # run query
        conn, cur = connect_to_db()
        if type(entity_obj) is Question:  # for the Question object
            sql = "INSERT INTO questions(user_id, question_question, question_date_posted) VALUES(%s, %s, %s) RETURNING question_id"
            cur.execute(sql, (str(entity_obj.user_id), entity_obj.question, entity_obj.date_posted))
        elif type(entity_obj) is Answer:  # for the Answer object
            sql = "INSERT INTO answers(question_id, user_id, answer_answer, answer_accepted, answer_date_posted) VALUES(%s, %s, %s, %s, %s) RETURNING answer_id"
            cur.execute(sql, (str(entity_obj.question_id), str(entity_obj.user_id), entity_obj.answer, entity_obj.accepted, entity_obj.date_posted))
        elif type(entity_obj) is User:  # for the User object
            sql = "INSERT INTO users(user_username, user_password) VALUES(%s, %s) RETURNING user_id"
            cur.execute(sql, (entity_obj.username, entity_obj.password))

        # return new id after adding
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


def get_all_entities(entity_obj, question_id=0):
    """Get all entities (e.g. Questions or Answers or Users ) of the type of object passed
    'question_id' is an optional argument used only when fetching objects/entities of type Answer"""
    conn = None
    try:
        # create database tables if they don't exist
        create_tables()

        # fetch form database and save in list
        entities_list = []
        # get connection and cursor and run query
        conn, cur = connect_to_db()
        if type(entity_obj) is Question:
            cur.execute("SELECT question_id, user_id, question_question, question_date_posted FROM questions")
        elif type(entity_obj) is Answer:
            cur.execute("SELECT answer_id, question_id, user_id, answer_answer, answer_accepted, answer_date_posted FROM answers WHERE question_id = " + str(question_id))
        elif type(entity_obj) is User:
            cur.execute("SELECT user_id, user_username, user_password FROM users")

        print("Number of rows in db: ", cur.rowcount)
        row = cur.fetchone()
        while row is not None:
            # add / append an object to the list
            if type(entity_obj) is Question:
                entities_list.append(Question(row[0], row[1], row[2], row[3]))
            elif type(entity_obj) is Answer:
                entities_list.append(Answer(row[0], row[1], row[2], row[3], row[4], row[5]))
            elif type(entity_obj) is User:
                entities_list.append(User(row[0], row[1], row[2]))
            row = cur.fetchone()

        cur.close()
        conn.commit()
        return entities_list
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()  # close database connection


def get_one_entity(entity_obj, entity_id):
    """Get one entity (e.g. Question or Answer or Users ) from the database
    entity_obj is only used to determine the table to read from"""
    conn = None
    try:
        # create database tables if they don't exist
        create_tables()

        entity = None
        conn, cur = connect_to_db()
        # run query
        if type(entity_obj) is Question:
            cur.execute("SELECT question_id, user_id, question_question, question_date_posted FROM questions WHERE question_id=" + str(entity_id))
        elif type(entity_obj) is Answer:
            cur.execute("SELECT answer_id, question_id, user_id, answer_answer, answer_accepted, answer_date_posted FROM answers WHERE answer_id=" + str(entity_id))
        elif type(entity_obj) is User:
            cur.execute("SELECT user_id, user_username, user_password FROM users WHERE user_id = " + str(entity_id))

        row = cur.fetchone()
        if row is not None:
            if type(entity_obj) is Question:
                entity = Question(row[0], row[1], row[2], row[3])
            elif type(entity_obj) is Answer:
                entity = Answer(row[0], row[1], row[2], row[3], row[4], row[5])
            elif type(entity_obj) is User:
                entity = User(row[0], row[1], row[2])
        cur.close()
        conn.commit()
        return entity
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def update_entity(entity_obj):
    """Update questions, answers, or users"""
    conn = None
    try:
        # create database tables if they don't exist
        create_tables()

        # run query
        conn, cur = connect_to_db()
        if type(entity_obj) is Question:
            sql = """UPDATE questions SET question_question = %s WHERE question_id = %s"""
            cur.execute(sql, (entity_obj.question, str(entity_obj.id)))
        elif type(entity_obj) is Answer:
            sql = """UPDATE answers SET question_id = %s, answer_answer = %s, answer_accepted = %s WHERE answer_id = %s"""
            cur.execute(sql, (str(entity_obj.question_id), entity_obj.answer, str(entity_obj.accepted), str(entity_obj.id)))
        elif type(entity_obj) is User:
            sql = """UPDATE users SET user_username = %s, user_password = %s WHERE user_id = %s"""
            cur.execute(sql, (entity_obj.username, entity_obj.password))

        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def delete_entity(entity_obj):
    """Delete a specific question, answer, or user"""
    conn = None
    try:
        # create database tables if they don't exist
        create_tables()

        # run query
        conn, cur = connect_to_db()
        if type(entity_obj) is Question:
            cur.execute("DELETE FROM questions WHERE question_id = %s", str(entity_obj.id))
        elif type(entity_obj) is Answer:
            cur.execute("DELETE FROM answers WHERE answer_id = %s", str(entity_obj.id))
        elif type(entity_obj) is User:
            cur.execute("DELETE FROM users WHERE user_id = %s", str(entity_obj.id))

        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
