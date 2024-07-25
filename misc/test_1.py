import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from catsim.initialization import FixedPointInitializer
from catsim.selection import MaxInfoSelector
from catsim.estimation import NumericalSearchEstimator
from catsim.stopping import MaxItemStopper
from catsim.irt import icc
import random
from fpdf import FPDF
import os

# Load the CSV file
file_path = r'C:\Users\user\python_projects\item_response_theory\S08_question_answer_pairs_cleaned.csv'
df = pd.read_csv(file_path)

# Map difficulty levels to numerical values
difficulty_mapping = {
    'easy': -2.0,
    'medium': 0.0,
    'hard': 2.0
}

# Assign item parameters based on the dataset
def assign_parameters(df):
    num_items = df.shape[0]
    discrimination = np.random.uniform(0.5, 2.0, num_items)  # discrimination parameter (a)
    difficulty = df['DifficultyFromQuestioner'].map(difficulty_mapping)  # map difficulty to (b)
    guessing = np.random.uniform(0.1, 0.3, num_items)  # guessing parameter (c)
    upper_asymptote = np.ones(num_items)  # upper_asymptote parameter (d)
    parameters = np.column_stack((discrimination, difficulty, guessing, upper_asymptote))
    return parameters

# Assign parameters to questions
item_parameters = assign_parameters(df)
print(item_parameters)

# Function to simulate user responses
def ask_question(item, question_text, est_theta):
    a, b, c, d = item
    prob = icc(est_theta, a, b, c, d)
    
    print(f"\nQuestion: {question_text}")
    print(f"Difficulty: {b:.2f}, Discrimination: {a:.2f}")
    
    answer = input("Your answer: ").strip().lower()
    correct_answer = df.loc[df['Question'] == question_text, 'Answer'].values[0].strip().lower()
    correct = (answer == correct_answer)
    return correct, prob

# Function to generate the proficiency report
def generate_proficiency_report(student_id, topic, administered_items, responses, difficulties_correct, difficulties_incorrect, estimations):
    report = {
        'Student ID': student_id,
        'Topic': topic,
        'Total Questions': len(administered_items),
        'Correct Answers': sum(responses),
        'Incorrect Answers': len(responses) - sum(responses),
        'Average Difficulty of Correct Answers': np.mean(difficulties_correct) if difficulties_correct else 'N/A',
        'Average Difficulty of Incorrect Answers': np.mean(difficulties_incorrect) if difficulties_incorrect else 'N/A',
        'Proficiency Estimation over Time': estimations
    }
    return report

# Function to visualize the proficiency report and save plots
def visualize_proficiency_report(report, output_dir):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    estimations = report['Proficiency Estimation over Time']
    questions = list(range(1, len(estimations) + 1))

    # Plot proficiency estimation over time
    plt.figure(figsize=(10, 6))
    plt.plot(questions, estimations, marker='o', linestyle='-', color='b', label='Proficiency Estimation')
    plt.xlabel('Question Number')
    plt.ylabel('Proficiency Estimation')
    plt.title(f"Proficiency Estimation Over Time for {report['Student ID']} ({report['Topic']})")
    plt.legend()
    plt.grid(True)
    plt_path = f"{output_dir}/proficiency_estimation_{report['Student ID']}_{report['Topic']}.png"
    plt.savefig(plt_path)
    plt.close()

    # Plot the difficulty distribution of correct and incorrect answers
    plt.figure(figsize=(10, 6))
    plt.hist(report['Average Difficulty of Correct Answers'], bins=10, alpha=0.5, label='Correct Answers', color='g')
    plt.hist(report['Average Difficulty of Incorrect Answers'], bins=10, alpha=0.5, label='Incorrect Answers', color='r')
    plt.xlabel('Difficulty')
    plt.ylabel('Number of Questions')
    plt.title(f"Difficulty Distribution for {report['Student ID']} ({report['Topic']})")
    plt.legend()
    plt.grid(True)
    plt_path_diff = f"{output_dir}/difficulty_distribution_{report['Student ID']}_{report['Topic']}.png"
    plt.savefig(plt_path_diff)
    plt.close()

    return plt_path, plt_path_diff

# Function to create a PDF report
def create_pdf_report(reports, output_file, output_dir):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for report in reports:
        pdf.add_page()

        # Title
        pdf.set_font("Arial", size=16)
        pdf.cell(200, 10, f"Proficiency Report for {report['Student ID']} ({report['Topic']})", ln=True, align='C')

        # Report content
        pdf.set_font("Arial", size=12)
        for key, value in report.items():
            if key != 'Proficiency Estimation over Time':
                pdf.cell(200, 10, f"{key}: {value}", ln=True)

        # Add plots
        proficiency_plot, difficulty_plot = visualize_proficiency_report(report, output_dir)
        pdf.image(proficiency_plot, x=10, y=None, w=190)
        pdf.add_page()  # New page for the next plot
        pdf.image(difficulty_plot, x=10, y=None, w=190)

    pdf.output(output_file)

# Main function to run the adaptive test
def main(df, item_parameters):
    student_id = input("Enter Student ID: ")
    topics = df['ArticleTitle'].unique()
    initializer = FixedPointInitializer(0.0)
    selector = MaxInfoSelector()
    estimator = NumericalSearchEstimator()
    stopper = MaxItemStopper(5)  # Stop after 5 questions per topic

    reports = []
    output_dir = 'reports'

    for topic in topics:
        print(f"\nTopic: {topic}")
        topic_df = df[df['ArticleTitle'] == topic]
        topic_item_parameters = item_parameters[df['ArticleTitle'] == topic]

        est_theta = initializer.initialize()
        print(f"Starting estimated proficiency: {est_theta:.2f}")
        administered_items = []
        responses = []
        difficulties_correct = []
        difficulties_incorrect = []
        estimations = [est_theta]

        while len(administered_items) < 5:
            item_index = selector.select(items=topic_item_parameters, administered_items=administered_items, est_theta=est_theta)
            print(type(item_index))
            print(f"Selected item index: {item_index}")

            question_text = topic_df.iloc[item_index]['Question']
            correct, prob = ask_question(topic_item_parameters[item_index], question_text, est_theta)
            print(correct)
            administered_items.append(item_index)
            responses.append(correct)
            print(responses)
            print(administered_items)

            difficulty = topic_item_parameters[item_index][1]
            if correct:
                difficulties_correct.append(difficulty)
            else:
                difficulties_incorrect.append(difficulty)

            est_theta = estimator.estimate(items=topic_item_parameters, administered_items=administered_items, response_vector=responses, est_theta=est_theta)
            estimations.append(est_theta)
            print(f"Estimated proficiency: {est_theta:.2f}")

        # Generate report for this topic
        report = generate_proficiency_report(student_id, topic, administered_items, responses, difficulties_correct, difficulties_incorrect, estimations)
        reports.append(report)

    # Create PDF report
    output_file = f"proficiency_report_{student_id}.pdf"
    create_pdf_report(reports, output_file, output_dir)

    print(f"\nQuiz finished! Reports have been saved to '{output_file}'.")

# Run the test
main(df, item_parameters)
