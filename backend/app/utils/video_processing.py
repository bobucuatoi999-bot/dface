"""
Video processing utilities for face recognition.
Handles video decoding, frame extraction, and video quality validation.
"""

import numpy as np
import cv2
import base64
import io
import re
from typing import List, Tuple, Optional, Dict
from PIL import Image
import logging

logger = logging.getLogger(__name__)


def decode_base64_video(base64_string: str) -> bytes:
    """
    Decode base64 encoded video string to bytes.
    
    Args:
        base64_string: Base64 encoded video (with or without data URL prefix)
        
    Returns:
        Video bytes
    """
    if not base64_string:
        raise ValueError("Empty base64 string provided")
    
    # Remove data URL prefix if present (e.g., "data:video/webm;base64,...")
    if ',' in base64_string:
        base64_string = base64_string.split(',')[-1]  # Take the last part after comma
    
    # Clean the base64 string: remove all whitespace, newlines, and non-base64 characters
    # Base64 only contains: A-Z, a-z, 0-9, +, /, and = (for padding)
    base64_string = re.sub(r'[^A-Za-z0-9+/=]', '', base64_string)
    
    if not base64_string:
        raise ValueError("Invalid base64 video data: only base64 characters are allowed")
    
    # Fix base64 padding (base64 strings must have length multiple of 4)
    # Add padding if needed
    missing_padding = len(base64_string) % 4
    if missing_padding:
        base64_string += '=' * (4 - missing_padding)
    
    try:
        # Validate base64 string contains only valid characters
        # Base64 alphabet: A-Z, a-z, 0-9, +, /, = (padding)
        if not re.match(r'^[A-Za-z0-9+/]+=*$', base64_string):
            raise ValueError("Invalid base64 video data: only base64 data is allowed")
        
        # Decode base64 with validation
        video_data = base64.b64decode(base64_string, validate=True)
        
        if len(video_data) == 0:
            raise ValueError("Decoded video data is empty")
        
        return video_data
    except base64.binascii.Error as e:
        logger.error(f"Base64 decoding error: {e}")
        raise ValueError(f"Invalid base64 video data: only base64 data is allowed. Error: {str(e)}")
    except Exception as e:
        logger.error(f"Error decoding base64 video: {e}")
        # Try without strict validation as fallback
        try:
            video_data = base64.b64decode(base64_string, validate=False)
            if len(video_data) == 0:
                raise ValueError("Decoded video data is empty")
            return video_data
        except Exception as e2:
            logger.error(f"Error decoding base64 video (fallback): {e2}")
            raise ValueError(f"Invalid base64 video data: only base64 data is allowed. Error: {str(e2)}")


def detect_video_format(video_data: bytes) -> str:
    """
    Detect video format from video bytes.
    
    Args:
        video_data: Video bytes
        
    Returns:
        Format string ('webm', 'mp4', or 'unknown')
    """
    # Check magic bytes to determine format
    # WebM: starts with 1A 45 DF A3 (EBML header)
    # MP4: starts with ftyp box (00 00 00 ?? 66 74 79 70)
    
    if len(video_data) < 12:
        return 'unknown'
    
    # Check for WebM (EBML header)
    if video_data[:4] == b'\x1a\x45\xdf\xa3':
        return 'webm'
    
    # Check for MP4 (ftyp box)
    # MP4 files have 'ftyp' at offset 4 after a 4-byte size field
    if b'ftyp' in video_data[:12]:
        return 'mp4'
    
    # Check for older MP4 format
    if video_data[4:8] == b'ftyp':
        return 'mp4'
    
    return 'unknown'


def extract_frames_from_video(video_data: bytes, max_frames: int = 30, 
                              frame_interval: int = 5) -> List[np.ndarray]:
    """
    Extract frames from video data.
    
    Args:
        video_data: Video bytes (MP4, WebM, etc.)
        max_frames: Maximum number of frames to extract
        frame_interval: Extract every Nth frame (to avoid processing all frames)
        
    Returns:
        List of numpy arrays representing frames (RGB format)
    """
    frames = []
    tmp_path = None
    
    if not video_data or len(video_data) == 0:
        logger.error("Empty video data provided")
        return frames
    
    # Validate minimum size (at least 1KB for a valid video)
    if len(video_data) < 1024:
        logger.error(f"Video data too small: {len(video_data)} bytes (minimum 1KB required)")
        return frames
    
    logger.info(f"Processing video data: {len(video_data)} bytes ({len(video_data) / 1024:.2f} KB)")
    
    try:
        import tempfile
        import os
        
        # Detect video format
        video_format = detect_video_format(video_data)
        logger.info(f"Detected video format: {video_format}")
        
        # Log first few bytes for debugging
        if len(video_data) >= 12:
            first_bytes = video_data[:12]
            logger.debug(f"Video header bytes: {first_bytes.hex()}")
        
        # Determine file extension based on detected format
        if video_format == 'webm':
            suffix = '.webm'
        elif video_format == 'mp4':
            suffix = '.mp4'
        else:
            # Try WebM first (most common for browser recordings)
            logger.warning(f"Unknown video format, defaulting to .webm")
            suffix = '.webm'
        
        # Create temporary file with appropriate extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(video_data)
            tmp_path = tmp_file.name
            tmp_file.flush()
            os.fsync(tmp_file.fileno())  # Ensure data is written to disk
        
        try:
            # Open video with OpenCV
            logger.info(f"Attempting to open video file: {tmp_path} (format: {video_format})")
            cap = cv2.VideoCapture(tmp_path)
            
            if not cap.isOpened():
                error_msg = f"OpenCV could not open video file: {tmp_path}"
                logger.error(error_msg)
                logger.error(f"Video file size: {os.path.getsize(tmp_path) if os.path.exists(tmp_path) else 0} bytes")
                logger.error(f"Video format detected: {video_format}, extension used: {suffix}")
                
                # Check if OpenCV has codec support
                backend_info = cv2.videoio_registry.getBackends()
                logger.error(f"Available OpenCV backends: {[str(b) for b in backend_info]}")
                
                # Try alternative format if WebM failed
                if suffix == '.webm':
                    logger.info("Trying MP4 format as fallback...")
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file2:
                        tmp_file2.write(video_data)
                        tmp_file2.flush()
                        os.fsync(tmp_file2.fileno())
                        tmp_path2 = tmp_file2.name
                    
                    cap = cv2.VideoCapture(tmp_path2)
                    if cap.isOpened():
                        logger.info("Successfully opened video with MP4 format")
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)
                        tmp_path = tmp_path2
                    else:
                        logger.error("Could not open video with MP4 format either")
                        logger.error("Possible causes:")
                        logger.error("1. Video codec not supported by OpenCV")
                        logger.error("2. Video file is corrupted")
                        logger.error("3. OpenCV build doesn't include required codecs")
                        if os.path.exists(tmp_path2):
                            os.unlink(tmp_path2)
                        return frames
                else:
                    return frames
            
            # Get video properties for validation
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count_total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            logger.info(f"Video properties: {width}x{height}, {fps} FPS, {frame_count_total} total frames")
            
            if frame_count_total == 0:
                logger.warning("Video reports 0 frames, attempting to read anyway")
            
            extracted_count = 0
            current_frame = 0
            
            # Read frames
            while extracted_count < max_frames:
                ret, frame = cap.read()
                
                if not ret:
                    # No more frames or error reading
                    if extracted_count == 0:
                        logger.warning(f"No frames could be read from video (read {current_frame} frames before failure)")
                    break
                
                # Extract frame at intervals
                if current_frame % frame_interval == 0:
                    # Validate frame
                    if frame is not None and frame.size > 0:
                        # Convert BGR to RGB (OpenCV uses BGR)
                        if len(frame.shape) == 3:
                            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        else:
                            # Grayscale frame, convert to RGB
                            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
                        
                        frames.append(frame_rgb)
                        extracted_count += 1
                    else:
                        logger.warning(f"Invalid frame at position {current_frame}")
                
                current_frame += 1
            
            cap.release()
            
            logger.info(f"Successfully extracted {len(frames)} frames from video")
            
        finally:
            # Clean up temporary file
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception as cleanup_error:
                    logger.warning(f"Error cleaning up temp file {tmp_path}: {cleanup_error}")
    
    except Exception as e:
        logger.error(f"Error extracting frames from video: {e}", exc_info=True)
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    return frames


def validate_video_for_face_detection(frames: List[np.ndarray], 
                                     min_frames_with_face: int = 5,
                                     min_face_size: int = 100,
                                     min_quality_score: float = 0.5) -> Dict:
    """
    Validate that video contains sufficient good-quality face frames.
    
    Args:
        frames: List of video frames (numpy arrays)
        min_frames_with_face: Minimum number of frames that must contain a detectable face
        min_face_size: Minimum face size in pixels
        min_quality_score: Minimum quality score for a frame to be considered valid
        
    Returns:
        Dictionary with validation results:
        {
            "valid": bool,
            "frames_analyzed": int,
            "frames_with_face": int,
            "frames_meeting_requirements": int,
            "best_frame_index": int,
            "best_frame_quality": float,
            "issues": List[str],
            "recommendations": List[str]
        }
    """
    from app.services.face_detection import FaceDetectionService
    from app.utils.image_processing import check_face_size, calculate_image_quality
    
    face_detection_service = FaceDetectionService()
    
    frames_analyzed = len(frames)
    frames_with_face = 0
    frames_meeting_requirements = 0
    best_frame_index = -1
    best_frame_quality = 0.0
    issues = []
    recommendations = []
    
    valid_frames = []  # Store (index, quality, face_location) for valid frames
    
    for idx, frame in enumerate(frames):
        try:
            # Detect faces in frame
            face_locations = face_detection_service.detect_faces(frame)
            
            if not face_locations:
                continue
            
            frames_with_face += 1
            
            # Use first face
            face_location = face_locations[0]
            
            # Check face size
            if not check_face_size(face_location, min_size=min_face_size):
                continue
            
            # Calculate quality
            quality = calculate_image_quality(frame, face_location)
            
            if quality >= min_quality_score:
                frames_meeting_requirements += 1
                valid_frames.append((idx, quality, face_location))
                
                # Track best frame
                if quality > best_frame_quality:
                    best_frame_quality = quality
                    best_frame_index = idx
            
        except Exception as e:
            logger.warning(f"Error analyzing frame {idx}: {e}")
            continue
    
    # Determine if video is valid
    valid = frames_meeting_requirements >= min_frames_with_face
    
    # Generate issues and recommendations
    if frames_analyzed == 0:
        issues.append("No frames could be extracted from video")
        recommendations.append("Ensure video format is supported (MP4, WebM)")
    elif frames_with_face == 0:
        issues.append("No faces detected in any frame")
        recommendations.append("Ensure face is clearly visible and well-lit")
        recommendations.append("Look directly at the camera")
        recommendations.append("Remove obstructions (glasses, masks, hands)")
    elif frames_meeting_requirements < min_frames_with_face:
        issues.append(f"Only {frames_meeting_requirements} frame(s) meet quality requirements (need {min_frames_with_face})")
        recommendations.append("Improve lighting - ensure face is well-lit")
        recommendations.append("Hold still and look directly at camera")
        recommendations.append("Ensure face fills at least 1/4 of the frame")
        recommendations.append("Avoid blur - hold camera steady")
    else:
        recommendations.append("Video quality is good!")
    
    if best_frame_quality < 0.7:
        recommendations.append("Consider improving lighting and reducing blur for better recognition accuracy")
    
    return {
        "valid": valid,
        "frames_analyzed": frames_analyzed,
        "frames_with_face": frames_with_face,
        "frames_meeting_requirements": frames_meeting_requirements,
        "min_frames_required": min_frames_with_face,
        "best_frame_index": best_frame_index,
        "best_frame_quality": best_frame_quality,
        "issues": issues,
        "recommendations": recommendations
    }


def get_best_frames_from_video(frames: List[np.ndarray], 
                               num_frames: int = 3,
                               min_face_size: int = 100,
                               min_quality_score: float = 0.5) -> List[Tuple[np.ndarray, float, Tuple[int, int, int, int]]]:
    """
    Extract the best quality frames from video for registration.
    
    Args:
        frames: List of video frames
        num_frames: Number of best frames to return
        min_face_size: Minimum face size
        min_quality_score: Minimum quality score
        
    Returns:
        List of tuples: (frame, quality_score, face_location)
        Sorted by quality (best first)
    """
    from app.services.face_detection import FaceDetectionService
    from app.utils.image_processing import check_face_size, calculate_image_quality
    
    face_detection_service = FaceDetectionService()
    
    valid_frames = []
    
    for frame in frames:
        try:
            # Detect faces
            face_locations = face_detection_service.detect_faces(frame)
            
            if not face_locations:
                continue
            
            face_location = face_locations[0]
            
            # Check face size
            if not check_face_size(face_location, min_size=min_face_size):
                continue
            
            # Calculate quality
            quality = calculate_image_quality(frame, face_location)
            
            if quality >= min_quality_score:
                valid_frames.append((frame, quality, face_location))
        
        except Exception as e:
            logger.warning(f"Error processing frame: {e}")
            continue
    
    # Sort by quality (best first)
    valid_frames.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N frames
    return valid_frames[:num_frames]

