import os
from pathlib import Path

# --- PATH CONFIGURATION ---
# Structure: server/src/config/settings.py
# .parent = config
# .parent.parent = src
# .parent.parent.parent = server
# .parent.parent.parent.parent = Project_Luna (Root)

CURRENT_FILE = Path(__file__).resolve()
SRC_ROOT = CURRENT_FILE.parent.parent
PROJECT_ROOT = CURRENT_FILE.parent.parent.parent.parent

# Model Directory
MODEL_DIR = SRC_ROOT / "models"

# RAG Data Directory (Stored in Project Root/rag_data)
RAG_DATA_DIR = PROJECT_ROOT / "rag_data"
CHROMA_PATH = str(RAG_DATA_DIR / "chroma_db")
CACHE_PATH = str(RAG_DATA_DIR / "disk_cache")

# Ensure directories exist
os.makedirs(RAG_DATA_DIR, exist_ok=True)

# --- MODEL REGISTRY ---
MODEL_REGISTRY = {
    "default": "DeepSeek-R1-Distill-Qwen-14B-Q4_K_M.gguf",
    "vision": "mmproj-Qwen2.5-VL-7B-Instruct-bf16.gguf" 
}

# --- RAG CONFIGURATION ---
# CPU-Optimized Embedding Model
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Memory Rules
TEMP_RETENTION_DAYS = 5
PROMOTION_THRESHOLD = 5

# Search Settings
DEFAULT_K = 20
RERANK_TOP_K = 3

def get_model_path(model_key: str = "default") -> str:
    # Returns the absolute path to the requested model.
    filename = MODEL_REGISTRY.get(model_key, MODEL_REGISTRY["default"])
    model_path = MODEL_DIR / filename
    
    if not model_path.exists():
        # Fallback check: sometimes models are in the root 'server/models'
        fallback_path = PROJECT_ROOT / "server" / "models" / filename
        if fallback_path.exists():
            return str(fallback_path)
        raise FileNotFoundError(f"Model file not found at: {model_path}")
        
    return str(model_path)

# --- CONTEXT MANAGEMENT ---
MAX_HISTORY_MESSAGES = 10 
MAX_CONTEXT_TOKENS = 4096