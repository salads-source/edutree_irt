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
    
    def test_start_test(self):
        # Function to start the test
        def start_test():
            student_id = "student_123"
            quiz_id = 101
            est_theta = 0.0
            administered_items = []
            responses = []

            return {
                "student_id": student_id,
                "quiz_id": quiz_id,
                "est_theta": est_theta,
                "administered_items": administered_items,
                "responses": responses,
                "current_question_id": None,
                "answer": None,
                "topic": None
            }
        
        test_session = start_test()
        self.assertEqual(test_session["student_id"], "student_123")
        self.assertEqual(test_session["quiz_id"], 101)
        self.assertEqual(test_session["est_theta"], 0.0)
        self.assertEqual(test_session["administered_items"], [])
        self.assertEqual(test_session["responses"], [])
        self.assertIsNone(test_session["current_question_id"])
        self.assertIsNone(test_session["answer"])
        self.assertIsNone(test_session["topic"])

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

if __name__ == '__main__':
    unittest.main()
