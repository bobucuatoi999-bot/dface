"""
Direct script to create admin user with provided credentials.
Usage: python create_admin_direct.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, init_db
from app.models.auth import AuthUser, UserRole
from app.services.auth_service import AuthService

def main():
    """Create admin user with provided credentials."""
    print("=" * 60)
    print("  Creating Admin User")
    print("=" * 60)
    
    # Credentials
    username = "123admin"
    password = "duyan2892006"
    email = "admin@facestream.local"
    
    # Initialize database
    print("\nInitializing database...")
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        error_msg = str(e)
        if "Connection refused" in error_msg or "could not connect" in error_msg.lower():
            print("\n" + "="*60)
            print("  DATABASE CONNECTION ERROR")
            print("="*60)
            print("\nPostgreSQL database is not running or not accessible.")
            print("\nPlease:")
            print("1. Start PostgreSQL database")
            print("2. Check DATABASE_URL in .env file")
            print("3. Ensure database server is running on port 5432")
            print("\nThen run this script again.")
            return
        else:
            print(f"Warning: {e}")
    
    db = SessionLocal()
    auth_service = AuthService()
    
    try:
        # Check if admin exists
        existing = db.query(AuthUser).filter(AuthUser.username == username).first()
        if existing:
            print(f"\n⚠️  User '{username}' already exists!")
            response = input("Update password? (y/n): ")
            if response.lower() == 'y':
                existing.hashed_password = auth_service.get_password_hash(password)
                db.commit()
                print(f"\n✅ Password updated for user '{username}'")
            else:
                print("Cancelled.")
            return
        
        # Create admin user
        print(f"\nCreating admin user: {username}")
        admin = auth_service.create_user(
            db=db,
            username=username,
            password=password,
            email=email,
            role=UserRole.ADMIN
        )
        
        print(f"\n✅ Admin user created successfully!")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email or 'N/A'}")
        print(f"   Role: {admin.role.value}")
        print(f"\n💡 Login credentials:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"\n🌐 You can now login at: http://localhost:3000")
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()

