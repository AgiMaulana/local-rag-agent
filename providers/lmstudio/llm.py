from langchain_openai import ChatOpenAI

from core.interfaces.llm import (
    LlmProvider,
)

class LmStudioLlmProvider(
    LlmProvider
):

    def __init__(
        self,
        base_url: str,
        model: str,
    ):

        self.client = ChatOpenAI(
            openai_api_base=base_url,
            openai_api_key="lm-studio",
            model=model,
            streaming=False,
        )

    def get_client(self):
        return self.client