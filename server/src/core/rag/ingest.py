import hashlib
from datetime import datetime
from server.src.core.rag.store import store
from server.src.core.rag.embedder import embedder

# ==============================================================================
# DOCUMENT PROCESSING & INGESTION
# ==============================================================================

def recursive_split(text: str, chunk_size=500, overlap=50):
    """
    Splits a large text block into smaller, overlapping chunks 
    to preserve contextual boundaries during vector search.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def generate_id(url: str, index: int) -> str:
    """
    Generates a deterministic, repeatable ID based on the source URL and chunk index.
    Prevents duplicate entries if the same page is ingested multiple times.
    """
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return f"{url_hash}_{index}"

def process_and_save(text: str, url: str):
    """
    Main ingestion pipeline: chunks raw text, generates CPU embeddings, 
    and commits the data to the Working Memory database tier.
    """
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
    
    # --- GENERATE EMBEDDINGS & STORE ---
    embeddings = embedder.embed_documents(chunks)
    store.save_to_working(chunks, metadatas, ids)
    
    return len(chunks)