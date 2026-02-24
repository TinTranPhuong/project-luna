import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path

# ==============================================================================
# PATH RESOLUTION & SYSTEM ENVIRONMENT
# ==============================================================================
current_file = Path(__file__).resolve() 
PROJECT_ROOT = current_file.parent.parent.parent.parent 

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

SRC_DIR = current_file.parent.parent 
WORKFLOW_PATH = SRC_DIR / "tools" / "comfyui" / "workflow_api.json"

# ==============================================================================
# INTERNAL IMPORTS
# ==============================================================================
from server.src.api.routers import chat, memory
from server.src.core.rag.store import store
from server.src.core.llm.comfy_adapter import ComfyAdapter
from server.src.api.routers.chat import llm_manager

# ==============================================================================
# ADAPTER INITIALIZATION
# ==============================================================================
if not WORKFLOW_PATH.exists():
    print(f"ERROR: Still cannot find workflow at: {WORKFLOW_PATH}")
else:
    print(f"SUCCESS: Workflow found at: {WORKFLOW_PATH}")

comfy_adapter = ComfyAdapter(str(WORKFLOW_PATH))

# ==============================================================================
# APPLICATION LIFECYCLE
# ==============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events for the FastAPI application."""
    print("Luna Server Starting...")
    store.cleanup()
    yield
    print("Luna Server Shutting Down...")
    
app = FastAPI(title="Luna Server", version="1.3", lifespan=lifespan)

# ==============================================================================
# MIDDLEWARE & ROUTING
# ==============================================================================
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

# ==============================================================================
# ROOT ENDPOINTS
# ==============================================================================
class GenerateRequest(BaseModel):
    prompt: str

@app.post("/api/v1/image/generate", tags=["Image"])
async def generate_image(request: GenerateRequest):
    """
    Intercepts image generation requests. Unloads the LLM from VRAM 
    and hands the prompt over to the ComfyUI adapter.
    """
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