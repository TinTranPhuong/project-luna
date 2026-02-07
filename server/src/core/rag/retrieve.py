import json
from diskcache import Cache
from flashrank import Ranker, RerankRequest
from server.src.config.settings import CACHE_PATH, DEFAULT_K, RERANK_TOP_K
from server.src.core.rag.store import store
from server.src.core.rag.embedder import embedder

cache = Cache(CACHE_PATH)
ranker = Ranker(model_name="ms-marco-TinyBERT-L-2-v2", cache_dir=CACHE_PATH)

class Retriever:
    def __init__(self):
        self.cache = cache
        self.ranker = ranker

    def search(self, query: str) -> list:
        # 1. Check Cache (Speed Layer) - ENABLED 
        # If we asked this exact question recently, return the saved answer.
        cache_key = f"search:{query}"
        if cache_key in self.cache:
            print(f"Cache Hit: {query}")
            return self.cache[cache_key]

        print(f"Searching: {query}...")

        # 2. Embed Query
        query_vector = embedder.embed_query(query)

        # 3. Vector Search
        raw_results = store.query_all(query_vector, n_results=DEFAULT_K)
        
        # 4. Flatten Results
        candidates = []
        
        if raw_results["core"]["documents"]:
            for i, doc in enumerate(raw_results["core"]["documents"][0]):
                candidates.append({
                    "id": raw_results["core"]["ids"][0][i],
                    "text": doc,
                    "meta": raw_results["core"]["metadatas"][0][i],
                    "score": raw_results["core"]["distances"][0][i]
                })

        if raw_results["working"]["documents"]:
            for i, doc in enumerate(raw_results["working"]["documents"][0]):
                candidates.append({
                    "id": raw_results["working"]["ids"][0][i],
                    "text": doc,
                    "meta": raw_results["working"]["metadatas"][0][i],
                    "score": raw_results["working"]["distances"][0][i]
                })

        if not candidates:
            return []

        # 5. Rerank
        passages = [
            {"id": c["id"], "text": c["text"], "meta": c["meta"]} 
            for c in candidates
        ]
        
        rerank_request = RerankRequest(query=query, passages=passages)
        ranked_results = self.ranker.rerank(rerank_request)

        # 6. Select Top K
        final_results = ranked_results[:RERANK_TOP_K]
        
        # 7. AUTOMATION: Update Usage Stats (Rule of 5)
        try:
            update_ids = [r["id"] for r in final_results]
            update_metas = [r["meta"] for r in final_results]
            update_docs = [r["text"] for r in final_results]
            
            store.update_usage(update_ids, update_metas, update_docs)
        except Exception as e:
            print(f"Failed to update stats: {e}")

        # 8. Update Cache - ENABLED 
        self.cache[cache_key] = final_results
        
        return final_results

retriever = Retriever()