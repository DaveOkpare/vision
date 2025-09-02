#!/usr/bin/env python3
"""
Simple test script for the FastAPI backend
"""
import requests
import os
import sys

def test_api():
    """Test the FastAPI detection endpoint"""
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/")
        print(f"✅ Server is running: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Start it with: uv run python api_server.py")
        return
    
    # Find a test image
    test_images = ["test_image.jpg", "street.jpg", "time.jpg", "plan.jpg"]
    test_image = None
    
    for img in test_images:
        if os.path.exists(img):
            test_image = img
            break
    
    if not test_image:
        print("❌ No test image found. Available images:", test_images)
        return
    
    print(f"📷 Using test image: {test_image}")
    
    # Test single object detection
    print("\n🔍 Testing single object detection...")
    with open(test_image, 'rb') as f:
        files = {'file': f}
        data = {'targets': 'car'}
        
        response = requests.post("http://localhost:8000/api/detect", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Single detection successful!")
            print(f"   - Image URL: {result['imageUrl']}")
            print(f"   - Targets: {result['targets']}")
            print(f"   - Results: {len(result['results'])} detections")
            for r in result['results']:
                print(f"     * {r['object']}: {r['confidence']} ({r['confidence_score']:.1f}%)")
        else:
            print(f"❌ Single detection failed: {response.status_code} - {response.text}")
    
    # Test multi-object detection
    print("\n🔍 Testing multi-object detection...")
    with open(test_image, 'rb') as f:
        files = {'file': f}
        data = {'targets': 'car, person, building'}
        
        response = requests.post("http://localhost:8000/api/detect", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Multi-detection successful!")
            print(f"   - Image URL: {result['imageUrl']}")
            print(f"   - Targets: {result['targets']}")
            print(f"   - Results: {len(result['results'])} detections")
            for r in result['results']:
                print(f"     * {r['object']}: {r['confidence']} ({r['confidence_score']:.1f}%)")
        else:
            print(f"❌ Multi-detection failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check-env":
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            print("✅ OPENAI_API_KEY is set")
        else:
            print("❌ OPENAI_API_KEY environment variable is not set")
            print("Set it with: export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(0)
    
    test_api()