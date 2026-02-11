import requests
import json
import time
import sys

# --- CONFIG ---
BASE_URL = "http://127.0.0.1:8000/api/v1"
HEADERS = {"Content-Type": "application/json"}

# Colors for clarity
class Colors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def print_pass(msg):
    print(f"{Colors.OKGREEN}   ✅ PASS: {msg}{Colors.ENDC}")

def print_fail(msg):
    print(f"{Colors.FAIL}   ❌ FAIL: {msg}{Colors.ENDC}")
    sys.exit(1)

def section(title):
    print(f"\n{Colors.HEADER}➤ {title}{Colors.ENDC}")

# --- 1. TEST THE "TEACH LUNA" MENU ---
def test_ingest():
    section("1. Testing 'Teach Luna' (Ingest)")
    print("   [UI Action]: User pastes URL -> Clicks 'ADD'")
    
    payload = {
        "url": "https://chrome-extension.test/secret",
        "text": "The secret code for the Chrome Extension is 'OMEGA-77'."
    }
    
    try:
        res = requests.post(f"{BASE_URL}/memory/ingest", json=payload, headers=HEADERS)
        if res.status_code == 200:
            print_pass(f"Server accepted knowledge. (Chunks: {res.json().get('chunks')})")
        else:
            print_fail(f"Server rejected ingest: {res.text}")
    except Exception as e:
        print_fail(f"Connection error: {e}")

# --- 2. TEST THE "BRAIN TOGGLE" ---
def test_chat_modes():
    section("2. Testing 'Brain Toggle'")
    query = "What is the secret code for the Chrome Extension?"
    
    # --- TEST 1: BRAIN OFF ---
    print("   [UI Action]: Toggle set to 'OFF 💤'")
    payload_off = {"message": query, "use_rag": False}
    
    response_off = ""
    print("   ... Asking LLM (Pure Generation) ...")
    with requests.post(f"{BASE_URL}/chat", json=payload_off, stream=True) as r:
        for chunk in r.iter_content(chunk_size=None):
            if chunk: response_off += chunk.decode()
            
    if "OMEGA-77" not in response_off:
        print_pass("Brain OFF worked (LLM did not know the secret).")
    else:
        print_fail("Brain OFF failed (LLM hallucinated or accessed memory?).")

    # --- TEST 2: BRAIN ON ---
    print("\n   [UI Action]: Toggle set to 'ON 🧠'")
    payload_on = {"message": query, "use_rag": True}
    
    response_on = ""
    print("   ... Asking LLM (RAG Retrieval) ...")
    with requests.post(f"{BASE_URL}/chat", json=payload_on, stream=True) as r:
        for chunk in r.iter_content(chunk_size=None):
            if chunk: response_on += chunk.decode()

    if "OMEGA-77" in response_on:
        print_pass("Brain ON worked (LLM found 'OMEGA-77').")
    else:
        print_fail("Brain ON failed (LLM did not find the secret).")

# --- 3. TEST THE HISTORY SIDEBAR ---
def test_history():
    section("3. Testing 'History Sidebar'")
    print("   [UI Action]: Loading sidebar items...")
    
    try:
        res = requests.get(f"{BASE_URL}/chat/sessions")
        if res.status_code == 200:
            sessions = res.json()
            if len(sessions) > 0:
                print_pass(f"Successfully loaded {len(sessions)} sessions.")
                print(f"      Latest Session: '{sessions[0]['title']}'")
            else:
                print_pass("Sidebar loaded (but was empty).")
        else:
            print_fail(f"Failed to load sessions: {res.text}")
    except Exception as e:
        print_fail(f"Connection error: {e}")

if __name__ == "__main__":
    print(f"{Colors.HEADER}🚀 STARTING CHROME EXTENSION BACKEND TEST{Colors.ENDC}")
    
    # 1. Teach it something new
    test_ingest()
    time.sleep(1) # Give DB a moment
    
    # 2. Try to recall it
    test_chat_modes()
    
    # 3. Check if it saved to history
    test_history()
    
    print(f"\n{Colors.OKGREEN}🎉 READY FOR CLIENT DEPLOYMENT{Colors.ENDC}")