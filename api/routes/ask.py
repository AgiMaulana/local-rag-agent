from fastapi import APIRouter
from pydantic import BaseModel

from core.services.rag_pipeline import (
    RagPipeline,
)

from core.factories.provider_factory import (
    create_llm_provider,
    create_vector_store_provider,
)

router = APIRouter()

class Query(BaseModel):
    question: str

pipeline = RagPipeline(
    llm_provider=(
        create_llm_provider()
    ),
    vector_store_provider=(
        create_vector_store_provider()
    ),
)

@router.post("/ask")
async def ask(
    query: Query,
):

    return pipeline.ask(
        query.question
    )