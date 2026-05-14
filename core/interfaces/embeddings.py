from typing import Protocol

class EmbeddingProvider(Protocol):

    def get_client(self):
        """Returns the underlying embedding provider client instance."""
        pass