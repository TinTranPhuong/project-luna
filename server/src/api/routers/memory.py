from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# Import our new core modules
from server.src.core.rag.ingest import process_and_save
from server.src.core.rag.retrieve import retriever
from server.src.core.rag.store import store

router = APIRouter()

# --- Request Schemas ---
class IngestRequest(BaseModel):
    url: str
    text: str  # The raw text scraped from the website

class QueryRequest(BaseModel):
    query: str

class SearchResult(BaseModel):
    id: str
    text: str
    score: float
    source: str
    tier: str
    tier: str

# --- Endpoints ---

@router.post("/ingest")
async def ingest_content(request: IngestRequest):
    """
    The 'Scan' Endpoint.
    Takes raw text from a website, cleans it, checks for duplicates,
    and saves it to 'Working Memory' (Tier 2).
    """
    try:
        # 1. Pass to the Gatekeeper (ingest.py)
        # It handles Hashing, Deduplication, and Embedding on CPU
        chunk_count = process_and_save(request.text, request.url)
        
        return {
            "status": "success",
            "message": f"Successfully memorized {chunk_count} chunks from {request.url}",
            "chunks": chunk_count
        }
    except Exception as e:
        print(f"❌ Ingest Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=List[SearchResult])
async def query_memory(request: QueryRequest):
    """
    The 'Recall' Endpoint.
    Searches Cache -> Vault -> Scratchpad.
    Reranks results using FlashRank (CPU).
    """
    try:
        # 1. Search using our Split-Brain Retriever
        results = retriever.search(request.query)
        
        # 2. Format for API response
        formatted_results = []
        for res in results:
            formatted_results.append(SearchResult(
                id=res["id"],
                text=res["text"],
                score=res["score"],  # FlashRank Score (0.0 - 1.0)
                source=res["meta"].get("source", "unknown"),
                tier=res["meta"].get("tier", "unknown")
            ))
            
        return formatted_results

    except Exception as e:
        print(f"❌ Search Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/wipe")
async def wipe_memory():
    """Debug Tool: Clears ALL memory."""
    try:
        store.working_memory.delete()
        store.core_memory.delete()
        return {"status": "success", "message": "Memory Wiped."}
    except Exception as e:
        return {"status": "error", "detail": str(e)}