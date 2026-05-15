from typing import Protocol

class VectorStoreProvider(Protocol):

    def get_client(self):
        """Returns the underlying vector store client instance."""
        pass

    def as_retriever(self):
        """Returns a retriever instance for searching the vector store."""
        pass

    def from_documents(
        self,
        documents,
        embedding,
    ):
        """Ingests the given documents into the vector store using the provided embedding function."""
        pass

    def delete_by_source(self, source: str):
        """Deletes all documents that match the given source path in metadata."""
        pass