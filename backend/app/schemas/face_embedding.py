"""
Pydantic schemas for FaceEmbedding model.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FaceEmbeddingCreate(BaseModel):
    """Schema for creating a face embedding."""
    user_id: int = Field(..., description="User ID to associate embedding with")
    capture_angle: Optional[str] = Field(None, max_length=50, description="Angle description (e.g., 'frontal', 'left', 'right')")
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Quality score (0.0 to 1.0)")


class AddFaceRequest(BaseModel):
    """Schema for adding face to existing user."""
    image_data: str = Field(..., description="Base64 encoded image string")
    capture_angle: Optional[str] = Field("frontal", max_length=50, description="Angle description")


class FaceEmbeddingResponse(BaseModel):
    """Schema for face embedding response."""
    id: int
    user_id: int
    embedding_length: int = Field(..., description="Length of embedding vector (should be 128)")
    capture_angle: Optional[str]
    quality_score: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True

