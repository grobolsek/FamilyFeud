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
    pos_ans = question.possible_answers.items() if question.question_type == "multi" else {}
    hi_id = int(question.get_highest_id()) + 1 if question.question_type == "multi" else 0
    return render_template('editQuestions.html', question=question, pos_ans = pos_ans, hi_id=hi_id)

@app.route('/admin/questions/add/<int:question_id>/')
def add_question(question_id):
    question = request.args.get('question')
    type_ = request.args.get('type')
    if type_ == "none": # string
        storage.edit_question(question_id, question, "string")
    else: # multi
        pos_answers = [value for key, value in request.args.items() if key.startswith('pos_ans')]
        storage.edit_question(question_id, question, "multi", pos_answers)
    return redirect(url_for('manage_questions'))

if __name__ == '__main__':
    app.run()
