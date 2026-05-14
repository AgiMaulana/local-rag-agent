import os
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv

load_dotenv()


@dataclass
class AppConfig:
    lm_studio_base_url: str
    llm_model: str
    embedding_model: str
    vector_db_dir: str
    knowledge_dir: str
    api_key: str = "lm-studio"
    chunk_size: int = 1000
    chunk_overlap: int = 150
    llm_streaming: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    api_prefix: str = "/v1"


config = AppConfig(
    lm_studio_base_url=os.getenv("LM_STUDIO_BASE_URL"),
    llm_model="google/gemma-4-e4b",
    embedding_model="text-embedding-nomic-embed-text-v1.5",
    vector_db_dir=os.getenv("DB_DIR"),
    knowledge_dir=os.getenv("KNOWLEDGE_DIR"),
    api_key=os.getenv("OPENAI_API_KEY", "lm-studio"),
    cors_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    api_prefix=os.getenv("API_PREFIX", "/v1"),
)