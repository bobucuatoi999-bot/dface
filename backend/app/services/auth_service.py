"""
Authentication service for JWT tokens and password management.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import logging

from app.config import settings
from app.models.auth import AuthUser, UserRole

logger = logging.getLogger(__name__)

# Password hashing context
# Initialize with explicit backend to avoid bcrypt initialization issues
try:
    # Try to use bcrypt backend explicitly
    pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto")
    # Force backend initialization by trying a simple hash
    _test_hash = pwd_context.hash("test")
except Exception as e:
    logger.warning(f"Bcrypt initialization issue: {e}. Using fallback.")
    # Fallback: use bcrypt directly if passlib fails
    import bcrypt
    pwd_context = None  # Will use bcrypt directly


class AuthService:
    """Service for authentication and authorization."""
    
    def __init__(self):
        """Initialize authentication service."""
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Data to encode in token (usually username and role)
            expires_delta: Optional expiration time
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt
    
    def decode_access_token(self, token: str) -> Optional[dict]:
        """
        Decode and verify a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token data or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.warning(f"JWT decode error: {e}")
            return None
    
    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[AuthUser]:
        """
        Authenticate a user by username and password.
        
        Args:
            db: Database session
            username: Username
            password: Plain text password
            
        Returns:
            AuthUser if authenticated, None otherwise
        """
        user = db.query(AuthUser).filter(AuthUser.username == username).first()
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not self.verify_password(password, user.hashed_password):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        return user
    
    def create_user(self, db: Session, username: str, password: str, 
                   email: Optional[str] = None, role: UserRole = UserRole.OPERATOR) -> AuthUser:
        """
        Create a new authentication user.
        
        Args:
            db: Database session
            username: Username
            password: Plain text password
            email: Email address
            role: User role
            
        Returns:
            Created AuthUser
        """
        hashed_password = self.get_password_hash(password)
        
        user = AuthUser(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"Created auth user: {username} (role: {role.value})")
        return user
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[AuthUser]:
        """Get user by username."""
        return db.query(AuthUser).filter(AuthUser.username == username).first()
    
    def has_permission(self, user: AuthUser, required_role: UserRole) -> bool:
        """
        Check if user has required permission.
        
        Role hierarchy:
        - ADMIN: Full access
        - OPERATOR: Can use recognition, view logs
        - VIEWER: Read-only access
        """
        role_hierarchy = {
            UserRole.ADMIN: 3,
            UserRole.OPERATOR: 2,
            UserRole.VIEWER: 1
        }
        
        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level

