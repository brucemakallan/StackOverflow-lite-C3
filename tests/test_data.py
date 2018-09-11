class TestData(object):

    # test data for questions
    test_data_question1 = dict(question='Test question sample one')
    test_data_question2 = dict(question='Test question sample two')
    test_data_question3 = dict(question='Test question sample three')
    test_data_question4 = dict(question='Test question sample four')

    # test data for answers
    test_data_answer = dict(answer="Test answer sample one")

    # test data for users
    user_data = dict(full_name="Jane Doe", email="jane@gmail.com", password="password123",
                     retype_password="password123")
    user_data2 = dict(full_name="Annie Jones", email="annie@gmail.com", password="believe_you",
                      retype_password="believe_you")
    user_data3 = dict(full_name="Jane Doe", email="jane@gmail.com", password="pass")

    # test data for tokens
    wrong_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MzU2NjgmmTAsIm5iZiI6MTUzNTY2ODU1MCwianRpIjoiZjA0MTVmODUtYjBkNC00MWYwLWFmMTAtNzU5YjhmNzgxY2Q0IiwiZXhwIjoxNTM1NjY5NDUwLCJpZGVudGl0eSI6MSwiZnJlc2giOmZhbHNlLCJ0eXBlIjoiYWNjZXNzIn0.9WTmhO49Ta2M3tvNuuUME52zObxW14jenCsIOFKo_cg"
