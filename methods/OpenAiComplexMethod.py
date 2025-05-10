from .AbstractComplexMethod import AbstractComplexMethod
import os

class OpenAiComplexMethod(AbstractComplexMethod):
    def __init__(self, model: str = None, reasoning_effort: str = "high", answer_agents: int = None, agents: int = None, rounds: int = None, question_count: int = None, api_url: str = None, api_key: str = None, logging: bool = None):
        if api_key is None:
            api_key = os.getenv("OPEN_AI_API_KEY")
        if model is None:
            model = os.getenv("OPEN_AI_MODEL", "o3-mini-2025-01-31")
        super().__init__(answer_agents, agents, rounds, question_count, api_key, api_url, logging)
        self.model = model
        self.reasoning_effort = reasoning_effort

    def execution_params(self) -> dict:
        params = super().execution_params()
        params["model"] = self.model
        params["reasoning_effort"] = self.reasoning_effort
        return params