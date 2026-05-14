from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.openai_compatible import router as openai_router

from config import config

app = FastAPI(
    title="Local RAG Agent API",
    description="OpenAI-compatible API for local RAG with HuggingFace chat-ui",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(openai_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8100,
    )