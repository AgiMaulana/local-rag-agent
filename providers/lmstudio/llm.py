from langchain_openai import ChatOpenAI

from core.interfaces.llm import (
    LlmProvider,
)
from core.models.model_config import (
    ModelConfig,
)


class LmStudioLlmProvider(
    LlmProvider
):

    def __init__(
        self,
        config: ModelConfig,
    ):

        self.client = ChatOpenAI(
            openai_api_base=config.base_url,
            openai_api_key=config.api_key,
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            streaming=config.streaming,
        )

    def get_client(self):
        return self.client