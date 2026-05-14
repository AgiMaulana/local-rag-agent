import json
from typing import List, Optional

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.documents import Document

from langchain_classic.chains import (
    create_retrieval_chain,
)

from langchain_classic.chains.combine_documents import (
    create_stuff_documents_chain,
)

from langchain_core.prompts import (
    ChatPromptTemplate,
)

SYSTEM_PROMPT = """You are a helpful, concise, and accurate local documentation assistant.

<STRICT RULES>
- ONLY use the information from the provided Context to answer.
- If the answer cannot be found in the Context, respond with: "Information not found in local documents."
- Do not hallucinate or use external knowledge.
- Be clear, professional, and well-formatted.
- Use markdown when helpful (bold, lists, code blocks, etc.).
</STRICT RULES>

<context>
{context}
</context>

Answer the user's question based on the context above. Show your reasoning process before giving the final answer.

Format your response exactly as:

<think>
[Your step-by-step reasoning using only the provided context]
</think>

[Your final answer]"""


class RagPipeline:

    def __init__(
        self,
        llm_provider,
        vector_store_provider,
        streaming: bool = False,
    ):
        self.llm = llm_provider.get_client()
        self.streaming = streaming

        self.retriever = vector_store_provider.as_retriever()

        prompt = (
            ChatPromptTemplate
            .from_messages(
                [
                    ("system", SYSTEM_PROMPT),
                    ("human", "{input}"),
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

    def ask(self, question: str) -> dict:
        response = self.chain.invoke({"input": question})

        sources = [
            doc.metadata.get("source", "Unknown")
            for doc in response["context"]
        ]

        return {
            "answer": response["answer"],
            "sources": list(set(sources)),
        }

    def ask_with_sources(self, question: str) -> tuple[str, List[str]]:
        response = self.chain.invoke({"input": question})

        sources = [
            doc.metadata.get("source", "Unknown")
            for doc in response["context"]
        ]

        answer = response["answer"]

        if '{"thinking"' in answer or '"answer"' in answer:
            try:
                data = json.loads(answer)
                answer = data.get("answer", answer)
            except json.JSONDecodeError:
                pass

        return answer, list(set(sources))

    def ask_stream(self, question: str):
        try:
            docs = self.retriever.invoke(question)
            sources = list(set(doc.metadata.get("source", "Unknown") for doc in docs))

            combine_inputs = {
                "input": question,
                "context": docs,
            }

            full_content = ""
            for chunk in self.combine_docs_chain.stream(combine_inputs):
                if chunk:
                    chunk_str = chunk.content if hasattr(chunk, 'content') else str(chunk)
                    full_content += chunk_str
                    yield chunk_str, sources

        except Exception as e:
            yield f"Error: {str(e)}", []

    def stream(self, question: str):
        for content, sources in self.ask_stream(question):
            yield content

    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4


def convert_openai_messages(messages: List[dict]) -> tuple[str, List[Document]]:
    system_prompt = ""
    user_question = ""

    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")

        if role == "system":
            system_prompt += content + "\n"
        elif role == "user":
            user_question = content
        elif role == "assistant":
            pass

    return user_question or system_prompt


def extract_user_question(messages: List[dict]) -> str:
    for msg in reversed(messages):
        if msg.get("role") == "user":
            return msg.get("content", "")
    return ""


def format_rag_response(response: dict) -> str:
    if isinstance(response, dict):
        answer = response.get("answer", str(response))
    else:
        answer = str(response)

    thinking = response.get("thinking") if isinstance(response, dict) else None
    if thinking:
        return f"{answer}"

    sources = response.get("sources", []) if isinstance(response, dict) else []
    if sources:
        return f"{answer}"

    return answer