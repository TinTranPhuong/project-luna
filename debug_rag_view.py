import requests
import json

URL = "http://127.0.0.1:8000/api/v1/memory/all"

def inspect_brain():
    print(f"🧠 Connecting to Luna's Neural Network ({URL})...")
    
    try:
        response = requests.get(URL, params={"limit": 50}) # Limit to 50 items
        
        if response.status_code != 200:
            print(f"❌ Error: {response.text}")
            return

        memories = response.json()
        count = len(memories)
        
        print(f"\n📂 FOUND {count} MEMORY FRAGMENTS:\n")
        print("="*60)
        
        for i, mem in enumerate(memories):
            source = mem['metadata'].get('source', 'Unknown Source')
            text_preview = mem['text'][:100].replace('\n', ' ') + "..."
            
            print(f"📄 ID: {mem['id']}")
            print(f"🔗 Source: {source}")
            print(f"📝 Content: {text_preview}")
            print("-" * 60)

    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    inspect_brain()