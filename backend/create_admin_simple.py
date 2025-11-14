"""
Simple script to create admin user.
This script directly creates the admin user without any complex logic.
Run this via Railway CLI: railway run python create_admin_simple.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("=" * 60, file=sys.stderr)
    print("  Creating Admin User", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("", file=sys.stderr)
    
    from app.database import SessionLocal, engine, Base
    from app.models.auth import AuthUser, UserRole
    from app.services.auth_service import AuthService
    
    # Ensure tables exist
    print("Step 1: Ensuring database tables exist...", file=sys.stderr)
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables exist", file=sys.stderr)
    print("", file=sys.stderr)
    
    # Create database session
    print("Step 2: Connecting to database...", file=sys.stderr)
    db = SessionLocal()
    print("✓ Connected to database", file=sys.stderr)
    print("", file=sys.stderr)
    
    # Initialize auth service
    print("Step 3: Initializing auth service...", file=sys.stderr)
    auth_service = AuthService()
    print("✓ Auth service initialized", file=sys.stderr)
    print("", file=sys.stderr)
    
    # Credentials
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin123")
    email = os.getenv("ADMIN_EMAIL", "admin@facestream.local")
    
    print(f"Step 4: Checking if admin user exists...", file=sys.stderr)
    print(f"   Username: {username}", file=sys.stderr)
    
    # Check if admin exists
    existing_admin = db.query(AuthUser).filter(AuthUser.role == UserRole.ADMIN).first()
    
    if existing_admin:
        print(f"⚠️  Admin user already exists: {existing_admin.username} (ID: {existing_admin.id})", file=sys.stderr)
        print(f"   Email: {existing_admin.email or 'N/A'}", file=sys.stderr)
        print(f"   Active: {existing_admin.is_active}", file=sys.stderr)
        
        # Test password verification
        if auth_service.verify_password(password, existing_admin.hashed_password):
            print(f"✅ Password verification works correctly", file=sys.stderr)
            print(f"✅ Admin user is ready: username='{username}', password='{password}'", file=sys.stderr)
        else:
            print(f"⚠️  Password verification failed - password might be different", file=sys.stderr)
        
        db.close()
        sys.exit(0)
    
    print("✓ No admin user found - will create one", file=sys.stderr)
    print("", file=sys.stderr)
    
    # Create admin user
    print(f"Step 5: Creating admin user...", file=sys.stderr)
    print(f"   Username: {username}", file=sys.stderr)
    print(f"   Email: {email}", file=sys.stderr)
    print(f"   Role: admin", file=sys.stderr)
    
    try:
        # Hash password
        hashed_password = auth_service.get_password_hash(password)
        print(f"✓ Password hashed", file=sys.stderr)
        
        # Create user
        admin = AuthUser(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin)
        print(f"✓ User added to session", file=sys.stderr)
        
        # Commit transaction
        db.commit()
        print(f"✓ Transaction committed", file=sys.stderr)
        
        # Refresh to get ID
        db.refresh(admin)
        print(f"✓ User refreshed (ID: {admin.id})", file=sys.stderr)
        print("", file=sys.stderr)
        
        # Verify user was created
        print(f"Step 6: Verifying admin user...", file=sys.stderr)
        verify_user = db.query(AuthUser).filter(AuthUser.id == admin.id).first()
        
        if verify_user:
            print(f"✅ User exists in database (ID: {verify_user.id})", file=sys.stderr)
            print(f"   Username: {verify_user.username}", file=sys.stderr)
            print(f"   Email: {verify_user.email}", file=sys.stderr)
            print(f"   Role: {verify_user.role.value}", file=sys.stderr)
            print(f"   Active: {verify_user.is_active}", file=sys.stderr)
            
            # Test password verification
            if auth_service.verify_password(password, verify_user.hashed_password):
                print(f"✅ Password verification works correctly", file=sys.stderr)
                print("", file=sys.stderr)
                print("=" * 60, file=sys.stderr)
                print("  ✅ SUCCESS: Admin user created successfully!", file=sys.stderr)
                print("=" * 60, file=sys.stderr)
                print("", file=sys.stderr)
                print(f"Username: {username}", file=sys.stderr)
                print(f"Password: {password}", file=sys.stderr)
                print(f"Email: {email}", file=sys.stderr)
                print("", file=sys.stderr)
                print("You can now login with these credentials!", file=sys.stderr)
            else:
                print(f"❌ ERROR: Password verification FAILED!", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"❌ ERROR: User was not found after creation!", file=sys.stderr)
            sys.exit(1)
        
    except Exception as e:
        print(f"❌ ERROR: Failed to create admin user: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        db.rollback()
        sys.exit(1)
    finally:
        db.close()
        
except Exception as e:
    print(f"❌ ERROR: Failed to import modules: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

