"""
Configuration management for FaceStream backend.
Loads environment variables and provides application settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "FaceStream Recognition System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    
    # Server
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    
    # Database
    DATABASE_URL: Optional[str] = Field(
        default=None,
        description="PostgreSQL database connection URL (required for production)"
    )
    
    def __init__(self, **kwargs):
        """Initialize settings and trim DATABASE_URL if present."""
        super().__init__(**kwargs)
        # Trim whitespace from DATABASE_URL to prevent connection errors
        if self.DATABASE_URL:
            self.DATABASE_URL = self.DATABASE_URL.strip()
    
    # WebSocket Settings
    WS_MAX_CONNECTIONS: int = Field(
        default=100,
        description="Maximum concurrent WebSocket connections"
    )
    WS_HEARTBEAT_INTERVAL: int = Field(
        default=30,
        description="WebSocket heartbeat interval in seconds"
    )
    
    # Face Recognition Settings (for Phase 2)
    FACE_RECOGNITION_MODEL: str = Field(
        default="hog",
        description="Face detection model: 'hog' or 'cnn'"
    )
    FACE_MATCH_THRESHOLD: float = Field(
        default=0.6,
        description="Face matching threshold (lower = more strict)"
    )
    FACE_CONFIDENCE_THRESHOLD: float = Field(
        default=0.85,
        description="Minimum confidence for identification"
    )
    
    # Frame Processing Settings
    MAX_FRAME_RATE: int = Field(
        default=5,
        description="Maximum frames per second to process"
    )
    MIN_FACE_SIZE: int = Field(
        default=100,
        description="Minimum face size in pixels (width or height)"
    )
    OPTIMAL_FACE_SIZE_MIN: int = Field(
        default=150,
        description="Optimal minimum face size for best recognition quality"
    )
    OPTIMAL_FACE_SIZE_MAX: int = Field(
        default=350,
        description="Optimal maximum face size for best recognition quality"
    )
    
    # Security & Authentication
    SECRET_KEY: str = Field(
        default="change-this-secret-key-in-production",
        description="Secret key for JWT/session management"
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )
    ADMIN_PASSWORD: Optional[str] = Field(
        default=None,
        description="Admin password for protected endpoints"
    )
    
    # Redis Cache
    REDIS_URL: Optional[str] = Field(
        default=None,
        description="Redis connection URL (e.g., redis://localhost:6379/0)"
    )
    REDIS_ENABLED: bool = Field(
        default=False,
        description="Enable Redis caching"
    )
    CACHE_TTL: int = Field(
        default=3600,
        description="Cache TTL in seconds (default: 1 hour)"
    )
    
    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR"
    )
    
    # CORS
    CORS_ORIGINS: Optional[str] = Field(
        default=None,
        description="Comma-separated list of allowed CORS origins (e.g., 'https://example.com,https://app.example.com')"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()

