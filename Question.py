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

    def __init__(self, answer: str):
        """
        Initialize the Answer with the provided answer text.

        Args:
            answer (str): The answer text.
        """
        self.answer = answer

    def to_dict(self) -> dict:
        # Convert class instance to a dictionary
        return {
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data):
        # Convert a dictionary back to the class instance
        return cls(data["answer"])


class Question(ABC):
    """
    Abstract base class representing a general question.

    Attributes:
        question_text (str): The text of the question.
        question_id (int): The unique identifier for the question.
        answers (list): A list to store answers to the question.
        grouped (defaultdict): A dictionary to store grouped answers with their count.

    Methods:
        group() -> dict: Abstract method to group answers, to be implemented in subclasses.
        add_answer(answer: str): Add an answer to the question.
        answers() -> list: Return a list of answers for the question.
    """

    def __init__(self, question_text: str, question_id: int, type_: str, answers: list):
        """
        Initialize the Question with the provided question text and ID.

        Args:
            question_text (str): The text of the question.
            question_id (int): The unique identifier for the question.
        """
        self.question_text = question_text
        self.question_id = question_id
        self.type_ = type_
        self.answers = answers
        self.grouped = defaultdict(int)

    @abstractmethod
    def group(self):
        """
        Abstract method to group answers based on specific logic.

        This method should be implemented by subclasses to group answers
        according to the needs of the question type.
        """
        pass

    def add_answer(self, answer: str):
        """
        Add an answer to the question.

        Args:
            answer (str): The answer text to be added.
        """
        self.answers.append(Answer(answer=answer))

    def get_answers(self) -> list[str]:
        """
        Get a list of answers for the question.

        Returns:
            list: A list of answer texts.
        """
        return [a.answer for a in self.answers]

    def sort_grouped_answers(self):
        self.grouped = sorted(self.grouped.items(), key=lambda x: x[1], reverse=True)

    def to_dict(self) -> dict:
        # Convert class instance to a dictionary
        return {
            "question_id": self.question_id,
            "question_text": self.question_text,
            "type": self.type_,
            "answers": self.get_answers(),
        }


class MultiChoiceQuestion(Question):
    """
    A class representing a multiple choice question.

    Inherits from the Question class and implements the group method
    to group answers based on their frequency.

    Methods:
        group() -> dict: Group answers based on their frequency and return the result.
    """

    def __init__(self, question_text: str, question_id: int, answers: list):
        """
        Initialize the Multiple Choice Question with the provided question text and ID.

        Args:
            question_text (str): The text of the question.
            question_id (int): The unique identifier for the question.
        """
        super().__init__(question_text, question_id, "multi", answers)

    def group(self):
        """
        Group answers based on their frequency.

        Returns:
            dict: A dictionary with answers as keys and their counts as values.
        """

        for answer in self.answers:
            self.grouped[answer.answer] += 1

    @classmethod
    def from_dict(cls, data):
        # Convert a dictionary back to the class instance
        return cls(
            data["question_text"],
            data["question_id"],
            [Answer(answer) for answer in data["answers"]],
        )


class StringQuestion(Question):
    """
    A class representing a string-based question where answers may vary in wording.

    Inherits from the Question class and implements the group method
    to group similar answers using string matching and fuzzing.

    Methods:
        group(threshold=80) -> dict: Group similar answers using fuzzy matching.
    """

    def __init__(self, question_text: str, question_id: int, answers: list):
        """
        Initialize the String Question with the provided question text and ID.

        Args:
            question_text (str): The text of the question.
            question_id (int): The unique identifier for the question.
        """
        super().__init__(question_text, question_id, "string", answers)

    def group(self, threshold: int = 80):
        """
        Group similar answers using fuzzy matching and a given threshold score.

        Args:
            threshold (int): The minimum similarity score to consider answers as matching.

        Returns:
            dict: A dictionary with grouped answers and their counts.
        """
        grouped = {}

        for s in self.answers:
            match = process.extractOne(s, grouped.keys(), scorer=fuzz.ratio, score_cutoff=threshold)

            if match:
                grouped[match[0]].append(s)
            else:
                grouped[s] = [s]

        self.grouped = {key: len(value) for key, value in grouped.items()}

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

    @classmethod
    def from_dict(cls, data):
        # Convert a dictionary back to the class instance
        return cls(
            data["question_text"],
            data["question_id"],
            [Answer(answer) for answer in data["answers"]],
        )


class Questions:
    """
    A class for managing a collection of questions.

    Attributes:
        questions (list): A list to store all questions.
        counter (int): A counter to keep track of the unique question IDs.

    Methods:
        add_question(question: str, type: [str]): Add a question to the collection.
        randomise() -> list: Return a shuffled list of the questions.
    """

    def __init__(self, questions_list: list):
        """
        Initialize the Questions collection with an empty list and a counter set to 0.
        """
        self.questions = questions_list
        self.counter = 0

    def add_question(self, question: str, type_: [str]):
        """
        Add a question to the collection based on its type.

        Args:
            question (str): The text of the question to be added.
            type_ (str): The type of the question, either "string" or "multi choice".
        Raises:
            Exception: If the question type is unknown.
        """
        if type_ == "text":
            self.questions.append(StringQuestion(question, self.counter, []))
        elif type_ == "multi":
            self.questions.append(MultiChoiceQuestion(question, self.counter, []))
        else:
            raise Exception(f"Unknown question type: {type_}")

        self.counter += 1

    def randomise(self) -> list:
        """
        Return a shuffled list of questions.

        Returns:
            list: A shuffled list of questions.
        """
        copied_list = deepcopy(self.questions)
        shuffle(copied_list)
        return copied_list

    def get_by_id(self, id_: int) -> Question:
        return self.questions[id_]

    def get_by_text(self, text: str) -> Question:
        for question in self.questions:
            if question.question_text == text:
                return question

    def to_dict(self):
        # Convert class instance to a dictionary
        return {
            "questions": [question.to_dict() for question in self.questions],
        }

    @classmethod
    def from_dict(cls, data):
        # Convert a dictionary back to the class instance
        questions_list = []

        for q_data in data["questions"]:
            if q_data["type"] == "multi":
                questions_list.append(MultiChoiceQuestion.from_dict(q_data))
            elif q_data["type"] == "string":
                questions_list.append(StringQuestion.from_dict(q_data))
            else:
                raise ValueError(f"Unknown question type: {q_data['type']}")

        return cls(questions_list)
