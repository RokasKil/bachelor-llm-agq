from .AbstractSimpleMethod import AbstractSimpleMethod
import os
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.completion_create_params import ResponseFormat


class AlibabaSimpleMethod(AbstractSimpleMethod):
    def __init__(self, model=None, top_p = None, temperature = None, question_count: int = None, api_url: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1", api_key: str = None, logging: bool = None):
        if api_key is None:
            api_key = os.getenv("ALIBABA_API_KEY")
        if model is None:
            model = os.getenv("ALIBABA_MODEL", "qwq-plus")
        super().__init__(question_count, api_key, api_url, logging)
        self.model = model
        self.top_p = top_p
        self.temperature = temperature

    @property
    def system_role(self) -> str:
        return "system"
    
    def execution_params(self) -> dict:
        params = super().execution_params()
        params["model"] = self.model

        # does nothing for qwq models
        if self.top_p is not None:
            params["top_p"] = self.top_p # The probability threshold of the sampling method. A greater value indicates a greater randomness of generated content.
        if self.temperature is not None:
            params["temperature"] = self.temperature # The temperature determines the randomness of the output. Valid values: (0,2). Higher values mean more random completions. Lower values mean more deterministic completions.
       
        if self.model.startswith("qwq"):
            params["stream"] = True
            params["stream_options"] = {
                "include_usage": True
            }
        return params