import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config

from core.factories.provider_factory import (
    create_embedding_provider,
    create_vector_store_provider,
)

from ingestion import (
    DocumentLoaderService,
    RecursiveChunker,
    IngestionPipeline,
)


def on_progress(message: str, progress: int):
    bar_width = 30
    filled = int(bar_width * progress / 100)
    bar = "█" * filled + "░" * (bar_width - filled)
    sys.stdout.write(f"\r[{bar}] {progress}% {message}")
    sys.stdout.flush()
    if progress >= 100:
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Local RAG Agent - Ingestion",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Force full re-ingestion of all files (ignore manifest)",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Specific file(s) to ingest (relative to KNOWLEDGE_DIR)",
    )

    args = parser.parse_args()

    print("🚀 Local RAG Agent - Ingestion")
    print("=" * 40)

    document_loader = DocumentLoaderService(
        knowledge_dir=config.knowledge_dir
    )

    chunker = RecursiveChunker(
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
    )

    embedding_provider = create_embedding_provider()
    vector_store_provider = create_vector_store_provider()

    pipeline = IngestionPipeline(
        document_loader=document_loader,
        chunker=chunker,
        embedding_provider=embedding_provider,
        vector_store_provider=vector_store_provider,
        on_progress=on_progress,
    )

    if args.all:
        print("⚡ Full re-ingestion mode (ignoring manifest)")
        pipeline.run_all(force=True)
    elif args.files:
        for file_rel in args.files:
            pipeline.run_file(file_rel)
    else:
        print("🔍 Smart ingestion mode (detect changes)")
        pipeline.run()


if __name__ == "__main__":
    main()