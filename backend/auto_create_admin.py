"""
Automatically create admin user on startup if none exists.
This script runs silently and only creates admin if database is empty.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.database import SessionLocal, init_db
    from app.models.auth import AuthUser, UserRole
    from app.services.auth_service import AuthService
    
    # Initialize database
    init_db()
    
    db = SessionLocal()
    auth_service = AuthService()
    
    try:
        # Check if any admin exists
        existing_admin = db.query(AuthUser).filter(AuthUser.role == UserRole.ADMIN).first()
        
        if not existing_admin:
            # No admin exists, create one
            username = os.getenv("ADMIN_USERNAME", "admin")
            password = os.getenv("ADMIN_PASSWORD", "admin123")
            email = os.getenv("ADMIN_EMAIL", "admin@facestream.local")
            
            admin = auth_service.create_user(
                db=db,
                username=username,
                password=password,
                email=email,
                role=UserRole.ADMIN
            )
            
            db.commit()
            print(f"✅ Auto-created admin user: {username}", file=sys.stderr)
            print(f"   Password: {password}", file=sys.stderr)
            print(f"   ⚠️  Please change the password after first login!", file=sys.stderr)
        else:
            # Admin exists, do nothing
            pass
            
    except Exception as e:
        # Silently fail - don't crash the app if admin creation fails
        print(f"⚠️  Could not auto-create admin: {e}", file=sys.stderr)
    finally:
        db.close()
        
except Exception as e:
    # Silently fail if imports fail
    pass

