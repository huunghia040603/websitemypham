#!/bin/bash

echo "🚀 Deploying final bank transfer upload fix to production..."

# Upload the updated app.py file
echo "📤 Uploading app.py..."
scp app.py budduskincarevn@gmail.com@files.pythonanywhere.com:/home/buddyskincare/websitemypham/app.py

# Upload the updated main.js file
echo "📤 Uploading main.js..."
scp static/js/main.js budduskincarevn@gmail.com@files.pythonanywhere.com:/home/buddyskincare/websitemypham/static/js/main.js

echo "✅ Bank transfer upload fix deployed successfully!"
echo ""
echo "📋 Changes made:"
echo "   - Updated JavaScript to call Django endpoint: /backend/api/upload-bank-transfer/"
echo "   - Django endpoint uploads directly to Cloudinary"
echo "   - Removed duplicate Flask endpoint"
echo ""
echo "🔄 Please reload your web app on PythonAnywhere to apply changes"
echo ""
echo "🧪 Test the fix by:"
echo "   1. Go to checkout page"
echo "   2. Select 'Chuyển khoản ngân hàng'"
echo "   3. Upload a bank transfer image"
echo "   4. Place order"
echo "   5. Check that bank_transfer_image field is populated with Cloudinary URL"