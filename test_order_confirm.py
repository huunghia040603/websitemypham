#!/usr/bin/env python3
"""
Script test để kiểm tra API xác nhận đơn hàng
"""

import requests
import json

def test_order_confirm():
    """Test xác nhận đơn hàng"""
    
    # Test 1: Kiểm tra API PythonAnywhere trực tiếp
    print("🔍 Test 1: Kiểm tra API PythonAnywhere trực tiếp")
    print("=" * 50)
    
    order_id = 1  # Thay đổi ID đơn hàng nếu cần
    
    # Test PATCH request
    url = f"https://buddyskincare.pythonanywhere.com/orders/{order_id}/"
    data = {
        "is_confirmed": True,
        "status": "processing"
    }
    
    try:
        response = requests.patch(url, json=data, timeout=30)
        print(f"📡 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ API PythonAnywhere hoạt động bình thường!")
            return True
        else:
            print("❌ API PythonAnywhere cần được cập nhật")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def test_flask_integration():
    """Test integration với Flask"""
    print("\n🔍 Test 2: Kiểm tra Flask integration")
    print("=" * 50)
    
    order_id = 1  # Thay đổi ID đơn hàng nếu cần
    
    # Test Flask API
    url = f"http://localhost:8000/admin/api/orders/{order_id}/confirm"
    
    try:
        response = requests.post(url, timeout=30)
        print(f"📡 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'order_status_updated' in data.get('details', {}):
                if data['details']['order_status_updated']:
                    print("✅ Flask integration hoạt động hoàn toàn!")
                    return True
                else:
                    print("⚠️ Flask integration hoạt động một phần (chỉ cập nhật stock)")
                    return False
            else:
                print("❌ Flask integration không hoạt động")
                return False
        else:
            print("❌ Flask API lỗi")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def main():
    """Chạy tất cả tests"""
    print("🚀 Bắt đầu test API xác nhận đơn hàng")
    print("=" * 60)
    
    # Test 1: PythonAnywhere API
    pythonanywhere_ok = test_order_confirm()
    
    # Test 2: Flask integration
    flask_ok = test_flask_integration()
    
    # Kết quả tổng hợp
    print("\n📊 Kết quả tổng hợp:")
    print("=" * 30)
    print(f"PythonAnywhere API: {'✅ OK' if pythonanywhere_ok else '❌ Cần sửa'}")
    print(f"Flask Integration: {'✅ OK' if flask_ok else '❌ Cần sửa'}")
    
    if pythonanywhere_ok and flask_ok:
        print("\n🎉 Tất cả đều hoạt động bình thường!")
    elif pythonanywhere_ok and not flask_ok:
        print("\n⚠️ PythonAnywhere OK, Flask cần kiểm tra")
    elif not pythonanywhere_ok:
        print("\n🔧 Cần cập nhật Django backend trước")
        print("📋 Xem file ORDER_CONFIRM_FIX.md để biết cách sửa")

if __name__ == "__main__":
    main()
 
 
 
 