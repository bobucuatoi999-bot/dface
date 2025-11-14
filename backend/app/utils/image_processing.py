"""
Image processing utilities for face recognition.
Handles image loading, preprocessing, and quality checks.
"""

import numpy as np
from PIL import Image
import io
import base64
from typing import Tuple, Optional, List
import cv2


def decode_base64_image(base64_string: str) -> np.ndarray:
    """
    Decode base64 encoded image string to numpy array.
    
    Args:
        base64_string: Base64 encoded image (with or without data URL prefix)
        
    Returns:
        numpy array representing the image (RGB format)
    """
    # Remove data URL prefix if present
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    
    # Decode base64
    image_data = base64.b64decode(base64_string)
    
    # Convert to PIL Image
    image = Image.open(io.BytesIO(image_data))
    
    # Convert to RGB if necessary
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Convert to numpy array
    image_array = np.array(image)
    
    return image_array


def encode_image_to_base64(image_array: np.ndarray) -> str:
    """
    Encode numpy image array to base64 string.
    
    Args:
        image_array: numpy array representing image (RGB format)
        
    Returns:
        Base64 encoded string
    """
    # Convert numpy array to PIL Image
    image = Image.fromarray(image_array.astype('uint8'))
    
    # Convert to bytes
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    image_bytes = buffer.getvalue()
    
    # Encode to base64
    base64_string = base64.b64encode(image_bytes).decode('utf-8')
    
    return base64_string


def resize_image(image: np.ndarray, max_size: int = 1920) -> np.ndarray:
    """
    Resize image if it's larger than max_size, maintaining aspect ratio.
    
    Args:
        image: numpy array representing image
        max_size: Maximum width or height
        
    Returns:
        Resized image array
    """
    height, width = image.shape[:2]
    
    if max(height, width) <= max_size:
        return image
    
    # Calculate scaling factor
    scale = max_size / max(height, width)
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    # Resize using OpenCV
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    return resized


def calculate_image_quality(image: np.ndarray, face_location: Optional[Tuple[int, int, int, int]] = None) -> float:
    """
    Calculate image quality score (0.0 to 1.0).
    Considers blur, brightness, and contrast.
    
    Args:
        image: numpy array representing image
        face_location: Optional tuple (top, right, bottom, left) of face location
        
    Returns:
        Quality score between 0.0 and 1.0
    """
    # Extract face region if provided, otherwise use full image
    if face_location:
        top, right, bottom, left = face_location
        roi = image[top:bottom, left:right]
        if roi.size == 0:
            return 0.0
    else:
        roi = image
    
    # Convert to grayscale for analysis
    if len(roi.shape) == 3:
        gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
    else:
        gray = roi
    
    # Calculate Laplacian variance (blur detection)
    # Higher variance = sharper image
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    blur_score = min(laplacian_var / 100.0, 1.0)  # Normalize to 0-1
    
    # Calculate brightness (should be around 0.5 for good lighting)
    brightness = np.mean(gray) / 255.0
    brightness_score = 1.0 - abs(brightness - 0.5) * 2  # Penalize too dark or too bright
    
    # Calculate contrast (standard deviation)
    contrast = np.std(gray) / 255.0
    contrast_score = min(contrast * 2, 1.0)  # Normalize
    
    # Weighted average
    quality = (blur_score * 0.5 + brightness_score * 0.3 + contrast_score * 0.2)
    
    return max(0.0, min(1.0, quality))


def check_face_size(face_location: Tuple[int, int, int, int], min_size: int = 100) -> bool:
    """
    Check if face is large enough for recognition.
    
    Args:
        face_location: Tuple (top, right, bottom, left)
        min_size: Minimum width or height in pixels
        
    Returns:
        True if face is large enough, False otherwise
    """
    top, right, bottom, left = face_location
    width = right - left
    height = bottom - top
    
    return width >= min_size and height >= min_size


def extract_face_region(image: np.ndarray, face_location: Tuple[int, int, int, int], 
                       padding: int = 20) -> np.ndarray:
    """
    Extract face region from image with padding.
    
    Args:
        image: Full image array
        face_location: Tuple (top, right, bottom, left)
        padding: Padding in pixels around face
        
    Returns:
        Cropped face region
    """
    top, right, bottom, left = face_location
    height, width = image.shape[:2]
    
    # Add padding
    top = max(0, top - padding)
    left = max(0, left - padding)
    bottom = min(height, bottom + padding)
    right = min(width, right + padding)
    
    return image[top:bottom, left:right]

