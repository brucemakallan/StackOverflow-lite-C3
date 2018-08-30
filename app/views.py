import datetime
import os

from flask import jsonify, request, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app import create_app
from app.database import Database

from app.modals.answer import Answer
from app.modals.question import Question
from app.modals.user import User
from passlib.hash import pbkdf2_sha256 as sha256

# config_name is set from the terminal: set APP_SETTINGS=environment
config_name = os.getenv('APP_SETTINGS')
if not config_name:  # set default
    config_name = 'development'
app = create_app(config_name)

# Connect to the database (dependent on environment)
db = Database()


@app.route("/api/v1/questions", methods=['GET'])
@jwt_required
def api_get_all_questions():
    """Get all questions"""

    list_of_question_objects = Question.read_all(db.cur)
    if list_of_question_objects is not None:
        # Convert the list of objects into a list of dictionaries
        list_of_question_dicts = [question_obj.obj_to_dict() for question_obj in list_of_question_objects]
        if len(list_of_question_dicts) == 0:
            return custom_response(200, 'OK', 'Request Successful BUT There are no Questions in store')
        return jsonify(list_of_question_dicts), 200
    else:
        return custom_response(200, 'OK', 'Request Successful BUT There are no Questions in store')


@app.route("/api/v1/questions/<int:question_id>/answers", methods=['GET'])
@jwt_required
def api_get_answers(question_id):
    """Get all answers to a specific question"""

    list_of_answer_objects = Answer.read_all(db.cur, question_id)
    if list_of_answer_objects is not None:
        # Convert the list of objects into a list of dictionaries
        list_of_answer_dicts = [answer_obj.obj_to_dict() for answer_obj in list_of_answer_objects]
        if len(list_of_answer_dicts) == 0:
            return custom_response(200, 'OK', 'Request Successful BUT There are no Answers for this question')
        return jsonify(list_of_answer_dicts), 200
    else:
        return custom_response(200, 'OK', 'Request Successful BUT There are no Answers for this question')


@app.route("/api/v1/questions/<int:question_id>", methods=['GET'])
@jwt_required
def api_get_one_question(question_id):
    """Get a specific question using its id. Also fetch all answers for the question"""

    questions_with_answers = dict()
    question_obj = Question.read_one(db.cur, question_id)
    if question_obj is None:
        return custom_response(404, 'Not Found', 'Question with id:' + str(question_id) + ' does not exist')

    # get all answers for the question
    questions_with_answers['question'] = question_obj.obj_to_dict()
    answers_list = Answer.read_all(db.cur, question_id)
    if answers_list is not None:
        list_of_answer_dicts = [answer_obj.obj_to_dict() for answer_obj in answers_list]
        if len(list_of_answer_dicts) > 0:
            questions_with_answers['answers'] = list_of_answer_dicts

    return jsonify(questions_with_answers), 200


@app.route("/api/v1/questions", methods=['POST'])
@jwt_required
def api_add_question():
    """Post / Add a new question"""

    # get id of user currently logged in (from authentication token) and save it alongside the question
    current_user_id = get_jwt_identity()
    input_data = request.get_json(force=True)
    if 'question' not in input_data.keys():
        return custom_response(400, 'Bad Request', "Request must contain 'question' data")
    question = input_data['question'].strip()
    if len(question) == 0:
        return custom_response(400, 'Bad Request', "Provide a value for question")
    all_questions = Question.read_all(db.cur)
    if all_questions is not None:
        for qn in all_questions:
            if qn.question.strip().lower() == question.strip().lower():  # check if question already exists
                return custom_response(409, 'Conflict', "Duplicate Value. Question already exists")
    date_posted = datetime.datetime.now()
    new_id = Question(0, current_user_id, question, date_posted).create(db.cur)
    return jsonify(Question(new_id, current_user_id, question, date_posted).obj_to_dict()), 201  # 201 = created


@app.route("/api/v1/questions/<int:question_id>/answers", methods=['POST'])
@jwt_required
def api_add_answer(question_id):
    """Add an answer to a specific question"""

    # get id of user currently logged in (from authentication token)
    current_user_id = get_jwt_identity()
    input_data = request.get_json(force=True)
    if 'answer' not in input_data.keys():
        return custom_response(400, 'Bad Request', "Request must contain 'answer' data")
    answer = input_data['answer'].strip()
    if len(answer) == 0:
        return custom_response(400, 'Bad Request', "Provide a value for answer")
    all_answers = Answer.read_all(db.cur, question_id)

    # make sure the question for which the answer is to be posted is present
    question = Question.read_one(db.cur, question_id)
    if question is not None:
        for ans in all_answers:
            if ans.answer.strip().lower() == answer.strip().lower():  # check if value already exists
                return custom_response(409, 'Conflict', "Duplicate Value. Answer already exists")
        accepted = 'false'
        date_posted = datetime.datetime.now()
        new_id = Answer(0, question_id, current_user_id, answer, accepted, date_posted).create(db.cur)
        return jsonify(Answer(new_id, question_id, current_user_id, answer, accepted, date_posted).obj_to_dict()), 201
    else:
        return custom_response(404, 'Not Found', 'Question with id:' + str(question_id) + ' does not exist')


@app.route("/api/v1/questions/<int:questionId>", methods=['DELETE'])
@jwt_required
def api_delete_question(questionId):
    """Delete a specific question based on id"""

    # get object from database
    all_questions = Question.read_all(db.cur)
    if all_questions is not None:
        for qn in all_questions:
            if qn.id == questionId:
                qn.delete(db.cur)
                return custom_response(202, 'Accepted', 'Question with id, ' + str(questionId) + ' was deleted')
        return custom_response(404, 'Not Found', 'No question in store matching the id')
    else:
        return custom_response(200, 'OK', 'Request Successful BUT There are no Answers in store')


@app.route("/api/v1/questions/<int:questionId>/answers/<int:answerId>", methods=['PUT'])
@jwt_required
def api_update_answer(questionId, answerId):
    """Update an answer to a specific question"""

    # get new answer values
    input_data = request.get_json(force=True)

    all_answers = Answer.read_all(db.cur, questionId)
    if all_answers is not None:
        for ans in all_answers:
            if ans.id == answerId:  # check if answer exists
                # replace old values with new ones if available
                answer_edited = False
                if 'accepted' in input_data.keys():
                    new_accepted_value = input_data['accepted']  # boolean
                    # validate accepted value (must be a valid boolean value for postgres)
                    if isinstance(new_accepted_value, bool):
                        ans.accepted = new_accepted_value
                        answer_edited = True
                    else:
                        return custom_response(400, 'Bad Request', "Provide 'accepted' data as a boolean (true OR false)")
                if 'answer' in input_data.keys():
                    new_answer_value = input_data['answer'].strip()
                    if len(new_answer_value) == 0:
                        return custom_response(400, 'Bad Request', "Provide a value for 'answer'")
                    ans.answer = new_answer_value
                    answer_edited = True
                if answer_edited:
                    ans.update(db.cur)
                    return jsonify(ans.obj_to_dict()), 202  # HTTP_202_ACCEPTED
                else:
                    return custom_response(400, 'Bad Request', "Provide 'answer' data to edit answer, OR 'accepted' data (as a boolean) to edit accepted status")

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
    if len(str(username).strip()) == 0:
        return custom_response(400, 'Bad Request', "Provide a username")
    password = input_data['password']
    if len(str(password).strip()) == 0:
        return custom_response(400, 'Bad Request', "Provide a password")
    all_users = User.read_all(db.cur)
    if all_users is not None:
        for user in all_users:
            if user.username.strip().lower() == username.strip().lower():  # check if user already exists
                return custom_response(409, 'Conflict', "Duplicate Value. Username is already taken")
    new_id = User(0, username, password).create(db.cur)  # add to database and return new id
    user_dict = User(new_id, username, sha256.hash(password)).obj_to_dict()
    # don't show password in the returned JSON
    del user_dict['password']
    # create token
    access_token = create_access_token(identity=new_id)
    user_dict['access_token'] = access_token
    user_dict['msg'] = 'User Registration Successful!'
    return jsonify(user_dict), 201


@app.route("/api/v1/auth/login", methods=['POST'])
def login_user():
    """User verification and Login"""

    input_data = request.get_json(force=True)

    # validation check for required values
    if 'username' not in input_data.keys() or 'password' not in input_data.keys():
        return custom_response(400, 'Bad Request', "Request must contain 'username' and 'password' data")
    username = input_data['username'].strip()
    if len(username) == 0:
        return custom_response(400, 'Bad Request', "Provide a username")
    password = input_data['password']
    if len(password.strip()) == 0:
        return custom_response(400, 'Bad Request', "Provide a password")

    # get all users and check if username and password match
    all_users = User.read_all(db.cur)
    if all_users is not None:
        for user in all_users:
            # verify that password and username match those of a user in the database
            if username.strip() == user.username.strip() and sha256.verify(password, user.password):
                # don't show password in the returned JSON
                user_dict = user.obj_to_dict()
                del user_dict['password']

                # create token
                access_token = create_access_token(identity=user.id)
                user_dict['access_token'] = access_token
                user_dict['msg'] = 'Login Successful!'
                return jsonify(user_dict), 200  # return user with access token
        # if the iterations do not find any matching user, return message:
        return custom_response(403, 'Forbidden', 'Invalid Login Credentials')
    else:
        return custom_response(200, "OK", "Request Successful BUT There are no users in store")


@app.errorhandler(404)
def page_not_found(e):  # Page not found
    return custom_response(404, 'Resource Not Found', 'You are trying to access a resource that does not exist')


@app.errorhandler(400)
def bad_request(e):  # Bad request e.g. missing JSON post request data
    return custom_response(400, 'Bad request', 'Provide POST request data as valid JSON')


def custom_response(status_code, status_message, friendly_message):
    """Return a response with Status Code, its corresponding message, and a friendly message"""

    response = make_response(
        jsonify({'status_code': str(status_code) + ': ' + status_message + ', ' + friendly_message}),
        status_code)
    response.headers['Status-Code'] = str(status_code) + ': ' + status_message + ', ' + friendly_message
    return response
