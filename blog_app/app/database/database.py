from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.config import settings

# Create async engine for asyncpg
async_engine = create_async_engine(settings.database_url)

# Create sync engine for migrations
sync_engine = create_engine(settings.database_url.replace("+asyncpg", ""))

# Create AsyncSession class
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

# Create sync SessionLocal for migrations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Create Base class
Base = declarative_base()

# Dependency to get async DB session
async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Dependency to get sync DB session (for migrations)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
