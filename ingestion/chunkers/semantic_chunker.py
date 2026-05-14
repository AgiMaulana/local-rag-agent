try:
    from langchain_experimental.text_splitter import (
        SemanticChunker as LangchainSemanticChunker,
    )
    from langchain_openai import OpenAIEmbeddings


    class SemanticChunker:

        def __init__(
            self,
            breakpoint_threshold_amount: float = 0.5,
            embedding_model: str = "text-embedding-nomic-embed-text-v1.5",
            base_url: str = None,
        ):

            embeddings = OpenAIEmbeddings(
                model=embedding_model,
                openai_api_base=base_url,
                openai_api_key="lm-studio",
            )

            self.splitter = LangchainSemanticChunker(
                embeddings=embeddings,
                breakpoint_threshold_amount=breakpoint_threshold_amount,
            )

        def split(self, documents):
            return self.splitter.split_documents(documents)

except ImportError:
    # Fallback - use recursive chunker as substitute
    from ingestion.chunkers.recursive_chunker import RecursiveChunker as SemanticChunker