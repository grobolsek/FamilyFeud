from abc import ABC, abstractmethod
from collections import defaultdict
from random import shuffle
from copy import deepcopy

from rapidfuzz import process, fuzz


class Answer:
    """
    A class representing a single answer to a question.

    Attributes:
        answer (str): The answer text.
    """

    def __init__(self, answer: str, answer_id: int = None):
        """
        Initialize the Answer with the provided answer text.

        Args:
            answer (str): The answer text.
            answer_id (int): The id of the answer.
        """
        self.answer: str = answer
        self.answer_id: int = answer_id

    def __str__(self):
        return self.answer

    def get_answer_id(self):
        return self.answer_id

    def to_dict(self) -> dict:
        # Convert class instance to a dictionary
        return {
            "answer": str(self.answer),
            "answer_id": self.answer_id
        }

    @classmethod
    def from_dict(cls, data):
        # Convert a dictionary back to the class instance
        return cls(data["answer"], data["answer_id"])


class Question(ABC):
    """
    Abstract base class representing a general question.

    Attributes:
        question_text (str): The text of the question.
        answers (list): A list to store answers to the question.
        grouped (defaultdict): A dictionary to store grouped answers with their count.

    Methods:
        group() -> dict: Abstract method to group answers, to be implemented in subclasses.
        add_answer(answer: str): Add an answer to the question.
        answers() -> list: Return a list of answers for the question.
    """

    def __init__(self, question_text: str, question_type: str, answers: list, grouped = None, question_id: int = None):
        """
        Initialize the Question with the provided question text and ID.

        Args:
            question_text (str): The text of the question.
        """
        self.question_text = question_text
        self.question_type = question_type
        self.answers = answers
        self.grouped = grouped if grouped else defaultdict(int)
        self.question_id = question_id
        self.counter = 0

    @abstractmethod
    def group(self):
        """
        Abstract method to group answers based on specific logic.

        This method should be implemented by subclasses to group answers
        according to the needs of the question type.
        """
        pass

    def edit_question(self, new_question: str):
        self.question_text = new_question

    def add_answer(self, answer: str):
        """
        Add an answer to the question.

        Args:
            answer (str): The answer text to be added.
        """
        self.answers.append(Answer(answer=answer, answer_id=self.counter))
        self.counter += 1

    def get_answers(self) -> list[str]:
        """
        Get a list of answers for the question.

        Returns:
            list: A list of answer texts.
        """
        return [str(a) for a in self.answers]

    def sort_grouped_answers(self):
        """
        Sort the grouped answers
        """
        self.grouped = sorted(self.grouped.items(), key=lambda x: x[1], reverse=True)


class MultiChoiceQuestion(Question):
    """
    A class representing a multiple choice question.

    Inherits from the Question class and implements the group method
    to group answers based on their frequency.

    Methods:
        group() -> dict: Group answers based on their frequency and return the result.
    """

    def __init__(self, question_text: str, answers: list, grouped = None, possible_answers: list = None, question_id: int = None):
        """
        Initialize the Multiple Choice Question with the provided question text and ID.

        Args:
            question_text (str): The text of the question.
        """
        super().__init__(question_text,"multi", answers, grouped, question_id)
        self.possible_answers = possible_answers if possible_answers else []
        self.counter = 0

    def group(self):
        """
        Group answers based on their frequency.

        Returns:
            dict: A dictionary with answers as keys and their counts as values.
        """
        for answer in self.answers:
            self.grouped[str(answer)] += 1

    def add_possible_answer(self, answer: str):
        self.possible_answers.append(Answer(answer, self.counter))
        self.counter += 1

    def edit_possible_answer(self, old_answer:str, new_answer: str):
        for answer in self.possible_answers:
            if str(answer) == old_answer:
                answer.answer = new_answer
                return

    def remove_possible_answer(self, answer: str):
        self.possible_answers.remove(answer)


    def to_dict(self) -> dict:
        """
        Convert class instance to a dictionary
        :return: returns dict of values of the question.
        """
        return {
            "question_text": self.question_text,
            "type": self.question_type,
            "answers": self.get_answers(),
            "grouped": self.grouped,
            "possible_answers": [{a.answer_id: a.answer} for a in self.possible_answers],
            "id": self.question_id,
        }

    @classmethod
    def from_dict(cls, data):
        # Convert a dictionary back to the class instance
        return cls(
            data["question_text"],
            [Answer(answer) for answer in data["answers"]],
            data["grouped"],
            data["possible_answers"],
            data["id"],
        )


class StringQuestion(Question):
    """
    A class representing a string-based question where answers may vary in wording.

    Inherits from the Question class and implements the group method
    to group similar answers using string matching and fuzzing.

    Methods:
        group(threshold=80) -> dict: Group similar answers using fuzzy matching.
    """

    def __init__(self, question_text: str, answers: list, grouped = None, question_id: int = None):
        """
        Initialize the String Question with the provided question text and ID.

        Args:
            question_text (str): The text of the question.
        """
        super().__init__(question_text, "string", answers, grouped, question_id)

    def group(self, threshold=85, case_sensitive=False):
        clusters = {}  # Maps original keys to their counts
        processed_keys = {}  # Maps original keys to their processed versions (e.g., lowercase)

        data = self.get_answers()

        for s in data:
            processed_s = s if case_sensitive else s.lower()

            if not clusters:
                clusters[s] = 1
                processed_keys[s] = processed_s
            else:
                processed_choices = list(processed_keys.values())
                original_choices = list(processed_keys.keys())

                best_match = process.extractOne(
                    processed_s,
                    processed_choices,
                    scorer=fuzz.WRatio,
                    score_cutoff=threshold
                )

                if best_match:
                    matched_index = best_match[2]
                    matched_original_key = original_choices[matched_index]
                    clusters[matched_original_key] += 1
                else:
                    clusters[s] = 1
                    processed_keys[s] = processed_s

        self.grouped = defaultdict(int, clusters)

    def manual_group_fix(self, group_name: str, answers: list[str]):
        """
        Manually fix the grouping by adjusting the count for a specific group.

        This method increments the count of a specified group by the number of answers
        in the provided list. Additionally, any answers that belong to the specified group
        are removed from the grouped dictionary.

        Args:
            group_name (str): The name of the group to be adjusted.
            answers (list): A list of answers that belong to the specified group.

        Example:
            manual_group_fix("Group A", ["Answer 1", "Answer 2"])
        """
        self.grouped[group_name] += len(answers)

        for key in self.grouped.keys():
            if key in answers:
                self.grouped.pop(key)

    def manual_group(self, groups: dict[str, int]):
        """
        Manually set the groups for the answers.

        This method directly replaces the `grouped` dictionary with a new one
        provided in the `groups` argument.

        Args:
            groups (dict): A dictionary where keys are group names and values are their counts.

        Example:
            manual_group({"Group A": 5, "Group B": 3})
        """
        self.grouped = groups

    def to_dict(self) -> dict:
        """
        Convert class instance to a dictionary
        :return: returns dict of values of the question.
        """
        return {
            "question_text": self.question_text,
            "type": self.question_type,
            "answers": self.get_answers(),
            "grouped": self.grouped,
            "id": self.question_id,
        }

    @classmethod
    def from_dict(cls, data):
        # Convert a dictionary back to the class instance
        return cls(
            data["question_text"],
            [Answer(answer) for answer in data["answers"]],
            data["grouped"],
            data["id"],
        )


class Questions:
    """
    A class for managing a collection of questions.

    Attributes:
        questions (list): A list to store all questions.

    Methods:
        add_question(question: str, type: [str]): Add a question to the collection.
        randomise() -> list: Return a shuffled list of the questions.
    """

    def __init__(self, questions_list: dict = None):
        """
        Initialize the Questions collection with an empty list and a counter set to 0.
        """
        self.questions = questions_list if questions_list else {}

    def add_question(self, question: str, type_: [str], question_id: int = None):
        """
        Add a question to the collection based on its type.

        Args:
            question (str): The text of the question to be added.
            type_ (str): The type of the question, either "string" or "multi choice".
            question_id:
        Raises:
            Exception: If the question type is unknown.
        """
        if type_ == "text":
            self.questions[question_id] = (StringQuestion(question, [], question_id=question_id))
        elif type_ == "multi":
            self.questions[question_id] = (MultiChoiceQuestion(question, [], question_id=question_id))
        else:
            raise Exception(f"Unknown question type: {type_}")

    def remove_question_by_text(self, question_text: str):
        self.questions.pop(self.get_index_by_text(question_text))

    def remove_question(self, question_id: int):
        del self.questions[question_id]

    def get_questions_text(self) -> list[str]:
        return [question.question_text for question in self.questions.values()]

    def group_all_questions(self):
        for question in self.questions.values():
            question.group()

    def group_and_sort_all_questions(self):
        for question in self.questions.values():
            question.group()
            question.sort_grouped_answers()

    def sort_all_questions(self):
        for question in self.questions.values():
            question.sort_grouped_answers()

    def randomise(self) -> list:
        """
        Return a shuffled list of questions.

        Returns:
            list: A shuffled list of questions.
        """
        copied_list = deepcopy(self.questions)
        shuffle(copied_list)
        return copied_list

    def get_question_by_text(self, question_text: str) -> Question:
        for question in self.questions:
            if question.question_text == question_text:
                return question

    def get_question_by_id(self, question_id: int) -> Question:
        return self.questions[question_id]

    def get_id_by_text(self, question_text: str) -> int:
        return next((k for k, v in self.questions.items() if v.question_text == question_text), None)

    def to_dict(self):
        # Convert class instance to a dictionary
        return {
            "questions": [question.to_dict() for question in self.questions.values()],
        }

    @classmethod
    def from_dict(cls, data):
        # Convert a dictionary back to the class instance
        questions_list = {}
        for q_data in data["questions"]:
            if q_data["type"] == "multi":
                questions_list[x.question_id] = (x:=MultiChoiceQuestion.from_dict(q_data))
            elif q_data["type"] == "string":
                questions_list[x.question_id] = (x:=StringQuestion.from_dict(q_data))
            else:
                raise ValueError(f"Unknown question type: {q_data['type']}")

        return cls(questions_list)
