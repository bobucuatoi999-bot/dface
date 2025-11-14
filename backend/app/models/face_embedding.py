"""
FaceEmbedding model - stores face embeddings (128-dim vectors) for each user.
A user can have multiple embeddings captured from different angles.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, ARRAY, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import List

from app.database import Base


class FaceEmbedding(Base):
    """
    Face embedding model storing 128-dimensional face vectors.
    
    Each user can have multiple embeddings (from different angles/lighting).
    The embedding is a 128-element float array representing the face's
    unique characteristics.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User
        embedding: 128-dimensional float array (face encoding)
        capture_angle: Angle description (e.g., "frontal", "left", "right")
        quality_score: Quality score of the captured face (0-1)
        created_at: Timestamp when embedding was created
        user: Relationship to User model
    """
    
    __tablename__ = "face_embeddings"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Store embedding as ARRAY of floats (128 dimensions)
    # PostgreSQL ARRAY type for efficient storage and querying
    embedding = Column(ARRAY(Float), nullable=False)
    
    capture_angle = Column(String(50), nullable=True)  # "frontal", "left", "right", etc.
    quality_score = Column(Float, nullable=True)  # 0.0 to 1.0
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="face_embeddings")
    
    def __repr__(self) -> str:
        return f"<FaceEmbedding(id={self.id}, user_id={self.user_id}, quality={self.quality_score})>"
    
    def to_dict(self) -> dict:
        """Convert embedding to dictionary representation."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "embedding_length": len(self.embedding) if self.embedding else 0,
            "capture_angle": self.capture_angle,
            "quality_score": self.quality_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @classmethod
    def validate_embedding(cls, embedding: List[float]) -> bool:
        """
        Validate that embedding is correct format (128 dimensions).
        
        Args:
            embedding: List of floats representing face embedding
            
        Returns:
            True if valid, False otherwise
        """
        if not embedding:
            return False
        if len(embedding) != 128:
            return False
        if not all(isinstance(x, (int, float)) for x in embedding):
            return False
        return True

