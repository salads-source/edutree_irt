import unittest
import json
from app import app

class TestCliFunctions(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_store_quiz(self):
        # Example quiz data
        quiz_data = {
            "quiz_id": 101,
            "questions": [
                {"question_id": 1, "concept": "Math", "title": "Math Question 1", "marks": 1, "question_details": "What is 2+2?", "answer": "4", "difficulty": "easy"},
                {"question_id": 2, "concept": "Math", "title": "Math Question 2", "marks": 1, "question_details": "What is 3+5?", "answer": "8", "difficulty": "medium"},
                {"question_id": 3, "concept": "Science", "title": "Science Question 1", "marks": 1, "question_details": "What is H2O?", "answer": "Water", "difficulty": "easy"},
            ]
        }

        # Send POST request to store quiz
        response = self.app.post('/store_quiz', data=json.dumps(quiz_data), content_type='application/json')
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check response data
        response_data = json.loads(response.data)
        self.assertIn('message', response_data)
        self.assertIsInstance(response_data['message'], dict)
        self.assertIn('101', response_data['message'])  # Adjusted to check for string key

    def test_store_quiz_missing_fields(self):
        # Quiz data with missing fields
        quiz_data = {
            "quiz_id": 102
            # Missing "questions"
        }

        # Send POST request to store quiz
        response = self.app.post('/store_quiz', data=json.dumps(quiz_data), content_type='application/json')
        
        # Check response status
        self.assertNotEqual(response.status_code, 200)

    def test_store_quiz_empty_questions(self):
        # Quiz data with empty questions
        quiz_data = {
            "quiz_id": 103,
            "questions": []
        }

        # Send POST request to store quiz
        response = self.app.post('/store_quiz', data=json.dumps(quiz_data), content_type='application/json')
        
        # Check response status
        self.assertEqual(response.status_code, 200)

    def test_get_next_question(self):
        # Example quiz data to store
        quiz_data = {
            "quiz_id": 101,
            "questions": [
                {"question_id": 1, "concept": "Math", "title": "Math Question 1", "marks": 1, "question_details": "What is 2+2?", "answer": "4", "difficulty": "easy"},
                {"question_id": 2, "concept": "Math", "title": "Math Question 2", "marks": 1, "question_details": "What is 3+5?", "answer": "8", "difficulty": "medium"},
                {"question_id": 3, "concept": "Science", "title": "Science Question 1", "marks": 1, "question_details": "What is H2O?", "answer": "Water", "difficulty": "easy"},
            ]
        }

        # Store the quiz data first
        store_response = self.app.post('/store_quiz', data=json.dumps(quiz_data), content_type='application/json')
        self.assertEqual(store_response.status_code, 200)

        # Example request data for next question
        request_data = {
            "quiz_id": 101,
            "student_id": "student_123",
            "topic": None,
            "est_theta": 0.0,
            "administered_items": [],
            "responses": []
        }

        # Send POST request to get next question
        response = self.app.post('/next_question', data=json.dumps(request_data), content_type='application/json')
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check response data
        response_data = json.loads(response.data)
        self.assertIn('question_text', response_data)
        self.assertIn('item_index', response_data)
        self.assertIn('est_theta', response_data)

    def test_get_next_question_no_quiz_id(self):
        # Example request data for next question with missing quiz_id
        request_data = {
            "student_id": "student_123",
            "topic": None,
            "est_theta": 0.0,
            "administered_items": [],
            "responses": []
        }

        # Send POST request to get next question
        response = self.app.post('/next_question', data=json.dumps(request_data), content_type='application/json')
        
        # Check response status
        self.assertNotEqual(response.status_code, 200)

    def test_get_next_question_no_student_id(self):
        # Example request data for next question with missing student_id
        request_data = {
            "quiz_id": 101,
            "topic": None,
            "est_theta": 0.0,
            "administered_items": [],
            "responses": []
        }

        # Send POST request to get next question
        response = self.app.post('/next_question', data=json.dumps(request_data), content_type='application/json')
        
        # Check response status
        self.assertNotEqual(response.status_code, 200)

    def test_get_next_question_complete(self):
        # Example quiz data to store
        quiz_data = {
            "quiz_id": 104,
            "questions": [
                {"question_id": 1, "concept": "Math", "title": "Math Question 1", "marks": 1, "question_details": "What is 2+2?", "answer": "4", "difficulty": "easy"},
            ]
        }

        # Store the quiz data first
        store_response = self.app.post('/store_quiz', data=json.dumps(quiz_data), content_type='application/json')
        self.assertEqual(store_response.status_code, 200)

        # Example request data for next question
        request_data = {
            "quiz_id": 104,
            "student_id": "student_123",
            "topic": None,
            "est_theta": 0.0,
            "administered_items": [1],
            "responses": [True]
        }

        # Send POST request to get next question
        response = self.app.post('/next_question', data=json.dumps(request_data), content_type='application/json')
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check response data
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'completed')

    def test_get_next_question_multiple_topics(self):
        # Example quiz data to store
        quiz_data = {
            "quiz_id": 105,
            "questions": [
                {"question_id": 1, "concept": "Math", "title": "Math Question 1", "marks": 1, "question_details": "What is 2+2?", "answer": "4", "difficulty": "easy"},
                {"question_id": 2, "concept": "Science", "title": "Science Question 1", "marks": 1, "question_details": "What is H2O?", "answer": "Water", "difficulty": "easy"},
            ]
        }

        # Store the quiz data first
        store_response = self.app.post('/store_quiz', data=json.dumps(quiz_data), content_type='application/json')
        self.assertEqual(store_response.status_code, 200)

        # Example request data for next question
        request_data = {
            "quiz_id": 105,
            "student_id": "student_123",
            "topic": None,
            "est_theta": 0.0,
            "administered_items": [],
            "responses": []
        }

        # Send POST request to get next question
        response = self.app.post('/next_question', data=json.dumps(request_data), content_type='application/json')
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check response data
        response_data = json.loads(response.data)
        self.assertIn('question_text', response_data)
        self.assertIn('item_index', response_data)
        self.assertIn('est_theta', response_data)

    def test_update_question_bank(self):
        # Example quiz data to store
        quiz_data = {
            "quiz_id": 106,
            "questions": [
                {"question_id": 1, "concept": "Math", "title": "Math Question 1", "marks": 1, "question_details": "What is 2+2?", "answer": "4", "difficulty": "easy"},
            ]
        }

        # Store the quiz data first
        store_response = self.app.post('/store_quiz', data=json.dumps(quiz_data), content_type='application/json')
        self.assertEqual(store_response.status_code, 200)

        # Update quiz data
        updated_quiz_data = {
            "quiz_id": 106,
            "questions": [
                {"question_id": 1, "concept": "Math", "title": "Math Question 1", "marks": 1, "question_details": "What is 2+2?", "answer": "4", "difficulty": "easy"},
                {"question_id": 2, "concept": "Math", "title": "Math Question 2", "marks": 1, "question_details": "What is 3+3?", "answer": "6", "difficulty": "easy"},
            ]
        }

        # Send POST request to update quiz
        update_response = self.app.post('/store_quiz', data=json.dumps(updated_quiz_data), content_type='application/json')
        
        # Check response status
        self.assertEqual(update_response.status_code, 200)
        
        # Check response data
        response_data = json.loads(update_response.data)
        self.assertIn('message', response_data)
        self.assertIsInstance(response_data['message'], dict)
        self.assertIn('106', response_data['message'])

    def test_get_next_question_no_more_questions(self):
        # Example quiz data to store
        quiz_data = {
            "quiz_id": 107,
            "questions": [
                {"question_id": 1, "concept": "Math", "title": "Math Question 1", "marks": 1, "question_details": "What is 2+2?", "answer": "4", "difficulty": "easy"},
            ]
        }

        # Store the quiz data first
        store_response = self.app.post('/store_quiz', data=json.dumps(quiz_data), content_type='application/json')
        self.assertEqual(store_response.status_code, 200)

        # Example request data for next question
        request_data = {
            "quiz_id": 107,
            "student_id": "student_123",
            "topic": "Math",
            "est_theta": 0.0,
            "administered_items": [1],
            "responses": [True]
        }

        # Send POST request to get next question
        response = self.app.post('/next_question', data=json.dumps(request_data), content_type='application/json')
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check response data
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'completed')
        self.assertEqual(response_data['message'], 'No more questions available')

if __name__ == '__main__':
    unittest.main()
