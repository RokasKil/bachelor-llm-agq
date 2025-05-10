from abc import ABC, abstractmethod
from typing import Tuple
from openai import OpenAI, OpenAIError
from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionMessageParam
from openai.types.chat.completion_create_params import ResponseFormat
from openai.types.completion_usage import CompletionUsage
import os
import time
import json
import re

class AbstractBaseMethod(ABC):
    def __init__(self, question_count: int = None, api_key = None, api_url: str = None, logging: bool = None):
        if logging is None:
            logging = os.getenv("LOGGING", "false").lower() == "true"
        if question_count is None:
            question_count = int(os.getenv("QUESTION_COUNT", "10"))
        self.logging = logging
        self.openai_client = OpenAI(api_key=api_key, base_url=api_url)
        self.usage = {}
        self.question_count = question_count

    @abstractmethod
    def execution_params(self) -> dict:
        return {}

    def execute(self, response_format: ResponseFormat, messages: list[ChatCompletionMessageParam]) -> ChatCompletion | list[ChatCompletionChunk]:
        try:
            params = self.execution_params()
            params.setdefault("messages", []).extend(messages)
            params.setdefault("response_format", response_format)
            result = self.openai_client.chat.completions.create(**params)
            if 'stream' in params and params["stream"]:
                results = []
                for chunk in result:
                    results.append(chunk)
                self._sum_usage(results[-1].usage)
                self._log({"request": params, "response": [chunk.to_dict() for chunk in results]})
                return results
            else:
                self._sum_usage(result.usage)
                self._log({"request": params, "response": result.to_dict()})
                return result
        except OpenAIError as e:
            self._log({"request": params, "response": str(e)})
            raise e

    def get_response_text(self, response: ChatCompletion | list[ChatCompletionChunk]) -> str:
        if isinstance(response, ChatCompletion):
            return response.choices[0].message.content
        else:
            flattened_choices = (
                choice.delta.content 
                for chunk in response 
                for choice in chunk.choices
            )
            return "".join(filter(lambda content: content != None, flattened_choices))

    @abstractmethod
    def generate_questionnaire(self, text: str) -> dict:
        pass

    @abstractmethod
    def evaluate_answers(self, source_material: str, questionnaire: str | dict, answers: list[str]) -> dict:
        pass

    def _log(self, obj: object):
        if self.logging:
            os.makedirs("logged_requests", exist_ok=True)  # using makedirs instead of mkdir
            timestamp = int(time.time() * 1000)
            with open(os.path.join("logged_requests", f"{timestamp}_{self.__class__.__name__}.json"), "w") as file:
                file.write(json.dumps(obj, indent=2))
    
    def _sum_usage(self, usage: CompletionUsage | dict, sum_target: dict = None):
        if usage is None:
            return
        if isinstance(usage, CompletionUsage):
            usage = usage.to_dict()
        if sum_target is None:
            sum_target = self.usage
        for key, value in usage.items():
            if isinstance(value, dict):
                self._sum_usage(value, sum_target.setdefault(key, {}))
            else:
                if key in sum_target:
                    sum_target[key] += value
                else:
                    sum_target[key] = value
    
    def reset_usage(self):
        self.usage = {}
            
    def validate_questionnaire(self, text: str):
        questions = json.loads(text)
        if "questions" not in questions:
            raise Exception("The questionnaire must contain a list of questions.")
        if len(questions["questions"]) != self.question_count:
            raise Exception(f"The questionnaire must contain exactly {self.question_count} questions")
        for index, question in enumerate(questions["questions"]):
            if "question_text" not in question:
                raise Exception(f"Question {index + 1} does not contain a 'question_text' property.")
            if "answer" not in question:
                raise Exception(f"Question {index + 1} does not contain an 'answer' property.")
            if "nr" not in question:
                raise Exception(f"Question {index + 1} does not contain an 'nr' property.")
            if question["answer"].strip() == "":
                raise Exception(f"Question {index + 1} has an empty answer.")
            
    def validate_evaluations(self, text: str, question_count: int):
        evaluations = json.loads(text)
        if "evaluations" not in evaluations:
            raise Exception("The response must contain a list of evaluations.")
        if len(evaluations["evaluations"]) != question_count:
            raise Exception(f"The response must contain exactly {question_count} evaluations")
        for index, evaluation in enumerate(evaluations["evaluations"]):
            if "evaluation" not in evaluation:
                raise Exception(f"Evaluation {index + 1} does not contain an 'evaluation' property.")
            if "nr" not in evaluation:
                raise Exception(f"Evaluation {index + 1} does not contain an 'nr' property.")
            if evaluation["evaluation"] not in ["correct", "incorrect", "unanswerable"]:
                raise Exception(f"Evaluation {index + 1} has an invalid evaluation value. Must be 'correct', 'incorrect', or 'unanswerable'.")
            if evaluation["evaluation"] == "incorrect":
                if "reasoning" not in evaluation or "answer" not in evaluation:
                    raise Exception(f"Incorrect evaluation {index + 1} must contain both 'reasoning' and 'answer' properties.")
            if evaluation["evaluation"] == "unanswerable":
                if "reasoning" not in evaluation:
                    raise Exception(f"Unanswerable evaluation {index + 1} must contain a 'reasoning' property.")

    def __enter__(self):
        return self

    def __exit__(self, **kwargs):
        self.openai_client.close()