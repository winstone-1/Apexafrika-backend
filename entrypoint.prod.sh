#!/bin/bash
set -e

echo "========================================"
echo "🚀 APEXAFRIKA - Production Mode"
echo "========================================"

# Wait for PostgreSQL
echo "📦 Waiting for PostgreSQL..."
while ! nc -z ${DB_HOST} ${DB_PORT}; do
    sleep 1
done
echo "✅ PostgreSQL is ready"

# Wait for Redis
echo "📦 Waiting for Redis..."
while ! nc -z ${REDIS_HOST} ${REDIS_PORT}; do
    sleep 1
done
echo "✅ Redis is ready"

# Run migrations
echo "📦 Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if env vars are set
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "👤 Creating superuser..."
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists() or User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')" | python manage.py shell 2>/dev/null || true
fi

# Start Gunicorn
echo "🔥 Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-4} \
    --threads ${GUNICORN_THREADS:-2} \
    --worker-class sync \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    core.wsgi:application
