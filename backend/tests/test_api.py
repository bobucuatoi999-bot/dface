"""
Test script for API endpoints.
Run this to test all API functionality.
"""

import requests
import base64
import json
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def create_test_image_base64():
    """
    Create a simple test image (1x1 pixel PNG) encoded as base64.
    In real testing, you would use actual face images.
    """
    # This is a minimal 1x1 pixel PNG (transparent)
    # For real testing, replace with actual face image
    minimal_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    return base64.b64encode(minimal_png).decode('utf-8')

def test_health_check():
    """Test health check endpoint."""
    print_section("Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_create_user():
    """Test creating a user without face."""
    print_section("Testing Create User (No Face)")
    try:
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "employee_id": "TEST-001"
        }
        response = requests.post(f"{API_BASE}/users/", json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            user = response.json()
            print(f"Created User: {json.dumps(user, indent=2, default=str)}")
            return user.get("id")
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_get_all_users():
    """Test getting all users."""
    print_section("Testing Get All Users")
    try:
        response = requests.get(f"{API_BASE}/users/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            print(f"Found {len(users)} users")
            for user in users:
                print(f"  - {user['name']} (ID: {user['id']}, Faces: {user['face_count']})")
            return users
        else:
            print(f"Error: {response.text}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def test_get_user(user_id):
    """Test getting a specific user."""
    print_section(f"Testing Get User (ID: {user_id})")
    try:
        response = requests.get(f"{API_BASE}/users/{user_id}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            user = response.json()
            print(f"User: {json.dumps(user, indent=2, default=str)}")
            return user
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_update_user(user_id):
    """Test updating a user."""
    print_section(f"Testing Update User (ID: {user_id})")
    try:
        data = {
            "name": "Updated Test User",
            "is_active": True
        }
        response = requests.put(f"{API_BASE}/users/{user_id}", json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            user = response.json()
            print(f"Updated User: {json.dumps(user, indent=2, default=str)}")
            return user
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_get_logs():
    """Test getting recognition logs."""
    print_section("Testing Get Recognition Logs")
    try:
        response = requests.get(f"{API_BASE}/logs/", params={"limit": 10})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            logs = response.json()
            print(f"Found {len(logs)} log entries")
            for log in logs[:5]:  # Show first 5
                print(f"  - {log.get('user_name', 'Unknown')} at {log.get('created_at')}")
            return logs
        else:
            print(f"Error: {response.text}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def test_get_stats():
    """Test getting recognition statistics."""
    print_section("Testing Get Statistics")
    try:
        response = requests.get(f"{API_BASE}/logs/stats")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"Statistics: {json.dumps(stats, indent=2, default=str)}")
            return stats
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_get_sessions():
    """Test getting recognition sessions."""
    print_section("Testing Get Sessions")
    try:
        response = requests.get(f"{API_BASE}/logs/sessions", params={"limit": 5})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            sessions = response.json()
            print(f"Found {len(sessions)} sessions")
            for session in sessions:
                print(f"  - Session {session['session_id'][:8]}... ({session['total_recognitions']} recognitions)")
            return sessions
        else:
            print(f"Error: {response.text}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("  FaceStream Backend API Test Suite")
    print("=" * 60)
    print(f"\nTesting against: {BASE_URL}")
    print("Make sure the server is running!")
    print("\nPress Enter to start testing...")
    input()
    
    # Test health check
    if not test_health_check():
        print("\n❌ Health check failed! Is the server running?")
        return
    
    # Test user management
    user_id = test_create_user()
    if user_id:
        test_get_user(user_id)
        test_update_user(user_id)
    
    test_get_all_users()
    
    # Test logs
    test_get_logs()
    test_get_stats()
    test_get_sessions()
    
    print_section("Testing Complete!")
    print("\nNote: Face registration tests require actual face images.")
    print("See test_websocket.py for WebSocket testing.")
    print("See test_with_images.py for image-based testing.")

if __name__ == "__main__":
    main()

