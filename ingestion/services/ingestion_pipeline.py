from typing import Callable, Optional


class IngestionPipeline:

    def __init__(
        self,
        document_loader,
        chunker,
        embedding_provider,
        vector_store_provider,
        on_progress: Optional[Callable[[str, int], None]] = None,
    ):

        self.document_loader = document_loader
        self.chunker = chunker
        self.embedding_provider = embedding_provider
        self.vector_store_provider = vector_store_provider
        self.on_progress = on_progress

    def _notify(self, message: str, progress: int = 0):
        print(message)
        if self.on_progress:
            self.on_progress(message, progress)

    def run(self):

        self._notify("🚀 Starting ingestion...", 0)

        docs = self.document_loader.load_documents()
        self._notify(
            f"📄 Loaded {len(docs)} documents",
            10
        )

        if len(docs) == 0:
            self._notify("🛑 No documents found", 0)
            return

        chunks = self.chunker.split(docs)
        self._notify(
            f"✂️ Created {len(chunks)} chunks",
            30
        )

        embeddings = self.embedding_provider.get_client()
        self._notify(
            "🧠 Generating embeddings and saving to vector store...",
            50
        )

        self.vector_store_provider.from_documents(
            documents=chunks,
            embedding=embeddings,
        )

        self._notify(
            "✅ Ingestion completed",
            100
        )