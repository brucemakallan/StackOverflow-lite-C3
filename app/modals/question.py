import psycopg2


class Question:

    def __init__(self, question_id, user_id, question, date_posted):
        self.id = question_id
        self.user_id = user_id
        self.question = question
        self.date_posted = date_posted

    def create(self, cur):
        """Create a new row"""
        try:
            # run query and return new id
            sql = """INSERT INTO questions(user_id, question_question, question_date_posted) 
                                        VALUES(%s, %s, %s) RETURNING question_id"""
            cur.execute(sql, (str(self.user_id), self.question, self.date_posted))
            new_id = cur.fetchone()[0]
            return new_id
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    @staticmethod
    def read_all(cur):
        """Read all rows"""
        try:
            questions_list = []
            cur.execute("SELECT question_id, user_id, question_question, question_date_posted FROM questions")
            row = cur.fetchone()
            while row is not None:
                questions_list.append(Question(row[0], row[1], row[2], row[3]))
                row =cur.fetchone()
            return questions_list
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    @staticmethod
    def read_one(cur, question_id):
        """Read one row"""
        try:
            question = None
            cur.execute(
                "SELECT question_id, user_id, question_question, question_date_posted FROM questions WHERE question_id=" + str(
                    question_id))
            row = cur.fetchone()
            if row is not None:
                question = Question(row[0], row[1], row[2], row[3])
            return question
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def update(self, cur):
        """Update one row"""
        try:
            sql = """UPDATE questions SET question_question = %s WHERE question_id = %s"""
            cur.execute(sql, (self.question, str(self.id)))
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def delete(self, cur):
        """Delete one row"""
        try:
            cur.execute("DELETE FROM questions WHERE question_id = %s", (str(self.id),))
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def obj_to_dict(self):
        """Convert object to dictionary (for use as JSON)"""
        question_dict = dict()
        question_dict['id'] = self.id
        question_dict['user_id'] = self.user_id
        question_dict['question'] = self.question
        question_dict['date_posted'] = self.date_posted
        return question_dict
