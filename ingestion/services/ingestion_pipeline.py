from typing import List, Optional, Callable
import os

from config import config
from ingestion.manifest import IngestManifest


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
        self.manifest = IngestManifest()

    def _notify(self, message: str, progress: int = 0):
        print(message)
        if self.on_progress:
            self.on_progress(message, progress)

    def _ingest_documents(self, docs):
        if not docs:
            return 0

        chunks = self.chunker.split(docs)
        self._notify(f"  Created {len(chunks)} chunks", 0)

        embeddings = self.embedding_provider.get_client()
        self.vector_store_provider.from_documents(
            documents=chunks,
            embedding=embeddings,
        )

        return len(chunks)

    def run(self):
        new_count = 0
        changed_count = 0
        unchanged_count = 0
        error_count = 0

        docs_to_ingest = []

        for root, _, files in self._walk_knowledge():
            for file in files:
                file_abs = self._abs_path(root, file)
                file_rel = self._rel_path(file_abs)

                if not self._is_supported(file):
                    continue

                try:
                    if self.manifest.is_ingested(file_rel):
                        if self.manifest.is_changed(file_abs, file_rel):
                            self._notify(f"🔄 Changed: {file_rel}")
                            changed_count += 1
                            self.vector_store_provider.delete_by_source(file_abs)
                        else:
                            self._notify(f"✅ Unchanged: {file_rel}")
                            unchanged_count += 1
                            continue
                    else:
                        self._notify(f"🆕 New: {file_rel}")
                        new_count += 1

                    docs = self.document_loader.load_file(file_abs)
                    if docs:
                        for doc in docs:
                            doc.metadata["source"] = file_abs
                        docs_to_ingest.extend(docs)
                    else:
                        error_count += 1

                except Exception as e:
                    self._notify(f"⚠️ Error processing {file_rel}: {e}")
                    error_count += 1

        total_chunks = self._ingest_documents(docs_to_ingest)

        for doc in docs_to_ingest:
            file_rel = self._rel_path(doc.metadata.get("source", ""))
            self.manifest.mark_ingested(
                doc.metadata.get("source", ""),
                file_rel,
            )

        self._notify(
            f"✅ Ingestion completed — "
            f"{new_count} new, {changed_count} changed, "
            f"{unchanged_count} unchanged, {error_count} errors — "
            f"{total_chunks} chunks",
            100,
        )

    def run_file(self, file_rel_path: str):
        file_abs = os.path.join(config.knowledge_dir, file_rel_path)
        file_abs = os.path.abspath(file_abs)

        if not os.path.exists(file_abs):
            print(f"❌ File not found: {file_rel_path}")
            return

        if not self._is_supported(file_rel_path):
            print(f"❌ Unsupported file type: {file_rel_path}")
            return

        self._notify(f"📄 Loading {file_rel_path}...", 0)
        docs = self.document_loader.load_file(file_abs)

        if not docs:
            print(f"❌ Failed to load {file_rel_path}")
            return

        for doc in docs:
            doc.metadata["source"] = file_abs

        chunks = self.chunker.split(docs)
        self._notify(f"  Created {len(chunks)} chunks", 50)

        embeddings = self.embedding_provider.get_client()
        self.vector_store_provider.from_documents(
            documents=chunks,
            embedding=embeddings,
        )

        for doc in docs:
            self.manifest.mark_ingested(
                doc.metadata.get("source", ""),
                file_rel_path,
            )

        self._notify(f"✅ Ingested {file_rel_path} — {len(chunks)} chunks", 100)

    def run_all(self, force: bool = False):
        new_count = 0
        error_count = 0
        docs_to_ingest = []

        for root, _, files in self._walk_knowledge():
            for file in files:
                file_abs = self._abs_path(root, file)
                file_rel = self._rel_path(file_abs)

                if not self._is_supported(file):
                    continue

                try:
                    self._notify(f"📄 Loading {file_rel}")
                    docs = self.document_loader.load_file(file_abs)

                    if docs:
                        for doc in docs:
                            doc.metadata["source"] = file_abs
                        docs_to_ingest.extend(docs)
                        new_count += 1
                    else:
                        error_count += 1

                except Exception as e:
                    self._notify(f"⚠️ Error processing {file_rel}: {e}")
                    error_count += 1

        total_chunks = self._ingest_documents(docs_to_ingest)

        for doc in docs_to_ingest:
            file_abs = doc.metadata.get("source", "")
            file_rel = self._rel_path(file_abs)
            self.manifest.mark_ingested(file_abs, file_rel)

        self._notify(
            f"✅ Full ingestion completed — "
            f"{new_count} files processed, "
            f"{error_count} errors — "
            f"{total_chunks} chunks",
            100,
        )

    def _walk_knowledge(self):
        return os.walk(config.knowledge_dir)

    def _abs_path(self, root: str, file: str) -> str:
        return os.path.join(root, file)

    def _rel_path(self, abs_path: str) -> str:
        import os
        abs_path = os.path.abspath(abs_path)
        knowledge_dir = os.path.abspath(config.knowledge_dir)
        rel = os.path.relpath(abs_path, knowledge_dir)
        return rel.replace("\\", "/")

    def _is_supported(self, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        return ext in {
            ".pdf", ".txt", ".md", ".csv",
            ".doc", ".docx", ".ppt", ".pptx",
            ".xls", ".xlsx", ".epub", ".json",
        }


if __name__ == "__main__":
    pass