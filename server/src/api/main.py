from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.src.api.routers import chat, memory

# Import the Smart Router we just created
from server.src.api.routers import chat

# Initialize the Application
app = FastAPI(title="Luna Server", version="1.1")

# 1. Setup CORS (Essential for Chrome Extension)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Register the Chat Router
# This connects your "Smart Router" to the main application
# The prefix means all chat requests go to: http://localhost:8000/api/v1/chat
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["Memory"])

# 3. Health Check Endpoint
@app.get("/")
async def root():
    return {"status": "online", "message": "Luna Server is Running"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "mode": "gpu_accelerated"}
