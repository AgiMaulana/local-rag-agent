import json
from typing import Any, List

from langchain_core.documents import Document


class JsonLoaderService:

    def __init__(self, knowledge_dir: str):
        self.knowledge_dir = knowledge_dir

    def load(self, file_path: str) -> List[Document]:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            docs = []
            for i, item in enumerate(data):
                content = json.dumps(item, indent=2)
                docs.append(
                    Document(
                        page_content=content,
                        metadata={
                            "source": file_path,
                            "index": i,
                        },
                    )
                )
            return docs
        else:
            return [
                Document(
                    page_content=json.dumps(data, indent=2),
                    metadata={"source": file_path},
                )
            ]