import json
import time
import uuid
from typing import AsyncGenerator, List, Optional, Union

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Literal

from config import config
from core.services.rag_pipeline import (
    RagPipeline,
    extract_user_question,
    format_rag_response,
)
from core.factories.provider_factory import (
    create_llm_provider,
    create_vector_store_provider,
)


router = APIRouter(prefix=config.api_prefix, tags=["OpenAI Compatible"])


llm_provider = create_llm_provider()
vector_store_provider = create_vector_store_provider()

pipeline = RagPipeline(
    llm_provider=llm_provider,
    vector_store_provider=vector_store_provider,
    streaming=True,
)


class Message(BaseModel):
    role: Literal["system", "user", "assistant", "function"]
    content: str
    name: Optional[str] = None


class StreamOptions(BaseModel):
    include_usage: Optional[bool] = False


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = None
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    user: Optional[str] = None
    stream_options: Optional[StreamOptions] = None


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = "stop"


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Usage
    system_fingerprint: Optional[str] = None


class StreamChoice(BaseModel):
    index: int
    delta: dict
    finish_reason: Optional[str] = None


class StreamChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[StreamChoice]
    usage: Optional[Usage] = None


class Model(BaseModel):
    id: str
    object: str = "model"
    created: int = 1700000000
    owned_by: str = "local"
    permission: Optional[List[str]] = None
    root: Optional[str] = None


class ModelList(BaseModel):
    object: str = "list"
    data: List[Model]


@router.get("/models", response_model=ModelList)
async def list_models():
    return ModelList(
        data=[
            Model(
                id=config.llm_model,
                owned_by="local",
            ),
        ]
    )


@router.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
):
    request_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
    created = int(time.time())
    model = request.model or config.llm_model

    if request.stream:
        return StreamingResponse(
            stream_response(
                request_id=request_id,
                created=created,
                model=model,
                messages=request.messages,
            ),
            media_type="text/event-stream",
        )

    question = extract_user_question([msg.model_dump() for msg in request.messages])

    answer, sources = pipeline.ask_with_sources(question)

    response_text = answer
    if sources:
        response_text = f"{answer}\n\nSources: {', '.join(sources)}"

    prompt_tokens = pipeline.estimate_tokens(question)
    completion_tokens = pipeline.estimate_tokens(response_text)

    return ChatCompletionResponse(
        id=request_id,
        created=created,
        model=model,
        choices=[
            ChatCompletionChoice(
                index=0,
                message=ChatMessage(
                    role="assistant",
                    content=response_text,
                ),
                finish_reason="stop",
            )
        ],
        usage=Usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
    )


async def stream_response(
    request_id: str,
    created: int,
    model: str,
    messages: List[Message],
) -> AsyncGenerator[str, None]:
    try:
        yield f"data: {json.dumps({'id': request_id, 'object': 'chat.completion.chunk', 'created': created, 'model': model, 'choices': [{'index': 0, 'delta': {'role': 'assistant'}, 'finish_reason': None}]})}\n\n"

        question = extract_user_question([msg.model_dump() for msg in messages])

        docs = pipeline.retriever.invoke(question)
        sources = list(set(doc.metadata.get("source", "Unknown") for doc in docs))

        combine_inputs = {
            "input": question,
            "context": docs,
        }

        full_content = ""
        buffer = ""

        for chunk in pipeline.combine_docs_chain.stream(combine_inputs):
            if chunk:
                if hasattr(chunk, 'content'):
                    chunk_str = chunk.content
                else:
                    chunk_str = str(chunk)

                full_content += chunk_str
                yield f"data: {json.dumps({'id': request_id, 'object': 'chat.completion.chunk', 'created': created, 'model': model, 'choices': [{'index': 0, 'delta': {'content': chunk_str}, 'finish_reason': None}]})}\n\n"

        if sources:
            sources_line = f"\n\n**Sources:** {', '.join(sources)}"
            full_content += sources_line
            yield f"data: {json.dumps({'id': request_id, 'object': 'chat.completion.chunk', 'created': created, 'model': model, 'choices': [{'index': 0, 'delta': {'content': sources_line}, 'finish_reason': None}]})}\n\n"

        completion_tokens = pipeline.estimate_tokens(full_content)
        yield f"data: {json.dumps({'id': request_id, 'object': 'chat.completion.chunk', 'created': created, 'model': model, 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}], 'usage': {'prompt_tokens': 0, 'completion_tokens': completion_tokens, 'total_tokens': completion_tokens}})}\n\n"
        yield "data: [DONE]\n\n"

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        yield f"data: {json.dumps({'id': request_id, 'object': 'chat.completion.chunk', 'created': created, 'model': model, 'choices': [{'index': 0, 'delta': {'content': error_msg}, 'finish_reason': 'stop'}]})}\n\n"
        yield "data: [DONE]\n\n"