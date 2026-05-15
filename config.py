import os
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _require_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"Required env var '{var_name}' is not set")
    return value


@dataclass
class AppConfig:
    llm_base_url: str
    llm_model: str
    llm_api_key: str
    embedding_base_url: str
    embedding_model: str
    embedding_api_key: str
    vector_db_dir: str
    knowledge_dir: str
    chunk_size: int = 1000
    chunk_overlap: int = 150
    llm_streaming: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    api_prefix: str = "/v1"

    def __post_init__(self):
        if not self.llm_base_url:
            raise ValueError("llm_base_url is required")
        if not self.embedding_base_url:
            raise ValueError("embedding_base_url is required")


config = AppConfig(
    llm_base_url=_require_env("LLM_BASE_URL"),
    llm_model=_require_env("LLM_MODEL"),
    llm_api_key=_require_env("LLM_API_KEY"),
    embedding_base_url=_require_env("EMBEDDING_BASE_URL"),
    embedding_model=_require_env("EMBEDDING_MODEL"),
    embedding_api_key=_require_env("OPENAI_API_KEY"),
    vector_db_dir=_require_env("DB_DIR"),
    knowledge_dir=_require_env("KNOWLEDGE_DIR"),
    cors_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    api_prefix=os.getenv("API_PREFIX", "/v1"),
)