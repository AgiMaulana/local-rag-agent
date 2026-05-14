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

SYSTEM_PROMPT = """You are a helpful local documentation assistant.
    <STRICT RULES>
        - ONLY use the provided Context to answer the question.
        - If the answer is not in the Context, say exactly: "Information not found in local documents."
        - Do not add any external knowledge.
    </STRICT RULES>

    <context>
        {context}
    </context>

    Question: {input}

    Respond in valid JSON format only. Use this exact structure and do not add any extra text:

    {{
        "thinking": "Brief and concise step-by-step reasoning using only the context",
        "answer": "Clear, well-formatted final answer to the user"
    }}
    """

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

    def _event(self, event_type: str, **data):
        return f"data: {json.dumps({'type': event_type, **data})}\n\n"

    def ask_stream(
        self,
        question: str,
    ):
        try:
            yield self._event("status", message="🔍 Searching relevant documents...")

            docs = self.retriever.invoke(question)

            sources = [
                doc.metadata.get("source", "Unknown")
                for doc in docs
            ]
            unique_sources = list(set(sources))

            yield f"data: {json.dumps({'type': 'sources', 'sources': unique_sources})}\n\n"
            yield self._event("status", message=f"📚 Found {len(docs)} relevant documents")

            yield self._event("status", message="🤔 Analyzing context and thinking...")

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

            yield self._event("done", message="Done")

        except Exception as e:
            yield self._event("error", message=str(e))