FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE 8003

# Başlatma: migration + gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn mathlock_backend.wsgi:application --bind 0.0.0.0:8003 --workers 2"]
