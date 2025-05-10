
from methods.AbstractBaseMethod import AbstractBaseMethod
from methods.OpenAiSimpleMethod import OpenAiSimpleMethod
from methods.OpenAiComplexMethod import OpenAiComplexMethod
from methods.AlibabaSimpleMethod import AlibabaSimpleMethod
from methods.AlibabaComplexMethod import AlibabaComplexMethod
from methods.MockMethod import MockMethod

class MethodConfig:
    def __init__(self, method: AbstractBaseMethod, use: bool = True):
        self.method = method
        self.use = use

METHODS = {
    "MOCK_METHOD_1": MethodConfig(MockMethod("1742637931091_OpenAiSimpleMethod.json"), False),
    "OpenAi-simple-o3-mini-2025-01-31": MethodConfig(OpenAiSimpleMethod(), True),
    "OpenAi-improved-o3-mini-2025-01-31": MethodConfig(OpenAiComplexMethod(), True),
    "Alibaba-simple-qwen-max-2025-01-25": MethodConfig(AlibabaSimpleMethod(), True),
    "Alibaba-improved-qwen-max-2025-01-25": MethodConfig(AlibabaComplexMethod(), True)
}