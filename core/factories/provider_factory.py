from config import config

from core.models.model_config import (
    ModelConfig,
)

from providers.lmstudio.llm import (
    LmStudioLlmProvider,
)

from providers.lmstudio.embeddings import (
    LmStudioEmbeddingProvider,
)

from providers.chroma.vector_store import (
    ChromaVectorStoreProvider,
)


def create_embedding_provider():

    embedding_config = ModelConfig(
        model=config.embedding_model,
        api_key=config.api_key,
        base_url=config.lm_studio_base_url,
    )

    return LmStudioEmbeddingProvider(
        config=embedding_config,
    )


def create_llm_provider():

    llm_config = ModelConfig(
        model=config.llm_model,
        api_key=config.api_key,
        base_url=config.lm_studio_base_url,
    )

    return LmStudioLlmProvider(
        config=llm_config,
    )


def create_vector_store_provider():

    embeddings = (
        create_embedding_provider()
    )

    return ChromaVectorStoreProvider(
        persist_directory=(
            config.vector_db_dir
        ),
        embedding_function=(
            embeddings.get_client()
        ),
    )