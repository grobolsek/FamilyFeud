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

    def __init__(self, question_text: str, question_id: int):
        """
        Initialize the Question with the provided question text and ID.

        Args:
            question_text (str): The text of the question.
            question_id (int): The unique identifier for the question.
        """
        self.question_text = question_text
        self.question_id = question_id
        self.answers = []
        self.grouped = defaultdict(int)

    @abstractmethod
    def group(self) -> dict[str, int]:
        """
        Abstract method to group answers based on specific logic.

        This method should be implemented by subclasses to group answers
        according to the needs of the question type.

        Returns:
            dict: A dictionary with grouped answers and their counts.
        """
        pass

    def add_answer(self, answer: str):
        """
        Add an answer to the question.

        Args:
            answer (str): The answer text to be added.
        """
        self.answers.append(Answer(answer=answer))

    def answers(self) -> list[str]:
        """
        Get a list of answers for the question.

        Returns:
            list: A list of answer texts.
        """
        return [a.answer for a in self.answers]


class MultyChoiceQuestion(Question):
    """
    A class representing a multiple choice question.

    Inherits from the Question class and implements the group method
    to group answers based on their frequency.

    Methods:
        group() -> dict: Group answers based on their frequency and return the result.
    """

    def __init__(self, question_text: str, question_id: int):
        """
        Initialize the Multiple Choice Question with the provided question text and ID.

        Args:
            question_text (str): The text of the question.
            question_id (int): The unique identifier for the question.
        """
        super().__init__(question_text, question_id)

    def group(self) -> dict[str, int]:
        """
        Group answers based on their frequency.

        Returns:
            dict: A dictionary with answers as keys and their counts as values.
        """
        d = defaultdict(int)

        for answer in self.answers:
            d[answer.answer] += 1

        return d


class StringQuestion(Question):
    """
    A class representing a string-based question where answers may vary in wording.

    Inherits from the Question class and implements the group method
    to group similar answers using string matching and fuzzing.

    Methods:
        group(threshold=80) -> dict: Group similar answers using fuzzy matching.
    """

    def __init__(self, question_text: str, question_id: int):
        """
        Initialize the String Question with the provided question text and ID.

        Args:
            question_text (str): The text of the question.
            question_id (int): The unique identifier for the question.
        """
        super().__init__(question_text, question_id)

    def group(self, threshold: int = 80) -> dict[str, int]:
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

        return {key: len(value) for key, value in grouped.items()}


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

    def __init__(self):
        """
        Initialize the Questions collection with an empty list and a counter set to 0.
        """
        self.questions = []
        self.counter = 0

    def add_question(self, question: str, type_: [str]):
        """
        Add a question to the collection based on its type.

        Args:
            question (str): The text of the question to be added.
            type_ (str): The type of the question, either "string" or "multy choice".

        Raises:
            Exception: If the question type is unknown.
        """
        if type_ == "string":
            self.questions.append(StringQuestion(question, self.counter))
        elif type_ == "multy choice":
            self.questions.append(MultyChoiceQuestion(question, self.counter))
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