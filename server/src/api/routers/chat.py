from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, delete
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import asyncio
import os
import re 
from pathlib import Path

# Imports
from server.src.data.database.sqlite import get_db
from server.src.data.database.models import ChatSession, ChatMessage
from server.src.core.llm.manager import LLMManager
from server.src.core.rag.retrieve import retriever
from server.src.agents.registry import get_agent
from server.src.core.llm.comfy_adapter import ComfyAdapter

router = APIRouter()
llm_manager = LLMManager()

# --- BULLETPROOF PATH SETUP ---
CURRENT_FILE = Path(__file__).resolve()
SRC_DIR = CURRENT_FILE.parent.parent.parent
WORKFLOW_PATH = SRC_DIR / "tools" / "comfyui" / "workflow_api.json"

# Initialize Adapter
comfy_adapter = ComfyAdapter(str(WORKFLOW_PATH))

# --- Schemas ---
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None
    use_rag: Optional[bool] = True
    image: Optional[str] = None
    mode: Optional[str] = "general"

class ChatResponse(BaseModel):
    response: str
    session_id: int

class SessionSchema(BaseModel):
    id: int
    title: str
    created_at: datetime
    class Config: from_attributes = True

class MessageSchema(BaseModel):
    id: int
    role: str
    content: str
    class Config: from_attributes = True

# --- Endpoints ---

@router.get("/sessions", response_model=List[SessionSchema])
async def get_sessions(limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatSession).order_by(desc(ChatSession.created_at)).limit(limit))
    return result.scalars().all()

@router.get("/history/{session_id}", response_model=List[MessageSchema])
async def get_session_history(session_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Session not found")
    msgs_result = await db.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at)
    )
    return msgs_result.scalars().all()

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: int, db: AsyncSession = Depends(get_db)):
    await db.execute(delete(ChatMessage).where(ChatMessage.session_id == session_id))
    await db.execute(delete(ChatSession).where(ChatSession.id == session_id))
    await db.commit()
    return {"status": "success"}

@router.delete("/sessions")
async def clear_all_sessions(db: AsyncSession = Depends(get_db)):
    await db.execute(delete(ChatMessage))
    await db.execute(delete(ChatSession))
    await db.commit()
    return {"status": "success"}

@router.post("")
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    # 1. Manage Session
    session = None
    if request.session_id:
        result = await db.execute(select(ChatSession).where(ChatSession.id == request.session_id))
        session = result.scalar_one_or_none()

    if not session:
        short_title = request.message[:30] + "..." if len(request.message) > 30 else request.message
        session = ChatSession(title=short_title)
        db.add(session)
        await db.commit()
        await db.refresh(session)

    # 2. Save User Message
    user_msg = ChatMessage(session_id=session.id, role="user", content=request.message)
    db.add(user_msg)
    await db.commit()

    # 3. Load History
    history_result = await db.execute(
        select(ChatMessage).where(ChatMessage.session_id == session.id).order_by(ChatMessage.created_at)
    )
    
    # HISTORY SCRUBBER
    # We strip all hidden tags from the history so the LLM never sees them or tries to mimic them!
    chat_history = []
    for msg in history_result.scalars().all():
        clean_content = msg.content
        if isinstance(clean_content, str):
            clean_content = re.sub(r'<cmd_image_approve>.*?</cmd_image_approve>', '', clean_content, flags=re.DOTALL)
            clean_content = re.sub(r'<cmd_image_track>.*?</cmd_image_track>', '', clean_content, flags=re.DOTALL)
            clean_content = clean_content.strip()
        chat_history.append({"role": msg.role, "content": clean_content})

    # 4. Agent Setup
    agent_config = get_agent(request.mode)
    print(f"Routing to Agent: {agent_config.name}")

    current_prompt_text = request.message
    if request.use_rag and request.mode == "general":
        try:
            rag_results = retriever.search(request.message)
            if rag_results:
                context_str = (
                    "\n\n--- RELEVANT CONTEXT ---\n"
                    + "\n".join([f"[{i+1}] {doc['text'].strip()}" for i, doc in enumerate(rag_results)])
                    + "\n------------------------\n"
                )
                current_prompt_text = context_str + "Question: " + current_prompt_text
        except Exception:
            pass

    if request.image:
        if chat_history and chat_history[-1]["role"] == "user":
            chat_history[-1] = {
                "role": "user",
                "content": [
                    {"type": "text", "text": current_prompt_text},
                    {"type": "image_url", "image_url": {"url": request.image}},
                ],
            }
    else:
        if chat_history and chat_history[-1]["role"] == "user":
            chat_history[-1]["content"] = current_prompt_text

    # 5. Stream Response
    async def iter_response():
        full_response = ""
        
        # HANDLE EXECUTION COMMAND 
        if request.message.startswith("/execute_image"):
            refined_prompt = request.message.replace("/execute_image", "").strip()
            
            # yield "\n\n**Phase 1:** Unloading Brain (Freeing VRAM)...\n"
            llm_manager.unload_model()
            await asyncio.sleep(0.5) 

            # yield "**Phase 2:** Generating Image (Please Wait)...\n"
            comfy_response = comfy_adapter.queue_prompt(refined_prompt)

            if "error" in comfy_response:
                yield f"**Error:** {comfy_response['error']}"
                await llm_manager.initialize() 
            else:
                prompt_id = comfy_response.get("prompt_id")
                yield f"\n\n<cmd_image_track>{prompt_id}</cmd_image_track>\n\n"

                try:
                    await comfy_adapter.wait_for_completion(prompt_id)
                except Exception as e:
                    print(f"Backend waiting error: {e}")

                try:
                    import urllib.request, json
                    print("Forcing ComfyUI to empty VRAM cache...")
                    payload = json.dumps({"unload_models": True, "free_memory": True}).encode("utf-8")
                    req = urllib.request.Request(
                        "[http://127.0.0.1:8188/free](http://127.0.0.1:8188/free)",
                        data=payload,
                        headers={"Content-Type": "application/json"},
                    )
                    urllib.request.urlopen(req)
                    await asyncio.sleep(1.0) 
                except Exception as e:
                    print(f"Cleanup warning: {e}")

                await llm_manager.initialize()
                yield "**Ready:** Generation successful."
            
            async for db_new in get_db():
                ai_msg = ChatMessage(session_id=session.id, role="assistant", content=f"*(User Approved Generation)*\n\n<cmd_image_track>{prompt_id}</cmd_image_track>")
                db_new.add(ai_msg)
                await db_new.commit()
                break
            return 

        # --- NORMAL LLM GENERATION ---
        try:
            async for chunk in llm_manager.stream_chat(chat_history, agent_config=agent_config):
                full_response += chunk
                yield chunk
        except Exception as e:
            yield f"\n[Error: {e}]"
            return

        # INITIAL PROMPT GENERATION
        if request.mode == "image_gen":
            
            match = re.search(r'```(?:[a-zA-Z]+\s*)?(.*?)```', full_response, re.DOTALL)
            
            if match:
                refined_prompt = match.group(1).strip()
            else:
                # Fallback: Strip any hallucinated tags before wrapping
                clean_response = re.sub(r'<cmd_.*?>.*?</cmd_.*?>', '', full_response, flags=re.DOTALL).strip()
                refined_prompt = clean_response 
                
            yield f"\n\n<cmd_image_approve>{refined_prompt}</cmd_image_approve>"
            full_response += f"\n\n<cmd_image_approve>{refined_prompt}</cmd_image_approve>"
        # ----------------------------------------

        if full_response:
            async for db_new in get_db():
                ai_msg = ChatMessage(session_id=session.id, role="assistant", content=full_response)
                db_new.add(ai_msg)
                await db_new.commit()
                break

    response = StreamingResponse(iter_response(), media_type="text/event-stream")
    response.headers["X-Session-ID"] = str(session.id)
    return response