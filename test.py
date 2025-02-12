from Question import *
from Storage import Storage

questions = Questions()
questions.add_question("What is your favorite color?", "multi", 0)
questions.add_question("What is your favorite sport?", "text", 1)


q1: MultiChoiceQuestion = questions.get_question_by_id(0)

q1.add_possible_answer("Red", 0)
q1.add_possible_answer("Blue", 1)
q1.add_possible_answer("Yellow", 2)
q1.add_possible_answer("White", 3)

q1.add_answer("Blue")
q1.add_answer("Red")
q1.add_answer("Blue")
q1.add_answer("Green")
q1.add_answer("Red")
q1.add_answer("Red")

q2: StringQuestion = questions.get_question_by_id(1)
q2.add_answer("Football")
q2.add_answer("Soccer")
q2.add_answer("soccer")
q2.add_answer("Basketball")
q2.add_answer("football")
q2.add_answer("tennis")

questions.group_and_sort_all_questions()
db = Storage("questions.json")
print(questions.to_dict())
db.create(questions.to_dict())

