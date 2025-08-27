#!/usr/bin/env python3
"""
BeautySale - Website Bán Mỹ Phẩm Thanh Lý
File chạy chính cho ứng dụng Flask
"""

import os
import sys
from app import app

def check_dependencies():
    """Kiểm tra và cài đặt dependencies nếu cần"""
    try:
        import flask
        print("✅ Flask đã được cài đặt")
    except ImportError:
        print("❌ Flask chưa được cài đặt")
        print("🔧 Đang cài đặt dependencies...")
        os.system(f"{sys.executable} -m pip install -r requirements.txt")
        print("✅ Đã cài đặt xong dependencies")

def create_directories():
    """Tạo các thư mục cần thiết"""
    directories = [
        'static',
        'static/css',
        'static/js', 
        'static/image',
        'templates'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Đã tạo thư mục: {directory}")

def main():
    """Hàm chính để chạy ứng dụng"""
    print("=" * 60)
    print("🛍️  BeautySale - Website Bán Mỹ Phẩm Thanh Lý")
    print("=" * 60)
    
    # Kiểm tra dependencies
    check_dependencies()
    
    # Tạo thư mục
    create_directories()
    
    print("\n🚀 Đang khởi động server...")
    print("📱 Website sẽ chạy tại: http://localhost:8000")
    print("🛍️  Trang chủ: http://localhost:8000/")
    print("📦 Sản phẩm: http://localhost:8000/products")
    print("🛒 Giỏ hàng: http://localhost:8000/cart")
    print("💳 Thanh toán: http://localhost:8000/checkout")
    
    print("\n✨ Tính năng demo:")
    print("   • Flash sale với countdown timer")
    print("   • Bộ lọc sản phẩm đa tiêu chí")
    print("   • Đánh giá và bình luận")
    print("   • Responsive design")
    print("   • Add to cart với animation")
    print("   • Newsletter subscription")
    print("   • Search API")
    
    print("\n🔧 Để dừng server: Nhấn Ctrl+C")
    print("=" * 60)
    
    # Chạy Flask app
    app.run(
        debug=True,
        host='0.0.0.0',
        port=8000,
        use_reloader=True
    )

if __name__ == '__main__':
    main() 