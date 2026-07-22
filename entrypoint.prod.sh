#!/bin/bash
set -e

echo "========================================"
echo "APEXAFRIKA - Production Mode"
echo "========================================"

# Use Render's PORT or default to 8000
PORT=${PORT:-8000}

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
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn on Render's PORT
echo "Starting Gunicorn on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT \
    --workers ${GUNICORN_WORKERS:-4} \
    --threads ${GUNICORN_THREADS:-2} \
    --worker-class sync \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    core.wsgi:application
