import sys
import os
from pathlib import Path

# 1. Setup the Path so Python can find 'server'
# We assume this script is in D:\Project_Luna\scripts
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from server.src.config.settings import get_model_path, MODEL_REGISTRY
from server.src.core.llm.manager import LLMManager

def test_settings():
    print("📋 Testing Configuration Layer...")
    
    # Test 1: Can we read the registry?
    print(f"   - Found {len(MODEL_REGISTRY)} models in registry.")
    
    # Test 2: Does the path resolve correctly?
    try:
        path = get_model_path("default")
        print(f"   - ✅ Default Model Resolved: {Path(path).name}")
        print(f"   - Full Path: {path}")
    except Exception as e:
        print(f"   - ❌ PATH ERROR: {e}")
        return

    # Test 3: Does the Manager load without crashing?
    print("\n🧠 Testing LLM Manager Initialization...")
    try:
        llm = LLMManager()
        # We just check if it initializes, we don't need to load the full GPU weights for this test
        # unless you want to wait 5 seconds.
        print(f"   - ✅ LLMManager initialized successfully.")
        print(f"   - Active Model: {llm.current_model_key}")
    except Exception as e:
        print(f"   - ❌ MANAGER ERROR: {e}")

if __name__ == "__main__":
    test_settings()