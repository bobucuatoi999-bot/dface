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
        
        if existing_admin:
            # Admin exists, log info
            print(f"ℹ️  Admin user already exists: {existing_admin.username} (ID: {existing_admin.id})", file=sys.stderr)
            print(f"   Email: {existing_admin.email or 'N/A'}", file=sys.stderr)
            print(f"   Active: {existing_admin.is_active}", file=sys.stderr)
        else:
            # No admin exists, create one
            username = os.getenv("ADMIN_USERNAME", "admin")
            password = os.getenv("ADMIN_PASSWORD", "admin123")
            email = os.getenv("ADMIN_EMAIL", "admin@facestream.local")
            
            print(f"Creating admin user: {username}...", file=sys.stderr)
            
            admin = auth_service.create_user(
                db=db,
                username=username,
                password=password,
                email=email,
                role=UserRole.ADMIN
            )
            
            # Note: auth_service.create_user() already commits, but let's verify
            db.refresh(admin)
            print(f"✅ Auto-created admin user: {username}", file=sys.stderr)
            print(f"   Password: {password}", file=sys.stderr)
            print(f"   Email: {email}", file=sys.stderr)
            print(f"   ID: {admin.id}", file=sys.stderr)
            print(f"   Active: {admin.is_active}", file=sys.stderr)
            print(f"   Role: {admin.role.value}", file=sys.stderr)
            print(f"   ⚠️  Please change the password after first login!", file=sys.stderr)
            
            # Verify the user was created correctly - use same session
            verify_user = db.query(AuthUser).filter(AuthUser.username == username).first()
            if verify_user:
                print(f"✅ Verified: User '{username}' exists in database (ID: {verify_user.id})", file=sys.stderr)
                # Test password verification
                if auth_service.verify_password(password, verify_user.hashed_password):
                    print(f"✅ Verified: Password verification works correctly", file=sys.stderr)
                    print(f"✅ Admin user is ready to use: username='{username}', password='{password}'", file=sys.stderr)
                    print(f"✅ SUCCESS: Admin user created and verified!", file=sys.stderr)
                else:
                    print(f"❌ ERROR: Password verification FAILED!", file=sys.stderr)
                    print(f"   This means the password hash is incorrect!", file=sys.stderr)
                    sys.exit(1)  # Fail loudly
            else:
                print(f"❌ ERROR: User was not found after creation!", file=sys.stderr)
                print(f"   Database transaction may have failed!", file=sys.stderr)
                sys.exit(1)  # Fail loudly
            
    except Exception as e:
        # Log error details
        import traceback
        print(f"❌ ERROR: Could not auto-create admin: {e}", file=sys.stderr)
        print(f"Traceback:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
    finally:
        db.close()
        
except Exception as e:
    # Log import errors
    import traceback
    print(f"❌ ERROR: Failed to import modules: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)

