from dataclasses import dataclass

@dataclass
class RetrievedDocument:
    id: str
    content: str
    source: str
    score: float