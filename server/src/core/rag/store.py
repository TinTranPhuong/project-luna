import chromadb
from chromadb.config import Settings
from server.src.config.settings import CHROMA_PATH
import time

class MemoryStore:
    _instance = None

    def __new__(cls):
        # Singleton pattern for database connection
        if cls._instance is None:
            cls._instance = super(MemoryStore, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        print(f"Connecting to ChromaDB at: {CHROMA_PATH}")
        
        # Setup Persistent Client
        self.client = chromadb.PersistentClient(
            path=CHROMA_PATH,
            settings=Settings(allow_reset=True, anonymized_telemetry=False)
        )

        # Initialize Working Memory (Temp)
        self.working_memory = self.client.get_or_create_collection(
            name="working_memory",
            metadata={"hnsw:space": "cosine", "type": "temp"}
        )

        # Initialize Core Memory (Vault)
        self.core_memory = self.client.get_or_create_collection(
            name="core_memory",
            metadata={"hnsw:space": "cosine", "type": "core"}
        )
        
        print(f"Memory Store Ready. Working: {self.working_memory.count()} | Core: {self.core_memory.count()}")

    def save_to_working(self, chunks: list, metadatas: list, ids: list):
        # Saves data to the temporary collection
        if not ids: return
        self.working_memory.upsert(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Saved {len(ids)} chunks to Working Memory.")

    def promote_to_core(self, chunk_id: str, document: str, metadata: dict):
        # Moves a chunk from Working to Core collection
        print(f"Promoting Memory: {chunk_id}")
        
        metadata["tier"] = "core"
        # Upsert to Core
        self.core_memory.upsert(
            documents=[document],
            metadatas=[metadata],
            ids=[chunk_id]
        )
        
        # Delete from Working
        self.working_memory.delete(ids=[chunk_id])

    def query_all(self, query_vector, n_results=10):
        # Queries both collections
        core_results = self.core_memory.query(
            query_embeddings=[query_vector],
            n_results=n_results
        )
        
        work_results = self.working_memory.query(
            query_embeddings=[query_vector],
            n_results=n_results
        )
        
        return {
            "core": core_results,
            "working": work_results
        }

# Global instance
store = MemoryStore()