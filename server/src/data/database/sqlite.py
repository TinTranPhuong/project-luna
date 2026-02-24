from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# ==============================================================================
# DATABASE CONFIGURATION
# ==============================================================================
DATABASE_URL = "sqlite+aiosqlite:///./luna.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  
    future=True
)

# ==============================================================================
# SESSION MANAGEMENT
# ==============================================================================
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass

# ==============================================================================
# DEPENDENCY INJECTION
# ==============================================================================
async def get_db():
    """
    Provides an asynchronous database session for FastAPI routes.
    Ensures the connection is safely closed and returned to the pool 
    after the request completes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()