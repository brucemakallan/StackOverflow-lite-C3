import unittest

from flask import json
from flask_jwt_extended import JWTManager

from app.database import Database
from app.views import app


class EndpointsTestCase(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client(self)

        # test data
        self.test_data_question1 = dict(question='Test question sample one')
        self.test_data_question2 = dict(question='Test question sample two')
        self.test_data_question3 = dict(question='Test question sample three')
        self.test_data_question4 = dict(question='Test question sample four')
        self.test_data_answer = dict(answer="Test answer sample one")
        self.user_data = dict(username="jane", password="pass")
        self.user_data2 = dict(username="annie", password="pass")

        self.database_obj = Database()  # connection to the database
        app.config['JWT_SECRET_KEY'] = 'kk38e1c32de0961d5d3bfb14f8a66e006cfb1cfbf3f0c0f5'
        JWTManager(app)

        # get Authorization token (used for all protected endpoints)
        signup_response = self.client.post('/api/v1/auth/signup',
                                           data=json.dumps(self.user_data2),
                                           content_type='application/json')
        token_json_dict = json.loads(signup_response.data.decode())
        self.access_token = token_json_dict['access_token']

    # test for endpoints. Run using $pytest
    def test_sign_up(self):
        """Run test for: Register a new User"""
        signup_response = self.client.post('/api/v1/auth/signup',
                                           data=json.dumps(self.user_data),
                                           content_type='application/json')
        self.assertIn("jane", str(signup_response.data))  # check if test username is returned after signup as it should
        self.assertEqual(signup_response.status_code, 201)  # 201: Created

    def test_post_question(self):
        """Run test for: Post a question"""
        post_response = self.client.post('/api/v1/questions',
                                         data=json.dumps(self.test_data_question2),
                                         content_type='application/json',
                                         headers={'Authorization': 'Bearer {}'.format(self.access_token)})
        self.assertEqual(post_response.status_code, 201)
        self.assertIn('Test question sample two', str(post_response.data))
        return post_response

    def test_get_all_questions(self):
        """Run test for: Get all questions"""
        # first get a post response from the responsible method then read data from it
        get_response = self.client.get('/api/v1/questions',
                                       content_type='application/json',
                                       data=json.loads(self.test_post_question().data.decode()),
                                       headers={'Authorization': 'Bearer {}'.format(self.access_token)})
        self.assertEqual(get_response.status_code, 200)
        self.assertIn('Test question sample two', str(get_response.data))
        return get_response

    def test_post_duplicate_question(self):
        """Run test for: Post a duplicate question"""

        self.client.post('/api/v1/questions',
                                         data=json.dumps(self.test_data_question1),
                                         content_type='application/json',
                                         headers={'Authorization': 'Bearer {}'.format(self.access_token)})
        # post again and run test for Duplicate Value
        post_response = self.client.post('/api/v1/questions',
                                         data=json.dumps(self.test_data_question1),
                                         content_type='application/json',
                                         headers={'Authorization': 'Bearer {}'.format(self.access_token)})
        self.assertEqual(post_response.status_code, 409)  # 409 Conflict (Due to duplicate value)
        self.assertIn('Duplicate Value. Question already exists', str(post_response.data))  # check for error message

    # def test_get_one_question(self):
    #     """Run test for: Get one question using its id"""
    #     # read all questions, get one question's id and try to read it from the database using that id
    #     response_data = self.test_get_all_questions()
    #     all_questions_list = json.loads(response_data.data.decode())
    #     sample_question = all_questions_list[0]
    #     url = '/api/v1/questions/' + str(sample_question['id'])
    #     get_response = self.client.get(url,
    #                                    content_type='application/json',
    #                                    data=json.loads(response_data.data.decode()),
    #                                    headers={'Authorization': 'Bearer {}'.format(self.access_token)})
    #     self.assertEqual(get_response.status_code, 200)
    #     self.assertIn(str(sample_question['id']), str(get_response.data))

    def test_post_answer(self):
        """Run test for: Post an answer to a specific question"""
        # read all questions, get one question's id and pass it in the endpoint to post an answer for it
        response_data = self.test_get_all_questions()
        all_questions_list = json.loads(response_data.data.decode())
        sample_question = all_questions_list[0]
        url = '/api/v1/questions/' + str(sample_question['id']) + '/answers'
        post_response = self.client.post(url,
                                         data=json.dumps(self.test_data_answer),
                                         content_type='application/json',
                                         headers={'Authorization': 'Bearer {}'.format(self.access_token)})
        self.assertEqual(post_response.status_code, 201)
        self.assertIn('Test answer sample one', str(post_response.data))

    def tearDown(self):
        """Remove all sample entities used from database"""
        self.database_obj.delete_entity_by_value("users", "user_username", "annie")
        self.database_obj.delete_entity_by_value("users", "user_username", "jane")
        self.database_obj.delete_entity_by_value("questions", "question_question", "Test question sample one")
        self.database_obj.delete_entity_by_value("questions", "question_question", "Test question sample two")
        self.database_obj.delete_entity_by_value("questions", "question_question", "Test question sample three")
        self.database_obj.delete_entity_by_value("questions", "question_question", "Test question sample four")
        self.database_obj.delete_entity_by_value("answers", "answer_answer", "Test answer sample one")
