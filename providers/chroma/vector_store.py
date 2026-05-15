from langchain_chroma import Chroma

from core.interfaces.vector_store import (
    VectorStoreProvider,
)

class ChromaVectorStoreProvider(
    VectorStoreProvider
):

    def __init__(
        self,
        persist_directory: str,
        embedding_function,
    ):

        self.client = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_function,
        )

    def get_client(self):
        return self.client

    def as_retriever(self):
        return self.client.as_retriever()

    def from_documents(
        self,
        documents,
        embedding,
    ):
        self.client.add_documents(documents=documents)

    def delete_by_source(self, source: str):
        self.client.delete(where={"source": {"$eq": source}})