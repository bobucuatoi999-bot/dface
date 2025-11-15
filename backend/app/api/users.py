"""
REST API endpoints for user management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserRegisterRequest, MultiAngleRegistrationRequest, VideoRegistrationRequest
from app.schemas.face_embedding import FaceEmbeddingResponse, AddFaceRequest
from app.services.user_service import UserService
from app.config import settings
from app.utils.errors import (
    handle_exception, ValidationError, NotFoundError, FaceDetectionError,
    AuthenticationError, AuthorizationError,
    validate_face_image, validate_user_data
)
from app.api.auth import get_current_user, require_role
from app.models.auth import AuthUser, UserRole

# Optional face recognition imports
try:
    from app.services.face_detection import FaceDetectionService
    from app.services.face_recognition import FaceRecognitionService
    from app.utils.image_processing import (
        decode_base64_image, calculate_image_quality, check_face_size,
        calculate_face_position_status
    )
    from app.utils.video_processing import (
        decode_base64_video, extract_frames_from_video, 
        validate_video_for_face_detection, get_best_frames_from_video
    )
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FaceDetectionService = None
    FaceRecognitionService = None
    FACE_RECOGNITION_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["users"])

user_service = UserService()
if FACE_RECOGNITION_AVAILABLE:
    face_detection_service = FaceDetectionService()
    face_recognition_service = FaceRecognitionService()
else:
    face_detection_service = None
    face_recognition_service = None


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_role(UserRole.ADMIN))
):
    """
    Create a new user.
    
    This endpoint creates a user record but does not add face embeddings.
    Use POST /api/users/{user_id}/faces to add face embeddings.
    """
    try:
        # Check if email already exists (if provided)
        if user_data.email:
            existing = user_service.get_user_by_email(db, user_data.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with email {user_data.email} already exists"
                )
        
        user = user_service.create_user(
            db=db,
            name=user_data.name,
            email=user_data.email,
            employee_id=user_data.employee_id,
            extra_data=user_data.extra_data
        )
        
        # Get face count
        user_dict = user.to_dict()
        return UserResponse(**user_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user_with_face(
    request: UserRegisterRequest,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_role(UserRole.ADMIN))
):
    """
    Register a new user with face capture.
    
    This is a convenience endpoint that creates a user and adds face embeddings
    from the provided image(s).
    
    The image_data should be a base64-encoded image string. The first face detected
    will be used for registration.
    
    Returns the created user with face embeddings.
    """
    try:
        # Validate input
        validate_user_data(request.name, request.email)
        validate_face_image(request.image_data)
        
        # Decode image
        image = decode_base64_image(request.image_data)
        
        # Detect faces
        face_locations = face_detection_service.detect_faces(image)
        
        if not face_locations:
            raise FaceDetectionError("No face detected in image. Please ensure the image contains a clear face.")
        
        # Use first face
        face_location = face_locations[0]
        
        # Check face size
        if not check_face_size(face_location, min_size=100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Face too small. Please ensure face is clearly visible."
            )
        
        # Extract embedding
        embedding = face_recognition_service.extract_embedding(image, face_location)
        
        if embedding is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract face embedding"
            )
        
        # Check for duplicates
        duplicate = user_service.check_duplicate(db, embedding)
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Face already registered for user: {duplicate.name} (ID: {duplicate.id})"
            )
        
        # Calculate quality
        quality = calculate_image_quality(image, face_location)
        
        # Create user
        user = user_service.create_user(
            db=db,
            name=request.name,
            email=request.email,
            employee_id=request.employee_id
        )
        
        # Add face embedding
        user_service.add_face_embedding(
            db=db,
            user_id=user.id,
            embedding=embedding,
            capture_angle="frontal",
            quality_score=quality
        )
        
        # Refresh user to get face count
        db.refresh(user)
        user_dict = user.to_dict()
        
        logger.info(f"Registered user: {user.name} (ID: {user.id})")
        return UserResponse(**user_dict)
        
    except (ValidationError, NotFoundError, FaceDetectionError, AuthenticationError, AuthorizationError) as e:
        raise handle_exception(e)
    except Exception as e:
        logger.error(f"Error registering user: {e}", exc_info=True)
        raise handle_exception(e)


@router.post("/register/multi-angle", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user_multi_angle(
    request: MultiAngleRegistrationRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user with multi-angle face capture.
    
    This endpoint captures faces from multiple angles (frontal, left, right) to improve
    recognition accuracy. You can either:
    1. Provide individual angle images (frontal_image, left_image, right_image)
    2. Provide a list of images (images) - will use first 3
    
    At least one image is required. More angles = better recognition accuracy.
    """
    try:
        # Collect images to process
        images_to_process = []
        angles = []
        
        if request.images:
            # Use list of images
            images_to_process = request.images[:3]  # Max 3 images
            angles = ["frontal", "left", "right"][:len(images_to_process)]
        else:
            # Use individual angle images
            if request.frontal_image:
                images_to_process.append(request.frontal_image)
                angles.append("frontal")
            if request.left_image:
                images_to_process.append(request.left_image)
                angles.append("left")
            if request.right_image:
                images_to_process.append(request.right_image)
                angles.append("right")
        
        if not images_to_process:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one image is required (frontal_image, left_image, right_image, or images list)"
            )
        
        # Process all images
        embeddings = []
        quality_scores = []
        
        for img_data, angle in zip(images_to_process, angles):
            try:
                image = decode_base64_image(img_data)
                
                # Detect faces
                face_locations = face_detection_service.detect_faces(image)
                
                if not face_locations:
                    logger.warning(f"No face detected in {angle} image, skipping")
                    continue
                
                # Use first face
                face_location = face_locations[0]
                
                # Check face size
                if not check_face_size(face_location, min_size=100):
                    logger.warning(f"Face too small in {angle} image, skipping")
                    continue
                
                # Extract embedding
                embedding = face_recognition_service.extract_embedding(image, face_location)
                
                if embedding is None:
                    logger.warning(f"Could not extract embedding from {angle} image, skipping")
                    continue
                
                # Calculate quality
                quality = calculate_image_quality(image, face_location)
                
                embeddings.append((embedding, angle, quality))
                quality_scores.append(quality)
                
            except Exception as e:
                logger.warning(f"Error processing {angle} image: {e}, skipping")
                continue
        
        if not embeddings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid faces found in any provided images. Please ensure images contain clear faces."
            )
        
        # Check for duplicates using first embedding
        first_embedding = embeddings[0][0]
        duplicate = user_service.check_duplicate(db, first_embedding)
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Face already registered for user: {duplicate.name} (ID: {duplicate.id})"
            )
        
        # Create user
        user = user_service.create_user(
            db=db,
            name=request.name,
            email=request.email,
            employee_id=request.employee_id
        )
        
        # Add all face embeddings
        added_count = 0
        for embedding, angle, quality in embeddings:
            try:
                user_service.add_face_embedding(
                    db=db,
                    user_id=user.id,
                    embedding=embedding,
                    capture_angle=angle,
                    quality_score=quality
                )
                added_count += 1
            except Exception as e:
                logger.error(f"Error adding {angle} embedding: {e}")
        
        if added_count == 0:
            # Rollback user creation if no embeddings added
            db.delete(user)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add face embeddings"
            )
        
        # Refresh user to get face count
        db.refresh(user)
        user_dict = user.to_dict()
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        logger.info(f"Registered user with {added_count} angles: {user.name} (ID: {user.id}, avg quality: {avg_quality:.2f})")
        return UserResponse(**user_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user with multi-angle: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {str(e)}"
        )


@router.post("/register/video", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user_with_video(
    request: VideoRegistrationRequest,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_role(UserRole.ADMIN))
):
    """
    Register a new user with video capture.
    
    This endpoint accepts a video (MP4 or WebM) and:
    1. Extracts frames from the video
    2. Validates that the video contains sufficient good-quality face frames
    3. Selects the best frames for registration
    4. Creates face embeddings from multiple angles for better recognition
    
    Video Requirements:
    - Format: MP4 or WebM
    - Duration: 3-10 seconds recommended
    - At least 5 frames must contain a detectable face
    - Face should be clearly visible, well-lit, and fill at least 1/4 of frame
    - Minimum face size: 100x100 pixels
    
    Returns the created user with face embeddings and validation results.
    """
    if not FACE_RECOGNITION_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Face recognition services are not available"
        )
    
    try:
        # Validate input
        validate_user_data(request.name, request.email)
        
        # Decode video
        logger.info(f"Decoding video for user registration: {request.name}")
        video_data = decode_base64_video(request.video_data)
        
        # Extract frames from video
        logger.info("Extracting frames from video...")
        frames = extract_frames_from_video(video_data, max_frames=30, frame_interval=5)
        
        if not frames:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract frames from video. Please ensure video format is supported (MP4 or WebM)."
            )
        
        logger.info(f"Extracted {len(frames)} frames from video")
        
        # Validate video meets requirements
        logger.info("Validating video for face detection...")
        validation_result = validate_video_for_face_detection(
            frames,
            min_frames_with_face=request.min_frames_with_face,
            min_face_size=settings.MIN_FACE_SIZE,
            min_quality_score=request.min_quality_score
        )
        
        if not validation_result["valid"]:
            # Return detailed validation errors
            error_detail = {
                "message": "Video does not meet face detection requirements",
                "validation": validation_result
            }
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail
            )
        
        logger.info(f"Video validation passed: {validation_result['frames_meeting_requirements']} frames meet requirements")
        
        # Get best frames for registration
        logger.info("Selecting best frames for registration...")
        best_frames = get_best_frames_from_video(
            frames,
            num_frames=3,  # Use top 3 frames
            min_face_size=settings.MIN_FACE_SIZE,
            min_quality_score=request.min_quality_score
        )
        
        if not best_frames:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not find suitable frames for registration"
            )
        
        logger.info(f"Selected {len(best_frames)} best frames for registration")
        
        # Process frames and extract embeddings
        embeddings = []
        quality_scores = []
        angles = ["frontal", "left", "right"]  # Assign angles to frames
        
        for idx, (frame, quality, face_location) in enumerate(best_frames):
            try:
                # Extract embedding
                embedding = face_recognition_service.extract_embedding(frame, face_location)
                
                if embedding is None:
                    logger.warning(f"Could not extract embedding from frame {idx}, skipping")
                    continue
                
                # Determine angle (use first as frontal, others as left/right)
                angle = angles[min(idx, len(angles) - 1)]
                
                embeddings.append((embedding, angle, quality))
                quality_scores.append(quality)
                
            except Exception as e:
                logger.warning(f"Error processing frame {idx}: {e}, skipping")
                continue
        
        if not embeddings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract face embeddings from any frames"
            )
        
        logger.info(f"Extracted {len(embeddings)} embeddings from video")
        
        # Check for duplicates using first embedding
        first_embedding = embeddings[0][0]
        duplicate = user_service.check_duplicate(db, first_embedding)
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Face already registered for user: {duplicate.name} (ID: {duplicate.id})"
            )
        
        # Create user
        user = user_service.create_user(
            db=db,
            name=request.name,
            email=request.email,
            employee_id=request.employee_id
        )
        
        # Add all face embeddings
        added_count = 0
        for embedding, angle, quality in embeddings:
            try:
                user_service.add_face_embedding(
                    db=db,
                    user_id=user.id,
                    embedding=embedding,
                    capture_angle=angle,
                    quality_score=quality
                )
                added_count += 1
            except Exception as e:
                logger.error(f"Error adding {angle} embedding: {e}")
        
        if added_count == 0:
            # Rollback user creation if no embeddings added
            db.delete(user)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add face embeddings"
            )
        
        # Refresh user to get face count
        db.refresh(user)
        user_dict = user.to_dict()
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        logger.info(f"Registered user with video: {user.name} (ID: {user.id}, {added_count} embeddings, avg quality: {avg_quality:.2f})")
        
        # Log validation info (for debugging)
        logger.info(f"Video registration details: {validation_result['frames_analyzed']} frames analyzed, "
                   f"{validation_result['frames_meeting_requirements']} met requirements, "
                   f"best quality: {validation_result['best_frame_quality']:.2f}")
        
        return UserResponse(**user_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user with video: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {str(e)}"
        )


@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)  # Require auth but any role
):
    """
    Get all users.
    
    Parameters:
    - active_only: If True, only return active users (default: True)
    """
    try:
        users = user_service.get_all_users(db, active_only=active_only)
        return [UserResponse(**user.to_dict()) for user in users]
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting users: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    """Get a specific user by ID."""
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return UserResponse(**user.to_dict())


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update a user's information."""
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    try:
        # Update fields
        if user_data.name is not None:
            user.name = user_data.name
        if user_data.email is not None:
            # Check if email already exists (for another user)
            existing = user_service.get_user_by_email(db, user_data.email)
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email {user_data.email} already in use"
                )
            user.email = user_data.email
        if user_data.employee_id is not None:
            user.employee_id = user_data.employee_id
        if user_data.extra_data is not None:
            user.extra_data = user_data.extra_data
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        
        db.commit()
        db.refresh(user)
        
        return UserResponse(**user.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_role(UserRole.ADMIN))
):
    """Delete a user and all associated data (face embeddings, logs)."""
    success = user_service.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return None


@router.post("/detect-faces")
async def detect_faces_endpoint(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Detect faces in an image with landmarks, position analysis, and quality feedback.
    Enhanced for optimal recognition positioning guide.
    
    Request body:
    {
        "image_data": "<base64_encoded_image>"
    }
    
    Returns:
    {
        "faces": [
            {
                "bbox": [top, right, bottom, left],
                "confidence": 1.0,
                "landmarks": {
                    "chin": [[x, y], ...],
                    "left_eyebrow": [[x, y], ...],
                    "right_eyebrow": [[x, y], ...],
                    "nose_bridge": [[x, y], ...],
                    "nose_tip": [[x, y], ...],
                    "left_eye": [[x, y], ...],
                    "right_eye": [[x, y], ...],
                    "top_lip": [[x, y], ...],
                    "bottom_lip": [[x, y], ...]
                },
                "position_status": {
                    "size_status": "optimal|too_small|too_large|acceptable",
                    "distance_status": "perfect|too_far|too_close|acceptable",
                    "position_status": "centered|off_center|edge",
                    "quality_status": "excellent|good|fair|poor",
                    "face_size": 200.5,
                    "face_width": 180,
                    "face_height": 220,
                    "face_center": [320.0, 240.0],
                    "center_offset": [0.05, 0.03],
                    "optimal_size_range": [150, 350]
                },
                "quality_score": 0.85
            }
        ],
        "face_count": 1,
        "image_size": [640, 480]
    }
    """
    if not FACE_RECOGNITION_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Face detection services are not available"
        )
    
    try:
        image_data = request.get("image_data")
        if not image_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="image_data is required"
            )
        
        # Decode image
        image = decode_base64_image(image_data)
        height, width = image.shape[:2]
        
        # Detect faces with landmarks
        face_locations, face_landmarks_list = face_detection_service.detect_faces_with_landmarks(image)
        
        # Format response with enhanced information
        faces = []
        for idx, face_loc in enumerate(face_locations):
            top, right, bottom, left = face_loc
            
            # Get landmarks for this face
            landmarks_dict = {}
            if idx < len(face_landmarks_list) and face_landmarks_list[idx]:
                landmarks = face_landmarks_list[idx]
                # Convert landmarks to serializable format
                for key, points in landmarks.items():
                    landmarks_dict[key] = [[int(p[0]), int(p[1])] for p in points]
            
            # Calculate position status
            position_status = calculate_face_position_status(
                face_loc,
                width,
                height,
                optimal_size_min=settings.OPTIMAL_FACE_SIZE_MIN,
                optimal_size_max=settings.OPTIMAL_FACE_SIZE_MAX
            )
            
            # Calculate quality score
            quality_score = calculate_image_quality(image, face_loc)
            
            faces.append({
                "bbox": [int(top), int(right), int(bottom), int(left)],
                "confidence": 1.0,  # face_recognition doesn't provide confidence, assume 1.0
                "landmarks": landmarks_dict,
                "position_status": position_status,
                "quality_score": round(quality_score, 2)
            })
        
        return {
            "faces": faces,
            "face_count": len(faces),
            "image_size": [width, height]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error detecting faces: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error detecting faces: {str(e)}"
        )


@router.get("/{user_id}/faces", response_model=List[FaceEmbeddingResponse])
async def get_user_faces(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get all face embeddings for a user."""
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    embeddings = user.face_embeddings
    return [FaceEmbeddingResponse(**emb.to_dict()) for emb in embeddings]


@router.post("/{user_id}/faces", response_model=FaceEmbeddingResponse, status_code=status.HTTP_201_CREATED)
async def add_user_face(
    user_id: int,
    request: AddFaceRequest,
    db: Session = Depends(get_db)
):
    """
    Add a face embedding for an existing user.
    
    Request body:
    {
        "image_data": "<base64_string>",
        "capture_angle": "frontal"
    }
    """
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    try:
        # Decode image
        image = decode_base64_image(request.image_data)
        
        # Detect face
        face_locations = face_detection_service.detect_faces(image)
        if not face_locations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected in image"
            )
        
        face_location = face_locations[0]
        
        # Check face size
        if not check_face_size(face_location, min_size=100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Face too small"
            )
        
        # Extract embedding
        embedding = face_recognition_service.extract_embedding(image, face_location)
        if embedding is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract face embedding"
            )
        
        # Calculate quality
        quality = calculate_image_quality(image, face_location)
        
        # Add embedding
        face_emb = user_service.add_face_embedding(
            db=db,
            user_id=user_id,
            embedding=embedding,
            capture_angle=request.capture_angle,
            quality_score=quality
        )
        
        return FaceEmbeddingResponse(**face_emb.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding face: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding face: {str(e)}"
        )
