from typing import Protocol

class LlmProvider(Protocol):

    def get_client(self):
        """Returns the underlying LLM client instance."""
        pass