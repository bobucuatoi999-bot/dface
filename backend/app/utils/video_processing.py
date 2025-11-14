"""
Video processing utilities for face recognition.
Handles video decoding, frame extraction, and video quality validation.
"""

import numpy as np
import cv2
import base64
import io
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
    # Remove data URL prefix if present
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    
    # Decode base64
    video_data = base64.b64decode(base64_string)
    return video_data


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
    
    try:
        # Write video data to temporary file-like object
        video_buffer = io.BytesIO(video_data)
        
        # Use OpenCV to read video
        # Create a temporary file path or use memory buffer
        # OpenCV VideoCapture needs a file path, so we'll use a workaround
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            tmp_file.write(video_data)
            tmp_path = tmp_file.name
        
        try:
            # Open video with OpenCV
            cap = cv2.VideoCapture(tmp_path)
            
            if not cap.isOpened():
                logger.error("Could not open video file")
                return frames
            
            frame_count = 0
            extracted_count = 0
            
            while extracted_count < max_frames:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Extract frame at intervals
                if frame_count % frame_interval == 0:
                    # Convert BGR to RGB (OpenCV uses BGR)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(frame_rgb)
                    extracted_count += 1
                
                frame_count += 1
            
            cap.release()
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        logger.error(f"Error extracting frames from video: {e}")
    
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

