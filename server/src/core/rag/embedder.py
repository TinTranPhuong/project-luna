from sentence_transformers import SentenceTransformer
from typing import List
from server.src.config.settings import EMBEDDING_MODEL_NAME

# ==============================================================================
# EMBEDDING ENGINE
# ==============================================================================

class CPUEmbedder:
    """
    Singleton class managing the SentenceTransformer model.
    Forces embedding generation onto the CPU to reserve VRAM for the main LLM.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CPUEmbedder, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        print(f"Loading Embedding Model ({EMBEDDING_MODEL_NAME}) on CPU...")
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME, device='cpu')
        print("Embedding Model Ready")

    def embed_query(self, text: str) -> List[float]:
        """Encodes a single search query into a dense vector."""
        return self.model.encode(text, convert_to_tensor=False).tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Encodes a batch of document chunks into dense vectors."""
        return self.model.encode(texts, convert_to_tensor=False).tolist()

embedder = CPUEmbedder()