from langchain_openai import OpenAIEmbeddings

from core.interfaces.embeddings import (
    EmbeddingProvider,
)
from core.models.model_config import (
    ModelConfig,
)


class LmStudioEmbeddingProvider(
    EmbeddingProvider
):

    def __init__(
        self,
        config: ModelConfig,
    ):

        self.client = OpenAIEmbeddings(
            openai_api_base=config.base_url,
            openai_api_key=config.api_key,
            model=config.model,
            check_embedding_ctx_length=False,
        )

    def get_client(self):
        return self.client