#!/bin/bash

echo "🚀 Deploying bulk upload API to production..."

# Kill any existing processes
pkill -f "python app.py" || true

# Activate virtual environment
source beautysale_env/bin/activate

# Pull latest changes
git add .
git commit -m "Add bulk upload API for marketing resources" || true
git push origin main

echo "✅ Code pushed to repository"
echo "📝 Next steps:"
echo "1. SSH into your production server"
echo "2. Pull the latest changes: git pull origin main"
echo "3. Restart your production server"
echo "4. Test the bulk upload feature"

echo "🔗 Test URLs:"
echo "- Local: http://localhost:8000/admin/resources/"
echo "- Production: https://buddyskincare.vn/admin/resources/"