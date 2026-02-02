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
    messages: List[ChatMessage]
    model: Optional[str] = Field(None, description="Specific model to use (e.g., 'llama3')")
    stream: bool = Field(False, description="Whether to stream the response")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    
    # Context ID for linking to specific browser tabs or sessions
    context_id: Optional[str] = None

class ChatResponse(BaseModel):
    id: str
    created: int
    model: str
    message: ChatMessage
    usage: Optional[Dict[str, int]] = None