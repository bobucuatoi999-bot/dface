"""
Face detection service using face_recognition library.
Detects faces in images and returns their locations.
"""

import face_recognition
import numpy as np
from typing import List, Tuple, Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class FaceDetectionService:
    """Service for detecting faces in images."""
    
    def __init__(self):
        """Initialize face detection service."""
        self.model = settings.FACE_RECOGNITION_MODEL  # 'hog' or 'cnn'
        logger.info(f"Face detection service initialized with model: {self.model}")
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect all faces in an image.
        
        Args:
            image: numpy array representing image (RGB format)
            
        Returns:
            List of face locations as tuples (top, right, bottom, left)
        """
        try:
            # Validate image input
            if image is None or image.size == 0:
                logger.warning("Empty or None image provided for face detection")
                return []
            
            # Log image properties for debugging
            height, width = image.shape[:2] if len(image.shape) >= 2 else (0, 0)
            logger.debug(f"Face detection: image shape={image.shape}, size={width}x{height}, dtype={image.dtype}")
            
            # face_recognition uses RGB format
            # Increase upsampling from 1 to 2 for better detection of smaller faces
            # number_of_times_to_upsample=2 means we'll detect faces that are 2x smaller
            # This improves reliability but is slightly slower (acceptable trade-off)
            face_locations = face_recognition.face_locations(
                image,
                model=self.model,
                number_of_times_to_upsample=2  # Enhanced: increased from 1 to 2 for better detection
            )
            
            # Log detection results
            if face_locations:
                logger.info(f"✅ Detected {len(face_locations)} face(s) in image ({width}x{height})")
                # Log face sizes for debugging
                for i, (top, right, bottom, left) in enumerate(face_locations):
                    face_width = right - left
                    face_height = bottom - top
                    logger.debug(f"  Face {i+1}: {face_width}x{face_height}px at ({left}, {top})")
            else:
                logger.debug(f"⚠️ No faces detected in image ({width}x{height}), model={self.model}, upsampling=2")
            
            return face_locations
            
        except Exception as e:
            logger.error(f"Error detecting faces: {e}", exc_info=True)
            return []
    
    def detect_faces_with_landmarks(self, image: np.ndarray) -> Tuple[List[Tuple[int, int, int, int]], List]:
        """
        Detect faces and their facial landmarks.
        
        Args:
            image: numpy array representing image (RGB format)
            
        Returns:
            Tuple of (face_locations, face_landmarks_list)
        """
        try:
            face_locations = self.detect_faces(image)
            face_landmarks = face_recognition.face_landmarks(image, face_locations)
            
            return face_locations, face_landmarks
            
        except Exception as e:
            logger.error(f"Error detecting faces with landmarks: {e}")
            return [], []
    
    def count_faces(self, image: np.ndarray) -> int:
        """
        Count number of faces in image.
        
        Args:
            image: numpy array representing image
            
        Returns:
            Number of faces detected
        """
        return len(self.detect_faces(image))
    
    def is_face_present(self, image: np.ndarray) -> bool:
        """
        Check if at least one face is present in image.
        
        Args:
            image: numpy array representing image
            
        Returns:
            True if face detected, False otherwise
        """
        return self.count_faces(image) > 0

