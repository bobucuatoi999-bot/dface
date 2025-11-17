"""
Face recognition service for extracting embeddings and comparing faces.
Handles face encoding and similarity comparison.
"""

import face_recognition
import numpy as np
from typing import List, Tuple, Optional
import logging

from app.config import settings
from app.database import SessionLocal
from app.models import FaceEmbedding, User
from app.services.cache_service import CacheService
from sqlalchemy.orm import Session
import hashlib

logger = logging.getLogger(__name__)


class FaceRecognitionService:
    """Service for face recognition and comparison."""
    
    def __init__(self):
        """Initialize face recognition service."""
        self.match_threshold = settings.FACE_MATCH_THRESHOLD
        self.confidence_threshold = settings.FACE_CONFIDENCE_THRESHOLD
        self.cache_service = CacheService()
        logger.info(f"Face recognition service initialized (threshold: {self.match_threshold}, cache: {self.cache_service.enabled})")
    
    def extract_embedding(self, image: np.ndarray, face_location: Optional[Tuple[int, int, int, int]] = None) -> Optional[np.ndarray]:
        """
        Extract 128-dimensional face embedding from image.
        
        Args:
            image: numpy array representing image (RGB format)
            face_location: Optional tuple (top, right, bottom, left) of face location
            
        Returns:
            128-dimensional numpy array (face encoding) or None if face not found
        """
        try:
            if face_location:
                # Extract embedding for specific face location
                encodings = face_recognition.face_encodings(image, [face_location])
            else:
                # Extract embedding for first face found
                encodings = face_recognition.face_encodings(image)
            
            if len(encodings) > 0:
                return encodings[0]  # Return first encoding (128-dim array)
            else:
                logger.warning("No face encoding found in image")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting face embedding: {e}")
            return None
    
    def extract_multiple_embeddings(self, image: np.ndarray, face_locations: List[Tuple[int, int, int, int]]) -> List[np.ndarray]:
        """
        Extract embeddings for multiple faces.
        
        Args:
            image: numpy array representing image
            face_locations: List of face location tuples
            
        Returns:
            List of 128-dimensional embeddings
        """
        try:
            encodings = face_recognition.face_encodings(image, face_locations)
            return encodings
        except Exception as e:
            logger.error(f"Error extracting multiple embeddings: {e}")
            return []
    
    def compare_faces(self, known_encoding: np.ndarray, unknown_encoding: np.ndarray) -> Tuple[bool, float]:
        """
        Compare two face embeddings using a weighted distance + improved confidence.
        
        Args:
            known_encoding: Known face embedding (128-dim)
            unknown_encoding: Unknown face embedding (128-dim)
            
        Returns:
            Tuple of (is_match: bool, confidence: float)
        """
        try:
            # Euclidean distance (lower = more similar)
            euclidean_distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
            
            # Cosine distance (converted from similarity)
            known_norm = np.linalg.norm(known_encoding)
            unknown_norm = np.linalg.norm(unknown_encoding)
            if known_norm > 0 and unknown_norm > 0:
                known_normalized = known_encoding / known_norm
                unknown_normalized = unknown_encoding / unknown_norm
                cosine_similarity = np.dot(known_normalized, unknown_normalized)
                cosine_distance = (1.0 - cosine_similarity) / 2.0
                combined_distance = (0.7 * euclidean_distance) + (0.3 * cosine_distance)
            else:
                cosine_distance = None
                combined_distance = euclidean_distance
            
            is_match = combined_distance <= self.match_threshold
            
            # Improved confidence curve (sigmoid-like)
            if combined_distance < 0.3:
                confidence = 0.95 + (0.05 * (0.3 - combined_distance) / 0.3)
            elif combined_distance < 0.5:
                confidence = 0.80 + (0.15 * (0.5 - combined_distance) / 0.2)
            elif combined_distance < self.match_threshold:
                confidence = 0.70 + (0.10 * (self.match_threshold - combined_distance) / (self.match_threshold - 0.5))
            else:
                confidence = max(0.0, 0.70 - (combined_distance - self.match_threshold) / self.match_threshold)
            
            confidence = max(0.0, min(1.0, confidence))
            
            if cosine_distance is not None:
                logger.debug(
                    f"Face comparison: euclidean={euclidean_distance:.4f}, "
                    f"cosine={cosine_distance:.4f}, combined={combined_distance:.4f}, "
                    f"match={is_match}, confidence={confidence:.4f}"
                )
            else:
                logger.debug(
                    f"Face comparison: euclidean={euclidean_distance:.4f}, "
                    f"combined={combined_distance:.4f}, match={is_match}, confidence={confidence:.4f}"
                )
            
            return is_match, confidence
            
        except Exception as e:
            logger.error(f"Error comparing faces: {e}")
            return False, 0.0
    
    def find_best_match(self, unknown_encoding: np.ndarray, db: Session) -> Optional[Tuple[User, float]]:
        """
        Find best matching user in database for given face encoding.
        Uses Redis cache if available for faster lookups.
        
        Args:
            unknown_encoding: Face embedding to match (128-dim numpy array)
            db: Database session
            
        Returns:
            Tuple of (User, confidence) if match found, None otherwise
        """
        try:
            # Check cache first
            embedding_hash = self._get_embedding_hash(unknown_encoding)
            cached_result = self.cache_service.get_recognition_result(embedding_hash)
            if cached_result:
                logger.debug("Using cached recognition result")
                # Reconstruct user from cached data
                user = db.query(User).filter(User.id == cached_result["user_id"]).first()
                if user and user.is_active:
                    return (user, cached_result["confidence"])
            
            # Get all face embeddings from database
            embeddings = db.query(FaceEmbedding).join(User).filter(User.is_active == True).all()
            
            if not embeddings:
                logger.debug("No embeddings in database")
                return None
            
            best_match = None
            best_confidence = 0.0
            best_embedding_id = None
            
            # Enhanced matching: Try all embeddings for each user and use best one
            # This improves accuracy by comparing against multiple angles
            user_confidence_map = {}  # Track best confidence per user
            
            for embedding in embeddings:
                # Try cache first
                cached_emb = self.cache_service.get_face_embedding(embedding.user_id, embedding.id)
                if cached_emb is not None:
                    known_encoding = cached_emb
                else:
                    # Convert database array to numpy array
                    known_encoding = np.array(embedding.embedding)
                    # Cache it for next time
                    self.cache_service.cache_face_embedding(
                        embedding.user_id, 
                        embedding.id, 
                        known_encoding
                    )
                
                # Compare faces
                is_match, confidence = self.compare_faces(known_encoding, unknown_encoding)
                
                # For each user, keep track of the best confidence across all their embeddings
                if is_match:
                    user_id = embedding.user_id
                    if user_id not in user_confidence_map:
                        user_confidence_map[user_id] = {
                            "user": embedding.user,
                            "best_confidence": confidence,
                            "best_embedding_id": embedding.id
                        }
                    else:
                        # Update if this embedding has better confidence
                        if confidence > user_confidence_map[user_id]["best_confidence"]:
                            user_confidence_map[user_id]["best_confidence"] = confidence
                            user_confidence_map[user_id]["best_embedding_id"] = embedding.id
            
            # Find the user with the highest confidence
            for user_id, user_data in user_confidence_map.items():
                if user_data["best_confidence"] > best_confidence:
                    best_match = user_data["user"]
                    best_confidence = user_data["best_confidence"]
                    best_embedding_id = user_data["best_embedding_id"]
            
            # Check if best match meets confidence threshold
            if best_match and best_confidence >= self.confidence_threshold:
                logger.info(f"Found match: {best_match.name} (confidence: {best_confidence:.2f})")
                
                # Cache the result
                self.cache_service.cache_recognition_result(
                    embedding_hash,
                    {
                        "user_id": best_match.id,
                        "user_name": best_match.name,
                        "confidence": best_confidence,
                        "embedding_id": best_embedding_id
                    }
                )
                
                return (best_match, best_confidence)
            else:
                if best_match:
                    logger.debug(f"Best match {best_match.name} below confidence threshold ({best_confidence:.2f} < {self.confidence_threshold})")
                return None
                
        except Exception as e:
            logger.error(f"Error finding best match: {e}")
            return None
    
    def find_all_matches(self, unknown_encoding: np.ndarray, db: Session, 
                        top_k: int = 5) -> List[Tuple[User, float]]:
        """
        Find top K matching users in database.
        
        Args:
            unknown_encoding: Face embedding to match
            db: Database session
            top_k: Number of top matches to return
            
        Returns:
            List of tuples (User, confidence) sorted by confidence (descending)
        """
        try:
            embeddings = db.query(FaceEmbedding).join(User).filter(User.is_active == True).all()
            
            if not embeddings:
                return []
            
            matches = []
            
            # Compare with all embeddings
            for embedding in embeddings:
                known_encoding = np.array(embedding.embedding)
                is_match, confidence = self.compare_faces(known_encoding, unknown_encoding)
                
                if is_match:
                    matches.append((embedding.user, confidence))
            
            # Sort by confidence (descending) and return top K
            matches.sort(key=lambda x: x[1], reverse=True)
            return matches[:top_k]
            
        except Exception as e:
            logger.error(f"Error finding all matches: {e}")
            return []

