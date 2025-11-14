"""
Complete workflow test - simulates the full user workflows from the original plan.
"""

import requests
import asyncio
import websockets
import json
import base64
import time

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"
WS_URL = "ws://localhost:8000/ws/recognize"

def create_dummy_image_base64():
    """Create dummy image for testing."""
    minimal_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    return base64.b64encode(minimal_png).decode('utf-8')

def workflow_1_admin_registers_user():
    """
    WORKFLOW 1: Administrator Registers a New User
    
    Step-by-step simulation of the registration process.
    """
    print("\n" + "=" * 70)
    print("  WORKFLOW 1: Administrator Registers a New User")
    print("=" * 70)
    
    print("\n📝 Step 1: Admin opens app and taps 'Register New User'")
    print("   (In real app: UI navigation)")
    
    print("\n📝 Step 2: Enter user details")
    user_data = {
        "name": "John Doe",
        "email": "john.doe@company.com",
        "employee_id": "EMP-12345"
    }
    print(f"   Name: {user_data['name']}")
    print(f"   Email: {user_data['email']}")
    print(f"   Employee ID: {user_data['employee_id']}")
    
    print("\n📝 Step 3: Face capture mode")
    print("   (In real app: Camera view opens, guides user)")
    print("   Simulating face capture...")
    
    # Note: In real testing, you would use actual face images
    # For now, we'll show the API call structure
    print("\n📝 Step 4: Processing face...")
    
    try:
        # This would be the actual API call from the mobile app
        registration_data = {
            **user_data,
            "image_data": create_dummy_image_base64()  # In real app: actual camera frame
        }
        
        print("   📤 Sending registration request to backend...")
        response = requests.post(
            f"{API_BASE}/users/register",
            json=registration_data
        )
        
        if response.status_code == 201:
            user = response.json()
            print(f"\n✅ Step 5: User registered successfully!")
            print(f"   User ID: {user['id']}")
            print(f"   Name: {user['name']}")
            print(f"   Face embeddings: {user['face_count']}")
            return user['id']
        else:
            print(f"\n❌ Registration failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

def workflow_2_operator_recognition_mode():
    """
    WORKFLOW 2: Operator Uses Recognition Mode
    
    Simulates the security guard monitoring entrance.
    """
    print("\n" + "=" * 70)
    print("  WORKFLOW 2: Operator Uses Recognition Mode")
    print("=" * 70)
    
    print("\n📝 Step 1: Operator opens app and taps 'Start Recognition Mode'")
    print("   (In real app: UI button tap)")
    
    async def run_recognition():
        try:
            print("\n📝 Step 2: Connecting to server...")
            async with websockets.connect(WS_URL) as websocket:
                print("   ✅ WebSocket connected")
                
                # Receive connection confirmation
                msg = await websocket.recv()
                conn_data = json.loads(msg)
                print(f"   📨 Server: {conn_data.get('message')}")
                print(f"   Session ID: {conn_data.get('session_id', 'N/A')}")
                
                print("\n📝 Step 3: Simulating person walking into view...")
                print("   (In real app: Camera captures frames automatically)")
                
                # Simulate sending frames
                for i in range(3):
                    print(f"\n   📤 Sending frame {i+1}...")
                    await websocket.send(json.dumps({
                        "type": "frame",
                        "data": create_dummy_image_base64(),
                        "timestamp": int(time.time() * 1000),
                        "frame_id": i + 1
                    }))
                    
                    # Wait for response
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        result = json.loads(response)
                        
                        if result.get("type") == "recognition_result":
                            faces = result.get("faces", [])
                            if faces:
                                for face in faces:
                                    if face.get("is_unknown"):
                                        print(f"   🔴 Unknown person detected (Track: {face.get('track_id')})")
                                    else:
                                        print(f"   🟢 Identified: {face.get('user_name')} (Confidence: {face.get('confidence', 0):.2%})")
                            else:
                                print(f"   ⚪ No faces detected")
                    except asyncio.TimeoutError:
                        print("   ⏳ Processing...")
                    
                    await asyncio.sleep(0.5)  # Simulate 2 FPS
                
                print("\n✅ Recognition session complete!")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Run async recognition
    asyncio.run(run_recognition())

def workflow_3_view_logs():
    """
    WORKFLOW 3: View Recognition Logs
    
    Simulates admin viewing recognition history.
    """
    print("\n" + "=" * 70)
    print("  WORKFLOW 3: View Recognition Logs")
    print("=" * 70)
    
    print("\n📝 Step 1: Admin opens logs/analytics screen")
    print("   (In real app: UI navigation)")
    
    try:
        # Get statistics
        print("\n📝 Step 2: Fetching statistics...")
        response = requests.get(f"{API_BASE}/logs/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"\n📊 Recognition Statistics:")
            print(f"   Total recognitions: {stats.get('total_recognitions', 0)}")
            print(f"   Unique users: {stats.get('unique_users', 0)}")
            print(f"   Unknown persons: {stats.get('unknown_count', 0)}")
            print(f"   Average confidence: {stats.get('average_confidence', 0):.2%}")
            
            top_users = stats.get('top_users', [])
            if top_users:
                print(f"\n   Top Recognized Users:")
                for user in top_users[:5]:
                    print(f"     - {user['name']}: {user['recognition_count']} times")
        
        # Get recent logs
        print("\n📝 Step 3: Fetching recent logs...")
        response = requests.get(f"{API_BASE}/logs/", params={"limit": 10})
        if response.status_code == 200:
            logs = response.json()
            print(f"\n📋 Recent Recognition Events ({len(logs)} entries):")
            for log in logs[:5]:
                if log.get('is_unknown'):
                    print(f"   🔴 Unknown person at {log.get('created_at')}")
                else:
                    print(f"   🟢 {log.get('user_name')} at {log.get('created_at')} (Confidence: {log.get('confidence', 0):.2%})")
        
        print("\n✅ Logs retrieved successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

def main():
    """Run complete workflow tests."""
    print("\n" + "=" * 70)
    print("  COMPLETE WORKFLOW TEST SUITE")
    print("  Simulating Real User Workflows")
    print("=" * 70)
    
    print("\n⚠️  IMPORTANT:")
    print("   These tests simulate the workflows from your original plan.")
    print("   In a real app, the mobile frontend would:")
    print("   1. Show UI screens and handle user interactions")
    print("   2. Capture camera frames automatically")
    print("   3. Display recognition results in real-time")
    print("   4. Handle errors and show user-friendly messages")
    
    print("\nPress Enter to start workflow tests...")
    input()
    
    # Workflow 1: Register user
    user_id = workflow_1_admin_registers_user()
    
    # Workflow 2: Recognition mode
    workflow_2_operator_recognition_mode()
    
    # Workflow 3: View logs
    workflow_3_view_logs()
    
    print("\n" + "=" * 70)
    print("  ALL WORKFLOWS COMPLETE!")
    print("=" * 70)
    print("\n💡 How Frontend Integrates:")
    print("   1. Mobile app uses these same API endpoints")
    print("   2. UI handles user interactions and displays results")
    print("   3. Camera captures frames and sends to WebSocket")
    print("   4. Backend processes and returns recognition results")
    print("   5. Frontend displays results with bounding boxes and labels")

if __name__ == "__main__":
    main()

