# StackOverflow-lite-C3
StackOverflow-lite is a platform where people can ask questions and provide answers.

UI URL:
https://brucemakallan.github.io/StackOverflow-lite/UI/

[![Build Status](https://travis-ci.com/brucemakallan/StackOverflow-lite-C3.svg?branch=master)](https://travis-ci.com/brucemakallan/StackOverflow-lite-C3)
[![Coverage Status](https://coveralls.io/repos/github/brucemakallan/StackOverflow-lite-C3/badge.svg?branch=master)](https://coveralls.io/github/brucemakallan/StackOverflow-lite-C3?branch=master)
    

## Main Features

1. Create user accounts that can signin/signout from the app.
2. Get all questions.
3. Get a question
4. Post a question.
5. Delete a question.
6. Post an answer to a question.
7. Mark an answer as preferred.

## API Endpoints
The API is hosted on Heroku at:
```
https://stackoverflow-lite-abm.herokuapp.com
```

### Fetch all questions:
```
GET /api/v1/questions
```
For example: https://stackoverflow-lite-abm.herokuapp.com/api/v1/questions

### Fetch a specific question
```
GET /api/v1/questions/<questionId>
```
For example: https://stackoverflow-lite-abm.herokuapp.com/api/v1/questions/1

### Add a question
```
POST /api/v1/questions
```
Provide POST data in JSON format e.g.
```
{
    "question": "Sample text"
}
```

### Get all answers for a specific question
```
GET /api/v1/questions/<questionId>/answers
```
For example: https://stackoverflow-lite-abm.herokuapp.com/api/v1/questions/1/answers

### Add an answer
```
POST /api/v1/questions/<questionId>/answers
```
Provide POST data in JSON format e.g.
```
{
    "answer": "Sample text"
}
```