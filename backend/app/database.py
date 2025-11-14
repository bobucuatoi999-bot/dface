"""
Database connection and session management.
Uses SQLAlchemy for PostgreSQL database operations.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import sys

from app.config import settings

# Validate DATABASE_URL before creating engine
if not settings.DATABASE_URL:
    error_msg = """
    ERROR: DATABASE_URL environment variable is not set!
    
    Please set DATABASE_URL in your environment variables or .env file.
    
    For Railway deployment:
    1. Add a PostgreSQL service to your Railway project
    2. Railway will automatically inject DATABASE_URL
    3. Or manually set: DATABASE_URL=${{Postgres.DATABASE_URL}}
    
    For local development:
    DATABASE_URL=postgresql://user:password@localhost:5432/dbname
    
    Example:
    DATABASE_URL=postgresql://postgres:password@localhost:5432/facestream
    """
    print(error_msg, file=sys.stderr)
    sys.exit(1)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,  # Connection pool size
    max_overflow=20,  # Max connections beyond pool_size
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get database session.
    Yields a database session and closes it after use.
    
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database by creating all tables.
    Call this after defining all models.
    """
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    Drop all database tables.
    Use with caution - only for development/testing!
    """
    Base.metadata.drop_all(bind=engine)

