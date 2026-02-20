import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path

# --- 1. BULLETPROOF PATH & IMPORTS ---
current_file = Path(__file__).resolve() 
# Path: D:\Project_Luna\server\src\api\main.py -> D:\Project_Luna\server\
# We need to reach the server root for the 'server.src' imports to work
PROJECT_ROOT = current_file.parent.parent.parent.parent 
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Now construct the correct workflow path (up two levels to 'src')
SRC_DIR = current_file.parent.parent 
WORKFLOW_PATH = SRC_DIR / "tools" / "comfyui" / "workflow_api.json"

# --- 2. IMPORTS ---
from server.src.api.routers import chat, memory
from server.src.core.rag.store import store
from server.src.core.llm.comfy_adapter import ComfyAdapter
from server.src.api.routers.chat import llm_manager

# --- 3. INITIALIZE ADAPTER ---
if not WORKFLOW_PATH.exists():
    print(f"ERROR: Still cannot find workflow at: {WORKFLOW_PATH}")
else:
    print(f"SUCCESS: Workflow found at: {WORKFLOW_PATH}")

comfy_adapter = ComfyAdapter(str(WORKFLOW_PATH))

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Luna Server Starting...")
    store.cleanup()
    yield
    print("Luna Server Shutting Down...")
    
app = FastAPI(title="Luna Server", version="1.3", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Session-ID"]
)

app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["Memory"])

class GenerateRequest(BaseModel):
    prompt: str

@app.post("/api/v1/image/generate", tags=["Image"])
async def generate_image(request: GenerateRequest):
    print(f"Received Image Request: {request.prompt}")
    print("Handoff: Unloading LLM to clear VRAM for ComfyUI...")
    llm_manager.unload_model()

    response = comfy_adapter.queue_prompt(request.prompt)
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
        
    return {
        "status": "queued",
        "prompt_id": response.get('prompt_id'),
        "message": "Sent to ComfyUI successfully!"
    }

@app.get("/")
async def root():
    return {"status": "online", "message": "Luna Server is Running"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "mode": "gpu_accelerated"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)