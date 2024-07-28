
import numpy as np
from catsim.initialization import FixedPointInitializer
from catsim.selection import MaxInfoSelector
from catsim.selection import UrrySelector
from catsim.selection import RandomSelector
from catsim.estimation import NumericalSearchEstimator
from catsim.irt import icc
import random
import sys

# Global variables to store the question bank and item parameters
question_bank = {}
item_parameters = {}
student_progress = {}

# Map difficulty levels to numerical values
difficulty_mapping = {
    'easy': -2.0,
    'medium': 0.0,
    'hard': 2.0
}

selector = RandomSelector()
estimator = NumericalSearchEstimator()

# Function to initialize the item parameters from the question bank
def initialize_item_parameters(questions):
    num_items = len(questions)
    discrimination = np.random.uniform(0.5, 2.0, num_items)  # discrimination parameter (a)
    difficulty = np.array([difficulty_mapping[q['difficulty']] for q in questions])  # map difficulty to (b)
    guessing = np.random.uniform(0.1, 0.3, num_items)  # guessing parameter (c)
    upper_asymptote = np.ones(num_items)  # upper_asymptote parameter (d)
    # exposure_rate = np.zeros(num_items)  # item exposure rate
    parameters = np.column_stack((discrimination, difficulty, guessing, upper_asymptote))
    return parameters

# Function to store the quiz in the question bank
def store_quiz(data):
    global question_bank, item_parameters, student_progress
    quiz_id = data['quiz_id']
    questions = data['questions']
    question_bank[quiz_id] = questions
    item_parameters[quiz_id] = initialize_item_parameters(questions)
    student_progress[quiz_id] = {}

# Function to get the next question
def get_next_question(quiz_id, student_id, topic, est_theta, administered_items, responses, current_question_id, answer):
    if quiz_id not in question_bank:
        raise KeyError(f"Quiz ID {quiz_id} not found in the question bank")

    if student_id not in student_progress[quiz_id]:
        student_progress[quiz_id][student_id] = {"topics_attempted": {t: 0 for t in set(q['concept'] for q in question_bank[quiz_id])}}

    questions = question_bank[quiz_id]
    topic_questions = [q for q in questions if q['concept'] == topic]
    topic_item_indices = [i for i, q in enumerate(questions) if q['concept'] == topic]
    topic_item_parameters = item_parameters[quiz_id][topic_item_indices]

    # selector = UrrySelector(r_max=0.2)
    # estimator = NumericalSearchEstimator()

    # Process the current question
    if current_question_id is not None:
        current_item_index = next((i for i, q in enumerate(questions) if q['question_id'] == current_question_id), None)
        # current_item_index = current_question_id
        if current_item_index is None:
            raise ValueError(f"Current question ID {current_question_id} not found in questions")

        print(f"Processing current question ID {current_question_id}", file=sys.stderr)
        print(f"Current question details: {questions[current_item_index]['question_details']}", file=sys.stderr)
        print(f"Answer received: {answer}", file=sys.stderr)

        correct_answer = questions[current_item_index]['answer']
        print(f"Correct answer: {correct_answer}", file=sys.stderr)
        correct = (answer.strip().lower() == correct_answer.strip().lower())

        print(f"Correct: {correct}", file=sys.stderr)

        administered_items.append(current_item_index)
        responses.append(correct)

        est_theta = estimator.estimate(items=item_parameters[quiz_id], administered_items=administered_items, response_vector=responses, est_theta=est_theta)
        student_progress[quiz_id][student_id]["topics_attempted"][topic] += 1

    # Check if we have completed 5 questions from this topic
    if student_progress[quiz_id][student_id]["topics_attempted"][topic] >= 5:
        remaining_topics = [t for t in student_progress[quiz_id][student_id]["topics_attempted"] if student_progress[quiz_id][student_id]["topics_attempted"][t] < 5]
        print(remaining_topics, file=sys.stderr)
        
        if not remaining_topics:
            return None, "No more questions available", est_theta
        topic = random.choice(remaining_topics)
        topic_questions = [q for q in questions if q['concept'] == topic]
        topic_item_indices = [i for i, q in enumerate(questions) if q['concept'] == topic]
        topic_item_parameters = item_parameters[quiz_id][topic_item_indices]

    # Select the next question
    item_index = selector.select(items=topic_item_parameters, administered_items=administered_items, est_theta=est_theta)
    # while item_index == current_question_id:
    #   item_index = selector.select(items=topic_item_parameters, administered_items=administered_items, est_theta=est_theta)
      
    print(f"Selected item index: {item_index}", file=sys.stderr)

    if item_index is None:
        return None, "No more questions available", est_theta
    
    print(topic_item_indices, file=sys.stderr)
    print(topic_item_parameters, file=sys.stderr)
    # print(topic_questions, file=sys.stderr)

    question_text = topic_questions[item_index - 1]['question_details']
    print(question_text, file=sys.stderr)

    return topic, topic_item_indices[item_index], question_text, float(est_theta)

# Function to handle fetching the next question and updating proficiency
def handle_next_question(request_data):
    quiz_id = request_data['quiz_id']
    student_id = request_data['student_id']
    topic = request_data['topic']
    est_theta = request_data['est_theta']
    administered_items = request_data['administered_items']
    responses = request_data['responses']
    current_question_id = request_data.get('current_question_id')
    answer = request_data.get('answer')

    if topic is None:
        # Initialize topic to the first topic
        topics = [q['concept'] for q in question_bank[quiz_id]]
        topic = topics[0]

    topic, item_index, question_text, est_theta = get_next_question(quiz_id, student_id, topic, est_theta, administered_items, responses, current_question_id, answer)
    print(item_index, file=sys.stderr)
    if item_index is None:
        return {
            'status': 'completed',
            'message': question_text,
            'est_theta': est_theta
        }

    return {
        'item_index': item_index,
        'question_text': question_text,
        'est_theta': est_theta,
        'administered_items': administered_items,
        'responses': responses,
        'topic': topic,
        'topics_attempted': student_progress[quiz_id][student_id]["topics_attempted"]
    }
