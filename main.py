from fastapi import FastAPI

from api.routes.ask import router

app = FastAPI(
    title="Local RAG Agent API"
)

app.include_router(router)

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8100,
    )