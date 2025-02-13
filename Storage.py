import tinydb
from tinydb import Query
from Question import *

class Storage:
    def __init__(self, file):
        self.db = tinydb.TinyDB(file)
        self.questions_dict = self.get_questions_dict()

        self.questions = Questions.from_dict({"questions": self.questions_dict})
        self.counter = self.questions.get_highest_id() + 1

    def create(self, data):
        self.db.insert(data)

    def add_question(self, question_text, question_type, possible_answers: dict = None):
        if question_type == "string":
            # Add the new question to the questions list
            self.questions.add_question(question_text, question_type, question_id=self.counter)

        else:
            # Add the new question to the questions list
            self.questions.add_question(question_text, question_type, question_id=self.counter, possible_answers=possible_answers)

        if len(self.db) > 0:
            self.db.update(self.questions.to_dict(), doc_ids=[1])
        else:
            self.db.insert(self.questions.to_dict())
        self.counter += 1

    def delete_question(self, question_id: int):
        question_id = int(question_id)

        # Get the main document with doc_id=1
        entry = self.db.get(doc_id=1)

        if entry and "questions" in entry:
            # Filter out the question with the given ID
            updated_questions = {int(k): v for k, v in entry["questions"].items() if int(k) != question_id}
            # Update the database with the modified questions list
            self.db.update({"questions": updated_questions}, doc_ids=[1])

        # Remove from class
        self.questions.remove_question(question_id)

    def get_question(self, question_id: int):
        return self.questions.get_question_by_id(question_id)

    def get_questions(self):
        return self.questions.questions

    def add_possible_answer(self, question_id, answer):
        pos = self.questions.get_question_by_id(question_id)
        pos.add_possible_answer(answer, pos.get_highest_id() + 1)
        # todo: insert into db new pos answer

    def edit_question(self, question_id: int, question_text: str, question_type: str, possible_answers: list = None):
        question = self.questions.get_question_by_id(question_id)
        question.question_text = question_text
        question.type = question_type

        Question_query = Query()
        if question_type == "multi":
            pos_ans = {}
            question: MultiChoiceQuestion = question
            question.remove_possible_answers()
            for i, possible_answer in enumerate(possible_answers):
                question.add_possible_answer(possible_answer, i)
                pos_ans[i] = possible_answer

        self.db.update(self.questions.to_dict(), doc_ids=[1])

    def get_questions_dict(self):
        if len(self.db) > 0:
            return self.db.all()[0]["questions"]
        else:
            return {}

    def add_answer(self, question_id, answer):
        self.questions.get_question_by_id(question_id).add_answer(answer)
        self.db.update(self.questions.to_dict(), doc_ids=[1])


class Users:
    def __init__(self, file):
        self.db = tinydb.TinyDB(file)

