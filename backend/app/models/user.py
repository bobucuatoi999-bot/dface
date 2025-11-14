"""
User model - stores registered users in the system.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.database import Base


class User(Base):
    """
    User model representing a registered person in the system.
    
    Attributes:
        id: Primary key, auto-incrementing user ID
        name: Full name of the user
        email: Email address (optional)
        employee_id: Employee/ID number (optional)
        metadata: Additional JSON metadata (optional)
        is_active: Whether the user is active in the system
        created_at: Timestamp when user was registered
        updated_at: Timestamp when user was last updated
        face_embeddings: Relationship to FaceEmbedding records
        recognition_logs: Relationship to RecognitionLog records
    """
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    employee_id = Column(String(100), nullable=True, index=True)
    extra_data = Column(Text, nullable=True)  # JSON string for additional data (renamed from metadata - reserved keyword)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    face_embeddings = relationship(
        "FaceEmbedding",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    recognition_logs = relationship(
        "RecognitionLog",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"
    
    def to_dict(self) -> dict:
        """Convert user to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "employee_id": self.employee_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "face_count": len(self.face_embeddings) if self.face_embeddings else 0,
        }

