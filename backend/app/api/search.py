"""
API endpoints for face similarity search and advanced features.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import numpy as np

from app.database import get_db
# Optional face recognition import
try:
    from app.services.face_recognition import FaceRecognitionService
    from app.utils.image_processing import decode_base64_image
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FaceRecognitionService = None
    decode_base64_image = None
    FACE_RECOGNITION_AVAILABLE = False
from app.services.user_service import UserService
from app.models import User, FaceEmbedding

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/search", tags=["search"])

if FACE_RECOGNITION_AVAILABLE:
    face_recognition_service = FaceRecognitionService()
else:
    face_recognition_service = None
user_service = UserService()


@router.get("/similar", response_model=List[dict])
async def find_similar_faces(
    image_data: str = Query(..., description="Base64 encoded image"),
    threshold: float = Query(0.6, ge=0.0, le=1.0, description="Similarity threshold"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """
    Find faces similar to the provided image.
    
    Returns a list of users whose faces are similar to the input image,
    sorted by similarity (most similar first).
    """
    try:
        # Decode image
        image = decode_base64_image(image_data)
        
        # Extract embedding
        embedding = face_recognition_service.extract_embedding(image)
        if embedding is None:
            raise HTTPException(
                status_code=400,
                detail="No face detected in image or could not extract embedding"
            )
        
        # Find all matches
        matches = face_recognition_service.find_all_matches(embedding, db, top_k=limit)
        
        # Filter by threshold and format results
        results = []
        for user, confidence in matches:
            if confidence >= threshold:
                results.append({
                    "user_id": user.id,
                    "user_name": user.name,
                    "email": user.email,
                    "similarity": round(confidence, 4),
                    "confidence": round(confidence, 4)
                })
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding similar faces: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error finding similar faces: {str(e)}"
        )


@router.get("/unknown-group", response_model=List[dict])
async def group_unknown_faces(
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    threshold: float = Query(0.7, ge=0.0, le=1.0, description="Grouping similarity threshold"),
    db: Session = Depends(get_db)
):
    """
    Group unknown faces that appear similar (potential same person).
    
    This helps identify when the same unknown person appears multiple times
    across different recognition events.
    """
    try:
        from app.models import RecognitionLog
        from collections import defaultdict
        
        # Get all unknown recognition logs
        query = db.query(RecognitionLog).filter(RecognitionLog.is_unknown == True)
        if session_id:
            query = query.filter(RecognitionLog.session_id == session_id)
        
        unknown_logs = query.all()
        
        if not unknown_logs:
            return []
        
        # Note: This is a simplified version. In a full implementation,
        # you would store embeddings for unknown faces and compare them.
        # For now, we'll group by track_id and frame_position similarity
        
        # Group by track_id (same track = same person)
        groups = defaultdict(list)
        for log in unknown_logs:
            if log.track_id:
                groups[log.track_id].append({
                    "log_id": log.id,
                    "track_id": log.track_id,
                    "frame_position": log.frame_position,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                    "session_id": log.session_id
                })
        
        # Format results
        result = []
        for track_id, logs in groups.items():
            if len(logs) > 1:  # Only groups with multiple occurrences
                result.append({
                    "group_id": track_id,
                    "occurrence_count": len(logs),
                    "first_seen": min(log["created_at"] for log in logs if log["created_at"]),
                    "last_seen": max(log["created_at"] for log in logs if log["created_at"]),
                    "occurrences": logs
                })
        
        return result
        
    except Exception as e:
        logger.error(f"Error grouping unknown faces: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error grouping unknown faces: {str(e)}"
        )


@router.post("/compare", response_model=dict)
async def compare_two_faces(
    image1_data: str = Query(..., description="Base64 encoded first image"),
    image2_data: str = Query(..., description="Base64 encoded second image"),
    db: Session = Depends(get_db)
):
    """
    Compare two face images and return similarity score.
    
    Useful for verifying if two images show the same person.
    """
    try:
        # Decode both images
        image1 = decode_base64_image(image1_data)
        image2 = decode_base64_image(image2_data)
        
        # Extract embeddings
        embedding1 = face_recognition_service.extract_embedding(image1)
        embedding2 = face_recognition_service.extract_embedding(image2)
        
        if embedding1 is None:
            raise HTTPException(status_code=400, detail="No face detected in first image")
        if embedding2 is None:
            raise HTTPException(status_code=400, detail="No face detected in second image")
        
        # Compare faces
        is_match, confidence = face_recognition_service.compare_faces(embedding1, embedding2)
        
        return {
            "is_match": is_match,
            "similarity": round(confidence, 4),
            "confidence": round(confidence, 4),
            "threshold": face_recognition_service.match_threshold
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing faces: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error comparing faces: {str(e)}"
        )

