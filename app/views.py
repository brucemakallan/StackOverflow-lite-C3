import datetime
import os

import re
from flask import jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app import create_app
from app.database import Database

from app.modals.answer import Answer
from app.modals.question import Question
from app.modals.user import User
from passlib.hash import pbkdf2_sha256 as sha256

from app.validator import Validator

config_name = os.getenv('APP_SETTINGS')
if not config_name:  # default set to 'development'
    config_name = 'development'
app = create_app(config_name)

# Connect to the database (dependent on environment)
db = Database(app)


@app.route("/api/v1/questions", methods=['GET'])
@jwt_required
def api_get_all_questions():
    """Get all questions"""
    return Validator.check_for_content(Question.read_all(db.cur), 'There are no Questions in store')


@app.route("/api/v1/answers", methods=['GET'])
@jwt_required
def api_get_all_answers():
    """Get all answers"""
    return Validator.check_for_content(Answer.read_all_answers(db.cur), 'There are no Answers')


@app.route("/api/v1/questions/<int:question_id>/answers", methods=['GET'])
@jwt_required
def api_get_answers(question_id):
    """Get all answers to a specific question"""
    return Validator.check_for_content(Answer.read_all(db.cur, question_id), 'There are no Answers for this question')


@app.route("/api/v1/questions/<int:question_id>", methods=['GET'])
@jwt_required
def api_get_one_question(question_id):
    """Get a specific question using its id. Also fetch all answers for the question"""

    questions_with_answers = dict()
    question_obj = Question.read_one(db.cur, question_id)
    if question_obj is None:
        return Validator.custom_response(404, 'Not Found', 'Question with id:' + str(question_id) + ' does not exist')

    # get all answers for the question
    questions_with_answers['question'] = question_obj.obj_to_dict()
    answers_list = Answer.read_all(db.cur, question_id)
    if answers_list is not None:
        list_of_answer_dicts = [answer_obj.obj_to_dict()
                                for answer_obj in answers_list]
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
        return Validator.custom_response(400, 'Bad Request', "Request must contain 'question' data")
    question = input_data['question'].strip()
    if len(question) == 0:
        return Validator.custom_response(400, 'Bad Request', "Provide a value for question")
    all_questions = Question.read_all(db.cur)
    if all_questions is not None:
        for qn in all_questions:
            if qn.question.strip().lower() == question.strip().lower():  # check if question already exists
                return Validator.custom_response(409, 'Conflict', "Duplicate Value. Question already exists")
    date_posted = datetime.datetime.now()
    new_id = Question(0, current_user_id, question, date_posted).create(db.cur)
    # 201 = created
    return jsonify(Question(new_id, current_user_id, question, date_posted).obj_to_dict()), 201


@app.route("/api/v1/questions/<int:question_id>/answers", methods=['POST'])
@jwt_required
def api_add_answer(question_id):
    """Add an answer to a specific question"""

    # get id of user currently logged in (from authentication token)
    current_user_id = get_jwt_identity()
    input_data = request.get_json(force=True)
    if 'answer' not in input_data.keys():
        return Validator.custom_response(400, 'Bad Request', "Request must contain 'answer' data")
    answer = input_data['answer'].strip()
    if len(answer) == 0:
        return Validator.custom_response(400, 'Bad Request', "Provide a value for answer")
    all_answers = Answer.read_all(db.cur, question_id)

    # make sure the question for which the answer is to be posted is present
    question = Question.read_one(db.cur, question_id)
    if question is not None:
        for ans in all_answers:
            if ans.answer.strip().lower() == answer.strip().lower():  # check if value already exists
                return Validator.custom_response(409, 'Conflict', "Duplicate Value. Answer already exists")
        accepted = 'false'
        date_posted = datetime.datetime.now()
        new_id = Answer(0, question_id, current_user_id, answer,
                        0, accepted, date_posted).create(db.cur)
        return jsonify(Answer(new_id, question_id, current_user_id, answer, 0, accepted, date_posted).obj_to_dict()), 201
    else:
        return Validator.custom_response(404, 'Not Found', 'Question with id:' + str(question_id) + ' does not exist')


@app.route("/api/v1/questions/<int:question_id>", methods=['DELETE'])
@jwt_required
def api_delete_question(question_id):
    """Delete a specific question based on id"""

    # get object from database
    all_questions = Question.read_all(db.cur)
    if all_questions is not None:
        for qn in all_questions:
            if qn.id == question_id:
                # only the owner of the question can delete it
                if qn.user_id != get_jwt_identity():
                    return Validator.custom_response(403, 'Forbidden',
                                                     "You do not have permission to delete this question")
                qn.delete(db.cur)
                return Validator.custom_response(202, 'Accepted',
                                                 'Question with id, ' + str(question_id) + ' was deleted')
        return Validator.custom_response(404, 'Not Found', 'No question in store matching the id')
    else:
        return Validator.custom_response(200, 'OK', 'Request Successful BUT There are no Questions in store')


@app.route("/api/v1/questions/<int:question_id>/answers/<int:answer_id>", methods=['PUT'])
@jwt_required
def api_update_answer(question_id, answer_id):
    """Update an answer to a specific question"""

    # get new answer values
    input_data = request.get_json(force=True)

    all_answers = Answer.read_all(db.cur, question_id)
    if all_answers is not None:
        for ans in all_answers:
            if ans.id == answer_id:  # check if answer exists
                # replace old values with new ones if available
                answer_edited = False
                if 'accepted' in input_data.keys():
                    new_accepted_value = input_data['accepted']  # boolean
                    # validate accepted value (must be a valid boolean value for postgres)
                    if isinstance(new_accepted_value, bool):
                        # make sure it's the user who posted the question accepting the answer
                        qn = Question.read_one(db.cur, question_id)
                        if qn.user_id != get_jwt_identity():
                            return Validator.custom_response(403, 'Forbidden',
                                                             "You do not have permission to accept this answer")
                        ans.accepted = new_accepted_value
                        answer_edited = True
                    else:
                        return Validator.custom_response(400, 'Bad Request',
                                                         "Provide 'accepted' data as a boolean (true OR false)")
                if 'answer' in input_data.keys():
                    new_answer_value = input_data['answer'].strip()
                    if len(new_answer_value) == 0:
                        return Validator.custom_response(400, 'Bad Request', "Provide a value for 'answer'")
                    if ans.user_id != get_jwt_identity():  # only the answer owner can edit it
                        return Validator.custom_response(403, 'Forbidden',
                                                         "You do not have permission to edit this answer")
                    ans.answer = new_answer_value
                    answer_edited = True

                if 'vote' in input_data.keys():
                    new_vote_value = input_data['vote']  # boolean
                    if isinstance(new_vote_value, bool):
                        if new_vote_value:
                            ans.votes += 1  # add a vote
                        else:
                            ans.votes -= 1  # remove a vote
                        answer_edited = True
                    else:
                        return Validator.custom_response(400, 'Bad Request',
                                                         "Provide 'vote' data as a boolean (true OR false)")

                if answer_edited:
                    ans.update(db.cur)
                    return jsonify(ans.obj_to_dict()), 202  # HTTP_202_ACCEPTED
                else:
                    return Validator.custom_response(400,
                                                     'Bad Request',
                                                     """Provide 'answer' data to edit answer, OR 'accepted' data (as a boolean) to edit accepted status OR 'vote' data (as a boolean) to up-vote or down-vote""")

        # Answer does not exist
        return Validator.custom_response(404, 'Not Found', 'No Answer found with id, ' + str(answer_id))
    else:  # Question does not exist
        return Validator.custom_response(404, 'Not Found', 'No answers for the question')


@app.route("/api/v1/auth/signup", methods=['POST'])
def register_user():
    """Post / Add a new user"""

    # validate presence of appropriate data
    input_data = request.get_json(force=True)
    if 'full_name' not in input_data.keys():
        return Validator.custom_response(400, 'Bad Request', "Request must contain 'full_name' data")
    if 'email' not in input_data.keys():
        return Validator.custom_response(400, 'Bad Request', "Request must contain 'email' data")
    if 'password' not in input_data.keys():
        return Validator.custom_response(400, 'Bad Request', "Request must contain 'password' data")
    if 'retype_password' not in input_data.keys():
        return Validator.custom_response(400, 'Bad Request', "Request must contain 'retype_password' data")

    password = input_data['password']
    if len(str(password)) < 6:
        return Validator.custom_response(400, 'Bad Request', "Password must be at least 6 characters long")
    full_name = input_data['full_name']
    if len(str(full_name).strip()) == 0:
        return Validator.custom_response(400, 'Bad Request', "Provide a name")
    email = input_data['email']
    if len(str(email).strip()) == 0:
        return Validator.custom_response(400, 'Bad Request', "Provide an email address")
    # email validator
    if not re.match(r"^[A-Za-z0-9.+_-]+@[A-Za-z0-9._-]+\.[a-zA-Z]+$", email):
        return Validator.custom_response(400, 'Bad Request', "Invalid email format")
    retype_password = input_data['retype_password']
    if len(str(retype_password)) == 0:
        return Validator.custom_response(400, 'Bad Request', "Retype password")

    # check if user already exists (compare emails)
    all_users = User.read_all(db.cur)
    if all_users is not None:
        for user in all_users:
            if user.email.strip().lower() == email.strip().lower():
                return Validator.custom_response(409, 'Conflict', "Duplicate Value. Email Address is already taken")

    # check if passwords match
    if password != retype_password:
        return Validator.custom_response(400, 'Bad Request', "Password mismatch")

    # if all is well; Add to database and return new id
    new_id = User(0, full_name, email, password).create(db.cur)
    user_dict = User(new_id, full_name, email,
                     sha256.hash(password)).obj_to_dict()

    # create token
    access_token = create_access_token(identity=new_id, expires_delta=False)
    user_dict['access_token'] = access_token
    user_dict['msg'] = 'User Registration Successful!'
    return jsonify(user_dict), 201


@app.route("/api/v1/auth/login", methods=['POST'])
def login_user():
    """User verification and Login"""

    input_data = request.get_json(force=True)

    # validation check for required values
    if 'email' not in input_data.keys() or 'password' not in input_data.keys():
        return Validator.custom_response(400, 'Bad Request', "Request must contain 'email' and 'password' data")
    email = input_data['email'].strip()
    if len(email) == 0:
        return Validator.custom_response(400, 'Bad Request', "Provide an email address")
    password = input_data['password']
    if len(password.strip()) == 0:
        return Validator.custom_response(400, 'Bad Request', "Provide a password")

    # get all users and check if email and password match
    all_users = User.read_all(db.cur)
    if all_users is not None:
        for user in all_users:
            if email.strip().lower() == user.email.strip().lower() and sha256.verify(password, user.password):
                user_dict = user.obj_to_dict()
                # create token
                access_token = create_access_token(
                    identity=user.id, expires_delta=False)
                user_dict['access_token'] = access_token
                user_dict['msg'] = 'Login Successful!'
                return jsonify(user_dict), 200  # return user with access token
        # if the iterations do not find any matching user, return message:
        return Validator.custom_response(403, 'Forbidden', 'Invalid Login Credentials')
    else:
        return Validator.custom_response(200, "OK", "Request Successful BUT There are no users in store")


@app.errorhandler(404)
def page_not_found(e):  # Page not found
    return Validator.custom_response(404, 'Resource Not Found',
                                     'You are trying to access a resource that does not exist')


@app.errorhandler(400)
def bad_request(e):  # Bad request e.g. missing JSON post request data
    return Validator.custom_response(400, 'Bad request', 'Provide POST request data as valid JSON')
