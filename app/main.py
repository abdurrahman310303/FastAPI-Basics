from fastapi import FastAPI
from datetime import datetime

from .routers import items, categories, search
from .database.database import create_tables
from .core.config import settings

# Create database tables on startup
create_tables()

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version
)

# Include routers
app.include_router(items.router)
app.include_router(categories.router)
app.include_router(search.router)

@app.get('/', response_model=dict)
def read_root():
    return {
        "Hello": "This is my first FastAPI Practice with SQLite Database",
        "Version": settings.app_version,
        "database": "SQLite",
        "endpoints": {
            "docs": "/docs",
            "items": "/items/",
            "health": "/health"
        }
    }

@app.get("/health", response_model=dict)
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "database": "SQLite Connected",
        "version": settings.app_version
    }