import os
import json
import random


class MockMethod:
    def __init__(self, input_log_file: str | None = None, mock_questionnaire: str | dict | None = None,):
        self.input_log_file = input_log_file
        if isinstance(mock_questionnaire, str):
            mock_questionnaire = json.loads(mock_questionnaire)
        self.mock_quesitonnaire = mock_questionnaire
        self.usage = {}

    def generate_questionnaire(self, _: str) -> dict:
        self.usage = {
            "completion_tokens": random.randint(0, 99999),
            "prompt_tokens": random.randint(0, 99999),
            "total_tokens": random.randint(0, 99999)
        }
        if self.mock_quesitonnaire is not None:
            return self.mock_quesitonnaire
        with open(os.path.join("logged_requests", self.input_log_file), "r", encoding="utf-8") as file:
            obj = json.loads(file.read())
            return json.loads(obj["response"]["choices"][0]["message"]["content"])

    def evaluate_answers(self, _source_material: str, _questionnaire: str | dict, _answers: list[str]) -> dict:
        self.usage = {
            "completion_tokens": random.randint(0, 99999),
            "prompt_tokens": random.randint(0, 99999),
            "total_tokens": random.randint(0, 99999)
        }
        mocked_answers = []
        for i in range(len(_answers)):
            choice = random.choice([
                {
                    "question_evaluation": "answerable",
                    "evaluation": "incorrect",
                    "reasoning": "According to the text, the Grand Duchy of Lithuania became the largest state in Europe in the 15th century, not the 16th century.",
                    "answer": "15th"
                },
                {
                    "question_evaluation": "answerable",
                    "evaluation": "correct"
                },
                {
                    "question_evaluation": "unanswerable",
                    "evaluation": "unanswerable",
                    "reasoning": "The provided source material does not mention Lithuania joining any organization in 2003."
                }
            ])
            mocked_answers.append(choice.copy())
        return {
            "evaluations": mocked_answers
        }
    
    def reset_usage(self):
        self.usage = {}