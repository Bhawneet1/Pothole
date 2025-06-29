import requests
import os
import time

def test_web_app():
    """Test the web application with sample files"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing Pothole Detection Web Application")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("1. Testing server connectivity...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the server is running with: python web_app.py")
        return
    
    # Test 2: Check available test files
    print("\n2. Checking for test files...")
    test_files = []
    
    # Check for video files
    if os.path.exists("p.mp4"):
        test_files.append(("p.mp4", "video"))
        print("✅ Found test video: p.mp4")
    
    # Check for images in DetekcijaRupa-main/imgs/
    imgs_dir = "DetekcijaRupa-main/imgs"
    if os.path.exists(imgs_dir):
        for file in os.listdir(imgs_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                test_files.append((os.path.join(imgs_dir, file), "image"))
                print(f"✅ Found test image: {file}")
    
    if not test_files:
        print("❌ No test files found")
        print("Please add some test images or videos to test with")
        return
    
    # Test 3: Test file upload
    print(f"\n3. Testing file upload with {len(test_files)} files...")
    
    for file_path, file_type in test_files:
        print(f"\n📁 Testing {file_type}: {os.path.basename(file_path)}")
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
                
                print("   Uploading file...")
                response = requests.post(f"{base_url}/upload", files=files, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print(f"   ✅ {file_type.capitalize()} processed successfully!")
                        print(f"   📊 Detections: {data['results'].get('statistics', {}).get('total_detections', 0)}")
                        
                        # Show download links
                        if 'download_url' in data['results']:
                            print(f"   📥 Download: {base_url}{data['results']['download_url']}")
                        if 'video_url' in data['results']:
                            print(f"   📥 Video: {base_url}{data['results']['video_url']}")
                        if 'csv_url' in data['results']:
                            print(f"   📥 CSV: {base_url}{data['results']['csv_url']}")
                    else:
                        print(f"   ❌ Processing failed: {data.get('error', 'Unknown error')}")
                else:
                    print(f"   ❌ Upload failed with status code: {response.status_code}")
                    print(f"   Response: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Error testing {file_path}: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")
    print(f"🌐 Access your web app at: {base_url}")
    print("📝 Manual testing steps:")
    print("   1. Open the URL in your browser")
    print("   2. Upload an image or video file")
    print("   3. Wait for processing")
    print("   4. View results and download processed files")

if __name__ == "__main__":
    test_web_app() 