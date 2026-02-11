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

@router.post("") 
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Send a message and get a response."""
    
    # 1. Manage Session
    if request.session_id:
        result = await db.execute(select(ChatSession).where(ChatSession.id == request.session_id))
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        # Create new chat
        short_title = request.message[:30] + "..." if len(request.message) > 30 else request.message
        session = ChatSession(title=short_title)
        db.add(session)
        await db.commit()
        await db.refresh(session)

    # 2. Save User Message to DB (Raw, without injected context)
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
    
    # Convert to list of dicts
    chat_history = [{"role": msg.role, "content": msg.content} for msg in history_records]

    # --- NEW: RAG Context Injection ---
    # We inject the memory into the prompt sent to the AI, 
    # but we DO NOT save this huge text block to the database.
    if request.use_rag:
        print(f"Searching memory for: '{request.message}'")
        rag_results = retriever.search(request.message)
        
        if rag_results:
            context_str = "\n\n--- RELEVANT MEMORY ---\n"
            for i, doc in enumerate(rag_results):
                # Add citation [Source 1], [Source 2]
                context_str += f"[Source {i+1}]: {doc['text'].strip()}\n"
            context_str += "-----------------------\n"
            context_str += "INSTRUCTION: Answer the user's question using ONLY the context above. If unsure, say so.\n\n"
            
            # Modify the LAST message (current user prompt) in the temporary history list
            if chat_history:
                last_msg = chat_history[-1]
                last_msg["content"] = context_str + "User Question: " + last_msg["content"]

    # 4. Stream the Response
    async def iter_response():
        full_response = ""
        # Stream the chunks
        async for chunk in llm_manager.stream_chat(chat_history):
             full_response += chunk
             yield chunk
        
        # 5. Save AI Response to DB (After streaming finishes)
        # We need a new session context here because the stream happens after the request finishes
        # Ideally, we should handle this differently, but for now, we assume simple usage.
        # Note: Saving async inside a generator can be tricky. 
        # A common pattern is to save it after the loop if possible or use a background task.
        
        # --- FIX: Manually get a fresh DB session ---
        if full_response:
            print(f"Saving AI response for Session {session.id}...")
            # We iterate the get_db generator to get a new session
            async for db_new in get_db():
                try:
                    ai_msg = ChatMessage(session_id=session.id, role="assistant", content=full_response)
                    db_new.add(ai_msg)
                    await db_new.commit()
                except Exception as e:
                    print(f"Failed to save history: {e}")
                finally:
                    break # We only need one session, then exit the loop

    # CREATE RESPONSE OBJECT
    response = StreamingResponse(iter_response(), media_type="text/event-stream")
    
    # ATTACH THE KEY 
    response.headers["X-Session-ID"] = str(session.id)
    
    return response

@router.delete("/sessions")
async def clear_all_sessions(db: AsyncSession = Depends(get_db)):
    """Delete all chat history."""
    await db.execute(delete(ChatMessage)) 
    await db.execute(delete(ChatSession))
    await db.commit()
    return {"status": "success", "message": "Memory wiped."}