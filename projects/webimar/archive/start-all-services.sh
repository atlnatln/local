#!/bin/bash
# Webimar Hibrit Sistem Başlatma Scripti

echo "🚀 Webimar Hibrit Sistem Başlatılıyor..."
echo "============================================"

# Django API Başlat (Port 8000)
echo "📡 Django API başlatılıyor (Port 8000)..."
cd /home/akn/Genel/webimar/webimar-api
source /home/akn/Genel/webimar/webimar-api/.venv/bin/activate
export DJANGO_SETTINGS_MODULE=webimar_api.settings
nohup python manage.py runserver 0.0.0.0:8000 > /tmp/django.log 2>&1 &
DJANGO_PID=$!
echo "✅ Django API başlatıldı (PID: $DJANGO_PID)"
sleep 2  # Django'nun başlaması için kısa bekleme

# Next.js Dev Server Başlat (Port 3000)
echo "🏠 Next.js Dev Server başlatılıyor (Port 3000)..."
cd /home/akn/Genel/webimar/webimar-nextjs
echo "📂 Working directory: $(pwd)"
echo "📁 Directory contents: $(ls -la pages | head -3 || echo 'No pages dir found')"
nohup npx next dev --port 3000 > /tmp/nextjs.log 2>&1 &
NEXTJS_PID=$!
echo "✅ Next.js başlatıldı (PID: $NEXTJS_PID)"
sleep 3  # Next.js'in başlaması için biraz daha uzun bekleme

# React SPA Başlat (Port 3001) 
echo "⚛️  React SPA başlatılıyor (Port 3001)..."
cd /home/akn/Genel/webimar/webimar-react
BROWSER=none PORT=3001 nohup npm run start > /tmp/react.log 2>&1 &
REACT_PID=$!
echo "✅ React SPA başlatıldı (PID: $REACT_PID)"
sleep 2  # Service'in başlaması için kısa bekleme

echo ""
echo "🎯 Tüm servisler başarıyla başlatıldı!"
echo "============================================"
echo "📡 Django API:   http://localhost:8000"
echo "🏠 Next.js:      http://localhost:3000"
echo "⚛️  React SPA:   http://localhost:3001"
echo ""
echo "📝 PID'ler:"
echo "   Django:  $DJANGO_PID"
echo "   Next.js: $NEXTJS_PID"
echo "   React:   $REACT_PID"
echo ""
echo "🛑 Durdurmak için: /bin/bash \"/home/akn/Genel/webimar/stop-all-services.sh\""
echo "============================================"
