"""
Enhanced error handling and validation utilities.
"""

from fastapi import HTTPException, status
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base exception for application errors."""
    def __init__(self, message: str, code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.code = code or "GENERIC_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AppException):
    """Validation error."""
    def __init__(self, message: str, field: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field


class NotFoundError(AppException):
    """Resource not found error."""
    def __init__(self, resource_type: str, resource_id: Any = None):
        message = f"{resource_type} not found"
        if resource_id is not None:
            message += f" (ID: {resource_id})"
        super().__init__(message, "NOT_FOUND", {"resource_type": resource_type, "resource_id": resource_id})


class AuthenticationError(AppException):
    """Authentication error."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(AppException):
    """Authorization error."""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, "AUTHORIZATION_ERROR")


class FaceDetectionError(AppException):
    """Face detection/recognition error."""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, "FACE_DETECTION_ERROR", details)


def handle_exception(e: Exception) -> HTTPException:
    """
    Convert application exceptions to HTTP exceptions with proper formatting.
    
    Args:
        e: Exception to handle
        
    Returns:
        HTTPException with proper status code and detail
    """
    if isinstance(e, ValidationError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": e.code,
                "message": e.message,
                "field": e.field,
                "details": e.details
            }
        )
    
    elif isinstance(e, NotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": e.code,
                "message": e.message,
                "details": e.details
            }
        )
    
    elif isinstance(e, AuthenticationError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": e.code,
                "message": e.message
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    elif isinstance(e, AuthorizationError):
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": e.code,
                "message": e.message
            }
        )
    
    elif isinstance(e, FaceDetectionError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": e.code,
                "message": e.message,
                "details": e.details
            }
        )
    
    elif isinstance(e, AppException):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": e.code,
                "message": e.message,
                "details": e.details
            }
        )
    
    else:
        # Generic exception
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "An internal error occurred",
                "details": {"exception_type": type(e).__name__}
            }
        )


def validate_face_image(image_data: str) -> None:
    """
    Validate face image data.
    
    Args:
        image_data: Base64 encoded image string
        
    Raises:
        ValidationError if image is invalid
    """
    if not image_data:
        raise ValidationError("Image data is required", field="image_data")
    
    if len(image_data) < 100:  # Too small to be a valid image
        raise ValidationError("Image data appears to be invalid or too small", field="image_data")
    
    # Could add more validation here (check if it's valid base64, valid image format, etc.)


def validate_user_data(name: str, email: Optional[str] = None) -> None:
    """
    Validate user registration data.
    
    Args:
        name: User name
        email: Email address (optional)
        
    Raises:
        ValidationError if data is invalid
    """
    if not name or len(name.strip()) == 0:
        raise ValidationError("Name is required", field="name")
    
    if len(name) > 255:
        raise ValidationError("Name is too long (max 255 characters)", field="name")
    
    if email:
        # Basic email validation
        if "@" not in email or "." not in email.split("@")[1]:
            raise ValidationError("Invalid email format", field="email")

