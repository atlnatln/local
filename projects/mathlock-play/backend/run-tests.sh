#!/bin/bash
# MathLock Backend Test Runner
# Çalıştırmak: ./run-tests.sh

set -e

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "[HATA] .venv dizini bulunamadı. Önce: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

source .venv/bin/activate

echo "🧪 Backend testleri çalıştırılıyor..."
python manage.py test credits --verbosity=2 "$@"

echo "✅ Tüm testler tamamlandı!"
