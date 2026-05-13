# Local RAG Agent

A privacy-focused Retrieval Augmented Generation (RAG) system that runs entirely on your local machine using LM Studio for LLM inference and embeddings.

## Features

- **Local-only**: No data leaves your machine
- **Document ingestion**: Supports PDF, TXT, and Markdown files
- **Vector storage**: Chroma vector database for semantic search
- **FastAPI API**: Simple REST API for querying documents
- **Configurable**: Easy to swap LLM and embedding models

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

Copy `.env.sample` to `.env` and configure:

```env
# LM Studio API endpoint
LM_STUDIO_BASE_URL="http://localhost:1234/v1"

# Directory containing your documents
KNOWLEDGE_DIR="./knowledge"

# Vector database directory
DB_DIR="./vector_db"
```

## Usage

### 1. Add Documents

Place your documents in the `knowledge/` directory. Supported formats:
- `.pdf` - PDF files
- `.txt` - Plain text
- `.md` - Markdown files

### 2. Ingest Documents

```bash
python ingest.py
```

This will:
- Load all documents from the knowledge directory
- Split them into chunks
- Generate embeddings using LM Studio
- Store them in the vector database

### 3. Start the API Server

```bash
python server.py
```

The server runs on `http://localhost:8100`.

### 4. Query the RAG Agent

```bash
curl -X POST http://localhost:8100/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Your question here"}'
```

Response:
```json
{
  "answer": "The generated answer...",
  "sources": ["source1.md", "source2.pdf"]
}
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ask` | POST | Query the RAG system |
| `/docs` | GET | Interactive API documentation |

## Project Structure

```
local-rag-agent/
├── ingest.py          # Document ingestion script
├── server.py          # FastAPI server
├── requirements.txt   # Python dependencies
├── knowledge/         # Source documents
├── vector_db/        # Chroma vector database
└── .env              # Configuration
```

## Troubleshooting

**Connection refused**: Ensure LM Studio is running and you have loaded both an embedding model and an LLM.

**No documents found**: Add files to the `knowledge/` directory before running `ingest.py`.

**Model not found**: Verify the model name in `.env` matches what's loaded in LM Studio.