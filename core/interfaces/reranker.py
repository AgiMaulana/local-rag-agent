from typing import Protocol
from core.models.retrieved_document import RetrievedDocument

class Reranker(Protocol):

    async def rerank(
        self,
        query: str,
        documents: list[RetrievedDocument],
    ) -> list[RetrievedDocument]:
        """Reranks the given list of documents based on their relevance to the query."""
        pass