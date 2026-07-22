#!/bin/bash
set -e

echo "========================================"
echo "🚀 APEXAFRIKA - Starting Application"
echo "========================================"

# Wait for PostgreSQL
echo "📦 Waiting for PostgreSQL..."
while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
    sleep 1
done
echo "✅ PostgreSQL is ready"

# Wait for Redis
echo "📦 Waiting for Redis..."
while ! nc -z ${REDIS_HOST:-redis} ${REDIS_PORT:-6379}; do
    sleep 1
done
echo "✅ Redis is ready"

# Run migrations
echo "📦 Running migrations..."
python manage.py makemigrations --noinput 2>/dev/null || true
python manage.py migrate --noinput 2>/dev/null || true

# Create superuser if env vars are set
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "👤 Creating superuser..."
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists() or User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')" | python manage.py shell 2>/dev/null || true
fi

# Start server (skip collectstatic in development)
if [ "$DJANGO_ENV" = "production" ]; then
    echo "📦 Collecting static files..."
    python manage.py collectstatic --noinput 2>/dev/null || true
    echo "🔥 Starting Gunicorn..."
    exec gunicorn --bind 0.0.0.0:8000 core.wsgi:application
else
    echo "🔥 Starting Django development server..."
    exec python manage.py runserver 0.0.0.0:8000
fi
