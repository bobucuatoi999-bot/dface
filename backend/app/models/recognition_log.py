"""
RecognitionLog model - stores recognition events for analytics and auditing.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class RecognitionLog(Base):
    """
    Recognition log model storing each recognition event.
    
    Records when a person was identified, with confidence scores,
    track IDs, and timestamps for analytics.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User (nullable if unknown person)
        track_id: Track ID assigned during recognition session
        confidence: Confidence score (0.0 to 1.0)
        is_unknown: Whether this was an unknown/unregistered person
        frame_position: Position of face in frame (x, y, width, height)
        session_id: Identifier for the recognition session
        created_at: Timestamp when recognition occurred
        user: Relationship to User model (if identified)
    """
    
    __tablename__ = "recognition_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    track_id = Column(String(50), nullable=True, index=True)  # Track ID from face tracking
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    is_unknown = Column(Boolean, default=False, nullable=False, index=True)
    
    # Frame position (stored as JSON string: "x,y,width,height")
    frame_position = Column(String(100), nullable=True)
    
    # Session identifier (can be used to group recognitions from same session)
    session_id = Column(String(100), nullable=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationship
    user = relationship("User", back_populates="recognition_logs")
    
    def __repr__(self) -> str:
        user_info = f"user_id={self.user_id}" if self.user_id else "unknown"
        return f"<RecognitionLog(id={self.id}, {user_info}, confidence={self.confidence:.2f})>"
    
    def to_dict(self) -> dict:
        """Convert log entry to dictionary representation."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else None,
            "track_id": self.track_id,
            "confidence": round(self.confidence, 4),
            "is_unknown": self.is_unknown,
            "frame_position": self.frame_position,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

