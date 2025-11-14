"""
Pydantic schemas for User model.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    employee_id: Optional[str] = Field(None, max_length=100, description="Employee/ID number")
    extra_data: Optional[str] = Field(None, description="Additional JSON metadata")


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    employee_id: Optional[str] = Field(None, max_length=100)
    extra_data: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    name: str
    email: Optional[str]
    employee_id: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    face_count: int = Field(0, description="Number of face embeddings for this user")
    
    class Config:
        from_attributes = True


class UserWithEmbeddings(UserResponse):
    """Schema for user with face embeddings."""
    face_embeddings: list["FaceEmbeddingResponse"] = []


class UserRegisterRequest(BaseModel):
    """Schema for registering a user with face capture."""
    name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    employee_id: Optional[str] = Field(None, max_length=100, description="Employee/ID number")
    image_data: str = Field(..., description="Base64 encoded image string")


class MultiAngleRegistrationRequest(BaseModel):
    """Schema for multi-angle face registration."""
    name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    employee_id: Optional[str] = Field(None, max_length=100, description="Employee/ID number")
    frontal_image: Optional[str] = Field(None, description="Base64 encoded frontal face image")
    left_image: Optional[str] = Field(None, description="Base64 encoded left profile image")
    right_image: Optional[str] = Field(None, description="Base64 encoded right profile image")
    images: Optional[List[str]] = Field(None, description="List of base64 encoded images (alternative to individual angles)")


class VideoRegistrationRequest(BaseModel):
    """Schema for video-based user registration."""
    name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    employee_id: Optional[str] = Field(None, max_length=100, description="Employee/ID number")
    video_data: str = Field(..., description="Base64 encoded video string (MP4 or WebM format)")
    min_frames_with_face: int = Field(5, ge=3, le=20, description="Minimum number of frames that must contain a detectable face")
    min_quality_score: float = Field(0.5, ge=0.0, le=1.0, description="Minimum quality score for frames to be considered valid")