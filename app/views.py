import datetime

from flask import jsonify, request, make_response

from app import create_app
from app.database import Database

from app.modals.answer import Answer
from app.modals.question import Question
from app.modals.user import User


app = create_app()

# get database object for connection to the database
database_obj = Database()


@app.route("/api/v1/questions", methods=['GET'])
def api_get_all_questions():
    """Get all questions"""

    list_of_question_objs = database_obj.get_all_entities('questions')
    if list_of_question_objs is not None:
        # Convert the list of objects into a list of dictionaries
        list_of_question_dicts = [question_obj.obj_to_dict() for question_obj in list_of_question_objs]
        return jsonify(list_of_question_dicts), 200
    else:
        return custom_response(204, 'No Content', 'There are no Questions in store')


@app.route("/api/v1/questions/<int:question_id>/answers", methods=['GET'])
def api_get_answers(question_id):
    """Get all answers to a specific question"""

    list_of_answer_objs = database_obj.get_all_entities('answers', question_id)
    if list_of_answer_objs is not None:
        # Convert the list of objects into a list of dictionaries
        list_of_answer_dicts = [answer_obj.obj_to_dict() for answer_obj in list_of_answer_objs]
        return jsonify(list_of_answer_dicts), 200
    else:
        return custom_response(204, 'No Content', 'There are no Answers in store')


@app.route("/api/v1/questions/<int:question_id>", methods=['GET'])
def api_get_one_question(question_id):
    """Get a specific question using its id"""

    question_selected = []
    question_obj = database_obj.get_one_entity('questions', question_id)
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
    all_questions = database_obj.get_all_entities('questions')
    if all_questions is not None:
        for qn in all_questions:
            if qn.question.strip().lower() == question.strip().lower():  # check if question already exists
                return custom_response(409, 'Conflict', "Duplicate Value")
    date_posted = datetime.datetime.now()
    new_id = database_obj.add_entity(Question(0, 0, question, date_posted))  # add to database and return new id
    return jsonify(Question(new_id, 0, question, date_posted).obj_to_dict()), 201


@app.route("/api/v1/questions/<int:question_id>/answers", methods=['POST'])
def api_add_answer(question_id):
    """Add an answer to a specific question"""

    input_data = request.get_json(force=True)
    if 'answer' not in input_data.keys():
        return custom_response(400, 'Bad Request', "Request must contain 'answer' data")
    answer = input_data['answer']
    all_answers = database_obj.get_all_entities('answers', question_id)
    for ans in all_answers:
        if ans.answer.strip().lower() == answer.strip().lower():  # check if value already exists
            return custom_response(409, 'Conflict', "Duplicate Value")
    accepted = 'false'
    date_posted = datetime.datetime.now()
    new_id = database_obj.add_entity(Answer(0, question_id, 0, answer, accepted, date_posted))
    return jsonify(Answer(new_id, question_id, 0, answer, accepted, date_posted).obj_to_dict()), 201


@app.route("/api/v1/questions/<int:questionId>", methods=['DELETE'])
def api_delete_question(questionId):
    """Delete a specific question based on id"""

    # get object from database
    all_questions = database_obj.get_all_entities('questions')
    if all_questions is not None:
        for qn in all_questions:
            if qn.id == questionId:
                database_obj.delete_entity(qn)
                return custom_response(202, 'Accepted', 'Question with id, ' + str(questionId) + ' was deleted')
        return custom_response(404, 'Not Found', 'No question in store matching the id')
    else:
        return custom_response(204, 'No Content', 'There are no Answers in store')


@app.route("/api/v1/questions/<int:questionId>/answers/<int:answerId>", methods=['PUT'])
def api_update_answer(questionId, answerId):
    """Update an answer to a specific question"""

    # get new answer values
    input_data = request.get_json(force=True)
    if 'answer' not in input_data.keys():
        return custom_response(400, 'Bad Request', "Request must contain 'answer' data")
    new_accepted_value = 'false'
    if 'accepted' in input_data.keys():
        new_accepted_value = input_data['accepted']
    new_answer_value = input_data['answer']

    all_answers = database_obj.get_all_entities('answers', questionId)
    if all_answers is not None:
        for ans in all_answers:
            if ans.id == answerId:  # check if answer exists
                # replace old values with new ones if available
                ans.answer = new_answer_value
                ans.accepted = new_accepted_value
                database_obj.update_entity(ans)
                return jsonify(ans.obj_to_dict()), 202  # HTTP_202_ACCEPTED

        # Answer does not exist
        return custom_response(404, 'Not Found', 'No Answer found with id, ' + str(answerId))
    else:  # Question does not exist
        return custom_response(404, 'Not Found', 'No answers for the question')


@app.route("/api/v1/auth/signup", methods=['POST'])
def register_user():
    """Post / Add a new user"""

    input_data = request.get_json(force=True)
    if 'username' not in input_data.keys() or 'password' not in input_data.keys():
        return custom_response(400, 'Bad Request', "Request must contain 'username' and 'password' data")
    username = input_data['username']
    password = input_data['password']
    all_users = database_obj.get_all_entities('users')
    if all_users is not None:
        for user in all_users:
            if user.username.strip().lower() == username.strip().lower():  # check if user already exists
                return custom_response(409, 'Conflict', "Duplicate Value")
    new_id = database_obj.add_entity(User(0, username, password))  # add to database and return new id
    return jsonify(User(new_id, username, password).obj_to_dict()), 201


def custom_response(status_code, status_message, friendly_message):
    """Return a response with Status Code, its corresponding message, and a friendly message"""

    response = make_response(
        jsonify({'status_code': str(status_code) + ': ' + status_message + ', ' + friendly_message}),
        status_code)
    response.headers['Status-Code'] = str(status_code) + ': ' + status_message + ', ' + friendly_message
    return response
