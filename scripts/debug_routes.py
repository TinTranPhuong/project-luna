import requests

try:
    # We fetch the OpenAPI schema which lists every valid URL
    response = requests.get("http://127.0.0.1:8000/openapi.json")
    
    if response.status_code == 200:
        data = response.json()
        print("\n🗺️  SERVER ROUTE MAP:")
        print("------------------------------------------------")
        paths = data.get("paths", {})
        for path, methods in paths.items():
            for method in methods:
                print(f"[{method.upper()}] http://127.0.0.1:8000{path}")
        print("------------------------------------------------")
    else:
        print("❌ Server is running but returned error on map.")
        
except Exception as e:
    print(f"❌ Could not connect to server. Is it running? Error: {e}")