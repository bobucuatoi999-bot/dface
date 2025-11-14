"""
User service for database operations related to users and face embeddings.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
import numpy as np
import logging

from app.models import User, FaceEmbedding, RecognitionLog
from app.services.cache_service import CacheService

# Optional face recognition import
try:
    from app.services.face_recognition import FaceRecognitionService
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FaceRecognitionService = None
    FACE_RECOGNITION_AVAILABLE = False

logger = logging.getLogger(__name__)


class UserService:
    """Service for user and face embedding management."""
    
    def __init__(self):
        """Initialize user service."""
        if FACE_RECOGNITION_AVAILABLE:
            self.face_recognition_service = FaceRecognitionService()
        else:
            self.face_recognition_service = None
        self.cache_service = CacheService()
    
    def create_user(self, db: Session, name: str, email: Optional[str] = None,
                   employee_id: Optional[str] = None, extra_data: Optional[str] = None) -> User:
        """
        Create a new user.
        
        Args:
            db: Database session
            name: User's full name
            email: Email address (optional)
            employee_id: Employee ID (optional)
            extra_data: Additional JSON data (optional)
            
        Returns:
            Created User object
        """
        user = User(
            name=name,
            email=email,
            employee_id=employee_id,
            extra_data=extra_data,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"Created user: {user.name} (ID: {user.id})")
        return user
    
    def add_face_embedding(self, db: Session, user_id: int, embedding: np.ndarray,
                          capture_angle: Optional[str] = None,
                          quality_score: Optional[float] = None) -> FaceEmbedding:
        """
        Add a face embedding for a user.
        
        Args:
            db: Database session
            user_id: User ID
            embedding: 128-dimensional face embedding
            capture_angle: Angle description (optional)
            quality_score: Quality score 0-1 (optional)
            
        Returns:
            Created FaceEmbedding object
        """
        # Convert numpy array to list for database storage
        embedding_list = embedding.tolist()
        
        face_embedding = FaceEmbedding(
            user_id=user_id,
            embedding=embedding_list,
            capture_angle=capture_angle,
            quality_score=quality_score
        )
        
        db.add(face_embedding)
        db.commit()
        db.refresh(face_embedding)
        
        # Cache the embedding
        self.cache_service.cache_face_embedding(user_id, face_embedding.id, embedding)
        
        logger.info(f"Added face embedding for user ID {user_id}")
        return face_embedding
    
    def get_user(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    def get_all_users(self, db: Session, active_only: bool = True) -> List[User]:
        """Get all users."""
        query = db.query(User)
        if active_only:
            query = query.filter(User.is_active == True)
        return query.all()
    
    def delete_user(self, db: Session, user_id: int) -> bool:
        """
        Delete a user and all associated data.
        
        Args:
            db: Database session
            user_id: User ID to delete
            
        Returns:
            True if deleted, False if user not found
        """
        user = self.get_user(db, user_id)
        if not user:
            return False
        
        db.delete(user)
        db.commit()
        
        # Invalidate cache
        self.cache_service.invalidate_user_embeddings(user_id)
        
        logger.info(f"Deleted user: {user.name} (ID: {user_id})")
        return True
    
    def check_duplicate(self, db: Session, embedding: np.ndarray) -> Optional[User]:
        """
        Check if face embedding already exists (duplicate detection).
        
        Args:
            db: Database session
            embedding: Face embedding to check
            
        Returns:
            User if duplicate found, None otherwise
        """
        if not FACE_RECOGNITION_AVAILABLE or not self.face_recognition_service:
            return None  # Cannot check duplicates without face recognition
        
        match = self.face_recognition_service.find_best_match(embedding, db)
        if match:
            user, confidence = match
            # Use higher threshold for duplicate detection
            if confidence > 0.9:  # Very high confidence for duplicates
                return user
        return None
    
    def create_recognition_log(self, db: Session, user_id: Optional[int], track_id: Optional[str],
                              confidence: float, is_unknown: bool, frame_position: Optional[str] = None,
                              session_id: Optional[str] = None) -> RecognitionLog:
        """
        Create a recognition log entry.
        
        Args:
            db: Database session
            user_id: User ID (None if unknown)
            track_id: Track ID
            confidence: Confidence score
            is_unknown: Whether person is unknown
            frame_position: Face position in frame
            session_id: Session identifier
            
        Returns:
            Created RecognitionLog object
        """
        log = RecognitionLog(
            user_id=user_id,
            track_id=track_id,
            confidence=confidence,
            is_unknown=is_unknown,
            frame_position=frame_position,
            session_id=session_id
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        
        return log

