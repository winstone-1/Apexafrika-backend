#!/bin/bash
set -e

echo "========================================"
echo "APEXAFRIKA - Production Mode"
echo "========================================"

PORT=${PORT:-8000}

# Wait for database (using python)
echo "Waiting for database..."
python -c "
import time
import os
import socket
import sys

# Try DATABASE_URL first, then individual vars
db_host = os.environ.get('DB_HOST', 'localhost')
db_port = int(os.environ.get('DB_PORT', 5432))

# If DATABASE_URL is set, parse it
if os.environ.get('DATABASE_URL'):
    import re
    match = re.search(r'@([^:]+):(\d+)/', os.environ.get('DATABASE_URL', ''))
    if match:
        db_host = match.group(1)
        db_port = int(match.group(2))

for i in range(30):
    try:
        with socket.create_connection((db_host, db_port), timeout=2):
            print('Database is ready')
            sys.exit(0)
    except:
        time.sleep(2)
        print(f'Waiting for database... {i+1}/30')
print('Database timeout - continuing anyway')
"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput || true

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || true

# Create superuser if env vars are set
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists() or User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')" | python manage.py shell 2>/dev/null || true
fi

# Start Django-Q cluster in background (if enabled)
if [ "$START_Q_CLUSTER" = "true" ]; then
    echo "Starting Django-Q cluster..."
    python manage.py qcluster &
    echo "Django-Q cluster started in background"
fi

# Start Gunicorn
echo "Starting Gunicorn on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT \
    --workers ${GUNICORN_WORKERS:-2} \
    --threads ${GUNICORN_THREADS:-2} \
    --worker-class sync \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    core.wsgi:application
