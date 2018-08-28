import psycopg2

from app.modals.answer import Answer
from app.modals.question import Question
from app.modals.user import User


class Database:

    def __init__(self):
        """Connect to the database"""
        try:
            self.conn = psycopg2.connect("dbname='stackoverflow' user='postgres' host='localhost' password='postgres' port='5432'")
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

    def add_entity(self, entity_obj):
        """Add an Entity (Answer, Question, User) to the database"""
        try:
            if type(entity_obj) is Question:  # for the Question object
                sql = "INSERT INTO questions(user_id, question_question, question_date_posted) VALUES(%s, %s, %s) RETURNING question_id"
                self.cur.execute(sql, (str(entity_obj.user_id), entity_obj.question, entity_obj.date_posted))
            elif type(entity_obj) is Answer:  # for the Answer object
                sql = "INSERT INTO answers(question_id, user_id, answer_answer, answer_accepted, answer_date_posted) VALUES(%s, %s, %s, %s, %s) RETURNING answer_id"
                self.cur.execute(sql, (
                    str(entity_obj.question_id), str(entity_obj.user_id), entity_obj.answer, entity_obj.accepted,
                    entity_obj.date_posted))
            elif type(entity_obj) is User:  # for the User object
                sql = "INSERT INTO users(user_username, user_password) VALUES(%s, %s) RETURNING user_id"
                self.cur.execute(sql, (entity_obj.username, entity_obj.password))

            # return new id after adding
            new_id = self.cur.fetchone()[0]
            print("Added! New id: ", new_id)
            return new_id
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def get_all_entities(self, tablename, question_id=0):
        """Get all entities (e.g. Questions or Answers or Users ) of the type of object passed
        'question_id' is an optional argument used only when fetching objects/entities of type Answer"""
        
        try:
            # fetch form database and save in list
            entities_list = []
            if tablename == 'questions':
                self.cur.execute("SELECT question_id, user_id, question_question, question_date_posted FROM questions")
            elif tablename == 'answers':
                self.cur.execute(
                    "SELECT answer_id, question_id, user_id, answer_answer, answer_accepted, answer_date_posted FROM answers WHERE question_id = " + str(
                        question_id))
            elif tablename == 'users':
                self.cur.execute("SELECT user_id, user_username, user_password FROM users")

            print("Number of rows in db: ", self.cur.rowcount)
            row = self.cur.fetchone()
            while row is not None:
                # add / append an object to the list
                if tablename == 'questions':
                    entities_list.append(Question(row[0], row[1], row[2], row[3]))
                elif tablename == 'answers':
                    entities_list.append(Answer(row[0], row[1], row[2], row[3], row[4], row[5]))
                elif tablename == 'users':
                    entities_list.append(User(row[0], row[1], row[2]))
                row = self.cur.fetchone()

            return entities_list
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def get_one_entity(self, tablename, entity_id):
        """Get one entity (e.g. Question or Answer or Users ) from the database
        entity_obj is only used to determine the table to read from"""
        
        try:
            entity = None
            if tablename == 'questions':
                self.cur.execute(
                    "SELECT question_id, user_id, question_question, question_date_posted FROM questions WHERE question_id=" + str(
                        entity_id))
            elif tablename == 'answers':
                self.cur.execute(
                    "SELECT answer_id, question_id, user_id, answer_answer, answer_accepted, answer_date_posted FROM answers WHERE answer_id=" + str(
                        entity_id))
            elif tablename == 'users':
                self.cur.execute("SELECT user_id, user_username, user_password FROM users WHERE user_id = " + str(entity_id))

            row = self.cur.fetchone()
            if row is not None:
                if tablename == 'questions':
                    entity = Question(row[0], row[1], row[2], row[3])
                elif tablename == 'answers':
                    entity = Answer(row[0], row[1], row[2], row[3], row[4], row[5])
                elif tablename == 'users':
                    entity = User(row[0], row[1], row[2])
            return entity
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def update_entity(self, entity_obj):
        """Update questions, answers, or users"""
        try:
            if type(entity_obj) is Question:
                sql = """UPDATE questions SET question_question = %s WHERE question_id = %s"""
                self.cur.execute(sql, (entity_obj.question, str(entity_obj.id)))
            elif type(entity_obj) is Answer:
                sql = """UPDATE answers SET question_id = %s, answer_answer = %s, answer_accepted = %s WHERE answer_id = %s"""
                self.cur.execute(sql, (
                str(entity_obj.question_id), entity_obj.answer, str(entity_obj.accepted), str(entity_obj.id)))
            elif type(entity_obj) is User:
                sql = """UPDATE users SET user_username = %s, user_password = %s WHERE user_id = %s"""
                self.cur.execute(sql, (entity_obj.username, entity_obj.password))

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def delete_entity(self, entity_obj):
        """Delete a specific question, answer, or user"""
        try:
            if type(entity_obj) is Question:
                self.cur.execute("DELETE FROM questions WHERE question_id = %s", str(entity_obj.id))
            elif type(entity_obj) is Answer:
                self.cur.execute("DELETE FROM answers WHERE answer_id = %s", str(entity_obj.id))
            elif type(entity_obj) is User:
                self.cur.execute("DELETE FROM users WHERE user_id = %s", str(entity_obj.id))

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def drop_table(self, tablename):
        """Drop the table passed"""
        try:
            self.cur.execute("DROP TABLE " + tablename)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
