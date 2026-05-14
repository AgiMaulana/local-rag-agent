from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from config import config

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

llm_provider = create_llm_provider()
vector_store_provider = create_vector_store_provider()

pipeline = RagPipeline(
    llm_provider=llm_provider,
    vector_store_provider=vector_store_provider,
    streaming=config.llm_streaming,
)


@router.post("/ask")
async def ask(
    query: Query,
):
    if pipeline.streaming:
        return StreamingResponse(
            pipeline.ask_stream(query.question),
            media_type="text/event-stream",
        )

    return pipeline.ask(query.question)