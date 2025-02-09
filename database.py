from tinydb import TinyDB, Query


class database:
    def __init__ (self, database_path ="database.json"):
        self.database = TinyDB(database_path)
        self.questions_table = self.database.table("questions")


    def add_question(self, question):
        Question = Query()

        # Check if the question already exists
        if self.questions_table.search(Question[question].exists()):
            print("Question already exists.")
            return False  # Or raise an exception if needed

        # Insert new question
        self.questions_table.insert({question: []})
        print("Question added successfully.")
        return True


    def add_answer(self, question, answer):
        Question = Query()

        # Check if the question already exists
        if not self.questions_table.search(Question[question].exists()):
            raise Exception("Question does not exist.")

        # Insert answer if question exists
        self.questions_table.insert({question: answer})


    def group_answers(self, question):
        Question = Query()
