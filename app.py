from flask import Flask, jsonify, render_template, request, redirect, url_for
from Question import *
from Storage import Storage

app = Flask(__name__)

file_location = "questions.json"

storage = Storage(file_location)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/admin/')
def admin():
    pass

@app.route('/admin/questions')
def manage_questions():
    return render_template('questions.html', questions=list(storage.get_questions().values()))

@app.route('/admin/questions/delete/<int:question_id>', methods=['GET'])
def delete_question(question_id):
    storage.delete_question(question_id)
    return redirect(url_for('manage_questions'))

@app.route('/admin/questions/edit/<int:question_id>', methods=['GET'])
def edit_question(question_id):
    question = storage.get_question(question_id)
    print(question.possible_answers)
    pos_ans = []
    if question.question_type == "multi":
        pos_ans = [[i, str(i.values())] for i in question.possible_answers]
    return render_template('editQuestions.html', question=question, pos_ans=pos_ans)

@app.route('/admin/questions', methods=['GET'])
def add_question():
    data = request.get_json()
    if 'text' in data:
        storage.add_question(data['text'], data['type'])
        return jsonify({"success": True}), 201
    return jsonify({"error": "Missing text"}), 400


if __name__ == '__main__':
    app.run()
