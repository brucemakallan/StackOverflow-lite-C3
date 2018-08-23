import datetime

from app.question import Question
from app.answer import Answer


class RawData:

    questions = []
    answers = []

    def __init__(self):
        # id, details, date
        add_element(Question(1, "What is a variable?", datetime.date(2018, 8, 1)), self.questions)
        add_element(Question(2, "What is an interpreted language?", datetime.date(2018, 8, 4)), self.questions)
        add_element(Question(3, "What does 'dynamically typed' mean?", datetime.date(2018, 8, 7)), self.questions)
        add_element(Question(4, "What is the difference between a String and an Integer?", datetime.date(2018, 8, 10)), self.questions)
        add_element(Question(5, "What is a programming language?", datetime.date(2018, 8, 12)), self.questions)

        # id, question_id, details, date
        add_element(Answer(1, 1, "A storage construct whose value can change", datetime.date(2018, 8, 3)), self.answers)
        add_element(Answer(2, 1, "A simple link to a location in memory", datetime.date(2018, 8, 4)), self.answers)
        add_element(Answer(3, 2, "An interpreted language doesn't need to be compiled", datetime.date(2018, 8, 4)), self.answers)
        add_element(Answer(4, 2, "An interpreted language ... another answer", datetime.date(2018, 8, 7)), self.answers)
        add_element(Answer(5, 2, "According to ... An interpreted language ... this is yet another answer", datetime.date(2018, 8, 12)), self.answers)
        add_element(Answer(6, 3, "One does not have to explicitly state the data-type of variables", datetime.date(2018, 8, 10)), self.answers)
        add_element(Answer(7, 4, "One is Stringy and the other is Integer-ry ;)", datetime.date(2018, 8, 3)), self.answers)
        add_element(Answer(8, 4, "Strings may contain any ASCII character while Integers do not", datetime.date(2018, 8, 1)), self.answers)
        add_element(Answer(9, 4, "Strings are ... while Integers are ...", datetime.date(2018, 8, 2)), self.answers)
        add_element(Answer(10, 4, "This is yet another answers about Strings and Integers", datetime.date(2018, 8, 6)), self.answers)


# only add element that doesn't already exist
def add_element(element, element_list):
    for item in element_list:
        if element.id == item.id:  # do not add elements that already exist based on ID
            return
    element_list.append(element)
