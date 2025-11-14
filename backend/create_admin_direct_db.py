"""
Create admin user by directly inserting into database.
This script uses bcrypt directly and works even if passlib has issues.
"""

import sys
import os
import bcrypt

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("=" * 60, file=sys.stderr)
    print("  Creating Admin User (Direct Database Method)", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("", file=sys.stderr)
    
    from app.database import SessionLocal, engine, Base
    from app.models.auth import AuthUser, UserRole
    from sqlalchemy import text
    
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
    
    # Credentials
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin123")
    email = os.getenv("ADMIN_EMAIL", "admin@facestream.local")
    
    print(f"Step 3: Checking if admin user exists...", file=sys.stderr)
    print(f"   Username: {username}", file=sys.stderr)
    
    # Check if admin exists
    existing_admin = db.query(AuthUser).filter(AuthUser.role == UserRole.ADMIN).first()
    
    if existing_admin:
        print(f"⚠️  Admin user already exists: {existing_admin.username} (ID: {existing_admin.id})", file=sys.stderr)
        print(f"   Email: {existing_admin.email or 'N/A'}", file=sys.stderr)
        print(f"   Active: {existing_admin.is_active}", file=sys.stderr)
        
        # Test password
        password_bytes = password.encode('utf-8')
        if bcrypt.checkpw(password_bytes, existing_admin.hashed_password.encode('utf-8')):
            print(f"✅ Password verification works correctly", file=sys.stderr)
            print(f"✅ Admin user is ready: username='{username}', password='{password}'", file=sys.stderr)
        else:
            print(f"⚠️  Password verification failed - password might be different", file=sys.stderr)
        
        db.close()
        sys.exit(0)
    
    print("✓ No admin user found - will create one", file=sys.stderr)
    print("", file=sys.stderr)
    
    # Create admin user using bcrypt directly
    print(f"Step 4: Creating admin user...", file=sys.stderr)
    print(f"   Username: {username}", file=sys.stderr)
    print(f"   Email: {email}", file=sys.stderr)
    print(f"   Role: admin", file=sys.stderr)
    
    try:
        # Hash password using bcrypt directly (no passlib)
        print("   Hashing password with bcrypt (direct)...", file=sys.stderr)
        password_bytes = password.encode('utf-8')
        hashed_password_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))
        hashed_password = hashed_password_bytes.decode('utf-8')
        print(f"✓ Password hashed successfully", file=sys.stderr)
        
        # Create user object
        admin = AuthUser(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=UserRole.ADMIN,
            is_active=True
        )
        
        # Add to database
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
        print(f"Step 5: Verifying admin user...", file=sys.stderr)
        verify_user = db.query(AuthUser).filter(AuthUser.id == admin.id).first()
        
        if verify_user:
            print(f"✅ User exists in database (ID: {verify_user.id})", file=sys.stderr)
            print(f"   Username: {verify_user.username}", file=sys.stderr)
            print(f"   Email: {verify_user.email}", file=sys.stderr)
            print(f"   Role: {verify_user.role.value}", file=sys.stderr)
            print(f"   Active: {verify_user.is_active}", file=sys.stderr)
            
            # Test password verification
            print("   Testing password verification...", file=sys.stderr)
            if bcrypt.checkpw(password_bytes, verify_user.hashed_password.encode('utf-8')):
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

