from fastapi import FastAPI
from datetime import datetime

from .routers import items, categories, search
from .database.fake_db import fake_items_db
from .core.config import settings

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
        "Hello": "This is my first FastAPI Practice",
        "Version": settings.app_version,
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
        "total_items": len(fake_items_db.items_db)
    }