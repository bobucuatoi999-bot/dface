"""
Test script for WebSocket real-time recognition.
Simulates the mobile app sending video frames.
"""

import asyncio
import websockets
import json
import base64
import time
from pathlib import Path

# Configuration
WS_URL = "ws://localhost:8000/ws/recognize"

def create_dummy_image_base64():
    """
    Create a dummy base64 image for testing.
    In production, this would be actual camera frames.
    """
    # Minimal 1x1 pixel PNG
    minimal_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    return base64.b64encode(minimal_png).decode('utf-8')

def load_image_base64(image_path):
    """Load an actual image file and convert to base64."""
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Image not found: {image_path}")
        return None

async def test_websocket_connection():
    """Test basic WebSocket connection."""
    print("\n" + "=" * 60)
    print("  Testing WebSocket Connection")
    print("=" * 60)
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ Connected to WebSocket")
            
            # Receive connection confirmation
            message = await websocket.recv()
            data = json.loads(message)
            print(f"📨 Received: {json.dumps(data, indent=2)}")
            
            # Send ping
            print("\n📤 Sending ping...")
            await websocket.send(json.dumps({
                "type": "ping",
                "timestamp": int(time.time())
            }))
            
            # Receive pong
            response = await websocket.recv()
            pong = json.loads(response)
            print(f"📨 Received pong: {json.dumps(pong, indent=2)}")
            
            print("\n✅ WebSocket connection test passed!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_frame_processing():
    """Test sending frames for recognition."""
    print("\n" + "=" * 60)
    print("  Testing Frame Processing")
    print("=" * 60)
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ Connected")
            
            # Receive connection message
            await websocket.recv()
            
            # Send test frame
            print("\n📤 Sending test frame...")
            frame_data = create_dummy_image_base64()
            
            await websocket.send(json.dumps({
                "type": "frame",
                "data": frame_data,
                "timestamp": int(time.time() * 1000),
                "frame_id": 1
            }))
            
            # Wait for response
            print("⏳ Waiting for recognition result...")
            response = await websocket.recv()
            result = json.loads(response)
            
            print(f"📨 Recognition Result:")
            print(json.dumps(result, indent=2))
            
            if result.get("type") == "recognition_result":
                faces = result.get("faces", [])
                print(f"\n✅ Processed frame: {len(faces)} face(s) detected")
                for face in faces:
                    if face.get("is_unknown"):
                        print(f"   - Unknown person (Track: {face.get('track_id')})")
                    else:
                        print(f"   - {face.get('user_name')} (Confidence: {face.get('confidence', 0):.2%})")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_multiple_frames():
    """Test sending multiple frames (simulating video stream)."""
    print("\n" + "=" * 60)
    print("  Testing Multiple Frames (Video Simulation)")
    print("=" * 60)
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ Connected")
            
            # Receive connection message
            await websocket.recv()
            
            # Send 5 frames (simulating 5 FPS)
            print("\n📤 Sending 5 frames at 5 FPS...")
            frame_data = create_dummy_image_base64()
            
            for i in range(5):
                await websocket.send(json.dumps({
                    "type": "frame",
                    "data": frame_data,
                    "timestamp": int(time.time() * 1000),
                    "frame_id": i + 1
                }))
                
                # Wait a bit (simulating 5 FPS = 200ms between frames)
                await asyncio.sleep(0.2)
                
                # Try to receive response (non-blocking)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                    result = json.loads(response)
                    if result.get("type") == "recognition_result":
                        faces = result.get("faces", [])
                        print(f"  Frame {i+1}: {len(faces)} face(s)")
                except asyncio.TimeoutError:
                    pass  # No response yet, continue
            
            print("\n✅ Multiple frames test completed!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_with_real_image(image_path):
    """Test with a real image file."""
    print("\n" + "=" * 60)
    print(f"  Testing with Real Image: {image_path}")
    print("=" * 60)
    
    image_data = load_image_base64(image_path)
    if not image_data:
        print("❌ Could not load image")
        return False
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ Connected")
            
            # Receive connection message
            await websocket.recv()
            
            # Send frame with real image
            print("\n📤 Sending frame with real image...")
            await websocket.send(json.dumps({
                "type": "frame",
                "data": image_data,
                "timestamp": int(time.time() * 1000),
                "frame_id": 1
            }))
            
            # Wait for response
            print("⏳ Processing...")
            response = await websocket.recv()
            result = json.loads(response)
            
            print(f"\n📨 Result:")
            print(json.dumps(result, indent=2))
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all WebSocket tests."""
    print("\n" + "=" * 60)
    print("  FaceStream WebSocket Test Suite")
    print("=" * 60)
    print(f"\nTesting: {WS_URL}")
    print("Make sure the server is running!")
    print("\nPress Enter to start testing...")
    input()
    
    # Test 1: Basic connection
    await test_websocket_connection()
    
    # Test 2: Frame processing
    await test_frame_processing()
    
    # Test 3: Multiple frames
    await test_multiple_frames()
    
    # Test 4: Real image (if provided)
    import sys
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        await test_with_real_image(image_path)
    else:
        print("\n💡 Tip: Provide an image path to test with real images:")
        print("   python test_websocket.py path/to/image.jpg")
    
    print("\n" + "=" * 60)
    print("  Testing Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())

