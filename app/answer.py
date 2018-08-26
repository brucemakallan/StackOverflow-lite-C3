class Answer:

    def __init__(self, id, question_id, answer, accepted, date_posted):
        self.id = id
        self.question_id = question_id
        self.answer = answer
        self.accepted = accepted
        self.date_posted = date_posted

    def obj_to_dict(self):
        answer_dict = dict()
        answer_dict['id'] = self.id
        answer_dict['question_id'] = self.question_id
        answer_dict['answer'] = self.answer
        answer_dict['accepted'] = self.accepted
        answer_dict['date_posted'] = self.date_posted
        return answer_dict

