"""
Script to create an admin user for authentication.
Run this to set up the first admin user.
"""

import sys
from app.database import SessionLocal, init_db
from app.models.auth import AuthUser, UserRole
from app.services.auth_service import AuthService

def main():
    """Create admin user."""
    print("=" * 60)
    print("  Create Admin User")
    print("=" * 60)
    
    # Initialize database
    print("\nInitializing database...")
    init_db()
    
    db = SessionLocal()
    auth_service = AuthService()
    
    try:
        # Check if admin exists
        existing = db.query(AuthUser).filter(AuthUser.role == UserRole.ADMIN).first()
        if existing:
            print(f"\n⚠️  Admin user already exists: {existing.username}")
            response = input("Create another admin? (y/n): ")
            if response.lower() != 'y':
                print("Cancelled.")
                return
        
        # Get admin details
        print("\nEnter admin user details:")
        username = input("Username: ").strip()
        if not username:
            print("❌ Username is required!")
            return
        
        password = input("Password: ").strip()
        if not password or len(password) < 6:
            print("❌ Password must be at least 6 characters!")
            return
        
        email = input("Email (optional): ").strip() or None
        
        # Create admin user
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
        print(f"\n💡 You can now login at: POST /api/auth/login")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()

