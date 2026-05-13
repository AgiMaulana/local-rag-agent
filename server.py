import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

app = FastAPI(title="Local RAG Agent API")

# 1. Setup Embeddings (Pointing to LM Studio Nomic)
embeddings = OpenAIEmbeddings(
    openai_api_base=os.getenv("LM_STUDIO_BASE_URL"),
    openai_api_key="lm-studio",
    model="text-embedding-nomic-embed-text-v1.5", # Critical: matches lms load
    check_embedding_ctx_length=False
)

# 2. Load the existing Vector DB
vectorstore = Chroma(
    persist_directory="./vector_db",
    embedding_function=embeddings
)

# 3. Setup LLM (Pointing to LM Studio Gemma 4)
llm = ChatOpenAI(
    openai_api_base=os.getenv("LM_STUDIO_BASE_URL"),
    openai_api_key="lm-studio",
    model="google/gemma-4-e4b", # Critical: matches lms load
    streaming=False
)

# 4. Define the RAG Prompt
system_prompt = (
    "SYSTEM RULE: You are a local documentation search engine. "
    "You are ONLY allowed to use the provided Context to answer. "
    "If the answer is not explicitly written in the Context, "
    "you MUST say: 'Information not found in local documents.'\n\n"
    "CRITICAL: Do not provide general knowledge, code, or advice "
    "unless it is directly extracted from the Context below.\n\n"
    "Context:\n{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

# 5. Create the Retrieval Chain (using langchain-classic logic)
combine_docs_chain = create_stuff_documents_chain(llm, prompt)
retriever = vectorstore.as_retriever()
rag_chain = create_retrieval_chain(retriever, combine_docs_chain)

# API Models
class Query(BaseModel):
    question: str

@app.post("/ask")
async def ask(query: Query):
    try:
        # The chain invoke returns a dict with 'answer' and 'context'
        response = rag_chain.invoke({"input": query.question})
        
        # Extract sources from the metadata
        sources = [doc.metadata.get("source", "Unknown") for doc in response["context"]]
        
        return {
            "answer": response["answer"],
            "sources": list(set(sources)) # Unique sources only
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)