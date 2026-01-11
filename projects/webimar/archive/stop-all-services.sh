#!/bin/bash
# Webimar Hibrit Sistem Durdurma Scripti

echo "🛑 Webimar Hibrit Sistem Durduruluyor..."
echo "============================================"

# Tüm servisleri durdur
echo "📡 Django API durduruluyor..."
pkill -f "python manage.py runserver" 2>/dev/null || true
pkill -f "manage.py runserver" 2>/dev/null || true

echo "⚡ Next.js SSR durduruluyor..."
pkill -f "npm run dev" 2>/dev/null || true
pkill -f "next dev" 2>/dev/null || true
pkill -f "next-server" 2>/dev/null || true

echo "⚛️  React SPA durduruluyor..."
pkill -f "npm start" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true
pkill -f "react-scripts" 2>/dev/null || true

# Port bazlı durdurma (daha güçlü)
echo "🔧 Port bazlı temizlik yapılıyor..."
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 3000/tcp 2>/dev/null || true
fuser -k 3001/tcp 2>/dev/null || true

# Node.js process'lerini de kontrol et
echo "🟡 Node.js process'leri kontrol ediliyor..."
pkill -f "node.*3001" 2>/dev/null || true
pkill -f "webpack" 2>/dev/null || true

echo ""
echo "✅ Tüm servisler durduruldu!"
echo "============================================"

# Port kontrolü
echo "🔍 Port durumu kontrol ediliyor..."
PORTS_IN_USE=$(netstat -tlnp 2>/dev/null | grep -E ":300[01]|:8000" || true)

if [ -z "$PORTS_IN_USE" ]; then
    echo "✅ Tüm portlar temizlendi"
else
    echo "⚠️  Hala aktif portlar:"
    echo "$PORTS_IN_USE"
fi

echo "============================================"
