import requests
import time
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8000/api/memory"

def test_ingest():
    print("\n1. 📥 Testing Ingestion (Scanning)...")
    payload = {
        "url": "https://luna-test.com/architecture",
        "text": """
        Luna is a personal AI assistant designed for the RTX 5060 Ti. 
        She uses a 'Split-Brain' architecture where the CPU handles memory (RAG) 
        and the GPU handles generation (LLM). This ensures 0GB VRAM usage for storage.
        """
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ingest", json=payload)
        if response.status_code == 200:
            print(f"   ✅ Success! {response.json()['message']}")
            return True
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_query():
    print("\n2. 🧠 Testing Retrieval (Recall)...")
    payload = {
        "query": "What is Luna's architecture?"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/query", json=payload)
        if response.status_code == 200:
            results = response.json()
            print(f"   ✅ Success! Found {len(results)} matches.")
            
            for i, res in enumerate(results):
                print(f"   --- Result {i+1} (Score: {res['score']:.4f}) ---")
                print(f"   📄 Source: {res['source']}")
                print(f"   💬 Text: {res['text'].strip()[:100]}...")
                print(f"   🏷️  Tier: {res['tier']}")
            return True
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Memory API Test...")
    print("⚠️  Ensure your server is running: 'python server/src/api/main.py'")
    
    # Check if requests is installed
    try:
        import requests
    except ImportError:
        print("❌ Missing dependency. Run: pip install requests")
        sys.exit(1)

    if test_ingest():
        time.sleep(1) # Give ChromaDB a moment to index
        test_query()