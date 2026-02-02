from fastapi import FastAPI, Depends, Security, Request
from fastapi.middleware.cors import CORSMiddleware

# Import your modules
from server.api.schemas import ChatRequest, ChatResponse, ChatMessage
from server.api.dependencies import get_llm_manager
from server.core.llm_manager import LLMManager
from server.api.middleware import RequestLoggingMiddleware, verify_api_key
from server.api.errors import global_exception_handler

app = FastAPI(title="Project Luna AI Server", version="0.1.0")

# 1. Global Error Handling
app.add_exception_handler(Exception, global_exception_handler)

# 2. CORS (Crucial for Chrome Extension)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev, we can allow all. Lock down later if needed.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Logging
app.add_middleware(RequestLoggingMiddleware)

# --- Routes ---

@app.get("/health")
async def health_check():
    return {"status": "ok", "mode": "personal"}

@app.post("/v1/chat", response_model=ChatResponse)
async def chat(
    chat_req: ChatRequest,
    api_key: str = Security(verify_api_key),  # 🔒 Protected
    llm: LLMManager = Depends(get_llm_manager)
):
    response_content = await llm.generate_response(
        messages=[m.model_dump() for m in chat_req.messages],
        settings={"temperature": chat_req.temperature, "model": chat_req.model}
    )
    
    return ChatResponse(
        id="gen-123",
        created=1234567890,
        model=chat_req.model or "local",
        message=ChatMessage(role="assistant", content=response_content)
    )