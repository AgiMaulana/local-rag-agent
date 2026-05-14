from core.models.retrieved_document import RetrievedDocument

class PromptService:

    def build_prompt(
        self,
        question: str,
        documents: list[RetrievedDocument],
    ) -> str:

        context = "\n\n".join([
            f"""
                Source: {doc.source}

                Content:
                {doc.content}
                """
                            for doc in documents
                        ])

                        return f"""
                You are an internal employee support assistant.

                Only answer using the provided context.

                If the answer does not exist in the context,
                say you could not find the information.

                Context:
                {context}

                Question:
                {question}
            """