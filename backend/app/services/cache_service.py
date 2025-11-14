"""
Redis caching service for face embeddings and other data.
"""

import json
import numpy as np
from typing import Optional, List
import logging
from app.config import settings

# Optional redis import
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CacheService:
    """Service for Redis caching operations."""
    
    def __init__(self):
        """Initialize cache service."""
        self.enabled = REDIS_AVAILABLE and settings.REDIS_ENABLED and settings.REDIS_URL is not None
        self.ttl = settings.CACHE_TTL
        self.client = None
        
        if not REDIS_AVAILABLE:
            logger.info("Redis not available. Caching disabled.")
            self.enabled = False
            return
        
        if self.enabled:
            try:
                self.client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=False  # We'll handle encoding ourselves
                )
                # Test connection
                self.client.ping()
                logger.info("Redis cache connected successfully")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Caching disabled.")
                self.enabled = False
                self.client = None
        else:
            logger.info("Redis caching disabled (REDIS_ENABLED=False or no REDIS_URL)")
    
    def _encode_embedding(self, embedding: np.ndarray) -> bytes:
        """Encode numpy array to bytes for Redis storage."""
        return embedding.tobytes()
    
    def _decode_embedding(self, data: bytes) -> np.ndarray:
        """Decode bytes from Redis to numpy array."""
        return np.frombuffer(data, dtype=np.float64)
    
    def cache_face_embedding(self, user_id: int, embedding_id: int, embedding: np.ndarray) -> bool:
        """
        Cache a face embedding.
        
        Args:
            user_id: User ID
            embedding_id: Embedding ID
            embedding: Face embedding (128-dim numpy array)
            
        Returns:
            True if cached successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            key = f"face_embedding:{user_id}:{embedding_id}"
            value = self._encode_embedding(embedding)
            self.client.setex(key, self.ttl, value)
            return True
        except Exception as e:
            logger.error(f"Error caching embedding: {e}")
            return False
    
    def get_face_embedding(self, user_id: int, embedding_id: int) -> Optional[np.ndarray]:
        """
        Get cached face embedding.
        
        Args:
            user_id: User ID
            embedding_id: Embedding ID
            
        Returns:
            Cached embedding or None if not found
        """
        if not self.enabled:
            return None
        
        try:
            key = f"face_embedding:{user_id}:{embedding_id}"
            data = self.client.get(key)
            if data:
                return self._decode_embedding(data)
            return None
        except Exception as e:
            logger.error(f"Error getting cached embedding: {e}")
            return None
    
    def cache_user_embeddings(self, user_id: int, embeddings: List[tuple]) -> bool:
        """
        Cache all embeddings for a user.
        
        Args:
            user_id: User ID
            embeddings: List of (embedding_id, embedding) tuples
            
        Returns:
            True if cached successfully
        """
        if not self.enabled:
            return False
        
        try:
            for embedding_id, embedding in embeddings:
                self.cache_face_embedding(user_id, embedding_id, embedding)
            
            # Also cache list of embedding IDs
            embedding_ids = [str(eid) for eid, _ in embeddings]
            list_key = f"user_embeddings:{user_id}"
            self.client.setex(list_key, self.ttl, json.dumps(embedding_ids))
            return True
        except Exception as e:
            logger.error(f"Error caching user embeddings: {e}")
            return False
    
    def invalidate_user_embeddings(self, user_id: int) -> bool:
        """
        Invalidate all cached embeddings for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if invalidated successfully
        """
        if not self.enabled:
            return False
        
        try:
            # Get list of embedding IDs
            list_key = f"user_embeddings:{user_id}"
            ids_json = self.client.get(list_key)
            
            if ids_json:
                embedding_ids = json.loads(ids_json)
                # Delete individual embeddings
                for eid in embedding_ids:
                    key = f"face_embedding:{user_id}:{eid}"
                    self.client.delete(key)
            
            # Delete list
            self.client.delete(list_key)
            return True
        except Exception as e:
            logger.error(f"Error invalidating user embeddings: {e}")
            return False
    
    def cache_recognition_result(self, embedding_hash: str, result: dict, ttl: int = 300) -> bool:
        """
        Cache recognition result for an embedding.
        
        Args:
            embedding_hash: Hash of the embedding
            result: Recognition result dict
            ttl: Time to live in seconds (default: 5 minutes)
            
        Returns:
            True if cached successfully
        """
        if not self.enabled:
            return False
        
        try:
            key = f"recognition:{embedding_hash}"
            value = json.dumps(result)
            self.client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Error caching recognition result: {e}")
            return False
    
    def get_recognition_result(self, embedding_hash: str) -> Optional[dict]:
        """
        Get cached recognition result.
        
        Args:
            embedding_hash: Hash of the embedding
            
        Returns:
            Cached result or None
        """
        if not self.enabled:
            return None
        
        try:
            key = f"recognition:{embedding_hash}"
            data = self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting cached recognition result: {e}")
            return None
    
    def clear_cache(self) -> bool:
        """Clear all cache (use with caution!)."""
        if not self.enabled:
            return False
        
        try:
            self.client.flushdb()
            logger.warning("Cache cleared!")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

