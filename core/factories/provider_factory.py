from config import config

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

    return LmStudioEmbeddingProvider(
        base_url=config.lm_studio_base_url,
        model=config.embedding_model,
    )

def create_llm_provider():

    return LmStudioLlmProvider(
        base_url=config.lm_studio_base_url,
        model=config.llm_model,
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