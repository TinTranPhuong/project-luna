from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
from datetime import datetime
import shutil
import os

# Import our new core modules
from server.src.core.rag.ingest import process_and_save
from server.src.core.rag.retrieve import retriever
from server.src.core.rag.store import store
from server.src.utils.scraper import scrape_url

router = APIRouter()

# --- Request Schemas ---
class IngestRequest(BaseModel):
    url: str
    text: str  # The raw text scraped from the website (or empty string)

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
    
# --- Endpoints ---

@router.post("/ingest")
async def ingest_content(request: IngestRequest):
    """
    The 'Scan' Endpoint.
    Takes raw text from a website, cleans it, checks for duplicates,
    and saves it to 'Working Memory' (Tier 2).
    """
    try:
        # --- NEW: AUTOPILOT LOGIC START ---
        # If the user sent a URL but NO text (like from the Menu), we scrape it here.
        content_to_save = request.text
        
        if not content_to_save and request.url:
            print(f"No text provided. Auto-scraping URL: {request.url}")
            scraped_text = scrape_url(request.url)
            
            if not scraped_text:
                raise HTTPException(status_code=400, detail="Could not scrape content from URL.")
            
            content_to_save = scraped_text
            print(f"Scraped {len(content_to_save)} characters.")
        # --- NEW: AUTOPILOT LOGIC END ---

        # 1. Pass to the Gatekeeper (ingest.py)
        # Note: We pass 'content_to_save' instead of 'request.text'
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
        print(f"Search Error: {e}")
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
    
from server.src.config.settings import CACHE_PATH 

@router.delete("/cache")
async def clear_cache():
    """
    Forces a 'Brain Flush'. 
    Uses the internal cache object to clear data safely on Windows.
    """
    try:
        # METHOD 1: The Polite Way (Ask the object to clear itself)
        # This works even if the file is locked, because the owner is doing it.
        if hasattr(retriever, "cache"):
            retriever.cache.clear()
            print("Cache Wiped via Internal Object.")
            return {"status": "success", "message": "Short-term memory cleared."}
            
        # METHOD 2: The Fallback (Only works if not locked)
        # We assume this is only needed if Method 1 failed or didn't exist
        from server.src.config.settings import CACHE_PATH
        if os.path.exists(CACHE_PATH):
            shutil.rmtree(CACHE_PATH)
            os.makedirs(CACHE_PATH, exist_ok=True)
            return {"status": "success", "message": "Cache folder deleted."}
            
        return {"status": "success", "message": "Cache was already empty."}

    except OSError as e:
        if e.winerror == 32:
            # If we STILL get locked, it means something else is holding it.
            print("Cache file is locked by Windows. Suggest server restart.")
            return {"status": "error", "message": "Cache is locked by Windows. Please restart the server console to force clear."}
        print(f"Cache Wipe Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"Cache Wipe Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/all", response_model=List[MemoryItem])
async def view_all_memories(limit: int = 100):
    try:
        memories = []

        # Helper to extract data from any memory tier
        def fetch_from_collection(collection_obj, tier_name):
            if not collection_obj: return []
            
            # ChromaDB .get() returns a dict of lists
            results = collection_obj.get(limit=limit)
            
            items = []
            ids = results["ids"]
            documents = results["documents"]
            metadatas = results["metadatas"]

            if ids:
                for i in range(len(ids)):
                    # We add the Tier Name to metadata so you know where it came from
                    meta = metadatas[i] or {}
                    meta["source_tier"] = tier_name 
                    
                    items.append({
                        "id": ids[i],
                        "text": documents[i],
                        "metadata": meta
                    })
            return items

        # 1. Fetch Working Memory (Tier 2)
        # Note: We check if it exists just to be safe
        if hasattr(store, "working_memory"):
            print("Scanning Working Memory...")
            memories.extend(fetch_from_collection(store.working_memory, "Working Memory"))

        # 2. Fetch Core Memory (Tier 1)
        if hasattr(store, "core_memory"):
            print("Scanning Core Memory...")
            memories.extend(fetch_from_collection(store.core_memory, "Core Memory"))
            
        return memories

    except Exception as e:
        print(f"Error fetching memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/source")
async def delete_source_memory(source: str):
    """
    Deletes ALL memory chunks linked to a specific Source URL.
    """
    try:
        print(f"🗑️ Deleting all memories from source: {source}")
        
        # 1. Delete from Working Memory (Tier 2)
        if hasattr(store, "working_memory"):
            # ChromaDB allows deleting by "metadata" filter
            store.working_memory.delete(where={"source": source})

        # 2. Delete from Core Memory (Tier 1)
        if hasattr(store, "core_memory"):
            store.core_memory.delete(where={"source": source})
            
        return {"status": "success", "message": f"Deleted all memories from {source}"}
    except Exception as e:
        print(f"Delete Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))