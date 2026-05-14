from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

class RecursiveChunker:

    def __init__(
        self,
        chunk_size: int,
        chunk_overlap: int,
    ):

        self.splitter = (
            RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
        )

    def split(
        self,
        documents,
    ):

        return self.splitter.split_documents(
            documents
        )