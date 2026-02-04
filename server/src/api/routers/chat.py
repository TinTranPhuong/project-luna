from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import delete

# Imports
from server.src.data.database.sqlite import get_db
from server.src.data.database.models import ChatSession, ChatMessage
from server.src.core.llm.manager import LLMManager

router = APIRouter()
llm_manager = LLMManager()

# --- Schemas ---
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    session_id: int

class SessionSchema(BaseModel):
    id: int
    title: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class MessageSchema(BaseModel):
    id: int
    role: str
    content: str
    
    class Config:
        from_attributes = True

# --- Endpoints ---

@router.get("/sessions", response_model=List[SessionSchema])
async def get_sessions(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Get a list of recent chat sessions."""
    result = await db.execute(
        select(ChatSession)
        .order_by(desc(ChatSession.created_at))
        .limit(limit)
    )
    return result.scalars().all()

@router.get("/history/{session_id}", response_model=List[MessageSchema])
async def get_session_history(session_id: int, db: AsyncSession = Depends(get_db)):
    """Load all messages for a specific session."""
    # 1. Check if session exists
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 2. Get messages
    msgs_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    return msgs_result.scalars().all()

@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Send a message and get a response."""
    
    # 1. Manage Session
    if request.session_id:
        result = await db.execute(select(ChatSession).where(ChatSession.id == request.session_id))
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        # Create new chat with a generated title (first 30 chars)
        short_title = request.message[:30] + "..." if len(request.message) > 30 else request.message
        session = ChatSession(title=short_title)
        db.add(session)
        await db.commit()
        await db.refresh(session)

    # 2. Save User Message
    user_msg = ChatMessage(session_id=session.id, role="user", content=request.message)
    db.add(user_msg)
    await db.commit()

    # 3. Load History for Context
    history_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at)
    )
    history_records = history_result.scalars().all()
    chat_history = [{"role": msg.role, "content": msg.content} for msg in history_records]

    # 4. Stream the Response
    async def iter_response():
        # FIX: Call the manager's stream_chat method
        # This fixes the "AttributeError: 'LLMManager' object has no attribute 'llm'"
        async for chunk in llm_manager.stream_chat(chat_history):
             yield chunk

    # 5. Save AI Response
    return StreamingResponse(iter_response(), media_type="text/plain")

@router.delete("/sessions")
async def clear_all_sessions(db: AsyncSession = Depends(get_db)):
    """Delete all chat history (The 'Men in Black' Neuralyzer)."""
    # SQLite usually handles cascading deletes, but let's be safe and delete messages first
    await db.execute(delete(ChatMessage)) 
    await db.execute(delete(ChatSession))
    await db.commit()
    return {"status": "success", "message": "Memory wiped."}