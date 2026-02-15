import os
from pathlib import Path

# --- PATH CONFIGURATION ---
CURRENT_FILE = Path(__file__).resolve()
SRC_ROOT = CURRENT_FILE.parent.parent
PROJECT_ROOT = CURRENT_FILE.parent.parent.parent.parent

# Model Directory
MODEL_DIR = SRC_ROOT / "models"

# RAG Data Directory
RAG_DATA_DIR = PROJECT_ROOT / "rag_data"
CHROMA_PATH = str(RAG_DATA_DIR / "chroma_db")
CACHE_PATH = str(RAG_DATA_DIR / "disk_cache")

os.makedirs(RAG_DATA_DIR, exist_ok=True)

# --- MODEL REGISTRY ---
QWEN_FILENAME = "Qwen3VL-8B-Instruct-Q8_0.gguf"

MODEL_REGISTRY = {
    "default": QWEN_FILENAME,
    "qwen": QWEN_FILENAME,  # The only key we need
}

# Vision Projector (Only used for Qwen)
MMPROJ_FILENAME = "mmproj-Qwen3VL-8B-Instruct-F16.gguf"
MMPROJ_PATH = str(MODEL_DIR / MMPROJ_FILENAME)

# --- RAG CONFIGURATION ---
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
TEMP_RETENTION_DAYS = 5
PROMOTION_THRESHOLD = 5
DEFAULT_K = 20
RERANK_TOP_K = 3

def get_model_path(model_key: str = "default") -> str:
    # 1. Try to find the key in the registry (e.g., "vision" -> "Qwen...gguf")
    filename = MODEL_REGISTRY.get(model_key)
    
    # 2. If not found, maybe the user passed the filename directly?
    if not filename:
        if (MODEL_DIR / model_key).exists():
            filename = model_key
        else:
            print(f"Model Key '{model_key}' not found. Using default.")
            filename = MODEL_REGISTRY["default"]

    model_path = MODEL_DIR / filename
    
    # 3. Last check for file existence
    if not model_path.exists():
        fallback_path = PROJECT_ROOT / "server" / "models" / filename
        if fallback_path.exists():
            return str(fallback_path)
        print(f"CRITICAL: Model file missing: {model_path}")
        
    return str(model_path)

# --- CONTEXT VARS ---
MAX_HISTORY_MESSAGES = 10 
MAX_CONTEXT_TOKENS = 50000