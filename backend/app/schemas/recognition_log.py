"""
Pydantic schemas for RecognitionLog model.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RecognitionLogResponse(BaseModel):
    """Schema for recognition log response."""
    id: int
    user_id: Optional[int]
    user_name: Optional[str] = Field(None, description="Name of recognized user")
    track_id: Optional[str]
    confidence: float = Field(..., ge=0.0, le=1.0)
    is_unknown: bool
    frame_position: Optional[str]
    session_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class RecognitionLogFilter(BaseModel):
    """Schema for filtering recognition logs."""
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    is_unknown: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)

