"""
Face tracking service for maintaining Track IDs across frames.
Tracks faces as they move through video frames.
"""

from typing import Dict, Tuple, Optional, List
import numpy as np
from datetime import datetime, timedelta
import logging

from app.services.face_recognition import FaceRecognitionService

logger = logging.getLogger(__name__)


class FaceTrack:
    """Represents a tracked face across multiple frames."""
    
    def __init__(self, track_id: str, face_encoding: np.ndarray, bbox: Tuple[int, int, int, int], 
                 user_id: Optional[int] = None, user_name: Optional[str] = None, 
                 confidence: float = 0.0):
        """
        Initialize a face track.
        
        Args:
            track_id: Unique track identifier
            face_encoding: Face embedding (128-dim)
            bbox: Bounding box (top, right, bottom, left)
            user_id: Identified user ID (if known)
            user_name: Identified user name (if known)
            confidence: Recognition confidence
        """
        self.track_id = track_id
        self.face_encoding = face_encoding
        self.bbox = bbox
        self.user_id = user_id
        self.user_name = user_name
        self.confidence = confidence
        self.first_seen = datetime.now()
        self.last_seen = datetime.now()
        self.frame_count = 1
        self.is_lost = False
    
    def update(self, bbox: Tuple[int, int, int, int], user_id: Optional[int] = None,
               user_name: Optional[str] = None, confidence: float = 0.0):
        """Update track with new detection."""
        self.bbox = bbox
        self.last_seen = datetime.now()
        self.frame_count += 1
        self.is_lost = False
        
        # Update identity if provided
        if user_id is not None:
            self.user_id = user_id
            self.user_name = user_name
            self.confidence = confidence
    
    def mark_lost(self):
        """Mark track as lost (face disappeared)."""
        self.is_lost = True
    
    def get_age_seconds(self) -> float:
        """Get age of track in seconds."""
        return (datetime.now() - self.first_seen).total_seconds()
    
    def get_time_since_last_seen(self) -> float:
        """Get seconds since last update."""
        return (datetime.now() - self.last_seen).total_seconds()


class FaceTrackingService:
    """Service for tracking faces across video frames."""
    
    def __init__(self, max_track_age_seconds: float = 6.0, 
                 max_time_since_last_seen: float = 1.0,
                 iou_threshold: float = 0.3):
        """
        Initialize face tracking service.
        
        Args:
            max_track_age_seconds: Maximum age of a track before removal
            max_time_since_last_seen: Max seconds without update before marking as lost
            iou_threshold: IoU threshold for matching bboxes (0.0 to 1.0)
        """
        self.tracks: Dict[str, FaceTrack] = {}
        self.next_track_id = 1
        self.max_track_age = max_track_age_seconds
        self.max_time_since_last_seen = max_time_since_last_seen
        self.iou_threshold = iou_threshold
        self.face_recognition_service = FaceRecognitionService()
        logger.info("Face tracking service initialized")
    
    def _calculate_iou(self, bbox1: Tuple[int, int, int, int], bbox2: Tuple[int, int, int, int]) -> float:
        """
        Calculate Intersection over Union (IoU) of two bounding boxes.
        
        Args:
            bbox1: (top, right, bottom, left)
            bbox2: (top, right, bottom, left)
            
        Returns:
            IoU value between 0.0 and 1.0
        """
        top1, right1, bottom1, left1 = bbox1
        top2, right2, bottom2, left2 = bbox2
        
        # Calculate intersection
        inter_top = max(top1, top2)
        inter_left = max(left1, left2)
        inter_bottom = min(bottom1, bottom2)
        inter_right = min(right1, right2)
        
        if inter_bottom <= inter_top or inter_right <= inter_left:
            return 0.0
        
        inter_area = (inter_bottom - inter_top) * (inter_right - inter_left)
        
        # Calculate union
        area1 = (bottom1 - top1) * (right1 - left1)
        area2 = (bottom2 - top2) * (right2 - left2)
        union_area = area1 + area2 - inter_area
        
        if union_area == 0:
            return 0.0
        
        return inter_area / union_area
    
    def _calculate_encoding_distance(self, encoding1: np.ndarray, encoding2: np.ndarray) -> float:
        """Calculate Euclidean distance between two face encodings."""
        return np.linalg.norm(encoding1 - encoding2)
    
    def update_tracks(self, face_locations: List[Tuple[int, int, int, int]], 
                     face_encodings: List[np.ndarray],
                     recognized_users: Optional[List[Tuple[Optional[int], Optional[str], float]]] = None) -> List[FaceTrack]:
        """
        Update tracks with new detections.
        
        Args:
            face_locations: List of face bounding boxes
            face_encodings: List of face embeddings
            recognized_users: Optional list of (user_id, user_name, confidence) for each face
            
        Returns:
            List of active FaceTrack objects
        """
        if recognized_users is None:
            recognized_users = [None] * len(face_locations)
        
        # Mark all existing tracks as potentially lost
        for track in self.tracks.values():
            track.mark_lost()
        
        # Match new detections to existing tracks
        matched_tracks = set()
        
        for i, (bbox, encoding) in enumerate(zip(face_locations, face_encodings)):
            best_track = None
            best_score = 0.0
            
            # Find best matching track
            for track_id, track in self.tracks.items():
                if track.is_lost:
                    continue
                
                # Calculate IoU
                iou = self._calculate_iou(bbox, track.bbox)
                
                # Calculate encoding distance
                encoding_dist = self._calculate_encoding_distance(encoding, track.face_encoding)
                encoding_similarity = 1.0 / (1.0 + encoding_dist)  # Convert distance to similarity
                
                # Combined score (weighted)
                score = (iou * 0.6) + (encoding_similarity * 0.4)
                
                if score > best_score and score > self.iou_threshold:
                    best_score = score
                    best_track = track
            
            # Update or create track
            if best_track:
                # Update existing track
                user_info = recognized_users[i] if i < len(recognized_users) else None
                if user_info:
                    user_id, user_name, confidence = user_info
                    best_track.update(bbox, user_id, user_name, confidence)
                else:
                    best_track.update(bbox)
                matched_tracks.add(best_track.track_id)
            else:
                # Create new track
                track_id = f"{self.next_track_id}"
                self.next_track_id += 1
                
                user_info = recognized_users[i] if i < len(recognized_users) else None
                if user_info:
                    user_id, user_name, confidence = user_info
                else:
                    user_id, user_name, confidence = None, None, 0.0
                
                track = FaceTrack(track_id, encoding, bbox, user_id, user_name, confidence)
                self.tracks[track_id] = track
                matched_tracks.add(track_id)
        
        # Clean up old tracks
        self._cleanup_tracks()
        
        # Return active tracks
        return [track for track in self.tracks.values() if not track.is_lost]
    
    def _cleanup_tracks(self):
        """Remove old or lost tracks."""
        tracks_to_remove = []
        now = datetime.now()
        
        for track_id, track in self.tracks.items():
            age = track.get_age_seconds()
            time_since_seen = track.get_time_since_last_seen()
            
            # Remove if too old or lost for too long
            if age > self.max_track_age or (track.is_lost and time_since_seen > self.max_time_since_last_seen):
                tracks_to_remove.append(track_id)
        
        for track_id in tracks_to_remove:
            del self.tracks[track_id]
            logger.debug(f"Removed track {track_id}")
    
    def get_active_tracks(self) -> List[FaceTrack]:
        """Get all currently active tracks."""
        self._cleanup_tracks()
        return [track for track in self.tracks.values() if not track.is_lost]
    
    def reset(self):
        """Reset all tracks (for new session)."""
        self.tracks.clear()
        self.next_track_id = 1
        logger.info("Face tracking reset")

