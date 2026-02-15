from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal

# Enforcing strict roles for the agent system
RoleType = Literal["system", "user", "assistant", "tool"]

class ChatMessage(BaseModel):
    role: RoleType = Field(..., description="Role of the message sender")
    content: str = Field(..., description="The content of the message")
    # Optional metadata for tool calls or RAG citations
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None
    use_rag: bool = False
    image: Optional[str] = None
    mode: Optional[str] = "general"

class ChatResponse(BaseModel):
    id: str
    created: int
    model: str
    message: ChatMessage
    usage: Optional[Dict[str, int]] = None