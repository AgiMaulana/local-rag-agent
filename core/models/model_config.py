from dataclasses import dataclass

@dataclass
class ModelConfig:
    model: str
    temperature: float = 0.0
    max_tokens: int = 1024