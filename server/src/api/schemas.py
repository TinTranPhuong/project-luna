from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal

# ==============================================================================
# TYPE DEFINITIONS
# ==============================================================================
RoleType = Literal["system", "user", "assistant", "tool"]

# ==============================================================================
# API SCHEMAS
# ==============================================================================
class ChatMessage(BaseModel):
    """Standard message format exchanged between the UI and LLM."""
    role: RoleType = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="The raw markdown or text content of the message")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Context tracking for RAG/Tools")

class ChatRequest(BaseModel):
    """Payload structure for incoming user chat requests."""
    message: str
    session_id: Optional[int] = None
    use_rag: bool = False
    image: Optional[str] = None
    mode: Optional[str] = "general"

class ChatResponse(BaseModel):
    """Payload structure for the completed LLM generation."""
    id: str
    created: int
    model: str
    message: ChatMessage
    usage: Optional[Dict[str, int]] = None