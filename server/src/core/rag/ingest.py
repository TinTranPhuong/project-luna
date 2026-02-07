import hashlib
from datetime import datetime
from server.src.core.rag.store import store
from server.src.core.rag.embedder import embedder

def recursive_split(text: str, chunk_size=500, overlap=50):
    # Splits text into smaller chunks with overlap
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def generate_id(url: str, index: int) -> str:
    # Generates a consistent ID based on URL and chunk index
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return f"{url_hash}_{index}"

def process_and_save(text: str, url: str):
    # Main entry point: Cleans, splits, embeds, and saves text
    print(f"Processing: {url}...")
    
    chunks = recursive_split(text)
    
    ids = []
    metadatas = []
    
    for i, chunk in enumerate(chunks):
        chunk_id = generate_id(url, i)
        ids.append(chunk_id)
        metadatas.append({
            "source": url,
            "created_at": str(datetime.now()),
            "tier": "temp",
            "usage_count": 0
        })
    
    # Generate Embeddings on CPU
    embeddings = embedder.embed_documents(chunks)
    
    # Save to Database
    store.save_to_working(chunks, metadatas, ids)
    
    return len(chunks)