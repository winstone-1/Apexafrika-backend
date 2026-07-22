#!/bin/bash
set -e

echo "========================================"
echo "🚀 APEXAFRIKA - Starting Application"
echo "========================================"

# Function to check if PostgreSQL is ready
wait_for_postgres() {
    echo "📦 Waiting for PostgreSQL..."
    while true; do
        if pg_isready -h ${DB_HOST:-db} -p ${DB_PORT:-5432} -U ${DB_USER:-apexafrika_user} > /dev/null 2>&1; then
            echo "✅ PostgreSQL is ready"
            break
        fi
        sleep 2
    done
}

# Function to check if Redis is ready
wait_for_redis() {
    echo "📦 Waiting for Redis..."
    while true; do
        if redis-cli -h ${REDIS_HOST:-redis} -p ${REDIS_PORT:-6379} ping > /dev/null 2>&1; then
            echo "✅ Redis is ready"
            break
        fi
        sleep 2
    done
}

# Wait for services
wait_for_postgres
wait_for_redis

# Run migrations
echo "📦 Running migrations..."
python manage.py makemigrations --noinput 2>/dev/null || true
python manage.py migrate --noinput 2>/dev/null || true

# Create superuser if env vars are set
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "👤 Creating superuser..."
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists() or User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')" | python manage.py shell 2>/dev/null || true
fi

# Start server
if [ "$DJANGO_ENV" = "production" ]; then
    echo "🔥 Starting Gunicorn..."
    exec gunicorn --bind 0.0.0.0:8000 core.wsgi:application
else
    echo "🔥 Starting Django development server..."
    exec python manage.py runserver 0.0.0.0:8000
fi
