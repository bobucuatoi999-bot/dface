"""
Main FastAPI application entry point.
Sets up the API server with WebSocket support.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import logging
import traceback
import os

from app.config import settings

# Configure logging FIRST (before other imports that might use logger)
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

from app.database import init_db, engine, Base, get_db
from app.models import User, FaceEmbedding, RecognitionLog
from app.services.user_service import UserService
from app.api import users, logs, search, auth

# Optional face recognition imports (backend can run without them for auth)
try:
    from app.services.face_detection import FaceDetectionService
    from app.services.face_recognition import FaceRecognitionService
    from app.services.face_tracking import FaceTrackingService
    from app.utils.image_processing import decode_base64_image, resize_image, check_face_size, calculate_image_quality
    FACE_RECOGNITION_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Face recognition modules not available: {e}. Backend will run in auth-only mode.")
    FaceDetectionService = None
    FaceRecognitionService = None
    FaceTrackingService = None
    FACE_RECOGNITION_AVAILABLE = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Initializes database on startup.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    try:
        if settings.DATABASE_URL:
            # Mask password in logs
            db_url_display = settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'configured'
            logger.info(f"Database URL: {db_url_display}")
        else:
            logger.warning("DATABASE_URL not configured")
    except Exception as e:
        logger.warning(f"Error logging database URL: {e}")
    
    # Initialize database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Database connection failed: {e}", exc_info=True)
        logger.warning("Server will start but database features will be unavailable.")
        logger.warning("Please ensure PostgreSQL is running and DATABASE_URL is correct in .env")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Real-time facial recognition system backend",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# CORS middleware (allow mobile app to connect)
# Get allowed origins from environment or default to all
if hasattr(settings, 'CORS_ORIGINS') and settings.CORS_ORIGINS:
    allowed_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
else:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Log CORS configuration
logger.info(f"CORS configured with allowed origins: {allowed_origins}")

# Global exception handler to ensure CORS headers are always sent
# Note: This only catches non-HTTPException errors (HTTPException is handled by FastAPI)
from fastapi import HTTPException as FastAPIHTTPException

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to ensure CORS headers are always sent,
    even when unhandled exceptions occur.
    Excludes HTTPException which FastAPI handles properly.
    """
    # Don't handle HTTPException - FastAPI handles those with CORS middleware
    if isinstance(exc, FastAPIHTTPException):
        raise exc
    
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Get the origin from request headers
    origin = request.headers.get("origin")
    
    # Check if origin is allowed
    if origin and (origin in allowed_origins or "*" in allowed_origins):
        headers = {"Access-Control-Allow-Origin": origin}
    elif "*" in allowed_origins:
        headers = {"Access-Control-Allow-Origin": "*"}
    else:
        headers = {}
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An internal server error occurred",
            "details": {"exception_type": type(exc).__name__}
        },
        headers=headers
    )

# Handle validation errors with CORS headers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with CORS headers."""
    origin = request.headers.get("origin")
    
    if origin and (origin in allowed_origins or "*" in allowed_origins):
        headers = {"Access-Control-Allow-Origin": origin}
    elif "*" in allowed_origins:
        headers = {"Access-Control-Allow-Origin": "*"}
    else:
        headers = {}
    
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
        headers=headers
    )


# WebSocket connection manager
class ConnectionManager:
    """
    Manages WebSocket connections for real-time recognition.
    Tracks active connections and can broadcast messages.
    """
    
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all active connections."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn)


# Global connection manager instance
manager = ConnectionManager()

# Initialize face processing services (if available)
if FACE_RECOGNITION_AVAILABLE:
    face_detection_service = FaceDetectionService()
    face_recognition_service = FaceRecognitionService()
    face_tracking_service = FaceTrackingService()
else:
    face_detection_service = None
    face_recognition_service = None
    face_tracking_service = None
    logger.warning("Face recognition services disabled. WebSocket recognition will not work.")

user_service = UserService()

# Include API routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(logs.router)
app.include_router(search.router)


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "endpoints": {
            "websocket": "/ws/recognize",
            "docs": "/docs",
            "health": "/health",
            "api": {
                "users": "/api/users",
                "logs": "/api/logs",
                "search": "/api/search",
            }
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Add actual database health check
        "active_connections": len(manager.active_connections),
    }


@app.get("/debug/users")
async def debug_users(db: Session = Depends(get_db)):
    """
    Debug endpoint to check users in database.
    ⚠️ WARNING: This exposes user information. Remove in production!
    """
    try:
        from app.models.auth import AuthUser, UserRole
        
        users = db.query(AuthUser).all()
        users_info = []
        for user in users:
            users_info.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "is_active": user.is_active,
                "created_at": str(user.created_at) if user.created_at else None,
            })
        
        return {
            "total_users": len(users_info),
            "users": users_info,
            "admin_count": len([u for u in users_info if u["role"] == "admin"])
        }
    except Exception as e:
        logger.error(f"Error getting users: {e}", exc_info=True)
        return {
            "error": str(e),
            "total_users": 0,
            "users": []
        }


@app.post("/debug/create-admin")
async def create_admin_endpoint(db: Session = Depends(get_db)):
    """
    Debug endpoint to create admin user if none exists.
    ⚠️ WARNING: This allows creating admin without authentication. Remove in production!
    """
    try:
        from app.models.auth import AuthUser, UserRole
        from app.services.auth_service import AuthService
        
        # Check if admin exists
        existing_admin = db.query(AuthUser).filter(AuthUser.role == UserRole.ADMIN).first()
        
        if existing_admin:
            return {
                "status": "exists",
                "message": f"Admin user already exists: {existing_admin.username}",
                "username": existing_admin.username,
                "id": existing_admin.id
            }
        
        # Create admin user
        auth_service = AuthService()
        username = os.getenv("ADMIN_USERNAME", "admin")
        password = os.getenv("ADMIN_PASSWORD", "admin123")
        email = os.getenv("ADMIN_EMAIL", "admin@facestream.local")
        
        logger.info(f"Creating admin user via endpoint: {username}")
        
        admin = auth_service.create_user(
            db=db,
            username=username,
            password=password,
            email=email,
            role=UserRole.ADMIN
        )
        
        # Verify user was created
        db.refresh(admin)
        verify_user = db.query(AuthUser).filter(AuthUser.username == username).first()
        
        if verify_user and auth_service.verify_password(password, verify_user.hashed_password):
            logger.info(f"Admin user created successfully: {username}")
            return {
                "status": "created",
                "message": f"Admin user created successfully",
                "username": username,
                "password": password,
                "id": admin.id,
                "verified": True
            }
        else:
            logger.error(f"Admin user creation failed verification")
            return {
                "status": "error",
                "message": "Admin user creation failed verification",
                "username": username
            }
            
    except Exception as e:
        logger.error(f"Error creating admin: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Error creating admin: {str(e)}",
            "error": str(e)
        }


@app.websocket("/ws/recognize")
async def websocket_recognize(websocket: WebSocket):
    """
    WebSocket endpoint for real-time face recognition.
    
    Expected flow:
    1. Client connects via WebSocket
    2. Client sends video frames (as base64 images)
    3. Server processes frames, detects faces, identifies users
    4. Server sends recognition results back to client
    
    Message format (from client):
    {
        "type": "frame",
        "data": "<base64_encoded_image>",
        "timestamp": 1234567890,
        "frame_id": 1
    }
    
    Message format (to client):
    {
        "type": "recognition_result",
        "frame_id": 1,
        "faces": [
            {
                "track_id": "1",
                "user_id": 248,
                "user_name": "John Doe",
                "confidence": 0.95,
                "bbox": [top, right, bottom, left],
                "is_unknown": false
            }
        ],
        "timestamp": 1234567890
    }
    """
    await manager.connect(websocket)
    
    # Generate session ID for this connection
    import uuid
    session_id = str(uuid.uuid4())
    
    # Check if face recognition is available
    if not FACE_RECOGNITION_AVAILABLE:
        await manager.send_personal_message({
            "type": "error",
            "message": "Face recognition services are not available. Please install face_recognition and dlib."
        }, websocket)
        manager.disconnect(websocket)
        return
    
    # Reset tracking for new session
    face_tracking_service.reset()
    
    # Frame rate limiting
    import time
    last_frame_time = 0
    min_frame_interval = 1.0 / settings.MAX_FRAME_RATE
    
    try:
        # Send connection confirmation
        await manager.send_personal_message({
            "type": "connection_established",
            "message": "WebSocket connected. Ready to receive frames.",
            "session_id": session_id,
            "settings": {
                "max_frame_rate": settings.MAX_FRAME_RATE,
                "face_match_threshold": settings.FACE_MATCH_THRESHOLD,
                "min_face_size": settings.MIN_FACE_SIZE,
            }
        }, websocket)
        
        # Get database session
        db_gen = get_db()
        db = next(db_gen)
        
        # Keep connection alive and process messages
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Handle different message types
            message_type = data.get("type")
            
            if message_type == "frame":
                # Frame rate limiting
                current_time = time.time()
                if current_time - last_frame_time < min_frame_interval:
                    continue  # Skip this frame
                last_frame_time = current_time
                
                try:
                    # Decode base64 image
                    base64_image = data.get("data")
                    if not base64_image:
                        continue
                    
                    image = decode_base64_image(base64_image)
                    
                    # Resize if too large (for performance)
                    image = resize_image(image, max_size=1920)
                    
                    # Detect faces
                    face_locations = face_detection_service.detect_faces(image)
                    
                    if not face_locations:
                        # No faces detected
                        await manager.send_personal_message({
                            "type": "recognition_result",
                            "frame_id": data.get("frame_id"),
                            "faces": [],
                            "timestamp": data.get("timestamp"),
                        }, websocket)
                        continue
                    
                    # Filter faces by minimum size
                    valid_faces = []
                    for face_loc in face_locations:
                        if check_face_size(face_loc, settings.MIN_FACE_SIZE):
                            valid_faces.append(face_loc)
                    
                    if not valid_faces:
                        await manager.send_personal_message({
                            "type": "recognition_result",
                            "frame_id": data.get("frame_id"),
                            "faces": [],
                            "timestamp": data.get("timestamp"),
                        }, websocket)
                        continue
                    
                    # Extract face embeddings
                    face_encodings = face_recognition_service.extract_multiple_embeddings(image, valid_faces)
                    
                    if len(face_encodings) != len(valid_faces):
                        logger.warning(f"Mismatch: {len(valid_faces)} faces but {len(face_encodings)} encodings")
                        continue
                    
                    # Recognize faces
                    recognized_users = []
                    for encoding in face_encodings:
                        match = face_recognition_service.find_best_match(encoding, db)
                        if match:
                            user, confidence = match
                            recognized_users.append((user.id, user.name, confidence))
                        else:
                            recognized_users.append((None, None, 0.0))
                    
                    # Update tracks
                    tracks = face_tracking_service.update_tracks(
                        valid_faces,
                        face_encodings,
                        recognized_users
                    )
                    
                    # Build response
                    faces_result = []
                    for track in tracks:
                        face_result = {
                            "track_id": track.track_id,
                            "bbox": list(track.bbox),  # [top, right, bottom, left]
                            "is_unknown": track.user_id is None,
                        }
                        
                        if track.user_id:
                            face_result["user_id"] = track.user_id
                            face_result["user_name"] = track.user_name
                            face_result["confidence"] = round(track.confidence, 4)
                        else:
                            face_result["confidence"] = 0.0
                        
                        faces_result.append(face_result)
                        
                        # Log recognition event
                        try:
                            user_service.create_recognition_log(
                                db=db,
                                user_id=track.user_id,
                                track_id=track.track_id,
                                confidence=track.confidence,
                                is_unknown=track.user_id is None,
                                frame_position=f"{track.bbox[3]},{track.bbox[0]},{track.bbox[1]-track.bbox[3]},{track.bbox[2]-track.bbox[0]}",  # x,y,width,height
                                session_id=session_id
                            )
                        except Exception as e:
                            logger.error(f"Error creating recognition log: {e}")
                    
                    # Send recognition results
                    await manager.send_personal_message({
                        "type": "recognition_result",
                        "frame_id": data.get("frame_id"),
                        "faces": faces_result,
                        "timestamp": data.get("timestamp"),
                        "session_id": session_id,
                    }, websocket)
                    
                except Exception as e:
                    logger.error(f"Error processing frame: {e}", exc_info=True)
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"Error processing frame: {str(e)}",
                        "frame_id": data.get("frame_id"),
                    }, websocket)
            
            elif message_type == "ping":
                # Heartbeat/ping message
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": data.get("timestamp"),
                }, websocket)
            
            elif message_type == "reset":
                # Reset tracking
                face_tracking_service.reset()
                await manager.send_personal_message({
                    "type": "reset_confirmed",
                    "message": "Tracking reset",
                }, websocket)
            
            else:
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}",
                }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Client disconnected (session: {session_id})")
        face_tracking_service.reset()
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(websocket)
        face_tracking_service.reset()
    finally:
        # Close database session
        try:
            db_gen.close()
        except:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        loop="asyncio",  # Use asyncio instead of uvloop for better compatibility
    )

