"""
REST API endpoints for recognition logs.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
import logging

from app.database import get_db
from app.schemas.recognition_log import RecognitionLogResponse, RecognitionLogFilter
from app.models import RecognitionLog, User
from app.api.auth import get_current_user
from app.models.auth import AuthUser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("/", response_model=List[RecognitionLogResponse])
async def get_recognition_logs(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    is_unknown: Optional[bool] = Query(None, description="Filter by unknown status"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum confidence"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Get recognition logs with optional filters.
    
    Supports filtering by:
    - user_id: Specific user
    - session_id: Specific session
    - is_unknown: Unknown vs recognized
    - start_date/end_date: Time range
    - min_confidence: Minimum confidence score
    
    Results are ordered by created_at (newest first).
    """
    try:
        query = db.query(RecognitionLog)
        
        # Apply filters
        if user_id is not None:
            query = query.filter(RecognitionLog.user_id == user_id)
        
        if session_id is not None:
            query = query.filter(RecognitionLog.session_id == session_id)
        
        if is_unknown is not None:
            query = query.filter(RecognitionLog.is_unknown == is_unknown)
        
        if start_date is not None:
            query = query.filter(RecognitionLog.created_at >= start_date)
        
        if end_date is not None:
            query = query.filter(RecognitionLog.created_at <= end_date)
        
        if min_confidence is not None:
            query = query.filter(RecognitionLog.confidence >= min_confidence)
        
        # Order by created_at (newest first) and apply pagination
        query = query.order_by(RecognitionLog.created_at.desc())
        logs = query.offset(offset).limit(limit).all()
        
        # Convert to response format
        result = []
        for log in logs:
            log_dict = log.to_dict()
            result.append(RecognitionLogResponse(**log_dict))
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting recognition logs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting recognition logs: {str(e)}"
        )


@router.get("/stats", response_model=dict)
async def get_recognition_stats(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Get recognition statistics.
    
    Returns:
    - total_recognitions: Total number of recognition events
    - unique_users: Number of unique users recognized
    - unknown_count: Number of unknown person detections
    - average_confidence: Average confidence score
    - top_users: Top 10 most recognized users
    """
    try:
        query = db.query(RecognitionLog)
        
        if start_date:
            query = query.filter(RecognitionLog.created_at >= start_date)
        if end_date:
            query = query.filter(RecognitionLog.created_at <= end_date)
        
        # Total recognitions
        total = query.count()
        
        # Unique users
        unique_users = query.filter(RecognitionLog.user_id.isnot(None)).distinct(RecognitionLog.user_id).count()
        
        # Unknown count
        unknown_count = query.filter(RecognitionLog.is_unknown == True).count()
        
        # Average confidence
        from sqlalchemy import func
        avg_confidence = query.with_entities(func.avg(RecognitionLog.confidence)).scalar() or 0.0
        
        # Top users
        top_users_query = (
            db.query(
                User.id,
                User.name,
                func.count(RecognitionLog.id).label('count')
            )
            .join(RecognitionLog, User.id == RecognitionLog.user_id)
        )
        
        if start_date:
            top_users_query = top_users_query.filter(RecognitionLog.created_at >= start_date)
        if end_date:
            top_users_query = top_users_query.filter(RecognitionLog.created_at <= end_date)
        
        top_users_list = (
            top_users_query
            .group_by(User.id, User.name)
            .order_by(func.count(RecognitionLog.id).desc())
            .limit(10)
            .all()
        )
        
        top_users = [
            {"user_id": user_id, "name": name, "recognition_count": count}
            for user_id, name, count in top_users_list
        ]
        
        return {
            "total_recognitions": total,
            "unique_users": unique_users,
            "unknown_count": unknown_count,
            "average_confidence": round(float(avg_confidence), 4),
            "top_users": top_users,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting stats: {str(e)}"
        )


@router.get("/sessions", response_model=List[dict])
async def get_sessions(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Get list of recognition sessions.
    
    Returns sessions with:
    - session_id
    - start_time
    - end_time
    - duration_seconds
    - total_recognitions
    - unique_users
    """
    try:
        from sqlalchemy import func
        
        sessions = (
            db.query(
                RecognitionLog.session_id,
                func.min(RecognitionLog.created_at).label('start_time'),
                func.max(RecognitionLog.created_at).label('end_time'),
                func.count(RecognitionLog.id).label('total_recognitions'),
                func.count(func.distinct(RecognitionLog.user_id)).label('unique_users')
            )
            .filter(RecognitionLog.session_id.isnot(None))
            .group_by(RecognitionLog.session_id)
            .order_by(func.min(RecognitionLog.created_at).desc())
            .limit(limit)
            .all()
        )
        
        result = []
        for session in sessions:
            session_id, start_time, end_time, total, unique = session
            duration = (end_time - start_time).total_seconds() if end_time and start_time else 0
            
            result.append({
                "session_id": session_id,
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat() if end_time else None,
                "duration_seconds": round(duration, 2),
                "total_recognitions": total,
                "unique_users": unique
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting sessions: {str(e)}"
        )

