import requests
import time

# --- Config ---
SERVER_URL = "http://localhost:8000/v1/chat"
API_KEY = "luna-dev-secret" # Must match your middleware

headers = {
    "X-LUNA-KEY": API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "messages": [
        {"role": "system", "content": "You are a concise assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ],
    # We can override the model here if we want, or leave it to use default
    "model": "luna-qwen", 
    "temperature": 0.3
}

print(f"🚀 Sending request to AI Server at {SERVER_URL}...")
start = time.time()

try:
    res = requests.post(SERVER_URL, headers=headers, json=payload)
    
    if res.status_code == 200:
        data = res.json()
        duration = time.time() - start
        content = data["message"]["content"]
        
        print(f"\n✅ SUCCESS! Full Stack Verified.")
        print(f"⏱️ Time: {duration:.2f}s")
        print(f"🤖 Response: {content}")
    else:
        print(f"\n❌ Server Error {res.status_code}:")
        print(res.text)

except Exception as e:
    print(f"\n❌ Connection Failed: {e}")