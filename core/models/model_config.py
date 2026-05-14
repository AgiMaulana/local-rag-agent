from dataclasses import dataclass


@dataclass
class ModelConfig:
    model: str
    api_key: str
    base_url: str
    temperature: float = 0.0
    max_tokens: int = 1024
    streaming: bool = False