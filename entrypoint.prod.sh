#!/bin/bash
set -e

echo "========================================"
echo "APEXAFRIKA - Production Mode"
echo "========================================"

PORT=${PORT:-8000}

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput || true

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || true

# Start Django-Q cluster in background (if not in free tier)
if [ "$START_Q_CLUSTER" = "true" ]; then
    echo "Starting Django-Q cluster..."
    python manage.py qcluster &
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
