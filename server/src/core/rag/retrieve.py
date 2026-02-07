import json
from diskcache import Cache
from flashrank import Ranker, RerankRequest
from server.src.config.settings import CACHE_PATH, DEFAULT_K, RERANK_TOP_K
from server.src.core.rag.store import store
from server.src.core.rag.embedder import embedder

# 1. Initialize Components
# DiskCache acts like Redis but simpler (Filesystem based)
cache = Cache(CACHE_PATH)

# FlashRank runs on CPU (TinyBERT) to sort results by quality
# It fixes the "Dumb Vector" problem where results are relevant but not helpful
ranker = Ranker(model_name="ms-marco-TinyBERT-L-2-v2", cache_dir=CACHE_PATH)

class Retriever:
    def __init__(self):
        self.cache = cache
        self.ranker = ranker

    def search(self, query: str) -> list:
        # 1. Check Cache (Speed Layer)
        # If we asked this exact question recently, return the saved answer.
        cache_key = f"search:{query}"
        if cache_key in self.cache:
            print(f"⚡ Cache Hit: {query}")
            return self.cache[cache_key]

        print(f"🔍 Searching: {query}...")

        # 2. Embed Query (CPU Layer)
        # Convert text -> [0.12, 0.99, ...]
        query_vector = embedder.embed_query(query)

        # 3. Vector Search (Database Layer)
        # We fetch MORE results than we need (DEFAULT_K=20) so the Reranker has options
        raw_results = store.query_all(query_vector, n_results=DEFAULT_K)
        
        # 4. Flatten Results
        # Combine Core and Working memory into a single list
        candidates = []
        
        # Process Core (The Vault)
        if raw_results["core"]["documents"]:
            for i, doc in enumerate(raw_results["core"]["documents"][0]):
                candidates.append({
                    "id": raw_results["core"]["ids"][0][i],
                    "text": doc,
                    "meta": raw_results["core"]["metadatas"][0][i],
                    "score": raw_results["core"]["distances"][0][i]  # Lower is better in Cosine
                })

        # Process Working (The Scratchpad)
        if raw_results["working"]["documents"]:
            for i, doc in enumerate(raw_results["working"]["documents"][0]):
                candidates.append({
                    "id": raw_results["working"]["ids"][0][i],
                    "text": doc,
                    "meta": raw_results["working"]["metadatas"][0][i],
                    "score": raw_results["working"]["distances"][0][i]
                })

        # If no results, return empty
        if not candidates:
            return []

        # 5. Rerank (Intelligence Layer)
        # We use FlashRank to grade the results from 0.0 to 1.0
        # This filters out "related but useless" text
        passages = [
            {"id": c["id"], "text": c["text"], "meta": c["meta"]} 
            for c in candidates
        ]
        
        rerank_request = RerankRequest(query=query, passages=passages)
        ranked_results = self.ranker.rerank(rerank_request)

        # 6. Select Top K (Precision Layer)
        # We only take the Top 3 (RERANK_TOP_K)
        final_results = ranked_results[:RERANK_TOP_K]
        
        # 7. Update Cache
        # Save results for next time
        self.cache[cache_key] = final_results
        
        # (Optional) Future: Increment Usage Count here for "Auto-Promotion"
        
        return final_results

# Global Instance
retriever = Retriever()