"""
Configuration settings for the Plan Recommendation Engine API
"""

import os
from typing import Optional

class Settings:
    """Application settings"""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./plan_engine.db")
    
    # API Settings
    API_TITLE: str = "Plan Recommendation Engine API"
    API_DESCRIPTION: str = "API for managing venues, areas, and creating personalized plans"
    API_VERSION: str = "1.0.0"
    
    # Server Settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS Settings
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 1000
    
    # Search Settings
    MAX_SEARCH_RESULTS: int = 100
    DEFAULT_SEARCH_RADIUS: float = 5.0  # km
    
    # External API Keys (if needed)
    GOOGLE_PLACES_API_KEY: Optional[str] = os.getenv("GOOGLE_PLACES_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # Cache Settings (if using Redis)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    CACHE_TTL: int = 3600  # 1 hour
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"

# Create global settings instance
settings = Settings()
