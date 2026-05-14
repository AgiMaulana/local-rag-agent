from core.interfaces.embeddings import EmbeddingProvider
from core.interfaces.vector_store import VectorStore

class RetrievalService:

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ):
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    async def retrieve(
        self,
        question: str,
    ):

        embedding = await self.embedding_provider.embed(
            question
        )

        documents = await self.vector_store.search(
            embedding
        )

        return documents