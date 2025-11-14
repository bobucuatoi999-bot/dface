"""
Quick test runner - tests the backend without needing a frontend.
"""

import sys
import subprocess
import time

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def check_server_running():
    """Check if server is running."""
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    print_header("FaceStream Backend - Quick Test Runner")
    
    print("\n⚠️  IMPORTANT: How Backend Works Without Frontend")
    print("\nThe backend is an API server - it doesn't have a UI.")
    print("Here's how it works:")
    print("\n1. Backend provides REST API endpoints (HTTP)")
    print("2. Backend provides WebSocket for real-time recognition")
    print("3. Mobile app (frontend) calls these APIs")
    print("4. Backend processes requests and returns JSON")
    print("\nTo test, we simulate what the frontend would do!")
    
    # Check if server is running
    print("\n🔍 Checking if server is running...")
    if not check_server_running():
        print("❌ Server is not running!")
        print("\nPlease start the server first:")
        print("  cd backend")
        print("  python -m app.main")
        print("\nThen run this script again.")
        return
    
    print("✅ Server is running!")
    
    print("\n📋 Available Tests:")
    print("  1. API Endpoints Test (REST API)")
    print("  2. WebSocket Test (Real-time recognition)")
    print("  3. Complete Workflow Test (Full simulation)")
    print("  4. All Tests")
    
    choice = input("\nSelect test (1-4): ").strip()
    
    if choice == "1":
        print_header("Running API Tests")
        subprocess.run([sys.executable, "tests/test_api.py"])
    elif choice == "2":
        print_header("Running WebSocket Tests")
        subprocess.run([sys.executable, "tests/test_websocket.py"])
    elif choice == "3":
        print_header("Running Complete Workflow Tests")
        subprocess.run([sys.executable, "tests/test_complete_workflow.py"])
    elif choice == "4":
        print_header("Running All Tests")
        print("\n1. API Tests...")
        subprocess.run([sys.executable, "tests/test_api.py"])
        time.sleep(2)
        print("\n2. WebSocket Tests...")
        subprocess.run([sys.executable, "tests/test_websocket.py"])
        time.sleep(2)
        print("\n3. Workflow Tests...")
        subprocess.run([sys.executable, "tests/test_complete_workflow.py"])
    else:
        print("Invalid choice!")
        return
    
    print_header("Testing Complete!")
    print("\n💡 Next Steps:")
    print("  - Use Swagger UI for interactive testing: http://localhost:8000/docs")
    print("  - Build mobile frontend that calls these APIs")
    print("  - Frontend will handle UI, backend handles processing")

if __name__ == "__main__":
    main()

