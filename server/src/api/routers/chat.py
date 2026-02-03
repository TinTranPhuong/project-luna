from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel

# Imports from our Enterprise Structure
from server.src.data.database.sqlite import get_db
from server.src.data.database.models import ChatSession, ChatMessage
from server.src.core.llm.manager import LLMManager

router = APIRouter()

# Initialize the Brain
llm_manager = LLMManager()

# --- Request Schemas ---
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None  # If None, we create a new chat

class ChatResponse(BaseModel):
    response: str
    session_id: int

@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    The Main Nervous System:
    1. Gets/Creates a Chat Session in DB.
    2. Saves User Message.
    3. Loads History.
    4. Generates AI Response (with Context Window).
    5. Saves AI Response.
    """
    
    # 1. Manage Session (Memory Slot)
    if request.session_id:
        # Try to find existing chat
        result = await db.execute(select(ChatSession).where(ChatSession.id == request.session_id))
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        # Create new chat
        session = ChatSession(title=request.message[:30] + "...")
        db.add(session)
        await db.commit()
        await db.refresh(session)

    # 2. Save User Message (Long-Term Memory)
    user_msg = ChatMessage(session_id=session.id, role="user", content=request.message)
    db.add(user_msg)
    await db.commit()

    # 3. Load History for Context (The "Brain Food")
    # We fetch all messages for this session to build the context
    history_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at)
    )
    history_records = history_result.scalars().all()
    
    # Convert DB objects to the format LLM expects
    chat_history = [{"role": msg.role, "content": msg.content} for msg in history_records]

    # 4. Generate Response (The "Thinking")
    # (The LLMManager handles the System Prompt & Sliding Window internally now)
    ai_text = await llm_manager.generate_response(chat_history)

    # 5. Save AI Response (Long-Term Memory)
    ai_msg = ChatMessage(session_id=session.id, role="assistant", content=ai_text)
    db.add(ai_msg)
    await db.commit()

    return ChatResponse(response=ai_text, session_id=session.id)