#!/bin/bash

echo "🚀 Deploying JavaScript fix for bank transfer upload..."

echo "📋 Fix applied:"
echo "   - Changed from: /backend/api/upload-bank-transfer/"
echo "   - Changed to:   /api/upload-bank-transfer"
echo "   - Using Flask endpoint instead of Django"
echo ""

echo "📤 Manual deploy instructions:"
echo ""
echo "1. Copy this line to PythonAnywhere Console:"
echo "   sed -i 's|/backend/api/upload-bank-transfer/|/api/upload-bank-transfer|g' /home/buddyskincare/websitemypham/static/js/main.js"
echo ""
echo "2. Or manually edit file:"
echo "   nano /home/buddyskincare/websitemypham/static/js/main.js"
echo "   Find line 863 and change to:"
echo "   const uploadResponse = await fetch('/api/upload-bank-transfer', {"
echo ""
echo "3. Reload web app on PythonAnywhere"
echo ""
echo "✅ This should fix the double /backend/ issue!"