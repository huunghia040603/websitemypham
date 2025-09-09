#!/usr/bin/env python3
"""
Test script for auto-complete orders functionality
"""

import requests
import json
from datetime import datetime, timedelta

# Test configuration
API_BASE_URL = 'http://localhost:8000'
TEST_ORDER_ID = 1  # Change this to an existing order ID

def test_auto_complete_api():
    """Test the auto-complete API endpoint"""
    print("🧪 Testing Auto-Complete Orders API...")
    
    try:
        # Test the auto-complete endpoint
        response = requests.post(f'{API_BASE_URL}/admin/api/orders/auto-complete', timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Auto-complete API successful!")
            print(f"📊 Result: {result}")
            
            if result.get('updated_orders'):
                print(f"🔄 Updated {len(result['updated_orders'])} orders:")
                for order in result['updated_orders']:
                    print(f"   - Order #{order['id']}: {order['customer_name']}")
            else:
                print("ℹ️ No orders were auto-completed")
                
        else:
            print(f"❌ Auto-complete API failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_order_status_check():
    """Test checking order status and updated_at field"""
    print("\n🧪 Testing Order Status Check...")
    
    try:
        # Get all orders
        response = requests.get(f'{API_BASE_URL}/admin/api/orders', timeout=30)
        
        if response.status_code == 200:
            orders = response.json()
            print(f"📋 Found {len(orders)} orders")
            
            shipped_orders = [order for order in orders if order.get('status') == 'shipped']
            print(f"🚚 Found {len(shipped_orders)} shipped orders")
            
            for order in shipped_orders:
                updated_at = order.get('updated_at')
                if updated_at:
                    try:
                        # Parse the datetime
                        updated_datetime = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                        updated_datetime = updated_datetime.replace(tzinfo=None)
                        
                        days_ago = (datetime.now() - updated_datetime).days
                        print(f"   - Order #{order['id']}: Shipped {days_ago} days ago")
                        
                        if days_ago >= 5:
                            print(f"     ⚠️  This order should be auto-completed!")
                        else:
                            print(f"     ✅ This order is still within 5-day window")
                            
                    except Exception as e:
                        print(f"   - Order #{order['id']}: Error parsing date - {e}")
                else:
                    print(f"   - Order #{order['id']}: No updated_at field")
                    
        else:
            print(f"❌ Failed to get orders: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_manual_order_update():
    """Test manually updating an order to shipped status"""
    print(f"\n🧪 Testing Manual Order Update (Order #{TEST_ORDER_ID})...")
    
    try:
        # First, get the current order
        response = requests.get(f'{API_BASE_URL}/admin/api/orders/{TEST_ORDER_ID}', timeout=30)
        
        if response.status_code == 200:
            order = response.json()
            print(f"📋 Current order status: {order.get('status')}")
            print(f"📅 Current updated_at: {order.get('updated_at')}")
            
            # Update to shipped status
            update_data = {'status': 'shipped'}
            update_response = requests.patch(
                f'{API_BASE_URL}/admin/api/orders/{TEST_ORDER_ID}',
                json=update_data,
                timeout=30
            )
            
            if update_response.status_code == 200:
                print(f"✅ Successfully updated order #{TEST_ORDER_ID} to shipped status")
                
                # Get updated order
                updated_response = requests.get(f'{API_BASE_URL}/admin/api/orders/{TEST_ORDER_ID}', timeout=30)
                if updated_response.status_code == 200:
                    updated_order = updated_response.json()
                    print(f"📅 New updated_at: {updated_order.get('updated_at')}")
                    
            else:
                print(f"❌ Failed to update order: {update_response.status_code}")
                print(f"Error: {update_response.text}")
                
        else:
            print(f"❌ Failed to get order: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Auto-Complete Orders Test Suite")
    print("=" * 50)
    
    # Run tests
    test_order_status_check()
    test_auto_complete_api()
    
    print("\n" + "=" * 50)
    print("🏁 Test Suite Complete")
    
    # Uncomment the line below to test manual order update
    # test_manual_order_update()