import psycopg2


class Answer:

    def __init__(self, answer_id, question_id, user_id, answer, votes, accepted, date_posted):
        self.id = answer_id
        self.question_id = question_id
        self.user_id = user_id
        self.answer = answer
        self.votes = votes
        self.accepted = accepted
        self.date_posted = date_posted

    def create(self, cur):
        """Create a new row"""
        try:
            sql = """INSERT INTO answers(question_id, user_id, answer_answer, answer_votes, answer_accepted, answer_date_posted) 
                                        VALUES(%s, %s, %s, %s, %s, %s) RETURNING answer_id"""
            cur.execute(sql, (
                str(self.question_id),
                str(self.user_id),
                self.answer,
                str(self.votes),
                self.accepted,
                self.date_posted))
            new_id = cur.fetchone()[0]
            return new_id
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    @staticmethod
    def read_all(cur, question_id):
        """Read all answers belonging to a specific question"""
        try:
            answers_list = []
            cur.execute(
                """SELECT answer_id, question_id, user_id, answer_answer, answer_votes, answer_accepted, answer_date_posted 
                  FROM answers WHERE question_id = """ + str(question_id))
            row = cur.fetchone()
            while row is not None:
                answers_list.append(Answer(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
                row = cur.fetchone()
            return answers_list
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    @staticmethod
    def read_one(cur, answer_id):
        """Read one row"""
        try:
            answer = None
            cur.execute(
                """SELECT answer_id, question_id, user_id, answer_answer, answer_votes, answer_accepted, answer_date_posted 
                  FROM answers WHERE answer_id=""" + str(answer_id))
            row = cur.fetchone()
            if row is not None:
                answer = Answer(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
            return answer
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def update(self, cur):
        """Update one row"""
        try:
            sql = """UPDATE answers SET question_id = %s, answer_answer = %s, answer_votes = %s, answer_accepted = %s 
                WHERE answer_id = %s"""
            cur.execute(sql, (
                str(self.question_id),
                self.answer,
                str(self.votes),
                str(self.accepted),
                str(self.id)))
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def delete(self, cur):
        """Delete one row"""
        try:
            cur.execute("DELETE FROM answers WHERE answer_id = %s", (str(self.id),))
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def obj_to_dict(self):
        """Convert object to dictionary (for use as JSON)"""
        answer_dict = dict()
        answer_dict['id'] = self.id
        answer_dict['question_id'] = self.question_id
        answer_dict['user_id'] = self.user_id
        answer_dict['answer'] = self.answer
        answer_dict['votes'] = self.votes
        answer_dict['accepted'] = self.accepted
        answer_dict['date_posted'] = self.date_posted
        return answer_dict
