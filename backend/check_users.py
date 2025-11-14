"""
Script to check existing users in database.
Run this to see what users exist and their details.
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
        # Get all users
        users = db.query(AuthUser).all()
        
        print("=" * 60)
        print("  Users in Database")
        print("=" * 60)
        
        if not users:
            print("\n❌ No users found in database!")
            print("\nTo create an admin user, run:")
            print("  python scripts/create_admin.py")
        else:
            print(f"\nFound {len(users)} user(s):\n")
            for user in users:
                print(f"ID: {user.id}")
                print(f"  Username: {user.username}")
                print(f"  Email: {user.email or 'N/A'}")
                print(f"  Role: {user.role.value}")
                print(f"  Active: {user.is_active}")
                print(f"  Created: {user.created_at}")
                print(f"  Last Login: {user.last_login or 'Never'}")
                print()
            
            # Check for admin users
            admins = [u for u in users if u.role == UserRole.ADMIN]
            if admins:
                print(f"✅ Found {len(admins)} admin user(s):")
                for admin in admins:
                    print(f"  - {admin.username} (Active: {admin.is_active})")
                print("\n💡 Try logging in with one of these usernames!")
            else:
                print("⚠️  No admin users found!")
                print("\nTo create an admin user, run:")
                print("  python scripts/create_admin.py")
                print("\nOr the admin will be auto-created on next startup.")
            
            # Test password verification for admin users
            if admins:
                print("\n" + "=" * 60)
                print("  Testing Password Verification")
                print("=" * 60)
                test_password = "admin123"
                for admin in admins:
                    if auth_service.verify_password(test_password, admin.hashed_password):
                        print(f"✅ User '{admin.username}': Password 'admin123' is CORRECT")
                    else:
                        print(f"❌ User '{admin.username}': Password 'admin123' is INCORRECT")
                        print(f"   (This user might have a different password)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        
except Exception as e:
    print(f"❌ Failed to import modules: {e}")
    import traceback
    traceback.print_exc()

