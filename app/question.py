class Question:

    def __init__(self, id, question, date_posted):
        self.id = id
        self.question = question
        self.date_posted = date_posted

    def obj_to_dict(self):
        question_dict = dict()
        question_dict['id'] = self.id
        question_dict['question'] = self.question
        question_dict['date_posted'] = self.date_posted
        return question_dict
