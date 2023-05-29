from flask import Flask, request, jsonify
from datetime import datetime
import mysql.connector

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'quiz api'
}

quizzes = []

class Quiz:
    def __init__(self, question, options, right_answer, start_date, end_date):
        self.question = question
        self.options = options
        self.right_answer = right_answer
        self.start_date = start_date
        self.end_date = end_date

def validate_datetime(datetime_str):
    try:
        datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        return True
    except ValueError:
        return False
    

def save_quiz_to_database(quiz):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Insert quiz data into the database
    query = "INSERT INTO users (question, options, right_answer, start_date, end_date) VALUES (%s, %s, %s, %s, %s)"
    values = (quiz.question, ', '.join(quiz.options), quiz.right_answer, quiz.start_date, quiz.end_date)
    cursor.execute(query, values)

    connection.commit()
    cursor.close()
    connection.close()



@app.route('/create_quiz', methods=['POST'])
def create_quiz():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    data = request.json
    question = data['question']
    options = data['options']
    right_answer = data['rightAnswer']
    start_date = data['startDate']
    end_date = data['endDate']

    if not isinstance(options, list) or not isinstance(right_answer, int):
        return jsonify({'message': 'Options must be an array and rightAnswer must be an integer.'}), 400

    if not (0 <= right_answer < len(options)):
        return jsonify({'message': 'Invalid rightAnswer index.'}), 400

    if not validate_datetime(start_date) or not validate_datetime(end_date):
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS.'}), 400

    quiz = Quiz(question, options, right_answer, start_date, end_date)
    quizzes.append(quiz)
    print(quizzes)
    # Insert quiz data into the database
    query = "INSERT INTO users (question, options, right_answer, start_date, end_date) VALUES (%s, %s, %s, %s, %s)"
    values = (quiz.question, ', '.join(quiz.options), quiz.right_answer, quiz.start_date, quiz.end_date)
    cursor.execute(query, values)

    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({'message': 'Quiz created successfully.'}), 201

@app.route('/get_active_quiz', methods=['GET'])
def get_active_quiz():
    now = datetime.now()
    active_quiz = None

    for quiz in quizzes:
        start_date = datetime.strptime(quiz.start_date, '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(quiz.end_date, '%Y-%m-%d %H:%M:%S')
        if start_date <= now <= end_date:
            active_quiz = quiz
            break

    if active_quiz is None:
        return jsonify({'message': 'No active quiz.'}), 404

    return jsonify({
        'question': active_quiz.question,
        'options': active_quiz.options
    }), 200

@app.route('/get_quiz_result', methods=['GET'])
def get_quiz_result():
    now = datetime.now()
    ended_quizzes = [quiz for quiz in quizzes if datetime.strptime(quiz.end_date, '%Y-%m-%d %H:%M:%S') < now]
    
    if not ended_quizzes:
        return jsonify({'message': 'No quiz results available yet.'}), 404

    results = []
    for quiz in ended_quizzes:
        results.append({
            'question': quiz.question,
            'right_answer': quiz.options[quiz.right_answer]
        })

    return jsonify(results), 200

if __name__ == '__main__':
    app.run(debug=True)
