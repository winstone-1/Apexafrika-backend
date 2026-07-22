#!/bin/bash
set -e

echo "========================================"
echo "APEXAFRIKA - Production Mode"
echo "========================================"

# Use Render's PORT or default to 8000
PORT=${PORT:-8000}

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "WARNING: DATABASE_URL not set. Using individual DB variables."
else
    echo "DATABASE_URL is set."
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput || {
    echo "Migration failed, continuing..."
}

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || {
    echo "Static collection failed, continuing..."
}

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
