import requests
import json

BASE_URL = "http://localhost:8000/api/v1/chat"

def test_full_stack():
    print("🚀 Testing Full Enterprise Stack...")

    # 1. Start a New Conversation
    print("\n1️⃣  Sending First Message (New Session)...")
    payload1 = {"message": "Hello, my name is Creator."}
    try:
        r1 = requests.post(BASE_URL, json=payload1)
        r1.raise_for_status()
        data1 = r1.json()
        session_id = data1['session_id']
        print(f"   ✅ AI Replied: {data1['response']}")
        print(f"   ✅ Created Session ID: {session_id}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return

    # 2. Continue Conversation (Test Memory)
    print("\n2️⃣  Sending Second Message (Testing Recall)...")
    payload2 = {
        "message": "What is my name?", 
        "session_id": session_id
    }
    
    try:
        r2 = requests.post(BASE_URL, json=payload2)
        r2.raise_for_status()
        data2 = r2.json()
        print(f"   ✅ AI Replied: {data2['response']}")
        
        if "Creator" in data2['response'] or "creator" in data2['response']:
            print("   🎉 SUCCESS: The AI remembers you!")
        else:
            print("   ⚠️ Note: AI might not have explicitly said the name, check context.")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_full_stack()