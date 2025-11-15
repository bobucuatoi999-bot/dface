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
    Professional image preprocessing with validation and quality checks.
    
    Args:
        base64_string: Base64 encoded image (with or without data URL prefix)
        
    Returns:
        numpy array representing the image (RGB format)
        
    Raises:
        ValueError: If image data is invalid or cannot be decoded
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if not base64_string:
        raise ValueError("Empty base64 string provided")
    
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[-1]  # Take last part after comma
        
        # Decode base64
        image_data = base64.b64decode(base64_string)
        
        if not image_data or len(image_data) == 0:
            raise ValueError("Decoded image data is empty")
        
        logger.debug(f"Decoded image data: {len(image_data)} bytes")
        
        # Convert to PIL Image
        try:
            image = Image.open(io.BytesIO(image_data))
        except Exception as e:
            raise ValueError(f"Failed to open image: {str(e)}")
        
        # Validate image was successfully opened
        if image is None:
            raise ValueError("Failed to decode image from base64")
        
        # Log original image properties
        logger.debug(f"Original image: mode={image.mode}, size={image.size}, format={image.format}")
        
        # Convert to RGB if necessary (required for face_recognition)
        if image.mode != 'RGB':
            logger.debug(f"Converting image from {image.mode} to RGB")
            # Handle different color modes
            if image.mode == 'RGBA':
                # Create white background for RGBA images
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[3] if len(image.split()) > 3 else None)
                image = rgb_image
            elif image.mode == 'L':  # Grayscale
                # Convert grayscale to RGB
                image = image.convert('RGB')
            elif image.mode == 'P':  # Palette mode
                # Convert palette to RGB
                image = image.convert('RGB')
            else:
                # Try direct conversion
                image = image.convert('RGB')
        
        # Convert to numpy array
        image_array = np.array(image)
        
        # Validate numpy array
        if image_array is None or image_array.size == 0:
            raise ValueError("Failed to convert image to numpy array")
        
        # Validate array shape (should be height x width x 3 for RGB)
        if len(image_array.shape) != 3 or image_array.shape[2] != 3:
            raise ValueError(f"Invalid image shape: {image_array.shape}, expected (height, width, 3) for RGB")
        
        # Validate array dtype (should be uint8)
        if image_array.dtype != np.uint8:
            logger.warning(f"Image dtype is {image_array.dtype}, converting to uint8")
            # Ensure values are in valid range [0, 255]
            if image_array.max() > 255 or image_array.min() < 0:
                image_array = np.clip(image_array, 0, 255)
            image_array = image_array.astype(np.uint8)
        
        # Validate pixel values are in valid range
        if image_array.min() < 0 or image_array.max() > 255:
            logger.warning(f"Image pixel values out of range: min={image_array.min()}, max={image_array.max()}")
            image_array = np.clip(image_array, 0, 255).astype(np.uint8)
        
        height, width = image_array.shape[:2]
        logger.debug(f"✅ Successfully decoded image: shape={image_array.shape}, dtype={image_array.dtype}, "
                    f"range=[{image_array.min()}, {image_array.max()}], mean={image_array.mean():.2f}")
        
        return image_array
        
    except ValueError:
        raise  # Re-raise ValueError as-is
    except Exception as e:
        logger.error(f"Error decoding base64 image: {e}", exc_info=True)
        raise ValueError(f"Failed to decode base64 image: {str(e)}")


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
    Uses high-quality interpolation to preserve face detail.
    
    Args:
        image: numpy array representing image (RGB format)
        max_size: Maximum width or height
        
    Returns:
        Resized image array (same dtype and format as input)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if image is None or image.size == 0:
        logger.warning("Empty image provided for resize")
        return image
    
    height, width = image.shape[:2]
    original_size = max(height, width)
    
    # Don't resize if image is already smaller than max_size
    if original_size <= max_size:
        logger.debug(f"Image size {width}x{height} is within limit ({max_size}), no resize needed")
        return image
    
    # Calculate scaling factor
    scale = max_size / original_size
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    # Ensure minimum size for face detection (at least 300px to preserve detail)
    if min(new_width, new_height) < 300:
        logger.warning(f"Resized image would be too small ({new_width}x{new_height}), "
                      f"using minimum size of 300px")
        # Scale to maintain aspect ratio with minimum 300px
        min_dimension = 300
        if width < height:
            new_height = int(height * (min_dimension / width))
            new_width = min_dimension
        else:
            new_width = int(width * (min_dimension / height))
            new_height = min_dimension
        # But still respect max_size
        if max(new_width, new_height) > max_size:
            scale = max_size / max(new_width, new_height)
            new_width = int(new_width * scale)
            new_height = int(new_height * scale)
    
    logger.debug(f"Resizing image from {width}x{height} to {new_width}x{new_height} "
                f"(scale={scale:.3f}, preserving aspect ratio)")
    
    # Use high-quality interpolation for better face detail preservation
    # INTER_AREA is best for downscaling, INTER_LINEAR for upscaling
    # Since we're downscaling, INTER_AREA is optimal
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    # Validate resized image
    if resized is None or resized.size == 0:
        logger.error(f"Resize failed, returning original image")
        return image
    
    # Ensure dtype is preserved
    if resized.dtype != image.dtype:
        resized = resized.astype(image.dtype)
    
    logger.debug(f"✅ Resized image: {resized.shape}, dtype={resized.dtype}")
    
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


def calculate_face_position_status(
    face_location: Tuple[int, int, int, int],
    image_width: int,
    image_height: int,
    optimal_size_min: int = 150,
    optimal_size_max: int = 350
) -> dict:
    """
    Calculate face position status for optimal recognition.
    
    Args:
        face_location: Tuple (top, right, bottom, left)
        image_width: Full image width
        image_height: Full image height
        optimal_size_min: Optimal minimum face size (pixels)
        optimal_size_max: Optimal maximum face size (pixels)
        
    Returns:
        Dictionary with:
        - size_status: "too_small", "too_large", "optimal", "acceptable"
        - distance_status: "too_far", "too_close", "perfect", "acceptable"
        - position_status: "centered", "off_center", "edge"
        - center_offset: (x_offset, y_offset) from image center
        - face_size: average of width and height
        - quality_status: overall quality assessment
    """
    from app.config import settings
    
    top, right, bottom, left = face_location
    face_width = right - left
    face_height = bottom - top
    face_size = (face_width + face_height) / 2.0  # Average size
    
    # Calculate face center
    face_center_x = (left + right) / 2.0
    face_center_y = (top + bottom) / 2.0
    
    # Calculate image center
    image_center_x = image_width / 2.0
    image_center_y = image_height / 2.0
    
    # Calculate offset from center (normalized to 0-1)
    x_offset = abs(face_center_x - image_center_x) / image_width if image_width > 0 else 0
    y_offset = abs(face_center_y - image_center_y) / image_height if image_height > 0 else 0
    center_offset = (x_offset, y_offset)
    
    # Determine size status
    if face_size < settings.MIN_FACE_SIZE:
        size_status = "too_small"
        distance_status = "too_far"
    elif face_size < optimal_size_min:
        size_status = "acceptable"
        distance_status = "acceptable"
    elif face_size <= optimal_size_max:
        size_status = "optimal"
        distance_status = "perfect"
    elif face_size <= optimal_size_max * 1.3:
        size_status = "acceptable"
        distance_status = "acceptable"
    else:
        size_status = "too_large"
        distance_status = "too_close"
    
    # Determine position status
    max_offset = max(x_offset, y_offset)
    if max_offset < 0.15:  # Within 15% of center
        position_status = "centered"
    elif max_offset < 0.30:  # Within 30% of center
        position_status = "off_center"
    else:
        position_status = "edge"
    
    # Overall quality status (combines all factors)
    if size_status == "optimal" and position_status == "centered":
        quality_status = "excellent"
    elif size_status in ["optimal", "acceptable"] and position_status in ["centered", "off_center"]:
        quality_status = "good"
    elif size_status in ["too_small", "too_large"]:
        quality_status = "poor"
    else:
        quality_status = "fair"
    
    return {
        "size_status": size_status,
        "distance_status": distance_status,
        "position_status": position_status,
        "center_offset": center_offset,
        "face_size": round(face_size, 1),
        "face_width": face_width,
        "face_height": face_height,
        "face_center": (round(face_center_x, 1), round(face_center_y, 1)),
        "quality_status": quality_status,
        "optimal_size_range": (optimal_size_min, optimal_size_max)
    }


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

