#!/usr/bin/env python3
"""
Script test API sau khi cập nhật views.py
"""

import requests
import json
import time

def test_pythonanywhere_api():
    """Test API PythonAnywhere trực tiếp"""
    print("🔍 Test 1: API PythonAnywhere trực tiếp")
    print("=" * 50)
    
    order_id = 1  # Thay đổi ID đơn hàng nếu cần
    
    # Test PATCH request
    url = f"https://buddyskincare.pythonanywhere.com/orders/{order_id}/"
    data = {
        "is_confirmed": True,
        "status": "processing"
    }
    
    try:
        print(f"📡 Testing: {url}")
        print(f"📄 Data: {json.dumps(data, indent=2)}")
        
        response = requests.patch(url, json=data, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ API PythonAnywhere hoạt động bình thường!")
            return True
        elif response.status_code == 401:
            print("❌ API vẫn yêu cầu authentication - cần cập nhật views.py")
            return False
        else:
            print(f"⚠️ API trả về status code không mong đợi: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def test_flask_integration():
    """Test integration với Flask"""
    print("\n🔍 Test 2: Flask integration")
    print("=" * 50)
    
    order_id = 1  # Thay đổi ID đơn hàng nếu cần
    
    # Test Flask API
    url = f"http://localhost:8000/admin/api/orders/{order_id}/confirm"
    
    try:
        print(f"📡 Testing: {url}")
        
        response = requests.post(url, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                if 'order_status_updated' in data.get('details', {}):
                    if data['details']['order_status_updated']:
                        print("✅ Flask integration hoạt động hoàn toàn!")
                        return True
                    else:
                        print("⚠️ Flask integration hoạt động một phần (chỉ cập nhật stock)")
                        return False
                else:
                    print("✅ Flask integration hoạt động (không có chi tiết)")
                    return True
            else:
                print("❌ Flask integration không hoạt động")
                return False
        else:
            print(f"❌ Flask API lỗi: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def test_order_status():
    """Test kiểm tra trạng thái đơn hàng"""
    print("\n🔍 Test 3: Kiểm tra trạng thái đơn hàng")
    print("=" * 50)
    
    order_id = 1  # Thay đổi ID đơn hàng nếu cần
    
    # Lấy thông tin đơn hàng
    url = f"https://buddyskincare.pythonanywhere.com/orders/{order_id}/"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"📦 Order ID: {data.get('id')}")
            print(f"📦 is_confirmed: {data.get('is_confirmed')}")
            print(f"📦 status: {data.get('status')}")
            print(f"📦 customer_name: {data.get('customer_name')}")
            print(f"📦 phone_number: {data.get('phone_number')}")
            return True
        else:
            print(f"❌ Không thể lấy thông tin đơn hàng: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def main():
    """Chạy tất cả tests"""
    print("🚀 Test API sau khi cập nhật views.py")
    print("=" * 60)
    
    # Test 1: PythonAnywhere API
    pythonanywhere_ok = test_pythonanywhere_api()
    
    # Test 2: Flask integration
    flask_ok = test_flask_integration()
    
    # Test 3: Order status
    order_status_ok = test_order_status()
    
    # Kết quả tổng hợp
    print("\n📊 Kết quả tổng hợp:")
    print("=" * 30)
    print(f"PythonAnywhere API: {'✅ OK' if pythonanywhere_ok else '❌ Cần sửa'}")
    print(f"Flask Integration: {'✅ OK' if flask_ok else '❌ Cần sửa'}")
    print(f"Order Status: {'✅ OK' if order_status_ok else '❌ Cần sửa'}")
    
    if pythonanywhere_ok and flask_ok and order_status_ok:
        print("\n🎉 Tất cả đều hoạt động bình thường!")
        print("✅ Chức năng xác nhận đơn hàng đã được sửa thành công!")
    elif pythonanywhere_ok and not flask_ok:
        print("\n⚠️ PythonAnywhere OK, Flask cần kiểm tra")
    elif not pythonanywhere_ok:
        print("\n🔧 Cần cập nhật Django backend trước")
        print("📋 Xem file COPY_TO_PYTHONANYWHERE.md để biết cách sửa")
    else:
        print("\n🔍 Cần kiểm tra chi tiết từng phần")

if __name__ == "__main__":
    main()
 
 
 
 