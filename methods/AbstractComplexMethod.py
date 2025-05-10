from typing import Tuple
from .AbstractBaseMethod import AbstractBaseMethod
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam, ChatCompletionChunk
from openai.types.chat.completion_create_params import ResponseFormat
import json
import os
import random
class AbstractComplexMethod(AbstractBaseMethod):
    
    def __init__(self, answer_agents: int = None, agents: int = None, rounds: int = None, question_count: int = None, api_key: str = None, api_url: str  = None, logging: bool = None):
        super().__init__(question_count, api_key, api_url, logging)
        if agents is None:
            agents = int(os.getenv("COMPLEX_METHOD_AGENTS", "2"))
        if rounds is None:
            rounds = int(os.getenv("COMPLEX_METHOD_ROUNDS", "2"))
        if answer_agents is None:
            answer_agents = int(os.getenv("COMPLEX_METHOD_ANSWERS", "4"))
        self.agents = agents
        self.rounds = rounds
        self.answer_agents = answer_agents

    @property
    def system_role(self) -> str:
        return "developer"
    
    def generate_questionnaire_full_response(self, text: str) -> Tuple[list[list[ChatCompletionMessageParam]], ChatCompletion | list[ChatCompletionChunk]]:
        agent_contexts = []
        # Sugeneruojam klausimynus paprastuoju būdų pirmam roundui
        print("getting round 1 quizes")
        for agent in range(self.agents):
            messages = [
                self.get_questionnaire_system_prompt(),
                {
                    "role": "user",
                    "content": text
                }
            ]
            result = self.get_response_text(self.execute(self.get_questionnaire_response_format(), messages))
            self.validate_questionnaire(result)
            messages.append(
                {
                    "role": "assistant",
                    "content": result
                }
            )
            agent_contexts.append(messages)
        
        # Kitiems roundams paduodam kitų agentų klausimynus ir prašom atnaujinti savo klausimyną
        for round in range(1, self.rounds):
            print(f"getting round {round + 1} quizes")
            responses = list(map(lambda agent_context: agent_context[-1]["content"], agent_contexts))
            for index, agent_context in enumerate(agent_contexts):
                # visi klausimynai  tik ne mūsų, tęsiam esamą dialogą
                agent_context.append(self.get_questionnaire_comparison_message(responses[:index] + responses[index + 1:]))
                result = self.get_response_text(self.execute(self.get_questionnaire_response_format(), agent_context))
                self.validate_questionnaire(result)
                agent_context.append(
                    {
                        "role": "assistant",
                        "content": result
                    }
                )
        
        print(f"getting the best quiz")
        #Surenkam galutinius klausimynus ir prašom pasirinkti geriausią
        responses = list(map(lambda agent_context: agent_context[-1]["content"], agent_contexts))
        result = self.execute(
            self.get_deciding_response_format(),
            self.get_deciding_messages(text, responses)
        )
        answer = self.get_response_text(result)
        print(f"the best quiz was {answer} out of {self.agents}")
        self.last_debate = agent_contexts
        return (agent_contexts, result)
    
    def generate_questionnaire(self, text: str) -> dict:
        agent_contexts, result = self.generate_questionnaire_full_response(text)
        return json.loads(agent_contexts[int(self.get_response_text(result)) - 1][-1]["content"])

    def get_questionnaire_system_prompt(self) -> ChatCompletionMessageParam:
        return {
            "role": self.system_role,
            "content": f"Create a fill-in-the-blank questionnaire based on the presented material, the questions must be in a form of a statement with a blank part marked by \"__________\" that needs to be filled in with the answer, an example question is \"Washington, D.C. is renowned for its national monuments and museums concentrated on and around the __________.\" with the answer \"National Mall\". The questions must be independant of each other, diverse and answerable based on the presented material, make sure you can't find the answers to questions in other questions. The questionnaire must contain {self.question_count} questions. The questions must match the language of the text.\nOutput a json object that has one property 'questions' with a list of objects with properties 'nr', 'question_text' and 'answer'." 
        }

    def get_questionnaire_comparison_message(self, responses: list[str]) -> ChatCompletionMessageParam:
        return {
            "role": "user",
            "content": f"Here are some questionnaires given by other agents: \n {'\n'.join(responses)}\n Closely examine your questionnaire and the quizes of other agents and provide an updated quiz."
        }

    def get_deciding_messages(self, material, questionnaires: list[str]) -> list[ChatCompletionMessageParam]:
        return [
            {
                "role": self.system_role,
                "content": f"Multiple agent created fill-in-the-blank questionnaires based on the presented material, the questions must be in a form of a statement with a blank part marked by \"__________\" that needs to be filled in with the answer, an example question is \"Washington, D.C. is renowned for its national monuments and museums concentrated on and around the __________.\" with the answer \"National Mall\". The questions must be diverse and answerable based on the presented material, it's important that you can't find the answers to questions in other questions. The questionnaire must contain {self.question_count} questions. The questions must match the language of the text. You will be presented the material and the questionnaires of other agents formatted as a json object that has one property 'questions' with a list of objects with string properties 'question_text' and 'answer', you must decide which questionnaire is the best. Answer with a single number starting from 1 indicating which questionnaire is the best."
            },
            {
                "role": "user",
                "content": material
            },
            {
                "role": "user",
                "content": '\n'.join(questionnaires)
            }
        ]

    def get_deciding_response_format(self) -> ResponseFormat:
        return {
            "type": "text"
        }
    
    def get_questionnaire_response_format(self) -> ResponseFormat:
        return {"type": "json_object"}
    
    def evaluate_answers(self, source_materal: str, questionnaire: str | dict, answers: list[str]) -> dict:
        raise NotImplementedError("evaluate_answers method must be implemented by child classes")
    
    def _evaluate_answers_full_response(self, source_material: str, questionnaire: str | dict, answers: str) -> Tuple[list[ChatCompletion | list[ChatCompletionChunk]], dict]:
        questionnaire = json.loads(questionnaire) if isinstance(questionnaire, str) else questionnaire
        if len(questionnaire["questions"]) != len(answers):
            raise ValueError("The number of answers must match the number of questions.")
        answers_prompt_json = [
            {
                "question_text": question["question_text"],
                "provided_answer": answer
            } for question, answer in zip(questionnaire["questions"], answers)
        ]
        results = []
        for i in range(self.answer_agents):
            results.append(self.execute(
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
            ))
        
        aggregated_evaluation = [{} for _ in range(len(answers))]
        for result in results:
            text_result = self.get_response_text(result)
            self.validate_evaluations(text_result, len(answers))
            evaluations = json.loads(text_result) 
            for index, evaluation in enumerate(evaluations["evaluations"]):
                key = evaluation["evaluation"]
                aggregated_evaluation[index].setdefault(key, []).append(evaluation)
        final_evaluation = []
        for eval_group in aggregated_evaluation:
            max_eval_count = len(max(eval_group.values(), key=len))
            final_evaluation.append(random.choice(list(filter(lambda evals: len(evals) == max_eval_count, eval_group.values())))[0])

        return results, {"evaluations": final_evaluation}
    
    def evaluate_answers(self, source_materal: str, questionnaire: str | dict, answers: list[str]) -> dict:
        results, evaluation = self._evaluate_answers_full_response(source_materal, questionnaire, answers)
        return evaluation
    
    def get_evaluation_system_prompt(self, question_count) -> ChatCompletionMessageParam:
        return {
            "role": self.system_role,
            "content": ("You will be provided a fill-in-the-blank questionnairea and the source material it is based on, "
                        "the questions are in a form of a statement with a single blank part marked by \"__________\" that needs to be filled in with the answer, "
                        "an example question is \"Washington, D.C. is renowned for its national monuments and museums concentrated on and around the __________.\" "
                        "with the answer \"National Mall\"."
                        f"You will be presented the source material and the questionnaires as json array of objects with string properties 'question_text', 'provided_answer', there are a total of {question_count} questions. "
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