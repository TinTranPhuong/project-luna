import requests
import os
import sys

# --- Config ---
BASE_URL = "http://localhost:8000"
API_KEY = "luna-dev-secret" # Must match the default in middleware.py
HEADERS = {"X-LUNA-KEY": API_KEY}

# --- Colors for Output ---
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def log(test_name, success, message=""):
    status = f"{GREEN}PASS{RESET}" if success else f"{RED}FAIL{RESET}"
    print(f"[{status}] {test_name}: {message}")

def run_tests():
    print(f"🔍 Testing Phase 1.1 Foundation at {BASE_URL}...\n")

    # 1. Test Health Check (Public Route)
    try:
        res = requests.get(f"{BASE_URL}/health")
        if res.status_code == 200:
            log("Health Check", True, res.json())
        else:
            log("Health Check", False, f"Status {res.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"\n{RED}❌ CRITICAL: Could not connect to server.{RESET}")
        print("Did you run: 'poetry run uvicorn server.api.main:app --reload'?")
        sys.exit(1)

    # 2. Test Security (Should FAIL without key)
    res = requests.post(f"{BASE_URL}/v1/chat", json={"messages": []})
    if res.status_code == 403:
        log("Security Shield", True, "Successfully blocked unauthorized request")
    else:
        log("Security Shield", False, f"Expected 403, got {res.status_code}")

    # 3. Test Valid Chat Request (Should PASS with key)
    payload = {
        "messages": [{"role": "user", "content": "Hello Luna"}],
        "model": "test-model",
        "temperature": 0.5
    }
    res = requests.post(f"{BASE_URL}/v1/chat", headers=HEADERS, json=payload)
    if res.status_code == 200:
        data = res.json()
        if data["message"]["content"] == "Core Backend is online. LLM Adapter not yet connected.":
            log("Chat Route & DI", True, "Received correct placeholder response")
        else:
            log("Chat Route & DI", False, "Response content mismatch")
    else:
        log("Chat Route & DI", False, f"Status {res.status_code}: {res.text}")

    # 4. Test Schema Validation (Should REJECT bad data)
    bad_payload = {
        "messages": [{"role": "invalid-role", "content": "hi"}] # 'invalid-role' is not allowed
    }
    res = requests.post(f"{BASE_URL}/v1/chat", headers=HEADERS, json=bad_payload)
    if res.status_code == 422:
        log("Data Validation", True, "Correctly rejected invalid role")
    else:
        log("Data Validation", False, f"Expected 422, got {res.status_code}")

if __name__ == "__main__":
    run_tests()