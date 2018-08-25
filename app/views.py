import datetime

from flask import jsonify, request, make_response

from app import create_app
from app.answer import Answer
from app.database.database_crud import get_all_questions, add_question, get_one_question
from app.question import Question


app = create_app()


@app.route("/api/v1/questions", methods=['GET'])
def api_questions():
    """Get all questions"""

    # fetch from the database
    list_of_question_objs = get_all_questions()
    if list_of_question_objs is not None:
        # Convert the list of question objects into a list of question dictionaries
        list_of_question_dicts = [question_obj.obj_to_dict() for question_obj in list_of_question_objs]
        return jsonify(list_of_question_dicts), 200
    else:
        return custom_response(204, 'No Content', 'There are no Questions in store')


@app.route("/api/v1/questions/<int:question_id>", methods=['GET'])
def api_quesiton(question_id):
    """Get a specific question using its id"""

    question_selected = []
    question_obj = get_one_question(question_id)
    if question_obj is None:
        return custom_response(404, 'Not Found', 'Question with id:' + str(question_id) + ' does not exist')
    question_selected.append(question_obj.obj_to_dict())
    return jsonify(question_selected), 200


@app.route("/api/v1/questions", methods=['POST'])
def api_add_question():
    """Post / Add a new question"""

    input_data = request.get_json(force=True)
    if 'question' not in input_data.keys():
        return custom_response(400, 'Bad Request', "Request must contain 'question' data")
    question = input_data['question']
    all_questions = get_all_questions()
    if all_questions is not None:
        for qn in all_questions:
            if qn.question.strip().lower() == question.strip().lower():  # check if question already exists
                return custom_response(409, 'Conflict', "Duplicate Value")
    date_posted = datetime.datetime.now()
    id = add_question(Question(0, question, date_posted))
    new_question = Question(id, question, date_posted)
    return jsonify(new_question.obj_to_dict()), 201


# @app.route("/api/v1/questions/<int:question_id>/answers", methods=['GET'])
# def api_answers(question_id):
#     """Get all answers to a specific question"""
#
#     # turn answer objects into dictionaries and store in one list
#     all_answers = [answer_obj.obj_to_dict() for answer_obj in RawData().answers if answer_obj.question_id == question_id]
#     if len(all_answers) == 0:
#         return custom_response(204, 'No Content', 'There are no Answers for the selected question')
#     return jsonify(all_answers), 200
#
#
# @app.route("/api/v1/questions/<int:question_id>/answers", methods=['POST'])
# def api_add_answer(question_id):
#     """Add an answer to a specific question"""
#
#     input_data = request.get_json(force=True)
#     if 'answer' not in input_data.keys():
#         return custom_response(400, 'Bad Request', "Request must contain 'answer' data")
#     answer = input_data['answer']
#     all_answers = RawData().answers
#     for ans in all_answers:
#         if ans.answer.strip().lower() == answer.strip().lower():  # check if value already exists
#             return custom_response(409, 'Conflict', "Duplicate Value")
#     date_posted = datetime.datetime.now()
#     id = RawData().answers[-1].id + 1
#     new_answer = Answer(id, question_id, answer, date_posted)
#     all_answers.append(new_answer)
#     return jsonify(new_answer.obj_to_dict()), 201


def custom_response(status_code, status_message, friendly_message):
    """Return a response with Status Code, its corresponding message, and a friendly message"""

    response = make_response(
        jsonify({'status_code': str(status_code) + ': ' + status_message + ', ' + friendly_message}),
        status_code)
    response.headers['Status-Code'] = str(status_code) + ': ' + status_message + ', ' + friendly_message
    return response
