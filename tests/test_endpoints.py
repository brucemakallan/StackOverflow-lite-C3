import unittest

from flask import json

from app.database import Database
from app.views import app

from tests.test_data import TestData


class EndpointsTestCase(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client(self)

        # RUN 'set APP_SETTINGS=testing' to set testing environment (for database)
        self.database_obj = Database(app)

        # get Authorization token (used for all protected endpoints)
        signup_response = self.client.post('/api/v1/auth/signup',
                                           data=json.dumps(TestData.user_data2),
                                           content_type='application/json')
        token_json_dict = json.loads(signup_response.data.decode())
        self.access_token = token_json_dict['access_token']

    # test for endpoints. Run using $pytest --cov=app/
    def test_sign_up(self):
        """Run test for: Register a new User"""
        signup_response = self.client.post('/api/v1/auth/signup',
                                           data=json.dumps(TestData.user_data),
                                           content_type='application/json')
        # check if test user data is returned after signup as it should
        self.assertIn("Jane Doe", str(signup_response.data))
        self.assertIn("jane@gmail.com", str(signup_response.data))
        self.assertEqual(signup_response.status_code, 201)  # 201: Created

    def test_login(self):
        """Run test for: Successful Login"""
        self.test_sign_up()
        login_response = self.client.post('/api/v1/auth/login',
                                          data=json.dumps(TestData.user_data),
                                          content_type='application/json')
        self.assertIn("Jane Doe", str(login_response.data))
        self.assertIn("jane@gmail.com", str(login_response.data))
        self.assertEqual(login_response.status_code, 200)

    def test_invalid_login(self):
        """Run test for: Invalid login credentials"""
        self.test_sign_up()
        login_response = self.client.post('/api/v1/auth/login',
                                          data=json.dumps(TestData.user_data3),
                                          content_type='application/json')
        self.assertIn("Invalid Login Credentials", str(login_response.data))
        self.assertEqual(login_response.status_code, 403)  # 403 Forbidden

    def test_no_authorization(self):
        """Run test for: Wrong access token"""
        post_response = self.client.post('/api/v1/questions',
                                         data=json.dumps(TestData.test_data_question2),
                                         content_type='application/json',
                                         headers={'Authorization': 'Bearer {}'.format(TestData.wrong_token)})
        self.assertIn('Signature verification failed', str(post_response.data))

    def test_post_question(self):
        """Run test for: Post a question"""
        post_response = self.client.post('/api/v1/questions',
                                         data=json.dumps(TestData.test_data_question2),
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
                         data=json.dumps(TestData.test_data_question1),
                         content_type='application/json',
                         headers={'Authorization': 'Bearer {}'.format(self.access_token)})
        # post again and run test for Duplicate Value
        post_response = self.client.post('/api/v1/questions',
                                         data=json.dumps(TestData.test_data_question1),
                                         content_type='application/json',
                                         headers={'Authorization': 'Bearer {}'.format(self.access_token)})
        self.assertEqual(post_response.status_code, 409)  # 409 Conflict (Due to duplicate value)
        self.assertIn('Duplicate Value. Question already exists', str(post_response.data))  # check for error message

    def test_post_answer(self):
        """Run test for: Post an answer to a specific question"""
        # read all questions, get one question's id and pass it in the endpoint to post an answer for it
        response_data = self.test_get_all_questions()
        all_questions_list = json.loads(response_data.data.decode())
        sample_question = all_questions_list[0]
        url = '/api/v1/questions/' + str(sample_question['id']) + '/answers'
        post_response = self.client.post(url,
                                         data=json.dumps(TestData.test_data_answer),
                                         content_type='application/json',
                                         headers={'Authorization': 'Bearer {}'.format(self.access_token)})
        self.assertEqual(post_response.status_code, 201)
        self.assertIn('Test answer sample one', str(post_response.data))

    def test_invalid_urls(self):
        """Run test for: Invalid URLs"""
        get_response = self.client.get('/api/v1/abc',
                                       content_type='application/json')
        self.assertIn('Resource Not Found', str(get_response.data))
        self.assertEqual(get_response.status_code, 404)  # 404 NOT FOUND

    def tearDown(self):
        """Drop all tables in the TEST database"""
        tables = ['users', 'answers', 'questions']
        self.database_obj.drop_all_tables(tables)
