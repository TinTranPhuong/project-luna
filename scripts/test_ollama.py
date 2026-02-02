import requests
import json
import time

# --- Config ---
MODEL = "luna-qwen"
# CHANGED: Use the 'chat' endpoint instead of 'generate'
URL = "http://localhost:11434/api/chat" 

print(f"⏳ Testing connection to Ollama ({MODEL})...")

try:
    start = time.time()
    
    # CHANGED: Payload uses 'messages' format (System + User)
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! Are you working?"}
        ],
        "stream": False,
        # Explicitly set context window to avoid VL model issues
        "options": {
            "num_ctx": 2048 
        }
    }
    
    response = requests.post(URL, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        duration = time.time() - start
        
        # CHANGED: Response parsing for chat object
        content = data.get("message", {}).get("content", "No content received")
        
        print("\n✅ SUCCESS! Custom GGUF Model is working via API.")
        print(f"⏱️ Response time: {duration:.2f}s")
        print(f"🤖 AI Answer: {content}")
    else:
        print(f"\n❌ Error: {response.text}")

except Exception as e:
    print(f"\n❌ Failed: {e}")