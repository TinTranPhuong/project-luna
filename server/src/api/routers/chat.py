from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, delete
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import time

# Imports
from server.src.data.database.sqlite import get_db
from server.src.data.database.models import ChatSession, ChatMessage
from server.src.core.llm.manager import LLMManager
from server.src.core.rag.retrieve import retriever

router = APIRouter()
llm_manager = LLMManager()

# --- Schemas ---
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None
    use_rag: Optional[bool] = True 
    image: Optional[str] = None

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
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    msgs_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    return msgs_result.scalars().all()

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: int, db: AsyncSession = Depends(get_db)):
    # Check if session exists
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Delete messages first (Cascade usually handles this, but manual is safer)
    await db.execute(delete(ChatMessage).where(ChatMessage.session_id == session_id))
    # Delete the session
    await db.execute(delete(ChatSession).where(ChatSession.id == session_id))
    
    await db.commit()
    return {"status": "success", "message": f"Session {session_id} deleted"}

@router.delete("/sessions")
async def clear_all_sessions(db: AsyncSession = Depends(get_db)):
    """Delete all chat history."""
    await db.execute(delete(ChatMessage)) 
    await db.execute(delete(ChatSession))
    await db.commit()
    return {"status": "success", "message": "Memory wiped."}

@router.post("") 
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Send a message and get a response."""
    
    # 1. Manage Session
    session = None
    if request.session_id:
        result = await db.execute(select(ChatSession).where(ChatSession.id == request.session_id))
        session = result.scalar_one_or_none()
    
    # Create new session if needed
    if not session:
        short_title = request.message[:30] + "..." if len(request.message) > 30 else request.message
        session = ChatSession(title=short_title)
        db.add(session)
        await db.commit()
        await db.refresh(session)

    # 2. Save User Message to DB (Text Only)
    user_msg = ChatMessage(session_id=session.id, role="user", content=request.message)
    db.add(user_msg)
    await db.commit()

    # 3. Load History
    # We fetch the history we just saved so the context is complete
    history_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at)
    )
    history_records = history_result.scalars().all()
    
    # Convert to list of dicts
    chat_history = [{"role": msg.role, "content": msg.content} for msg in history_records]

    # 4. Prepare Context & Vision
    current_prompt_text = request.message

    # RAG Context
    if request.use_rag:
        print(f"Searching memory for: '{request.message}'")
        try:
            rag_results = retriever.search(request.message)
            if rag_results:
                context_str = "\n\n--- RELEVANT CONTEXT ---\n"
                for i, doc in enumerate(rag_results):
                    context_str += f"[{i+1}] {doc['text'].strip()}\n"
                context_str += "------------------------\n"
                
                # Prepend context to the user's question in the prompt
                current_prompt_text = context_str + "Question: " + current_prompt_text
        except Exception as e:
            print(f"RAG Error (continuing without context): {e}")

    # Vision Payload
    if request.image:
        print(f"Constructing Vision Payload...")
        # Replace the last text message with the multimodal one
        if chat_history and chat_history[-1]['role'] == 'user':
             chat_history[-1] = {
                "role": "user",
                "content": [
                    {"type": "text", "text": current_prompt_text},
                    {"type": "image_url", "image_url": {"url": request.image}}
                ]
            }
    else:
        # Standard Text Mode: Update the last message with RAG context if needed
        if chat_history and chat_history[-1]['role'] == 'user':
            chat_history[-1]['content'] = current_prompt_text

    # 5. Stream Response
    async def iter_response():
        full_response = ""
        
        try:
            async for chunk in llm_manager.stream_chat(chat_history):
                 full_response += chunk
                 yield chunk
        except Exception as e:
            print(f"LLM Generation Error: {e}")
            yield f"\n[Error generating response: {e}]"
            return

        # Save AI Response
        if full_response:
            # New DB session for the background save
            async for db_new in get_db():
                try:
                    ai_msg = ChatMessage(session_id=session.id, role="assistant", content=full_response)
                    db_new.add(ai_msg)
                    await db_new.commit()
                except Exception as e:
                    print(f"Failed to save response: {e}")
                break

    response = StreamingResponse(iter_response(), media_type="text/event-stream")
    response.headers["X-Session-ID"] = str(session.id)
    return response