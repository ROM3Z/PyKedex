from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://isaac:20861681@localhost:5432/pykedex")

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    echo=True  # Muestra logs SQL (útil para desarrollo)
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    """
    Asynchronous generator that provides a database session for use within a context.
    
    Yields:
        An active asynchronous SQLAlchemy session. The session is automatically closed
        after use, even if an exception occurs.
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()