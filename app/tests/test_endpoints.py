import unittest

from flask import json

from app.views import app


class EndpointsTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = True
        self.client = app.test_client(self)
        self.test_data_question1 = dict(question='Test question 1')
        self.test_data_question2 = dict(question='Test question 2')
        self.test_data_question3 = dict(question='Test question 3')
        self.test_data_answer = dict(answer="Test answer 1")

    # TODO
    # def tearDown(self):
        # drop all tables from the test database
        # tables = ['users', 'answers', 'questions']
        # for table in tables:
        #     database_obj.drop_table(table)

    # test for endpoints. Run using $pytest
    def test_get_all_questions(self):
        """Run test for: Get all questions"""

        post_response = self.client.post('/api/v1/questions', data=json.dumps(self.test_data_question1), content_type='application/json')
        # check for duplicate value
        if 'Duplicate Value' in str(post_response.data):
            self.assertEqual(post_response.status_code, 409)  # 409 Conflict (Due to duplicate value)
        else:
            self.assertEqual(post_response.status_code, 201)
            self.assertIn('Test question 1', str(post_response.data))  # check response content after post request
            get_response = self.client.get('/api/v1/questions', content_type='application/json', data=json.loads(post_response.data.decode()))
            self.assertEqual(get_response.status_code, 200)
            self.assertIn('Test question 1', str(get_response.data))  # check response content after get request

    def test_post_question(self):
        """Run test for: Post a question"""

        post_response = self.client.post('/api/v1/questions', data=json.dumps(self.test_data_question2), content_type='application/json')
        if 'Duplicate Value' in str(post_response.data):
            self.assertEqual(post_response.status_code, 409)  # 409 Conflict (Due to duplicate value)
        else:
            self.assertEqual(post_response.status_code, 201)
            self.assertIn('Test question 2', str(post_response.data))  # check post response for data just entered

    # def test_post_duplicate_question(self):
    #     """Run test for: Post a duplicate question"""
    #
    #     post_response = self.client.post('/api/v1/questions', data=json.dumps(self.test_data_question1), content_type='application/json')
    #     self.assertEqual(post_response.status_code, 409)  # 409 Conflict (Due to duplicate value)
    #     self.assertIn('Duplicate Value', str(post_response.data))  # check for 'Duplicate Value' error message
    #
    # def test_get_one_question(self):
    #     """Run test for: Get one question using its id"""
    #
    #     post_response = self.client.post('/api/v1/questions', data=json.dumps(self.test_data_question3), content_type='application/json')
    #     if 'Duplicate Value' in str(post_response.data):
    #         self.assertEqual(post_response.status_code, 409)  # 409 Conflict (Due to duplicate value)
    #     else:
    #         self.assertEqual(post_response.status_code, 201)
    #         self.assertIn('Test question 3', str(post_response.data))
    #         get_response = self.client.get('/api/v1/questions/1', content_type='application/json', data=json.loads(post_response.data.decode()))
    #         self.assertEqual(get_response.status_code, 200)
    #
    # def test_post_answer(self):
    #     """Run test for: Post an answer to a specific question"""
    #
    #     post_response = self.client.post('/api/v1/questions/1/answers', data=json.dumps(self.test_data_answer), content_type='application/json')
    #     if 'Duplicate Value' in str(post_response.data):
    #         self.assertEqual(post_response.status_code, 409)  # 409 Conflict (Due to duplicate value)
    #     else:
    #         self.assertEqual(post_response.status_code, 201)
    #         self.assertIn('Test answer 1', str(post_response.data))
