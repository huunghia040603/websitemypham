# Hướng dẫn tích hợp Google Analytics API thật

## 🎯 Mục tiêu
Lấy dữ liệu thật từ Google Analytics để hiển thị thống kê email marketing campaigns.

## 📋 Bước 1: Tạo Google Analytics API Credentials

### 1.1. Truy cập Google Cloud Console
- Đi tới: https://console.cloud.google.com/
- Tạo project mới hoặc chọn project hiện có

### 1.2. Kích hoạt Google Analytics Reporting API
- Vào **APIs & Services** > **Library**
- Tìm "Google Analytics Reporting API"
- Click **Enable**

### 1.3. Tạo Service Account
- Vào **APIs & Services** > **Credentials**
- Click **Create Credentials** > **Service Account**
- Điền thông tin:
  - Name: `buddy-skincare-analytics`
  - Description: `Service account for email analytics`
- Click **Create and Continue**

### 1.4. Tạo JSON Key
- Click vào service account vừa tạo
- Vào tab **Keys**
- Click **Add Key** > **Create new key**
- Chọn **JSON** format
- Download file JSON (lưu an toàn)

## 📋 Bước 2: Cấu hình Google Analytics

### 2.1. Thêm Service Account vào GA4
- Truy cập: https://analytics.google.com/
- Chọn property của bạn
- Vào **Admin** > **Property Access Management**
- Click **+** > **Add users**
- Email: `buddy-skincare-analytics@your-project.iam.gserviceaccount.com`
- Role: **Viewer**
- Click **Add**

### 2.2. Lấy Property ID và Stream ID
- Vào **Admin** > **Data Streams**
- Click vào stream "BuddySkincare Website"
- Copy **Stream ID**: `12149140651`
- Copy **Measurement ID**: `G-JH1ST8ZFVK`

## 📋 Bước 3: Cài đặt Python Libraries

```bash
pip install google-analytics-data google-auth google-auth-oauthlib google-auth-httplib2
```

## 📋 Bước 4: Cập nhật code

### 4.1. Thêm vào requirements.txt
```
google-analytics-data==0.18.12
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
```

### 4.2. Cập nhật app.py
```python
import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)

def get_google_analytics_data(start_date, end_date):
    """Lấy dữ liệu thật từ Google Analytics"""
    try:
        # Đường dẫn đến file JSON credentials
        credentials_path = os.path.join(os.getcwd(), 'google-analytics-credentials.json')
        
        if not os.path.exists(credentials_path):
            print("❌ Google Analytics credentials not found")
            return None
        
        # Khởi tạo client
        client = BetaAnalyticsDataClient.from_service_account_file(credentials_path)
        
        # Property ID của bạn
        property_id = "12149140651"  # Stream ID from your GA4 setup
        
        # Query cho email campaigns
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[
                Dimension(name="campaignName"),
                Dimension(name="source"),
                Dimension(name="medium"),
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="users"),
                Metric(name="bounceRate"),
                Metric(name="conversions"),
                Metric(name="totalRevenue"),
            ],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimension_filter={
                "filter": {
                    "field_name": "medium",
                    "string_filter": {
                        "match_type": "EXACT",
                        "value": "email"
                    }
                }
            }
        )
        
        response = client.run_report(request)
        
        # Xử lý dữ liệu
        campaigns = []
        for row in response.rows:
            campaign_name = row.dimension_values[0].value
            sessions = int(row.metric_values[0].value)
            users = int(row.metric_values[1].value)
            bounce_rate = float(row.metric_values[2].value)
            conversions = int(row.metric_values[3].value)
            revenue = float(row.metric_values[4].value)
            
            campaigns.append({
                'name': campaign_name,
                'sessions': sessions,
                'users': users,
                'bounceRate': bounce_rate,
                'conversions': conversions,
                'revenue': revenue,
                'roi': (revenue / sessions * 100) if sessions > 0 else 0
            })
        
        return {
            'totalSessions': sum(c['sessions'] for c in campaigns),
            'totalUsers': sum(c['users'] for c in campaigns),
            'avgClickRate': sum(c['users'] for c in campaigns) / sum(c['sessions'] for c in campaigns) * 100 if campaigns else 0,
            'avgConversionRate': sum(c['conversions'] for c in campaigns) / sum(c['sessions'] for c in campaigns) * 100 if campaigns else 0,
            'campaigns': campaigns,
            'timeline': get_timeline_data(client, property_id, start_date, end_date),
            'topPages': get_top_pages_data(client, property_id, start_date, end_date)
        }
        
    except Exception as e:
        print(f"❌ Error fetching Google Analytics data: {e}")
        return None

def get_timeline_data(client, property_id, start_date, end_date):
    """Lấy dữ liệu timeline"""
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="date")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="users"),
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimension_filter={
            "filter": {
                "field_name": "medium",
                "string_filter": {
                    "match_type": "EXACT",
                    "value": "email"
                }
            }
        }
    )
    
    response = client.run_report(request)
    timeline = []
    
    for row in response.rows:
        timeline.append({
            'date': row.dimension_values[0].value,
            'sessions': int(row.metric_values[0].value),
            'users': int(row.metric_values[1].value)
        })
    
    return timeline

def get_top_pages_data(client, property_id, start_date, end_date):
    """Lấy dữ liệu top pages"""
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="pagePath")],
        metrics=[Metric(name="users")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimension_filter={
            "filter": {
                "field_name": "medium",
                "string_filter": {
                    "match_type": "EXACT",
                    "value": "email"
                }
            }
        },
        order_bys=[{"metric": {"metric_name": "users"}, "desc": True}],
        limit=10
    )
    
    response = client.run_report(request)
    top_pages = []
    total_users = sum(int(row.metric_values[0].value) for row in response.rows)
    
    for row in response.rows:
        users = int(row.metric_values[0].value)
        percentage = (users / total_users * 100) if total_users > 0 else 0
        
        top_pages.append({
            'page': row.dimension_values[0].value,
            'users': users,
            'percentage': percentage
        })
    
    return top_pages
```

## 📋 Bước 5: Cấu hình Environment Variables

### 5.1. Tạo file .env
```env
GOOGLE_ANALYTICS_PROPERTY_ID=12149140651
GOOGLE_ANALYTICS_CREDENTIALS_PATH=./google-analytics-credentials.json
```

### 5.2. Cập nhật app.py
```python
from dotenv import load_dotenv
load_dotenv()

# Trong function get_google_analytics_data
property_id = os.getenv('GOOGLE_ANALYTICS_PROPERTY_ID')
credentials_path = os.getenv('GOOGLE_ANALYTICS_CREDENTIALS_PATH', './google-analytics-credentials.json')
```

## 📋 Bước 6: Test và Deploy

### 6.1. Test locally
```bash
python app.py
```

### 6.2. Upload credentials to server
- Upload file `google-analytics-credentials.json` lên server
- Đặt trong thư mục root của project
- Đảm bảo file có quyền đọc

### 6.3. Cập nhật environment variables trên server
```bash
export GOOGLE_ANALYTICS_PROPERTY_ID="12149140651"
export GOOGLE_ANALYTICS_CREDENTIALS_PATH="./google-analytics-credentials.json"
```

## 🎯 Kết quả

Sau khi setup xong, trang **Thống kê Email** sẽ hiển thị:

✅ **Dữ liệu thật từ Google Analytics**
- Traffic từ email campaigns
- Click rates thực tế
- Conversion rates
- Revenue attribution
- Top landing pages từ email

✅ **Real-time updates**
- Dữ liệu cập nhật theo thời gian thực
- Bộ lọc theo ngày hoạt động
- Export Excel với dữ liệu thật

## 🔒 Bảo mật

- **Không commit** file `google-analytics-credentials.json` vào Git
- Thêm vào `.gitignore`:
```
google-analytics-credentials.json
*.json
```

- Sử dụng environment variables cho sensitive data
- Rotate credentials định kỳ

## 📞 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra Google Analytics API quota
2. Verify service account permissions
3. Check property ID format
4. Review error logs trong console