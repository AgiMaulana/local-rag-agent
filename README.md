# Local RAG Agent

A privacy-focused Retrieval Augmented Generation (RAG) system that runs entirely on your local machine using LM Studio for LLM inference and embeddings. Designed to be compatible with HuggingFace chat-ui via OpenAI-compatible API.

## Features

- **Local-only**: No data leaves your machine
- **Document ingestion**: Supports 12+ file formats including PDF, DOCX, PPTX, XLSX, CSV, EPUB, JSON, and more
- **Vector storage**: Chroma vector database for semantic search
- **OpenAI-compatible API**: Works with HuggingFace chat-ui and any OpenAI-compatible client
- **Streaming support**: Real-time token streaming for responsive UX
- **Configurable**: Easy to swap LLM and embedding models, chunking strategies, and more

## Requirements

- Python 3.12+
- [LM Studio](https://lmstudio.ai/) with:
  - An embedding model loaded (e.g., Nomic Embed Text)
  - An LLM loaded (e.g., Gemma 4)

## Installation

```bash
# Clone the repository
cd local-rag-agent

# Create virtual environment
python -m venv .ve
source .ve/bin/activate  # On Windows: .ve\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Copy `.env.sample` to `.env` and fill in the required values:

```env
# LLM Configuration
LLM_BASE_URL="http://localhost:1234/v1"
LLM_MODEL="google/gemma-4-e4b"
LLM_API_KEY="lm-studio"

# Embedding Configuration
EMBEDDING_BASE_URL="http://localhost:1234/v1"
EMBEDDING_MODEL="text-embedding-nomic-embed-text-v1.5"
OPENAI_API_KEY="lm-studio"

# Directories
KNOWLEDGE_DIR="./knowledge"
DB_DIR="./vector_db"

# Optional Configuration
API_PREFIX="/v1"
CORS_ORIGINS="*"
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
```

### Provider Compatibility

Both `LLM_BASE_URL` and `EMBEDDING_BASE_URL` must point to providers that follow the OpenAI API specification. In the current setup, both can point to the same LM Studio instance. For production, you can configure them to use different providers (e.g., LM Studio for LLM and OpenAI/Cohere for embeddings).

Supported providers include:
- **LM Studio** (local, recommended for development)
- **OpenAI** (cloud)
- **Any OpenAI-compatible API**

## Usage

### 1. Add Documents

Place your documents in the `knowledge/` directory. Supported formats:
- **Documents**: `.pdf`, `.txt`, `.md`, `.doc`, `.docx`, `.epub`
- **Spreadsheets**: `.csv`, `.xls`, `.xlsx`
- **Presentations**: `.ppt`, `.pptx`
- **Data**: `.json`

### 2. Ingest Documents

```bash
python -m ingestion.ingest
```

This will:
- Load all documents from the knowledge directory
- Split them into chunks (configurable size and overlap)
- Generate embeddings using your configured embedding provider
- Store them in the Chroma vector database

### 3. Start the API Server

```bash
python main.py
```

The server runs on `http://localhost:8100` with OpenAI-compatible endpoints.

### 4. Query the RAG Agent

The API is OpenAI-compatible, so you can use any standard client or curl:

```bash
# Non-streaming request
curl -X POST http://localhost:8100/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "google/gemma-4-e4b",
    "messages": [{"role": "user", "content": "Your question here"}],
    "stream": false
  }'
```

```bash
# Streaming request (recommended for better UX)
curl -X POST http://localhost:8100/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "google/gemma-4-e4b",
    "messages": [{"role": "user", "content": "Your question here"}],
    "stream": true
  }'
```

Response (non-streaming):
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1700000000,
  "model": "google/gemma-4-e4b",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The generated answer...\n\nSources: source1.md, source2.pdf"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 320,
    "total_tokens": 470
  }
}
```

### Using with HuggingFace chat-ui

Configure your chat-ui instance to point to this API:
- **Base URL**: `http://localhost:8100/v1`
- **Model**: Match the `LLM_MODEL` from your `.env`
- **API Key**: Use the value from `LLM_API_KEY` (e.g., `lm-studio`)

## API Endpoints

All endpoints are prefixed with `API_PREFIX` from `.env` (defaults to `/v1`).

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/v1/models` | GET | List available models |
| `/v1/chat/completions` | POST | Chat completions (OpenAI-compatible, supports streaming) |

### Request Parameters for `/v1/chat/completions`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Model identifier |
| `messages` | array | Yes | Array of message objects with `role` and `content` |
| `stream` | boolean | No | Enable streaming (default: `false`) |
| `temperature` | number | No | Sampling temperature (default: `0.7`) |
| `top_p` | number | No | Nucleus sampling parameter |
| `max_tokens` | integer | No | Maximum tokens to generate |
| `stop` | string/array | No | Stop sequences |
| `presence_penalty` | number | No | Presence penalty (-2.0 to 2.0) |
| `frequency_penalty` | number | No | Frequency penalty (-2.0 to 2.0) |

## Chunking Strategies

The system supports two chunking strategies for document processing:

### Recursive Chunking (Default)

Splits documents using recursive character-based splitting with configurable chunk size and overlap. This is the default strategy and works well for most document types.

```env
CHUNK_SIZE=1000      # Characters per chunk
CHUNK_OVERLAP=150    # Overlap between chunks
```

### Semantic Chunking (Optional)

Uses embedding similarity to determine optimal chunk boundaries, creating more semantically coherent chunks. Requires `langchain-experimental` package.

To enable semantic chunking, modify the ingestion pipeline to use `SemanticChunker` instead of `RecursiveChunker`.

## Customizing the System Prompt

The system prompt controls how the AI responds to questions. It's located in `core/services/rag_pipeline.py` as the `SYSTEM_PROMPT` constant.

### Prompt Structure

The default prompt includes:
- **STRICT RULES**: Guidelines for the AI (e.g., only use provided context, no hallucination)
- **Context placeholder**: `{context}` where retrieved documents are injected
- **Reasoning format**: `<think></think>` blocks for step-by-step thinking
- **Final answer**: The actual response after reasoning

### HuggingFace Chat-ui Integration

The `<think></think>` block is **required** for HuggingFace chat-ui to display the thinking process. The chat-ui parses this block to show a collapsible reasoning section before the final answer.

### Customization Example

```python
# In core/services/rag_pipeline.py

SYSTEM_PROMPT = """You are a helpful assistant specialized in [your domain].

<STRICT RULES>
- ONLY use the information from the provided Context
- If the answer cannot be found in the Context, respond with: "Information not found in local documents."
- Do not hallucinate or use external knowledge
- [Add your custom rules here]
</STRICT RULES>

<context>
{context}
</context>

Answer the user's question based on the context above. Show your reasoning process before giving the final answer.

Format your response exactly as:

</think>

[Your step-by-step reasoning using only the provided context]
</think>

[Your final answer]"""
```

### Important Notes

- Keep the `{context}` placeholder - it's where retrieved documents are injected
- Keep the `<think></think>` format if using HuggingFace chat-ui
- Modify the STRICT RULES section to adjust AI behavior
- The prompt uses the same format as the default to maintain compatibility with streaming and source extraction

## Project Structure

```
local-rag-agent/
├── main.py                      # FastAPI server entry point
├── config.py                    # Application configuration
├── ingestion/
│   ├── ingest.py                # CLI ingestion script
│   ├── manifest.py              # Tracks processed files
│   ├── checksum.py              # File change detection
│   ├── loaders/
│   │   ├── document_loader.py   # Multi-format document loader
│   │   ├── json_loader.py       # JSON document loader
│   │   └── csv_loader.py        # CSV document loader
│   ├── chunkers/
│   │   ├── recursive_chunker.py # Recursive text chunking
│   │   └── semantic_chunker.py  # Semantic-aware chunking
│   └── services/
│       └── ingestion_pipeline.py # Orchestration pipeline
├── core/
│   ├── interfaces/              # Abstract provider interfaces
│   ├── services/
│   │   ├── rag_pipeline.py      # RAG orchestration
│   │   ├── prompt_service.py    # Prompt management
│   │   └── retrieval_service.py # Document retrieval
│   ├── factories/
│   │   └── provider_factory.py  # Provider instantiation
│   └── models/                  # Data models
├── api/
│   └── routes/
│       └── openai_compatible.py # OpenAI-compatible API routes
├── providers/
│   ├── lmstudio/
│   │   ├── llm.py               # LM Studio LLM provider
│   │   └── embeddings.py        # LM Studio embedding provider
│   └── chroma/
│       └── vector_store.py      # Chroma vector store provider
├── knowledge/                   # Source documents (gitignored)
├── vector_db/                   # Chroma database (gitignored)
├── requirements.txt             # Python dependencies
└── .env                         # Environment configuration
```

## Troubleshooting

**Connection refused**: Ensure LM Studio is running and you have loaded both an embedding model and an LLM.

**No documents found**: Add files to the `knowledge/` directory before running ingestion.

**Model not found**: Verify the model name in `.env` matches what's loaded in LM Studio.

**JSON file fails to load**: Ensure your JSON files contain valid document structures. The JSON loader has specific format requirements.

**Semantic chunking not working**: Install the optional dependency: `pip install langchain-experimental`

**API returns 404**: Check that your `API_PREFIX` in `.env` matches the URL path you're using (default is `/v1`).