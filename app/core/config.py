from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = "FastAPI Learning Project"
    app_description: str = "A comprehensive FastAPI Project"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Database settings - using SQLite for easy setup
    database_url: str = Field(
        default="sqlite:///./fastapi_items.db",
        description="Database URL"
    )
    
    class Config:
        env_file = ".env"

settings = Settings()
