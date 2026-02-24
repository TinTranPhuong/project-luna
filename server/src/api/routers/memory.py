from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
from datetime import datetime
import shutil
import os

from server.src.core.rag.ingest import process_and_save
from server.src.core.rag.retrieve import retriever
from server.src.core.rag.store import store
from server.src.utils.scraper import scrape_url

router = APIRouter()

# ==============================================================================
# SCHEMAS
# ==============================================================================
class IngestRequest(BaseModel):
    url: str
    text: str 

class QueryRequest(BaseModel):
    query: str

class SearchResult(BaseModel):
    id: str
    text: str
    score: float
    source: str
    tier: str

class MemoryItem(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any]
    
# ==============================================================================
# DATA INGESTION & RETRIEVAL ENDPOINTS
# ==============================================================================

@router.post("/ingest")
async def ingest_content(request: IngestRequest):
    """
    Processes and stores external content into the Working Memory tier.
    Automatically triggers a web scraper if a URL is provided without raw text.
    """
    try:
        content_to_save = request.text
        
        # --- AUTOPILOT SCRAPING ---
        if not content_to_save and request.url:
            print(f"No text provided. Auto-scraping URL: {request.url}")
            scraped_text = scrape_url(request.url)
            
            if not scraped_text:
                raise HTTPException(status_code=400, detail="Could not scrape content from URL.")
            
            content_to_save = scraped_text
            print(f"Scraped {len(content_to_save)} characters.")

        chunk_count = process_and_save(content_to_save, request.url)
        
        return {
            "status": "success",
            "message": f"Successfully memorized {chunk_count} chunks from {request.url}",
            "chunks": chunk_count
        }
    except Exception as e:
        print(f"Ingest Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=List[SearchResult])
async def query_memory(request: QueryRequest):
    """
    Executes a multi-tier vector search across the knowledge base.
    Results are automatically re-ranked using FlashRank for higher accuracy.
    """
    try:
        results = retriever.search(request.query)
        
        formatted_results = []
        for res in results:
            formatted_results.append(SearchResult(
                id=res["id"],
                text=res["text"],
                score=res["score"], 
                source=res["meta"].get("source", "unknown"),
                tier=res["meta"].get("tier", "unknown")
            ))
            
        return formatted_results

    except Exception as e:
        print(f"Search Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================================================================
# MEMORY MANAGEMENT & MAINTENANCE ENDPOINTS
# ==============================================================================

@router.get("/all", response_model=List[MemoryItem])
async def view_all_memories(limit: int = 100):
    """Retrieves a paginated, global view of all stored memory chunks."""
    try:
        memories = []

        def fetch_from_collection(collection_obj, tier_name):
            if not collection_obj: return []
            
            results = collection_obj.get(limit=limit)
            
            items = []
            ids = results["ids"]
            documents = results["documents"]
            metadatas = results["metadatas"]

            if ids:
                for i in range(len(ids)):
                    meta = metadatas[i] or {}
                    meta["source_tier"] = tier_name 
                    
                    items.append({
                        "id": ids[i],
                        "text": documents[i],
                        "metadata": meta
                    })
            return items

        if hasattr(store, "working_memory"):
            print("Scanning Working Memory...")
            memories.extend(fetch_from_collection(store.working_memory, "Working Memory"))

        if hasattr(store, "core_memory"):
            print("Scanning Core Memory...")
            memories.extend(fetch_from_collection(store.core_memory, "Core Memory"))
            
        return memories

    except Exception as e:
        print(f"Error fetching memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/source")
async def delete_source_memory(source: str):
    """Purges all memory chunks associated with a specific origin URL or tag."""
    try:
        print(f"Deleting all memories from source: {source}")
        
        if hasattr(store, "working_memory"):
            store.working_memory.delete(where={"source": source})

        if hasattr(store, "core_memory"):
            store.core_memory.delete(where={"source": source})
            
        return {"status": "success", "message": f"Deleted all memories from {source}"}
    except Exception as e:
        print(f"Delete Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/wipe")
async def wipe_memory():
    """Nuclear option: Drops all internal collections."""
    try:
        store.working_memory.delete()
        store.core_memory.delete()
        return {"status": "success", "message": "Memory Wiped."}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    
from server.src.config.settings import CACHE_PATH 

@router.delete("/cache")
async def clear_cache():
    """
    Clears the short-term document cache.
    Implements file-locking safeguards specifically for Windows environments.
    """
    try:
        # STRATEGY 1: Internal Object Clearance
        if hasattr(retriever, "cache"):
            retriever.cache.clear()
            print("Cache Wiped via Internal Object.")
            return {"status": "success", "message": "Short-term memory cleared."}
            
        # STRATEGY 2: Hard File System Deletion
        from server.src.config.settings import CACHE_PATH
        if os.path.exists(CACHE_PATH):
            shutil.rmtree(CACHE_PATH)
            os.makedirs(CACHE_PATH, exist_ok=True)
            return {"status": "success", "message": "Cache folder deleted."}
            
        return {"status": "success", "message": "Cache was already empty."}

    except OSError as e:
        if e.winerror == 32:
            print("Cache file is locked by Windows. Suggest server restart.")
            return {"status": "error", "message": "Cache is locked by Windows. Please restart the server console to force clear."}
        print(f"Cache Wipe Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"Cache Wipe Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))