import unittest

from flask import json

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
        self.user_data3 = dict(username="jane", password="password")
        self.wrong_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MzU2NjgmmTAsIm5iZiI6MTUzNTY2ODU1MCwianRpIjoiZjA0MTVmODUtYjBkNC00MWYwLWFmMTAtNzU5YjhmNzgxY2Q0IiwiZXhwIjoxNTM1NjY5NDUwLCJpZGVudGl0eSI6MSwiZnJlc2giOmZhbHNlLCJ0eXBlIjoiYWNjZXNzIn0.9WTmhO49Ta2M3tvNuuUME52zObxW14jenCsIOFKo_cg'

        # connect to the database using current App-Settings
        # set APP_SETTINGS="testing"
        self.database_obj = Database()

        # get Authorization token (used for all protected endpoints)
        signup_response = self.client.post('/api/v1/auth/signup',
                                           data=json.dumps(self.user_data2),
                                           content_type='application/json')
        token_json_dict = json.loads(signup_response.data.decode())
        self.access_token = token_json_dict['access_token']

    # test for endpoints. Run using $pytest --cov=app/
    def test_sign_up(self):
        """Run test for: Register a new User"""
        signup_response = self.client.post('/api/v1/auth/signup',
                                           data=json.dumps(self.user_data),
                                           content_type='application/json')
        self.assertIn("jane", str(signup_response.data))  # check if test username is returned after signup as it should
        self.assertEqual(signup_response.status_code, 201)  # 201: Created

    def test_login(self):
        """Run test for: Successful Login"""
        self.test_sign_up()
        login_response = self.client.post('/api/v1/auth/login',
                                          data=json.dumps(self.user_data),
                                          content_type='application/json')
        self.assertIn("jane", str(login_response.data))
        self.assertEqual(login_response.status_code, 200)

    def test_invalid_login(self):
        """Run test for: Invalid login credentials"""
        self.test_sign_up()
        login_response = self.client.post('/api/v1/auth/login',
                                          data=json.dumps(self.user_data3),
                                          content_type='application/json')
        self.assertIn("Invalid Login Credentials", str(login_response.data))
        self.assertEqual(login_response.status_code, 403)  # 403 Forbidden

    def test_no_authorization(self):
        """Run test for: Wrong access token"""
        post_response = self.client.post('/api/v1/questions',
                                         data=json.dumps(self.test_data_question2),
                                         content_type='application/json',
                                         headers={'Authorization': 'Bearer {}'.format(self.wrong_token)})
        self.assertIn('Signature verification failed', str(post_response.data))

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
