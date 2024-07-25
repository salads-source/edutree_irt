import requests
import pandas as pd

BASE_URL = "http://localhost:5000"
CSV_FILE_PATH = 'C:/Users/user/python_projects/item_response_theory/S08_question_answer_pairs_cleaned.csv'

# Function to store the quiz
def store_quiz(quiz_data):
    response = requests.post(f"{BASE_URL}/store_quiz", json=quiz_data)
    if response.status_code == 200:
        print("Quiz successfully stored.")
    else:
        print("Failed to store quiz questions in the Python service.")
        print(response.text)

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

# Function to get the next question
def get_next_question(test_session):
    response = requests.post(f"{BASE_URL}/next_question", json=test_session)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch next question.")
        print(response.text)
        return None

# Function to load CSV data and format it for the quiz
def load_csv_data(file_path):
    df = pd.read_csv(file_path)
    df = df.fillna('')  # Replace NaN with empty strings
    quiz_data = {
        "quiz_id": 101,
        "questions": []
    }

    for idx, row in df.iterrows():
        question = {
            "question_id": idx + 1,
            "quiz_id": 101,
            "concept": row['ArticleTitle'],
            "title": row['ArticleTitle'],
            "marks": 1,
            "question_details": row['Question'],
            "answer": row['Answer'],
            "difficulty": row['DifficultyFromQuestioner']
        }
        quiz_data["questions"].append(question)

    return quiz_data

# Main function to run the test
def main():
    # Load and format CSV data
    quiz_data = load_csv_data(CSV_FILE_PATH)

    # Store the quiz
    store_quiz(quiz_data)

    # Start the test
    test_session = start_test()

    while True:
        next_question_data = get_next_question(test_session)
        if next_question_data is None or next_question_data.get("status") == "completed":
            print("Test completed.")
            break

        print(f"Question: {next_question_data['question_text']}")
        user_answer = input("Your answer: ")
        test_session["current_question_id"] = next_question_data["item_index"]
        test_session["answer"] = user_answer
        test_session["est_theta"] = next_question_data["est_theta"]
        test_session["administered_items"] = next_question_data["administered_items"]
        test_session["responses"] = next_question_data["responses"]
        test_session["topic"] = next_question_data["topic"]
        test_session["topics_attempted"] = next_question_data["topics_attempted"]

        print(f"Estimated proficiency: {test_session['est_theta']:.2f}")

    print("Test finished. Your final proficiency estimate is:")
    print(f"Estimated proficiency: {test_session['est_theta']:.2f}")

if __name__ == "__main__":
  main()  