#!/bin/bash
set -e

echo "========================================"
echo "APEXAFRIKA - Production Mode"
echo "========================================"

PORT=${PORT:-8000}

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL is not set!"
    echo "Please add DATABASE_URL to your environment variables."
    echo "Current environment variables:"
    env | grep -E "DATABASE|DB_|POSTGRES" || echo "No database env vars found"
    exit 1
fi

echo "DATABASE_URL is set."

# Show database connection info (hide password)
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
echo "Database host: $DB_HOST"
echo "Database port: $DB_PORT"

# Wait for database
echo "Waiting for database..."
python -c "
import time
import os
import socket
import sys
import re

db_url = os.environ.get('DATABASE_URL', '')
match = re.search(r'@([^:]+):(\d+)/', db_url)
if match:
    db_host = match.group(1)
    db_port = int(match.group(2))
else:
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = int(os.environ.get('DB_PORT', 5432))

print(f'Connecting to {db_host}:{db_port}')
for i in range(30):
    try:
        with socket.create_connection((db_host, db_port), timeout=2):
            print('Database is ready')
            sys.exit(0)
    except Exception as e:
        time.sleep(2)
        print(f'Waiting for database... {i+1}/30 ({str(e)})')
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
