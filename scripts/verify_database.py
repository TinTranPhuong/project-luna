import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.src.data.database.sqlite import AsyncSessionLocal, engine, Base
from server.src.data.database.models import ChatSession, ChatMessage
from sqlalchemy import select

async def main():
    print("💾 Testing Database Connection...")
    
    async with AsyncSessionLocal() as session:
        # 1. Create a new Chat Session
        new_chat = ChatSession(title="Test Conversation")
        session.add(new_chat)
        await session.commit()
        await session.refresh(new_chat)
        print(f"✅ Created Chat Session ID: {new_chat.id}")

        # 2. Add a Message to it
        msg = ChatMessage(
            session_id=new_chat.id,
            role="user",
            content="Hello, do you remember me?"
        )
        session.add(msg)
        await session.commit()
        print("✅ Saved Message to Database")

        # 3. Read it back
        result = await session.execute(select(ChatMessage).where(ChatMessage.session_id == new_chat.id))
        messages = result.scalars().all()
        
        print(f"\n📖 Reading from Memory:")
        for m in messages:
            print(f"   [{m.role}]: {m.content}")

    print("\n🎉 Database Test PASSED!")

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Error: {e}")