#!/usr/bin/env python3
"""
Setup script cho BeautySale Website
Tạo môi trường ảo và cài đặt dependencies
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Chạy lệnh và hiển thị kết quả"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} thành công")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} thất bại: {e}")
        return False

def check_python_version():
    """Kiểm tra phiên bản Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Cần Python 3.7 trở lên")
        print(f"   Phiên bản hiện tại: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def create_virtual_environment():
    """Tạo môi trường ảo"""
    venv_name = "beautysale_env"
    
    if os.path.exists(venv_name):
        print(f"📁 Môi trường ảo '{venv_name}' đã tồn tại")
        return venv_name
    
    print(f"🔧 Tạo môi trường ảo '{venv_name}'...")
    if run_command(f"{sys.executable} -m venv {venv_name}", "Tạo môi trường ảo"):
        return venv_name
    return None

def get_activate_script(venv_name):
    """Lấy đường dẫn script kích hoạt môi trường ảo"""
    system = platform.system().lower()
    
    if system == "windows":
        return os.path.join(venv_name, "Scripts", "activate")
    else:
        return os.path.join(venv_name, "bin", "activate")

def install_dependencies(venv_name):
    """Cài đặt dependencies trong môi trường ảo"""
    system = platform.system().lower()
    
    if system == "windows":
        pip_path = os.path.join(venv_name, "Scripts", "pip")
    else:
        pip_path = os.path.join(venv_name, "bin", "pip")
    
    if not os.path.exists(pip_path):
        print(f"❌ Không tìm thấy pip tại: {pip_path}")
        return False
    
    return run_command(f'"{pip_path}" install -r requirements.txt', "Cài đặt dependencies")

def create_run_scripts(venv_name):
    """Tạo script chạy cho các hệ điều hành khác nhau"""
    system = platform.system().lower()
    
    if system == "windows":
        # Windows batch script
        with open("run.bat", "w", encoding="utf-8") as f:
            f.write(f"""@echo off
echo 🛍️ BeautySale - Website Bán Mỹ Phẩm Thanh Lý
echo.
call {venv_name}\\Scripts\\activate
python run.py
pause
""")
        print("✅ Đã tạo run.bat")
        
    else:
        # Unix/Linux/Mac shell script
        with open("run.sh", "w") as f:
            f.write(f"""#!/bin/bash
echo "🛍️ BeautySale - Website Bán Mỹ Phẩm Thanh Lý"
echo ""
source {venv_name}/bin/activate
python run.py
""")
        # Cấp quyền thực thi
        os.chmod("run.sh", 0o755)
        print("✅ Đã tạo run.sh")

def main():
    """Hàm chính"""
    print("=" * 60)
    print("🛍️  BeautySale - Setup Môi Trường Ảo")
    print("=" * 60)
    
    # Kiểm tra Python version
    if not check_python_version():
        sys.exit(1)
    
    # Tạo môi trường ảo
    venv_name = create_virtual_environment()
    if not venv_name:
        print("❌ Không thể tạo môi trường ảo")
        sys.exit(1)
    
    # Cài đặt dependencies
    if not install_dependencies(venv_name):
        print("❌ Không thể cài đặt dependencies")
        sys.exit(1)
    
    # Tạo script chạy
    create_run_scripts(venv_name)
    
    print("\n" + "=" * 60)
    print("🎉 Setup hoàn tất!")
    print("=" * 60)
    
    system = platform.system().lower()
    if system == "windows":
        print("\n🚀 Để chạy website:")
        print("   • Double-click file 'run.bat'")
        print("   • Hoặc mở Command Prompt và chạy: run.bat")
    else:
        print("\n🚀 Để chạy website:")
        print("   • Mở Terminal và chạy: ./run.sh")
        print("   • Hoặc chạy: python run.py")
    
    print("\n📱 Website sẽ chạy tại: http://localhost:8000")
    print("🔧 Để dừng server: Nhấn Ctrl+C")
    
    print("\n📚 Hướng dẫn chi tiết:")
    print("   • Xem file README.md để biết thêm thông tin")
    print("   • Truy cập: http://localhost:8000 để xem website")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main() 