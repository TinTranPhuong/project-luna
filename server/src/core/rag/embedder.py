from sentence_transformers import SentenceTransformer
from typing import List
from server.src.config.settings import EMBEDDING_MODEL_NAME

class CPUEmbedder:
    _instance = None

    def __new__(cls):
        # Singleton pattern to prevent reloading the model multiple times
        if cls._instance is None:
            cls._instance = super(CPUEmbedder, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        print(f"Loading Embedding Model ({EMBEDDING_MODEL_NAME}) on CPU...")
        # device='cpu' is critical to save VRAM
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME, device='cpu')
        print("Embedding Model Ready")

    def embed_query(self, text: str) -> List[float]:
        # Encodes a single query string into a vector list
        return self.model.encode(text, convert_to_tensor=False).tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Encodes a list of documents into vector lists
        return self.model.encode(texts, convert_to_tensor=False).tolist()

# Global instance
embedder = CPUEmbedder()