#!/bin/bash
set -e

echo "========================================"
echo "APEXAFRIKA - Starting Application"
echo "========================================"

# Wait for PostgreSQL using python
echo "Waiting for PostgreSQL..."
python -c "
import time
import os
import socket
host = os.environ.get('DB_HOST', 'db')
port = int(os.environ.get('DB_PORT', 5432))
for i in range(30):
    try:
        with socket.create_connection((host, port), timeout=1):
            print('PostgreSQL is ready')
            break
    except:
        time.sleep(1)
        print(f'Waiting for PostgreSQL... {i+1}/30')
"

# Wait for Redis using python
echo "Waiting for Redis..."
python -c "
import time
import os
import socket
host = os.environ.get('REDIS_HOST', 'redis')
port = int(os.environ.get('REDIS_PORT', 6379))
for i in range(30):
    try:
        with socket.create_connection((host, port), timeout=1):
            print('Redis is ready')
            break
    except:
        time.sleep(1)
        print(f'Waiting for Redis... {i+1}/30')
"

# Run migrations
echo "Running migrations..."
python manage.py makemigrations --noinput 2>/dev/null || true
python manage.py migrate --noinput 2>/dev/null || true

# Start server
if [ "$DJANGO_ENV" = "production" ]; then
    PORT=${PORT:-8000}
    echo "Starting Gunicorn on port $PORT..."
    exec gunicorn --bind 0.0.0.0:$PORT core.wsgi:application
else
    echo "Starting Django development server..."
    exec python manage.py runserver 0.0.0.0:8000
fi
