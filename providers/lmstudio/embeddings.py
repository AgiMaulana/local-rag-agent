from langchain_openai import OpenAIEmbeddings

from core.interfaces.embeddings import (
    EmbeddingProvider,
)

class LmStudioEmbeddingProvider(
    EmbeddingProvider
):

    def __init__(
        self,
        base_url: str,
        model: str,
    ):

        self.client = OpenAIEmbeddings(
            openai_api_base=base_url,
            openai_api_key="lm-studio",
            model=model,
            check_embedding_ctx_length=False,
        )

    def get_client(self):
        return self.client