"""
Create admin user via API (if backend is running).
This works even if database connection fails in direct script.
"""

import requests
import json

def create_admin_via_api():
    """Create admin via API endpoint."""
    username = "123admin"
    password = "duyan2892006"
    email = "admin@facestream.local"
    
    # Try to create via API
    url = "http://localhost:8000/api/auth/register"
    
    data = {
        "username": username,
        "password": password,
        "email": email,
        "role": "admin"
    }
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 201:
            print("=" * 60)
            print("  Admin User Created Successfully!")
            print("=" * 60)
            print(f"\nUsername: {username}")
            print(f"Password: {password}")
            print(f"Email: {email}")
            print(f"\nYou can now login at: http://localhost:3000")
            return True
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False
    except requests.exceptions.ConnectionError:
        print("=" * 60)
        print("  Cannot connect to backend API")
        print("=" * 60)
        print("\nPlease ensure:")
        print("1. Backend is running: python -m app.main")
        print("2. Database is configured and running")
        print("\nAlternatively, use the direct script after starting database:")
        print("  python create_admin_direct.py")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    create_admin_via_api()

