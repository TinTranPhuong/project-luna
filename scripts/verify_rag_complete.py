import requests
import json
import time
import sys

# --- CONFIGURATION ---
BASE_URL = "http://127.0.0.1:8000/api/v1"
HEADERS = {"Content-Type": "application/json"}

# A unique secret fact that the LLM definitely doesn't know
TEST_SECRET = "Luna's favorite food is 'Quantum Spicy Noodles' with hex code #FF0099."
TEST_URL = "https://internal.test/luna-facts"
TEST_QUERY = "What is Luna's favorite food?"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def print_step(msg):
    print(f"\n{Colors.HEADER}➤ {msg}{Colors.ENDC}")

def print_success(msg):
    print(f"{Colors.OKGREEN}   ✅ PASS: {msg}{Colors.ENDC}")

def print_fail(msg):
    print(f"{Colors.FAIL}   ❌ FAIL: {msg}{Colors.ENDC}")
    sys.exit(1)

def test_health():
    print_step("Checking Server Health...")
    try:
        # FastAPI usually has a docs endpoint we can hit, or we just trust the connection
        resp = requests.get(f"{BASE_URL}/chat/sessions") 
        if resp.status_code == 200:
            print_success("Server is online and responding.")
        else:
            print_fail(f"Server returned {resp.status_code}")
    except requests.exceptions.ConnectionError:
        print_fail("Could not connect. Is the server running? (python -m poetry run uvicorn server.src.api.main:app --reload)")

def test_ingest():
    print_step(f"Teaching Luna a Secret: '{TEST_SECRET}'...")
    payload = {
        "url": TEST_URL,
        "text": TEST_SECRET
    }
    resp = requests.post(f"{BASE_URL}/memory/ingest", json=payload, headers=HEADERS)
    
    if resp.status_code == 200:
        data = resp.json()
        print_success(f"Ingested {data.get('chunks', 0)} chunks.")
    else:
        print_fail(f"Ingest failed: {resp.text}")

def test_retrieval():
    print_step("Testing Database Retrieval (The Search Engine)...")
    payload = {"query": TEST_QUERY}
    resp = requests.post(f"{BASE_URL}/memory/query", json=payload, headers=HEADERS)
    
    if resp.status_code == 200:
        results = resp.json()
        if not results:
            print_fail("No results found in memory.")
        
        top_match = results[0]
        print(f"   🔎 Found: {top_match['text']}")
        print(f"   📊 Score: {top_match['score']}")
        
        if "Quantum Spicy Noodles" in top_match['text']:
            print_success("Database found the correct secret.")
        else:
            print_fail("Database found something, but not our secret.")
    else:
        print_fail(f"Retrieval failed: {resp.text}")

def test_rag_chat():
    print_step("Testing RAG Chat (Brain ON)...")
    print("   (Asking Luna... this might take a few seconds)")
    
    payload = {
        "message": TEST_QUERY,
        "use_rag": True,
        "session_id": None
    }
    
    full_response = ""
    # Use streaming
    with requests.post(f"{BASE_URL}/chat", json=payload, stream=True, headers=HEADERS) as r:
        if r.status_code != 200:
            print_fail(f"Chat failed: {r.text}")
            
        for chunk in r.iter_content(chunk_size=None):
            if chunk:
                full_response += chunk.decode('utf-8')

    print(f"   🤖 Answer: {full_response.strip()}")
    
    if "Quantum Spicy Noodles" in full_response or "#FF0099" in full_response:
        print_success("Luna answered correctly using RAG!")
    else:
        print_fail("Luna did NOT mention the secret. RAG context injection might be failing.")

def test_no_rag_chat():
    print_step("Testing Logic Chat (Brain OFF)...")
    print("   (Asking same question with Memory Disabled...)")
    
    payload = {
        "message": TEST_QUERY,
        "use_rag": False, # <--- IMPORTANT
        "session_id": None
    }
    
    full_response = ""
    with requests.post(f"{BASE_URL}/chat", json=payload, stream=True, headers=HEADERS) as r:
        for chunk in r.iter_content(chunk_size=None):
            if chunk:
                full_response += chunk.decode('utf-8')

    print(f"   🤖 Answer: {full_response.strip()}")
    
    if "Quantum Spicy Noodles" not in full_response:
        print_success("Luna does NOT know the secret (Expected behavior). Toggle works.")
    else:
        print(f"{Colors.WARNING}   ⚠️ WARNING: Luna guessed the secret without memory? (Unlikely but possible hallucination){Colors.ENDC}")

if __name__ == "__main__":
    print(f"{Colors.OKBLUE}🚀 STARTING FINAL SYSTEM CHECK{Colors.ENDC}")
    print("==========================================")
    
    test_health()
    time.sleep(0.5)
    
    test_ingest()
    time.sleep(1) # Give ChromaDB a moment to index
    
    test_retrieval()
    time.sleep(0.5)
    
    test_rag_chat()
    time.sleep(0.5)
    
    test_no_rag_chat()
    
    print("\n==========================================")
    print(f"{Colors.OKGREEN}🎉 ALL SYSTEMS GO! READY FOR FRONTEND.{Colors.ENDC}")