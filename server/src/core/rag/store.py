import chromadb
from chromadb.config import Settings
from datetime import datetime, timedelta
from server.src.config.settings import CHROMA_PATH, PROMOTION_THRESHOLD, TEMP_RETENTION_DAYS 
import time

class MemoryStore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MemoryStore, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        print(f"Connecting to ChromaDB at: {CHROMA_PATH}")
        
        self.client = chromadb.PersistentClient(
            path=CHROMA_PATH,
            settings=Settings(allow_reset=True, anonymized_telemetry=False)
        )

        self.working_memory = self.client.get_or_create_collection(
            name="working_memory",
            metadata={"hnsw:space": "cosine", "type": "temp"}
        )

        self.core_memory = self.client.get_or_create_collection(
            name="core_memory",
            metadata={"hnsw:space": "cosine", "type": "core"}
        )
        
        print(f"Memory Store Ready. Working: {self.working_memory.count()} | Core: {self.core_memory.count()}")

    def cleanup(self):
        """
        The Janitor: Deletes 'temp' memories older than TEMP_RETENTION_DAYS (5 days).
        Runs on server startup.
        """
        print("Running Cleanup Task...")
        
        # 1. Get all temp items
        # We fetch only metadata/ids to save RAM
        data = self.working_memory.get(
            where={"tier": "temp"} # ChromaDB filter
        )
        
        if not data or not data['ids']:
            print("No temp memories to clean.")
            return

        ids_to_delete = []
        limit_date = datetime.now() - timedelta(days=TEMP_RETENTION_DAYS)
        
        count = 0
        for i, meta in enumerate(data['metadatas']):
            # Robust Date Parsing
            try:
                created_at_str = meta.get('created_at')
                if not created_at_str: continue
                
                # Parse the date string back to object
                created_at = datetime.fromisoformat(created_at_str)
                
                # Check if it's too old
                if created_at < limit_date:
                    ids_to_delete.append(data['ids'][i])
                    count += 1
            except Exception as e:
                print(f"Date parsing error for ID {data['ids'][i]}: {e}")

        # 2. Delete the old ones
        if ids_to_delete:
            print(f"Deleting {count} expired memories...")
            self.working_memory.delete(ids=ids_to_delete)
        else:
            print("All temp memories are fresh.")

    def save_to_working(self, chunks: list, metadatas: list, ids: list):
        if not ids: return
        
        existing = self.working_memory.get(ids=ids)
        if existing and existing['ids']:
            print(f"Skipping {len(existing['ids'])} duplicates.")
            return

        self.working_memory.upsert(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Saved {len(ids)} chunks to Working Memory.")

    def promote_to_core(self, chunk_id: str, document: str, metadata: dict):
        print(f"PROMOTION! Memory {chunk_id} has graduated to Core.")
        
        metadata["tier"] = "core"
        self.core_memory.upsert(
            documents=[document],
            metadatas=[metadata],
            ids=[chunk_id]
        )
        self.working_memory.delete(ids=[chunk_id])

    def update_usage(self, result_ids: list, result_metadatas: list, documents: list):
        for i, _id in enumerate(result_ids):
            meta = result_metadatas[i]
            if meta.get("tier") != "temp": continue
                
            current_count = int(meta.get("usage_count", 0))
            new_count = current_count + 1
            meta["usage_count"] = new_count
            
            if new_count >= PROMOTION_THRESHOLD:
                self.promote_to_core(_id, documents[i], meta)
            else:
                print(f"Updating memory usage: {_id} ({new_count}/{PROMOTION_THRESHOLD})")
                self.working_memory.update(ids=[_id], metadatas=[meta])

    def query_all(self, query_vector, n_results=10):
        core_results = self.core_memory.query(query_embeddings=[query_vector], n_results=n_results)
        work_results = self.working_memory.query(query_embeddings=[query_vector], n_results=n_results)
        return {"core": core_results, "working": work_results}

store = MemoryStore()