import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1/memory"
CHAT_URL = "http://127.0.0.1:8000/api/v1/chat"

def print_header(text):
    print(f"\n{'='*50}\n {text}\n{'='*50}")

def test_duplicates():
    print_header("1. 🛡️ Testing Duplicate Protection")
    payload = {
        "url": "https://test.com/rule_of_5",
        "text": "The Rule of 5 states that a memory must be recalled five times before entering the Core Vault."
    }
    
    # Scan 1
    print("   Attempt 1: Scanning...")
    requests.post(f"{BASE_URL}/ingest", json=payload)
    
    # Scan 2 (Should skip)
    print("   Attempt 2: Scanning again (Should skip)...")
    res = requests.post(f"{BASE_URL}/ingest", json=payload)
    print(f"   Result: {res.json()['message']}")

def test_promotion():
    print_header("2. 🎓 Testing 'Rule of 5' Promotion")
    
    # We ask the same question 5 times to trigger promotion
    query = {"message": "What is the Rule of 5?", "use_rag": True}
    
    for i in range(1, 7):
        print(f"\n--- Query Loop {i}/6 ---")
        
        # Ask Chat
        # We use stream=True but just consume it quickly to trigger the RAG logic
        with requests.post(CHAT_URL, json=query, stream=True) as r:
            for _ in r.iter_content(1024): pass 
        
        # Check Memory Status via Retrieval
        # We cheat and use the retrieval API to peek at the metadata
        check = requests.post(f"{BASE_URL}/query", json={"query": "Rule of 5"})
        data = check.json()
        
        if data:
            top_hit = data[0]
            tier = top_hit['tier']
            # Usage count might not be exposed in API response directly unless we added it,
            # but 'tier' is.
            print(f"   🔎 Memory Tier: {tier.upper()}")
            
            if tier == 'core':
                print(f"\n   ✅ SUCCESS! Memory promoted to CORE at Loop {i}")
                return
        else:
            print("   ⚠️ Memory not found?")
        
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        test_duplicates()
        test_promotion()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure server is running: python -m poetry run python server/src/api/main.py")