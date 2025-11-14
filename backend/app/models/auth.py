"""
Authentication models for user roles and sessions.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    """User roles in the system."""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class AuthUser(Base):
    """
    Authentication user model for API access.
    Separate from User model (which represents people being recognized).
    """
    
    __tablename__ = "auth_users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.OPERATOR, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self) -> str:
        return f"<AuthUser(id={self.id}, username='{self.username}', role='{self.role.value}')>"

