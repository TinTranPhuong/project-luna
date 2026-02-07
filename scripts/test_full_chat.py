import requests
import json

# FIX 1: Use the correct V1 URL
URL = "http://127.0.0.1:8000/api/v1/chat"

payload = {
    "message": "Explain the split-brain architecture in simple terms.",
    "use_rag": True
}

print(f"💬 Asking Luna at {URL}...")

try:
    # FIX 2: Enable Streaming (stream=True)
    with requests.post(URL, json=payload, stream=True) as res:
        
        if res.status_code == 200:
            print("\n🤖 Luna's Answer:")
            print("-" * 40)
            
            # FIX 3: Read the response chunk by chunk (Text Stream)
            # We do NOT use res.json() here because it's a stream
            for chunk in res.iter_content(chunk_size=None):
                if chunk:
                    print(chunk.decode('utf-8'), end='', flush=True)
            
            print("\n" + "-" * 40)
            print("✅ Stream Finished")
            
        else:
            print(f"❌ Server Error {res.status_code}:")
            print(res.text)

except Exception as e:
    print("❌ Connection Error:", e)