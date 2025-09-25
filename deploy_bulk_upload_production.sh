#!/bin/bash

echo "🚀 Deploying bulk upload API to production..."

# Commit changes
git add .
git commit -m "Add bulk upload API for marketing resources (Flask + Django)" || true

# Push to repository
git push origin main

echo "✅ Code pushed to repository"
echo ""
echo "📝 Next steps for production deployment:"
echo "1. SSH into your production server"
echo "2. Navigate to your project directory"
echo "3. Pull latest changes: git pull origin main"
echo "4. Restart your production server (both Flask and Django)"
echo ""
echo "🔧 Production server restart commands:"
echo "# For Flask app:"
echo "pkill -f 'python app.py'"
echo "nohup python app.py > flask.log 2>&1 &"
echo ""
echo "# For Django app (if running separately):"
echo "sudo systemctl restart your-django-service"
echo ""
echo "🔗 Test URLs after deployment:"
echo "- Local: http://localhost:8000/admin/resources/"
echo "- Production: https://buddyskincare.vn/admin/resources/"
echo ""
echo "✨ Features added:"
echo "- Bulk upload multiple files at once"
echo "- Auto environment detection (localhost vs production)"
echo "- Detailed error reporting per file"
echo "- Cloudinary integration with image optimization"
echo "- Automatic MarketingResource record creation"