from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, posts, users
from app.database.database import async_engine
from app.models.models import Base
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Create FastAPI app
app = FastAPI(
    title="Blog API",
    description="A complete blog application with authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(users.router)

async def create_database_if_not_exists():
    """Create database if it doesn't exist."""
    try:
        # Try to connect to the blog_db database
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except OperationalError:
        # Database doesn't exist, create it
        print("Database doesn't exist. Creating blog_db...")
        # Connect to default postgres database to create our database
        temp_engine = create_engine("postgresql://apple@localhost/postgres")
        with temp_engine.connect() as conn:
            conn.execute(text("COMMIT"))  # End any transaction
            conn.execute(text("CREATE DATABASE blog_db"))
        temp_engine.dispose()
        print("Database blog_db created successfully!")

@app.on_event("startup")
async def startup_event():
    """Create database and tables on startup."""
    await create_database_if_not_exists()
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Blog API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
