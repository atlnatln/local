#!/bin/bash
set -e

echo "🟢 Django migrate başlatılıyor..."
python3 manage.py migrate

echo "🟢 Statik dosyalar toplanıyor..."
python3 manage.py collectstatic --noinput

echo "🔄 webimar-api servisi yeniden başlatılıyor..."
sudo systemctl restart webimar-api

echo "✅ Deploy script başarıyla tamamlandı."
