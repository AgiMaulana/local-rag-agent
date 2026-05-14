import json

from langchain_classic.chains import (
    create_retrieval_chain,
)

from langchain_classic.chains.combine_documents import (
    create_stuff_documents_chain,
)

from langchain_core.prompts import (
    ChatPromptTemplate,
)

SYSTEM_PROMPT = (
    "SYSTEM RULE: You are a local "
    "documentation search engine. "
    "You are ONLY allowed to use "
    "the provided Context to answer. "
    "If the answer is not explicitly "
    "written in the Context, "
    "you MUST say: "
    "'Information not found "
    "in local documents.'\n\n"

    "CRITICAL: Do not provide "
    "general knowledge, code, "
    "or advice unless it is "
    "directly extracted from "
    "the Context below.\n\n"

    "Context:\n{context}"
)

class RagPipeline:

    def __init__(
        self,
        llm_provider,
        vector_store_provider,
        streaming: bool = False,
    ):

        self.llm = (
            llm_provider.get_client()
        )

        self.streaming = streaming

        self.retriever = (
            vector_store_provider
            .as_retriever()
        )

        prompt = (
            ChatPromptTemplate
            .from_messages(
                [
                    (
                        "system",
                        SYSTEM_PROMPT,
                    ),
                    (
                        "human",
                        "{input}",
                    ),
                ]
            )
        )

        self.combine_docs_chain = (
            create_stuff_documents_chain(
                self.llm,
                prompt,
            )
        )

        self.chain = (
            create_retrieval_chain(
                self.retriever,
                self.combine_docs_chain,
            )
        )

    def ask(
        self,
        question: str,
    ):

        response = self.chain.invoke(
            {
                "input": question
            }
        )

        sources = [
            doc.metadata.get(
                "source",
                "Unknown",
            )
            for doc in response["context"]
        ]

        return {
            "answer": response["answer"],
            "sources": list(set(sources)),
        }

    def ask_stream(
        self,
        question: str,
    ):
        docs = self.retriever.invoke(question)

        sources = [
            doc.metadata.get("source", "Unknown")
            for doc in docs
        ]
        unique_sources = list(set(sources))

        yield f"data: {json.dumps({'type': 'sources', 'sources': unique_sources})}\n\n"

        combine_inputs = {
            "input": question,
            "context": docs,
        }

        for chunk in self.combine_docs_chain.stream(
            combine_inputs
        ):
            if chunk:
                chunk_str = chunk.content if hasattr(chunk, 'content') else str(chunk)
                yield f"data: {json.dumps({'type': 'content', 'delta': chunk_str})}\n\n"

        yield "data: {\"type\": \"done\"}\n\n"