#!/usr/bin/env python3
"""
Script để deploy code lên PythonAnywhere qua web interface
Bạn cần chạy script này trên PythonAnywhere console
"""

import os
import shutil
from pathlib import Path

def deploy_files():
    """Deploy files locally on PythonAnywhere"""
    
    # Đường dẫn trên PythonAnywhere
    project_path = Path("/home/buddyskincare/websitemypham")
    
    print("🚀 Deploying files to PythonAnywhere...")
    
    # Files cần deploy
    files_to_deploy = [
        "app.py",
        "static/js/main.js", 
        "views.py",
        "urls.py"
    ]
    
    for file_path in files_to_deploy:
        source = Path(file_path)
        if source.exists():
            destination = project_path / source
            # Tạo thư mục nếu chưa có
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source, destination)
            print(f"✅ Deployed: {file_path}")
        else:
            print(f"❌ File not found: {file_path}")
    
    print("\n✅ Deployment completed!")
    print("🔄 Please reload your web app")
    
    # Kiểm tra endpoint
    print("\n🧪 Testing endpoints...")
    test_endpoints()

def test_endpoints():
    """Test if endpoints are working"""
    import requests
    
    base_url = "https://buddyskincare.vn"
    endpoints = [
        "/backend/api/upload-bank-transfer/",
        "/api/upload-bank-transfer"
    ]
    
    for endpoint in endpoints:
        try:
            # Test với HEAD request
            response = requests.head(f"{base_url}{endpoint}", timeout=5)
            status = "✅" if response.status_code != 404 else "❌"
            print(f"{status} {endpoint} -> {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} -> Error: {e}")

if __name__ == "__main__":
    deploy_files()