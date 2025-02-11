import tinydb
from tinydb import Query
from Question import *

class Storage:
    def __init__(self, file):
        self.db = tinydb.TinyDB(file)
        self.questions_dict = self.get_questions_dict()
        self.questions = Questions.from_dict({"questions": self.questions_dict})
        self.counter = 0

    def create(self, data):
        self.db.insert(data)

    def add_question(self, question_text, question_type):
        # Create a new question dictionary
        new_question = {
            "question_text": question_text,
            "type": question_type,
            "answers": [],
            "grouped": [],
            "id": self.counter,
        }

        # Add the new question to the database
        self.db.insert(new_question)

        # Add the new question to the questions list
        self.questions.add_question(question_text, question_type, question_id=self.counter)
        self.counter += 1

    def delete_question(self, question_id: int):
        question_id = int(question_id)

        # Get the main document with doc_id=1
        entry = self.db.get(doc_id=1)

        if entry and "questions" in entry:
            # Filter out the question with the given ID
            updated_questions = [q for q in entry["questions"] if q["id"] != question_id]

            # Update the database with the modified questions list
            self.db.update({"questions": updated_questions}, doc_ids=[1])

        # Remove from class
        self.questions.remove_question(question_id)

    def get_questions(self):
        return self.questions

    def get_questions_dict(self):
        if len(self.db) > 0:
            return self.db.all()[0]["questions"]
        else:
            return []