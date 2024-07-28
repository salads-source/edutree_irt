
from flask import Flask, request, jsonify
import test  # This imports the test.py module
import sys

app = Flask(__name__)

@app.route('/store_quiz', methods=['POST'])
def store_quiz():
    data = request.get_json()
    quiz_id = data['quiz_id']
    questions = data['questions']
    test.store_quiz({"quiz_id": quiz_id, "questions": questions})
    print(test.question_bank, file=sys.stderr)
    return jsonify({"message": test.question_bank}), 200

@app.route('/next_question', methods=['POST'])
def next_question():
    request_data = request.get_json()
    print(request_data, file=sys.stderr)
    response_data = test.handle_next_question(request_data)
    return jsonify(response_data)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
