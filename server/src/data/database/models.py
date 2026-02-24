from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from server.src.data.database.sqlite import Base

# ==============================================================================
# ORM MODELS
# ==============================================================================

class ChatSession(Base):
    """
    Represents a single conversation thread.
    Acts as the parent container for multiple chat messages.
    """
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # --- RELATIONSHIPS ---
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete")


class ChatMessage(Base):
    """
    Represents an individual message within a chat session.
    Records the sender role (user, assistant, system) and the text content.
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    
    role = Column(String)  
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # --- RELATIONSHIPS ---
    session = relationship("ChatSession", back_populates="messages")