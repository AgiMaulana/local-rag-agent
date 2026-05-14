from langchain_community.document_loaders import (
    CSVLoader,
)


class CsvLoaderService:

    def __init__(self, knowledge_dir: str):
        self.knowledge_dir = knowledge_dir
        self.loader_class = CSVLoader

    def load(self, file_path: str):
        return self.loader_class(file_path).load()