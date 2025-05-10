from .OpenAiSimpleMethod import OpenAiSimpleMethod
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
from openai.types.chat.completion_create_params import ResponseFormat
import os
import json


class AnswerGenerator(OpenAiSimpleMethod):
    def __init__(self, model: str = "gpt-4o", reasoning_effort: str = None, question_count: int = None, api_url: str = None, api_key: str = None, logging: bool = None):
        super().__init__(model, reasoning_effort, question_count, api_url, api_key, logging)
    
    def _generate_answers(self, questionnaire: list, answer_count: int) -> ChatCompletion:
        result =  self.execute(
            self.get_generate_answers_response_format(),
            [
                self.get_generate_answers_system_prompt(answer_count),
                {
                    "role": "user",
                    "content": json.dumps(questionnaire, indent=2)
                }
            ]
        )
        return result
    
    def generate_answers(self, questionnaire: str | list, answer_count: int) -> dict:
        if isinstance(questionnaire, str):
            questionnaire = json.loads(questionnaire)
        result = self.get_response_text(self._generate_answers(questionnaire, answer_count))
        self.validate_answers(result, questionnaire, answer_count)
        return json.loads(result)
    
    def get_generate_answers_response_format(self) -> ResponseFormat:
        return {"type": "json_object"}

    def get_generate_answers_system_prompt(self, answer_count: int) -> ChatCompletionMessageParam:
        return {
            "role": self.system_role,
            "content": f"You will be provided a fill-in-the-blank questionnaire the source material it is based on, the questions are in a form of a statement with a blank part marked by \"__________\" that needs to be filled in with the answer, an example question is \"Washington, D.C. is renowned for its national monuments and museums concentrated on and around the __________.\" with the answer \"National Mall\". You will be presented the questionnaire as json array of objects with string properties 'question_text' , 'answer' and 'generate_answers', the 'generate_answers' property contains a list string which can be either 'correct or 'incorrect'. Your task is to create {answer_count} answers to each question with them being correct or incorrect based on the 'generate_answers' property. When answering correctly sometimes but not always change the wording of the answer. Make sure that the sentence still flows properly with your answer inserted.\nDon't escape unicode symbols in the answers.\nRespond with a json object containing one property 'answers' with an array of arrays for each question containing objects with 'answer' property and 'type' property consisting of 'correct', 'incorrect'."
        }
    
    def validate_answers(self, answers: str | dict, questionnaire: list, answer_count: int) -> dict:
        if isinstance(answers, str):
            answers = json.loads(answers)

        if not isinstance(answers, dict) or 'answers' not in answers:
            raise ValueError("Response must be a dictionary with 'answers' key")

        if len(answers['answers']) != len(questionnaire):
            raise ValueError(f"Number of answer sets ({len(answers['answers'])}) does not match number of questions ({len(questionnaire)})")

        for i, answer_set in enumerate(answers['answers']):
            if not isinstance(answer_set, list):
                raise ValueError(f"Answer set {i} must be a list")
            
            if len(answer_set) != answer_count:
                raise ValueError(f"Answer set {i} must contain exactly {answer_count} answers")

            for answer in answer_set:
                if not isinstance(answer, dict):
                    raise ValueError(f"Each answer in set {i} must be a dictionary")
            
            if 'answer' not in answer or 'type' not in answer:
                raise ValueError(f"Each answer must contain 'answer' and 'type' properties")
            
            if answer['type'] not in ['correct', 'incorrect']:
                raise ValueError(f"Answer type must be either 'correct' or 'incorrect'")

        return answers