from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# 1. The Connection String (Creates 'luna.db' in project root)
DATABASE_URL = "sqlite+aiosqlite:///./luna.db"

# 2. The Engine (Connection Manager)
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set True to debug SQL queries
    future=True
)

# 3. Session Factory (Creates new DB sessions)
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 4. The ORM Base Class
class Base(DeclarativeBase):
    pass

# 5. Dependency for FastAPI (to be imported in api/deps.py later)
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()