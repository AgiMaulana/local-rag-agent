import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

def run_ingestion():
    print("🚀 Starting Ingestion...")
    
    knowledge_dir = os.getenv("KNOWLEDGE_DIR")
    
    # Define mapping of extensions to loaders
    loaders = {
        ".pdf": PyPDFLoader,
        ".txt": TextLoader,
        ".md": UnstructuredMarkdownLoader,
    }

    docs = []
    
    # Manual walk through the directory to ensure we catch files
    if not os.path.exists(knowledge_dir):
        print(f"❌ Error: Directory '{knowledge_dir}' does not exist.")
        return

    for file in os.listdir(knowledge_dir):
        file_path = os.path.join(knowledge_dir, file)
        ext = os.path.splitext(file)[1].lower()
        
        if ext in loaders:
            try:
                print(f"  📖 Loading {file}...")
                loader = loaders[ext](file_path)
                docs.extend(loader.load())
            except Exception as e:
                print(f"  ⚠️ Failed to load {file}: {e}")

    print(f"📄 Total documents loaded: {len(docs)}")

    if len(docs) == 0:
        print("🛑 No valid documents found. Ingestion aborted.")
        return

    # 2. Chunking
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = text_splitter.split_documents(docs)
    print(f"✂️ Created {len(chunks)} text chunks.")

    # 3. Embedding (Using LM Studio's Nomic-Embed model)
    embeddings = OpenAIEmbeddings(
        openai_api_base=os.getenv("LM_STUDIO_BASE_URL"),
        openai_api_key="lm-studio",
        check_embedding_ctx_length=False,
        model="text-embedding-nomic-embed-text-v1.5"
    )

    # 4. Save to Chroma
    print("🧠 Generating embeddings and saving to disk...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=os.getenv("DB_DIR")
    )
    print(f"✅ Ingestion complete. Data saved to {os.getenv('DB_DIR')}")

if __name__ == "__main__":
    run_ingestion()