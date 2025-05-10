from .AbstractBaseMethod import AbstractBaseMethod
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
from openai.types.chat.completion_create_params import ResponseFormat
import json

class AbstractSimpleMethod(AbstractBaseMethod):
    
    @property
    def system_role(self) -> str:
        return "developer"

    def _generate_questionnaire_full_response(self, text: str) -> ChatCompletion:
        result =  self.execute(
            self.get_questionnaire_response_format(),
            [
                self.get_questionnaire_system_prompt(),
                {
                    "role": "user",
                    "content": text
                }
            ]
        )
        return result
    
    def generate_questionnaire(self, text: str) -> str:
        result = self.get_response_text(self._generate_questionnaire_full_response(text))
        self.validate_questionnaire(result)
        return json.loads(result)
    
    def _evaluate_answers_full_response(self, source_material: str, questionnaire: str | dict, answers: str) -> ChatCompletion:
        questionnaire = json.loads(questionnaire) if isinstance(questionnaire, str) else questionnaire
        if len(questionnaire["questions"]) != len(answers):
            raise ValueError("The number of answers must match the number of questions.")
        answers_prompt_json = [
            {
                "question_text": question["question_text"],
                "provided_answer": answer
            } for question, answer in zip(questionnaire["questions"], answers)
        ]
        result =  self.execute(
            self.get_evaluation_response_format(),
            [
                self.get_evaluation_system_prompt(len(answers_prompt_json)),
                {
                    "role": "user",
                    "content": source_material
                },
                {
                    "role": "user",
                    "content": json.dumps(answers_prompt_json, indent = 2)
                },
            ]
        )
        return result
    
    def evaluate_answers(self, source_materal: str, questionnaire: str | dict, answers: list[str]) -> dict:
        result = self.get_response_text(self._evaluate_answers_full_response(source_materal, questionnaire, answers))
        self.validate_evaluations(result, len(answers))
        return json.loads(result)

    def get_questionnaire_system_prompt(self) -> ChatCompletionMessageParam:
        return {
            "role": self.system_role,
            "content": f"Create a fill-in-the-blank questionnaire based on the presented material, the questions must be in a form of a statement with a blank part marked by \"__________\" that needs to be filled in with the answer, an example question is \"Washington, D.C. is renowned for its national monuments and museums concentrated on and around the __________.\" with the answer \"National Mall\". The questions must be independant of each other, diverse and answerable based on the presented material, make sure you can't find the answers to questions in other questions. The questionnaire must contain {self.question_count} questions. The questions must match the language of the text.\nOutput a json object that has one property 'questions' with a list of objects with properties 'nr', 'question_text' and 'answer'; 'nr' is the question index starting from 1."
        }
    
    def get_questionnaire_response_format(self) -> ResponseFormat:
        return {"type": "json_object"}
    
    def get_evaluation_system_prompt(self, question_count) -> ChatCompletionMessageParam:
        return {
            "role": self.system_role,
            "content": ("You will be provided a fill-in-the-blank questionnaire and the source material it is based on, "
                        "the questions are in a form of a statement with a single blank part marked by \"__________\" that needs to be filled in with the answer, "
                        "an example question is \"Washington, D.C. is renowned for its national monuments and museums concentrated on and around the __________.\" "
                        "with the answer \"National Mall\"."
                        f"You will be presented the source material and the questionnaires as json array of objects with string properties 'question_text', 'provided_answer' there are a total of {question_count} questions. "
                        "Your task is to determine if the question is answerable based on the provided source material and whether the answer is correct. "
                        "Respond with a json object containing one property 'evaluations' with an array of objects, one for each question with these parameters:\n"
                        "'nr' the index of the question starting from 1;\n"
                        "'question_evaluation' containing either 'answerable', 'unanswerable' use 'unanswerable' if the provided question can't be answered with the provided source material;\n"
                        "'evaluation' containing one of these values 'correct', 'incorrect' or 'unanswerable', use 'unanswerable' if the provided question can't be answered with the provided source material;\n"
                        "'reasoning' a single sentence reasoning explaining the evaluation;\n"
                        "'answer' the actual answer.\n"
                        "Omit 'reasoning' if the evaluation was 'correct' and omit 'answer' if the evaluation was 'correct' or 'unanswerable'.")
        }
    
    def get_evaluation_response_format(self) -> ResponseFormat:
        return {"type": "json_object"}