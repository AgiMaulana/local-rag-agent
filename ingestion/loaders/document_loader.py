import os

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    CSVLoader,
)

from ingestion.loaders.json_loader import (
    JsonLoaderService,
)


class DocumentLoaderService:

    def __init__(
        self,
        knowledge_dir: str,
    ):

        self.knowledge_dir = knowledge_dir
        self.json_loader = JsonLoaderService(knowledge_dir)
        self._loader_map = {
            ".pdf": PyPDFLoader,
            ".txt": TextLoader,
            ".md": UnstructuredMarkdownLoader,
            ".csv": CSVLoader,
        }

    def _load_json(self, file_path: str):
        return self.json_loader.load(file_path)

    def load_documents(self):

        docs = []

        if not os.path.exists(
            self.knowledge_dir
        ):

            raise Exception(
                f"Directory does not exist: "
                f"{self.knowledge_dir}"
            )

        for root, _, files in os.walk(
            self.knowledge_dir
        ):

            for file in files:

                file_path = os.path.join(
                    root,
                    file,
                )

                ext = os.path.splitext(
                    file
                )[1].lower()

                if ext == ".json":
                    try:
                        print(f"📖 Loading {file_path}")
                        loaded_docs = self._load_json(file_path)
                    except Exception as e:
                        print(f"⚠️ Failed to load {file_path}: {e}")
                        continue
                elif ext not in self._loader_map:
                    continue
                else:
                    try:
                        print(f"📖 Loading {file_path}")
                        loader = self._loader_map[ext](file_path)
                        loaded_docs = loader.load()
                    except Exception as e:
                        print(f"⚠️ Failed to load {file_path}: {e}")
                        continue

                    for doc in loaded_docs:
                        doc.metadata["source"] = file_path

                    docs.extend(loaded_docs)

        return docs